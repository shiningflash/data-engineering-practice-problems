---
id: 68
title: Isolation Levels in Plain Words
category: Databases
topics: [isolation, snapshot, anomalies, MVCC]
difficulty: Medium
solution: solution.md
---

# Problem 68, Isolation Levels in Plain Words

**Scenario:**
A team is debugging an intermittent bug where a report sometimes shows a customer's balance as $0 right after a deposit. The deposit clearly went through. The report runs a long SELECT across many tables. Someone suspects an isolation issue. You are asked to explain the isolation levels and which one this team should be on.

In the interview, the question is:

> Explain Read Committed, Repeatable Read, and Serializable in plain words. Why does it matter which one you are on?

---

### Your Task:

1. Define each level in one sentence.
2. Show the anomaly each one prevents.
3. Cover defaults across common databases.
4. Pick the right level for the scenario.

---

### What a Good Answer Covers:

* Dirty read, non-repeatable read, phantom read.
* Postgres / MySQL / SQL Server default differences.
* Trade-off: stronger isolation, more locking or rollback risk.
* Snapshot isolation as a common middle ground.
* When the answer is "use the default plus careful design."
