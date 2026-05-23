---
id: 32
title: Inheriting a Pipeline No One Owns
category: Scenarios
topics: [ownership, judgement, rewrite-or-not]
difficulty: Medium
solution: solution.md
---

# Problem 32, Inheriting a Pipeline No One Owns

**Scenario:**
You inherit a pipeline that has been running for two years. The engineer who built it has left. The team has shrunk. A new requirement comes in that touches a transform deep inside the pipeline, and you realise no one alive understands how it works. The schedule says it runs daily, and most days it succeeds. Sometimes it fails and someone restarts it. Now you need to change something and you do not know what you will break.

In the interview, the question is:

> A pipeline you built two years ago is still running, but the original team is gone. A new requirement breaks it. What is the first thing you do?

This is testing your judgment under ownership transfer. Lots of engineers get this wrong by either rewriting too eagerly or being too scared to change anything.

---

### Your Task:

1. Resist the urge to start coding immediately.
2. Walk through how you would learn the pipeline before changing it.
3. Sketch a minimal first change that proves you understand the system.
4. Cover how you would document as you go.

---

### What a Good Answer Covers:

* Read the code and the schedule before touching anything.
* Run it locally or in a sandbox to feel its behavior.
* Find the seams: where could you change without rippling?
* Test coverage as the first investment.
* Make the new requirement a small, reversible change.
