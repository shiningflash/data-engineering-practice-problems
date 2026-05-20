## Problem 36: Scheduled Pipeline, Pay Only When It Runs

**Scenario:**
A small team has a daily Python ETL that takes about 15 minutes to run. They want it on a schedule (daily at 4 AM), but they want to pay only when it runs. They are price-sensitive and the script today runs on a small VM that sits idle 23 hours a day.

In the interview, the question is:

> A team wants their pipeline on a schedule but only wants to pay when it runs. What options do you give them, and what are the trade offs?

---

### Your Task:

1. List the practical options on AWS and GCP.
2. Compare them on cost, simplicity, and limits.
3. Pick one for the scenario.
4. Mention when the picture changes (longer jobs, more frequent runs, more steps).

---

### What a Good Answer Covers:

* EventBridge + Lambda; Cloud Scheduler + Cloud Function; Cloud Run Jobs.
* The 15-minute Lambda limit.
* AWS Batch / Step Functions; GCP Workflows.
* When to step up to Airflow / Dagster.
* Idle-cost math: the VM was costing $20/month; the function will cost cents.
