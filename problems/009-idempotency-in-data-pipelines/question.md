---
id: 9
title: Idempotency in Data Pipelines
category: Fundamentals
topics: [idempotency, retries, MERGE, partitions]
difficulty: Medium
solution: solution.md
---

# Problem 9, Idempotency in Data Pipelines

**Scenario:**
A scheduled job that loads daily orders into your warehouse failed at 2 AM, retried automatically, and finished successfully on the second attempt. The next morning, the revenue dashboard shows yesterday's number is exactly double. The team is confused. You explain that the job was not idempotent.

In the interview, the question is:

> What does idempotency mean for a data pipeline, and why do interviewers ask about it so often?

---

### Your Task:

1. Define idempotency in plain English.
2. Show a small example of a non idempotent pipeline and the same pipeline made idempotent.
3. Explain three real patterns to make a pipeline idempotent.
4. Explain why this matters more in batch pipelines than people think.

---

### What a Good Answer Covers:

* The link between idempotency and retries.
* The MERGE / UPSERT pattern.
* The "delete and reinsert by partition" pattern.
* The idempotency key pattern from APIs.
* Why "the job succeeded" is not enough.
