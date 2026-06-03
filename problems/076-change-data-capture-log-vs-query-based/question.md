---
id: 76
title: Change Data Capture, Log-Based vs Query-Based
category: Batch Pipelines & Orchestration
topics: [CDC, Debezium, binlog, replication]
difficulty: Medium
interview_value: must-have
learn_order: 80
solution: solution.md
---

# Problem 76, Change Data Capture, Log-Based vs Query-Based

**Scenario:**
Your team has been doing nightly full-table snapshots of a 200M-row Postgres OLTP database into the warehouse. The snapshot takes four hours, blows up the source disk IO, and silently misses any row that was created and deleted on the same day. The product team wants the warehouse to be "near real-time." The DBA refuses to add triggers on the production tables. You suggest change data capture.

In the interview, the question is:

> What is change data capture, what are the two main flavours, and how do you pick between them?

---

### Your Task:

1. Define CDC in plain English and say why you would reach for it.
2. Compare log-based and query-based CDC. What each gets right and where each hurts.
3. Sketch a realistic log-based setup (Postgres + Debezium + Kafka + warehouse).
4. Cover the three gotchas that bite real CDC pipelines: initial snapshot, schema changes, and large transactions.

---

### What a Good Answer Covers:

* Why nightly full reloads break at scale.
* The Postgres WAL / MySQL binlog as the source of truth for changes.
* What query-based CDC looks like with an `updated_at` column and why deletes are the hole.
* How Debezium handles the initial snapshot.
* Schema evolution: drop column on the source, what happens downstream.
* The transactional ordering guarantee and what it does not cover.
