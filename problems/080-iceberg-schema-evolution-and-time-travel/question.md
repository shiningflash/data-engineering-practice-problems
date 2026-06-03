---
id: 80
title: Iceberg, Schema Evolution and Time Travel
category: Storage & Lakehouse
topics: [Iceberg, lakehouse, schema evolution, time travel]
difficulty: Medium
interview_value: must-have
learn_order: 82
solution: solution.md
---

# Problem 80, Iceberg, Schema Evolution and Time Travel

**Scenario:**
Your team writes daily Parquet files into S3, partitioned by date, registered in a Hive metastore. A backfill three weeks ago renamed `user_id` to `customer_id` on the source. The day-by-day files now disagree. Spark reads break on the older partitions. A junior asks if the team should "just rename the column in the metastore." A senior mentions Iceberg has "schema evolution." The lead wants you to explain what Iceberg actually buys and whether the team should migrate.

In the interview, the question is:

> What problem does Apache Iceberg solve that plain Parquet on object storage does not, and how does it handle schema evolution and time travel?

---

### Your Task:

1. Explain the three pain points of "Parquet files in S3 + Hive metastore" at scale.
2. Describe Iceberg's table format at the level of snapshot, manifest, data file.
3. Walk through what happens when you add, rename, and drop a column.
4. Cover time travel queries and the operational cost of maintaining an Iceberg table.

---

### What a Good Answer Covers:

* Atomic commits on object storage.
* The metadata tree: snapshot, manifest list, manifest, data file.
* Column IDs vs column names, and why that makes safe rename possible.
* `AS OF` queries and snapshot retention.
* Compaction, snapshot expiry, orphan file cleanup.
* When Iceberg is overkill (small tables, single-engine workloads).
