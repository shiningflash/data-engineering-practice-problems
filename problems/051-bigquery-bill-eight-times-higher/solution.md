## Solution 51: BigQuery Bill Eight Times Higher

### Short version you can say out loud

> I would not guess. I would run six queries against INFORMATION_SCHEMA in the first hour. Almost every BigQuery cost explosion has the same shape: a handful of scheduled queries that scan unpartitioned data, or a SELECT * on a huge table, or a dashboard refreshing too often. Once I find the top 10 queries by bytes billed, the answer is usually obvious in 30 minutes.

### The six queries I would run

**1. Daily cost trend, last 90 days.**

```sql
SELECT
  DATE(creation_time) AS day,
  SUM(total_bytes_billed) / POW(2, 40) AS tib,
  SUM(total_bytes_billed) / POW(2, 40) * 6.25 AS approx_usd_on_demand
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
GROUP BY day
ORDER BY day;
```

This plots the inflection point. The day the bill started rising is the clue.

**2. By user / service account.**

```sql
SELECT
  user_email,
  SUM(total_bytes_billed) / POW(2,40) AS tib,
  COUNT(*) AS jobs
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY user_email
ORDER BY tib DESC
LIMIT 20;
```

Usually one or two accounts dominate. If a service account is at the top, the answer is a pipeline. If a human is at the top, the answer is an analyst's notebook or dashboard.

**3. Top queries by total bytes billed.**

```sql
SELECT
  SUBSTR(query, 1, 100) AS query_snippet,
  user_email,
  COUNT(*) AS runs,
  SUM(total_bytes_billed) / POW(2,40) AS tib_total,
  AVG(total_bytes_billed) / POW(2,30) AS gib_avg
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND job_type = 'QUERY'
  AND statement_type = 'SELECT'
GROUP BY query_snippet, user_email
ORDER BY tib_total DESC
LIMIT 30;
```

Sort by `tib_total`. The top 5-10 queries usually explain 70-90 percent of the bill.

**4. Scheduled queries by frequency.**

```sql
SELECT
  SUBSTR(query, 1, 100) AS query,
  COUNT(*) AS runs_in_30d
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND statement_type = 'SELECT'
GROUP BY query
HAVING runs_in_30d > 100
ORDER BY runs_in_30d DESC;
```

Anything running thousands of times a month is likely a dashboard refresh or a scheduled query. Often that is the culprit.

**5. Top tables scanned.**

```sql
SELECT
  ref.dataset_id,
  ref.table_id,
  SUM(j.total_bytes_billed) / POW(2,40) AS tib
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT j,
     UNNEST(j.referenced_tables) ref
WHERE j.creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY ref.dataset_id, ref.table_id
ORDER BY tib DESC
LIMIT 20;
```

Identifies the tables that drive the bill. Knowing the table makes the fix obvious (partition it, cluster it, archive old data).

**6. Comparison: April vs May, same queries.**

```sql
WITH monthly AS (
  SELECT
    EXTRACT(MONTH FROM creation_time) AS m,
    SUBSTR(query, 1, 100) AS q,
    SUM(total_bytes_billed) / POW(2,40) AS tib
  FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
  WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 60 DAY)
  GROUP BY 1, 2
)
SELECT q, MAX(IF(m=4, tib, 0)) AS april, MAX(IF(m=5, tib, 0)) AS may
FROM monthly
GROUP BY q
ORDER BY (may - april) DESC
LIMIT 20;
```

The biggest month-over-month deltas are the queries that grew. That is where new cost came from.

### What the answer usually is

In real incidents, the top of that list is one of:

1. **A scheduled query that scans an unpartitioned table** every hour. 500 GB scan × 720 hours = 360 TB billed, easily $1,000+.
2. **A new dashboard** that refreshes every 5 minutes against a multi-TB raw events table.
3. **A `SELECT *`** on a huge table inside a dbt model or a notebook.
4. **A backfill that nobody knew was running.** Sometimes a `dbt run --full-refresh` on a 50-model project rebuilds everything every night.
5. **A noisy ML pipeline** scanning the same training data 20 times for feature engineering.
6. **Real growth.** The business doubled its data; the bill doubled. This is rare for 8x, but possible.

### Walking the fix

Once I find the top 3 queries, the fixes are:

**Fix the scheduled scan.**

```sql
-- before: scans all partitions
SELECT ... FROM analytics.events;

-- after: partition pruned
SELECT ... FROM analytics.events
WHERE event_date = CURRENT_DATE - 1;
```

Often a 99% cost reduction on that query.

**Reduce dashboard refresh.**

Most dashboards on daily data only need a daily refresh. Drop the auto-refresh from 12x/hour to 1x/hour. 12x cost reduction, no user impact for daily data.

**Replace SELECT * with named columns.**

```sql
-- before: scans 50 columns
SELECT * FROM analytics.fact_orders WHERE date = ...;

-- after: scans 4 columns
SELECT order_id, customer_id, amount, date
FROM analytics.fact_orders WHERE date = ...;
```

The bill is bytes-billed. Selecting fewer columns reduces bytes proportionally.

**Materialize hot summaries.**

If 10 queries scan the same daily fact for the same aggregations, build a materialized view or a summary table. Each query then reads a few rows instead of millions.

### Long-term: governance

After the immediate fixes:

* **Query tags.** Every job carries a label (`team:`, `dataset:`, `purpose:`). Cost reports by tag.
* **Per-team budgets** with Slack alerts when on pace to exceed.
* **A weekly "top 10 queries" report** so the team sees what is expensive.
* **Reservation slots** if usage is predictable. BigQuery slots can save 30-50% over on-demand for steady workloads.

### Reservation vs on-demand: a quick decision

| Usage shape | Better choice |
| ------------------------------------------ | ---------------------- |
| Spiky, unpredictable, occasional heavy day | On-demand |
| Steady-state, high daily usage | Slot commitment |
| Multiple teams sharing a workload | Slots with reservations|
| Just starting out, no idea yet | On-demand |

For this scenario, $4k/month is still small. I would keep on-demand and just fix the queries. At $20k/month, the slot reservation conversation becomes worth having.

### The conversation with finance

> "The increase from $500 to $4,000 is driven by three queries:
>
> 1. A daily aggregation that was changed to scan the full events table instead of just yesterday's partition. ~$2,200 of the increase.
> 2. A new ML feature pipeline scanning 800 GB twelve times a day. ~$1,000.
> 3. A dashboard auto-refresh that was set to 5 minutes during launch and never lowered. ~$500.
>
> I have fixes ready for all three. Expected June bill is ~$700-900. The remaining $200-400 over April is real growth from the new pipeline, which is delivering business value."

Specific numbers, named queries, a plan, a future estimate. That is the right shape.

### Common mistakes interviewers want you to name

1. **Investigating from intuition** instead of from INFORMATION_SCHEMA.
2. **Switching to slots** before fixing wasteful queries. You lock in the inflated usage.
3. **Killing queries without finding their owner.**
4. **No follow-up alert.** Bills will rise again.
5. **Not communicating savings.** Team forgets the work happened; behaviour repeats.

### Bonus follow-up the interviewer might throw

> *"What if the team genuinely needs the data and there is no obvious waste?"*

Then the conversation shifts. Two moves:

1. Talk to finance about reserved slots for the steady portion of the workload. Long-term cost reduction without changing behaviour.
2. Look at storage as well as compute. Sometimes the cost is in long-term storage of data that nobody queries. Lifecycle rules and archive tables can save a real fraction.

If both have been exhausted and the workload is justified, the cost is the cost. Show the business "cost per user" or "cost per revenue dollar" and let them decide.
