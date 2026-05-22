## Solution 14: Exactly Once Delivery

### Short version you can say out loud

> Three delivery guarantees exist: at most once (might lose messages, never duplicate), at least once (never lose, might duplicate), and exactly once (never lose, never duplicate). At least once is what real networks naturally give you. Exactly once is hard because the only way to guarantee no loss is to retry on uncertainty, and retrying creates duplicates. The practical fix is to make the consumer idempotent, so duplicates from the wire stop mattering. When people say "exactly once," they usually mean "at least once delivery plus an idempotent consumer." Kafka's exactly once semantics covers Kafka to Kafka, but does not magically extend to your database or third party API.

### Picture the three modes

```
                Producer ────▶ Broker ────▶ Consumer

At most once    │ Fire and forget. If the message is lost in the wire, it is gone.
                │ Used for telemetry where losing a tiny percent is fine.

At least once   │ The producer retries until it sees an ack. The broker retries
                │ delivery until the consumer commits. Result: never lost,
                │ but can be delivered more than once. Default for Kafka.

Exactly once    │ Each message effects the consumer exactly one time.
                │ Hard, because retries are the only safe way to avoid loss,
                │ and retries cause duplicates. So "exactly once" really means
                │ "duplicate-aware consumer."
```

### Why it is hard

Networks fail in a specific way: when you call "did the other side receive my message?", you can get three answers — yes, no, or *I don't know*. The "I don't know" case is the whole problem. If the producer sent a message and never got an ack, two things could have happened:

1. The broker never received it.
2. The broker received it, but the ack got lost.

The producer cannot tell the difference. So it retries. If case 2 was the real one, the broker now has the message twice.

The same thing happens between broker and consumer: the consumer processes the message, then has to commit "I am done with it." If the commit ack is lost, the consumer (after a restart) re-reads the same message and processes it again.

You cannot have both "never lose" and "never duplicate" with only network calls. You have to add something else.

### The trick: idempotent consumers

If your consumer can recognize a duplicate and ignore it, you do not need exactly-once delivery from the broker. You only need at-least-once delivery, plus a consumer that does not care when it sees a duplicate.

The most common patterns:

**1. Idempotency key**
Every message carries a unique id. The consumer keeps a small store of "ids I have already processed" (a database table, Redis, a Bloom filter for big scale). Before doing the work, it checks. If already done, skip.

```python
def handle(msg):
    if seen.exists(msg.id):
        return                # duplicate, ignore
    do_the_work(msg)
    seen.insert(msg.id)       # remember it
```

The catch is the order: if you do the work first and crash before recording the id, you have done the work twice. If you record the id first and crash before doing the work, you have lost the message. The fix is to put both into a single transaction. Which leads to the next pattern.

**2. Transactional outbox / transactional consumer**
The consumer wraps both the work and the "seen" record in one database transaction. Either both commit, or neither does. If the transaction is in your application database, you can do this with normal SQL transactions.

```sql
BEGIN;
INSERT INTO payments (id, amount) VALUES (...);
INSERT INTO processed_ids (id) VALUES (...);
COMMIT;
```

Now there is no window where the work happened but the id was not recorded.

**3. Stateful processing with checkpointed state (Flink-style)**
A stream processor like Flink or Beam keeps a snapshot of its state. When it commits to Kafka, it commits its state snapshot at the same time, using a two-phase commit. On restart, it resumes from the last snapshot, so retried messages do not double-count. This is the cleanest version of "real" exactly once, but it only works when both ends speak the protocol (Kafka <-> Flink <-> Kafka).

### Kafka exactly once: what it actually covers

Kafka's "Exactly Once Semantics" (EOS) does three things:

1. The producer dedupes its own retries using a sequence number, so the broker stores each message once per partition.
2. Transactional writes let a producer write to multiple partitions atomically.
3. Read-process-write loops inside Kafka can commit consumer offsets and produced messages in one transaction.

What it does NOT cover:

* Writing to your **Postgres** or your **payment gateway**. Those are outside the Kafka transaction.
* Effects in any external system, including sending an email or invoking an API.

So the payments engineer in the scenario was technically right that Kafka delivered exactly once, but the consumer charged the customer via Stripe, which is outside Kafka. The retry happened at the Stripe call level after a timeout, and Stripe saw two charge requests with no idempotency key.

### The whole picture

```
End-to-end exactly once = at-least-once delivery + idempotent end side

Even with Kafka EOS, the moment you write to anything outside Kafka,
you are back to needing idempotency in that external write.
```

### Common mistakes interviewers want you to name

1. **Believing exactly once is a property of the transport.** It is really a property of the whole loop, including the consumer's side effects.
2. **No idempotency key on external API calls.** This is the Stripe-charged-twice bug.
3. **Recording "I am done" outside the transaction with the work.** Crash window.
4. **Using a small in-memory dedup set** that resets on restart. Duplicates that arrive after the restart slip through.
5. **Assuming Kafka EOS makes the database consistent.** It does not. The database is not in the Kafka transaction.

### Bonus follow-up the interviewer might throw

> *"How do you size the deduplication store? You cannot keep every id forever."*

You usually only need to dedupe within a window: the maximum time a duplicate could plausibly arrive. For Kafka with normal retry policies, that is minutes, not hours. So a TTL of a few hours on the dedup store is enough in practice, and you do not need infinite storage. If your idempotency key is content-based (a hash of the payload), you do not even need to keep ids: the same payload always produces the same key.
