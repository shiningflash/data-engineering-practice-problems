---
id: 4
title: Schema Evolution and Validation for Streaming Events
category: Schema Validation
topics: [JSON, schema evolution, type coercion, pydantic]
difficulty: Medium
solution: solution.py
---

# Problem 4, Schema Evolution and Validation for Streaming Events

**Scenario:**
You are building a streaming pipeline that ingests user event data from many microservices.
The data comes in as JSON, like this:

```json
{"user_id": 101, "event_type": "login", "timestamp": "2025-10-14T12:00:00Z"}
{"user_id": 102, "event_type": "purchase", "amount": 59.99, "timestamp": "2025-10-14T12:02:15Z"}
{"user_id": "103", "event_type": "logout", "timestamp": "2025-10-14T12:05:20Z"}
{"event_type": "login", "timestamp": "2025-10-14T12:07:00Z"}
```

Because these events come from different teams and versions, they are often incomplete, inconsistent, or change over time:

* `user_id` might be a string or int
* `amount` may appear only for purchase events
* Some fields may be missing
* Future versions may add new fields (like `device` or `location`)

Your goal: validate and normalize these events before they go to a downstream system (BigQuery, Kafka, Pub/Sub).

---

### Task:

Write a Python program that:

1. Reads a JSON lines file (`events.jsonl`) line by line. Treat it as streaming input.
2. Validates and normalizes each event against this expected schema:

| Field | Type | Required | Notes |
| ---------- | ----- | -------- | ---------------------------------------------------------------- |
| user_id | int | Yes | Convert to int if possible. Skip event if missing or invalid. |
| event_type | str | Yes | Must be one of `"login"`, `"logout"`, `"purchase"` |
| timestamp | str | Yes | Must be valid ISO8601 |
| amount | float | No | Only required for `"purchase"` events. Default to 0.0 if missing. |
| device | str | No | Optional new field. Can be present or not. |

3. Writes valid normalized events to `cleaned_events.jsonl`.
4. Writes invalid events to `invalid_events.jsonl` with an extra `"error_reason"` field describing why they failed.

---

### Example Output (cleaned_events.jsonl):

```json
{"user_id": 101, "event_type": "login", "timestamp": "2025-10-14T12:00:00Z", "amount": 0.0}
{"user_id": 102, "event_type": "purchase", "timestamp": "2025-10-14T12:02:15Z", "amount": 59.99}
{"user_id": 103, "event_type": "logout", "timestamp": "2025-10-14T12:05:20Z", "amount": 0.0}
```

### Example Output (invalid_events.jsonl):

```json
{"event_type": "login", "timestamp": "2025-10-14T12:07:00Z", "error_reason": "missing user_id"}
{"user_id": "abc", "event_type": "purchase", "timestamp": "2025-10-14T12:09:00Z", "amount": "NaN", "error_reason": "user_id not convertible to int"}
```

---

### Bonus Challenges (Highly Recommended):

* Make your schema evolution-proof. Ignore unknown fields instead of failing.
* Keep counters: total events processed, valid, invalid.
* Use `pydantic` for validation (optional, very handy).

---

**Hints:**

* Use `json.loads()` for line-by-line streaming.
* Use `try/except` for type conversions.
* Keep validation and normalization in one clean function.
* Think about how you would handle new fields without code changes. That is the heart of schema evolution.

---
