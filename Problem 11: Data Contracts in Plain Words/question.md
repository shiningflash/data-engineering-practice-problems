## Problem 11: Data Contracts in Plain Words

**Scenario:**
A producer team renames a column from `user_id` to `userId` in their event stream as part of a refactor. They do not tell anyone. Three downstream pipelines break overnight, including the daily revenue report. After the postmortem, leadership asks: how do we stop this from happening every quarter?

The answer everyone keeps mentioning is "data contracts."

In the interview, the question is:

> What is a data contract, in plain words, and why are companies suddenly talking about them?

---

### Your Task:

1. Explain what a data contract is and what it is not.
2. Explain why this conversation is happening now.
3. Sketch what a real data contract looks like (columns, types, rules).
4. Explain how it gets enforced in practice.

---

### What a Good Answer Covers:

* The shift from "data is a side effect" to "data is a product."
* The contract as an agreement between a producer and a consumer.
* Schema, semantics, freshness, ownership.
* Where it gets enforced: producer side, ingest side, CI checks.
* Why it usually fails when it's only a document.
