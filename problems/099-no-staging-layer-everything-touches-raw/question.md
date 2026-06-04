---
id: 99
title: No Staging Layer, Everything Touches Raw
category: Data Modeling
topics: [staging, layered architecture, dbt structure, refactoring]
difficulty: Medium
interview_value: strong
learn_order: 99
series: senior-scenarios
solution: solution.md
---

# Problem 99, No Staging Layer, Everything Touches Raw

**Scenario:**
You inherit a dbt project a junior set up six months ago. It works. 40 marts, all clean-looking SQL, builds in 20 minutes. Then last week the source team renamed `user_id` to `account_id` in the `users` source table. 31 of the 40 marts broke at once. Each one queries `raw.users` directly. Each one has to be edited and tested. Two days of work, half the team blocked. Meanwhile, you notice the same business logic ("active customer") is implemented in 8 different ways across 8 different marts, each one slightly different.

In the interview, the question is:

> What is missing from this project, and how do you introduce it without rewriting everything at once?

---

### Your Task:

1. Explain why every mart joining to raw is the underlying problem.
2. Walk through the three-layer architecture (raw, staging, marts) and what each layer is for.
3. Cover the gradual migration path: introducing staging without breaking what works.
4. Explain why this is the single highest-impact refactor most dbt projects need.

---

### What a Good Answer Covers:

* The "every mart talks to raw" anti-pattern.
* One staging model per source table, only renames and casts.
* Marts read staging, never raw.
* Centralised business logic (e.g., `is_active_user`) defined once.
* Migration: build staging, point marts one at a time, retire raw access at the end.
