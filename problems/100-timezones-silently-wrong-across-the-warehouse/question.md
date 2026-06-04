---
id: 100
title: Timezones Silently Wrong Across the Warehouse
category: SQL & Querying
topics: [timezones, UTC, timestamps, daylight saving]
difficulty: Medium
interview_value: strong
learn_order: 100
series: senior-scenarios
solution: solution.md
---

# Problem 100, Timezones Silently Wrong Across the Warehouse

**Scenario:**
A marketing analyst messages: "Our July 4th campaign report does not match what Meta is reporting. We're under by about 6%." After two days of digging, you find it. The `events` table stores `event_at` as `TIMESTAMP WITHOUT TIME ZONE`. The mobile app was sending local device time. The web app was sending UTC. Group-by-day was using `DATE(event_at)`, which silently interpreted local-time and UTC values the same way. For users in the US, "23:00 July 4 local" became "03:00 July 5 UTC," and the event slipped into the next day's bucket. Across the warehouse, "what happened on day X" is off by some fraction wherever the timezone story is unclear.

In the interview, the question is:

> How would you fix timezones across the warehouse, and what does a clean default look like so this does not happen again?

---

### Your Task:

1. Explain why this break is silent and slow to notice.
2. Walk through auditing what is currently stored where.
3. Define the clean default: UTC in storage, local for display, and the daylight-saving trap.
4. Cover the migration: fixing existing tables without breaking historical reports.

---

### What a Good Answer Covers:

* `TIMESTAMP` vs `TIMESTAMPTZ` and why one is a footgun.
* Storing UTC, deriving local at query time with explicit user timezone.
* Why daylight saving makes "local date" group-bys unreliable.
* Adding `_at_utc` and `_at_local` columns explicitly for clarity.
* The data contract: every new event field documents its timezone.
