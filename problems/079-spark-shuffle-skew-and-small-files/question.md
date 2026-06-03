---
id: 79
title: Spark Shuffle, Skew, and the Small File Problem
category: Cloud & Cost
topics: [Spark, shuffle, skew, partitioning]
difficulty: Hard
interview_value: must-have
learn_order: 85
solution: solution.md
---

# Problem 79, Spark Shuffle, Skew, and the Small File Problem

**Scenario:**
A nightly Spark job that aggregates a year of clickstream by user runs for four hours and costs the team a third of their EMR bill. Most of the executors finish in 20 minutes. A few stragglers grind on for the rest. The output dataset has 80,000 files, most under 1 MB. A new senior engineer hands you the job and asks you to make it fast and cheap. You start by explaining what is actually going wrong.

In the interview, the question is:

> Walk me through how a Spark job ends up slow and expensive, focusing on shuffles, data skew, and the small file problem. What do you actually change to fix it?

---

### Your Task:

1. Explain what a shuffle is and why every aggregation or join causes one.
2. Define data skew and show how it produces a few "long tail" tasks.
3. Explain the small file problem on both write and read sides.
4. Walk through a real diagnostic flow using the Spark UI: which tabs to open, what to look for.
5. Cover three concrete fixes (broadcast join, salting, AQE, coalesce / repartition).

---

### What a Good Answer Covers:

* Stages, tasks, and partitions as the unit of work.
* The shuffle as the moment data crosses the network.
* Why a single hot key destroys parallelism.
* Adaptive Query Execution (AQE) and what it can and cannot save.
* `coalesce` vs `repartition` and when each is right.
* The small file problem on Parquet output and how to size partitions.
