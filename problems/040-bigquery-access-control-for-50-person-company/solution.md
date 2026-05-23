## Solution 40: BigQuery Access Control for a 50 Person Company

### Short version you can say out loud

> Three principles. One: grant access to datasets, not to projects. Two: grant to Google groups, never to individual users. Three: put sensitive data (PII, finance, HR) in dedicated datasets with their own groups. On top of that, use service accounts for every pipeline, never personal credentials, and turn on audit logs so the auditor can see who looked at what. For 50 people, this is a one-week project, and it scales to 500.

### The dataset-as-unit model

BigQuery's natural permission boundary is the **dataset**. You can grant `roles/bigquery.dataViewer` on `analytics_marts` without exposing `hr_raw`. This is the building block.

```
Project: company-data
│
├── Dataset: raw_events             ── group: data-engineering@
├── Dataset: analytics_marts        ── group: analysts@
├── Dataset: customer_pii           ── group: pii-cleared@
├── Dataset: finance                ── group: finance-team@
├── Dataset: hr                     ── group: hr-team@
└── Dataset: sandbox                ── group: all-employees@ (read/write)
```

Each dataset gets a set of groups attached to it via IAM. Adding or removing a user is then a single change in the group.

### Why groups, never individuals

Imagine someone leaves the company. If you granted access to 12 individual users, you have to find every place that user appears. If you granted to groups, removing them from the group is one change.

Equally, hiring is one change: add the new analyst to `analysts@`.

The rule: **no `user:` bindings in IAM**. Only `group:` and `serviceAccount:`.

### The role tiers

For each dataset, the standard roles in BigQuery cover most cases:

| Role | What it does |
| ---------------------------------- | ------------------------------------------- |
| `bigquery.dataViewer` | Read tables |
| `bigquery.dataEditor` | Read + write tables |
| `bigquery.dataOwner` | All of the above + manage permissions |
| `bigquery.jobUser` (project-level) | Run queries (separate from data access) |
| `bigquery.user` (project-level) | Run queries + create datasets |

A typical analyst gets:

* Project-level: `bigquery.jobUser` (so they can run queries).
* Dataset-level: `bigquery.dataViewer` on `analytics_marts`, `bigquery.dataEditor` on `sandbox`.

That's it. No project-wide read.

### The groups, mapped to teams

```
data-engineering@          - all data engineers, dataEditor on raw_*, marts_*
analysts@                  - all analysts, dataViewer on analytics_marts
pii-cleared@               - small subset who have signed PII training, dataViewer on customer_pii
finance-team@              - finance team, dataViewer on finance
hr-team@                   - HR team, dataOwner on hr
all-employees@             - everyone, dataEditor on sandbox only
exec-team@                 - executives, dataViewer on marts and exec-only datasets
admins@                    - very small, project owners
service-accounts-prod@     - all production service accounts (kept separate)
```

Groups overlap. An analyst on the finance team is in both `analysts@` and `finance-team@`.

### Sensitive data: separate datasets, separate groups

Three categories of sensitive data:

1. **Customer PII.** Names, emails, phone numbers, addresses. Lives in `customer_pii` dataset. Access only via `pii-cleared@`, which requires a quick training and a manager request.
2. **Finance.** Revenue at line-item detail, payroll, contracts. In `finance` dataset. Access only via `finance-team@` and `exec-team@`.
3. **HR.** Compensation, performance reviews, personal data. In `hr` dataset. Access only via `hr-team@` and a few execs.

Each of these datasets is in the same project for convenience, but in a separate project is fine too if you want even harder isolation.

### Column and row-level security for the cases between

Sometimes you need "the analyst can see the customers table but not the email column." BigQuery has column-level security:

```sql
ALTER TABLE customer_pii.customers
ALTER COLUMN email
SET OPTIONS (
  policy_tags = [
    "projects/.../taxonomies/.../policyTags/pii_email"
  ]
);
```

Users without the `Fine-Grained Reader` role on that policy tag see `NULL` in that column.

Row-level security:

```sql
CREATE ROW ACCESS POLICY country_filter
ON sales.orders
GRANT TO ('group:apac-analysts@example.com')
FILTER USING (country IN ('SG','MY','ID','TH','VN'));
```

The APAC analyst only ever sees rows for those countries.

Use these sparingly. Coarse-grained dataset access is easier to reason about and easier to audit. Fine-grained access tags add complexity that pays off only for genuinely shared tables with sensitive columns.

### Pipelines and service accounts

Every production pipeline runs as a service account, never as a person. A few patterns:

* `sa-etl-prod@`, production ETL service account.
* `sa-ml-training@`, for model training.
* `sa-bi-tool@`, for the BI tool's queries.

Service accounts are members of relevant groups, just like users. The principle of least privilege still applies. The ETL service account does not need access to HR.

When a human queries the warehouse, they use their own identity. When a pipeline queries, it uses its own. You never share a service account key as a person.

### The rollout: how not to break anyone in week one

The danger is removing access too fast. People notice when their dashboards stop working. Plan:

**Week 1: discover.**

Pull the BigQuery audit logs for the last 30 days. Find every query and the dataset it touched.

```sql
SELECT
  protopayload_auditlog.authenticationInfo.principalEmail AS user,
  protopayload_auditlog.servicedata_v1_bigquery
    .jobCompletedEvent.job.jobStatistics.referencedTables[OFFSET(0)].datasetId AS dataset,
  COUNT(*) AS queries
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY user, dataset
ORDER BY user, queries DESC;
```

Now I know who actually needs access to what. Often you find that 80% of users only ever touch 2-3 datasets.

**Week 2: shadow.**

Create the new groups and dataset-level grants. Do NOT remove project-wide access yet. Now everyone has both project-wide and dataset-specific access. Nothing breaks.

**Week 3: cut over.**

Remove project-wide access in one stroke. Monitor audit logs. If someone screams, you know exactly who needs an additional group.

The "shadow then cut" is the trick. It is much safer than the reverse.

### Audit and access reviews

* Turn on **BigQuery Data Access** audit logs. They record every read of sensitive tables.
* Set up a saved query that reports "who read which sensitive table this week." Send it to a security channel.
* Run a **quarterly access review**: each group owner confirms the current member list.

For a 50-person company this is small overhead. For larger ones it becomes essential.

### Common mistakes interviewers want you to name

1. **Granting at project level.** Cannot revoke fine-grained access without breaking everything.
2. **Granting to individuals.** Permission sprawl.
3. **Same service account for many pipelines.** Hard to audit, blast radius too big.
4. **No audit log review.** Sensitive data access invisible.
5. **PII in shared datasets.** Once it's there, narrowing access later is much harder than starting clean.

### Bonus follow-up the interviewer might throw

> *"How would you handle a contractor who needs access for two weeks?"*

Add them to a "contractor" group with the specific dataset access they need, plus an automatic expiration. BigQuery has **conditional IAM bindings** that can include a time condition:

```yaml
binding:
  role: roles/bigquery.dataViewer
  members:
    - user:contractor@example.com
  condition:
    title: "Two-week access"
    expression: "request.time < timestamp('2025-06-01T00:00:00Z')"
```

After June 1, the binding becomes inert automatically. No one has to remember to revoke.
