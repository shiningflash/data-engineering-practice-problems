## Solution 33: Executive Needs a Number Tomorrow

### Short version you can say out loud

> Execs in a time crunch need a defensible number plus the smallest possible set of caveats. I always ship a number. I never ship a wall of disclaimers. I ask one quick question to make sure I'm answering the right one, run the cleanest version of the analysis I can in the time I have, and deliver the number with two or three sentences of context. After the meeting, I follow up with a clean rebuild and tell them if it changes.

### The conversation, before any SQL

When the CFO calls, the first move is to scope the question, not to start coding.

> "Quick clarification before I run this. By 'CAC by channel,' do you want it gross (all marketing spend per acquired customer) or net of partner reimbursements? And by 'last quarter,' Jan-Mar or your fiscal Q1?"

Two questions, one minute. Saves an hour later.

I'd also ask what confidence they need:

> "I can give you a directional number by 7 PM that's good to plus or minus 5 percent, or a tighter number tomorrow at noon. Which one do you need?"

Most of the time, "directional tonight" is the answer. The exec needs a number to talk to the board, not to file with the SEC.

### What I ship

One number per channel, plus a comparison metric they'll want next.

```
Channel        CAC last quarter   vs last year
─────────────────────────────────────────────
Paid Search          $42                +12%
Social               $61                +18%
Affiliate            $28                -4%
Referral             $9                 +2%
Organic              $3                 -1%
                  ─────────
Blended              $34                +9%
```

The "vs last year" is unsolicited but always asked next. Saves the second round.

### The caveats, kept short

I write a separate short note alongside the number. Two or three bullets. No more.

> Method: total spend in channel divided by new customers attributed to that channel, last-touch model. Source: marketing.spend_daily and analytics.customer_acquisition.
>
> Two things to know:
>
> 1. April had a 3-day gap in social ad spend ingestion. I filled it using the daily run-rate average. Impact is probably plus or minus $2 on the social CAC. The underlying issue is being addressed.
> 2. Finance attributes a few large referral bonuses on a different basis. The number above is the analytics team view; finance's version of "referral CAC" is around $11. We're aligning the methodology next week.

The principle: enough caveats that the CFO doesn't get blindsided when finance pushes back, not so many that the number looks unreliable.

### What I would not do

* Refuse to give a number. "The data is messy" is true and useless to a CFO at 4 PM.
* Bury caveats inside the analysis. They never get read.
* Make up a clean methodology I haven't used before. No surprises today. Use the existing model, flag where it disagrees with finance.
* Send the SQL and let them figure it out. Send a number with one clean table.
* Promise a more precise number than I can deliver. A wrong number tomorrow is worse than an honest one tonight.

### How I think about "the data is wrong"

Two categories of data quality issues:

* Quantitative. Missing rows, broken ingestion, late data. Often fixable with simple imputation or backfill. I disclose the imputation but I still ship.
* Methodological. Different teams compute the same metric differently. Last-touch vs multi-touch attribution. Net vs gross spend. I can't fix this in an evening. I disclose the methodology I used, name the alternative, and offer to align next week.

Both get a one-line caveat. Neither stops me from shipping.

### The follow-up after the meeting

The next morning, after the board update is over, two things happen:

1. I clean up the analysis properly. Rerun against the corrected data, document the methodology, write it up.
2. I tell the CFO if anything changed. "Yesterday's number was $42 for paid search. After the proper backfill, it's $41.20. The story is the same." This builds trust for the next time.

Equally important, I file a ticket for the longer-term fix on the data quality issue. The April ingestion gap probably has a root cause; we should find it.

### What if the data really can't give a defensible answer

Sometimes the gap is too large. The honest move is to say so, constructively.

> "I can't give you a CAC by channel with confidence tonight because the April spend ingestion has a 14-day gap. I can give you:
>
> - CAC by channel for the previous quarter, which is clean.
> - A blended CAC for the current quarter, which I'm confident in (channels aside, the totals are right).
>
> Which would be more useful for the board?"

This is still shipping a number, just a different one. It also surfaces the underlying issue without sounding like an excuse.

### The conversation if finance challenges the number

In the meeting, finance may say "our CAC for referrals is $11, not $28." Two outcomes:

1. They're using the same data with a different methodology. Both are defensible. The next slide should reconcile.
2. One of us is on broken data. Probably the team that hasn't reconciled in a while. We compare.

Either way, the conversation is calmer because I already flagged this in the caveats. The CFO isn't surprised.

### Common mistakes interviewers want you to name

1. Sending raw SQL or notebooks to an exec. They won't read it.
2. Wall of disclaimers. Makes the number look untrustworthy.
3. Refusing to provide a number. Looks like obstruction to the business.
4. Overpromising precision. "$41.78 paid-search CAC" implies a precision the data doesn't have.
5. No follow-up. The exec uses the number forever; you never came back to check.

### Bonus follow-up the interviewer might throw

> *"What if the CFO uses the number in a board document and then a more accurate number turns out to be different?"*

Tell them as soon as you know, before they hear it from someone else. The script:

> "Quick correction: the CAC number I sent you Tuesday was $42 for paid search. The cleaner rebuild this morning gives $39. The change is within the plus or minus 5% I quoted, and the channel rankings are unchanged. If anyone asks, the numbers are now in [link]."

Owning the change builds credibility. Hoping nobody notices destroys it.
