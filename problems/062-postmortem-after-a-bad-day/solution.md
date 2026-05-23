## Solution 62: Postmortem After a Bad Day

### Short version you can say out loud

> A postmortem has two goals: learn from what happened, and rebuild trust. The structure is timeline, root cause, what went well, what went badly, and action items with owners. The cultural rule is blameless: we never name a person as the cause. The deliverable is a short document, three to five pages, that anyone in the company can read in 15 minutes. The promise we make at the end is not "this will never happen again", it is "we will detect faster and respond better."

### The structure I would use

```
Postmortem: <one-line incident description>
Date of incident: 2025-05-14
Duration of bad data: ~22 hours
Author: <your name>

1. Summary               (one paragraph)
2. Impact                (numbers wrong, who used them)
3. Timeline              (what happened and when)
4. Root cause            (technical, not blame)
5. What went well        (don't skip this)
6. What went badly       (honestly)
7. Action items          (owners and dates)
```

### Section by section

**1. Summary.**

One paragraph. What broke, what the impact was, how it was found, when it was fixed.

> On May 14, the daily revenue dashboard reported numbers approximately 18% below actual revenue. The cause was a transform update on May 13 that filtered out a new product line. Detected at 09:40 by a finance review. Fixed and backfilled by 14:20 the same day. Approximately $X of revenue was misreported in three downstream communications.

**2. Impact.**

Concrete. Not "some data was wrong." How much, where, who used it.

* Revenue dashboard wrong by ~18% for one day.
* Sales used the number in a customer call.
* Finance shared it in a Tuesday business review.
* A PR draft cited the lower number; PR team caught it before send.

**3. Timeline.**

Hour by hour, what happened. From the original commit through the fix. Specific timestamps and actions.

```
May 13, 16:42  PR #2891 merged, adds filter excluding test products.
                The filter accidentally matches a new real product line.
May 14, 02:15  Daily ETL runs with new logic; revenue computed wrong.
May 14, 09:40  Finance analyst flags discrepancy in Slack.
May 14, 10:05  Data engineer investigates, finds the filter.
May 14, 11:30  Fix PR opened.
May 14, 12:15  Fix merged.
May 14, 13:40  Backfill of May 14 partition complete.
May 14, 14:20  Dashboard refreshed; downstream consumers notified.
```

The timeline is the spine. Everything else hangs off it.

**4. Root cause.**

Technical. Specific. No names.

> The filter in the `revenue_clean.sql` model uses `WHERE product_id NOT IN (SELECT id FROM test_products)`. The new product line had been added to `test_products` for QA on May 12 and not yet removed when launched on May 13. The transform inherited the QA flag without revalidating.
>
> Contributing factor: no data test verified that the day's row count was within tolerance of the previous week. A check would have flagged the issue at 02:30, seven hours before manual detection.

The contributing factor is as important as the cause. The cause is a single bug; the contributing factor is the missing safety net.

**5. What went well.**

Three to five bullets. Skipping this section is a mistake. It makes the document feel like punishment.

* Finance caught the issue manually and reported it immediately.
* Root cause was identified within 25 minutes of report.
* Fix was developed, reviewed, and shipped within 2.5 hours.
* PR team caught the bad number before the external communication went out.
* Communication during the incident was clear; stakeholders were updated hourly.

**6. What went badly.**

Honest. Specific. Still no names.

* No automated check flagged the row count anomaly.
* The dashboard had no "freshness and quality" indicator; consumers could not see it was suspect.
* Three communications were drafted on the wrong number before detection.
* The QA-flag-then-launch sequence is not documented as a known risk in the model's README.
* It took 100 minutes from "fix merged" to "consumers notified." Communication should have started earlier.

**7. Action items.**

The output everyone reads. Each item has an owner, a date, and a measurable target.

| # | Action | Owner | Due |
| - | ------ | ----- | --- |
| 1 | Add row-count anomaly test on `revenue_clean` (3σ threshold) | <name> | May 21 |
| 2 | Add freshness/quality badge to dashboard | <name> | May 28 |
| 3 | Move `test_products` to a separate "QA isolation" pattern; document in README | <name> | May 30 |
| 4 | Create incident playbook for "wrong data" with comms checklist | <name> | June 7 |
| 5 | Pre-launch checklist for new product lines: includes data team review | PM team | June 7 |

Five items. Not 50. Each one ships within four weeks. They are the actual prevention of the next incident.

### The cultural rules

**Blameless.** Never write "Alice committed PR #2891 without enough review." Write "PR #2891 was merged. The review process did not catch the filter interaction." The mistake belongs to the system, not the person.

This is not about being soft. It is about accuracy. If Alice were not here, the same bug would have happened, because the system did not catch it. The system is the thing to fix.

**Honest, including the slow parts.** Write the actual times. "100 minutes from fix to consumer notification" is uncomfortable but it is what happened. Owning it earns the right to fix it.

**Specific.** "We should be more careful" is not an action item. "Add automated tests" is closer, but still vague. "Add row-count anomaly test on revenue_clean, threshold 3σ, by May 21" is real.

### The communication around it

The postmortem is shared with:

* The team.
* The directly affected stakeholders (finance, sales, PR).
* Leadership.

Optional, but a good idea: a public version (with sensitive details removed) in the data team's wiki. Other teams reading "what we learned" makes the data team look more professional, not less.

### What I would NOT do

* **Promise it will never happen again.** It will. Promise to detect faster.
* **Add 30 new tests.** Alert fatigue. Add the three that would have caught this.
* **Name the person who wrote the PR.** Demotivating and inaccurate.
* **Skip the "what went well."** Looks like punishment, leaves the team demoralized.
* **Lock up the postmortem.** Sharing builds trust.

### Following up

Two weeks later: a quick check.

* Are the action items on track?
* Did the new test fire on any partition? (If yes, was it a real catch?)
* Is the team still feeling the incident, or have we moved on?

Three months later, look at the action items list. Anything still open? Why? Either close it or push it to closure.

### Common mistakes interviewers want you to name

1. **Blame.** Postmortem becomes a thing nobody wants to attend.
2. **Promises with no actions.** "We'll be careful" disappears.
3. **Too many action items.** Five focused ones beat 30 vague ones.
4. **Hiding the document.** Trust comes from transparency.
5. **No follow-up.** Action items rot. Schedule a check.

### Bonus follow-up the interviewer might throw

> *"What if the same team has a second similar incident a month later?"*

That is a real conversation. The pattern across two incidents tells you something the first one alone did not. Maybe the test you added did not cover the right thing, or maybe the deploy review process has a structural gap. The second postmortem includes "What did the first postmortem miss?" as a section. This is healthier than pretending it is unrelated. Two of the same kind of incident means a class of problem; that needs a deeper structural fix, not another patch.
