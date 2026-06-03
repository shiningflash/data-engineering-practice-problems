---
id: 92
title: Late Events After the Partition Closed
category: Streaming
topics: [late data, watermarks, event time, reprocessing]
difficulty: Medium
interview_value: strong
learn_order: 92
series: senior-scenarios
solution: solution.md
---

# Problem 92, Late Events After the Partition Closed

**Scenario:**
You run a streaming pipeline that aggregates app events into hourly buckets. The SLA promises a window is "closed and final" 30 minutes after the hour ends. A product manager flags that the Saturday 14:00 to 18:00 buckets look low. Investigation finds 380,000 events from those hours that arrived three days late, when a customer's phone came off airplane mode. The watermark moved past 18:30 on Saturday and those rows landed in a side table called `_late`. Sunday's daily rollup, the Monday dashboard, and the ML feature pipeline all used the "final" numbers and are wrong.

In the interview, the question is:

> How does your pipeline handle this kind of late arrival, what does the recovery look like for the already-published numbers, and how do you decide the policy for "how late is too late."

---

### Your Task:

1. Define event time vs processing time and explain why this case needs both.
2. Cover watermarks and allowed lateness, and where 380,000 events three days late falls.
3. Walk through the recovery: what to recompute, what not to, and how to communicate.
4. Cover the policy choice: how late do you accept, where do the rest go, and who decides.

---

### What a Good Answer Covers:

* Event time as the truth for aggregation; processing time as the truth for SLA.
* `withWatermark` and `allowedLateness` in the stream processor.
* The `_late` side table as a deliberate design, not an accident.
* Idempotent recomputation of closed windows.
* The cost-vs-correctness curve: open windows forever or freeze them.
* Communicating revised numbers to downstream consumers.
