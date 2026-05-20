## Solution 32: Inheriting a Pipeline No One Owns

### Short version you can say out loud

> I do not start coding. I spend the first day reading the pipeline end to end, running it in a sandbox, and writing down what I observe. I look for the seam where the new requirement is supposed to land. I add the smallest possible change with a way to roll back, and I add a test for the change so that even if I do not understand the rest of the pipeline yet, I understand the part I touched. The instinct to "just rewrite it" is the most expensive mistake here.

### Day 1: read, do not code

Things I would read in this order:

1. **The schedule and the recent run history.** When does it run, how often does it fail, how long does each step take?
2. **The DAG / orchestrator config.** Airflow, Dagster, whatever it is. Draw the dependency graph on paper.
3. **The code, top down.** Start from the entry point, not from the new requirement's spot.
4. **The destination tables.** What does the output look like, what are its grain, what columns are populated and which look untouched?
5. **The last 3 months of incident notes.** Slack, on-call channel, anything. People often leave breadcrumbs.

By end of day 1 I should be able to draw the pipeline on a whiteboard and explain each box. If I cannot, I keep reading.

### Day 2: run it in a sandbox

A real-data sandbox is the second most valuable investment. I would:

* Spin up a copy that points at a non-production target.
* Trigger one historical day's run.
* Diff the output of my sandbox against the real production output for the same day.
* They should match exactly. If they do not, my sandbox setup is wrong, or the pipeline has hidden state.

Running it teaches things reading does not: which steps are actually slow, which call external APIs, where retries happen, what the failure modes look like.

### What I am looking for

While reading and running, I am hunting for:

* **Pure functions vs side effects.** Pure transforms are easy to change. The dangerous code is the part that talks to external systems.
* **Idempotency.** Can I run it twice for the same day? If yes, I can experiment without fear.
* **Seams.** Places where the change is supposed to land. Usually it is one transform out of many, not a sprawling rewrite.
* **Surprises.** "Why is this transform here?" If I cannot explain it after reading, I do not delete it. Chesterton's fence.

### A note on Chesterton's fence

There is always code in an inherited pipeline that looks pointless. Maybe a strange filter, a magic constant, a weird CASE WHEN. The instinct is to delete it.

Don't.

It was put there for a reason, usually a bug or a stakeholder request. Until I know the reason, I leave it alone. If I really need to remove it, I ask first: "Anyone remember why this filter exists?" Half the time someone does. The other half, I add a comment "removed 2025-05, reason unknown, no apparent downstream impact" and watch for two weeks.

### Day 3: the smallest change that does the new requirement

Now I implement the change. The discipline:

* **Single PR.** No "while we are at it" cleanup.
* **Tests for the new behavior.** Even just a small fixture and an assertion in the same PR. This is now the only test in the pipeline. It is more than there was yesterday.
* **A way to roll back.** Either a feature flag, or a small migration that is reversible. Idempotent partition replace is gold here: I can rerun yesterday's data with the old code if the new one is wrong.
* **Production parity check.** Run the modified pipeline against the same day, compare the output against production. The new column or new rule should appear; everything else should be identical.

### Documentation as I learn

Every time I figure something out, I write it down. Not a beautiful doc. A `README.md` next to the code, with sections like:

```
# Pipeline: revenue-rollup

## Schedule
Runs at 03:00 UTC daily. Backfills allowed for last 14 days.

## Inputs
- raw.orders   (partitioned by event_date)
- raw.refunds  (partitioned by event_date)
- ref.tariffs  (full table, SCD2)

## Outputs
- marts.daily_revenue  (one row per region per day)

## Known quirks
- The `is_test_account` filter exists because of a 2023 incident
  with the QA team's traffic appearing in revenue. Do not remove.
- The Athena step in stage 3 is much slower than the rest. ~25 min.
  Not yet investigated.

## Failure modes I have observed
- Source partition arrives late. Pipeline succeeds on empty input.
  This is the silent failure mode; we have not added a check yet.
```

Three months from now, the next person inheriting this will thank me. So will I, when I have forgotten.

### What I would NOT do in the first month

* **Rewrite the pipeline.** It works. The new owner is the worst rewriter — I have least context.
* **Migrate it to a new orchestrator.** Even if Airflow is "old," the migration is the wrong first move.
* **Add 20 new dbt tests.** Add 2, on the things I touched. More can come later.
* **Remove the strange CASE WHEN.** Chesterton.
* **Restart failed runs without reading the error.** That is how the previous team got here.

### What I would do in the first month, besides the change

After the immediate change is live, I would:

* Add a freshness check on the output table. "Yesterday's row exists, and the row count is within 30 percent of the trailing 7-day average."
* Tag the pipeline with my name as owner so future questions come to me, not nobody.
* Schedule a 15-minute "data team handover" where I walk a colleague through what I know. Now we have two people who know it.

### The conversation with the requester

The new requirement came from somewhere. The conversation should be honest:

> "I will deliver the change by Friday. While I am there, I'm going to spend two days getting comfortable with the pipeline because the previous owner left and the code is dense. After Friday, I will know the pipeline well enough to commit to faster turnaround on future requests."

This sets expectations and earns time for the careful read. Most stakeholders are fine with this if you are clear.

### Common mistakes interviewers want you to name

1. **The big rewrite reflex.** Cost is high, risk is enormous, value is unclear.
2. **Touching prod first.** Always sandbox.
3. **Removing "obviously dead" code** without finding out why it was there.
4. **Not adding documentation** while the system is fresh in your head. It will not be fresh in a month.
5. **Working alone.** Pair the read with a teammate; the second pair of eyes catches surprises.

### Bonus follow-up the interviewer might throw

> *"At what point would you rewrite it?"*

Three signals together:

1. The code is genuinely hard to change safely (no tests, hidden state, fragile dependencies) AND a major requirement is coming that forces a deep change.
2. The cost of operating it (incidents, debugging time) is high enough to make rewriting cheaper over 6 months.
3. The team has the bandwidth to maintain both old and new for the transition.

If only one is true, do not rewrite. Patch carefully. The rewrite is justified only when the alternative is more painful, not when the existing code is ugly.
