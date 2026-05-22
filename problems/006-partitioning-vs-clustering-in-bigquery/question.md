---
id: 6
title: Partitioning vs Clustering in BigQuery
category: Fundamentals
topics: [BigQuery, partitioning, clustering, cost]
difficulty: Easy
solution: solution.md
---

# Problem 6 — Partitioning vs Clustering in BigQuery

**Scenario:**
You join a small analytics team and notice every important query runs against one giant `events` table with about 8 billion rows. The team has heard about partitioning and clustering, but they are not sure which one to use, or whether to use both.

In the interview, the question is short:

> Explain partitioning and clustering in BigQuery in plain words. When would you pick one over the other? When would you use both?

---

### Your Task:

1. Explain in plain English what partitioning is and what clustering is.
2. Give a real example for each.
3. Explain when you would pick one, when you would pick the other, and when you would use both.
4. Mention at least one common mistake people make.

---

### What a Good Answer Covers:

* The physical difference between partitions (separate storage units) and clustering (sort order inside a partition).
* How partitioning helps **pruning** at scan time.
* How clustering helps **filtering** and **joins** on high cardinality columns.
* The "partition first, cluster second" rule of thumb.
* Cost implications, since BigQuery charges by bytes scanned.
