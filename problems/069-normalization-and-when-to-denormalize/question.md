---
id: 69
title: Normalization and When to Denormalize
category: Databases
topics: [normalization, 3NF, denormalization, star schema]
difficulty: Medium
solution: solution.md
---

# Problem 69, Normalization and When to Denormalize

**Scenario:**
A team is designing tables for a new ordering system. One engineer wants to put the customer name and address directly on every order row "to make the queries simpler." Another wants strict normalization with foreign keys to a customer table. Both are partly right.

In the interview, the question is:

> Explain 1NF, 2NF, 3NF in plain words, and then tell me when you would denormalize on purpose.

---

### Your Task:

1. Define each normal form with one sentence and one example.
2. Show how 3NF looks for the order scenario.
3. Cover the cases where you would denormalize.
4. Mention how this connects to OLTP vs OLAP.

---

### What a Good Answer Covers:

* The point of normalization: remove redundancy, prevent anomalies.
* The classic "hidden update anomaly."
* When read performance or read shape justifies denormalizing.
* The link to warehouses (Problem 43 mentioned).
* Honest take: most code is "mostly 3NF with a few denormalized hot paths."
