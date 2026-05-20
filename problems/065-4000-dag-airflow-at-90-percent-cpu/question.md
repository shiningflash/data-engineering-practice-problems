---
id: 65
title: 4000 DAG Airflow at 90 Percent CPU
category: People & Process
topics: [Airflow, scheduler, parsing, scale-out]
difficulty: Medium
solution: solution.md
---

# Problem 65 — 4000 DAG Airflow at 90 Percent CPU

**Scenario:**
Your team's Airflow has grown to 4,000 DAGs over time. The scheduler is running at 90% CPU and missing schedules occasionally. Adding a bigger machine is the obvious fix, but the team has done that twice already and it always grows back.

In the interview, the question is:

> Your team's Airflow has 4000 DAGs and the scheduler is at 90 percent CPU. What is the first thing you would try, before scaling out?

This is the cost-vs-real-fix kind of question.

---

### Your Task:

1. Explain what the scheduler is doing.
2. Walk through the cheaper fixes.
3. Mention when scaling out is the right call.
4. Cover the structural issue.

---

### What a Good Answer Covers:

* DAG parsing as the main scheduler cost.
* Reducing DAG count or DAG complexity.
* Dynamic DAGs and parsing performance.
* min_file_process_interval and other tuning.
* When you have outgrown a single Airflow.
