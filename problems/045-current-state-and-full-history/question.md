---
id: 45
title: Current State and Full History
category: Data Modeling
topics: [event sourcing, projections, MV, audit]
difficulty: Medium
solution: solution.md
---

# Problem 45, Current State and Full History

**Scenario:**
The reporting team has a hot debate. Some queries want "the current state of every order" (latest status, shipped or cancelled, current refund amount). Other queries want "the full history" (every state change, when, who, why). Right now the team is duplicating the data: one table with current state, a parallel table with events. Storage is doubled. It is the wrong shape.

In the interview, the question is:

> A reporting team wants both "current state" and "full history" of every order. How do you build that without doubling storage?

---

### Your Task:

1. Show the right shape.
2. Sketch how to derive current state from history cheaply.
3. Cover the query patterns.
4. Address the team's worry about query speed.

---

### What a Good Answer Covers:

* One source-of-truth events table.
* A derived "current state" view or materialized view.
* Indexes / clustering on the event table for fast latest-state lookups.
* When you really do need a separate current-state table.
