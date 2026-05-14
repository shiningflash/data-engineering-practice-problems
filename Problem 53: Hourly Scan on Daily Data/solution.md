## Solution 53: Hourly Scan on Daily Data

### Short version you can say out loud

> The dashboard reads the same answer 24 times a day. The cheapest fix is to compute that answer once and cache it. The cleanest way is a daily summary table or a materialized view, refreshed once after the source data lands. The dashboard's query stays the same, just pointed at the small table instead of the 5 TB raw. User experience is unchanged. Cost drops from $750/month to under $10/month.

### Four options, ranked

**1. Daily summary table (my pick).**

Compute the dashboard's exact query into a small table once a day, right after the data lands. The dashboard reads the small table.

```sql
CREATE OR REPLACE TABLE marts.daily_dashboard_metrics AS
SELECT
  region,
  product_category,
  DATE_TRUNC(order_date, DAY) AS day,
  COUNT(*) AS orders,
  SUM(amount) AS revenue
FROM raw.orders
WHERE order_date BETWEEN '2025-01-01' AND CURRENT_DATE
GROUP BY 1, 2, 3;
```

The dashboard's query becomes:

```sql
SELECT * FROM marts.daily_dashboard_metrics WHERE ...;
```

A few thousand rows. Sub-second scan. Pennies per month.

The dashboard's URL, layout, filters, and look are unchanged. Users do not even know.

**2. Materialized view.**

If the warehouse supports them well (BigQuery, Snowflake), define a materialized view that captures the dashboard's query. The view is refreshed on a schedule or on insert. Queries against the source automatically rewrite to use the MV.

```sql
CREATE MATERIALIZED VIEW marts.dashboard_mv AS
SELECT region, product_category, ...
FROM raw.orders
GROUP BY ...;
```

Less control than option 1, but you do not have to maintain the refresh job yourself.

**3. BI tool extract / cache.**

Tools like Looker, Tableau, Power BI can build their own extract — basically option 1 but inside the BI tool. Refreshed daily, served from cache.

Less portable, less SQL-visible, but no warehouse-side change.

**4. Schedule change at the BI tool.**

Just change the dashboard refresh from hourly to daily. Same data, 24x cheaper.

This is the simplest one and the team did not consider it. Worth asking: do users really need hourly? If the data only changes daily, the hourly refresh shows the same answer 23 times in a row.

### My pick for this scenario

**Option 1 (daily summary table) plus Option 4 (daily refresh)** together.

* The summary table makes the query cheap.
* The daily refresh stops re-running the same answer 24 times.

Cost goes from $750/mo to under $10/mo. The dashboard renders faster, too, because the underlying query is smaller.

### Keeping the user experience identical

The user-facing pieces are:

* The dashboard URL.
* The chart names.
* The filters available.
* The numbers shown.

None of those need to change. The change is invisible to the user: only the underlying table swap. If anything, performance improves because the query is now reading a few thousand rows instead of 5 TB.

If there is a worry about new bugs, run both old and new for a few days. Compare row counts and sums. If they match, swap.

### What about hourly users?

If even one user needs hourly data, the picture changes. Two paths:

1. **Cap the hourly query to today's partition only.** Yesterday is fixed, today is live. Hourly is now scanning a few GB, not 5 TB.

```sql
WHERE date = CURRENT_DATE     -- only today's partition, ~200 GB instead of 5 TB
```

Cost drops from $750/mo to ~$30/mo.

2. **Two layers**: a daily summary for historical, a small "today" table refreshed hourly. The dashboard UNIONs them. Adds a little complexity for the team that wants up-to-the-hour data.

For this scenario, neither is needed because the source only updates daily.

### What about the storage cost of the summary table?

A daily summary table for a 5 TB source is typically megabytes, not gigabytes. The grain is much smaller than the raw events. Storage cost is negligible compared to the scan savings.

### How to talk to the team

The conversation matters:

> "I noticed the dashboard scans 5 TB every hour to show numbers that only change at 6 AM. I can change two things: rebuild the dashboard query into a small daily summary table, and switch the dashboard's refresh from hourly to daily. The dashboard itself does not change. Users see the same numbers, faster. Saves about $740 a month. Half a day of work, easy to roll back if something looks off."

Concrete, specific, and not preachy. The team will say yes.

### Longer term: how to catch this

Set up a weekly automated report:

* Top 10 queries by bytes-billed in the past week.
* Each one annotated with: how often it runs, what table it scans, who owns it.

Anyone glancing at the report will see "daily query running 24x/day on 5 TB" the next time it pops up. Catches the next instance early.

### Common mistakes interviewers want you to name

1. **Killing the dashboard refresh** without telling the team.
2. **Building a materialized view** but forgetting to refresh it (some engines require explicit refresh schedules).
3. **Picking the BI tool extract** when warehouse-side is simpler. Couples the fix to one tool.
4. **Not validating** that the summary matches the original. Different aggregation orders can produce subtle differences.
5. **One mega summary table** that tries to cover every dashboard. Becomes its own slow query.

### Bonus follow-up the interviewer might throw

> *"What if the team also has 30 other dashboards on the same table, all scanning hourly?"*

Then the fix scales naturally. Build a slightly wider summary table that covers the common columns. The 30 dashboards all read from it. Now you have replaced 30 × $750 = $22,500/month with one $50 summary table. The win is bigger when the source is shared.

Or, more structurally, treat this as a sign that the team needs a metrics layer (like dbt's metrics, or a semantic model). One place to define the metric, all dashboards read consistent numbers without scanning raw.
