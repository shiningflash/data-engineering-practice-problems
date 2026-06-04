---
id: 97
title: Backfill 90 Days Without Blowing the Budget
category: Batch Pipelines & Orchestration
topics: [backfill, idempotency, partition replace, throttling]
difficulty: Hard
interview_value: strong
learn_order: 97
series: senior-scenarios
solution: solution.md
---

# Problem 97, Backfill 90 Days Without Blowing the Budget

**Scenario:**
Three weeks ago, the source team added a new column `signup_channel` to the events stream. You picked it up two weeks ago, and from then on, the warehouse has it populated. But for the 90 days before, the column is null. Product wants the historical period populated for cohort analysis. The naive plan, "just rerun the daily job for each of the 90 days," would cost about 90x a normal day. Your monthly warehouse credit budget is enough for one and a half days of that. Finance will not approve more. The board meeting is in nine days.

In the interview, the question is:

> Plan the backfill. What do you reprocess, what do you skip, how do you make it idempotent, and how do you keep it from killing the budget or the warehouse?

---

### Your Task:

1. Define what actually needs to be backfilled vs what does not.
2. Walk through chunked, idempotent processing for the affected period.
3. Cover throttling and how to pause/resume safely.
4. Explain how to verify the backfill is correct before you mark it done.

---

### What a Good Answer Covers:

* The "least work needed" framing: only the affected column.
* Partition-replace for idempotency.
* Running the backfill in chunks (e.g., 7 days at a time).
* Throttling against cost: stop if today's burn exceeds N% of daily budget.
* Resume-from-where-you-stopped, not start-over.
* A spot-check that proves the new column matches what daily would produce.
