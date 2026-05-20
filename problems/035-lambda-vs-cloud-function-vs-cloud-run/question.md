---
id: 35
title: Lambda vs Cloud Function vs Cloud Run
category: Cloud Decisions
topics: [serverless, AWS, GCP, runtime limits]
difficulty: Medium
solution: solution.md
---

# Problem 35 — Lambda vs Cloud Function vs Cloud Run

**Scenario:**
You need to deploy a small Python service. It reads a file from S3 (or GCS), validates and transforms it, and writes the result to BigQuery. It runs maybe 200 times a day. The team is on Google Cloud, but the file lands in an AWS bucket owned by a partner. The hiring manager wants to know if you can defend a cloud choice.

In the interview, the question is:

> Lambda vs Cloud Function vs Cloud Run for a small Python job. Talk through what would push you toward each.

---

### Your Task:

1. Explain the three options in plain words.
2. Walk through the dimensions you would compare them on.
3. Pick one for the scenario, and defend it.
4. Mention when you would actually pick the other two.

---

### What a Good Answer Covers:

* Event source matters: where does the trigger come from?
* Container vs zip / image vs source bundle.
* Cold starts and concurrency.
* Cost shape (per invocation, per second).
* Runtime limits (15 min Lambda, 60 min Cloud Function gen2, basically unbounded Cloud Run).
