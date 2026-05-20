## Solution 6: Partitioning vs Clustering in BigQuery

### Short version you can say out loud

> Partitioning splits a table into separate physical buckets, usually by date. Clustering sorts the rows inside each bucket by one or more columns. Partitioning helps BigQuery skip whole chunks of the table, clustering helps it skip blocks inside a chunk. In practice you partition by a low cardinality column you almost always filter on (like date), and you cluster by the high cardinality columns you filter or join on (like `customer_id` or `event_type`).

### Picture it

```
Unpartitioned, unclustered table (8B rows)
┌──────────────────────────────────────────────┐
│ row row row row row row row row row row …    │
└──────────────────────────────────────────────┘
A query with WHERE event_date = '2025-05-01' scans ALL of it.


Partitioned by event_date
┌──── 2025-04-30 ────┐ ┌──── 2025-05-01 ────┐ ┌──── 2025-05-02 ────┐
│ rows for that day  │ │ rows for that day  │ │ rows for that day  │
└────────────────────┘ └────────────────────┘ └────────────────────┘
Same query now scans ONE partition.


Partitioned by event_date AND clustered by customer_id
┌──── 2025-05-01 ────────────────────────────────────────────┐
│ customer_id=1001..1500   block A                            │
│ customer_id=1501..2000   block B                            │
│ customer_id=2001..2500   block C                            │
└─────────────────────────────────────────────────────────────┘
WHERE event_date = '2025-05-01' AND customer_id = 1750
→ BigQuery jumps to block B only.
```

### What each one actually is

**Partitioning** is a physical split. BigQuery stores each partition as a separate unit. When your `WHERE` clause filters on the partition column, BigQuery prunes the other partitions before it even starts scanning. This is the single biggest cost lever in BigQuery, because BigQuery charges by bytes scanned.

You can partition by:
* Ingestion time (the default, `_PARTITIONTIME`)
* A date or timestamp column (`event_date`, `created_at`)
* An integer range (rare, but useful for tenant ids in some setups)

**Clustering** is a sort order. Inside each partition, rows are kept sorted by the cluster columns. BigQuery also keeps lightweight metadata about the value ranges in each storage block. When your `WHERE` filters on a clustered column, BigQuery uses that metadata to skip blocks that cannot match.

You can cluster on up to four columns. Order matters: the first clustering column gives the biggest skip, then the next, and so on.

### Concrete example

```sql
-- A typical pattern for an events table
CREATE TABLE analytics.events (
  event_date DATE,
  customer_id INT64,
  event_type STRING,
  payload JSON
)
PARTITION BY event_date
CLUSTER BY customer_id, event_type;
```

Query A:
```sql
SELECT COUNT(*)
FROM analytics.events
WHERE event_date = '2025-05-01';
```
BigQuery scans one partition, ignores the other 364.

Query B:
```sql
SELECT *
FROM analytics.events
WHERE event_date = '2025-05-01'
  AND customer_id = 1750
  AND event_type = 'purchase';
```
BigQuery scans one partition, then uses the clustering metadata to read only the storage blocks that contain `customer_id = 1750` and inside those, the blocks that contain `event_type = 'purchase'`. The cost can drop by orders of magnitude.

Query C (the trap):
```sql
SELECT *
FROM analytics.events
WHERE customer_id = 1750;
```
No partition filter, so BigQuery scans every partition. Clustering still helps, but the partition prune is gone. This is the most common mistake.

### When to use which

| Situation                                                  | What to use                                           |
| ---------------------------------------------------------- | ----------------------------------------------------- |
| Almost every query filters on a date                       | **Partition** by that date column                     |
| Queries filter on a high cardinality column (`customer_id`, `device_id`) | **Cluster** on that column                            |
| Both of the above                                          | **Partition + cluster** (the most common pattern)     |
| The table is small (under ~1 GB)                           | Skip both. The overhead is not worth it.              |
| You filter by a low cardinality column with only 2 to 10 values (`country`) | **Cluster**, not partition. Partitioning by something with 5 values is wasteful. |

### Rule of thumb to remember

* **Partition first.** Pick the column you filter on in 80 percent of queries. Usually a date.
* **Cluster second.** Pick up to four columns you filter or join on, in order of how often they appear in `WHERE` and `JOIN ON`.
* **Always include the partition filter in your queries.** If you forget, you pay for the full table.

### Common mistakes interviewers want you to name

1. Partitioning by a column that does not appear in most `WHERE` clauses. The table is just split for no benefit.
2. Forgetting the partition filter in the query. Cost stays the same.
3. Partitioning by a high cardinality column like `customer_id`. You can hit BigQuery's 4,000 partition limit very fast.
4. Clustering by too many columns. After four, you get nothing extra, and the order you picked may no longer be the most selective.
5. Thinking clustering is "an index." It is not. There is no random lookup, only block pruning.

### Bonus follow-up the interviewer might throw

> *"What if my queries change over time and the clustering becomes useless?"*

You can run `ALTER TABLE ... ALTER COLUMN` to change clustering, but BigQuery only re-clusters as it writes new data and during background optimizations. For a heavily queried table, you may want to use `CREATE TABLE AS SELECT` into a freshly clustered copy and swap names, which guarantees the new order from day one.
