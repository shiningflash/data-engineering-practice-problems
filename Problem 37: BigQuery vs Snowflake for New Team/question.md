## Problem 37: BigQuery vs Snowflake for a New Team

**Scenario:**
A startup is choosing a warehouse for a brand-new analytics team. They have ~50 engineers, no existing data warehouse, and they want to be productive within a month. Budget is reasonable but not unlimited. The team will start with simple dashboards and grow toward ML and reverse ETL.

In the interview, the question is:

> Why might you choose BigQuery over Snowflake, or the other way around, for a brand new analytics team?

---

### Your Task:

1. Compare on the things that actually matter at this stage.
2. Pick one for the scenario, defend it.
3. Mention when the other would have been the better choice.
4. Cover the things that look big in marketing but matter less in practice.

---

### What a Good Answer Covers:

* Pricing model: on-demand bytes vs warehouse compute time.
* Time to first query.
* Ecosystem in your existing stack (GCP-native vs cloud-agnostic).
* Concurrency and isolation.
* Migration cost later.
