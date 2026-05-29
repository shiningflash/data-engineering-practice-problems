## Solution 69: Normalization and When to Denormalize

### Short version you can say out loud

> Normalization is about removing redundancy so the same fact is stored in exactly one place. 1NF says no repeating groups in a single column. 2NF says no column depends on only part of a composite key. 3NF says no column depends on another non-key column. In practice, most OLTP designs aim for 3NF because it prevents update anomalies and saves space. You denormalize on purpose when reads are heavy, when joins are too expensive at scale, or when you want a write-once snapshot for audit. Almost every real system is mostly 3NF with a few denormalized hot paths.

### The three normal forms, with a tiny example

```
Not normalized (a single sheet of paper)
─────────────────────────────────────────
order_id │ customer_name │ items_bought             │ phones
1        │ Alice         │ apple, banana            │ 1234, 5678
2        │ Bob           │ apple                    │ 9999

Problems:
- "items_bought" is a list in one cell. Cannot filter or count cleanly.
- "phones" is a repeating group.
- Customer info repeats per order.
```

**1NF — each column holds one atomic value.**

```
order_id │ customer_name │ item       │ phone
1        │ Alice         │ apple      │ 1234
1        │ Alice         │ apple      │ 5678
1        │ Alice         │ banana     │ 1234
1        │ Alice         │ banana     │ 5678
2        │ Bob           │ apple      │ 9999
```

Now each cell is atomic. But notice the explosion: Alice's two items × two phones = four rows. That is the next problem.

**2NF — every non-key column depends on the entire primary key, not part of it.**

Imagine `(order_id, item)` is the composite key. `customer_name` does not depend on `item`, only on `order_id`. Same for `phone` (depends on customer, not on item). So we split:

```
orders                    order_items                customer_phones
──────────────────        ────────────────────       ───────────────
order_id │ customer       order_id │ item            customer │ phone
1        │ Alice          1        │ apple           Alice    │ 1234
2        │ Bob            1        │ banana          Alice    │ 5678
                          2        │ apple           Bob      │ 9999
```

**3NF — non-key columns depend only on the key, not on other non-key columns.**

Suppose `orders` also had `customer_address`. That depends on the customer, not on the order. So pull it out:

```
orders                    customers
──────────────────        ────────────────────────
order_id │ customer       customer │ address
1        │ Alice          Alice    │ 12 Bukit Rd
2        │ Bob            Bob      │ 5 Orchard
```

Now updating Alice's address means one row, not every order she ever placed. The "update anomaly" is gone.

### The benefits of 3NF

* **No redundancy.** The same fact is in one place.
* **No update anomalies.** Change a customer's address once, everywhere agrees.
* **No insertion anomalies.** You can have a customer without yet having an order.
* **No deletion anomalies.** Deleting Bob's last order does not lose Bob's address.

These are the bugs the rules were designed to prevent.

### When to denormalize on purpose

Real systems do denormalize, deliberately:

**1. Read performance at scale.**

A frequent query that joins five tables can be served from one wider table much faster. You eat write cost and storage to gain read cost.

**2. Historical snapshots.**

The order's shipping address at the time of the order should not change when the customer moves. So you copy the address onto the order at write time and never update it. This is normalized-thinking applied at write time, denormalized-looking at read time. It is correct.

**3. Aggregation tables in analytics.**

A `daily_revenue_by_country` table denormalizes raw orders into a small summary. Reads are fast, writes are append-only. The raw table still exists for audit.

**4. Document-shaped data.**

JSON and document stores embed related data. An `order` document might have an embedded `customer` and an array of `items`. Trade: faster reads, but updates that touch shared data are harder.

**5. Read replicas with materialized views.**

Sometimes you build a wide view on a replica for reporting. The OLTP side stays 3NF; the read side is denormalized for query shape.

### The scenario from the question

The engineer who wants customer name and address on every order row is partly right and partly wrong.

* **Right** to denormalize **shipping address** as it was at the time of the order. That is a snapshot, not redundancy.
* **Wrong** to denormalize the customer's current name and address. If they update their name, every old order would show the wrong name (Problem 43's bug, in disguise).

The 3NF design:

```
customers (customer_id, name, current_address)
orders    (order_id, customer_id, ship_address_at_order_time, ...)
```

Best of both: customer's current info in one place, the order's snapshot frozen forever.

### How this connects to OLTP vs OLAP

* **OLTP** (the live application database): leans 3NF. Writes are frequent and small; updating one row should not require touching many.
* **OLAP** (the warehouse): leans star schema, which is denormalized on purpose. Reads are huge and joins are expensive at scale; a fact table with snapshot dimensions is cheaper to query.

The same data lives in both shapes for different jobs. That is normal, not a bug.

### Beyond 3NF

* **BCNF** is a stricter version of 3NF. In practice nearly indistinguishable.
* **4NF and 5NF** address rare multi-valued and join dependency anomalies. You will not see these in most jobs.
* If somebody insists on 5NF in an interview, they are testing your patience.

### Common mistakes interviewers want you to name

1. **"Denormalize for speed"** without measuring. Often the join was not the bottleneck.
2. **Snapshot fields treated as live data.** Customer moves, old reports break.
3. **Comma-separated lists in a column.** Not 1NF. Causes endless pain.
4. **Over-normalizing the warehouse.** Five-way joins for every dashboard.
5. **Skipping foreign keys "because they're slow."** They prevent classes of bugs that cost far more than the lookup.

### Bonus follow-up the interviewer might throw

> *"What is your honest design rule of thumb today?"*

> "3NF for OLTP, star schema for the warehouse. Denormalize an OLTP table only when I have measured that the join is the bottleneck and I cannot fix it any other way. Snapshot the historical version of any value where 'what it was at the time' is the correct answer."

That sentence is what most senior engineers actually do. The rest is theory.
