## Solution 15: Teaching SQL Performance to a Junior

### Short version you can say out loud

> I would not start by rewriting their query. I would sit with them, run EXPLAIN, and let them see where the time is going. Most slow queries come from one of four causes: scanning too much data, joining too early, filtering with a function on the indexed column, or asking the database to sort more than it needs to. I walk them through those four, in that order, and they almost always find it themselves. The job is to give them the lens, not the answer.

### The mental model I would teach them

```
A SQL query has two costs:
  1. How much data the engine touches.
  2. How much work it does per row.

Optimization is mostly about touching less data.
The rest is helping the engine pick the right plan.
```

Then I would teach four habits, in this order.

### Habit 1: Read EXPLAIN before guessing

The first lesson: do not optimize from intuition. Read the plan.

```sql
EXPLAIN ANALYZE
SELECT ...
```

What I would show them on the plan:

* **The biggest box on the left.** That is where the time went. Look there first.
* **"Seq Scan" or "Full Table Scan."** The engine read the whole table. Why? Often there is no index, or the WHERE used a function that hid the index.
* **The estimated vs actual row counts.** If they are wildly different, the optimizer is making bad decisions because its stats are wrong. Often fixed by `ANALYZE`.
* **Nested loop join over millions of rows.** Almost always wrong. Should be hash join or merge join.

### Habit 2: Filter early, project narrow

Most beginners write queries like this:

```sql
-- Slow
SELECT *
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.created_at > '2025-01-01';
```

And then complain that it is slow.

I rewrite it with them like this:

```sql
-- Fast
SELECT o.id, o.amount, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.created_at > '2025-01-01';
```

The two lessons:

1. `SELECT *` reads every column. In a column store like BigQuery, this scans 10x more data than you need.
2. Always think about which side of the join is filterable. The engine can push the date filter down on `orders`, shrink that side, then join. If you filter after the join, both sides got fully read first.

### Habit 3: Do not wrap indexed columns in functions

This is the single most common slow query in a junior's code:

```sql
-- Slow
WHERE DATE(created_at) = '2025-05-14'

-- Fast
WHERE created_at >= '2025-05-14' AND created_at < '2025-05-15'
```

Why the first is slow: the index on `created_at` is on the raw timestamp values. `DATE(created_at)` is a function applied to every row, so the engine cannot use the index. It has to read every row, compute `DATE(...)`, and compare. The second version uses range comparisons directly on the indexed column.

The same lesson hits with `LOWER(email) = '...'`, `CAST(id AS TEXT) = '...'`, `SUBSTR(name, 1, 3) = '...'`. Functions on indexed columns kill the index.

### Habit 4: Aggregate before you join, when you can

```sql
-- Slow: joins billions, then aggregates
SELECT c.country, SUM(o.amount)
FROM orders o
JOIN customers c ON c.id = o.customer_id
GROUP BY c.country;

-- Sometimes faster: aggregate first, then join the small result
WITH per_customer AS (
  SELECT customer_id, SUM(amount) AS total
  FROM orders
  GROUP BY customer_id
)
SELECT c.country, SUM(p.total)
FROM per_customer p
JOIN customers c ON c.id = p.customer_id
GROUP BY c.country;
```

This is not always faster, and modern optimizers may do this automatically. But teaching the pattern is useful, because it makes the junior think about *what shape of data* they are passing to each step.

### A real before / after I would walk them through

```sql
-- Original (8 minutes)
SELECT
  o.id,
  c.name,
  ROW_NUMBER() OVER (PARTITION BY c.country ORDER BY o.amount DESC) AS rn
FROM orders o
JOIN customers c ON c.id = o.customer_id
JOIN regions  r ON r.country = c.country
WHERE EXTRACT(YEAR FROM o.created_at) = 2025
  AND r.active = true;

-- After teaching the habits (4 seconds)
WITH active_orders AS (
  SELECT id, customer_id, amount
  FROM orders
  WHERE created_at >= '2025-01-01' AND created_at < '2026-01-01'
)
SELECT
  ao.id,
  c.name,
  ROW_NUMBER() OVER (PARTITION BY c.country ORDER BY ao.amount DESC) AS rn
FROM active_orders ao
JOIN customers c ON c.id = ao.customer_id
JOIN regions  r ON r.country = c.country AND r.active = true;
```

What changed:

* `EXTRACT(YEAR FROM created_at)` became a range. The index on `created_at` is used.
* `r.active = true` moved into the JOIN, so the filter happens at the same time as the join.
* The CTE narrows `orders` to only the columns we need before joining.

### The soft side of the lesson

The harder part is the conversation, not the SQL. Things I keep in mind:

* **Don't rewrite for them.** They will not learn. Let them read EXPLAIN. Ask "where do you think the time is going?" before pointing.
* **Praise correctness first.** They got the right answer. That is harder than making it fast.
* **Show one fix at a time.** If you change five things in one pass, they cannot tell which one mattered.
* **Time each change.** Before and after on the same data. Numbers stick.
* **Tell them what NOT to do.** Premature optimization. Adding indexes "just in case." Rewriting working queries because they look ugly.

### A checklist I would actually leave with them

When a query is slow:

1. Run `EXPLAIN ANALYZE`. Find the biggest box.
2. Look for full table scans. Add a filter, or check if a function is hiding an index.
3. Look at the order of joins. The smallest filtered set should be on one side of the first join.
4. Select only the columns you need.
5. If using window functions, make sure the input is already as small as possible.
6. Try aggregating before joining if both sides are huge.
7. After each change, re-run EXPLAIN and the query. Note the time.

### Bonus follow-up the interviewer might throw

> *"What if the query is on BigQuery, where there are no indexes?"*

The habits transfer, but the levers are different. On BigQuery: think about **partition pruning** (does the WHERE hit the partition column?), **clustering** (does it hit clustered columns?), **selected columns** (BigQuery charges by bytes scanned), and **broadcast joins** (force the small side to be broadcast if the optimizer doesn't). The mental model "touch less data" stays the same, but "use the index" becomes "use the partition and the cluster."
