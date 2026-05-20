---
id: 40
title: BigQuery Access Control for 50 Person Company
category: Cloud Decisions
topics: [IAM, datasets, groups, RLS, audit]
difficulty: Medium
solution: solution.md
---

# Problem 40 — BigQuery Access Control for 50 Person Company

**Scenario:**
A 50-person company has been giving everyone "BigQuery Data Viewer" on the entire project. Some data is sensitive (HR, finance, customer PII). The CTO asks you to fix the permissions before the next audit, without breaking anyone's daily work.

In the interview, the question is:

> How would you design access control across BigQuery datasets in a 50 person company with both sensitive and non sensitive data?

---

### Your Task:

1. Lay out the access model.
2. Show how it maps to BigQuery's actual roles and IAM concepts.
3. Cover the rollout: how do you not break anyone in week one.
4. Mention auditing.

---

### What a Good Answer Covers:

* Datasets as the unit of access, not the whole project.
* Groups, not individual users.
* Sensitive datasets isolated.
* Row-level and column-level security for fine cases.
* Service accounts for pipelines.
* Audit logs and access reviews.
