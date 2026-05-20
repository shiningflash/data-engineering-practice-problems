---
id: 43
title: Mixing Facts and Dimensions
category: Data Modeling
topics: [star schema, SCD2, views, history]
difficulty: Medium
solution: solution.md
---

# Problem 43 — Mixing Facts and Dimensions

**Scenario:**
A team has a single "orders" table in their warehouse that includes the order details, the customer name and address, the product name and category, and the warehouse-of-origin name. Every analyst query reads from that one table, and "joins" are never needed. The team's reasoning: "it's easier to query."

A new requirement: when a customer changes their address, all the old orders in the table now show the new address, so historical reports change. The team is asked to "fix" this and they consider rebuilding the table daily as a snapshot.

In the interview, the question is:

> A team is mixing facts and dimensions in the same table because "it is easier to query." Explain why that quietly hurts them later.

---

### Your Task:

1. Explain the symptom and the underlying cause.
2. Show the fix.
3. Address the team's "but it's easier" argument honestly.
4. Cover when a wide denormalized table really IS the right call.

---

### What a Good Answer Covers:

* The grain trap.
* History rewriting silently.
* Storage cost vs query simplicity trade.
* The compromise: a wide reporting view on top of a clean star schema.
