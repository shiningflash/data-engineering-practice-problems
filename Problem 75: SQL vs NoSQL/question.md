## Problem 75: SQL vs NoSQL

**Scenario:**
A team is starting a new service. Half want Postgres because "we know it." Half want DynamoDB because "we need scale." Both arguments are weak. They ask you to help them choose for real reasons.

In the interview, the question is:

> When would you choose SQL, when would you choose NoSQL, and what does "NoSQL" even mean these days?

---

### Your Task:

1. Clear up what "NoSQL" actually covers.
2. Walk through the dimensions that matter.
3. Pick for the scenario, with assumptions.
4. Cover the "use both" pattern.

---

### What a Good Answer Covers:

* NoSQL is four very different families (KV, document, wide-column, graph).
* SQL still wins on most general apps.
* When you really need NoSQL: scale, document shape, KV access patterns.
* The trade-off: schema flexibility and scale vs joins and transactions.
* Most companies use both.
