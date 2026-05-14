## Solution 59: Onboarding a New Analyst

### Short version you can say out loud

> I would mix three things: read, shadow, and build, in that order. Week one is reading and access setup. Week two is shadowing me on real tickets. Week three is them shipping a small ticket end-to-end with review. Week four is independence. The thing that makes this fast is not the onboarding plan; it is what was built before they arrived: documented sources, a metrics layer, a sandbox they cannot break, and a friendly code review culture. Without those, no onboarding plan saves you.

### The 30-day plan

**Day 1: setup and welcome.**

* Accounts (warehouse, BI tool, GitHub, Slack).
* Pair on one real, low-stakes dashboard for 90 minutes. They watch, ask anything.
* End of day: they have run a SELECT, opened a dashboard, and edited a dbt model in their fork.

**Week 1: reading and exploring.**

* Read the "metrics" doc: definitions of revenue, active user, churn, anything the business uses.
* Read the high-level data flow diagram.
* Explore the warehouse with a guided tour: which dataset is what, which tables are stable, which to avoid.
* Daily 30-min check-in with me. They ask questions; I answer or point them at the doc.

**Week 2: shadowing.**

* They sit with me on real tickets. They write the SQL, I review and explain.
* One small ticket they own end-to-end with heavy pairing.
* By end of week 2, they have shipped one dashboard change with my help.

**Week 3: independence with safety net.**

* They pick up a small ticket on their own.
* Every PR they open gets reviewed by me before merge.
* They start joining standups, asking questions in the team channel themselves.

**Week 4: full ramp.**

* They own a small recurring report or dashboard.
* PRs reviewed by the team, not just me.
* By the end of week 4, they can answer the question "where do I find X" without asking.

### What I would NOT do

* **Dump a list of 30 docs to read.** They will skim and remember nothing.
* **Ship them straight to production with no review.** Trust them, but check the work.
* **Make them watch me code all month.** Boring and they do not learn by watching alone.
* **Assume the docs are correct.** They are not. Use the onboarding to fix what you find broken.

### What makes this work: the systemic side

The onboarding plan is the easy part. The hard part is what is already in place:

* **Metrics layer.** A single source for "active user" and "revenue" definitions. The analyst can find it in 30 seconds.
* **Documented tables.** Every important table has a one-paragraph description. Grain is named explicitly.
* **A sandbox dataset** they can write to without affecting production.
* **Friendly code review.** Reviewers explain, not just block.
* **Slack channel for data questions** where junior questions are welcome.

If any of these are missing, onboarding takes 3x as long because the analyst has to discover everything by asking.

### Pair, don't dump

The cheapest move is a 30-minute pairing session per day for the first two weeks. Twelve hours of pairing prevents a week of confusion. It is also where you find broken docs, weird table names, and questions you forgot you had.

### A "first ticket" that always exists

Have a small, real, low-stakes ticket ready for every new analyst:

* "Add a new dimension to the daily revenue dashboard."
* "Build a simple breakdown of orders by payment type for last 30 days."

Something where the right answer is known, the data exists, the impact is small, and there is no urgency. Their first end-to-end build is a contained success.

### Failure modes

* **They are afraid to ship.** Make the first PR small and pair-reviewed. Get them across the line.
* **They ask questions in DM.** Redirect to the channel. Helps them, helps everyone.
* **They get pulled into "urgent" requests too early.** Protect them. Their first month is not for fire-fighting.
* **They build their own off-warehouse pipeline.** Why? Because they could not find what they needed in the warehouse. That is your bug, not theirs.

### Letting them break things

Some breakage is fine. A bad PR caught in review is a great learning moment. A bad PR that hit production teaches them and the team that we need a better check. Both are healthy if the broken thing was small and recoverable.

What I would not let them do: drop a production table, send a wrong email to customers, push to the `main` branch directly. Those are guarded by access control, not by hoping they remember.

### Tracking success

After 30 days, the bar:

* Can they answer a stakeholder question without my help?
* Have they shipped at least one production dashboard?
* Are they comfortable opening PRs?
* Do they know who to ask for what?

If yes to all four, the onboarding worked. If not, identify which broke and fix the system, not the person.

### Common mistakes interviewers want you to name

1. **Document-heavy onboarding.** Most documents are stale; people learn by doing.
2. **No buddy.** Lonely week-one analysts disengage fast.
3. **Throwing them into prod day one.** Builds fear, not skill.
4. **Not telling them how to ask.** "Ask in the channel, here's the template."
5. **Skipping the "first ticket."** Without a small win, they feel lost.

### Bonus follow-up the interviewer might throw

> *"How do you scale this when you are hiring an analyst every two weeks?"*

You can't pair-onboard at that rate. Two changes:

1. **An onboarding squad rotation.** A different team member runs the onboarding each cycle. Everyone gets practice; no one is overloaded.
2. **A self-serve "first week" curriculum.** Pre-built sandbox, pre-built first ticket, pre-recorded walkthroughs for the basics.

The pairing parts are still needed but become 30 minutes a day instead of half a day. The systemic investment pays off as you grow.
