## Solution 57: Kafka Ordering Guarantee

### Short version you can say out loud

> Kafka guarantees ordering only within a single partition. Across the whole topic, messages can interleave any way. So the question becomes "do all messages that need to be ordered land in the same partition?" That depends on the partition key. If two related events use different keys, they can land in different partitions and arrive out of order downstream. Even within a partition, producer retries without idempotence and topic resharding can reorder things. Most "Kafka is reordering my data" cases are really "my partition key is wrong."

### The exact guarantee

> "Within a single partition of a single topic, messages are stored in the order they were written, and consumers see them in that order."

That's the entire promise. Notice what is NOT promised:

* Order across partitions.
* Order across producers.
* Order after compaction.
* Order after a topic reshuffle.

### Why ordering happens to be partitioned

Kafka scales by splitting a topic into partitions, each handled by a different broker. If Kafka tried to guarantee global ordering, it could only have one partition, and one broker, and one consumer at a time. The whole reason it scales is that partitions are independent.

So ordering is the price of scalability. If you need ordering for a set of messages, those messages must land in one partition.

### How to make messages land in the same partition

The producer specifies a **partition key**. Kafka hashes the key and assigns to a partition deterministically. Messages with the same key always go to the same partition.

```python
producer.send(
  topic='orders',
  key=str(order_id).encode(),     # ← partition key
  value=event_payload,
)
```

If you key by `order_id`, all events for the same order land in the same partition and stay ordered. Different orders may interleave across partitions, which is fine because they are independent.

The wrong move:

* No key: Kafka picks a partition round-robin. Same-order events can land anywhere.
* Wrong key: keying by something that varies (`timestamp`, `random_id`) puts related events in different partitions.

The most common bug: keying by `user_id` when the relevant ordering is by `order_id`. Two events for the same order go to different partitions because they happened to have different user-relevant fields.

### What can quietly break ordering within a partition

Even when you key correctly, ordering can still go wrong:

**1. Producer retries without idempotence.**

If the producer sends message A, times out, retries, then sends message B, you can end up with B-A-A in the partition. Enable idempotent producer (Kafka >= 0.11):

```
enable.idempotence = true
acks = all
```

With idempotence on, Kafka deduplicates retries and preserves order. This is on by default in recent versions.

**2. `max.in.flight.requests.per.connection > 1` without idempotence.**

The producer sends multiple batches in parallel. If batch 1 fails and is retried, batch 2 lands first. Idempotence fixes this; without it, lower this to 1.

**3. Multiple producers writing to the same partition.**

Each producer's messages are ordered, but Kafka does not order across producers in the same partition. If two services produce events for the same order from different machines, the order in the partition is "first to arrive at the broker." Usually fine, sometimes not.

**4. Topic reshuffling (partition count changes).**

If you increase the number of partitions, the hash mapping changes. New messages with the same key may now land in a different partition. Old messages stay where they were. Consumers see "old key X messages in partition 3, new key X messages in partition 7." Ordering across that boundary is gone.

This is the biggest gotcha. Once you've keyed for ordering, do not change partition counts.

**5. Compacted topics.**

A compacted topic keeps only the latest message per key. Older messages disappear. Ordering of the surviving messages is preserved, but you no longer see the full history.

**6. Consumer reprocessing.**

If a consumer resets and re-reads from an earlier offset, it sees the same messages again in order — but downstream side effects (database writes) may already exist from the first pass. Order is preserved on the wire; the downstream effect order depends on idempotency.

### When you need global ordering

If you truly need global ordering — every event in the topic seen in one true order:

* Use a single-partition topic. Throughput is bounded by one broker.
* Or, route through a sequencer (a single service that assigns monotonic ids before producing).

This is rare. Most "I need ordering" actually means "I need ordering per-entity," which the right key fixes.

### Production checklist when ordering matters

1. **Key by the entity that needs ordering** (`order_id`, `user_id`, `meter_id`, whatever the unit is).
2. **Enable idempotent producer.** Default in recent Kafka.
3. **`acks=all`** so retries don't lose messages.
4. **Document the partition key** in your data contract.
5. **Never change partition count** once keyed for ordering. If you must, create a new topic and migrate.
6. **Build idempotent consumers anyway**, because of dedup needs (Problem 14).

### A diagnostic for the scenario

The teammate is sure Kafka is innocent. To diagnose:

```sql
-- in your warehouse, after landing
SELECT event_id, event_time, ingest_time, partition
FROM raw.events
WHERE entity_id = '12345'
ORDER BY ingest_time
LIMIT 50;
```

Look at:

* Are messages from the same entity in different partitions? If yes, partition key is wrong.
* Are messages within one partition out of event-time order? Late delivery, not partition reorder. Check producer settings.
* Did the topic's partition count change recently? That is the boundary effect.

The answer is almost always in the first or third bullet.

### Common mistakes interviewers want you to name

1. **"Kafka guarantees ordering."** Without "per partition" it is wrong.
2. **No partition key.** Round-robin scatters related events.
3. **Wrong partition key.** Order is preserved per the wrong entity.
4. **Increasing partition count** breaks key-based ordering.
5. **Trusting wire ordering** without idempotent consumers. Retries reorder downstream effects.

### Bonus follow-up the interviewer might throw

> *"What if you want both high throughput AND strict ordering across the whole topic?"*

You can't, fundamentally. But you can simulate:

* Use a single-partition topic for the messages that need strict order, and a separate high-throughput topic for everything else.
* Use a "router" service that sequences events through a single point and emits to many partitions with a global sequence number, then a consumer re-sorts using the sequence number.

Both are operational complexity. Usually the right answer is to design the workflow so global ordering is not required, and per-entity ordering (via key) is enough.
