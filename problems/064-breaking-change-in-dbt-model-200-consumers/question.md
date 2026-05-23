---
id: 64
title: Breaking Change in dbt Model 200 Consumers
category: People & Process
topics: [dbt, deprecation, comms, rollout]
difficulty: Medium
solution: solution.md
---

# Problem 64, Breaking Change in dbt Model 200 Consumers

**Scenario:**
A column in a core dbt model needs to be renamed. The model has 200 downstream consumers: other dbt models, dashboards, scheduled queries, Reverse ETL jobs. Changing the column directly will break all of them at once. The team has done this before and it was a disaster. You are asked to plan the rollout.

In the interview, the question is:

> How would you safely roll out a change to a dbt model that has 200 downstream consumers?

---

### Your Task:

1. Show the high-level rollout strategy.
2. Walk through the deprecation window.
3. Cover communication with consumer teams.
4. Mention the tests that catch breakage.

---

### What a Good Answer Covers:

* Additive changes are safe; replacements are not.
* A deprecation window where both old and new exist.
* Communicating to consumer owners.
* dbt's `exposures` / dependency graph.
* A clear "you have to update by" deadline.
