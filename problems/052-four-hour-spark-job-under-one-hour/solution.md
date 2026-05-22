## Solution 52: Four Hour Spark Job Under One Hour

### Short version you can say out loud

> I would open the Spark UI and look for three things: one stage that takes most of the time, skew where a few tasks are much longer than the rest, and shuffle volume that is way bigger than the input. Most 4x wins come from one of: skewed joins, reading more data than needed, too few or too many partitions, and a sort-merge join that should have been broadcast. None of those require touching the business logic.

### The inspection order

```
1. Spark UI → Jobs → which stage is the slowest?
2. That stage → Tasks → are some tasks 10x longer than median?  (skew)
3. Shuffle Read / Write columns → how much data is being moved?
4. Input → are we reading whole files when we only need columns?
5. Final write → are we producing 50,000 tiny files?
```

### Step 1: find the slow stage

In the Spark UI, the Jobs page lists stages with duration. One or two stages usually dominate. Click into the slowest.

The Tasks page for that stage shows the distribution of task durations. Three patterns:

* **Even.** All tasks take similar time. You are CPU- or I/O-bound across the cluster. Scale-up helps.
* **Skewed.** A few tasks are 10x longer than the rest. Skew. This is the most common reason a Spark job is slow.
* **Mostly fast with a few slow stragglers.** Skew, but milder. Still worth fixing.

### Step 2: fix skew

Skew means data is unevenly distributed across partitions. Usually because of a join key with one or two huge values.

Detecting:

* Sort tasks by duration. The slowest tasks are processing the huge keys.
* Sort by shuffle read size. Same answer.

Fixing without changing logic:

* **Salting.** Add a random suffix to the join key on both sides (Spark 3+ does this automatically with AQE, Adaptive Query Execution). AQE can split skewed partitions on the fly.
* **Enable AQE.**

```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

If AQE is off, turn it on. This single change often shaves 50 percent off skewed jobs.

### Step 3: reduce shuffle

The Spark UI shows shuffle read and write per stage. If shuffle is bigger than the input data, the job is moving more than it needs to.

Common causes:

* **Two large tables joined on a high-cardinality key.** Required, but expensive.
* **A `groupBy` immediately followed by a wide aggregation.** Sometimes can be reorganized; not always.
* **A `repartition()` followed by a small filter.** Repartitioning before filtering is wasteful.

Without changing the logic, you can:

* **Filter earlier.** If the SQL filters after a join, move it before. AQE in Spark 3 does some of this, but not all.
* **Tune `spark.sql.shuffle.partitions`.** Default 200 is often wrong. Too few = giant shuffles. Too many = overhead. A rule of thumb: target ~128 MB per partition. If shuffle is 100 GB, aim for ~800 partitions.

### Step 4: read less

Spark reading from columnar storage (Parquet, ORC, Delta) should only read the columns it needs. If you have:

```python
df = spark.read.parquet("s3://...")
df.select("a", "b", "c").filter(...).join(...)
```

Spark should push down both the column selection and the filter. But sometimes a downstream operation breaks this (a `.collect()`, a `.cache()`, a UDF before the filter).

Check the physical plan:

```python
df.explain(True)
```

Look for:

* **PartitionFilters.** Make sure the filter on the partition column appears here. If it does not, the job is reading every partition.
* **PushedFilters.** The other filters should show up. If not, predicate pushdown is broken.
* **PrunedColumns.** Should show only the columns you actually use.

Reading 100 GB vs 5 GB makes a 20x difference in I/O time alone.

### Step 5: check the partition count of the input

If a 1 TB table is stored as 5 huge files, Spark only has 5 partitions to work on initially, no matter how many executors you have. The job stalls.

Fix without changing logic:

* `spark.read.parquet(...).repartition(N)` to split it up early. Sometimes a `.repartition()` before the heavy work is a 2x win even though it triggers a shuffle.
* If the source format is non-splittable (gzipped CSV), there is no fix at read time. The underlying problem is the file format.

### Step 6: check the output

Sometimes the 4-hour job is fast on the compute part but spends an hour writing tiny files. If your DataFrame has 5,000 partitions and you `write` to a partitioned destination with 100 partitions, you create 500,000 files.

Fix:

```python
df.repartition(100).write.partitionBy("date").parquet(out)
```

Or use `coalesce(n)` if you do not need a full shuffle.

### Step 7: cluster shape

Without rewriting logic, you can still:

* **Increase executors.** More parallelism, faster per-stage.
* **Right-size executor memory.** Too small causes spills to disk (very slow). Too big wastes cores. A sweet spot is usually 4-8 cores per executor and 4 GB per core.
* **Spot instances** for cost, not speed. Saves money, can hurt reliability if not careful.

If the job is I/O bound, more compute does not help. Look at network read instead.

### What does NOT count as "rewriting logic"

The team asked to keep the business logic the same. That still allows:

* Enabling AQE.
* Tuning shuffle partition count.
* Adding `repartition` or `coalesce` calls.
* Selecting columns before the heavy work.
* Filter pushdown.
* Broadcast hints (`broadcast(df)`).
* Cluster sizing.
* Output write strategy.

It does not allow rewriting the SQL or DataFrame transformations themselves. That is the line.

### A real fix walkthrough

A team's 4-hour job is mostly one stage with a sort-merge join. Spark UI shows:

* Input: 500 GB of orders + 50 MB of dim_country.
* Shuffle: 500 GB on each side of the join.
* Total time: 3.5 hours.

The dim_country is small but Spark is treating it like another large table. Fix:

```python
from pyspark.sql.functions import broadcast
joined = orders.join(broadcast(dim_country), "country_code")
```

Now Spark broadcasts the small side. No shuffle. The join completes in minutes instead of hours. Total job goes from 4 hours to ~45 minutes.

One line. No logic change. 4x.

### Common mistakes interviewers want you to name

1. **Adding more nodes** before checking the plan. Often the bottleneck is one stage, not capacity.
2. **Disabling AQE** because of an old bug. AQE in Spark 3.2+ is solid.
3. **Default `spark.sql.shuffle.partitions=200`** for a 1 TB job.
4. **Tiny output files** that take longer to write than the compute itself.
5. **Caching everything.** Sometimes the cache is the bottleneck.

### Bonus follow-up the interviewer might throw

> *"What if you actually do need to rewrite logic to hit one hour?"*

Then the conversation changes. Most often, the win is reducing what you compute, not how. For example, if 80 percent of the join output is then aggregated to 1 percent of the rows, do the aggregation first. Or, pre-compute features in a daily smaller table so the big nightly job has less to do.

But that should be a second conversation, after the no-logic-change wins are taken. They usually get you within 2x of the target by themselves.
