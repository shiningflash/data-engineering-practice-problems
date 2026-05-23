---
id: 29
title: Daily Report Quietly Wrong for Two Weeks
category: Scenarios
topics: [incident, postmortem, comms, data quality]
difficulty: Medium
solution: solution.md
---

# Problem 29, Daily Report Quietly Wrong for Two Weeks

**Scenario:**
The daily revenue report has been wrong for the last two weeks. Nobody noticed because the numbers looked plausible. The finance team caught it during a month-end reconciliation when their hand-computed total did not match what the dashboard had been claiming. By the time you find out, decisions have already been made on the wrong data, including an exec presentation last Wednesday.

In the interview, the question is:

> A daily report has been wrong for two weeks but nobody noticed because the numbers looked plausible. How do you investigate, and what do you change so it never happens again?

---

### Your Task:

1. Walk through how you would actually investigate.
2. Explain what you would communicate, to whom, and when.
3. Describe what changes after this incident.
4. Cover the postmortem mindset.

---

### What a Good Answer Covers:

* The investigation itself: stop the bleeding first.
* Identifying the change that caused the divergence.
* Telling stakeholders early, even before you know the cause.
* Data quality checks that would have caught it.
* The cultural shift from "tests pass" to "data is right."
