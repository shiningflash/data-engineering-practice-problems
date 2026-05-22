## Solution 30: Warehouse Cost Doubled in Two Months

### Short version you can say out loud

> I would get the data before the conversation. Almost always, 5 to 10 queries or jobs account for most of the increase. Then I would talk to finance with a number and a plan, and to engineering with options that don't break anyone's work. The biggest cost win is usually scheduled queries that scan more than they need to, plus one or two new dashboards that someone built without realising they would run hourly.

### Step 1: pull the actual numbers (the same day)

The warehouse usage tables tell you exactly what is happening.

In Snowflake:

```sql
-- Cost by warehouse by day, last 90 days
SELECT
  warehouse_name,
  DATE_TRUNC('day', start_time) AS day,
  SUM(credits_used) AS credits
FROM snowflake.account_usage.warehouse_metering_history
WHERE start_time > DATEADD(day, -90, CURRENT_DATE)
GROUP BY 1, 2
ORDER BY day, credits DESC;
```

In BigQuery:

```sql
-- Cost by user, by day, last 90 days
SELECT
  user_email,
  DATE(creation_time) AS day,
  SUM(total_bytes_billed) / POW(2,40) AS tib_billed,
  SUM(total_bytes_billed) / POW(2,40) * 6.25 AS approx_usd  -- on-demand pricing
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
GROUP BY 1, 2
ORDER BY 2, 4 DESC;
```

I run three slices:

1. **By day.** Where did the increase start?
2. **By user / service account.** Which team or pipeline is responsible?
3. **By query hash or destination table.** Which specific jobs are expensive?

Almost always, a chart shows the inflection point and a single user or service account explains most of the increase.

### Step 2: find the top offenders

The 80/20 rule holds in warehouse cost. Five to ten queries usually explain 70 to 90 percent of the growth.

```sql
-- BigQuery: top jobs by cost, last 30 days
SELECT
  query,
  user_email,
  COUNT(*) AS runs,
  SUM(total_bytes_billed) / POW(2,40) AS tib_billed
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND job_type = 'QUERY'
GROUP BY 1, 2
ORDER BY tib_billed DESC
LIMIT 20;
```

For each top offender, I want three answers:

* What is it for?
* Does it need to run as often as it does?
* Can it scan less?

The investigation usually finds:

1. **A new scheduled query** runs every hour, scans 500 GB of unpartitioned data, returns 10 rows. Easy win.
2. **A dashboard refresh** every 5 minutes, even though the data is daily. Easy win.
3. **A `SELECT *` from a 3 TB table** in a notebook somebody forgot about. Easy win.
4. **A model rebuild** that grew from 100 GB to 800 GB because the data grew. This is real growth, not waste.

### Step 3: framing for finance

Finance wants a number and a number. Not a journey.

> "The increase from $14k to $28k breaks down as: 60% (~$8.4k) is three scheduled queries that scan full table partitions when they only need yesterday. 20% (~$2.8k) is a dashboard that auto-refreshes 12 times an hour. 20% (~$2.8k) is real growth as our user base grew 30% this quarter.
>
> The first 80% can be addressed this week without breaking any user experience. I expect to land back around $16-17k next month.
>
> The remaining $3k is real growth; if revenue tracks, it should not concern us, but we will keep watching."

Three properties of a good finance message: a specific decomposition, a clear "what is fixable," and a forward number.

### Step 4: framing for engineering

Engineering does not want a number; they want options and impact.

> "Here are five changes. Each one I have estimated the savings, the risk, and the work.
>
> 1. Partition-prune the `daily_metrics_rollup` scheduled query (5 lines change). Save ~$3k/mo. Zero downstream impact.
> 2. Cap the dashboard auto-refresh to once per hour (dashboard config). Save ~$1.5k/mo. Users will notice "last refreshed an hour ago" but data is daily anyway.
> 3. Replace the abandoned notebook's nightly run by stopping the schedule. Save ~$1k/mo. Confirmed with the owner — they forgot it existed.
> 4. Materialize the heaviest dashboard query into a daily table (~$0.5k/mo savings, modest dbt work).
> 5. (Longer term) Adopt a query-tagging convention and per-team budgets.
>
> Total savings: about $6k/mo by next Wednesday. I will need ~half a day."

Note that I'm not asking for permission. I am proposing changes with their impact named. Engineering can push back on the dashboard refresh policy if they want to, but the proposal is on the table.

### The 80/20 list of fixes I would always check

1. **Unpartitioned scans on partitioned tables.** `WHERE date >= ...` is missing or wraps the date in a function.
2. **`SELECT *` from wide tables.** Especially in dashboards and notebooks. Costs you bytes-billed for every column.
3. **Dashboard auto-refresh** at higher frequency than the data changes.
4. **No materialised views or summary tables** for queries that run every hour and re-aggregate the same data.
5. **Massive joins where one side is huge and unfiltered.** A small WHERE moved before the join saves 90 percent.
6. **Compute warehouses left running** with too high a size, or auto-suspend turned off (Snowflake-specific).
7. **dbt `--full-refresh` running daily by accident.** Should be incremental.

### Long term: governance, not just optimization

After the immediate fixes, the goal is for this not to recur. I would propose:

* **Query tags.** Every dbt model, every dashboard, every scheduled query carries a tag (`team:`, `purpose:`, `dataset:`). Cost reports group by tag.
* **A weekly cost report.** Distributed automatically. Each team sees their own number.
* **A budget per team.** Soft for now: a Slack alert when a team is on pace to exceed the monthly budget. Hard later if needed.
* **A "before merging an expensive query" review rule.** dbt and the warehouse make this easy with dry runs.
* **Reserved capacity or commitments** if costs are stable enough. BigQuery slots or Snowflake commitments can save 30-50 percent vs on-demand once usage is predictable.

### The conversation with finance going forward

The relationship matters as much as the numbers. After this incident:

* Send finance a one-paragraph monthly summary, even when costs are flat. They do not have to chase me.
* Pre-warn them before a known cost-up event ("we are loading historical data next week, this will be a one-time spike").
* Have a rough rule of thumb for "cost per active user" or "cost per revenue dollar." That makes the conversation about value, not just spend.

### Common mistakes interviewers want you to name

1. **Adding more compute.** Some teams react to high cost by buying reserved capacity that locks in the inflated usage.
2. **Optimizing in the dark.** Without the usage tables, you guess.
3. **Killing a query without finding its owner.** Outages incoming.
4. **One-time fix, no follow-up.** Same problem in 3 months.
5. **Not telling the team what was fixed.** Bills drop, no one knows why, behavior repeats.

### Bonus follow-up the interviewer might throw

> *"What if cost is up but utilization is up too, and the team genuinely needs the data?"*

Then the conversation is about value, not cost. Show finance the metric: "cost per active user," "cost per dollar of revenue analyzed," whatever fits the business. If costs are growing slower than the business, you are doing fine. If they are growing faster, the optimisation work above is still useful, but the bigger question is "can we get to per-slot or reserved pricing now that we have a steady baseline."
