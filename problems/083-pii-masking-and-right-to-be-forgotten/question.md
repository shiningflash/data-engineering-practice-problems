---
id: 83
title: PII, Masking, and Right-to-be-Forgotten
category: Data Modeling
topics: [PII, GDPR, masking, tokenisation]
difficulty: Medium
interview_value: must-have
learn_order: 81
solution: solution.md
---

# Problem 83, PII, Masking, and Right-to-be-Forgotten

**Scenario:**
Legal sent a "right to be forgotten" request: a user wants every record deleted. Your warehouse holds their email in 18 tables. Their email also appears in three dashboards. The compliance officer wants a one-line answer: "is it gone?" The CTO wants a longer answer: "and how do we make this take an hour next time, not a week."

In the interview, the question is:

> Walk me through how a data platform handles PII end-to-end: classification, masking, and right-to-be-forgotten deletes.

---

### Your Task:

1. Define PII and explain why a clear taxonomy matters.
2. Compare the three main protection techniques (masking, hashing, tokenisation) and where each fits.
3. Walk through the deletion playbook for a real RTBF request.
4. Cover the policies you can encode (row-level access, column policies, retention).

---

### What a Good Answer Covers:

* Direct identifiers vs quasi-identifiers vs sensitive attributes.
* Static masking (in storage) vs dynamic masking (at query time).
* Hashing being one-way vs tokenisation being reversible with a vault.
* Why aggregates and ML features still leak (k-anonymity, joinability).
* The deletion fan-out: source, snapshots, derived models, backups, logs.
* Retention policies that prevent the next RTBF from being a week-long project.
