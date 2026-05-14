## Solution 27: Year in Review Recap

### The first thing to realize

This looks fancy. It is actually one of the simplest patterns in data engineering: **a huge batch job that pre-computes a small JSON per user, dropped into a fast key-value store, served as static content with personalization on top.**

There is no real-time anything. The "magic" is in the design, copywriting, and image rendering, not the data pipeline. The pipeline just runs once.

### The architecture

```
   ┌───────────────────────────────────┐
   │   Warehouse (full year of events) │
   │   plays / orders / activity rows  │
   │   already in BigQuery / Snowflake │
   └────────────────┬──────────────────┘
                    │
                    ▼
   ┌────────────────────────────────────────────────┐
   │  Yearly aggregation job (SQL + dbt)            │
   │                                                │
   │  Per user, compute ~20-50 features:            │
   │   - total minutes / km / spend                 │
   │   - top 5 things by count                      │
   │   - "biggest day", "longest streak"            │
   │   - novelty / rank vs other users              │
   │                                                │
   │  Output: one big table user_recap_features     │
   └────────────────┬───────────────────────────────┘
                    │
                    ▼
   ┌────────────────────────────────────────────────┐
   │  Story template selection (deterministic)      │
   │                                                │
   │  Map features → which "story cards" each user  │
   │  gets, in what order. Pure function of         │
   │  features. Same user, same year, same cards.   │
   └────────────────┬───────────────────────────────┘
                    │
                    ▼
   ┌────────────────────────────────────────────────┐
   │  Pre-rendered share images                     │
   │  (one PNG per user, generated headless)        │
   │  Stored on S3 / CDN                            │
   └────────────────┬───────────────────────────────┘
                    │
                    ▼
   ┌────────────────────────────────────────────────┐
   │  Serving store (DynamoDB / Bigtable / Memcache)│
   │  Key: user_id                                  │
   │  Value: { cards: [...], share_image_url, hash }│
   └────────────────┬───────────────────────────────┘
                    │
        ┌───────────┴────────────┐
        ▼                        ▼
   ┌──────────────┐         ┌────────────────────┐
   │ Mobile app   │         │ Social share image │
   │ requests     │         │ served from CDN    │
   │ recap        │         │ (no compute)       │
   └──────────────┘         └────────────────────┘
```

### Why batch is fine

The recap covers a year. Events from December 31 do not change "top artist of 2025." A weekly recompute in late December nails the freshness. There is no business value in real-time here.

The only realtime piece is "when the user opens the app, fetch their card list." That is a single point read.

### The aggregation job

The job runs entirely in SQL inside the warehouse. A simplified shape:

```sql
WITH per_user AS (
  SELECT
    user_id,
    SUM(seconds_played) / 60.0       AS minutes_total,
    COUNT(DISTINCT track_id)         AS unique_tracks,
    APPROX_TOP_COUNT(artist, 5)      AS top_artists,
    APPROX_TOP_COUNT(genre, 3)       AS top_genres,
    MAX_BY(date, seconds_played)     AS biggest_day,
    COUNT(DISTINCT date)             AS days_active
  FROM plays
  WHERE play_date BETWEEN '2025-01-01' AND '2025-12-31'
  GROUP BY user_id
)
SELECT
  user_id,
  *,
  -- a few percentile features
  PERCENT_RANK() OVER (ORDER BY minutes_total) AS minutes_percentile
FROM per_user;
```

The output is one row per user with 20-50 columns. For a 500M user platform, this is a few hundred GB. Trivial for a modern warehouse.

### The story template engine

A user does not see raw numbers. They see a narrative: "You listened to 8,432 minutes this year. That's more than 98% of listeners." The mapping from features to cards is a small rule engine:

```python
def build_cards(features):
    cards = []
    cards.append(intro_card(features.minutes_total))
    if features.minutes_percentile > 0.95:
        cards.append(top_listener_card(features.minutes_percentile))
    cards.append(top_artists_card(features.top_artists))
    if features.unique_tracks > 1000:
        cards.append(explorer_card(features.unique_tracks))
    # …and so on
    return cards
```

This runs as part of the same batch job (typically in dbt's macros, or a Spark/BigQuery Python step). The output is per-user JSON.

The critical property: **the output is a deterministic function of the features**. Same features in, same JSON out. So if the job re-runs, users do not see a different story tomorrow.

### Pre-rendered share images

The shareable image (Instagram story format, 1080×1920, with the user's stats overlaid) cannot be rendered on demand. Two reasons:

1. At launch, hundreds of millions of users open the app within 48 hours. On-demand rendering would melt any render farm.
2. Predictable storage is cheap; bursty CPU is expensive.

So we pre-render. The batch job, after producing the JSON, fans out to a small image renderer (often headless Chromium with a templated HTML page, or Skia, or a custom rasterizer). Output: one PNG per user, written to S3 / GCS / a CDN bucket.

URL pattern: `https://cdn.example.com/recap/2025/{user_id}.png`. The URL is the only thing the app needs to know. The CDN handles the load.

Approximate cost: 500M users × ~200 KB image = 100 TB on the CDN for the season. Reasonable.

### Serving

When a user opens the recap, the app calls a small API:

```
GET /recap/2025
→ { cards: [...], share_image_url: "..." }
```

The API is a thin layer over a KV store. Sub-50 ms latency. Same point-read pattern as the banking widget in Problem 22.

### The traffic spike

When the recap drops, every active user opens it within a day or two. That's a 10-30x spike over normal traffic. Strategies:

* **Pre-render everything.** No live rendering.
* **CDN for images.** Static assets handle a million requests per second on a CDN with no engineering effort.
* **API caches the JSON aggressively.** TTL of an hour is fine because the data does not change.
* **Gradual rollout.** Launch to 10% of users, then 30%, then 100% over a week. Smooths the spike.
* **Pre-warm the cache.** Just before launch, run a background sweep that touches every user's record, so caches are hot.

### Privacy and the "no, please don't" user

Some users do not want to be confronted with their year. The app should:

* Make the recap opt-in to push notifications.
* Allow opt-out before generation. If a user opts out, their record is filtered from the batch job.
* Never include features they would find uncomfortable (highly listened-to ex's playlists, etc.). The story engine includes a rules layer to skip cards that are likely to feel invasive.

### Rebuild and corrections

If a bug in the aggregation is discovered the day after launch, the recap can be rebuilt:

* Re-run the aggregation job.
* Same deterministic story engine produces new JSON.
* Re-render images.
* Push new JSON into the serving store.

Because the whole thing is a pure function of warehouse data, rebuilds are safe. The user might briefly see "their recap changed," which is acceptable in the first day.

### Common mistakes interviewers want you to name

1. **Trying to make this real-time.** No business value, huge cost.
2. **Rendering images on demand.** The first hour of launch dies.
3. **Non-deterministic story selection** (random emoji, random card order). Refreshing the recap shows a different version. Users hate that.
4. **No opt-out / privacy controls.** PR risk.
5. **No gradual rollout.** Launches at midnight, infra cooks.

### Bonus follow-up the interviewer might throw

> *"How would you decide what makes a 'good' card to include?"*

A few principles I would design around, mostly product not engineering:

* **The card celebrates the user**, never makes them feel bad.
* **Relative metrics beat absolute** ("more than 87% of listeners" beats "8,432 minutes").
* **A surprise** in each card, not just the obvious top-N list.
* **Tested.** A/B test cards on a small slice before the full launch.

Engineering enables this by making story templates pluggable and feature counts easy to add. The hard part is product judgment.
