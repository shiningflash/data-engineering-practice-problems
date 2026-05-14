## Problem 39: Managed Airflow vs Self Hosted

**Scenario:**
Your team is starting to run more than a handful of scheduled jobs and the cron-on-a-VM pattern is starting to crack. Someone proposes Airflow. The team can either self-host it on Kubernetes, or use a managed service like MWAA (AWS), Cloud Composer (GCP), or Astronomer. Some engineers say "managed is overkill, we know Kubernetes." Others say "let's not run database migrations in production." You are asked to call it.

In the interview, the question is:

> When does managed Airflow (MWAA or Cloud Composer) start to make sense over running your own, and when is it overkill?

---

### Your Task:

1. Describe the dimensions that matter.
2. Sketch the breakeven point.
3. Mention the alternatives that are not Airflow.
4. Give the rule of thumb for a small/medium team.

---

### What a Good Answer Covers:

* Operational overhead of Airflow: database, scheduler, workers, web server, secrets, upgrades.
* The cost of managed vs the cost of an on-call rotation.
* When Dagster or Prefect or even just Cloud Workflows might fit.
* Team size and DAG count thresholds.
