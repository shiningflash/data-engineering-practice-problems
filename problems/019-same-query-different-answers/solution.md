## Solution 19: Same Query, Different Answers

### Short version you can say out loud

> When a query gives different numbers in two environments and the data is "supposed to be the same," the data is almost never actually the same. I check seven things, in this order: time zones, row-level security or filtered views, late-arriving rows, exact table identity, session settings, collation and case sensitivity, and whether one environment has materialized views or aggregates that the other doesn't. About 90 percent of the time it is one of the first three.

### My mental order of checks

```
1. Time zone difference?     ← starts here most often
2. Row-level security / views the user can see?
3. Late-arriving rows: when was each snapshot taken?
4. Are you really reading the same table?
5. Session settings (date format, locale, NULLs ordering)?
6. Collation / case sensitivity / trim differences?
7. Materialized views or aggregated layers?
```

Let me walk through each.

### 1. Time zones

The single most common cause. The query has a date filter like:

```sql
WHERE created_at >= '2025-05-14'
```

In dev, the database time zone is UTC. In production, it is America/New_York. The exact same data, the exact same filter, returns different rows because midnight is at a different moment.

Or worse, the data was inserted with timestamps in one zone, and the query interprets them in another:

```sql
-- dev session
SHOW TIMEZONE; -- UTC
SELECT NOW();  -- 2025-05-14 23:50:00+00

-- production session
SHOW TIMEZONE; -- America/New_York
SELECT NOW();  -- 2025-05-14 19:50:00-04
```

How I check: run `SHOW TIMEZONE` and `SELECT CURRENT_SETTING('TimeZone')` in both. Compare. Or even simpler: rerun the query with explicit UTC bounds, like `created_at >= '2025-05-14 00:00:00 UTC'`, in both environments.

### 2. Row-level security or views the user can see

In dev I often log in as a power user or admin. In production I might be running as a service account with row-level security policies. The same query then returns a subset.

Examples:

* A view that filters `WHERE tenant_id = current_tenant()` exists in prod but not in dev.
* A row-level security policy hides rows from non-owner users.
* The table in production is actually a sharded view, and the user only sees some shards.

How I check: run a quick `SELECT COUNT(*) FROM the_table` as both users on production. If they differ, I'm hitting RLS or a filtered view.

### 3. Late-arriving rows

You took a dev snapshot at 6 AM. Production keeps getting new rows during the day. When you run the query in production at 3 PM, the result includes 9 more hours of data.

How I check: pick a stable lower bound. `WHERE created_at < '2025-05-14 06:00:00 UTC'` in both. If now they match, the difference was just freshness.

### 4. Are you really reading the same table?

It sounds silly but it bites people often.

* In dev, the analyst pointed at `analytics.orders`.
* In prod, "analytics.orders" is actually a view over `raw.orders` joined to `customers` with an inner join, which drops orders for deleted customers.
* Or the search path is different and you are reading a totally different schema.

How I check:

```sql
SELECT pg_get_viewdef('analytics.orders', true);  -- Postgres
-- Or in BigQuery
SELECT ddl FROM `project.dataset.INFORMATION_SCHEMA.VIEWS`
WHERE table_name = 'orders';
```

Compare the DDL. The view definitions sometimes differ between environments.

### 5. Session settings

A few that quietly change query results:

* `lc_collate` and `lc_ctype` affect string sorting and comparison.
* `default_text_search_config` affects `LIKE` and full-text search behavior.
* `null_first` vs `null_last` in ORDER BY can swap row order, which matters if you use `LIMIT N`.
* In BigQuery and Snowflake, default time zone for unparsed timestamps.

How I check: dump the relevant session settings. `SHOW ALL` in Postgres. `SHOW PARAMETERS` in Snowflake. Compare.

### 6. Collation and case sensitivity

This one is sneaky. A WHERE clause like:

```sql
WHERE country = 'sg'
```

* On a case-insensitive collation, matches `SG`, `sg`, `Sg`.
* On a case-sensitive collation, matches only `sg`.

Or trailing whitespace. `'SG'` and `'SG '` look the same on screen but compare unequal.

How I check: run `SELECT DISTINCT country, LENGTH(country) FROM orders WHERE LOWER(country) = 'sg'` and look for surprises.

### 7. Materialized views or aggregated layers

You think you queried the raw table, but in prod the query is silently rewritten to use a materialized view that lags behind. Some warehouses do this automatically (BigQuery materialized views, Oracle's query rewrite). The MV may have been built at 4 AM and is missing 11 hours of data.

How I check: check the query plan in prod. Look for a different table name than expected. In BigQuery, look at "referenced tables" in the job details.

### A short script I would run in both environments

```sql
-- Where are we?
SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_USER, CURRENT_TIMEZONE();

-- What does the table say?
SELECT COUNT(*) AS total,
       MIN(created_at) AS first_row,
       MAX(created_at) AS last_row
FROM the_table;

-- How does it look in UTC?
SELECT COUNT(*)
FROM the_table
WHERE created_at AT TIME ZONE 'UTC' >= '2025-05-14 00:00:00'
  AND created_at AT TIME ZONE 'UTC' <  '2025-05-15 00:00:00';
```

Comparing these three between dev and prod will catch the cause in almost every case I have seen.

### Why this kind of bug is so common

Because "the data is the same" is almost always wrong in subtle ways. Dev environments are usually:

* Refreshed at a fixed time, not continuously.
* Anonymized, which can subtly change row counts or distributions.
* Run with different user permissions.
* Configured with different session defaults.

The fix is not paranoia in queries. The fix is to make environment differences observable. A simple "where am I" header at the top of every notebook saves hours of confusion.

### Common mistakes interviewers want you to name

1. **Assuming dev = prod.** It almost never is.
2. **Trusting LIMIT in dev.** Different ORDER BY ties make LIMIT non-deterministic. Numbers can match in count but the actual rows differ.
3. **Running `EXPLAIN` only in dev.** A different plan in prod can mean a different result if the query has subtle ordering bugs.
4. **Ignoring NULL handling.** `COUNT(col)` vs `COUNT(*)` behaves differently with NULLs. If a column has more NULLs in one environment, the counts differ.

### Bonus follow-up the interviewer might throw

> *"How would you make this kind of bug less likely going forward?"*

Three habits help:

1. **Always include a deterministic time bound.** No `WHERE date >= CURRENT_DATE`. Make the bound explicit and absolute.
2. **Use the same time zone in all environments.** UTC is the cheap default.
3. **Snapshot dev data with a recorded `as_of` timestamp** and include that timestamp in the query when comparing. You will catch freshness mismatches in the first 30 seconds.
