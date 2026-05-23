## Solution 37: BigQuery vs Snowflake for a New Team

### Short version you can say out loud

> Both are excellent. For a brand-new team that just wants to be productive, the choice usually comes down to which cloud you're already on, and which pricing model fits your usage shape. BigQuery is best when you're on GCP and your usage is bursty (pay per byte scanned). Snowflake is best when you want cloud-agnostic, multiple tightly isolated compute environments, and a steady predictable workload. For a 50-person startup with no warehouse today, I'd default to BigQuery if they're on GCP, Snowflake if they're on AWS or multi-cloud. Either choice is hard to regret.

### The honest comparison

| Dimension | BigQuery | Snowflake |
| ------------------------------- | --------------------------------------- | --------------------------------------- |
| Cloud | GCP only | AWS, GCP, Azure |
| Pricing model (default) | On-demand bytes scanned | Per-second of warehouse uptime |
| Reserved option | Slots (committed capacity) | Capacity contracts |
| Time to first query | Minutes (just create a dataset) | Minutes |
| Compute isolation | Reservations + workload management | Multiple virtual warehouses (best in class) |
| Concurrency for many users | Good (with slots) | Excellent (size each warehouse independently) |
| Scaling on huge scans | Excellent (auto) | Excellent (resize warehouse) |
| Storage | Cheap, separate billing | Cheap, separate billing |
| ML in-database | BigQuery ML, very integrated | Snowpark, Snowflake Cortex |
| Streaming ingest | Streaming inserts, Storage Write API | Snowpipe, dynamic tables |
| Marketplace and sharing | Analytics Hub | Data Marketplace, native sharing |
| Lock-in | Tied to GCP | Portable across clouds |
| dbt support | Excellent | Excellent |

The features list is almost a draw. The real differences are the pricing shape and the operational model.

### Pricing shape, in plain words

BigQuery on-demand. You pay for the bytes the query scans. A 100 GB scan costs about $0.625 (US on-demand). Idle costs $0 for compute. Storage is separate, about $0.02/GB/mo for active, less for long-term.

Snowflake. You pay for the seconds a virtual warehouse is running. A "small" warehouse costs about $2/credit/hour-ish; it auto-suspends after a configurable idle (1 minute default). Storage is separate, about $0.023/GB/mo.

Two different cost shapes:

* BigQuery rewards spiky usage. If your team queries actively for 2 hours a day and nothing else, you pay only for those queries.
* Snowflake rewards steady usage. A warehouse sized appropriately and used continuously gives predictable cost.

For a small new team that doesn't yet know its query pattern, BigQuery on-demand has lower commitment. You truly pay per query. Snowflake is fine but you need to size warehouses and tune auto-suspend.

### Time to first useful dashboard

Both can get you there in a week. Slight edge to BigQuery if you're already on GCP, because IAM, projects, and identity are wired in. Snowflake is fast too but needs role configuration and a virtual warehouse plan from day one.

### What pushes me to Snowflake

* You're already on AWS or Azure. BigQuery is awkward outside GCP (egress costs, identity bridging).
* You expect many teams with very different workloads (heavy analysts, ML training, ad-hoc) and you want them on separate compute. Snowflake's per-warehouse model is built for this.
* You care about data sharing across organizations. Snowflake's native sharing is best in class.
* You want a single warehouse story across multiple clouds (some companies refuse vendor lock-in to one cloud).
* The team prefers a more conventional, predictable warehouse experience.

### What pushes me to BigQuery

* You're on GCP. Identity, billing, networking are all native.
* Storage and compute are decoupled cleanly. Idle is truly free.
* You like SQL-first ML (BQ ML is well integrated).
* The team will start small and might stay small. The on-demand model is forgiving.
* You need to query large public datasets (BigQuery has many; cost is just the scan).
* You like the no-cluster operational model: there's nothing to size, suspend, or resume.

### The pick for the scenario

A 50-person startup, no warehouse today. If they're on GCP, I'd default to BigQuery. The on-demand pricing forgives the team's early experimentation, and the operational model is the simplest (no clusters, no warehouse sizes, no auto-suspend tuning).

If they're on AWS or undecided, Snowflake. It doesn't pull them deeper into one cloud, and the per-warehouse model scales nicely as the team grows past the early phase.

### Things that look big but matter less than people think

* "Snowflake supports semi-structured better." True five years ago. Both have first-class JSON and arrays now.
* "BigQuery has BQ ML." True, but most ML in production isn't run inside the warehouse.
* "Snowflake has Snowpark." Useful for Python-in-warehouse, but if you really want Python, dbt + BigQuery or external compute is fine.
* "BigQuery is cheaper because storage is cheap." Both have cheap storage. The compute is where the bill is.

### When you might regret BigQuery later

* The on-demand bill grows unpredictable as the team grows. The fix is to switch to slot commitments. That's fine, but it's a project.
* The team needs strong workload isolation (one heavy job that ruins everyone else). Slots help, but Snowflake's per-warehouse isolation is more straightforward.

### When you might regret Snowflake later

* You ended up on GCP for everything else. Now your data plane is in a different cloud.
* Warehouse sizing turns into a small ops job. Not big, but non-zero.
* Idle cost from many small warehouses adds up if not watched.

### What does not change the answer

* "We need ML." Both have ML stories.
* "We need streaming." Both have streaming ingest.
* "We need data sharing." Both have it.
* "We need dbt." Both have it.

The deciding factors are pricing model fit and existing cloud.

### Common mistakes interviewers want you to name

1. Picking based on marketing. Both vendors have great marketing.
2. Ignoring the existing cloud. Cross-cloud egress is real money.
3. Comparing pricing without knowing the workload. Bytes scanned vs compute-second-up is apples and oranges without a usage pattern.
4. Picking the warehouse before the team can use it. dbt, BI tool, and orchestrator matter just as much.
5. Refusing to commit. "We'll start with both" is a way to never finish either setup.

### Bonus follow-up the interviewer might throw

> *"What about Databricks?"*

Different shape. Databricks is great when you have heavy Python / Spark / ML / streaming workloads alongside SQL. For a 50-person team starting with simple dashboards, it can feel heavy. BigQuery or Snowflake are simpler to onboard. Databricks shines when ML and data engineering dominate, not when reporting does. Many companies end up running Databricks plus a warehouse rather than choosing.
