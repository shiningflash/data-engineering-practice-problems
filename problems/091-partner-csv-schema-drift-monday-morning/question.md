---
id: 91
title: Partner CSV, Schema Drift on Monday Morning
category: Batch Pipelines & Orchestration
topics: [schema drift, contracts, ingestion, partner data]
difficulty: Medium
interview_value: strong
learn_order: 91
series: senior-scenarios
solution: solution.md
---

# Problem 91, Partner CSV, Schema Drift on Monday Morning

**Scenario:**
You own a nightly ingestion job that pulls a partner's `customers.csv` file from their S3 bucket into your warehouse. The job has run cleanly for 14 months. Monday at 09:00 you walk in and downstream dbt models are red. The CSV loaded successfully but the third column, which has been `country` (values like "Sweden", "Bangladesh"), arrived this morning as `country_code` (values like "SE", "BD"). Nobody on the partner side mentioned a change. Three dashboards that group by country are now showing one bucket called "SE". Tomorrow's load runs in 22 hours.

In the interview, the question is:

> Walk me through how you stabilise this pipeline against schema drift. What do you do today, what do you build this week, and what changes so the next surprise from a partner is a Slack ping, not an outage.

---

### Your Task:

1. List what you do in the first 30 minutes, before touching the architecture.
2. Describe the durable design so the same situation does not need an engineer next time.
3. Cover the four detection layers that catch drift at different points.
4. Explain the contract side: what you ask the partner for, and what you guarantee them.

---

### What a Good Answer Covers:

* The split between immediate triage and durable fix.
* All-string landing as a buffer between source and warehouse.
* Schema diff against the previous run.
* Great Expectations or a custom validator on the landing layer.
* The data contract: SLA on advance notice, schema version field, named owner on both sides.
* The "fail loudly, never silently" rule for ingestion.
