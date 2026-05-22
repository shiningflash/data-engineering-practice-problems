---
id: 58
title: Streaming Consumer Lag Diagnosis
category: Streaming
topics: [lag, back-pressure, skew, Flink UI]
difficulty: Medium
solution: solution.md
---

# Problem 58 — Streaming Consumer Lag Diagnosis

**Scenario:**
A Flink job consumes from Kafka and writes to a sink. The consumer lag has been growing steadily over the last 4 hours. By the time you check, it is 90 minutes behind. The on-call engineer wants to scale the job up immediately.

In the interview, the question is:

> A streaming job's consumer lag keeps growing. Walk through the questions you would ask before touching any code.

This is testing whether you can resist the "scale it up" reflex and find the real cause.

---

### Your Task:

1. List the questions you would ask first.
2. Explain how to read the lag pattern.
3. Cover the most common causes.
4. Decide when scaling is right and when it is the wrong move.

---

### What a Good Answer Covers:

* Is throughput slower than the source rate?
* Is the source rate suddenly higher than usual?
* Is the sink slow (back-pressure)?
* Hot key / skew.
* Resource constraints inside the job.
* When scaling helps; when it just hides the problem.
