---
id: 98
title: Same Metric, Three Different Numbers
category: Data Modeling
topics: [semantic layer, single source of truth, definitions, governance]
difficulty: Medium
interview_value: must-have
learn_order: 98
series: senior-scenarios
solution: solution.md
---

# Problem 98, Same Metric, Three Different Numbers

**Scenario:**
Monday's standup. The finance dashboard says June revenue is $1.20M. The sales dashboard says $1.21M. The CFO's board deck, sent yesterday, says $1.18M. All three queries say "from the warehouse." All three queries say "June revenue." The CEO asks which number is right. Three teams point at each other. You realise no one in the room knows the actual answer because three different SQL queries were used and nobody compared them.

In the interview, the question is:

> Walk me through how you resolve this without picking sides, and how you stop it from happening again. What is the durable fix that most teams skip because it feels slow?

---

### Your Task:

1. Resolve the immediate disagreement by reading the actual SQL behind each number.
2. Identify the patterns that cause this (timezone, refunds, currency, definition of "order").
3. Walk through introducing a single source of truth for the metric.
4. Cover what changes for the next metric so this does not happen again.

---

### What a Good Answer Covers:

* Reading SQL is faster than running meetings.
* The four usual definition gaps: refunds, time zone, currency, order vs line.
* A `fct_revenue_daily` (or semantic-layer metric) that every dashboard joins to.
* Naming the metric what it actually is ("gross revenue, USD, ex-tax, on order date").
* The metric review process for any new metric.
