## Problem 55: Partitioning, Clustering, Materialized Views

**Scenario:**
A junior engineer asks you to explain the three main BigQuery cost levers and when to use each. They have heard the words, used them inconsistently, and want a clear picture.

In the interview, the question is:

> Explain how partitioning, clustering, and materialized views each save money in BigQuery, and when each one is the right tool.

This is a "do you actually understand these" question, with the test that your answer can be used by a junior the next day.

---

### Your Task:

1. Explain each one in one sentence.
2. Show a small example of when each saves money.
3. Walk through the combinations.
4. Mention the order to think about them.

---

### What a Good Answer Covers:

* Partitioning prunes whole partitions before scan.
* Clustering prunes blocks inside a partition.
* Materialized views compute the aggregate once and reuse it.
* When two or three work together.
* Common mistakes.
