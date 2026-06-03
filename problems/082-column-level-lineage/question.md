---
id: 82
title: Column-Level Lineage in Practice
category: Batch Pipelines & Orchestration
topics: [lineage, OpenLineage, dbt, impact analysis]
difficulty: Medium
interview_value: strong
learn_order: 87
solution: solution.md
---

# Problem 82, Column-Level Lineage in Practice

**Scenario:**
A product manager wants to deprecate the `legacy_score` column on the `customers` table. Three engineers say "we don't think anything uses it." A junior says "let me check." Four hours later they list 12 dashboards and 7 dbt models that touch it directly. Nobody knows about the four downstream models that read those. The PM postpones the deprecation. The lead asks you to set up column-level lineage so the next deprecation takes minutes, not days.

In the interview, the question is:

> Why is column-level lineage useful and how do you set it up across a typical warehouse + dbt + BI stack?

---

### Your Task:

1. Explain the difference between table-level and column-level lineage.
2. List the three concrete things lineage unlocks (impact analysis, root-cause debugging, compliance).
3. Walk through how lineage is actually extracted (SQL parsing, dbt manifest, OpenLineage events).
4. Cover the real limits: dynamic SQL, views, UDFs, BI tools that hide their queries.

---

### What a Good Answer Covers:

* dbt's `manifest.json` and `catalog.json` as the cheapest source of lineage.
* OpenLineage as the open standard for emitting lineage from anywhere.
* Tools that consume it (DataHub, OpenMetadata, Marquez, Atlan, Collibra).
* Why BI tools are usually the lineage cliff.
* The difference between static lineage (from SQL) and runtime lineage (from execution).
