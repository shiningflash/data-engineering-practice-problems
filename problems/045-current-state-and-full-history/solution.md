## Solution 45: Current State and Full History

### Short version you can say out loud

> Keep one source of truth: the events table. Derive the current state as a view or a small materialized view on top. You never duplicate the data, you just have one base and one derived. Storage is not doubled. The events table is the history; the view is the latest snapshot. If the view is too slow to compute on the fly, materialize it, but the materialization is much smaller than the events table, so storage cost is barely affected.

### The shape

```
fact_order_events
─────────────────────────────────────────
event_id (PK)
order_id
event_type     ('created', 'paid', 'shipped', 'cancelled', 'refunded', ...)
event_payload  (JSON: amount, address, etc.)
actor          (user_id or system)
occurred_at
ingested_at

Indexes / clustering:
  (order_id, occurred_at DESC)   ← fast "last event per order"
  (event_type, occurred_at)      ← time-based queries
```

This is the only table that holds raw data. Every state change of an order produces one row.

Then a view:

```sql
CREATE OR REPLACE VIEW v_order_current_state AS
SELECT *
FROM (
  SELECT
    order_id,
    event_type,
    event_payload,
    occurred_at,
    ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY occurred_at DESC) AS rn
  FROM fact_order_events
)
WHERE rn = 1;
```

Or, depending on the engine, a `QUALIFY` clause:

```sql
SELECT *
FROM fact_order_events
QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY occurred_at DESC) = 1;
```

`v_order_current_state` has one row per order: the latest known state.

Both "current state" and "full history" come from one source. No duplication.

### How big is each side

* `fact_order_events`: many events per order. For an order with 6 state changes, 6 rows. Storage is real.
* `v_order_current_state`: as a view, no storage. As a materialized table, one row per order. Much smaller than the events table.

So even when you materialize the "current state," storage is not doubled. The materialized snapshot is a fraction of the event log size.

### The query patterns

**"What is the current state of order 5001?"**

```sql
SELECT * FROM v_order_current_state WHERE order_id = 5001;
```

One row. Fast.

**"Show me the full history of order 5001."**

```sql
SELECT *
FROM fact_order_events
WHERE order_id = 5001
ORDER BY occurred_at;
```

All rows. Fast with the right clustering or index.

**"How many orders are in 'shipped' state today?"**

```sql
SELECT COUNT(*)
FROM v_order_current_state
WHERE event_type = 'shipped';
```

Fast. Once.

**"How long does it take orders to go from 'paid' to 'shipped' on average?"**

```sql
WITH paid AS (
  SELECT order_id, occurred_at AS paid_at FROM fact_order_events WHERE event_type = 'paid'
),
shipped AS (
  SELECT order_id, occurred_at AS shipped_at FROM fact_order_events WHERE event_type = 'shipped'
)
SELECT AVG(EXTRACT(EPOCH FROM (s.shipped_at - p.paid_at)) / 3600.0) AS hours_to_ship
FROM paid p
JOIN shipped s USING (order_id);
```

This needs the history, not the current state. The events table is the only place that has it.

### When the view is too slow

For a small table (millions of rows), the view is fast. For a huge table (billions), the `ROW_NUMBER` over the whole thing can be slow on cold cache.

Two ways to speed it up:

**1. Materialize.**

```sql
CREATE MATERIALIZED VIEW mv_order_current_state AS
SELECT ...
```

Refreshed every N minutes, or on demand. Rows are pre-computed.

**2. Maintain an incremental snapshot table.**

A separate table `dim_order_current_state` updated by a small pipeline. When a new event arrives, MERGE into this table:

```sql
MERGE INTO dim_order_current_state AS dst
USING (
  SELECT * FROM fact_order_events
  WHERE event_id = :new_event_id
) AS src
ON dst.order_id = src.order_id
WHEN MATCHED THEN UPDATE SET
  event_type = src.event_type,
  event_payload = src.event_payload,
  occurred_at = src.occurred_at
WHEN NOT MATCHED THEN INSERT VALUES (...);
```

`dim_order_current_state` is much smaller than `fact_order_events`. Storage is barely affected.

### The team's worry: "querying the events table is too slow"

This is the team's real concern. The answer:

* For point lookups by `order_id`, with clustering on `(order_id, occurred_at)`, the events table is fast even at billion rows.
* For aggregates ("how many orders are shipped"), the materialized current-state table is the right answer.
* For history-aware queries ("time from paid to shipped"), nothing beats the events table.

So the right setup is: events as base + a thin current-state materialized table. Both serve their queries fast.

### When you might really need two physical tables

Three real cases:

1. **Different consumers, very different access patterns.** A customer-facing API reads `current_state` thousands of times per second; the warehouse reads events in batch. The API gets its own table, optimized for point reads, possibly in a different store entirely (Postgres, DynamoDB).
2. **Compliance retention differences.** Events kept for 7 years (audit); current state kept indefinitely. Same data, different lifecycles.
3. **The current state has computed fields** that are expensive to recompute (a status that depends on rules, not just the last event). Worth materializing.

In all three, the rule is: events are still the source of truth, and the second table is derived.

### What I would NOT do

* **Build current state as a primary table** and bolt on events as an afterthought. The team usually starts here and regrets it.
* **Update current state in place without writing an event.** Audit gap.
* **Keep "old current state" history by overwriting the same row.** Lose the history. Cannot recover.

### Common mistakes interviewers want you to name

1. **Duplicating data instead of deriving.** "Two tables that should always agree" never do.
2. **Computing current state from events with no clustering.** Slow at scale.
3. **Forgetting that events are append-only.** Updating event rows breaks audit.
4. **No event types beyond "updated."** Then you do not know what changed; only that something did. Use specific types.
5. **Storing the whole new state in every event.** Storage explodes. Store either the delta or just enough to reconstruct.

### Bonus follow-up the interviewer might throw

> *"This looks a lot like event sourcing. Are you proposing event sourcing for the warehouse?"*

It is event-sourced thinking, applied to data modeling, yes. The principle is the same: the events are the truth, the current state is a projection. The difference is that we are not running our application off the event log; we are running our analytics on top of it. That makes the trade-offs gentler. No need for event-by-event replay; we just SELECT.

For domains where the audit story matters (finance, billing, healthcare, energy markets), this pattern is almost always worth the small extra effort.
