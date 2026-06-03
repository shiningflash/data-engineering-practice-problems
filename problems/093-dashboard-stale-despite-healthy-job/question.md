---
id: 93
title: Dashboard Stale Despite a Healthy Job
category: Batch Pipelines & Orchestration
topics: [stale data, freshness, cache, SLA]
difficulty: Medium
interview_value: strong
learn_order: 93
series: senior-scenarios
solution: solution.md
---

# Problem 93, Dashboard Stale Despite a Healthy Job

**Scenario:**
A finance PM messages at 09:14: "Revenue dashboard is showing yesterday's number. Did the job fail again?" You check. The job ran at 06:00 and succeeded. The warehouse query against `fct_revenue` returns today's data. The PM refreshes the dashboard; still yesterday. You realise the source for the dashboard is a BI cache that was refreshed at 06:05, and the source data only landed in the warehouse at 07:30. The 06:00 job ran on yesterday's late-arriving data. Three teams disagree on what "stale" means. The CTO asks you to lead a fix that prevents this monthly conversation.

In the interview, the question is:

> What does "stale" actually mean in a layered data stack, and how do you design freshness so this same conversation does not happen next month?

---

### Your Task:

1. Decompose "stale" into the three layers it can live in (data lands late, job runs early, cache is stale).
2. Propose a freshness contract that resolves the ambiguity.
3. Walk through the technical changes (SLA timing, dependency-aware scheduling, cache invalidation).
4. Cover the cultural change: the conversation pattern that ends "is it stale?" debates.

---

### What a Good Answer Covers:

* Data freshness vs job freshness vs view freshness.
* Why 06:00 was the wrong schedule and what should set the schedule.
* Sensor-based dependencies in the orchestrator (event-driven, not time-driven).
* Cache TTL vs cache invalidation triggered by the load.
* The "freshness SLO" as a one-line declaration per critical table.
* Communicating freshness in the BI tool itself (last-updated badge).
