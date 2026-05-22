## Solution 39: Managed Airflow vs Self Hosted

### Short version you can say out loud

> Managed Airflow makes sense the moment Airflow stops being a side project for someone. Self-hosted is cheap until you count the engineer hours spent on the database, the scheduler, the upgrades, and the inevitable 3 AM scheduler hang. For a team with fewer than ~50 DAGs and no dedicated infra person, managed wins almost every time. For a large platform team that already runs Kubernetes well and has Airflow as part of their core product, self-hosted is reasonable. And for a small team starting today, I would consider not using Airflow at all.

### What "running Airflow" actually involves

Airflow is more than a Python library. It is a multi-process system:

```
Web server        Scheduler         Workers (Celery / Kubernetes)
       \             |                       /
        \            v                      /
         ▶  Metadata database (Postgres) ◀
                     |
                     v
              Logs (filesystem / S3)
              Secrets backend
              Plugins, providers, Python deps
              Upgrades, every few months
```

Each of these is a thing that breaks at some point. The scheduler in particular has a long history of needing tuning at scale (parsing performance, executor restarts, DB connection limits).

When the team is small, this is "someone's side job." That works for a while, then breaks at the worst time.

### When self-hosted is fine

* You already run Kubernetes and have an SRE team.
* You have 100+ DAGs and a custom plugin ecosystem.
* You need control over Python versions, providers, networking.
* You can afford one engineer's time on Airflow ops continuously.
* You want full IAM and network customization that managed services don't allow.

This is real for big companies. Airbnb runs it themselves. So do many large data platform teams.

### When managed is the right call

* The team is small (less than 10 data engineers).
* You have 5-100 DAGs.
* You do not have an SRE team that wants to own this.
* You want to focus on data, not infra.
* You can absorb the cost (typically $300-$1,500/month for small managed Airflow on MWAA / Composer).

For most companies under 200 people, this is the right answer.

### A rough cost picture

```
Self-hosted on Kubernetes (small)
  Cluster cost           : $300-700/mo
  Postgres for metadata  : $50-200/mo
  Engineer hours         : 5-20 hours/month at incident time
  Engineer hourly cost   : $50-150 (loaded)
  Real total             : ~$1,000-3,000/mo

MWAA / Composer (small)
  Service cost           : $300-700/mo
  Engineer hours         : 1-3 hours/month
  Real total             : ~$500-1,000/mo
```

The hidden cost of self-hosted is the engineer hours, especially during upgrades and incidents. Most teams underestimate this by 3-5x when they pitch self-hosted.

### When I would not use Airflow at all

Airflow is the default, but it is not always the right tool. For a small team starting today:

* **Cloud Workflows + Cloud Scheduler (GCP)** or **Step Functions + EventBridge (AWS)** for under 20 simple pipelines. No Airflow at all.
* **Dagster** if asset-centric thinking suits the team and they like declarative data lineage.
* **Prefect** if Python-first scripting suits the team.
* **dbt Cloud** for SQL-only workloads; it has its own scheduler.

For 5-20 DAGs with simple dependencies, Cloud Workflows or Step Functions cost almost nothing and have no operational burden.

### The deciding question

I would ask: "Do we want to run Airflow, or do we want our DAGs to run?"

If the answer is "we want our DAGs to run," managed Airflow or one of the alternatives is the right call. Self-hosting Airflow is a choice to invest in the tool, not just use it.

### A breakeven sketch

| DAGs | Team size | Recommendation |
| ---- | --------- | -------------- |
| 1-10 | 2-5 | Cloud Workflows / Step Functions, or dbt Cloud. Skip Airflow. |
| 10-50 | 5-15 | Managed Airflow (MWAA / Composer / Astronomer). |
| 50-200 | 10-30 | Managed Airflow, possibly evaluate Dagster. |
| 200-1000 | 20-50 | Managed if cost ok; consider self-hosted with dedicated owner. |
| 1000+ | 50+ | Self-hosted on Kubernetes, dedicated platform team. |

### What I would do for the scenario in the question

A team that has outgrown cron-on-a-VM. I would:

* Estimate the DAG count realistically. "How many in 6 months?"
* If under 50, recommend managed Airflow.
* If over 50, recommend managed Airflow plus a clear plan to keep DAG counts sane (use task groups, dynamic DAGs sparingly).
* Either way, push back against "let's self-host because we know Kubernetes." Knowing Kubernetes is not the same as wanting to own Airflow's quirks.

### Common mistakes interviewers want you to name

1. **Pitching self-hosted because the team likes infrastructure.** Hobby vs job.
2. **Picking Airflow when a few Step Functions would do.** Operational overhead for nothing.
3. **Not counting upgrade cost.** Airflow 1 to 2 to 2.x has been painful.
4. **Forgetting the metadata DB needs backups and tuning.**
5. **"Managed is too expensive."** When the engineer time is counted, often the other way around.

### Bonus follow-up the interviewer might throw

> *"What is the case for Dagster over Airflow today?"*

Dagster is asset-centric: you define the data you want to exist, and Dagster figures out how to keep it fresh. Airflow is task-centric: you define tasks and their dependencies. The Dagster model often matches how teams actually think about data ("the orders mart should be fresh by 8 AM") more cleanly than Airflow's "run this task." For a new project, Dagster is genuinely worth evaluating. For a team migrating away from existing Airflow pipelines, the cost of switching paradigms is usually higher than the benefit.
