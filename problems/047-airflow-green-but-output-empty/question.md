---
id: 47
title: Airflow Green but Output Empty
category: Debugging
topics: [silent success, idempotency, anomaly checks]
difficulty: Medium
solution: solution.md
---

# Problem 47 — Airflow Green but Output Empty

**Scenario:**
The pipeline ran. Airflow shows all tasks green. The downstream dashboard says yesterday's data is missing. The on-call engineer is confused: "everything succeeded, but the output table didn't update."

In the interview, the question is:

> An Airflow task is green but the output table did not update. What are the first three things you check?

---

### Your Task:

1. Explain why "task succeeded" is not the same as "data is correct."
2. Walk through the three quickest checks.
3. List the most common silent-success patterns.
4. Mention how to prevent this class of failure.

---

### What a Good Answer Covers:

* Success means the code did not throw, not that data is present.
* Empty input still produces empty output successfully.
* Row count checks and freshness checks as guardrails.
* Idempotent overwrite vs append: which makes silent failures invisible.
* dbt tests, Great Expectations, or simple SQL guards.
