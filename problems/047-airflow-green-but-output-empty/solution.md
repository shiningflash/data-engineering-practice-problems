## Solution 47: Airflow Green but Output Empty

### Short version you can say out loud

> "Task succeeded" just means the code did not throw an exception. It does not mean data is present. The three things I check, in order: did the source have data, did the transform actually write rows, and was the output overwritten with empty. About 80 percent of "green but empty" incidents come from one of those three. The bigger lesson is that the pipeline should fail the task when the data is wrong, not just when the code crashes.

### The three checks, in order

**1. Did the source have data?**

```sql
SELECT COUNT(*), MIN(event_time), MAX(event_time)
FROM raw.source_table
WHERE event_date = CURRENT_DATE - 1;
```

If this is zero, the source did not send. The task ran, read an empty source, wrote nothing, succeeded. This is the most common cause.

**2. Did the transform actually write rows?**

```sql
SELECT
  table_name,
  row_count,
  last_modified
FROM information_schema.tables
WHERE table_name = 'curated_orders';
```

If `last_modified` is recent but `row_count` is the same as yesterday, the transform ran but the SQL produced no new rows. Maybe a filter condition is wrong, maybe the join key changed.

**3. Was the output overwritten with empty?**

Run the transform's main query manually for yesterday's date. If it returns 0 rows, the transform is "succeeding" by producing nothing.

```sql
SELECT * FROM curated_orders WHERE event_date = CURRENT_DATE - 1 LIMIT 10;
```

If empty, the pipeline cheerfully overwrote yesterday's partition with zero rows. This is the worst silent failure: it wipes existing data.

### Why "green" lies

Airflow's task success is binary on the exit code. A Python script that does `print("done")` and exits successfully is green. A SQL job that runs `INSERT INTO ... SELECT WHERE 1=0` is green. A `bq load` of an empty file is green.

The orchestrator does not know what "right" looks like. It is your job to tell it.

### Common patterns that produce silent success

1. **Empty source, idempotent overwrite.** The classic one. Source was late, transform ran on empty, output was overwritten with empty. Yesterday's data is now gone in the destination too.
2. **Filter on a column that has changed.** A new region code (Problem 46), a renamed event type, all rows filtered out.
3. **Join to a dimension that lost a row.** Inner join drops everything. Outer join would have shown nulls; the team uses inner because "it has always worked."
4. **Time zone or date math drift.** "Yesterday" is computed in a different time zone than the source uses.
5. **A `LIMIT 0` left in code** from someone's debugging session.
6. **A failed upstream that the task "handles gracefully."** Should have failed loudly.
7. **dbt model with `materialized: incremental` and a broken `is_incremental()` check.** Nothing inserted.

### What I would change to prevent silent success

The fix is to make the pipeline fail when the data is wrong, not when code crashes. A few simple guards:

**Row count assertions** as part of every load step:

```sql
-- in dbt, or as a separate guard task
SELECT
  CASE
    WHEN COUNT(*) = 0 THEN ERROR('No rows for yesterday')
    WHEN COUNT(*) < (SELECT AVG(cnt) * 0.5 FROM daily_counts_last_7) THEN ERROR('Half-empty')
    ELSE 1
  END
FROM curated_orders
WHERE event_date = CURRENT_DATE - 1;
```

**Freshness checks**: max(event_time) should be within an expected window of now.

**Source-of-truth reconciliation**: yesterday's row count in the destination should be within X% of yesterday's row count in the source.

These are cheap, run in seconds, and convert a "green task with empty output" into a "red task that gets investigated."

### Tools

* **dbt has built-in tests**: `not_null`, `unique`, custom assertions. The `dbt_expectations` package has many more. Failed tests fail the model.
* **Great Expectations** for more elaborate validation.
* **Custom Airflow `PythonOperator` or `BashOperator` tasks** that run a SQL check and fail the task if the count is wrong.

In Dagster, the same idea is "asset checks." They are first-class.

### When the silent overwrite is the real culprit

The most painful version is: the transform did write, but it wrote empty rows, overwriting yesterday's good data. Recovery requires:

* Reading the source (or backup) again.
* Re-running the transform with correct logic.
* If the source is gone, you may have permanent data loss in the destination.

The protection against this is to never overwrite blindly. Either:

* Check row count before overwriting (refuse to write 0 if yesterday had millions).
* Snapshot the destination partition to an archive before overwriting.
* Use Delta/Iceberg time travel so you can restore.

### The lesson

The team's mental model has to shift from "the task succeeded" to "the data is right." Every important transform should publish two facts at the end:

* The task succeeded.
* The output passes its data checks.

A green task without data checks is a half-deployed pipeline.

### Common mistakes interviewers want you to name

1. **Trusting Airflow green.** Code-level success is not data-level success.
2. **Idempotent overwrite without count protection.** Silent erasure.
3. **No anomaly alert on row count.** The smallest signal that catches most of this.
4. **Inner join in places that should be outer.** Drops "missing" silently.
5. **Letting "no data is fine" be the default.** It is not. Make it a failure.

### Bonus follow-up the interviewer might throw

> *"How would you design the pipeline so a missing source delays the run rather than producing empty output?"*

Use a sensor (Airflow Sensor, Dagster `auto_observe`). The pipeline waits for the source to arrive before it starts the transform. If the source does not arrive within a timeout, the sensor fails the DAG with a clear "source missing" message. Now the failure is loud and actionable, not silent.
