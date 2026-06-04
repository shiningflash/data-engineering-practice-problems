---
id: 95
title: Duplicate Rows From a Successful Pipeline
category: Batch Pipelines & Orchestration
topics: [duplicates, idempotency, MERGE, unique key]
difficulty: Medium
interview_value: must-have
learn_order: 95
series: senior-scenarios
solution: solution.md
---

# Problem 95, Duplicate Rows From a Successful Pipeline

**Scenario:**
The nightly load to `dim_customers` has been "green" for months. This Tuesday an analyst notices the daily active count jumped 35% with no real reason. You check. The table has 2.4M rows. It should have around 1.8M. Querying for duplicates: a third of the customer_ids appear two or three times. Same id, slightly different `last_seen_at`. The job never failed once. Nobody got paged. The data just slowly stopped being trustworthy.

In the interview, the question is:

> Walk me through how you diagnose this, clean it up, and stop it from happening again. What is the underlying pattern most teams get wrong here?

---

### Your Task:

1. Explain how a "successful" job can quietly produce duplicates.
2. Walk through the cleanup: pick the winner, dedupe safely, prove the fix worked.
3. Describe the durable fix and why one common shortcut does not work.
4. Cover the tests that catch this on the next change.

---

### What a Good Answer Covers:

* Append-only INSERTs vs idempotent MERGE.
* Retries on a non-idempotent job double-write.
* Two sources overlapping on the same key.
* `ROW_NUMBER()` for picking the right version.
* A `unique` test on the natural key as the long-term safety net.
