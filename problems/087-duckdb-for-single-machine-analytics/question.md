---
id: 87
title: DuckDB for Single-Machine Analytics
category: SQL & Querying
topics: [DuckDB, analytics, OLAP, single-node]
difficulty: Easy
interview_value: strong
learn_order: 76
solution: solution.md
---

# Problem 87, DuckDB for Single-Machine Analytics

**Scenario:**
A teammate is spinning up a Snowflake warehouse to crunch a 30 GB Parquet file once a quarter for a regulatory report. The warehouse is on for an hour and costs more than the report is worth. A junior asks "why don't we just use DuckDB on my laptop." The senior engineer hesitates. You explain why the junior is right, and where DuckDB is actually the wrong choice.

In the interview, the question is:

> What is DuckDB, what workloads is it the right answer for, and where does it stop being the right answer?

---

### Your Task:

1. Explain what DuckDB is in one paragraph.
2. List the workloads where it is the right answer.
3. List the workloads where it is the wrong answer.
4. Walk through a realistic example: querying Parquet on S3 from a laptop.
5. Cover where DuckDB fits in a modern stack alongside Snowflake and Spark.

---

### What a Good Answer Covers:

* In-process, columnar, vectorised, MIT licensed.
* No server, no cluster, runs in Python / R / C++ / browser.
* Direct queries on Parquet, CSV, JSON, Iceberg, S3.
* The "if it fits on one machine" rule and what that means in 2026.
* Where Spark or a warehouse beat it (multi-user, persistent storage, governance).
