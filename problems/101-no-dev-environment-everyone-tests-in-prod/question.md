---
id: 101
title: No Dev Environment, Everyone Tests in Prod
category: People & Process
topics: [environments, dbt targets, schema-per-PR, CI]
difficulty: Medium
interview_value: strong
learn_order: 101
series: senior-scenarios
solution: solution.md
---

# Problem 101, No Dev Environment, Everyone Tests in Prod

**Scenario:**
The team you joined has one dbt project. It targets production. To test a change, you either run it in prod and hope, or run it locally with prod credentials and write to a temp table. Last week a teammate accidentally wrote a 50M-row CTAS to `analytics.fct_orders_test` and forgot to drop it. Storage cost spiked 12%. Another teammate's "quick test" overwrote `fct_revenue` for two hours before someone caught it. The CTO asks you to set up "a proper dev environment" by end of next week.

In the interview, the question is:

> Walk me through how you separate dev, CI, and prod for a dbt project, what the boundaries are, and how you prevent the "I tested in prod" mistake from happening again.

---

### Your Task:

1. Explain why "we share prod" is unsafe and how the team got there.
2. Define dev, CI, and prod as three distinct environments with three distinct rules.
3. Walk through the dbt targets and schema patterns that make it work.
4. Cover the cleanup and permission changes that keep dev cheap and prod safe.

---

### What a Good Answer Covers:

* `target: dev` writes to a personal schema named after the developer.
* `target: ci` writes to a `pr_NNN` schema, dropped after merge.
* `target: prod` is locked: only the CI service account can write.
* Production credentials never leave CI.
* A nightly job drops dev and CI schemas older than N days.
