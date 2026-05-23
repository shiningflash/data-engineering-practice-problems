## Solution 58: Streaming Consumer Lag Diagnosis

### Short version you can say out loud

> Before I scale anything, I want answers to four questions: is the source producing more than usual, is the sink slower than usual, is the processing stuck on a hot key, and is the job hitting a resource limit. Each one has a different fix. Scaling helps with one of them and is wasted on the rest.

### The four questions

```
1. Is the source rate higher than normal?           (input side)
2. Is the sink slower than normal?                  (output side, back-pressure)
3. Is the job's processing stuck somewhere?         (skew, hot key)
4. Is the job hitting a resource limit?             (CPU, memory, network)
```

I check them in that order because each fix is cheaper than the next.

### Question 1: source rate

Look at producer-side metrics. Is the topic's input rate higher than usual?

```
Producer rate, last 6 hours
─────────────────────────────
typical : 5,000 msgs/sec
now     : 28,000 msgs/sec
```

If yes, the source is producing faster than usual. Probably a marketing campaign, a scheduled batch dump, or a new feature went live. The job is doing what it should; it just can't keep up with the new rate.

The fix here is scaling. This is the case where the on-call's "scale up" instinct is right. But understand the why, because tomorrow you might need to scale back down.

### Question 2: sink rate (back-pressure)

Look at the sink. If the job writes to a database, is the database saturated? If it writes to another Kafka topic, is the downstream consumer keeping up?

Flink's UI shows back-pressure per operator. A red "high back-pressure" on the sink operator means the sink is the bottleneck. The job is processing fast but can't push fast enough.

If this is the case, scaling the job up does nothing. The sink can't take more. Fixes:

* Scale the sink (more database connections, bigger instance, partition the write).
* Batch sink writes (fewer larger inserts instead of many small ones).
* Async sink with proper back-pressure (Flink has an async I/O operator).

### Question 3: a stuck stage (hot key or skew)

Flink's UI shows per-task metrics. If one task is at 100% and the others are idle, you have skew.

```
Operator: keyed aggregation
  Task 0:  100% busy  (processing user_id="superuser")
  Task 1:  10% busy
  Task 2:  9% busy
  Task 3:  11% busy
```

One key dominates. Adding workers doesn't help because the work is bottlenecked on one slot.

Fixes:

* Find the hot key and decide how to handle it (rate-limit, route to a dedicated stream).
* Use Flink's salt pattern: append a random suffix to the key and aggregate in two phases.
* Some processors handle this automatically (Spark Structured Streaming with AQE).

### Question 4: resource limits

Look at cluster metrics for the job:

* CPU at 100% across all workers? Genuinely compute-bound. Scale up.
* Memory pressure with GC pauses? Increase memory or shrink state.
* Network saturated? Probably reading large messages; consider compression.

These call for scaling, but the target depends on the constraint. Adding workers doesn't help if per-worker memory is the issue.

### Reading the lag pattern

The shape of the lag over time tells you which case you're in:

* Lag was steady, then started growing 4 hours ago. Something changed at that point. Look at deploys, source-side changes, sink changes. Question 1, 2, or 4.
* Lag is growing at a constant rate. The job's processing rate is just below the source rate. Scale up.
* Lag growth is bursty. Source has spikes the job can't smooth out. Either scale to peak or accept some lag.
* Lag is huge on one partition only. That partition is hot or its keys are skewed. Question 3.

### A diagnostic walkthrough

The scenario: lag is 90 minutes after 4 hours of growth. Steps:

1. Source rate: check the producer dashboard. Up 3x for the last 4 hours. A vendor restarted and is replaying their buffered data.
2. Sink rate: nominal.
3. Skew: none.
4. Cluster: CPU at 65%, headroom available.

The source is dumping a replay. The job has room to scale but isn't maxed. Lag will recover once the replay finishes. Two options:

* Scale the job up temporarily to catch up faster.
* Do nothing; the lag will recover naturally in about 6 hours.

Either is fine. Pick based on whether downstream consumers can tolerate 90-minute lag for that long.

### When scaling is the right call

* The source rate has genuinely increased and will stay there.
* The job is CPU- or network-bound and has headroom on the cluster.
* You need to drain a backlog quickly, even if it's temporary.

### When scaling is the wrong call

* Sink is the bottleneck. Scaling the job adds back-pressure without throughput.
* Hot-key skew. Adding workers does nothing for the overloaded slot.
* Memory-bound. More workers with the same per-worker memory hit the same wall.

The danger of scaling first: it sometimes masks the real problem long enough for it to compound later.

### Tools

* Kafka lag metric: `consumer_group_lag` is the most direct signal.
* Flink UI: per-operator back-pressure indicator, per-task busy time, watermark progress.
* Cluster metrics: CPU, memory, network on each worker.
* Source-side metrics: producer rate, message size, errors.

### What I would also do besides scaling

* Alerts on lag. Page when lag exceeds N minutes for M minutes. This incident should have woken someone at the 15-minute mark.
* Capacity planning. Know the job's maximum throughput in messages/sec. Compare against expected peak.
* Replay protocol. When a vendor replays, the consumer side often sees exactly this. Have a "scale to 2x during expected replays" runbook.

### Common mistakes interviewers want you to name

1. Scaling before diagnosing. Wastes money and hides the real cause.
2. Trusting that "the job looks fine." The Flink UI's back-pressure indicator is your friend.
3. No alerting on lag. Always discovered too late.
4. Confusing a source spike with a sink slowdown. Different fixes.
5. Forgetting hot keys. A single skewed key undoes any scaling.

### Bonus follow-up the interviewer might throw

> *"What if scaling fixes it for a few hours, then the lag grows again?"*

That's a sign of a hidden steady-state problem. The source rate is creeping up, or the job's per-message work is growing (state size growing, GC getting worse). Don't keep scaling. Profile the job:

* State size growing unbounded? Add TTL or shrink the state.
* CPU time per message growing? A library update introduced overhead.
* Network or sink saturated at higher scale?

Scaling gives you breathing room. The fix to a creeping problem lives upstream of scaling.
