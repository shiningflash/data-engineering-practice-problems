---
id: 84
title: Data Observability, Freshness, Volume, and Drift
category: System Design
topics: [observability, SLO, freshness, drift]
difficulty: Medium
interview_value: must-have
learn_order: 88
solution: solution.md
---

# Problem 84, Data Observability, Freshness, Volume, and Drift

**Scenario:**
A revenue dashboard sat at "no change since yesterday" for four days before a finance analyst noticed. The job had been failing silently, the warehouse had stale numbers, and downstream models continued to read them. The lead asks you to design a data observability layer so a four-day stale dashboard is impossible.

In the interview, the question is:

> What does data observability mean, what do you actually monitor, and how do you turn it into alerts that page the right person?

---

### Your Task:

1. List the four pillars of data observability (freshness, volume, schema, distribution) and what each catches.
2. Walk through how each is implemented as a check against a warehouse table.
3. Cover where the checks live (dbt tests, Great Expectations, Monte Carlo, custom).
4. Explain the SLA / SLO / SLI vocabulary applied to data.
5. Cover the alert fatigue problem and how to avoid it.

---

### What a Good Answer Covers:

* `MAX(updated_at)` as the cheapest freshness check.
* Row-count-per-day Z-scores for volume.
* `INFORMATION_SCHEMA` diffs for schema drift.
* Min, max, null-rate, distinct-count for distribution drift.
* Why "alert on every dbt test failure" burns the team in a week.
* SLO on critical tables vs noisy alerts on the rest.
