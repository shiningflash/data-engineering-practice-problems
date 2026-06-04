---
id: 102
title: Critical Model, No Tests, Nobody Dares Touch It
category: Batch Pipelines & Orchestration
topics: [testing, refactoring, characterization tests, legacy]
difficulty: Hard
interview_value: strong
learn_order: 102
series: senior-scenarios
solution: solution.md
---

# Problem 102, Critical Model, No Tests, Nobody Dares Touch It

**Scenario:**
`fct_orders` is the most queried model in the warehouse. 200+ dashboards read from it. 12 dbt models reference it. It has zero tests. The SQL is 600 lines with three nested CTEs and four `CASE WHEN` statements. There is a known bug: refunds are sometimes double-counted in the southeast region. The fix is one line. The PR has been open for three weeks because nobody dares merge it. "What if it breaks something?" is the comment on every review. The lead asks you to make `fct_orders` safe to change.

In the interview, the question is:

> Walk me through how you make a critical, untested, much-depended-on model safe to change. What tests do you add, in what order, and why does this matter before the refactor?

---

### Your Task:

1. Explain why the team is paralysed and what to do about it.
2. Walk through the four layers of tests you add, in order, before changing any logic.
3. Cover characterization tests: how to lock down the model's current behaviour.
4. Explain how to then ship the one-line bug fix with confidence.

---

### What a Good Answer Covers:

* The PR is stuck because there is no safety net.
* Layer 1: schema tests (unique, not null, accepted_values).
* Layer 2: row-count and cardinality invariants.
* Layer 3: business invariants (sum reconciles to source).
* Layer 4: snapshot test (today's output vs frozen snapshot).
* The "tests first, then refactor" rule for legacy code.
