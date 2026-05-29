---
id: 66
title: Indexes When to Add and When They Hurt
category: Databases
topics: [indexes, B-tree, write cost, EXPLAIN]
difficulty: Easy
solution: solution.md
---

# Problem 66, Indexes When to Add and When They Hurt

**Scenario:**
A junior teammate just learned what indexes are and is enthusiastically adding them to every column on every table. The writes on the production database are getting slower, but most reads now look fine. You are asked to mentor them on when to add an index and when not to.

In the interview, the question is:

> When would you add an index, and when would adding one actually hurt? Walk me through how you decide.

---

### Your Task:

1. Explain what an index actually is, in one paragraph.
2. List the cases where an index is the right answer.
3. List the cases where it is the wrong answer.
4. Cover the trade-off: read speed vs write cost.

---

### What a Good Answer Covers:

* B-tree as the default kind.
* The "selectivity" idea — an index on a low-cardinality column rarely helps.
* The write amplification cost.
* Composite indexes and column order.
* Covering indexes.
* The "looks fine in dev, slow in prod" trap.
