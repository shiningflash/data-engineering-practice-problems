## Solution 49: User Says "The Data Is Wrong"

### Short version you can say out loud

> I treat "the data is wrong" as the start of a conversation, not the end. The first reply asks for the minimum I need to act: which screen, which number, what they expected. From there I triage. If they give me concrete details, I investigate. If they don't, I either move on with a "we'll check what we can" message, or I try to reproduce from common patterns. The goal is to respect their time without burning an afternoon on something that may not be a real bug.

### The first response

A short, structured reply:

> "Thanks for letting us know. To track this down, can you share:
>
> 1. Which page or report?
> 2. Which specific number looks wrong?
> 3. What did you expect it to be?
> 4. Any filters you had applied?
>
> A screenshot helps a lot if you can."

Four questions, no jargon. Most users answer 2 or 3 of them, which is enough.

### Why these four questions

* Which page narrows the problem to a specific table or query.
* Which number localizes it inside the page.
* What they expected is the most useful piece. Often the data is correct and the expectation is wrong, or the other way around. Either way, the gap tells you where to look.
* Filters matter because the same number can differ under different filter combinations.

### Triage when the user has given useful detail

I run through the same hierarchy as Problem 46:

1. Did the data arrive in the source?
2. Did the transform include it correctly?
3. Did the mart serve it correctly?
4. Is the dashboard's query and filter doing what the user thinks?

For a user-reported issue, step 4 is the most common cause. The user is hitting an edge: a filter combination that excludes legitimate rows, a metric that includes refunds when they expected gross, a time zone different from the one they assumed.

### Categories of "the data is wrong"

After enough complaints, you start to see patterns:

| Complaint | Most common cause |
| ---------------------------------------- | -------------------------------------------------- |
| "The number is too low" | Filter excludes legitimate rows; late data |
| "The number is too high" | Refund logic; double-counted join; duplicates |
| "It doesn't match what I see elsewhere" | Different metric definition; different time zone |
| "It is showing zero" | Source outage; bad join; permission filter |
| "It changed since yesterday" | History was rewritten (Problem 43); recompute |
| "Some users are missing" | RLS or filter; deletion; classification logic |

A rough mental classifier saves time: read the complaint, pick the likely category, jump to the most likely cause.

### What if the user can't or won't give details?

Sometimes you get a one-line complaint and then silence. Two options.

Option A, respectful close-out:

> "Thanks for flagging this. Without more detail, we can't reproduce the issue. If it happens again, the screenshot and the page name will help us look into it quickly. Closing this for now."

Not dismissive when phrased right. You're being honest.

Option B, try common patterns first.

If the user matters (a senior stakeholder), run through the top 3 likely complaints on the page they last viewed. Pre-compute the answers. Reply with something like:

> "I checked the three most-viewed numbers on this page for yesterday and they reconcile to source. If you can point me at a specific one, I can dig further."

Shows effort and often surfaces an issue without their input.

### When to escalate

Three signals push me to escalate the investigation, not the user:

1. Multiple users report the same vague thing. That's a real bug, even without the detail.
2. The user is in finance or another sensitive function. Those numbers do need to be right.
3. My own anomaly checks are red. They're reporting something I already know is off.

In all three cases, I don't wait for clarification. I dig and tell them what I find.

### The communication while investigating

If I'm investigating without clear detail, I post an interim:

> "I'm checking the page you mentioned. If I find the issue, I'll share what I found. If I don't, I'll let you know what I ruled out, in case it helps you reproduce."

Sets expectations and protects me from "you said you'd look into this, what happened?" three days later.

### How to reduce these reports

The systemic fix is making "what is this number" easier to self-answer.

* Tooltips on every metric explaining the definition (gross vs net, time zone, refresh schedule).
* A "last refreshed" stamp. Half of "data is wrong" complaints are "data is stale."
* A "what does this number mean" link to a doc that explains the metric, the source, the refresh cadence.
* A "report a problem" button that captures the page, filter, user, and time automatically.

The button alone often turns a vague complaint into a complete bug report.

### Common mistakes interviewers want you to name

1. Asking the user to "explain the bug clearly." Comes across as dismissive.
2. Treating one vague report as a major incident. Wastes hours and burns credibility for the next real one.
3. Treating one vague report as nothing. Especially when the user is senior, this is risky.
4. No template for the follow-up. Each engineer asks different questions, the user gets confused.
5. Closing without a clear status. "Can't reproduce, please re-open with details" is fine. Silence is not.

### Bonus follow-up the interviewer might throw

> *"How would you build a self-service tool that helps users investigate themselves?"*

A few small things go a long way:

* A page that says "the data was last refreshed at HH:MM" and "next refresh expected at HH:MM."
* A "compare to last week" toggle on every dashboard. Users often spot drift before we do.
* A small "show source query" link that displays the SQL behind the chart. Tech-savvy users can investigate on their own.
* A "data quality status" page that aggregates the most recent test failures and ingestion lags.

Most users don't want to bother us. They file vague complaints because they have no other tool. Give them one.
