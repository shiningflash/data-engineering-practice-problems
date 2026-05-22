## Solution 64: Breaking Change in a dbt Model With 200 Consumers

### Short version you can say out loud

> I treat it like an API change in software. Add the new column first, leave the old one in place, communicate the deprecation with a clear deadline, give consumers time to migrate, then remove the old one. Never remove and rename in the same release. The whole rollout takes 4 to 8 weeks for 200 consumers. The discipline is what saves you, not the cleverness of the change.

### The four phases

```
Phase 1   Add the new column alongside the old one        Week 0
Phase 2   Communicate deprecation with a deadline         Week 0
Phase 3   Wait while consumers migrate                    Weeks 1 - 6
Phase 4   Remove the old column                           Week 6 - 8
```

### Phase 1: add, don't replace

The model gets both columns. The new one is populated correctly; the old one is computed for compatibility, possibly as an alias.

```sql
-- in the dbt model
SELECT
  ...
  amount_cents AS amount_cents,        -- new column, the right name
  amount_cents AS amount,              -- old column, deprecated alias
  ...
FROM ...
```

A single dbt run, no consumer breaks. Consumers can use the new name when ready.

If the change is more than a rename — say, a units change from dollars to cents — the alias is more complex but still possible:

```sql
SELECT
  ...
  amount_cents          AS amount_cents,    -- new (integer cents)
  amount_cents / 100.0  AS amount_dollars,  -- old (float dollars)
  ...
```

Both are correct and identifiable. Consumers can move at their pace.

### Phase 2: communicate

Three things happen the day the alias ships:

**1. Mark the column as deprecated in dbt.**

```yaml
models:
  - name: fact_orders
    columns:
      - name: amount
        description: |
          DEPRECATED. Use `amount_cents` instead.
          Will be removed on 2025-07-01.
        meta:
          deprecated: true
          deprecated_at: '2025-05-15'
          remove_at: '2025-07-01'
```

dbt's docs page now shows the deprecation. Anyone hovering over the column sees the message.

**2. Send a clear announcement.**

```
Subject: `fact_orders.amount` will be removed on July 1, 2025.

Hi all,

We're cleaning up `fact_orders`. Today's release adds `amount_cents`
(integer cents, the right one), and renames the existing
`amount` (float dollars) as deprecated.

Action you need to take:
- Switch any code reading `amount` to `amount_cents` before July 1.
- The old column will be removed on that date.
- I have generated a list of consumers that reference `amount` and
  will follow up with the owners individually.

Timeline:
- May 15: both columns available.
- June 1: friendly reminder, list of remaining users.
- June 22: final 10-day warning.
- July 1: `amount` removed.

Questions: drop them in #data-platform.
```

Specific, dated, action-oriented.

**3. Identify the consumers and their owners.**

dbt's `exposures` and the column-level lineage tools (dbt's `--select` with column flags, or third-party tools like dbt-cloud, Castor, SelectStar) tell you exactly which models, dashboards, and pipelines read `amount`. Make a list. Find the owner of each one. Either notify the owner directly or open a small PR / ticket for them.

For 200 consumers, this list will probably reveal:

* 30 dbt models — easy to migrate, possibly one PR.
* 80 dashboards — usually a quick rename per dashboard.
* 30 reverse ETL jobs — straightforward config update.
* 60 ad-hoc reports / scheduled queries / one-off bookmarks — the long tail.

The first three groups migrate in week one. The long tail is what the deprecation window protects.

### Phase 3: wait, nudge, monitor

For four to six weeks, both columns exist. Things to do:

* **Monitor usage.** Run a periodic check of `INFORMATION_SCHEMA.JOBS_BY_PROJECT` (BigQuery) or query history (Snowflake) for references to `amount`. Send a personalized reminder to anyone still using it.

```sql
SELECT user_email, COUNT(*) AS uses
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND REGEXP_CONTAINS(query, r'\bamount\b')
  AND NOT REGEXP_CONTAINS(query, r'amount_cents')
GROUP BY 1
ORDER BY 2 DESC;
```

* **Send the reminders on schedule.** Week 2, week 4, week 5, last week. Each reminder includes the remaining list.
* **Help the slow migrators.** Open the PR for them if they need help.

### Phase 4: remove

When the deadline arrives:

* Remove the old column from the dbt model.
* Run a final usage check. If anyone is still using it, decide: extend by a week, or break them with notice. The right call depends on who is still using it.
* Merge, deploy, watch for breakage.

If you have done the previous phases well, removal day is uneventful. That is the goal.

### Tests that catch breakage

In the dbt project, you can include a test that checks the model still has the new column and the old one is gone:

```yaml
- name: fact_orders
  columns:
    - name: amount_cents
      tests:
        - not_null
```

For consumers, the protection is theirs to add. Encourage them to add explicit column-existence tests on their critical dashboards.

### What if a senior stakeholder says "we cannot break the dashboard"?

Then you do not break the dashboard. The deprecation window exists for a reason. If after 6 weeks they still cannot migrate, you negotiate: maybe a quick PR you write for them, maybe a 2-week extension, maybe they accept a brief outage if not.

The leverage is the deadline. Without one, consumers never migrate.

### Why "rename and remove in the same release" fails

Doing it in one shot has two failure modes:

1. **You break consumers all at once.** Dashboards, jobs, reports go red on Monday morning.
2. **You undo the change in panic.** Now the dbt history has both versions and nobody trusts the change.

The deprecation pattern is annoying because it requires patience, but it is the only safe way at this scale.

### Tools that help

* **dbt's exposures**: declare downstream consumers (dashboards, reports) in the dbt project. Lineage now includes them.
* **dbt's docs page**: shows deprecation info if you put it in the schema YAML.
* **Column-level lineage tools** (Castor, SelectStar, Atlan): find every place a column is used.
* **Query history mining**: a script reading INFORMATION_SCHEMA.JOBS_BY_PROJECT to find references.

### Common mistakes interviewers want you to name

1. **Rename in one PR.** Breaks everyone simultaneously.
2. **No deadline.** Migrations drag on forever.
3. **No owner per consumer.** Reminders go nowhere.
4. **No usage monitoring.** Deadline arrives, surprises everyone.
5. **Removing without final notice.** Even with notice, the last warning matters.

### Bonus follow-up the interviewer might throw

> *"What if you cannot keep the old column as an alias because the new logic is fundamentally different?"*

Then you create a new model, not a new column. `fact_orders_v2`. Both `fact_orders` and `fact_orders_v2` exist for the deprecation window. The communication is the same shape: announce, deadline, migrate, deprecate, remove. The cost is two models in parallel for a few weeks; the safety is that nothing breaks unexpectedly.
