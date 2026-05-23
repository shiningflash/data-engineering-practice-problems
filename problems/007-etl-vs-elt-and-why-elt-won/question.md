---
id: 7
title: ETL vs ELT and Why ELT Won
category: Fundamentals
topics: [ETL, ELT, dbt, warehouse]
difficulty: Easy
solution: solution.md
---

# Problem 7, ETL vs ELT and Why ELT Won

**Scenario:**
You walk into a team that still runs every nightly transform on a separate ETL server before loading the cleaned data into the warehouse. The server is creaking, scaling it up is expensive, and adding a new transform requires a release. Someone asks the obvious question:

> Why do most modern teams do this the other way around now?

In the interview, this question is short and conversational:

> What is the difference between ETL and ELT, and why has the industry mostly moved to ELT?

---

### Your Task:

1. Explain ETL and ELT in plain English, with one sentence each.
2. Draw a small diagram of the two flows.
3. Explain what changed in the world that made ELT possible.
4. Give two situations where ETL is still the right choice.

---

### What a Good Answer Covers:

* The basic order: where the transform happens.
* Why cheap, scalable warehouses (BigQuery, Snowflake, Redshift) changed the game.
* The role of tools like dbt.
* The trade-offs: data freshness, cost predictability, governance, PII handling.
* When you would still pick ETL on purpose.
