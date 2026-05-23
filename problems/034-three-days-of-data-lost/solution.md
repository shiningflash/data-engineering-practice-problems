## Solution 34: Three Days of Data Lost

### Short version you can say out loud

> First I fix the config so today's data is safe. Then I find out which producers still have the original events and replay from them, idempotently. Anything that only lived in Kafka and aged out is permanently gone; I write that down honestly. After recovery, the real change is structural: a retention floor that can't be lowered below the consumer lag SLA, plus monitoring on consumer lag versus retention.

### Hour 1: stop the bleeding

The first thing I do isn't investigate. It's stop today's events from also being lost.

1. Restore the retention setting on the Kafka topic to its proper value (7 days, or whatever the standard is).
2. Catch up the consumer group that fell behind. If it's still running but lagged, scale it up or unblock it.
3. Page the right people. Producer team owners, data team lead, on-call.

While that's happening, I post in the incident channel:

> "Incident: kafka topic `app_events` had retention misconfigured (1h instead of 7d). Consumer lag caused 3 days of events to age out before being landed. Retention has been restored. Investigating recovery options now. Will update at the top of every hour."

### Hour 2: scope the loss

For each topic involved, I want three numbers:

1. First and last lost event time. Exactly the window we're recovering.
2. Approximate count of lost events. From producer logs or upstream metrics.
3. Downstream tables that depend on this. Which marts, which dashboards, which models.

```sql
-- in the warehouse, where the consumer would have landed events
SELECT MIN(event_time) AS first_ok, MAX(event_time) AS last_ok
FROM raw.app_events
WHERE event_time > NOW() - INTERVAL 10 DAYS;
```

The gap between the producer-side timeline and the warehouse-side timeline is the lost window.

### Hour 3: recovery options, source by source

Now the recovery thinking. For each producer that fed the lost topic, ask: does the source system still have the originals?

Three possible answers per producer.

1. Yes, still in the OLTP / source database.

Replay from there. CDC can usually be rewound to a starting point in time. Or a one-off SQL extract can produce the same events with the same shape. Land them into the lost window, idempotently.

```sql
INSERT INTO raw.app_events
SELECT
  event_id,
  user_id,
  event_type,
  event_time,
  payload
FROM source.events
WHERE event_time BETWEEN @lost_start AND @lost_end;
```

Because rows have an `event_id`, we can dedupe naturally on insert (MERGE / upsert). Idempotent. If we accidentally replay events that did make it into the warehouse, no harm done.

2. Producer kept an outgoing log.

Some teams write the same event to both Kafka and a local file or DynamoDB stream "for audit." Check. If found, replay from the audit.

3. Producer kept nothing. The event was emit-and-forget.

This is the part that's gone. There's nothing to recover. Tell people. Don't paper over it.

### Idempotent replay

The replay is a backfill of the lost window. The pattern from Problem 9:

* Treat the window as a partition.
* Delete what's in that window in the destination (any partial events that did sneak through), then re-insert.
* Or, if every event has a stable `event_id`, MERGE on the id.

```sql
MERGE INTO raw.app_events AS dst
USING staging.replayed AS src
ON dst.event_id = src.event_id
WHEN NOT MATCHED THEN INSERT (event_id, ...)
WHEN MATCHED THEN UPDATE SET ...;
```

Once raw is restored, every downstream model is rebuilt for that window. Because every model is partition-keyed and idempotent, this is mechanical.

### What is permanently gone

Be honest about this in the incident channel and the postmortem. Examples of unrecoverable categories:

* Client-side events sent only to Kafka without a server-side mirror. Browser pings, app analytics events that never went through a server log.
* Third-party webhook events if the third party doesn't allow replay.
* Derived events computed in the stream itself and not stored anywhere upstream.

Quantify the loss. "We lost approximately 1.2 million events out of 38 million for the window, all client-side analytics. They're not recoverable. Server-side events (checkout, payments) are fully recovered."

### The communication thread

The incident channel gets four updates that day:

1. Initial post: "incident, retention misconfig, investigating."
2. After scoping: "lost window is X to Y, downstream tables affected: A, B, C."
3. After recovery plan: "recovering from sources for 95% of events. Client-side telemetry is unrecoverable."
4. After recovery: "raw is rebuilt, marts being rebuilt now, ETA tomorrow morning. Final loss estimate: about 5% of telemetry events, no impact on financial data."

Stakeholders get a separate, shorter version aimed at their concerns. Finance only cares about "do our money numbers move?" If not, that's the message they need.

### The postmortem, after the dust settles

A blameless postmortem within a week. Honest about what went wrong.

Timeline. Exactly when each event happened.

What went well. Recovery started within an hour. Most data was recovered. Comms were clear.

What went badly.

* The retention change shipped without review specific to data-team consumers.
* Consumer lag was silently growing for a day before retention expired.
* No alert fired when retention was set below the lag SLA.
* The list of "downstream owners of this topic" didn't exist; nobody knew who to page.

Action items. Each one assigned to a person with a date.

* Add a Kafka admission control: can't set retention below `max(consumer_lag * 2)` for any consumer group on the topic.
* Alert: consumer lag exceeds 50% of retention. Pages the data team.
* Alert: producer-side event rate vs warehouse-side landing rate divergence. Pages the data team.
* Topic owners are recorded in a registry; deploy reviews include checking "does this topic have warehouse consumers."
* Critical client-side events get a server-side mirror.

### The bigger lesson

The technical fix is easy. The harder lesson is that a deploy in one part of the system can silently destroy data in another. This calls for:

* Data contracts that include retention requirements.
* Cross-team review for changes to topics that have data-team consumers.
* A defense-in-depth mindset that doesn't rely on any one team to do the right thing.

If I had to pick one change, it would be the retention floor: just make it impossible to lower retention below the SLA. That removes the failure class permanently.

### Common mistakes interviewers want you to name

1. Investigating before fixing the config. Today is still leaking.
2. Trying to recover from Kafka after retention has expired. The data is gone.
3. No quantification of the loss. Saying "some data was lost" is unactionable.
4. Blaming the engineer who shipped the deploy. The system allowed it.
5. No structural change. "We will be more careful" never works.

### Bonus follow-up the interviewer might throw

> *"What if the lost data drives a financial number that has already been published?"*

That's a regulatory and legal event, not just an engineering one. Bring in legal and the finance lead immediately. The technical recovery is the same. The harder part is the disclosure: the published number was wrong by X%. Whether it's material enough to restate depends on the jurisdiction and the size. Don't make that call alone.
