## Solution 66: Indexes: When to Add and When They Hurt

### Short version you can say out loud

> An index is a separate sorted copy of one or more columns that lets the database jump to the rows it wants instead of scanning the whole table. They are great when a query filters or joins on a column that has many distinct values and the query returns a small fraction of the table. They are bad when the column has few distinct values, when most queries return most of the rows anyway, or when the table is write-heavy and the index just slows every insert without paying off for reads. The rule of thumb is: add an index for a specific query that needs it, not "just in case."

### What an index actually is

```
Table: users  (10 million rows)
─────────────────────────────────
id │ email           │ country │ created_at
1  │ a@example.com   │ SG      │ 2024-01-12
2  │ b@example.com   │ MY      │ 2024-02-03
…

Index on (email):
   "a@example.com" → row 1
   "b@example.com" → row 2
   "c@example.com" → row 5
   …  (B-tree, sorted)

SELECT * FROM users WHERE email = 'b@example.com';
 → index seek finds row 2 in microseconds, instead of scanning 10M rows.
```

The index is a B-tree (in almost every relational database) keyed on the indexed columns. Lookups are O(log N) instead of O(N).

### When an index is the right answer

1. **The query filters on a column that has many distinct values.** `WHERE user_id = ...`, `WHERE email = ...`, `WHERE order_id = ...`. The index dramatically reduces the rows read.
2. **The query joins on a foreign key.** An index on the foreign key turns the join from a hash or merge into a fast lookup.
3. **The query sorts on a column.** A B-tree index is already sorted, so `ORDER BY indexed_col` can skip the sort step.
4. **A unique business identifier.** Even if you do not query by it often, a unique index enforces correctness (`email`, `username`).
5. **A column you filter by very often, even if the cardinality is moderate.** Sometimes worth it for a hot query.

### When an index is the wrong answer

1. **Low-cardinality columns.** A boolean `is_active` column has 2 values. An index on it usually returns half the table. Index ignored, write cost paid for nothing.
2. **Tiny tables.** Anything under a few thousand rows. A full scan is faster than an index lookup.
3. **Heavy write tables with rarely-used columns.** Every insert, update, and delete has to maintain the index. If reads don't use it, it is pure cost.
4. **A column you wrap in a function.** `WHERE LOWER(email) = ...` cannot use a plain `email` index. You need either a different query or a functional index.
5. **A column that is going to be filtered out by `WHERE` but the result still returns most rows.** Like `WHERE status != 'archived'` on a table where 1% of rows are archived. The optimizer often does a sequential scan anyway.

### The write cost

Every index makes writes slower:

* **Insert**: write to the table, write to each index.
* **Update**: write to the table, update each index whose columns changed.
* **Delete**: write to the table, delete from each index.

A table with 10 indexes has roughly 10x the write amplification of a table with one. For a high-throughput OLTP table, that can be the difference between 10,000 writes/sec and 1,000 writes/sec.

The teammate in the scenario is hitting exactly this: every column got an index, writes slowed down, reads got marginally faster.

### Composite indexes and column order

`CREATE INDEX ON orders (customer_id, created_at);`

This index helps:

* `WHERE customer_id = 42`
* `WHERE customer_id = 42 AND created_at > '2025-01-01'`
* `WHERE customer_id = 42 ORDER BY created_at`

But NOT:

* `WHERE created_at > '2025-01-01'` (left column missing)

Order matters: put the most-filtered column first. The rule "left-prefix matches" is universal across B-tree indexes.

### Covering indexes

If the index includes every column the query reads, the database doesn't even need to touch the table.

```sql
CREATE INDEX ix_orders_cust_date_amount ON orders (customer_id, created_at) INCLUDE (amount);

SELECT amount FROM orders WHERE customer_id = 42 AND created_at > '2025-01-01';
-- → index-only scan, no table access at all.
```

Worth it for hot read paths. Not worth it for every query.

### The "looks fine in dev, slow in prod" trap

A 10,000-row dev table is fast no matter what. A 100M-row prod table needs the right index. Three habits:

* Test query plans on prod-scale data, not dev.
* Run `EXPLAIN ANALYZE` before adding the index, and after.
* Watch `pg_stat_user_indexes` (Postgres) or equivalent to see which indexes are actually used. Drop the ones nobody uses.

### How to add an index responsibly

1. **Find the slow query.** Not "indexes I might want."
2. **Read its plan.** Confirm the bottleneck is a scan.
3. **Pick the smallest index that helps.** One column if you can, two if you must, three rarely.
4. **Create it CONCURRENTLY** in Postgres (or with low priority in your engine), so it doesn't lock writes.
5. **Re-run EXPLAIN.** Confirm the optimizer uses it.
6. **Check write impact** on production for a day. Sometimes the cost is real and you need to revisit.

### Common mistakes interviewers want you to name

1. **Index every column "just in case."** Write cost compounds; reads don't get faster.
2. **Index a boolean.** Almost never helps.
3. **Function on the indexed column.** Index is bypassed silently.
4. **Composite index with the wrong order.** Half the queries miss it.
5. **Never drop unused indexes.** They accumulate over years and slow every write.

### Bonus follow-up the interviewer might throw

> *"How do you find unused indexes in production?"*

In Postgres:

```sql
SELECT schemaname, relname AS table, indexrelname AS index, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

`idx_scan = 0` means the index has not been used since the stats were reset. Drop after confirming with the team and watching for one more week (some indexes are used only in monthly jobs). Each engine has an equivalent.
