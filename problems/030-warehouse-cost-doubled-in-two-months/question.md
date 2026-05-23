---
id: 30
title: Warehouse Cost Doubled in Two Months
category: Scenarios
topics: [cost, governance, comms, INFORMATION_SCHEMA]
difficulty: Medium
solution: solution.md
---

# Problem 30, Warehouse Cost Doubled in Two Months

**Scenario:**
Your finance team forwards a bill. The Snowflake or BigQuery bill is up 100% over two months, from $14,000/month to $28,000/month. They want an explanation by Friday, and they want it not to grow further. The engineering manager wants no breaking changes for the existing analytics team.

In the interview, the question is:

> Your team's warehouse cost doubled in two months. Walk through the conversation you would have with finance and with engineering.

This is a hybrid: technical investigation plus stakeholder management.

---

### Your Task:

1. Walk through your investigation in the warehouse.
2. Show how you would frame the answer for finance vs engineering.
3. Sketch the immediate cost reductions you would propose.
4. Cover the longer-term governance.

---

### What a Good Answer Covers:

* Reading the warehouse usage tables (INFORMATION_SCHEMA, ACCOUNT_USAGE).
* Splitting cost by query, by user, by warehouse, by table.
* The 80/20 rule of warehouse cost: a handful of queries.
* The conversation: finance wants a number, engineering wants a plan.
* Tagging, alerting, and budgets.
