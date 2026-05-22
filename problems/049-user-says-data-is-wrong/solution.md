## Solution 49: User Says "The Data Is Wrong"

### Short version you can say out loud

> I treat "the data is wrong" as the start of a conversation, not the end. The first response acknowledges them and asks for the minimum information to act: which screen, which number, what they expected. From there I triage. If they can give me concrete details, I investigate. If they cannot, I either move on with a "we will check what we can" message, or I try to reproduce from common patterns. The trick is to be respectful of their time without spending a whole afternoon on something that may not be a real bug.

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

Four questions, no jargon. Most users answer 2-3 of them, which is enough.

### Why these four questions

* **Which page** narrows the problem to a specific table or query.
* **Which number** localizes it inside the page.
* **What they expected** is the most valuable piece. Often the data is correct and the user's expectation is wrong, or vice versa. Either way, the gap tells you what to investigate.
* **Filters** matter because the same number can be different under different filter combinations.

### Triage when the user has given useful detail

I run through the same hierarchy as Problem 46:

1. Did the data arrive in the source?
2. Did the transform include it correctly?
3. Did the mart serve it correctly?
4. Is the dashboard's query / filter doing what the user thinks?

For a user-reported issue, step 4 is the most common cause. The user is hitting an edge: a filter combination that excludes legitimate rows, a metric that includes refunds when they expected gross, a time zone different than they assumed.

### Categories of "the data is wrong"

After enough complaints, you start to see patterns:

| Complaint                                | Most common cause                                  |
| ---------------------------------------- | -------------------------------------------------- |
| "The number is too low"                  | Filter excludes legitimate rows; late data         |
| "The number is too high"                 | Refund logic; double-counted join; duplicates      |
| "It doesn't match what I see elsewhere"  | Different metric definition; different time zone   |
| "It is showing zero"                     | Source outage; bad join; permission filter         |
| "It changed since yesterday"             | History was rewritten (Problem 43); recompute      |
| "Some users are missing"                 | RLS or filter; deletion; classification logic      |

A rough mental classifier saves you time: read the complaint, pick the likely category, jump to the most likely cause.

### What if the user can't or won't give details?

Sometimes you get a one-line complaint and then silence. Two options:

**Option A: respectful close-out.**

> "Thanks for flagging this. Without more detail, we cannot reproduce the issue. If it happens again, the screenshot and the page name will help us look into it quickly. Closing this for now."

This is not dismissive when phrased right. You are being honest.

**Option B: try common patterns first.**

If the user is important (a senior stakeholder), run through the top 3 likely complaints on the page they last viewed. Pre-compute the answers. Reply with something like:

> "I checked the three most-viewed numbers on this page for yesterday and they reconcile to source. If you can point me at a specific one, I can dig further."

This shows effort and often surfaces an issue without their input.

### When to escalate

Three signals push me to escalate the investigation, not the user:

1. **Multiple users report the same vague thing.** That is a real bug, even if no one has the detail.
2. **The user is in finance or another sensitive function.** Numbers there really do need to be right.
3. **My own anomaly checks are red.** They are reporting something I already know is off.

In all three cases, I do not wait for clarification. I dig and tell them what I find.

### The communication while investigating

If I am investigating without clear detail, I post an interim:

> "I'm checking the page you mentioned. If I find the issue, I'll share what I found. If I don't, I'll let you know what I ruled out, in case it helps you reproduce."

This sets expectations and protects me from "you said you would look into this, what happened?" three days later.

### How to reduce these reports

The systemic fix is to make "what is this number" easier to self-answer.

* **Tooltips on every metric** explaining the definition (gross vs net, time zone, refresh schedule).
* **"Last refreshed" stamp.** Half of "data is wrong" complaints are "data is stale."
* **A "what does this number mean" link** to a doc that explains the metric, the source, the refresh cadence.
* **A "report a problem" button** that captures the page, filter, user, and time automatically.

The button alone often turns a vague complaint into a complete bug report.

### Common mistakes interviewers want you to name

1. **Asking the user to "explain the bug clearly."** Comes across as dismissive.
2. **Treating one vague report as a major incident.** Wastes hours; reduces credibility for the next real one.
3. **Treating one vague report as nothing.** Especially when the user is senior, this is risky.
4. **No template for the follow-up.** Each engineer asks different questions, the user gets confused.
5. **Closing without a clear status.** "Cannot reproduce, please re-open with details" is fine; silence is not.

### Bonus follow-up the interviewer might throw

> *"How would you build a self-service tool that helps users investigate themselves?"*

A few small things go a long way:

* A page that says "the data was last refreshed at HH:MM" and "next refresh expected at HH:MM."
* A "compare to last week" toggle on every dashboard. Users often spot drift before we do.
* A small "show source query" link that displays the SQL behind the chart. Tech-savvy users can investigate themselves.
* A "data quality status" page that aggregates the most recent test failures and ingestion lags.

Most users do not want to bother us. The reason they file vague complaints is that they have no other tool. Give them one.
