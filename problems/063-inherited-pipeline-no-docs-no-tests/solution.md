## Solution 63: Inherited Pipeline With No Docs, No Tests

### Short version you can say out loud

> My first month is read, run, document, test, then change. In week one I read the code and the schedule. In week two I run it in a sandbox and confirm parity with production. In week three I add the smallest meaningful tests, and I write a README as I go. In week four I make the smallest useful change someone has been asking for. I tell my manager up front that the first month is mostly about not breaking things and understanding what I have inherited. If they expect heroic delivery in the first month, that is a different conversation.

### Week 1: read and run history

Tasks:

* Read every Python file or SQL model in the pipeline.
* Look at the orchestrator graph (Airflow / Dagster) and draw it on paper.
* Read the last 90 days of run history. Note which tasks fail or slow down.
* Read the last 90 days of Slack messages about this pipeline.
* Find the output tables and look at what they produce.

By the end of week 1, I should be able to:

* Draw the data flow on a whiteboard.
* Name every input source.
* Name every output table.
* Roughly explain what the pipeline does to anyone who asks.

I do not change anything yet.

### Week 2: run it in a sandbox

Set up a clone of the pipeline that points to a non-production target. Pick one historical day and run the full pipeline against it. Compare every output table row by row, sum by sum, against the production output for the same day. They should match exactly.

If they don't match, my sandbox setup is wrong (more common) or the pipeline has hidden state (less common). I keep going until parity is real.

At the end of week 2:

* I can reproduce a historical day's output.
* I have a working sandbox to experiment in.
* I have a feel for which steps are slow, which are fragile, which are clean.

### Week 3: tests and a README

Now I start protecting the pipeline.

Add a small README at the root of the pipeline's code:

```
# Revenue Rollup Pipeline

## What it does
One sentence. What goes in, what comes out, on what schedule.

## Inputs
- raw.events    (partitioned by date, written by event-ingest team)
- ref.products  (full table, refreshed daily at 03:00)
- ref.tariffs   (SCD2 dim)

## Outputs
- marts.daily_revenue    (one row per region per day)
- marts.product_summary  (one row per product per week)

## Schedule
Daily at 04:00 UTC. Backfills allowed for last 14 days.

## Known quirks
- The is_test_account filter exists because of a 2023 incident.
  Do not remove.
- Stage 3 (Athena step) is ~25 min, slowest part. Not yet investigated.

## How to backfill
dagster job backfill --partition YYYY-MM-DD ...
```

Then I add the minimum useful tests:

1. **Row count tolerance**: today's row count is within 30% of the trailing 7-day average. Catches "silent zero" days.
2. **Source freshness**: the input partition for today exists and has >0 rows.
3. **Output uniqueness**: no duplicate primary keys.
4. **Source-of-truth reconciliation**: today's sum matches an independent source within 1%.

Four tests. Each prevents a class of incident. None of them touch the business logic.

By end of week 3:

* The README exists.
* The first round of tests is wired in.
* My understanding is solid enough to talk about the pipeline confidently.

### Week 4: the first real change

Pick the smallest, most useful change someone has been asking for. Make it. Use the sandbox for parity check. Open a PR with tests. Merge. Watch the next run.

This first change is the proof that I can change the pipeline without breaking it. Once it's shipped, my confidence and the team's confidence in me both go up.

### Setting expectations with my manager

Day one, I would say:

> "I will keep the pipeline running and start learning it deeply in the first month. I expect to ship one meaningful change by end of week four, with tests. Bigger changes or a rewrite, if needed, would come later, after I am sure I understand what I am touching. Is that pace acceptable, or do you need something faster from me in the first month?"

Three properties of this:

* Honest about velocity.
* Promises a deliverable (the week-four change).
* Opens space for negotiation.

If they say "we need feature X in week one," it is a conversation, not a fight. Either feature X is simple enough that I can do it, or they need to know the risk.

### When I would consider a rewrite

Not in month one. Not in month three. Maybe in month six, and only if:

* I have shipped multiple small changes safely.
* The current code blocks a major requirement.
* The team has bandwidth.
* I can explain to my manager why it is cheaper to rewrite than to keep patching.

Most pipelines don't need rewriting. They need documentation, tests, and small clear changes.

### The Chesterton's fence rule

Through the whole month, when I find code that looks unnecessary, I do not delete it. I ask "why is this here?" If nobody knows, I leave it and write a comment:

> // This filter was added in 2023 commit abc1234. Reason unclear. Investigated 2025-05; nobody on the team remembers. Leaving in until impact of removal can be measured.

The comment is a placeholder for the next person. It is honest. It does not break anything.

### What I would NOT do

* **Rewrite anything in month one.** Even if it is ugly.
* **Add 30 tests at once.** Four good ones beat 30 noisy ones.
* **Promise the moon to my manager.** It will hurt me later.
* **Restart failed runs without reading the error.** That is how the previous owner got here.
* **Delete the "weird" code.** Chesterton.

### After the first month

By month two and three:

* I am the owner. Pages come to me.
* I have shipped 3-5 small improvements.
* I have added a few more tests, one at a time, each motivated by a near-miss.
* I have started a "future improvements" list with a rough order.

By month six:

* I know the pipeline as well as anyone ever did.
* I can talk about rewriting, with evidence.
* The pipeline is in better shape than when I inherited it.

### Common mistakes interviewers want you to name

1. **Big-bang rewrite.** Highest risk move for the least context.
2. **No README.** Next person inheriting hits the same wall.
3. **No sandbox.** All changes go straight to production.
4. **Removing "obviously dead" code.** Bites you.
5. **Setting unrealistic expectations.** Disappoints everyone, you most of all.

### Bonus follow-up the interviewer might throw

> *"What if the pipeline is actively broken when you arrive?"*

Different problem. First, stop the bleeding: identify the immediate failure and patch it minimally to get it running again. Then revert to the month-one plan. The patch you applied is in the README under "known issues to investigate." Do not let the urgency tempt you into a rewrite while you still do not understand the pipeline.
