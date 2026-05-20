---
id: 38
title: Store Partner Files in S3 or Warehouse
category: Cloud Decisions
topics: [S3, raw layer, audit, schema evolution]
difficulty: Easy
solution: solution.md
---

# Problem 38 — Store Partner Files in S3 or Warehouse

**Scenario:**
A partner sends 50 large CSV files every day, totaling about 30 GB. They arrive on SFTP. A team member is pushing to load all of them straight into the warehouse. Another team member says "keep them in S3, load only what we need." You are asked to mediate.

In the interview, the question is:

> A team is debating whether to store partner files in S3 or load them straight into the warehouse. What questions do you ask before answering?

This is a "how do you think" question. The right answer is rarely one-or-the-other; it's usually "both, in a sensible order."

---

### Your Task:

1. List the questions you would ask first.
2. Explain the standard pattern (land in object storage, then load).
3. Pick the right answer for the scenario.
4. Cover the cases where you would deviate from the default.

---

### What a Good Answer Covers:

* Raw vs curated layering.
* Schema evolution and reprocessing.
* Cost of warehouse storage vs object storage.
* Audit and immutability.
* When you really do load straight to the warehouse.
