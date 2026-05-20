---
id: 51
title: BigQuery Bill Eight Times Higher
category: Cost & Performance
topics: [INFORMATION_SCHEMA, top queries, slot reservation]
difficulty: Medium
solution: solution.md
---

# Problem 51 — BigQuery Bill Eight Times Higher

**Scenario:**
The monthly BigQuery bill jumped from $500 to $4,000 between April and May. Nobody on the team can immediately say why. Finance wants an answer this week. You have full access to billing data and INFORMATION_SCHEMA.

This is the more focused cousin of Problem 30. Here the question is the investigation method itself, top to bottom.

In the interview, the question is:

> Your BigQuery bill jumped from 500 to 4000 dollars in one month. Walk me through how you would find what caused it.

---

### Your Task:

1. List the queries you would run first.
2. Walk through how to split cost by user, by query, by table.
3. Cover what the answer usually is.
4. Propose the immediate fixes and the longer term governance.

---

### What a Good Answer Covers:

* INFORMATION_SCHEMA.JOBS_BY_PROJECT.
* Bytes billed as the cost driver.
* Partitioning that is not used, clustering that is not used, SELECT * patterns.
* Scheduled queries running too often.
* Reservation vs on-demand decision.
