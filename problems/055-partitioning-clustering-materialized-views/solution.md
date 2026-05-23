## Solution 55: Partitioning, Clustering, Materialized Views

### Short version you can say out loud

> Partitioning lets BigQuery skip whole chunks of the table when your WHERE filters on the partition column. Clustering lets it skip storage blocks inside a partition when your WHERE filters on the cluster columns. Materialized views let it skip the whole computation when you ask for the same aggregate again. They stack: partition first, then cluster, then materialize the heavy aggregates that read this layout. Most cost savings come from getting these three things right.

### One sentence each

* **Partitioning** physically splits the table into pieces (usually by date), so queries that filter on the partition column read only the relevant pieces.
* **Clustering** sorts rows inside each partition by chosen columns, so queries that filter on those columns skip blocks that cannot match.
* **Materialized view** stores the result of an expensive aggregation once and updates it as new data arrives, so repeated queries read pennies instead of terabytes.

### Where they save money

```
Table: events  (8 billion rows, 4 TB)
Query: SELECT COUNT(*) FROM events WHERE event_date = '2025-05-14';

Without anything                            Cost: 4 TB scan = expensive
Partitioned by event_date                   Cost: 1/365 of the table = $X / 365
Clustered by event_type after partition     Cost: even smaller for filtered subsets
Materialized view of daily counts           Cost: <1 GB, pennies
```

Each layer adds a multiplier of savings, applied to different shapes of query.

### When to use partitioning

Partition by the column that almost every query filters on. For event/log tables that is usually `event_date` or `created_at`. Rule: at most ~4,000 partitions in BigQuery, so do NOT partition by a high-cardinality column like `customer_id`.

```sql
CREATE TABLE analytics.events (
  event_date DATE,
  user_id INT64,
  event_type STRING,
  payload JSON
)
PARTITION BY event_date;
```

After partitioning, queries that include `WHERE event_date =...` prune to one partition. Queries that omit the partition filter still scan the whole table.

### When to use clustering

Cluster on columns that you filter or join on, that are NOT the partition column. Up to four columns. Order matters: most-filtered column first.

```sql
CREATE TABLE analytics.events (
  event_date DATE,
  user_id INT64,
  event_type STRING,
  payload JSON
)
PARTITION BY event_date
CLUSTER BY user_id, event_type;
```

Now `WHERE event_date = '2025-05-14' AND user_id = 1234` is cheap: BigQuery prunes to one partition, then uses block metadata to skip blocks that cannot contain `user_id = 1234`.

Clustering is not an index. It is a sort order plus per-block min/max. So it helps for **equality and range filters** on the clustered columns, and for joins on those columns. It does not help for arbitrary substring searches.

### When to use materialized views

When the same expensive aggregate is asked for repeatedly. Examples:

* Daily revenue by region.
* Active users per day.
* Top products by month.

```sql
CREATE MATERIALIZED VIEW analytics.daily_revenue_by_region AS
SELECT
  event_date,
  region,
  SUM(amount) AS revenue,
  COUNT(*) AS orders
FROM analytics.events
WHERE event_type = 'purchase'
GROUP BY event_date, region;
```

BigQuery maintains the MV automatically as new rows are inserted. Queries against the original table that match the MV's pattern are automatically rewritten to use the MV. Even queries that need to combine with the MV partially are sometimes optimized.

Storage of the MV is usually small (rolled-up data). Cost is the small storage plus the maintenance, which is far less than the repeated full scans.

### When to use which

| Situation | Tool |
| --------- | ---- |
| Query always filters on a date column | Partition by that date |
| Query filters on a high-cardinality column | Cluster on that column |
| Query joins on a column | Cluster on the join column (both sides) |
| Same aggregate asked many times | Materialized view |
| Mix of filtered + aggregated queries on the same table | Partition + cluster + MV |

### The stacking principle

These compose:

* Partition first. Pick the column you filter on in 80 percent of queries.
* Then cluster. Pick up to four columns you filter or join on next.
* Then materialize. Only the aggregates that are run often enough to justify the maintenance.

A typical large analytics table ends up with all three:

```sql
CREATE TABLE analytics.events ...
PARTITION BY event_date
CLUSTER BY user_id, event_type;

CREATE MATERIALIZED VIEW analytics.daily_user_counts AS
SELECT event_date, COUNT(DISTINCT user_id) AS dau
FROM analytics.events
GROUP BY event_date;
```

A query for "active users by day last quarter" hits the MV. Cost: cents.
A query for "all events for user 1234 last week" hits the partition + cluster. Cost: a few MB scan.
An ad-hoc query on a column we did not cluster on falls back to the partition. Cost: more, but still bounded to one day.

### Things that look like savings but are not

* **Adding indexes.** BigQuery does not have traditional indexes. Clustering is the closest thing.
* **Caching.** BigQuery caches query results for 24 hours by default, but only for identical queries. Useful, not a substitute.
* **Wide pre-joined tables** without thinking. Sometimes save cost, sometimes hurt because rows are bigger.

### Common mistakes interviewers want you to name

1. **Partitioning by a high-cardinality column** like `user_id`. Hits the 4000-partition limit fast.
2. **Querying without the partition filter.** The partition does nothing.
3. **Clustering on too many columns.** After the first 2-3, returns diminish, and the order may be wrong for new queries.
4. **Materialized view without checking it actually gets used.** BigQuery only auto-rewrites if the query matches the MV pattern. Otherwise you pay the MV maintenance for nothing.
5. **Trying to retrofit on a huge table.** Repartitioning a 50 TB table takes hours. Plan from day one.

### Quick rule of thumb

If your team is asking "should we partition or cluster?" the answer is almost always **both**. They serve different purposes. Materialized views come third, when a specific aggregate justifies the maintenance.

### Bonus follow-up the interviewer might throw

> *"What if the team doesn't know yet what columns to cluster on?"*

Three steps:

1. Look at INFORMATION_SCHEMA.JOBS_BY_PROJECT for the past 30 days. Find the top 10 queries against that table.
2. Look at their WHERE clauses and JOIN conditions. The columns that appear most often are your cluster candidates.
3. Recreate the table with `PARTITION BY date CLUSTER BY top_columns`. Measure scan size before vs after.

Empirical, not guessed. The data tells you the right clustering.
