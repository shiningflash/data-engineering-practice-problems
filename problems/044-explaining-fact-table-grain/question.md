---
id: 44
title: Explaining Fact Table Grain
category: Data Modeling
topics: [grain, facts, dimensions, aggregations]
difficulty: Easy
solution: solution.md
---

# Problem 44, Explaining Fact Table Grain

**Scenario:**
You are mentoring an analyst who keeps producing dashboards that don't quite match. The cause is the same every time: they don't have a clear sense of what each row in the fact table represents. They ask you to explain "grain" in a way they can use the next time they build a model.

In the interview, the question is:

> What is the grain of a fact table, and how would you explain it to a non technical stakeholder?

---

### Your Task:

1. Define grain in one sentence.
2. Give three different grains for the same business.
3. Show why getting it wrong produces bad numbers.
4. Walk through how to choose grain for a new fact.

---

### What a Good Answer Covers:

* Grain as "one row means one X."
* Picking grain by what the dashboard asks.
* Mixing grains is the bug.
* Coarser is faster; finer is more flexible.
* Bridge tables for many-to-many.
