---
id: 86
title: Event Tracking Schema Design
category: Streaming
topics: [event tracking, telemetry, schema, analytics]
difficulty: Medium
interview_value: strong
learn_order: 84
solution: solution.md
---

# Problem 86, Event Tracking Schema Design

**Scenario:**
A product analytics team has three years of event data. Some events are named `signup`, some `user_signed_up`, some `UserSignup`. Properties are inconsistent: one event has `user_id`, another has `userId`, a third has `uid`. Queries take hours and answers disagree. The PM asks "can we just rename them now." You sit down with the analytics engineer to design a tracking schema worth keeping for the next three years.

In the interview, the question is:

> Design a clean event tracking schema for a product. What do you put in every event, what stays out, and how do you avoid the mess most products end up in?

---

### Your Task:

1. Define the common envelope: properties every event should have.
2. Design the event taxonomy (naming conventions, hierarchies, version).
3. Cover the contract enforcement story (schema registry, CI checks, client SDKs).
4. Walk through migrating a legacy mess to a clean schema.

---

### What a Good Answer Covers:

* `event_id`, `user_id`, `timestamp`, `session_id`, `source`, `schema_version`.
* Verb-noun naming, lower_snake_case, no abbreviations.
* Why "page_viewed" is better than "page_view" (action, not noun).
* Schema registry as the contract (Avro, Protobuf, JSON schema).
* The dual-schema migration: emit old + new for a window, then cut over.
