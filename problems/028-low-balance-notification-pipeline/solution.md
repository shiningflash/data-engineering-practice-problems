## Solution 28: Low Balance Notification Pipeline

### The pipeline

```
   ┌──────────────────────────────────────────────┐
   │  Warehouse (BigQuery / Snowflake)            │
   │   - accounts (current balance, tz, opt-in)   │
   │   - notifications_sent (audit log)           │
   └────────────────┬─────────────────────────────┘
                    │
            Scheduled per time zone
                    │
                    ▼
   ┌──────────────────────────────────────────────┐
   │  Eligibility query (SQL)                     │
   │                                              │
   │  WHERE balance < threshold                   │
   │    AND user is opted in                      │
   │    AND user's local time is within           │
   │        send-window (9 AM .. 7 PM)            │
   │    AND no notification sent today already    │
   │        for this user (anti-join)             │
   │                                              │
   │  → produces a small "candidates" set         │
   └────────────────┬─────────────────────────────┘
                    │
                    ▼
   ┌──────────────────────────────────────────────┐
   │  Notification job                            │
   │   For each candidate:                        │
   │    1. Insert into notifications_sent with    │
   │       unique key (user_id, date, type)       │
   │    2. If insert succeeds (no duplicate),     │
   │       call push API with idempotency_key     │
   │       = the same (user_id, date, type) hash  │
   │    3. If insert fails (already there), skip  │
   └────────────────┬─────────────────────────────┘
                    │
                    ▼
   ┌──────────────────────────────────────────────┐
   │  Push provider (APNs / FCM / Twilio)         │
   │  Receives idempotency_key, dedupes on it     │
   └──────────────────────────────────────────────┘
```

The trick: **the dedup gate is a row in a real table with a unique constraint**. The order is "claim the right to send" first, then "send." If two workers try the same user at the same instant, only one wins the INSERT, only one calls the push API.

### The eligibility query

```sql
WITH local_now AS (
  SELECT
    a.user_id,
    a.balance,
    a.timezone,
    a.threshold,
    DATE(CURRENT_TIMESTAMP() AT TIME ZONE a.timezone) AS local_date,
    EXTRACT(HOUR FROM CURRENT_TIMESTAMP() AT TIME ZONE a.timezone) AS local_hour
  FROM accounts a
  WHERE a.notifications_opt_in = TRUE
    AND a.low_balance_enabled  = TRUE
)
SELECT n.user_id
FROM local_now n
LEFT JOIN notifications_sent s
  ON  s.user_id = n.user_id
  AND s.notification_type = 'low_balance'
  AND s.local_date = n.local_date
WHERE n.balance < n.threshold
  AND n.local_hour BETWEEN 9 AND 18
  AND s.user_id IS NULL;
```

This finds users who:

* Are opted in.
* Are below their threshold (note: per-user threshold, not a global $50).
* Are inside their local 9-7 PM window.
* Have not yet received the notification today.

The `LEFT JOIN... IS NULL` is the dedup gate at query time. It is fast and avoids sending to anyone we already sent.

### The unique constraint is the real safety

The query is fast but not safe by itself. If the job runs twice (Airflow retry), both runs could see the same eligible user. The unique constraint in `notifications_sent` is what makes this idempotent.

```sql
CREATE TABLE notifications_sent (
  user_id           STRING,
  notification_type STRING,
  local_date        DATE,
  sent_at           TIMESTAMP,
  push_status       STRING,
  PRIMARY KEY (user_id, notification_type, local_date)
);
```

The notification worker pattern:

```python
def send_one(user_id, local_date):
    key = (user_id, "low_balance", local_date)
    try:
        notifications_sent.insert(
            user_id=user_id,
            notification_type="low_balance",
            local_date=local_date,
            sent_at=now(),
            push_status="pending",
        )
    except UniqueViolation:
        return                       # someone else already sent

    push_provider.send(
        user_id=user_id,
        body="Your balance is low",
        idempotency_key=hash(key),   # so the push API also dedupes
    )

    notifications_sent.update(key, push_status="delivered")
```

The unique constraint guarantees "at most once per user per day, per notification type." Even if 50 workers retry the same user, only one row gets inserted, only one push goes out.

### Quiet hours and time zones

This is the part most teams get wrong. They run one global "8 AM" cron and surprise users in other time zones.

Right approach: the eligibility query knows each user's time zone. Run the job often (every hour) but the WHERE clause filters to users whose **local hour** is currently in the allowed window. So a user in Singapore is checked when it is 9 AM in Singapore. A user in San Francisco gets checked when it is 9 AM in SF.

```sql
WHERE EXTRACT(HOUR FROM CURRENT_TIMESTAMP() AT TIME ZONE a.timezone) BETWEEN 9 AND 18
```

This produces a rolling wave through the day rather than one global send.

### What about a user with no time zone set?

Two policies, pick consciously:

* Conservative: fall back to UTC and only send between 9 AM and 6 PM UTC (which spans Europe). Some users get nothing, but no one gets woken.
* Best guess: infer from the country code on their account.

I would default to conservative for the first launch.

### Privacy and opt-out

The `notifications_opt_in` and feature-specific flags (`low_balance_enabled`) live in the user profile. The query checks both. Two protections:

* A user who opts out today does not receive the message even if they were below the threshold this morning. The opt-out check is in the live query, not a snapshot.
* A user who deletes their account flows through CDC into the warehouse and is marked inactive. They are filtered out.

### What can go wrong

**Crash mid-run.** Half the inserts happened, half did not. Re-running the job sees the half that did, skips them, sends to the rest. No duplicates. The unique constraint is doing the work.

**Push provider double-sends.** APNs and FCM both support idempotency keys. We pass the same key for the same (user, type, date). The provider dedupes.

**The balance flickers.** A user dropped to $49, the job sent the message, then their salary hit and the balance jumped to $5,000. We do not "take back" the notification. The day's row exists. They will not get the message again tomorrow unless they drop again.

**Time zone update.** A user changed their time zone after we evaluated them. We sent at 9 AM old time zone, which is now 3 AM in their new one. Sad but unavoidable. Mitigation: re-evaluate the row's `local_hour` at send time, not just query time.

**The threshold changes.** A user lowered their threshold from $100 to $20. Tomorrow's query naturally picks them up at the new threshold. No backfill needed.

### Why I would NOT do this in a streaming job

Tempting design: "send the notification the moment the balance drops below the threshold." Two problems:

* Need to suppress duplicates across a day, including across pauses in the stream. Stream state must persist for 24 hours per user.
* Quiet hours mean the event needs to be delayed until morning. Now you need a "send later" queue.
* A failed pipeline silently drops notifications.

A daily batch job, run hourly per time zone, with a unique constraint dedup, is simpler and equally good for this use case. Real-time would matter if the SLA were "within 5 minutes of the balance dropping," but it is not.

### Common mistakes interviewers want you to name

1. **No unique constraint.** Retries duplicate notifications.
2. **One global cron.** Wakes up users at 3 AM.
3. **Insert row AFTER push.** Crash window: push sent, no record, retry sends again.
4. **Inferring time zone from the device IP.** Inaccurate and creepy.
5. **Same template for every user.** Should be localized.

### Bonus follow-up the interviewer might throw

> *"How would you handle a customer who responds 'stop' to the notification?"*

The response is a customer-care channel signal. Route it back into the account record as an opt-out on this specific notification type. The next day's eligibility query filters them out. The opt-out is per notification type so they can still get fraud alerts even if they muted low-balance notifications.
