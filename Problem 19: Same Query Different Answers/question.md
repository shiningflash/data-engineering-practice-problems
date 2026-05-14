## Problem 19: Same Query, Different Answers

**Scenario:**
You have one SQL query. You run it in development against a copy of yesterday's production data. It returns 142,500 rows. You run the exact same SQL in production. It returns 138,920 rows. The team is told "the data is the same." Something is off, and it is not obvious where.

In the interview, the question is:

> The same query gives one answer in dev and a different answer in production, even though the data is supposed to be identical. What kinds of bugs would you check for?

This is a "be systematic" question. The interviewer wants to see your debugging instincts.

---

### Your Task:

1. List the categories of reasons this can happen.
2. Walk through how you would actually check each one.
3. Explain why this kind of bug is so common.

---

### What a Good Answer Covers:

* The data is not actually the same.
* Time zone differences.
* Late-arriving rows.
* Different SQL dialects / casing / collation.
* Session settings (date format, time zone, character set).
* Sampling, table partitions, materialized views.
* Permission filtering on production (row-level security).
