---
id: 48
title: Query Suddenly 80x Slower
category: Debugging
topics: [EXPLAIN, statistics, plan flip, join strategy]
difficulty: Medium
solution: solution.md
---

# Problem 48, Query Suddenly 80x Slower

**Scenario:**
A SQL query that the team has run daily for a year used to finish in 30 seconds. Today, on identical-looking data and the same warehouse, it takes 40 minutes. Nothing about the query has changed. Nothing about the destination has changed. Someone wants to "throw more compute at it."

In the interview, the question is:

> A query that used to run in 30 seconds last week takes 40 minutes today. How do you find out what changed?

---

### Your Task:

1. Resist "add more compute."
2. Walk through the diagnostic order.
3. Cover the most common causes when the query itself hasn't changed.
4. Mention the prevention layer.

---

### What a Good Answer Covers:

* EXPLAIN / query plan comparison.
* Data volume changes.
* Statistics drift.
* A join's broadcast vs hash flip due to size growth.
* Storage layout (partitioning, clustering, fragmentation).
* Concurrent workloads on the same warehouse.
