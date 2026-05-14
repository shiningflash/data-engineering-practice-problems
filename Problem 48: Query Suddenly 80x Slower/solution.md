## Solution 48: Query Suddenly 80x Slower

### Short version you can say out loud

> First thing I do is compare the query plan today against the plan from when it was fast. Most of these incidents have the same shape: a join changed strategy because one side crossed a size threshold. The query did not change, but the data did, and the optimizer made a different choice. The cure is almost never "more compute." It is finding which join flipped and helping the optimizer pick the right plan, often by updating statistics or adding a small hint.

### The diagnostic order

**1. Get the plan from today.**

```sql
EXPLAIN ANALYZE <the slow query>;
```

**2. Get the plan from when it was fast.**

* If the team uses an APM tool that records plans, retrieve last week's.
* In BigQuery, you can find the past job and inspect its execution.
* In Snowflake, query_history retains plans for some time.
* Otherwise, try to reconstruct: run the same query on a snapshot of last week's data if you have one.

**3. Diff the two plans.**

Look for:

* Join type changed (Hash → Nested Loop, or broadcast → hash).
* Scan changed from index/cluster prune to full scan.
* Sort that now spills to disk (writes to temporary storage).
* Estimated rows vs actual rows now wildly off.

The diff almost always tells you the bug in two minutes.

### The classic causes when the query didn't change

**1. A join flipped from broadcast to hash because the small side grew.**

A query that used to broadcast a "small dimension" of 10 MB now broadcasts 5 GB because the dimension grew. The optimizer either picks a slow plan or runs out of memory. Fix: either cap the broadcast size, force a hash join, or shrink the dimension.

**2. Statistics are stale.**

The table grew 10x but `ANALYZE` was never re-run. The optimizer thinks the table has 100k rows, picks a nested loop because "the other side is huge anyway," and the nested loop runs over 10M rows.

Fix:

```sql
-- Postgres
ANALYZE my_table;

-- BigQuery / Snowflake usually keep stats current automatically, but
-- if a CTAS just created the table, stats may not be present yet.
```

**3. A new column or change made a filter unselective.**

A `WHERE status = 'active'` used to match 5% of rows. After a backfill, 95% of rows are 'active'. The plan optimizer's choices invert: what was a good index is now bad.

Fix: either change the query, add a better partition / cluster, or use a different filter.

**4. Storage layout changed.**

In BigQuery: someone deleted and reinserted the partition with a different cluster ordering. In Postgres: heavy churn caused table bloat. In Snowflake: clustering depth got bad and the table needs reclustering.

Fix: rebuild the table or trigger reclustering.

**5. Resource contention from a noisy neighbor.**

Another team launched a daily 6 PM job that uses the same warehouse. Your 6 PM query now waits for slots.

Fix: separate warehouses or schedule shift.

**6. A new index or constraint slowed writes** (and the query happens to involve a temp table with an unexpected lock).

This is the OLTP version. Less common in warehouses.

### A real diagnostic walkthrough

Yesterday's plan:

```
HashJoin
  ├ HashAggregate over fact (returns ~10k rows)
  └ SeqScan over dim_region (5 rows)
```

Today's plan:

```
NestedLoop
  ├ SeqScan over fact (returns ~10M rows)
  └ IndexScan over dim_region
```

The reading: `dim_region` did not change, but `fact` did. The optimizer thinks `fact` is small now (statistics are stale) and picked a nested loop. Each `fact` row triggers a lookup in `dim_region`. With 10M rows in fact, that is 10M index lookups.

Fix: `ANALYZE fact`. The optimizer now sees the real row count and re-picks the hash join. Query goes back to 30 seconds.

### What I would NOT do first

* **Throw more compute at it.** Sometimes works, but you do not learn anything, and the problem grows back.
* **Rewrite the query.** Not yet. The query was fine last week.
* **Restart the warehouse.** Cargo-cult fix; rarely solves anything but feels productive.

### Other things to check quickly

* **Did the underlying tables grow a lot?** 10x growth often crosses an optimizer threshold.
* **Was there a schema change overnight?** Adding a column can change row width and storage.
* **Are there new materialized views or indexes** that the optimizer might be choosing badly?
* **Is the warehouse the same size?** A teammate accidentally downsized the Snowflake warehouse.
* **Are you actually reading the same table?** A view definition changed, or a search path changed.

### Prevention

Three habits help:

1. **Tag and time critical queries.** A daily job that times itself and alerts on >2x slowdown catches this on day one.
2. **Periodic `ANALYZE`** on growing tables. Most warehouses do this automatically, but some configurations require it.
3. **Pin the plan when it really matters.** Some engines support plan hints (BigQuery has limited hints; Postgres has `pg_hint_plan`). For a critical job, locking the plan removes the surprise.

### Common mistakes interviewers want you to name

1. **Reaching for more compute first.** Wastes money and time.
2. **Not capturing the plan when it was fast.** Then you cannot compare.
3. **Skipping ANALYZE / statistics update.** Often the cure.
4. **Blaming the database.** Usually the data changed.
5. **Not setting up alerting on query duration.** This incident should have been caught at 1 minute, not 40.

### Bonus follow-up the interviewer might throw

> *"What if the data didn't change either? Same query, same data, suddenly 80x slower."*

Then the cause is environmental. Likely:

* Warehouse downsized.
* Heavy concurrent workload from another team or job.
* A new query has poisoned the result cache and is forcing recomputation.
* Storage backend issue (rare but real).

Check the warehouse load metrics for that timestamp and see if there's a spike of concurrent jobs. If yes, the problem is contention, not the query.
