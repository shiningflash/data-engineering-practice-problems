---
id: 81
title: Delta vs Iceberg vs Hudi
category: Storage & Lakehouse
topics: [Delta Lake, Iceberg, Hudi, lakehouse]
difficulty: Medium
interview_value: strong
learn_order: 83
solution: solution.md
---

# Problem 81, Delta vs Iceberg vs Hudi

**Scenario:**
Your platform team is picking a lakehouse table format for the next two years of new pipelines. The shop runs Spark, Trino, and some Snowflake. A Databricks rep pitched Delta Lake. The Snowflake rep pitched Iceberg. Someone read a Uber engineering blog about Hudi. The lead wants a one-pager that says "pick X for these reasons" with the trade-offs honest.

In the interview, the question is:

> Three open table formats exist for lakehouses: Delta Lake, Iceberg, and Hudi. Compare them and recommend one for a multi-engine shop.

---

### Your Task:

1. Explain what an open table format is and what all three share.
2. Compare each format on metadata, engine support, schema evolution, and operational complexity.
3. Cover where each one shines.
4. Recommend one for the scenario above and defend it.

---

### What a Good Answer Covers:

* The shared base: ACID on object storage, schema evolution, time travel.
* Delta's transaction log of JSON + checkpoint parquet.
* Iceberg's snapshot/manifest tree and column IDs.
* Hudi's two table types (CoW, MoR) and indexed lookups.
* Engine support in 2026 (Spark, Trino, DuckDB, Snowflake, BigQuery).
* The "pick by who is reading" rule of thumb.
