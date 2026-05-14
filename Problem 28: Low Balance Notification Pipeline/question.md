## Problem 28: Low Balance Notification Pipeline

**Scenario:**
A neobank wants to send a push notification "your balance is below $50" to each customer whose balance drops under that threshold. The notification should fire at most once per day per customer, must never wake up the wrong customer, and must respect the customer's local time zone (no push at 3 AM). They have 8 million customers.

In the interview, the question is:

> Design a "low balance" notification pipeline that runs daily and absolutely must not wake the wrong customer.

The phrase "must not wake the wrong customer" is the whole point of the question. The interviewer is testing how you think about correctness under retries, idempotency, and personalization.

---

### Your Task:

1. Sketch the daily pipeline.
2. Show how you guarantee "at most once" per customer per day.
3. Cover the local time zone and quiet-hours rules.
4. Cover what happens when the job retries.
5. Cover privacy and opt-out.

---

### What a Good Answer Covers:

* Batch eligibility computation in the warehouse.
* A notifications-sent log used as a dedup gate.
* Idempotent push with a unique key.
* Schedule per time zone, not one global schedule.
* What happens when the pipeline crashes mid-run.
