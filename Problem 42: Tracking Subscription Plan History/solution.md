## Solution 42: Tracking Subscription Plan History

### Short version you can say out loud

> A `subscription_periods` table. Each row is one continuous stretch of time during which the customer was on one specific plan, with `valid_from` and `valid_to` columns. When the plan changes, we close the current row and open a new one. The "current" plan is just the row whose `valid_to` is in the far future. Disputes get resolved by joining the bill date against this table. Audit events also exist separately, but they record "who did what" rather than "what was true when."

### The table

```sql
CREATE TABLE subscription_periods (
  period_id        UUID PRIMARY KEY,
  customer_id      UUID NOT NULL,
  plan_id          UUID NOT NULL,
  billing_cycle    TEXT NOT NULL,        -- monthly, yearly
  status           TEXT NOT NULL,        -- active, paused
  valid_from       TIMESTAMP NOT NULL,
  valid_to         TIMESTAMP NOT NULL,   -- '9999-12-31' for current
  created_by       TEXT,                 -- user / system
  created_at       TIMESTAMP NOT NULL DEFAULT NOW(),

  CONSTRAINT period_is_well_formed CHECK (valid_from < valid_to)
);

CREATE INDEX ix_sub_customer_valid
  ON subscription_periods (customer_id, valid_from, valid_to);
```

Example rows:

```
customer_id │ plan       │ cycle    │ status │ valid_from           │ valid_to
1001        │ basic      │ monthly  │ active │ 2024-08-15 10:00:00  │ 2025-01-12 14:30:00
1001        │ pro        │ monthly  │ active │ 2025-01-12 14:30:00  │ 2025-04-01 09:00:00
1001        │ pro        │ yearly   │ active │ 2025-04-01 09:00:00  │ 2025-05-10 11:00:00
1001        │ pro        │ yearly   │ paused │ 2025-05-10 11:00:00  │ 2025-05-22 09:30:00
1001        │ pro        │ yearly   │ active │ 2025-05-22 09:30:00  │ 9999-12-31 00:00:00
```

You can read this row by row and understand the customer's life: started on basic, upgraded to pro, switched to yearly billing, paused for 12 days, resumed.

### How events update the table

Pseudocode for a plan change:

```python
def change_plan(customer_id, new_plan_id, billing_cycle, when, who):
    with transaction:
        # Close the current period
        current = sql("""
          UPDATE subscription_periods
          SET valid_to = :when
          WHERE customer_id = :customer_id
            AND valid_to = '9999-12-31'
          RETURNING *
        """, when=when, customer_id=customer_id)

        # Open a new one starting at the same instant
        insert(
          subscription_periods,
          customer_id=customer_id,
          plan_id=new_plan_id,
          billing_cycle=billing_cycle,
          status='active',
          valid_from=when,
          valid_to='9999-12-31',
          created_by=who,
        )
```

The two writes happen in one transaction. The intervals are half-open: `valid_from` inclusive, `valid_to` exclusive. The new period starts at the exact instant the old one ends. No gaps, no overlaps.

Pause and resume are the same shape, just with a `status` change instead of a `plan_id` change.

### The three classic queries

**"What plan is this customer on right now?"**

```sql
SELECT *
FROM subscription_periods
WHERE customer_id = :id
  AND valid_to = '9999-12-31';
```

Or equivalently, `WHERE NOW() >= valid_from AND NOW() < valid_to`.

**"What plan was this customer on on a specific date?"**

```sql
SELECT *
FROM subscription_periods
WHERE customer_id = :id
  AND :date >= valid_from
  AND :date <  valid_to;
```

This is the as-of join from Problem 10. It answers the billing dispute in seconds.

**"List every change this customer made."**

```sql
SELECT *
FROM subscription_periods
WHERE customer_id = :id
ORDER BY valid_from;
```

Customer support reads this top-to-bottom. The whole history is right there.

### Joining to bills

A monthly bill for May covers a window of dates. The customer may have been on different plans in different parts of the month. The bill builds itself from this table:

```sql
SELECT
  p.plan_id,
  p.billing_cycle,
  GREATEST(p.valid_from, :period_start) AS effective_start,
  LEAST(p.valid_to, :period_end)        AS effective_end
FROM subscription_periods p
WHERE p.customer_id = :id
  AND p.valid_to    > :period_start
  AND p.valid_from  < :period_end;
```

This returns one row per plan-segment within the billing window. Each segment gets its own line on the bill ("Pro plan May 1-9: $X. Paused May 10-21: $0. Pro plan May 22-31: $Y"). This is exactly how the smart meter bill in Problem 25 handled tariffs.

### What goes in here vs in an audit table

This table is **what was true when**. It is the source of truth for billing and reporting.

An audit log table is separate. It records **who did what**:

```
audit_events
─────────────────────────────────────
event_id, customer_id, action_type, actor (user or system),
before_state, after_state, occurred_at
```

The two tables answer different questions. The periods table answers "what was the plan." The audit table answers "who changed it." For disputes you usually want both.

### Pause and resume

Two ways to model:

**Option A: status column.** A row with `status = 'paused'` indicates the customer was paused during that period. Pricing logic treats paused periods as $0. The schema does not need new tables.

**Option B: separate "active vs paused" intervals.** More normalized: one table tracks plan, another tracks paused/active. More complex to join.

I prefer Option A. It is simple and it composes well with billing logic.

### Trade-offs vs an event-only table

Some teams only store events:

```
events_only
─────────────────────────────────────
event_id, customer_id, action ('upgraded', 'downgraded', 'paused'),
new_plan_id, occurred_at
```

To answer "what plan was the customer on on May 10," you replay events from the start. This is correct but slow. For frequent dispute lookups, recomputing the state is wasteful.

The period table is the **materialized** form of the same information. It is precomputed, indexed, and fast. Best practice: keep both. Events drive updates to periods. Periods are the read model.

### Common mistakes interviewers want you to name

1. **Overlapping intervals.** Two rows both claim to cover the same instant. Bug somewhere in the update logic. Add a constraint or a check.
2. **Using `NULL` for `valid_to` on the current row.** Then "as-of date" queries need `COALESCE`. `9999-12-31` is simpler.
3. **Closing the old row but not opening a new one.** Customer has a gap; their plan looks "deleted" for an instant. The transaction must do both.
4. **Updating the period table in place without history.** Then a dispute six months later cannot be answered.
5. **Storing the period in the user row** (`plan_id`, `plan_started_at`). The history is gone.

### Bonus follow-up the interviewer might throw

> *"How do you avoid race conditions when two plan changes hit at the same time?"*

Two protections:

1. The whole "close old + open new" runs in a single transaction with a row lock on the customer's current period.
2. A unique constraint that ensures at most one row per customer has `valid_to = '9999-12-31'`. The second concurrent insert fails, the application retries.

Together these guarantee a consistent timeline even with simultaneous writes.
