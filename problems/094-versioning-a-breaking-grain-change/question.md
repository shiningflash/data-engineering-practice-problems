---
id: 94
title: Versioning a Breaking Grain Change
category: Data Modeling
topics: [versioning, grain, dbt, deprecation, contracts]
difficulty: Hard
interview_value: must-have
learn_order: 94
series: senior-scenarios
solution: solution.md
---

# Problem 94, Versioning a Breaking Grain Change

**Scenario:**
The product team wants per-line analysis on orders: which SKUs ship together, which lines get refunded. Your current `fct_orders` is one row per order. You need to change it to one row per order line. 30 dashboards and 12 dbt models depend on the current grain. A naive change breaks every revenue number in the company on the day you ship it. The CFO's board meeting is in three weeks. The lead asks you to plan the rollout.

In the interview, the question is:

> Walk me through how you ship a breaking change to a heavily-used model. What do you version, how do you keep the old grain alive during the transition, and how do you communicate the deprecation.

---

### Your Task:

1. Explain why this is a contract change, not a refactor.
2. Design the dual-version setup: v1 and v2 living side by side.
3. Cover the deprecation timeline and what milestones go in writing.
4. Walk through the rollback plan if v2 misbehaves after cutover.

---

### What a Good Answer Covers:

* The grain change is a semantic break, not a syntactic one.
* dbt's `versions:` feature and `ref('fct_orders', v=1)` syntax.
* The migration matrix: which consumers move when.
* `is_deprecated` and `deprecation_date` metadata on v1.
* Parallel-running both grains and validating row totals match.
* The communication cadence: announce, remind, deprecate, retire.
