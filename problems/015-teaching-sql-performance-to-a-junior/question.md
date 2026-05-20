---
id: 15
title: Teaching SQL Performance to a Junior
category: SQL Thinking
topics: [EXPLAIN, performance, mentoring, optimization]
difficulty: Medium
solution: solution.md
---

# Problem 15 — Teaching SQL Performance to a Junior

**Scenario:**
A junior engineer on your team writes a query that joins three tables and uses a window function. The query is correct. The result is right. But it takes 8 minutes to run on a table the rest of the team queries in 4 seconds. They ask you for help, and the manager asks you to mentor them.

In the interview, the question is:

> A junior wrote a correct query that runs slow. How do you teach them to make it faster, step by step?

This is a teaching question. The interviewer is checking whether you can mentor, not just whether you know optimization tricks.

---

### Your Task:

1. Walk through the mental model you would teach.
2. Show the actual checklist you would have them apply.
3. Give a real before-and-after example.
4. Mention the soft skills (how to make them learn, not just copy).

---

### What a Good Answer Covers:

* Read the EXPLAIN plan first.
* Filter early, project narrow.
* Avoid functions on indexed columns.
* Push aggregates before joins where possible.
* Be honest that "correct first, fast second" is a culture, not a rule.
