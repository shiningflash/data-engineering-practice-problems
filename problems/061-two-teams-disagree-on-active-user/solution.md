## Solution 61: Two Teams Disagree on "Active User"

### Short version you can say out loud

> The two numbers are almost certainly both right. Each team has a definition that fits their work, and neither knows the other's definition. My job isn't to pick a winner. It's to surface both definitions side by side, get them in one room, and help them agree on what each one means and when each one should be used. The longer-term fix is a metrics layer where every metric has a name, an owner, and a definition that everyone can see.

### Step 1: get both numbers and both definitions

Before any meeting, I gather the raw material:

* Product team's query: users who logged in at least once in the last 30 days.
* Finance team's query: users with a paid event in the last 30 days, excluding trial-only accounts and accounts marked as test.

The numbers diverge because the definitions diverge. The product number is bigger because it counts more.

I write both definitions in plain English and put them side by side:

```
Metric                    Product's count       Finance's count
─────────────────────────────────────────────────────────────────
Users counted             logged in >=1 time    had a paid event
                          in last 30 days       in last 30 days
                                                AND not trial
                                                AND not test account
Number                    1,200,000             980,000
Source                    events.logins         marts.fact_payments
                                                + dim_users filters
```

Already visible: the two aren't measuring the same thing.

### Step 2: get both teams in one room

Don't email. Don't Slack. Schedule a 30-minute meeting with one representative from each team plus you. Bring the table above and a shared document.

The meeting isn't "who is right." It's "what is each one for."

Likely outcome:

* Product's definition is right for product engagement.
* Finance's definition is right for revenue-related reporting.
* They're not the same metric. They shouldn't be called the same name.

### Step 3: rename and document

In the meeting, propose new names:

* "Monthly Active Users (MAU)" for product's number.
* "Paying Users" or "Active Paying Customers" for finance's number.

Now there's no ambiguity. The CEO sees 1.2M MAU and 980K paying customers. Both true, both useful, different meanings.

Get verbal agreement from both teams in the meeting. Write it up in the doc. Each definition has:

* A name (unique).
* An owner (the team that defines it).
* A precise definition.
* The source query or model.
* A version date.

### Step 4: implement the agreement

Within a week:

* Both dashboards relabeled to use the new names.
* Definitions added to the metrics doc or metrics layer.
* If the warehouse has a metrics layer (dbt metrics, Cube, etc.), encode the metrics there so everyone reads from one source.

The CEO now sees both numbers, both correctly labeled, no confusion.

### What if the teams disagree on which number gets the name "active user"?

Happens often. Product feels "active user" is theirs because they own engagement. Finance feels "active user" is the meaningful business number, so it should mean paying.

The resolution:

* Neither metric gets the bare name "active user." Both get specific names ("MAU" vs "paying users").
* In any executive dashboard, both numbers are shown with clear labels.

Refusing to give either team the generic name is the cleanest move. It forces precision in conversations.

### Step 5: the systemic fix

This problem happens because metrics are defined in dashboards, not in a shared layer. To stop it from recurring:

* Metrics layer. Every important metric is defined once, in code, with tests. Dashboards consume the metric; they don't redefine it.
* Metric registry. A page that lists every metric, its definition, and its owner. New metrics go through a quick review before being added.
* PR review for metrics. When someone adds a new metric, both data team and the business owner sign off.

With this in place, the next "active user" question never happens because there's no "active user", only "MAU" and "paying users," each with a defined home.

### What I would NOT do

* Pick a winner without the teams in the room. Whoever loses feels overruled. Now you have an enemy.
* Try to combine the two definitions into one. Frankenstein metrics please no one.
* Just tell the CEO "they're both right." That's true but unhelpful. They need a resolution.
* Spend a quarter building a metrics layer without addressing this week's question. Ship the rename now; build the layer over the next month.

### The cultural side

The data team gains credibility by being the neutral arbiter. We don't pick teams. We make the data visible and help people see what they're arguing about. After this conversation, both teams trust us a bit more.

A failure mode: getting drawn into being "the team that decides who's right." That role poisons every later disagreement. Stay neutral. Surface, document, codify.

### Common mistakes interviewers want you to name

1. Telling the CEO one number is right. Then you have to defend a definition you don't own.
2. Letting each team keep their own private definition. Same metric, two numbers, forever.
3. Naming both metrics "active user." The confusion is in the name.
4. No follow-up in code. Verbal agreement, no metrics layer entry, repeats in six months.
5. Treating it as a math problem. It's a definition problem.

### Bonus follow-up the interviewer might throw

> *"What if neither team will budge and the CEO sides with one of them?"*

Implement what the CEO decides, but still create the second metric with a clear name and add it to the dashboard. The losing team's number doesn't disappear; it's just no longer called "active user." Six months later, the people who needed it will still ask for it under its new name, and the company will use both. Quiet wins.
