---
id: 96
title: The 20-Minute Query That Should Be 2 Seconds
category: SQL & Querying
topics: [EXPLAIN, partitioning, clustering, optimization]
difficulty: Medium
interview_value: strong
learn_order: 96
series: senior-scenarios
solution: solution.md
---

# Problem 96, The 20-Minute Query That Should Be 2 Seconds

**Scenario:**
A finance analyst messages you: "Why does the daily revenue query take 20 minutes? It is just last 30 days, grouped by region. The dashboard times out and I have to keep refreshing." You run the query yourself. It is 14 lines of SQL: a `SELECT` on `fct_orders`, a join to `dim_customer` for region, a `WHERE order_date >= CURRENT_DATE - 30`, and a `GROUP BY region`. The table has 800M rows. The query plan shows a full scan. 20 minutes is generous.

In the interview, the question is:

> Walk me through how you make this query fast. What do you actually change, and why does the optimizer not save you?

---

### Your Task:

1. Read the query plan and explain what is going wrong.
2. Walk through the layered fix: partition filter first, then clustering, then materialization if needed.
3. Cover the common mistake of "just add an index."
4. Explain how to verify the fix actually worked.

---

### What a Good Answer Covers:

* Partition pruning vs full scan.
* Clustering for the filter columns the optimizer cannot prune.
* Pre-aggregated tables when the same group-by runs 100x a day.
* `EXPLAIN ANALYZE` before and after.
* Why a "missing index" answer reveals you have not used a columnar warehouse before.
