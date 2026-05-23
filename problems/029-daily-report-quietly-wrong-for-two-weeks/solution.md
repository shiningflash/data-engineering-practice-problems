## Solution 29: Daily Report Quietly Wrong for Two Weeks

### Short version you can say out loud

> The first 30 minutes are about telling people and stopping further bad decisions. The next few hours are about finding the cause and the size of the error. The rest of the week is about correction and rebuilding trust. The real work begins after, with the question "why did this go undetected for two weeks." That answer is almost never one bug. It is a missing check.

### Hour 1: communicate, don't investigate alone

Before I open a query editor, I post in the team channel and the analytics channel:

> "Heads up, finance found a mismatch on the daily revenue numbers, possibly going back two weeks. I am investigating. Please pause any decisions based on the daily revenue dashboard while I confirm what's going on. I will post an update by 2 PM."

Three reasons:

1. People who used the number this morning need to know.
2. It looks bad to investigate quietly for 6 hours and then post a bombshell.
3. Others on the team might already know something useful.

I also tag the analytics lead and let my manager know one-to-one.

### Hour 2-3: triage

Two things in parallel:

**A. How big is the error?**

Compare three numbers for the last 30 days:

* The dashboard's claimed daily revenue.
* The source-of-truth system's daily revenue (the payment gateway, the OLTP database, the partner statement).
* The warehouse's raw fact, recomputed from scratch.

A simple SQL or notebook produces three columns side by side. The day the mismatch starts is usually obvious.

**B. When did the divergence start?**

The first day where the warehouse number stops matching the source is the inflection point. I look at:

* Git log of dbt models touched that week.
* Airflow / Dagster runs and their durations on those days.
* Schema change events on the source.
* Any product release that might have changed event emission.

Three out of four times, the cause is something in that list. The first cause I find may be the only cause, or there may be two combining. Be honest about which.

### Hour 4-5: confirm root cause

A few classic culprits:

* **A source schema change.** A new column was added or a value's meaning changed. The transform silently dropped or miscategorized rows.
* **A renamed column** killed a join key, producing NULL where there used to be a value.
* **A new product feature** generates events with a different shape. The transform never accounted for them.
* **A time zone change** in some source system, off by one day.
* **A unit change**, like a price moving from cents to dollars (this one I've seen).

I want to be able to say "the divergence is N% per day and is caused by X." If I cannot, I keep digging.

### Hour 6 onwards: tell stakeholders the real story

A second message, this time concrete:

> "Update: the daily revenue dashboard has been undercounting by about 4.2% since May 1. Cause: on April 30 we added a new product line whose events come through a different topic, and the transform that builds the revenue fact was not updated to include them. The amount is real revenue, not lost, it just was not showing in the dashboard. I have a fix in PR review and will backfill the last 14 days by tomorrow morning. Decisions made on this data should be revisited; I am compiling a list of which dashboards were affected."

The tone matters. Specific. Not blaming a person. Names the impact.

### The fix and the backfill

The fix lands in dbt. The backfill runs the corrected model for the affected partitions. Because dbt models are idempotent by partition (as in Problem 9), the backfill is safe to rerun.

After the backfill, I refresh the comparison and confirm the numbers match the source of truth.

### Now the real work: why did nobody notice

This is what the postmortem is actually about. The answer is usually one of:

* **No tolerance check.** Nobody had wired "warehouse daily revenue should be within 1% of payments source daily revenue." If they had, page would have fired on day one.
* **No anomaly check.** Daily revenue dropped 4.2% with no explanation. A simple "compare to 28-day moving average" would have flagged it.
* **The dashboard owner moved teams** and the new owner did not know to monitor it.
* **People don't believe the dashboard anymore**, so they don't look at it carefully. This one is cultural and it's the worst.

### The changes I would propose

Three layers of defense:

**1. Source-of-truth reconciliation.** A dbt test that compares the daily revenue fact to the source system's daily total within a tolerance. Runs after every load. Pages on mismatch larger than 1%.

```yaml
- name: revenue_matches_source
  test: assert_within_tolerance
  expression: |
    SELECT
      ABS(SUM(warehouse_revenue) - SUM(source_revenue)) /
      NULLIF(SUM(source_revenue), 0) AS diff_pct
    FROM revenue_reconciliation_view
    WHERE date = CURRENT_DATE - 1
  threshold: 0.01
```

**2. Anomaly check.** A check that compares yesterday's value to the trailing 28-day average. Pages on >3 standard deviations. Catches even smaller drifts.

**3. Schema drift alert.** Any column added or removed in a source feeds a notification to the data team. Even if the transform survives, someone looks at the change.

**4. Ownership.** Every important dashboard has a named owner. The owner gets a weekly "your dashboard updated successfully" digest. If the digest stops, they know to ask why.

### What I would NOT do

* Blame an individual. Two weeks of silence is a system problem.
* Add a check for this specific schema change. The bug will not repeat. The next one will be different.
* Promise "this will never happen again." It will. Promise to detect it within a day.

### How to talk about this in a real interview

If the interviewer wants you to actually walk it through, the spine of the answer is:

1. Communicate first.
2. Quantify the error.
3. Find the change that caused it.
4. Confirm size, tell stakeholders, fix and backfill.
5. Postmortem on the *detection failure*, not the bug itself.
6. Add structural checks so the next divergence is caught fast.

If you can hit those six points, you are answering the question they are really asking, which is: "are you the kind of engineer I want around when something goes wrong?"

### Common mistakes interviewers want you to name

1. **Investigating quietly.** Other people are still using the wrong number while you dig.
2. **Focusing on the bug, not the detection gap.** Catching the next one matters more than this one.
3. **Adding 50 alerts after the incident.** Alert fatigue. Three high-signal checks beat 50 noisy ones.
4. **Not actually backfilling.** Some teams "fix forward" only. Old reports remain wrong.
5. **Forgetting to tell the people who used the bad data.** Decisions they made may need revisiting.

### Bonus follow-up the interviewer might throw

> *"How would you build a culture where teams trust the data enough to actually report mismatches early?"*

Two things help:

1. **Make data quality visible.** A "freshness and accuracy" status page that updates automatically. People learn the system has health.
2. **Reward early reporting.** When finance reports a mismatch, thank them in public. Make it clear that catching things is good, not annoying.

Trust is built slowly and broken fast. The two-week silence above destroyed some of it; rebuilding takes a few quarters of clean operation and visible checks.
