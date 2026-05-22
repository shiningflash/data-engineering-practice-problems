## Solution 43: Mixing Facts and Dimensions

### Short version you can say out loud

> Two problems. First, when a customer's address changes, every old order silently shows the new address. History is rewritten. Second, when a customer or product gets updated in any way, every row referencing them has to change, which is slow and locks the table. The fix is the boring textbook one: put the order facts in a fact table and the customer and product attributes in dimension tables, joined by surrogate keys. The "it is easier to query" argument is real but solvable with a single view on top of the star schema.

### The symptom, drawn out

```
The single wide orders table

order_id │ order_date │ customer_name │ customer_address    │ product_name │ amount
1001     │ Jan 2      │ Alice Tan     │ 12 Bukit Rd, SG     │ Widget A     │ 50
1002     │ Jan 5      │ Bob Khan      │ 5 Orchard Rd, SG    │ Widget B     │ 30
1003     │ Mar 1      │ Alice Tan     │ 12 Bukit Rd, SG     │ Widget A     │ 50

Now Alice moves to Malaysia. They update the row in the app DB.
The ETL re-runs the orders table from scratch.

order_id │ order_date │ customer_name │ customer_address    │ product_name │ amount
1001     │ Jan 2      │ Alice Tan     │ 8 Jalan Ipoh, MY    │ Widget A     │ 50  ← changed
1002     │ Jan 5      │ Bob Khan      │ 5 Orchard Rd, SG    │ Widget B     │ 30
1003     │ Mar 1      │ Alice Tan     │ 8 Jalan Ipoh, MY    │ Widget A     │ 50  ← changed

The January revenue by region report now shifts $50 from SG to MY.
But that order was placed and shipped in SG. The history is now wrong.
```

This is the classic SCD problem (Problem 10) in disguise. By denormalizing customer attributes onto the fact table, every change to a customer mutates the past.

### The fix

```
fact_orders                              dim_customer (SCD2)
─────────────────────────────────        ───────────────────────────────────
order_id (PK)                            customer_key (PK, surrogate)
order_date                               customer_id  (natural)
customer_key (FK to dim_customer)        name, address, country
product_key  (FK to dim_product)         valid_from, valid_to, is_current
amount

dim_product
─────────────────────────────────
product_key (PK, surrogate)
product_id (natural)
name, category, brand
valid_from, valid_to, is_current
```

When Alice moves, dim_customer gets a new row (Type 2). The old order rows still point to her old customer_key. The January revenue by region report is correct.

### Joining is the easy part

```sql
SELECT
  c.country,
  SUM(o.amount) AS revenue
FROM fact_orders o
JOIN dim_customer c
  ON c.customer_key = o.customer_key
WHERE o.order_date BETWEEN '2025-01-01' AND '2025-01-31'
GROUP BY c.country;
```

Two table join. Indexed. Fast. The result is the customer state **at the time of the order**, because that's what the surrogate key locked.

### The team's "but it's easier to query" argument

This is the part to address honestly, not dismiss.

The argument: analysts do not want to write joins. They want `SELECT * FROM orders` and be done.

The fix: **build a wide reporting view on top of the star schema.**

```sql
CREATE VIEW v_orders AS
SELECT
  o.order_id,
  o.order_date,
  c.name        AS customer_name,
  c.address     AS customer_address,
  c.country     AS customer_country,
  p.name        AS product_name,
  p.category    AS product_category,
  o.amount
FROM fact_orders o
JOIN dim_customer c ON c.customer_key = o.customer_key
JOIN dim_product  p ON p.product_key  = o.product_key;
```

Analysts query `v_orders`. It looks exactly like the old wide table. But the data underneath is correct: each row shows the customer and product **as they were at order time**.

You get the simplicity AND the correctness.

### Storage and write performance

The wide table is also worse for storage and writes, even before correctness comes up:

* **Storage.** Every order row repeats the customer's full name, address, and country. Millions of orders, gigabytes of redundancy.
* **Writes.** When a customer's email changes, you update one dimension row, not every fact row that references them. On large tables this is the difference between seconds and minutes.

In a column-store, the redundant fields compress well, so storage matters less. Writes still matter.

### When wide IS the right call

A few cases where I would intentionally denormalize:

* **Reporting marts** at the very last layer, where the join overhead matters and the dimensions are stable enough. The trick is to snapshot the dimension state at the time the fact is loaded, so history does not rewrite.
* **Single-purpose extract for a downstream tool** that does not understand joins (a legacy BI tool, an external partner).
* **Search indexes** (Elasticsearch, OpenSearch). Wide documents are the norm there.
* **Aggregation tables** that are themselves derivative ("daily revenue by country and product"). These do not have user-level identity, so SCD is not an issue.

In all of these, the rule is: the wide table is built **from** the star schema, not instead of it.

### The migration path

The team has a wide table. How do you fix it without breaking everyone:

1. **Build the star schema next to it.** dim_customer with SCD2, dim_product, fact_orders pointing at surrogate keys.
2. **Build `v_orders`** as a view on top, with the same column names as the old wide table.
3. **Sanity-check** that `v_orders` matches the old wide table for current customers and products. It should, except for some historical rows where the dimensions have changed since.
4. **Repoint analyst queries** at `v_orders`. Most do not have to change SQL.
5. **Deprecate the old wide table.** Drop it once you are sure no one reads it directly.

The whole thing takes a week or two for a real warehouse and pays off forever.

### Common mistakes interviewers want you to name

1. **Snapshot-of-the-day denormalization** (rebuild the wide table every night from current dimensions). Looks fine until someone asks "what about three months ago," and the answer is "today's customer attributes."
2. **One mega dimension.** Trying to fit every attribute on one user-dimension. Split if dimensions vary at different rates (a frequently-changing "preferences" dimension separate from a stable "demographics" dimension).
3. **Surrogate keys for fact tables.** Facts use their natural id (`order_id`). Surrogates are for dimensions.
4. **Joining on natural keys instead of surrogates.** Then SCD2 history breaks.

### Bonus follow-up the interviewer might throw

> *"What if the dimension is small (say, 100 rows) and rarely changes?"*

Then denormalizing onto the fact is fine, with one rule: do it at fact-load time, snapshotting the dimension value, and never recompute. That way history is preserved even though you skipped the join.

In practice, very few dimensions are actually stable. Customer and product almost always change. So I would still keep them as dimensions and use a view if joins feel painful.
