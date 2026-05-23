## Solution 56: Watermarks in Plain Words

### Short version you can say out loud

> A watermark is the system saying "I am willing to bet that no events older than this timestamp will arrive from now on." It tells windowed aggregations when they are allowed to close and emit a result. Set it too tight and you close windows before late events arrive, those events get dropped. Set it too loose and the output is correct but late, because you keep waiting for stragglers that may never come. The right value is a guess based on how late events realistically arrive.

### Picture event time vs processing time

```
Event time   :   when the event actually happened (in the device, app, etc.)
Processing time: when the event is processed by your pipeline

In a perfect world they are equal. In real life:
  - Network delays
  - Mobile clients with bad connections
  - Cross-region delivery
  - Backpressure in Kafka

So events from 12:05:00 might arrive at the processor at 12:05:01 (a 1-second lag),
or at 12:09:30 (a 4.5-minute lag), or at 13:00:00 (an hour late).
```

The pipeline wants to compute "events that happened between 12:00 and 12:05." It has to decide when to stop waiting and emit the answer.

### What a watermark actually is

A watermark is a piece of timing metadata. When the processor sees a watermark of `12:08:00`, it is asserting: **"I think I have all events with event time ≤ 12:08:00."**

This belief drives window closure:

* The window `[12:00, 12:05)` closes when the watermark crosses `12:05`.
* After it closes, any late event for that window is by default dropped.

### Tight watermark: low latency, dropped events

If you set the watermark to `current_event_time - 1 second`, you are saying "all events arrive within 1 second of their event time."

* **Pro**: windows close fast. Result emitted within seconds.
* **Con**: any event that is slow (mobile retry, network blip) is dropped because it arrives after its window has closed.

In real-life pipelines, even "fast" streams have a tail of events arriving 30-60 seconds late, often more. A tight watermark loses them.

### Loose watermark: correct but slow

If you set the watermark to `current_event_time - 10 minutes`, you are saying "events can arrive up to 10 minutes late."

* **Pro**: late events are still captured.
* **Con**: results take 10 extra minutes to emit. A 5-minute window emits 15 minutes after it should.

For some use cases (a dashboard, a billing roll-up), this lag is fine. For others (fraud detection, real-time pricing), it is not.

### How to choose

There is no universal value. The right watermark is **a guess at how late events realistically arrive in your system**. Steps:

1. **Measure your tail.** Look at the difference between event time and processing time for a representative sample. Plot the distribution. Pick a percentile that matches your appetite.
2. **A common starting point**: watermark = current event time - the 99th percentile of lag.
3. **For most systems**: somewhere between 30 seconds and 5 minutes is typical.

You are explicitly trading off latency for completeness. Most teams converge on "a few minutes" because the cost of a slightly late result is much less than the cost of losing data.

### Allowed lateness

A separate knob from the watermark. The watermark closes the window. Allowed lateness says "even after the window closes, accept events older than the watermark for this much longer, and re-emit the result."

```
Window [12:00, 12:05)
Watermark says "complete" at 12:05 + 1 min  → window closes, first result emitted
Allowed lateness = 10 min                    → updates re-emitted for late events until 12:16
After 12:16, late events go to "side output" (drop or audit)
```

This is the production sweet spot: get a fast first answer, refine it as stragglers arrive, eventually finalize.

### Per-event watermarks

Some pipelines have event sources with very different lag profiles. A web event has different lag than a batch upload from a vendor. You can:

* **Per-source watermarks**: each Kafka topic or producer has its own watermark, the processor takes the minimum across all sources.
* **Idle source handling**: if one source goes idle, don't let it freeze the watermark. Flink has `withIdleness` for this.

### Side outputs for late events

Don't just drop late events. Route them to a "late" sink:

* Useful for diagnosing whether your watermark is too tight.
* Useful for audits.
* Useful for compensating updates downstream (re-bill, re-flag).

The cost is tiny; the visibility is great.

### A concrete recipe

For a typical app event stream with the goal "5-minute windows, results within 2-3 minutes, no event loss":

```
watermark         = current event time - 2 minutes
allowed lateness  = 5 minutes
side output       = anything later than that

Result: first emission at watermark + window end (~2 min after wall clock).
Updates for the next 5 minutes as stragglers arrive.
After that, events go to the late sink for analysis.
```

### Common mistakes interviewers want you to name

1. **Watermark = current processing time.** No allowance for lateness. Drops the tail.
2. **Watermark = current event time - 1 hour.** Output is too slow to be useful.
3. **No side output for late events.** Silent loss.
4. **Same watermark across very different sources.** The slowest source dominates.
5. **Confusing watermark with allowed lateness.** Both knobs exist for a reason.

### Bonus follow-up the interviewer might throw

> *"What if you need 'exactly correct' aggregates at the end of the day, but also fast early results?"*

Two-tier approach:

1. **Stream layer** with a moderately tight watermark gives near-real-time results (good enough for dashboards).
2. **Batch layer** (typically a nightly warehouse job) recomputes the same aggregates over the day's full event log, with effectively infinite "watermark." This is the audited number.

If the two diverge (they will, slightly), the batch one wins for reporting. This is the original "lambda architecture" pattern. It is more operational work but gives you the guarantees both audiences want.
