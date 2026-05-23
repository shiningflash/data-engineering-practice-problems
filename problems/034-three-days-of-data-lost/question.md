---
id: 34
title: Three Days of Data Lost
category: Scenarios
topics: [Kafka retention, replay, recovery, postmortem]
difficulty: Hard
solution: solution.md
---

# Problem 34, Three Days of Data Lost

**Scenario:**
Three days of production data has been lost. A Kafka topic was misconfigured during a deploy: the retention was set to 1 hour instead of 7 days, and the consumer group that lands events into the data lake fell behind. By the time anyone noticed, the missing events had aged out of Kafka. They are gone from there. The source systems may still have them, but only some do.

In the interview, the question is:

> Production lost three days of data because a Kafka topic was misconfigured. How do you recover, and what do you change after?

This is a recovery scenario plus a postmortem scenario. The interviewer wants to see calm, structured thinking, plus the harder lesson at the end.

---

### Your Task:

1. Sketch the immediate recovery plan.
2. Cover what is recoverable and what is permanently lost.
3. Plan the postmortem.
4. Propose what changes to prevent this class of failure.

---

### What a Good Answer Covers:

* Stop the bleeding: fix the config first.
* Recover from upstream sources where possible.
* Be honest about what is gone.
* Idempotent replay, no double counting.
* Guards: schema registry, config review, monitoring, retention floors.
