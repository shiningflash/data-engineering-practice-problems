---
id: 46
title: Region Suddenly Shows Zero Revenue
category: Debugging
topics: [dashboard, joins, SCD, time zones]
difficulty: Medium
solution: solution.md
---

# Problem 46 — Region Suddenly Shows Zero Revenue

**Scenario:**
The daily revenue dashboard shows total revenue across regions. Today, one region — say, Indonesia — shows zero. The other regions look normal. Yesterday Indonesia showed $X. The business hasn't shut down operations there.

In the interview, the question is:

> Your daily revenue dashboard suddenly shows zero for one region. Walk me through your investigation step by step.

---

### Your Task:

1. Resist the urge to guess. Walk through the actual diagnostic steps.
2. Show what you check first, second, third.
3. Cover the most common causes.
4. Mention the communication step.

---

### What a Good Answer Covers:

* Bottom-up: did the data even arrive?
* Middle: did the transforms include it?
* Top: did the dashboard's query filter it out?
* Source vs warehouse vs dashboard.
* The common culprits: filter typo, dimension change, source outage, time zone.
