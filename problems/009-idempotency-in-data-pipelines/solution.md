## Solution 9: Idempotency in Data Pipelines

### Short version you can say out loud

> Idempotent means you can run the same job twice and the result is the same as running it once. In a data pipeline, this matters because retries are normal. Network blips, crashed workers, slow APIs, all of those cause a step to run again. If the pipeline is not idempotent, retrying it corrupts your data. Interviewers ask about this because production systems retry constantly, and any pipeline that cannot survive a retry will eventually produce a doubled or missing number.

### The story above, drawn out

```
Non idempotent (the bug)
─────────────────────────
Run 1:   INSERT INTO orders SELECT * FROM source WHERE date = '2025-05-14';
         ✗ Crashes halfway through.
Retry:   INSERT INTO orders SELECT * FROM source WHERE date = '2025-05-14';
         ✓ Success. But the first INSERT had already written rows.
Result:  Some rows appear twice. Yesterday's revenue is doubled.

Idempotent (the fix)
────────────────────
Run 1:   DELETE FROM orders WHERE date = '2025-05-14';
         INSERT INTO orders SELECT * FROM source WHERE date = '2025-05-14';
         ✗ Crashes halfway through.
Retry:   DELETE FROM orders WHERE date = '2025-05-14';
         INSERT INTO orders SELECT * FROM source WHERE date = '2025-05-14';
         ✓ Success. The DELETE wipes anything from the bad run.
Result:  Exactly one set of rows for that date, every time.
```

### What "idempotent" means in this context

If `f(x)` is your pipeline step and you run it once, you get a certain state in the warehouse. If you then run it again with the same input, the warehouse state should be unchanged. `f(f(x)) == f(x)`. That is the whole definition.

The key part is the end state, not the side effects along the way. The second run can do work (queries, writes), but the data that lands in the destination is the same as if it had only run once.

### Three patterns that make a step idempotent

**1. MERGE / UPSERT by a stable key**

Every row has a stable primary key. Instead of `INSERT`, you `MERGE` (or `INSERT... ON CONFLICT UPDATE`):

```sql
MERGE INTO orders AS target
USING staging AS source
ON target.order_id = source.order_id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT (...);
```

Running this twice does not duplicate rows. The second run finds the same keys and updates in place. Works in BigQuery, Snowflake, Postgres, most warehouses.

**2. Delete and reinsert by partition**

For partitioned tables, treat the partition as the unit of work:

```sql
DELETE FROM orders WHERE event_date = @target_date;
INSERT INTO orders
SELECT * FROM source WHERE event_date = @target_date;
```

The job "owns" that day. Whatever was there from a previous attempt is wiped first. Safe to retry as many times as you want. This is the most common pattern in daily batch pipelines.

In BigQuery I usually do it cleaner with a partition replace:

```sql
CREATE OR REPLACE TABLE orders$20250514 AS
SELECT * FROM source WHERE event_date = '2025-05-14';
```

**3. Idempotency key**

Common in streaming and API style pipelines. Every event carries a unique id (`event_id`, `message_id`, or a hash of its content). On insert, you skip rows where the id already exists.

```sql
INSERT INTO events (event_id, ...)
SELECT event_id, ...
FROM staging s
WHERE NOT EXISTS (
  SELECT 1 FROM events e WHERE e.event_id = s.event_id
);
```

Or with a unique constraint, you let the database reject the duplicate.

### A less obvious pattern: idempotent file writes

Writing to S3 or GCS feels safe, but it is easy to get wrong. If your job appends a file with a timestamp name and crashes between writing the file and committing the metadata, a retry creates a second file. Two patterns fix this:

* Deterministic file names. `orders/date=2025-05-14/part-001.parquet`. A retry overwrites the same file.
* Manifest files. Write all data files first, then write a tiny `_SUCCESS` or `manifest.json` last. Downstream readers ignore everything not in the manifest. A crashed run leaves orphan files that a cleanup step removes later.

### Side effects that quietly are NOT idempotent

These are the ones that bite you in real life:

* Sending notifications or emails. A retried job that sends "your bill is ready" can send it three times.
* Calling third party APIs that have their own state. A retried Stripe charge can charge the customer twice.
* Auto incrementing surrogate keys. A retry may produce a row with a new key, so the "same row" looks different.
* Appending to a CSV. If your job does `>>` append instead of write-then-rename, retries grow the file.

For these, you usually need an idempotency key passed to the external system, or a "did I already do this" check before doing the work.

### Why this matters more than people expect

Three reasons:

1. Retries are not exceptional, they are normal. Airflow, Dagster, every orchestrator retries on failure by default. A 1 percent flake rate means every long pipeline retries something every day.
2. The data lies quietly when it goes wrong. A doubled INSERT does not throw an error. Numbers just look "a bit high." You may not notice for weeks.
3. Backfills depend on it. When the business says "rerun the last 30 days," you can only do it safely if every step is idempotent. Otherwise you clean up by hand first, every time.

### Rule of thumb

> "I should be able to rerun this task for the same partition at any time, and the table looks the same after."

If you cannot say that, the task is not done.

### Bonus follow-up the interviewer might throw

> *"What if the upstream data changes between runs? Then the same partition gives a different answer."*

Good question. There are two stances:

1. Source of truth wins. The destination always reflects the latest upstream. Fine for reporting where you want the freshest picture.
2. Snapshot wins. The destination is frozen as of the first run. You record what was true at that moment. This is what you need for audit, billing, or regulatory data.

Pick one on purpose and document it. Most bugs in this area come from the team being unsure which one they wanted.
