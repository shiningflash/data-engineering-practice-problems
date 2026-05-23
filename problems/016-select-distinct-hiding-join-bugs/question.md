---
id: 16
title: SELECT DISTINCT Hiding Join Bugs
category: SQL Thinking
topics: [DISTINCT, joins, grain, semi-join]
difficulty: Medium
solution: solution.md
---

# Problem 16, SELECT DISTINCT Hiding Join Bugs

**Scenario:**
An analyst on the team writes `SELECT DISTINCT` on almost every query. When you ask why, they say "because the joins keep duplicating rows, and DISTINCT cleans it up." The numbers in their dashboards mostly look right, but every few weeks something is off by a small amount and nobody can explain why.

In the interview, the question is:

> An analyst is using SELECT DISTINCT everywhere because joins keep producing duplicates. What is actually going wrong, and how would you fix it without DISTINCT?

---

### Your Task:

1. Explain what causes the duplicates in the first place.
2. Show the bug with a small example.
3. Show two ways to fix it without DISTINCT.
4. Explain why DISTINCT is a dangerous habit, not just a slow one.

---

### What a Good Answer Covers:

* The cardinality (grain) of each table in the join.
* "Many-to-many" joins exploding row counts.
* Aggregating before joining.
* Using EXISTS or a semi-join.
* Why DISTINCT can also collapse rows that *should* be different.
