## Solution 50: One Partition Always Ten Percent Smaller

### Short version you can say out loud

> First question: does this pattern map to reality? If the small partition is always a Sunday, that's probably just user behavior. If it's a random-looking Tuesday, that's suspicious. Second question: what's missing, a category of events, a region, a producer? If you can name a missing slice, you have a bug. If the loss is even across all dimensions, you're probably looking at noise. Ten percent is large enough to be worth an hour of investigation.

### Step 1: confirm the pattern is real

Pull the per-partition row counts for the last 60 days:

```sql
SELECT
  event_date,
  COUNT(*) AS rows,
  EXTRACT(DOW FROM event_date) AS day_of_week
FROM events
WHERE event_date > CURRENT_DATE - 60
GROUP BY 1, 3
ORDER BY 1;
```

Plot it. Three possible shapes:

* A clean weekly dip on a specific day. Day-of-week effect, likely real user behavior.
* A dip that wanders across days. Suspicious. Patterns that move tell a different story.
* A consistent percentage off every day of the week. Noise, not a single-partition issue at all.

The "always 10% smaller" framing suggests a fixed cadence. Confirm: is it always the same day?

### Step 2: account for the obvious

Things to rule out:

* Day of week. Many businesses have lower activity on weekends. A Sunday partition being 30% smaller is normal.
* Public holidays. Specific dates have lower volume. Map the dip dates to holiday calendars.
* Time zone effect. "Day" in the warehouse may not align with "day" at the source. If the source closes at 8 PM local, "their day" ends earlier than UTC midnight.
* Recurring maintenance. Some sources have scheduled maintenance windows on a specific weekday.

If the dip aligns with any of these, it's not a bug. Document it ("Sunday partitions average 30% lower due to weekend traffic patterns") so the next person doesn't chase it.

### Step 3: find what is missing

If the dip survives the explanations above, look for which slice of the data is short:

```sql
SELECT
  event_type,
  COUNT(*) AS rows
FROM events
WHERE event_date = '2025-05-11'   -- the small day
GROUP BY event_type
ORDER BY rows DESC;
```

Compare to a normal day. If `event_type = 'page_view'` is missing 30% and other types look normal, you have a clue: one producer is misbehaving on that day.

Same exercise across other dimensions: by region, by app version, by source, by hour. The missing rows are usually concentrated, not evenly thinned.

### Common real causes

When the dip turns out to be a bug, it's usually one of:

1. A weekly job at the source pauses ingestion for a maintenance window. Their "data missing for 4 hours" shows up as your "10% smaller partition."
2. A specific service has a weekly deploy that takes minutes, during which events drop.
3. A scheduled batch in the source is competing for the same Kafka topic, causing brief backpressure.
4. A weekly partner upload runs late, beyond your partition boundary, and lands in the following day's partition instead.
5. A daylight-saving-time edge that shifts an hour out of one partition into the next, twice a year.

Each is fixable, but the fix usually lives on a different team than yours.

### Step 4: judge if it matters

Even if it is a bug, you have to decide whether to spend time on it. The honest test:

* Does the missing 10% affect any downstream business decision?
* Does the smaller partition cause downstream errors (failed joins, broken counts)?
* Does the pattern hide a worse failure that could grow?

If the answer is "no, no, no," document it and move on. If the missing rows are a category that finance cares about, investigate properly.

### A useful statistical anchor

10% is suspicious because it is too large for random noise on a high-volume table, but small enough that "normal variation" is plausible. A rough rule:

* If daily counts have a standard deviation of `s`, a partition that is more than `3*s` below the mean is unusual.
* If the dips are systematically at the same level (clear 10% every Tuesday), that is not noise, it is signal.

Quick:

```sql
WITH daily AS (
  SELECT event_date, COUNT(*) AS cnt FROM events
  WHERE event_date > CURRENT_DATE - 90
  GROUP BY event_date
)
SELECT
  AVG(cnt) AS avg_rows,
  STDDEV(cnt) AS stddev_rows,
  AVG(cnt) - 3 * STDDEV(cnt) AS lower_3sigma
FROM daily;
```

If the dip partitions are below the lower-3-sigma line, they are unusual.

### What to do once I know

If the dip is **real and bothersome**: file a ticket with the team owning the source. "Every Tuesday between 2-3 AM UTC, the `events` topic has reduced throughput by ~10%. Can you confirm a maintenance window?"

If the dip is **real but harmless**: write it down in the table's documentation. "Tuesdays are typically 10% lower due to source maintenance. Not a bug."

If the dip is **noise**: do nothing, but add an anomaly check so a *real* drop would page.

### Common mistakes interviewers want you to name

1. **Ignoring patterns because "data is noisy."** A repeated pattern is not noise.
2. **Spending a week investigating a 10% dip on Sundays.** Day of week, ignore.
3. **Assuming a fix is on your side.** Often the bug is at the source.
4. **No documentation.** The next engineer chases the same ghost.
5. **No alert for a worse version.** Today it's 10%; tomorrow it could be 90%.

### Bonus follow-up the interviewer might throw

> *"What if the partition is exactly 10% smaller, never more, never less? Almost too consistent."*

That is a much stronger signal. Random data losses are rarely exactly the same percentage. A consistent 10% smells like:

* A specific producer is offline on that day (a known set of devices, services, or geographies).
* A scheduled job at the source skips that day (a planned partial outage).
* A filter at the ingest is dropping a specific category every Tuesday.

Investigate by slicing the data. The missing 10% is almost certainly a clean category you can name. Once named, the fix is obvious.
