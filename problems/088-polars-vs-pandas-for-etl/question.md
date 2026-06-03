---
id: 88
title: Polars vs Pandas for ETL
category: SQL & Querying
topics: [Polars, Pandas, Arrow, ETL]
difficulty: Easy
interview_value: optional
learn_order: 77
solution: solution.md
---

# Problem 88, Polars vs Pandas for ETL

**Scenario:**
A Pandas ETL job that processes a 20 GB Parquet file runs out of memory on a 64 GB box and falls back to processing in chunks, taking 90 minutes. A teammate rewrites the same job in Polars and it finishes in 6 minutes using 30 GB of memory. They ask whether the team should standardise on Polars. You explain when that is right and when Pandas still wins.

In the interview, the question is:

> Pandas or Polars: what is the actual difference, and how do you pick for an ETL pipeline?

---

### Your Task:

1. Explain Pandas in one paragraph: what it gets right, what it gets wrong.
2. Explain Polars in one paragraph: what is different.
3. Compare on memory, speed, API surface, and ecosystem.
4. Walk through a realistic ETL: read Parquet, join, group, write.
5. Cover when to stay on Pandas, even now.

---

### What a Good Answer Covers:

* Pandas built on NumPy, single-threaded, object dtype, eager.
* Polars built on Arrow, multi-threaded, strict typing, lazy + eager.
* The lazy execution model and query optimisation.
* The DataFusion / DuckDB / Polars convergence around Arrow.
* Why Pandas still wins for small data, niche libraries, teaching, notebooks.
