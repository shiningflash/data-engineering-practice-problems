## Solution 22: Banking App Monthly Spending Widget

### What "instant" means

"Instant" on a phone means the widget renders in under 200 ms after the screen opens. The data fetch itself has maybe 80-100 ms of that budget after we account for TLS, app rendering, and the rest. So the backend has to answer in roughly 50 ms at p95.

That number drives every design choice. A warehouse query takes seconds. A relational database can do it. A key-value store does it easily. So we are not going to query the warehouse from the phone, ever. We are going to maintain a small pre-computed answer in a fast store.

### The shape of the system

```
   Card swipe / digital payment
              │
              ▼
   ┌──────────────────────┐
   │   Core banking       │   (source of truth, OLTP, Postgres or
   │   transactions DB    │    a mainframe-equivalent)
   └─────────┬────────────┘
             │ CDC (Debezium / Striim)
             ▼
   ┌──────────────────────┐
   │   Kafka topic        │
   │   "transactions"     │
   └─────────┬────────────┘
             │
             ▼
   ┌─────────────────────────────┐
   │  Stream processor (Flink /  │
   │  Kafka Streams)             │
   │                             │
   │  - look up category for     │
   │    merchant_id              │
   │  - apply +/-  (refund vs    │
   │    purchase)                │
   │  - keyed by (user, month,   │
   │    category)                │
   │  - emit updated totals      │
   └────────────┬────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │  Fast serving store         │
   │  (DynamoDB / Bigtable /     │
   │  Redis / Aerospike)         │
   │                             │
   │  Key: user_id|YYYY-MM       │
   │  Value: { category -> sum,  │
   │           total, updated_at}│
   └────────────┬────────────────┘
                │
                │ <50 ms point read
                ▼
   ┌──────────────────────┐
   │   Mobile app widget  │
   └──────────────────────┘

                  (in parallel, for analytics / dispute / reporting)
                ┌─────────────────────────────────┐
                │  Same Kafka topic also drains   │
                │  to S3 → Warehouse (BigQuery /  │
                │  Snowflake) for non realtime    │
                │  use cases                      │
                └─────────────────────────────────┘
```

### Data shape in the serving store

```
Key:    user_id | YYYY-MM
Value:  {
  total:      4321.50,
  categories: {
    groceries: 850.20,
    transport: 130.00,
    dining:    295.75,
    bills:    1820.00,
    other:    1225.55
  },
  txn_count:    78,
  updated_at:   "2025-05-14T08:21:12Z",
  last_seq:     991283
}
```

One record per user per month. Reading it is a single point lookup. ~5 KB per user. 5 million users × 12 months would be a few hundred GB at most. Cheap.

### How a transaction flows

1. Customer pays at a merchant. The core banking system writes the transaction row. This is the moment of truth.
2. CDC (Debezium reading the Postgres WAL, or its mainframe equivalent) emits the row to Kafka within a second or two.
3. A stream processor reads the Kafka topic. For each transaction:
 * Look up the merchant category from a small in-memory map (categories rarely change, refreshed every hour).
 * Compute the signed amount: positive for purchases, negative for refunds.
 * Update the (user, year-month, category) total.
4. The new total is written to the fast serving store.
5. Next time the user opens the app, the widget reads the row in one call.

End to end latency from swipe to widget refresh: typically 2-5 seconds. The user does not see latency because they were not staring at the app at the moment of swipe.

### The merchant-to-category problem

The biggest soft problem in this pipeline. A swipe at "TESCO SG #421" should become "groceries." A swipe at "GRAB *XR23F" should become "transport." This mapping is messy and changes over time.

How I would handle it:

* **A `merchant_categories` table** keyed by merchant id, maintained by a small team. Loaded into the stream processor as a broadcast state, refreshed hourly.
* **A fallback rule engine** for unknown merchants: pattern match on the descriptor string ("UBER" → transport, "STARBUCKS" → dining).
* **An "other" bucket** for genuinely unmapped transactions. The widget shows them but they get reviewed weekly.

When a category changes (the mapping is fixed), I would NOT retroactively change past months. The widget shows what was said at the time. Otherwise the user sees their March number change in May, which feels wrong.

### Handling refunds and corrections

Refunds are just negative transactions. The stream processor adds them and the totals go down. Important: if the original purchase happened in April and the refund happens in May, which month does the refund belong to?

Two conventions, pick one:

* **Banking convention (post date):** the refund hits whatever month it cleared in. So the May refund reduces the May total.
* **Spending convention (transaction date):** the refund reduces the month the original purchase was in. So the May refund reduces the April total retroactively.

Banks usually go with post date, because that's how the statement reads. The widget should match the statement.

### Cold start and the first-of-the-month problem

On the first of the month, every user has a fresh empty record. The very first read after midnight needs to materialize the empty row. Two ways:

1. **Lazy:** the widget service checks the store, finds nothing, returns zeros, and the row gets created on the first transaction. Simple but produces a brief "your spending: 0" until the first txn arrives, which is correct anyway.
2. **Eager:** a scheduled job at midnight of the user's local time zone creates an empty record. Slightly nicer UX but more code.

Lazy is fine for a v1.

### Idempotency

CDC can deliver the same transaction twice (Kafka retries, processor restarts). The stream processor must dedupe by `transaction_id`. Two patterns:

* Keep the last `last_seq` processed in the same record. Skip anything ≤ that.
* Use Flink exactly-once with checkpointing.

Either way, the rule is: applying the same transaction twice produces the same total once. This is the same idempotency rule from Problem 9, just inside a streaming processor.

### Why not query the warehouse directly?

* Warehouse query latency is seconds, not milliseconds.
* Warehouse is not built for thousands of concurrent point reads.
* Cost scales with reads. Each widget render would cost real money at 5 million daily active users.

The warehouse is still part of the picture, but for analytics, disputes, and historical reports, not for the live widget.

### What the warehouse layer does

The same Kafka topic drains to S3 (Firehose) and then to BigQuery or Snowflake. The warehouse hosts:

* Full transaction history (years).
* Analytics: "average spend per customer per category."
* Risk and fraud models.
* Customer support: "show me this user's full statement."

The widget never touches it.

### Common mistakes interviewers want you to name

1. **Pointing the widget at the warehouse.** Lots of teams try this. Latency, cost, and concurrency all bite.
2. **Recomputing the monthly total on every read** ("aggregate the last 30 days from a transactions cache"). Even on a fast store, this is expensive at the first-of-month-just-after-payday spike.
3. **Forgetting to dedupe.** CDC retries are normal. A doubled total is a customer complaint.
4. **Mapping changes that rewrite history.** Surprising the user is worse than a bad mapping.
5. **No fallback for when the serving store is down.** If the widget is critical, fall back to a stale cached number, not a spinner forever.

### Bonus follow-up the interviewer might throw

> *"How would you make this work offline, when the phone has no network?"*

Cache the last successful response on the phone with a short TTL (an hour). Show it with a small "as of 8:21" timestamp. The user sees their last known number instead of an error, and the freshness label is honest. When the phone reconnects, refresh in the background.
