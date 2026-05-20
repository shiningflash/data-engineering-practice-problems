## Solution 18: CTE vs Subquery

### Short version you can say out loud

> A CTE is a named result you build with `WITH ... AS (...)` and then reference by name later. A subquery is an inline `SELECT` nested inside another query. They are usually equivalent in meaning. The reason CTEs matter is mostly readability: you can name a step, reuse it, and read the query top to bottom like a paragraph. The reason they were a performance trap is that older Postgres treated CTEs as an "optimization fence," meaning it would materialize them before using them, even when a subquery would have been folded into the main plan. Modern Postgres (12+), BigQuery, Snowflake and most others inline CTEs by default, so the difference is mostly stylistic again.

### Same query, two ways

```sql
-- Subquery
SELECT c.country, COUNT(*) AS big_orders
FROM customers c
JOIN (
  SELECT customer_id, amount
  FROM orders
  WHERE amount > 1000
) big ON big.customer_id = c.id
GROUP BY c.country;


-- CTE
WITH big_orders AS (
  SELECT customer_id, amount
  FROM orders
  WHERE amount > 1000
)
SELECT c.country, COUNT(*) AS big_orders
FROM customers c
JOIN big_orders b ON b.customer_id = c.id
GROUP BY c.country;
```

Same result, same intent. Different shape.

### Why I usually reach for a CTE

* **Naming a step.** "These are the big orders" reads better than a nested SELECT.
* **Reusing a step.** I can reference `big_orders` twice in the same query. A subquery would have to be repeated.
* **Top-to-bottom flow.** You build up small intermediate results, then combine them. Same idea as breaking a Python function into smaller helpers.

For long queries (5+ joins, multiple aggregates), this matters a lot. A 100-line query with five CTEs reads like five short paragraphs. The same logic with nested subqueries reads like one paragraph with five embedded clauses.

### The historical trap (Postgres < 12, and a few others)

Older Postgres treated every CTE as a "materialization fence." It computed the CTE once, stored the result in a temporary structure, and then read from that structure in the main query. That sounds fine, but it killed plan optimization. Consider:

```sql
WITH recent AS (
  SELECT * FROM orders
)
SELECT * FROM recent WHERE created_at > '2025-05-01';
```

In old Postgres, the CTE materialized the entire `orders` table first, then filtered. A naked subquery would have pushed the WHERE down into the scan. So the CTE version could read 10x more data.

The fix in modern Postgres: CTEs are inlined by default if they are referenced once and have no side effects. You can force the old behavior with `WITH recent AS MATERIALIZED (...)`. You can force inlining with `WITH recent AS NOT MATERIALIZED (...)`.

In BigQuery, Snowflake, Redshift, DuckDB, the optimizer almost always treats CTEs as views (inlined). The trap mostly does not apply there.

### When do you WANT a materialized CTE?

Sometimes you specifically want the CTE computed once and reused. Use cases:

1. **The CTE is expensive and referenced many times.** Inlining means running it every time. Materializing means once.
2. **The CTE has side effects** (DML inside a CTE, like `INSERT ... RETURNING`). It has to run exactly once.
3. **You want to force a specific join order** that the optimizer keeps getting wrong. Materializing creates a hard boundary.

If your engine does not auto-detect this, you can be explicit:

```sql
WITH expensive AS MATERIALIZED (
  SELECT ... -- referenced 5 times below
)
SELECT ...
```

### What CTEs can do that subqueries cannot

**Recursive queries.** Only CTEs support recursion:

```sql
WITH RECURSIVE org_tree AS (
  SELECT id, manager_id, name, 1 AS level
  FROM employees
  WHERE manager_id IS NULL
  UNION ALL
  SELECT e.id, e.manager_id, e.name, t.level + 1
  FROM employees e
  JOIN org_tree t ON e.manager_id = t.id
)
SELECT * FROM org_tree;
```

Walking trees, graph traversal, parent-child unfolding. No subquery form exists for this.

### My rule of thumb today

* Default to CTEs for **anything over 20 lines** or **anything with more than one logical step**. Readability is the bigger long-term cost.
* Use a subquery when the inner part is **tiny and used exactly once**, like `WHERE id IN (SELECT customer_id FROM banned_users)`.
* On Postgres < 12, watch for materialization. If a query gets slow when you switch from subquery to CTE, that is the cause.
* On modern engines, write whichever reads better. The plan will be the same.
* Use `MATERIALIZED` or a real temp table when the CTE is expensive and reused, and the optimizer is not picking that up.

### A note on temp tables vs CTEs

If a "CTE" is reused across multiple queries (not just inside one query), it should not be a CTE. It should be a temp table:

```sql
CREATE TEMP TABLE big_orders AS
SELECT customer_id, amount FROM orders WHERE amount > 1000;

-- Now reuse big_orders in many queries this session.
```

This is a clearer signal to anyone reading the code, and to the engine, that this is a real intermediate result.

### Common mistakes interviewers want you to name

1. **Switching everything to CTEs "for readability"** on an old Postgres and watching plans get worse.
2. **Using `WITH RECURSIVE` for things that have a known finite depth** (3-level org chart) when a self-join would have been clearer.
3. **Computing the same CTE twice when referenced once.** If the planner inlines, you pay twice. Add `MATERIALIZED` if reused.
4. **Treating CTEs as variables.** They are not. You cannot assign to them. They are query-level views.

### Bonus follow-up the interviewer might throw

> *"What about CTEs in BigQuery specifically? Is there a cost difference?"*

In BigQuery, CTEs are inlined into the SQL, so they do not change the bytes scanned. But if you reference the same CTE multiple times, the underlying query runs each time. For very expensive CTEs referenced many times, write the intermediate to a real table or use a `TEMP TABLE` in a multi-statement query, so the work happens once.
