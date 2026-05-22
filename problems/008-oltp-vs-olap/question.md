---
id: 8
title: OLTP vs OLAP
category: Fundamentals
topics: [OLTP, OLAP, column store, row store]
difficulty: Easy
solution: solution.md
---

# Problem 8 — OLTP vs OLAP

**Scenario:**
An analyst on your team writes a SQL query against the production Postgres database. The query is simple: count orders by day for the last year. It takes 90 seconds and the on-call engineer pings you because it briefly slowed down the checkout API. You explain that this kind of query does not belong on the production database. They ask you why.

In the interview, the question is:

> What is OLTP, what is OLAP, and why does the same query feel fast in one and slow in the other?

---

### Your Task:

1. Define OLTP and OLAP in one sentence each.
2. Explain how the underlying storage and query engine differ.
3. Give an example of a typical OLTP query and a typical OLAP query.
4. Explain why running the wrong query on the wrong system is bad for both speed and the business.

---

### What a Good Answer Covers:

* Row-oriented vs columnar storage.
* Indexes and point lookups vs scans and aggregates.
* Transactions and ACID guarantees vs append-only analytical workloads.
* Why we have a separate warehouse at all.
