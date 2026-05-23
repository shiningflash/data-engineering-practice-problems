---
id: 18
title: CTE vs Subquery
category: SQL Thinking
topics: [CTE, subquery, materialization, recursion]
difficulty: Medium
solution: solution.md
---

# Problem 18, CTE vs Subquery

**Scenario:**
A teammate refactors a long query, replacing every subquery with a CTE (`WITH... AS`) "for readability." The next day, the query is 4x slower in production. They're confused, because in older databases CTEs were always at least as fast as subqueries. You explain that this is a Postgres-specific (and historically common) gotcha that newer versions changed.

In the interview, the question is:

> When would you choose a CTE over a subquery, and when does it actually matter for performance?

---

### Your Task:

1. Explain what a CTE is, and what a subquery is, in one line each.
2. Explain the readability case for CTEs.
3. Explain the historical performance trap.
4. Give a clear rule of thumb for which to use today.

---

### What a Good Answer Covers:

* CTEs as "named temporary results."
* Postgres < 12 "optimization fence" behavior.
* Modern engines mostly inline CTEs.
* When you actually want a *materialized* CTE.
* Recursive CTEs, which only CTEs can do.
