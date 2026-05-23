---
id: 27
title: Year in Review Recap
category: System Design
topics: [batch, KV store, CDN, image render]
difficulty: Medium
solution: solution.md
---

# Problem 27, Year in Review Recap

**Scenario:**
Every December, almost every consumer app sends out a "your year in review" recap: top songs, favorite artists, total kilometers driven, money saved, hours focused. They roll out to hundreds of millions of users in a short window and need to feel personal and beautiful, but be cheap to generate at scale.

In the interview, the question is:

> Sketch the architecture behind those "your year in review" recaps almost every consumer app sends in December.

---

### Your Task:

1. Decide whether this is real-time or batch.
2. Sketch the pipeline from raw event history to a personalized recap.
3. Decide the storage and serving model.
4. Cover the social-share angle (deep link, image generation).
5. Mention the rollout strategy.

---

### What a Good Answer Covers:

* This is a batch problem, with a serving cache.
* Aggregation over a year of events, per user.
* The pre-rendered image / video for sharing.
* Personalisation as a deterministic function of features.
* The "everyone opens it within 48 hours" load spike.
