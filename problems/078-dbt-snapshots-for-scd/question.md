---
id: 78
title: dbt Snapshots for Slowly Changing Dimensions
category: Data Modeling
topics: [dbt, snapshot, SCD type 2, history]
difficulty: Medium
interview_value: strong
learn_order: 79
solution: solution.md
---

# Problem 78, dbt Snapshots for Slowly Changing Dimensions

**Scenario:**
The finance team needs to know what a customer's billing plan was on any given day for the last two years. The source `customers` table in the OLTP database only holds the current state. Yesterday a refund dispute came in for a customer who changed their plan three times in six months. Finance has no way to see the history. The lead asks you to "build a Type 2 SCD in dbt."

In the interview, the question is:

> Walk me through how you would use dbt snapshots to track slowly changing dimensions, and where snapshots fit alongside other SCD strategies.

---

### Your Task:

1. Re-explain SCD Type 2 quickly (one paragraph, link mentally to problem 10).
2. Show a working dbt snapshot config and walk through what dbt does on each run.
3. Compare timestamp strategy vs check strategy and where each fails.
4. Cover the operational story: where snapshots live, when they should run, how to use them downstream.

---

### What a Good Answer Covers:

* The four columns dbt adds: `dbt_valid_from`, `dbt_valid_to`, `dbt_scd_id`, `dbt_updated_at`.
* Why snapshots are their own materialisation, not a model.
* Source freshness matters: a missed snapshot run is a hole in history.
* `check` strategy for sources without a reliable `updated_at`.
* Joining a fact to a snapshot via `BETWEEN dbt_valid_from AND dbt_valid_to`.
* When to use dbt snapshots vs CDC into Iceberg vs handwritten SCD logic.
