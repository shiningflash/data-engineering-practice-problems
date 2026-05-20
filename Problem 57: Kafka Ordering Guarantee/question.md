## Problem 57: Kafka Ordering Guarantee

**Scenario:**
A teammate says Kafka "guarantees message ordering," and your pipeline depends on that. You have noticed messages occasionally appearing out of order downstream. The teammate is sure Kafka could not be at fault.

In the interview, the question is:

> Kafka is said to "guarantee ordering." What does that actually mean, and what can quietly break it in practice?

---

### Your Task:

1. State the exact guarantee.
2. Explain why it is conditional.
3. List the realistic ways the guarantee breaks.
4. Cover what to do when ordering matters.

---

### What a Good Answer Covers:

* Ordering per partition, not per topic.
* Partitioning key choice.
* Producer retries and idempotence.
* Multiple producers, consumer groups, reprocessing.
* When you actually need global ordering.
