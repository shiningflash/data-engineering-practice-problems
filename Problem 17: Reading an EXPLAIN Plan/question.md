## Problem 17: Reading an EXPLAIN Plan

**Scenario:**
A query is slow. You ask the engineer "what does the EXPLAIN plan say?" and they shrug. Most engineers know `EXPLAIN ANALYZE` exists but freeze when they see the actual output. The interviewer wants to know if you can read it confidently and use it to diagnose.

In the interview, the question is:

> You see an EXPLAIN plan for the first time. Talk me through what you actually look at, and in what order.

---

### Your Task:

1. Explain what EXPLAIN tells you, in plain words.
2. Walk through the order in which you would scan a plan.
3. Show a sample plan and point out what would jump out to you.
4. List the four or five things that consistently cause slow queries.

---

### What a Good Answer Covers:

* The difference between EXPLAIN and EXPLAIN ANALYZE.
* Reading a plan bottom up (or innermost out).
* Row estimate vs actual row count: the biggest hint.
* Join types and what they mean.
* Common red flags: Seq Scan on big tables, Nested Loop with millions of rows, Sort spilling to disk.
