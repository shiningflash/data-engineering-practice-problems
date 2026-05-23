## Solution 17: Reading an EXPLAIN Plan

### Short version you can say out loud

> EXPLAIN shows the engine's plan for running my query. I read it inside out because that's the order it executes. The four things I look at first: where it scans the biggest tables (Seq Scan vs Index Scan), the join types it picked, the gap between estimated and actual rows, and any Sort or Hash that spilled to disk. Those four account for maybe 80% of slow queries.

### EXPLAIN vs EXPLAIN ANALYZE

`EXPLAIN` shows the planner's guess of what it'll do. Cheap, returns instantly.

`EXPLAIN ANALYZE` actually runs the query and gives you real timing and real row counts. This is the one you want when debugging.

One catch: `EXPLAIN ANALYZE` runs the query, including any side effects. Don't `EXPLAIN ANALYZE` a `DELETE` unless you mean it.

### A sample plan to read together

```
EXPLAIN ANALYZE
SELECT c.country, SUM(o.amount)
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.created_at >= '2025-01-01'
GROUP BY c.country;
```

Output (Postgres-style, simplified):

```
HashAggregate  (cost=120000.00..120004.00 rows=4 width=40)
                (actual time=8421.5..8421.7 rows=4 loops=1)
  Group Key: c.country
  ->  Hash Join  (cost=2500.00..115000.00 rows=2000000 width=18)
                  (actual time=180.2..7900.0 rows=1850000 loops=1)
        Hash Cond: (o.customer_id = c.id)
        ->  Seq Scan on orders o  (cost=0.00..100000.00 rows=2000000 width=12)
                                   (actual time=0.05..3500 rows=1850000 loops=1)
              Filter: (created_at >= '2025-01-01')
              Rows Removed by Filter: 6150000
        ->  Hash  (cost=2000.00..2000.00 rows=200000 width=14)
                   (actual time=160 rows=200000 loops=1)
              ->  Seq Scan on customers c  (rows=200000)
Planning Time: 0.5 ms
Execution Time: 8422 ms
```

Don't panic. Read it inside out.

### How to read it, step by step

**1. Find the innermost steps first.**
The plan is a tree. The innermost nodes (deepest indentation) run first. Here that's the two `Seq Scan` nodes. Reading inside out:

```
Seq Scan on orders → filter by date         (3.5 seconds, returns 1.85M rows)
Seq Scan on customers → loaded into a Hash  (0.16 seconds)
Hash Join the two                            (7.9 seconds total)
HashAggregate the result                     (8.42 seconds total)
```

**2. Look at the biggest time.**
The biggest jump is the join itself: 3.5 seconds for the orders scan, but 7.9 seconds total at the join level means the join phase ate ~4 seconds. That's where to focus.

**3. Compare estimated rows to actual rows.**
The planner estimated 2,000,000 rows from the orders scan and got 1,850,000. Close enough. If those numbers were off by 100x (say, estimate 20,000, actual 2,000,000) the optimizer was probably picking a bad plan. Fix with `ANALYZE` on the table or by updating stats.

**4. Check for the red flags.**

| Red flag | What it usually means |
| --------------------------------- | ------------------------------------------------------ |
| `Seq Scan` on a huge table | Missing index, function on indexed column, or `SELECT *` |
| `Nested Loop` over millions | Optimizer thought one side was tiny. It wasn't. |
| `Hash` with a huge build side | The "smaller" side isn't small. Memory pressure. |
| `Sort` writing to disk | Working set didn't fit in memory. Slow. |
| Estimate vs actual off by 10x+ | Bad stats, planner is flying blind. |
| `Rows Removed by Filter` very high | You read 8M rows to keep 100k. Filter earlier. |

### Join types you'll see, in plain words

* **Nested Loop**: for each row on the left, look up matching rows on the right. Cheap when one side is tiny and the other has an index. Disastrous when both sides are big.
* **Hash Join**: build a hash table on one side (the "build" side), probe it from the other. Best when both sides are medium to large. Cost is roughly read both sides once.
* **Merge Join**: both sides are sorted on the join key, then merged. Used when the optimizer already has both sides sorted, or for very large joins where hashing wouldn't fit in memory.

The most common bad plan you'll see: a Nested Loop the optimizer chose because it thought the outer side was tiny, but it wasn't. The fix is usually to update stats or rewrite the filter.

### Things to do once you spot a problem

* **Seq Scan on a filtered query**: add an index on the filter column, or rewrite to remove a function on the indexed column.
* **Bad estimate**: `ANALYZE <table>` to refresh stats. Sometimes increase `default_statistics_target` for skewed columns.
* **Nested Loop bug**: try forcing a hash join with hints (`pg_hint_plan` in Postgres) or rewrite to give the optimizer a clearer shape.
* **Sort to disk**: increase `work_mem` for that session, or add an index that produces presorted output, or reduce the data you sort.

### EXPLAIN on BigQuery, Snowflake, etc.

Each engine shows it differently:

* **BigQuery** shows an execution plan in the job details: stages, slot time, rows in/out, bytes shuffled. First look at `bytes processed` (cost) and `slot time` (the actual work). Big shuffle stages are the equivalent of a sort spill.
* **Snowflake** shows a graph in the UI. Click the slowest box. Look for "remote disk I/O" (bad), "spilling to local storage" (bad), and "broadcast vs hash partitioned" joins.
* **Spark** has `df.explain(True)` for the logical plan and the Spark UI for the physical execution.

Different vocabulary, same lens: find the biggest box, check estimate vs actual, look for red flags.

### A 30-second checklist to keep in your head

When you see a plan:

1. Look at the **total time** at the top.
2. Find the **biggest single step**.
3. Is it a Seq Scan on a big table? Why? Can you add an index or filter earlier?
4. Are the row estimates off?
5. Is anything spilling to disk (Sort, Hash)?
6. What join types were chosen? Do they make sense for the sizes?

### Bonus follow-up the interviewer might throw

> *"What if the plan looks fine but the query is still slow?"*

Two common causes:

1. Lock contention. The query is fast in isolation but waits behind other transactions. Check `pg_stat_activity` or your engine's equivalent.
2. Cold cache. First run hits disk, second hits memory. Run the query twice and compare. If the second run is much faster, you're I/O bound. Either accept the cold cost, warm the cache deliberately, or rebuild the table to be smaller (drop unused columns, partition).
