---
id: 24
title: Spotify Minutes Listened This Week
category: System Design
topics: [streaming aggregation, KV store, watermarks]
difficulty: Hard
solution: solution.md
---

# Problem 24 — Spotify Minutes Listened This Week

**Scenario:**
A music streaming app shows "minutes listened this week" on every user's profile. Hundreds of millions of users open the app each day. Scanning the full play event history every time someone opens their profile would be impossibly expensive. The product team wants the number to be at most 5 minutes stale.

In the interview, the question is:

> Design how Spotify might compute "minutes listened this week" without scanning all play events every time someone opens the app.

---

### Your Task:

1. Estimate the read and write volumes at the scale described.
2. Pick a storage and update pattern.
3. Decide what "this week" means and how it rolls over.
4. Cover correctness in the presence of pauses, skips, and replays.
5. Mention how it stays fast at 200 million daily users.

---

### What a Good Answer Covers:

* A pre-aggregated counter per (user, week), updated incrementally.
* Streaming aggregation over play heartbeat events.
* The "what counts as a minute listened" definition.
* Week boundary handling and time zones.
* The serving store choice.
