## Solution 46: Region Suddenly Shows Zero Revenue

### Short version you can say out loud

> I work bottom up. Did the data even land for that region? If yes, did the transforms include it? If yes, did the dashboard's filter accidentally drop it? Nine times out of ten, one of three things: the source feed for that region was late or empty, the join to the dimension table dropped them because a code changed, or someone added a filter to the dashboard that excludes the new value. I check each layer in order and the bug shows up by elimination.

### The four layers I check, in order

```
1. Raw layer   : did the data arrive?
2. Curated     : did the data survive the transform?
3. Marts       : did the data survive joins to dimensions?
4. Dashboard   : did the data survive the dashboard's query/filter?
```

If a layer's number is zero and the layer below has data, the bug is in this layer. If the layer below has no data, drop one more level.

### Step 1: did the data land?

```sql
SELECT COUNT(*), SUM(amount) FROM raw.orders
WHERE region = 'ID'
  AND created_at >= CURRENT_DATE - INTERVAL '2 days';
```

Three outcomes:

* **Zero rows.** The data did not arrive. Check the source feed: is the partner sending, is the SFTP empty, is the Kafka topic dry? This is now a "data is missing" investigation, not a "dashboard is wrong" one. Most likely cause.
* **Normal row count.** The data is there. Move up.
* **Reduced row count.** Partial outage. Dig into when it stopped.

In about half of incidents, the answer is here. The data did not arrive.

### Step 2: did the curated layer include it?

```sql
SELECT COUNT(*), SUM(amount) FROM curated.orders
WHERE region = 'ID'
  AND order_date = CURRENT_DATE - 1;
```

If raw has data but curated does not, the transform dropped it. Common causes:

* The transform has a hard-coded list of regions and Indonesia is not in it.
* A new region code (`ID` becomes `IDN` or `ID-JK` for Jakarta) and the transform's CASE WHEN doesn't recognize the new value.
* The transform filters out test data and Indonesia's rows accidentally got flagged as test.

Look at the transform code (dbt model, SQL, whatever it is) and find any place that filters or maps the `region` column.

### Step 3: did the marts layer include it?

```sql
SELECT r.name AS region, SUM(o.amount) AS revenue
FROM marts.fact_orders o
JOIN marts.dim_region r ON r.region_key = o.region_key
WHERE o.order_date = CURRENT_DATE - 1
GROUP BY r.name;
```

If curated has Indonesia but marts does not, the join to `dim_region` dropped them. This is the SCD trap. Common causes:

* `dim_region` has been re-keyed and the old surrogate keys don't match.
* Indonesia's row was accidentally deleted or marked `is_active = false`.
* A new region was added but the SCD2 valid_to window expired for the old one.

Check `dim_region` directly:

```sql
SELECT * FROM marts.dim_region WHERE code = 'ID';
```

### Step 4: is the dashboard's filter wrong?

If marts is correct but the dashboard shows zero, the bug is in the dashboard's SQL or filter.

* Did someone add `WHERE region != 'ID'` while debugging?
* Is the dashboard filtering on a stale dropdown value?
* Is the dashboard reading from a different table than you think?

Inspect the dashboard's underlying query. Often there are extra filters injected by the BI tool that you don't see in the model.

### The most common causes I have seen

Ranked by how often they bite:

1. **Source feed late or empty.** Partner outage, scheduled job slipped, SFTP credentials rotated.
2. **A code value changed at the source.** Two letter to three letter ISO code. Filter drops them all.
3. **A new product launched that doesn't emit the region field correctly.** Region is null for those rows, dropped by the join.
4. **A time zone effect.** Indonesia's day rolled over differently than expected; "yesterday in UTC" misses them.
5. **A dimension table got rebuilt** and the surrogate keys changed underneath the facts.
6. **Someone changed the dashboard yesterday.** Check git history.
7. **Test data filter that accidentally matches real data.** "Filter where email like '%@test.com'" matches a real customer.

### The communication step

While investigating, I post:

> "Looking into the Indonesia revenue showing zero on the dashboard. Tracking it down now, will update in 30 min."

Even if I find it in 5 minutes, the early message lowers the panic. If 30 minutes pass and I still don't know, I post again with what I have ruled out so far.

### How I would set up to catch this faster next time

* **A per-region freshness check** on the marts table. Yesterday should have at least N% of the last week's average per region. Pages on big drops.
* **A schema drift detector** that flags new values in low-cardinality columns. Helps with the "two letter to three letter" failure.
* **Dashboard "as of" stamp** so I know if the dashboard is stale vs zero.

### What I would NOT do

* **Guess and fix in production.** Without confirming the layer, you might "fix" the dashboard while the real bug is in the source.
* **Add `OR region IS NULL`** as a quick patch. Hides the real issue.
* **Tell the business "it's a known issue, we'll look at it tomorrow."** A zero region looks bad. Take it seriously.

### Common mistakes interviewers want you to name

1. **Starting from the dashboard.** Bottom-up is faster.
2. **Trusting "the pipeline succeeded."** Tasks pass with empty input.
3. **Not checking source freshness.** Often the cause and the cheapest check.
4. **Editing dashboards without recording what changed.**
5. **No alert that would catch this automatically.**

### Bonus follow-up the interviewer might throw

> *"What if Indonesia is consistently 'zero' for the first few hours of every day, and then catches up?"*

That is a "late data" pattern, not a bug. The source for Indonesia is shipping data after midnight Jakarta time, so by your dashboard's "yesterday" cutoff in UTC, their data has not arrived yet. The fix is either to wait until Indonesia's data lands before computing the dashboard, or to mark the dashboard as "still loading for Indonesia" until the freshness check passes. Either is correct; the wrong move is to say "the data is wrong" because the timing is wrong.
