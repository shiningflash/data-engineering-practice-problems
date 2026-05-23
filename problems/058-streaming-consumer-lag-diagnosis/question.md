---
id: 58
title: Streaming Consumer Lag Diagnosis
category: Streaming
topics: [lag, back-pressure, skew, Flink UI]
difficulty: Medium
solution: solution.md
---

# Problem 58, Streaming Consumer Lag Diagnosis

**Scenario:**
A Flink job consumes from Kafka and writes to a sink. Consumer lag has grown steadily over the last 4 hours. By the time you look, the job is 90 minutes behind. The on-call engineer wants to scale it up right now.

In the interview, the question is:

> A streaming job's consumer lag keeps growing. Walk through the questions you would ask before touching any code.

The interviewer wants to see if you can resist the "scale it up" reflex and find the actual cause.

---

### Your Task:

1. List the questions you would ask first.
2. Explain how to read the lag pattern.
3. Cover the common causes.
4. Say when scaling is the right call and when it isn't.

---

### What a Good Answer Covers:

* Is throughput slower than the source rate?
* Is the source rate suddenly higher than usual?
* Is the sink slow (back-pressure)?
* Hot key or skew.
* Resource constraints inside the job.
* When scaling helps and when it hides the problem.
