---
id: 13
title: Data Lake vs Warehouse vs Lakehouse
category: Fundamentals
topics: [lake, warehouse, lakehouse, Iceberg, Delta]
difficulty: Medium
solution: solution.md
---

# Problem 13 — Data Lake vs Warehouse vs Lakehouse

**Scenario:**
A product manager joins your team and asks why your stack has three different storage layers: raw files in S3, tables in BigQuery, and something the team calls "the lakehouse." They want to understand the point of each.

In the interview, the question is:

> Explain the difference between a data lake, a data warehouse, and a lakehouse. Pretend you are explaining it to a product manager who has never worked with data infrastructure.

---

### Your Task:

1. Define each in one sentence a non-technical person can follow.
2. Show a small diagram of the three.
3. Explain what each one is good at and bad at.
4. Explain where the "lakehouse" idea actually came from and why it gets debated.

---

### What a Good Answer Covers:

* Lake as raw files (cheap, flexible, hard to govern).
* Warehouse as managed tables (governed, fast, more expensive).
* Lakehouse as "warehouse features on top of lake files," using formats like Delta, Iceberg, Hudi.
* The honest take: most companies have all three.
