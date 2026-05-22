## Solution 31: "The Dashboard Is Wrong"

### Short version you can say out loud

> I take it seriously and I do not argue with the gut feeling. I ask one open question to find the specific number, then I show my work as I check. Usually the analyst has noticed a real thing — they just have not localized it yet. If it turns out the data is right, the conversation ends with "thanks for catching this" and a small change so the next person trusts the dashboard faster.

### The first reply

```
Don't say: "The data is correct, I checked yesterday."
Don't say: "The pipeline is healthy, no errors."
Don't say: "Which exact number?"  (too blunt)

Do say:
"I'll take a look. To help me find it fast — what were you
expecting to see, and what looks off? Even rough numbers are fine."
```

This does three things:

1. Takes them seriously instantly.
2. Asks for their expectation, not the actual number. This is the key move. "It feels off" is hard; "I expected revenue around $X" is concrete.
3. Lowers the cost for them to engage. They do not have to be precise.

### Turning vague into specific

Senior analysts almost always have a number in mind. A few questions that get there:

* "Roughly when did it look off? Today, this week?"
* "Is one chart wrong, or does it ripple through several?"
* "Compared to what — last week, last quarter, your forecast?"

Within two messages, you usually have something concrete: "Revenue for last Thursday showed $182k, I expected closer to $220k."

Now I have something to check.

### My investigation, out loud

I share my screen or paste queries as I go. Three reasons:

1. The analyst can correct me if I am looking at the wrong thing.
2. They learn the data better. Next time they can self-serve a little more.
3. It builds trust: I am not deciding alone behind a curtain.

The checks:

```
1. Does the dashboard match the warehouse table it claims to read from?
   SELECT SUM(revenue) FROM marts.daily_revenue WHERE date = '2025-05-08';

2. Does the warehouse table match its upstream source?
   Compare against payments source / OLTP / partner statement.

3. Did the pipeline run fully and on time for that date?
   Check Airflow / dbt / data freshness.

4. Is there something special about that date?
   Holiday, deploy, migration, source outage.

5. Has the dashboard's underlying query changed recently?
   git blame on the SQL.
```

In 80 percent of cases, one of these surfaces the answer in 15 minutes.

### Three possible outcomes

**Outcome A: there really is a bug.**

Now treat it like Problem 29. Communicate to the wider team, find the size of the error, fix and backfill, and add a check so the next time it shows up automatically.

**Outcome B: the data is right, the analyst's expectation was wrong.**

This is the delicate one. Don't say "the data is fine, you were wrong." Instead:

> "Confirmed against the payments source: Thursday was $182,144. The dip was a Singapore public holiday — the same drop appears in last year's data. I will add a holiday flag to the dashboard so this is obvious next time."

The analyst's instinct was good. They saw an unusual number. The data is correct, but the dashboard could have made it easier to read. The fix on our side is a small UX improvement.

**Outcome C: the number is right, but the metric definition surprised them.**

Common case: "revenue" includes refunds, or excludes them, and the analyst assumed the opposite. The dashboard is technically correct but doesn't show the assumption.

> "Found it. The number is net of refunds. You were expecting gross. Both are valid views, but the dashboard does not say which. I will add a tooltip and rename the column."

### The trust dynamic

The hardest part of this conversation is not the SQL. It is that an analyst who flags a "wrong dashboard" is risking their reputation. If I argue back, they will stop telling me. The next time something is actually broken, I will not hear about it.

So the rule is: never make them feel small. Even when the data is right, their instinct caught something — usually a clarity gap.

Equally, the rule for them: I will not let them fix it for themselves with side queries that diverge from the dashboard. We will fix the dashboard. That keeps a single source of truth.

### Making this easier next time

After the conversation, a few small changes pay off forever:

* **Tooltips on every metric** explaining the definition. "Revenue = gross sales net of refunds, in local currency."
* **A "data freshness as of" stamp** on the dashboard. Stale data is the second most common cause of "this feels wrong."
* **A "compare to last week" or "compare to last year"** toggle. The analyst's instinct usually came from a comparison.
* **A "report a problem" button** that captures the dashboard, the filters, the user, and a short note. Half of these messages would be specific from the start.

### What I would NOT do

* Reply "the pipeline succeeded, the data is correct." It is dismissive even when literally true.
* Demand they file a ticket before I look. They might never come back.
* Investigate in silence for 4 hours and then announce a conclusion. Bring them along.
* Take the blame for nothing. If the data is right, say so plainly, while still thanking them.

### How to talk about this in an interview

The interviewer is checking three things:

1. **Empathy.** Do you take the analyst seriously?
2. **Structure.** Do you have a checklist when the question is vague?
3. **Honesty.** Can you say "the data is right" without being defensive?

If you can show all three in three minutes, you are answering the question.

### Common mistakes interviewers want you to name

1. **Defending the pipeline before checking.** "The pipeline is fine" is not the same as "the dashboard is fine."
2. **Asking for too much detail up front.** "Which date, which filter, which row" feels like an interrogation.
3. **Fixing only the symptom.** The analyst gets a new dashboard; the next analyst will be confused too.
4. **Not closing the loop.** They reported it; tell them what you found.
5. **Marking the issue "won't fix"** because the data was technically right. It cost trust; that is not "won't fix."

### Bonus follow-up the interviewer might throw

> *"How do you handle it when the analyst is wrong twice in a week and the team starts treating them as 'that person who cries wolf'?"*

Take them aside privately and offer a hand. "I noticed both reports last week turned out to be misunderstanding the definition. Want me to walk through the metric layer with you in 30 minutes? It'll save us both time." This protects them, builds their understanding, and reduces noise without ever shaming them in public.
