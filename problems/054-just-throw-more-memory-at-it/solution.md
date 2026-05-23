## Solution 54: "Just Throw More Memory at It"

### Short version you can say out loud

> Upsizing is real, it works. But it locks in cost forever, and the same query usually has a cheaper fix that has not been tried. I would agree to upsize as a temporary measure to unblock today, while we look for the underlying cause. The questions I would ask are: what is the plan showing, what is the table layout, and have we tried the four or five common optimizations before tripling the bill. Eight out of ten times, one of those wins gets us the same result without the cost.

### Acknowledging it can be the right move

It would be wrong to dismiss the suggestion. "Throw more memory" is sometimes correct:

* The job is one-time (a backfill, a migration). Optimization time costs more than the extra compute.
* The data is genuinely big and the query is already efficient.
* The deadline is in 2 hours.

So the answer is not "no." The answer is "let's verify."

### The questions I would ask

1. **What does the query plan look like?** Are we sorting to disk? Reading 10x more than we need? Picking a nested loop? Each of those has a cheaper fix than memory.
2. **Is the table partitioned and clustered well?** A 5 TB scan on a poorly clustered table is often a 50 GB scan after re-clustering.
3. **Have we tried the obvious filter and join improvements?** SELECT *, function on indexed column, broadcast join missed.
4. **Is this query going to run once or every day?** Once: just upsize. Every day: optimize.
5. **What was the size before this got slow?** If the table doubled, the optimizer may have flipped a join. Plan diff (Problem 48).

If none of those have been investigated, I would ask for an hour to look before agreeing to the upsize.

### The cheaper alternatives I would check

Before agreeing to upsize, in order of effort:

**1. Reduce data read.**

Column pruning, partition pruning, filter pushdown. Often a 10x reduction in bytes scanned with no logic change.

**2. Force a better join.**

Broadcast hints, MERGE JOIN with sorted inputs. A wrong join strategy is the most common cause of memory pressure.

**3. Use a temp table.**

Sometimes the optimizer cannot figure out a path. Materialize the intermediate result to a small temp table, then join. This breaks the planner's bad assumptions.

**4. Re-cluster the table.**

In Snowflake, run `ALTER TABLE... RECLUSTER`. In BigQuery, recreate with proper clustering. Slow queries due to clustering drift get a big win.

**5. Update statistics.**

Often the answer (Problem 48). Free, fast, sometimes magic.

**6. Cache or summary.**

If the query runs often, build a summary table or materialized view (Problem 53).

**7. Then upsize.**

If none of those work and the job is critical, upsize. But document why, so the next person knows.

### When upsize IS the right answer

Three cases:

1. **One-time big work.** A monthly reconciliation, a quarterly data migration. Two hours of upsized compute is cheaper than two days of optimization.
2. **The query is already optimal.** You have tried all of the above, plans look clean, the data is just big.
3. **You are time-pressured.** The dashboard has to render in 5 minutes for the board meeting. Upsize now, optimize Monday.

The honest move in case 3 is to upsize *and* file a ticket for Monday. Otherwise the temporary fix becomes permanent.

### The cost math

```
Snowflake warehouse sizes (rough)
─────────────────────────────────
X-Small   →   1 credit/hour
Small     →   2
Medium    →   4
Large     →   8
X-Large   →   16
2X-Large  →   32
3X-Large  →   64

Going from Large to 2X-Large is 4x cost.
Going from X-Small to 2X-Large is 32x cost.
```

A query that runs once a day for 30 minutes:

* Large: ~$15 per day = ~$450/month.
* 2X-Large: ~$60 per day = ~$1,800/month.

If the optimization would have taken 4 hours and saved you the upsize, that's $1,350/month saved for the price of an afternoon's work.

### The cultural side

When a senior engineer suggests something, the worst move is "that's wrong." Instead:

> "That would work. Before we commit to the cost, can we spend an hour checking the plan? If there's a free fix, we save the upsize. If not, we upsize and move on."

You are agreeing to upsize as the fallback. You are also buying time to investigate without making it look like you are blocking them.

If the investigation finds an obvious fix, the senior engineer learns something. If it doesn't, you upsize together and have shared confidence in the decision.

### What I would NOT do

* **Refuse outright.** Sometimes upsize is right.
* **Spend two days optimizing.** Not worth it for a small win.
* **Upsize permanently** to make a sporadic problem go away. The cost compounds.
* **Hide the upsize.** Document it so it gets reviewed.

### Common mistakes interviewers want you to name

1. **Upsize first, ask later.** Triples the bill, often without reason.
2. **Optimize forever** for a one-time job.
3. **No follow-up.** Upsize becomes permanent.
4. **Treating "the senior engineer said so" as proof.** Senior engineers are right often but not always.
5. **No comparison.** Without a before/after measurement, you cannot tell if the upsize even helped.

### Bonus follow-up the interviewer might throw

> *"What if the job is genuinely too big for the smaller warehouse, but we cannot rewrite the logic?"*

Then the upsize is correct, but consider:

* **Use a larger warehouse only for that job.** Snowflake lets you assign warehouses per task. Other jobs stay on the smaller warehouse.
* **Schedule it off-peak.** A larger warehouse for 30 minutes at 2 AM costs less impact than fighting for slots at 9 AM.
* **Use a reservation or commitment** if the upsized warehouse becomes a regular pattern. Reserved capacity is 30-50 percent cheaper than on-demand.

Treat the upsize as a tool, not a default.
