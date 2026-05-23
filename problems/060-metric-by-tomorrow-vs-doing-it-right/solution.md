## Solution 60: "I Need This Metric by Tomorrow"

### Short version you can say out loud

> I ship a number tomorrow and a proper version next week. The tomorrow version is a one-off query, clearly marked as draft, with the caveats I'd share in an exec briefing. The proper version goes through the regular metric flow: definition reviewed, model in dbt, tests, dashboard. The stakeholder gets what they need; the team doesn't accumulate undocumented one-offs. The only thing I refuse to do is ship a one-off and call it done.

### The conversation, tomorrow morning

> "I can have a number for you by end of day. I want to confirm the definition with you in 10 minutes so we're computing the same thing. Then I'll share the number with the caveats. Next week, I'll productize it in the dashboard with proper tests so it doesn't need me to rerun it. Sound good?"

Three things in that message:

1. Commits to today. Stakeholder gets unblocked.
2. Locks the definition. Cheap conversation now, expensive surprise later if skipped.
3. Promises the proper version. Not "if I get time," not "we'll see." A date.

### Locking the definition before computing

The 10-minute definition conversation is the single most important step. The question I always ask:

> "If we measure this metric tomorrow and the number is X, what would make you say 'that's wrong'?"

Their answer tells me what they actually mean. Often it's not what the requested wording said.

Concrete examples that catch real ambiguity:

* "Active user": does that include trial users? Bot accounts? Mobile-only?
* "Revenue": gross or net of refunds? In what currency? Include subscription pro-rations?
* "Conversion rate": over what funnel step? Over what time window?

Settling these before computing saves multiple rounds of "actually, I meant..."

### What I ship tomorrow

A single Slack message or document with:

* The number.
* One paragraph on how it was computed (named tables, named filters).
* Two or three caveats that affect interpretation.
* The note "This is a draft for tomorrow's meeting. Full productized version coming by [date]."

That's it. Not a spreadsheet flying around. A Slack message in their team channel, archived, readable.

Example:

> Adoption of new feature in Q1: **12.4%**.
>
> Computed as users who triggered `feature_unlocked` at least once between Jan 1 and Mar 31, divided by all active users in that period. Sources: `events.feature_events`, `marts.daily_active_users`.
>
> Caveats:
> 1. "Active" here means at least one login in the period. Stricter definitions of "active" change the number by 1-2 pp.
> 2. Users on legacy mobile clients (~3% of base) don't emit the event. The true rate is slightly higher.
>
> A productized dashboard with these numbers will be ready by Wednesday.

### What I ship next week

The proper version goes through the regular flow:

1. Add the metric to the metrics layer or dbt project.
2. Build the dashboard.
3. Add data tests.
4. Document the definition in the metrics doc.
5. Share with the stakeholder; have them confirm the dashboard matches what they expected.

This takes a couple of days, not a heroic week. The hard part was the definition, which we already did.

### Why I would not just ship the one-off and stop

Two real costs of "one-off as final":

1. Stakeholders ask for the same number again next quarter. I re-run the one-off and possibly get a slightly different number because the data changed or my SQL was different. Now I look unreliable.
2. The one-off has no tests, no documentation, no lineage. When the source schema changes, my one-off breaks silently and the stakeholder uses a wrong number for a quarter.

The productized version is the protection.

### Avoiding "tomorrow" becoming forever

The "by next week" promise has to be real. Two protections:

* Put it in the team's planning. A ticket, a date, an owner. Not a Slack promise.
* Keep the stakeholder in the loop on the proper version. They'll ask if it slips. Their pressure replaces yours.

If you skip both, three months later the stakeholder is still pasting your one-off number into board decks.

### How to handle "tomorrow's tomorrow"

If they need the number again next week and the proper version isn't ready, you might be tempted to re-run the one-off. Don't. Instead:

> "Same number for last week, computed the same way: 14.1%. Productized dashboard with this and weekly refresh is on track for Wednesday."

The interim re-run is documented, attached to the same Slack thread, and the proper version's ETA stays visible.

### The cultural side

The stakeholder is asking "tomorrow" because past experience says data takes too long. If you keep that promise and follow through on the productized version, the next ask is easier:

> "Hey, can we add a new metric? I know it'll take a week to do properly."

That's the goal. They've learned that "tomorrow" gets a number and "next week" gets a real thing, and that both are reliable.

### What I would NOT do

* Refuse the tomorrow ask. Looks obstructive.
* Quietly ship something half-baked that they then quote as final.
* Promise it'll be ready tomorrow when it won't. Tells them I can't estimate.
* Wing the definition. Ten minutes saves ten rounds of revision.

### Common mistakes interviewers want you to name

1. No definition lock. Number ships, stakeholder reads it differently, conflict in two weeks.
2. Ship one-off and stop. Stakeholder bases decisions on un-tested SQL.
3. Make them wait a week. Looks like the data team is slow.
4. Skip the caveats. Avoid friction now, cause bigger friction later.
5. No tracking of pending productizations.

### Bonus follow-up the interviewer might throw

> *"What if you also have three other tomorrow asks competing for the same day?"*

That's a prioritization conversation, not a data conversation. Push it to whoever owns the team's priorities. Be transparent:

> "I have three other asks for tomorrow. I can do all four with quick one-off numbers, or two of them properly. Which two are most important?"

Most stakeholders, forced to triage, drop the lower-priority ones. The ones that survive get done well.
