---
id: 89
title: Great Expectations vs dbt Tests
category: Batch Pipelines & Orchestration
topics: [data testing, dbt tests, Great Expectations, CI]
difficulty: Medium
interview_value: strong
learn_order: 86
solution: solution.md
---

# Problem 89, Great Expectations vs dbt Tests

**Scenario:**
A team is starting to take data quality seriously. The lead has two camps: one wants to use Great Expectations because "it has hundreds of validators and a UI", the other says "we already have dbt, why add another tool, just use dbt tests." You are asked to write a one-page decision so the team can move on.

In the interview, the question is:

> dbt tests, Great Expectations, or both? What does each one cover that the other does not, and how should a team pick?

---

### Your Task:

1. Explain what dbt tests cover, with examples.
2. Explain what Great Expectations covers, with examples.
3. Compare on placement (where the test runs), expressiveness, lifecycle, and operational overhead.
4. Recommend a pragmatic stack for the team in the scenario.
5. Cover the testing pyramid for data: source tests, model tests, contract tests, monitoring.

---

### What a Good Answer Covers:

* dbt's four built-in tests and the custom test pattern.
* Great Expectations' expectation suites and data docs.
* Test placement: source vs model vs downstream.
* Why neither replaces observability (see problem 84).
* The cost of running tests on big tables and how to scope them.
