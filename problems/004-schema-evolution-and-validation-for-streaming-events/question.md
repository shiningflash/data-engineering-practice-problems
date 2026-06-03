---
id: 4
title: Schema Evolution and Validation for Streaming Events
category: Streaming
topics: [JSON, schema evolution, type coercion, pydantic]
difficulty: Medium
interview_value: strong
learn_order: 41
solution: solution.py
---

# Problem 4, Schema Evolution and Validation for Streaming Events

## Scenario

A streaming pipeline ingests user events from many microservices into Kafka. Producer teams move at different speeds: some send the v1 schema, some have already added a `device` field, some send `user_id` as a string when the contract says int. Downstream wants only clean, normalized events.

```json
{"user_id": 101, "event_type": "login", "timestamp": "2025-10-14T12:00:00Z"}
{"user_id": 102, "event_type": "purchase", "amount": 59.99, "timestamp": "2025-10-14T12:02:15Z"}
{"user_id": "103", "event_type": "logout", "timestamp": "2025-10-14T12:05:20Z"}
{"event_type": "login", "timestamp": "2025-10-14T12:07:00Z"}
```

```mermaid
flowchart LR
    A([microservice v1])
    B([microservice v2<br/>adds device])
    C([microservice v1.5<br/>sends user_id as string])

    Q([Kafka topic<br/>raw events])

    V([Validator<br/>coerce + validate])

    OK([cleaned_events.jsonl])
    BAD([invalid_events.jsonl<br/>with error_reason])

    A --> Q
    B --> Q
    C --> Q
    Q --> V
    V --> OK
    V --> BAD

    style A fill:#dcfce7,stroke:#15803d,color:#14532d
    style B fill:#dcfce7,stroke:#15803d,color:#14532d
    style C fill:#dcfce7,stroke:#15803d,color:#14532d
    style Q fill:#fef3c7,stroke:#a16207,color:#713f12
    style V fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    style OK fill:#dcfce7,stroke:#15803d,color:#14532d
    style BAD fill:#fecaca,stroke:#b91c1c,color:#7f1d1d
```

## Schema

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `user_id` | int | yes | Coerce from string if possible. Reject if missing or not coercible. |
| `event_type` | str | yes | One of `login`, `logout`, `purchase`. |
| `timestamp` | str | yes | Valid ISO 8601. |
| `amount` | float | no | Required for `purchase` only. Default to `0.0` if absent. |
| `device` | str | no | New optional field. Pass through if present. |
| any other field | - | no | Unknown fields are silently kept under `_extra`. |

## Task

Read `events.jsonl` line by line. Write valid normalized events to `cleaned_events.jsonl`. Write rejects to `invalid_events.jsonl` with an `error_reason`.

## Bonus

- Support schema **versioning** so a `schema_version` field on the event picks the right validator.
- Log per-error reject counts at the end.
- Discuss how this hooks into a real schema registry (Confluent, Glue) and the trade-offs versus Pydantic-only validation.

## What a Good Answer Covers

- An incremental progression: manual `try/except`, dataclass with coercion, Pydantic model with strict and lax variants.
- Awareness that unknown fields are *not* errors; they are a future-compatibility signal.
- The reject sink with reasons, because downstream owners will need it.
- Time and space complexity per approach (mostly trivial here; the interview signal is the design).
