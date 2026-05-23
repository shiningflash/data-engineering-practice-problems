---
id: 52
title: Four Hour Spark Job Under One Hour
category: Cost & Performance
topics: [Spark UI, skew, AQE, broadcast joins]
difficulty: Medium
solution: solution.md
---

# Problem 52, Four Hour Spark Job Under One Hour

**Scenario:**
A nightly Spark job takes 4 hours. The team wants it under 1 hour without rewriting the business logic. The job reads several large tables, joins them, aggregates, and writes results. You are asked what you would check first.

In the interview, the question is:

> A nightly Spark job runs for 4 hours and the team needs it under 1 hour. Without rewriting logic, what do you check first?

This is testing your sense of where time hides in distributed jobs and what you can change without touching the SQL or DataFrame logic.

---

### Your Task:

1. List the things you would inspect, in order.
2. Explain how to use the Spark UI.
3. Cover the most common 4x wins.
4. Mention what does NOT count as "rewriting logic."

---

### What a Good Answer Covers:

* Spark UI stages and tasks.
* Skew detection.
* Partition count and shuffle size.
* Reading too much data (column pruning, partition pruning).
* Broadcast joins vs sort-merge joins.
* Output file size and small-file problem.
