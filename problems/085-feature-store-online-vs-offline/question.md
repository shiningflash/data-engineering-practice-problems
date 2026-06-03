---
id: 85
title: Feature Store, Online vs Offline
category: System Design
topics: [feature store, MLOps, online, offline]
difficulty: Hard
interview_value: strong
learn_order: 90
solution: solution.md
---

# Problem 85, Feature Store, Online vs Offline

**Scenario:**
The ML team trained a churn model on warehouse data: 90-day rolling average of orders, days since last order, plan tier. The model performs great offline. In production it under-performs and looks confused. After two weeks of debugging, the data engineer finds that the online inference path computes "days since last order" from a different table than the training pipeline, and the boundaries differ. The CTO asks why you do not have a feature store yet.

In the interview, the question is:

> What is a feature store, why does the online / offline split matter, and how do you handle training-serving skew?

---

### Your Task:

1. Define the offline store and the online store and what each is good at.
2. Explain training-serving skew and the two flavours (calculation skew, time skew).
3. Sketch a realistic feature store architecture (Feast, Tecton, Vertex AI Feature Store, or homegrown).
4. Cover point-in-time correctness and why it is the hard problem.
5. Compare buying vs building.

---

### What a Good Answer Covers:

* The offline store is the warehouse; the online store is a low-latency KV (Redis, DynamoDB, Bigtable).
* The shared feature definition that produces both consistently.
* "As of" joins for training that respect each row's timestamp.
* Real-time vs batch features and where streaming sits.
* Monitoring features for drift, the same way you monitor data.
