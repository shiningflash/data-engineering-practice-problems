## Solution 20: Window Functions vs GROUP BY

### Short version you can say out loud

> GROUP BY collapses many rows into one row per group. Window functions compute a value across a group but keep every row. If the question is "give me one number per customer," I use GROUP BY. If the question is "for each order, also show this customer's running total," I use a window function. The key tell is the word "for each row also" in the requirement.

### The whiteboard picture

```
Same data, two shapes.

orders
─────────────────────────────────────────
order_id │ customer_id │ amount │ created_at
1        │ A           │ 100    │ Jan 1
2        │ A           │ 50     │ Jan 5
3        │ B           │ 200    │ Jan 3
4        │ A           │ 70     │ Jan 10


GROUP BY                          WINDOW
────────────────                  ──────────────────────────────────
SELECT                            SELECT
  customer_id,                      order_id, customer_id, amount,
  SUM(amount) AS total              SUM(amount) OVER (
FROM orders                           PARTITION BY customer_id
GROUP BY customer_id;                 ORDER BY created_at
                                    ) AS running_total
                                  FROM orders;

Result:                           Result:
customer │ total                   order │ customer │ amount │ running
A        │ 220                     1     │ A        │ 100    │ 100
B        │ 200                     2     │ A        │ 50     │ 150
                                   3     │ B        │ 200    │ 200
                                   4     │ A        │ 70     │ 220
```

Notice: GROUP BY returned 2 rows. WINDOW returned 4 rows. Same SUM, different result shape.

### What each one is, in one line

* **GROUP BY**: collapse rows that share group-key values into one row per group, with aggregates over the group.
* **Window function**: compute an aggregate (or ranking, or lag) for each row, looking at a window of related rows around it, without collapsing anything.

### When to reach for each

| Need                                                | Use         |
| --------------------------------------------------- | ----------- |
| Total revenue per customer (one row per customer)   | GROUP BY    |
| Count of orders per country                         | GROUP BY    |
| For each order, show running total per customer     | Window      |
| Rank customers by spend within each country         | Window      |
| Find each customer's previous order date            | Window (LAG)|
| For each row, compare the value to the group avg    | Window      |
| Pick the top 1 row per group                        | Window (ROW_NUMBER)|

The shortcut: if the answer should have **more rows than the number of groups**, you need a window.

### Three things window functions do that GROUP BY cannot

**1. Running totals and moving averages.**

```sql
SELECT
  date,
  amount,
  SUM(amount) OVER (ORDER BY date) AS cumulative,
  AVG(amount) OVER (
    ORDER BY date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS rolling_7day_avg
FROM daily_sales;
```

GROUP BY cannot do this because it would force one row per group.

**2. Ranking inside a group.**

```sql
SELECT
  customer_id, country, total_spend,
  RANK() OVER (PARTITION BY country ORDER BY total_spend DESC) AS rank_in_country
FROM customer_totals;
```

`ROW_NUMBER`, `RANK`, `DENSE_RANK` give you the row's position inside its partition. Indispensable for "top N per group" queries.

**3. Lookups to previous / next rows.**

```sql
SELECT
  meter_id, reading_time, value,
  LAG(value) OVER (PARTITION BY meter_id ORDER BY reading_time) AS prev,
  value - LAG(value) OVER (PARTITION BY meter_id ORDER BY reading_time) AS delta
FROM meter_reads;
```

`LAG` and `LEAD` make "compare this row to the next/previous one" trivial. Without windows, you would need a self-join.

### The "top N per group" pattern

This is so common it is worth memorizing:

```sql
WITH ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY country ORDER BY total_spend DESC) AS rn
  FROM customer_totals
)
SELECT * FROM ranked WHERE rn <= 3;
```

This gives you the top 3 customers in each country. With GROUP BY alone, you would have to do tricks with self-joins or LATERAL queries.

### The PARTITION BY vs GROUP BY confusion

A common bug: writing `GROUP BY country` in a query that also has window functions, and being surprised the windows behave oddly.

* `GROUP BY country` collapses to one row per country. Window functions then operate on those collapsed rows.
* `PARTITION BY country` inside an OVER clause divides the rows into groups *without* collapsing.

These are different. They can coexist, but you have to be deliberate.

### Performance notes

Window functions are not free. They typically require a sort by the `PARTITION BY` columns, then by the `ORDER BY` columns. For very large tables, that sort can be the bottleneck.

Two practical things:

1. **Filter early.** Run the window only on the rows you need.
2. **Use the right window.** `ROWS BETWEEN ... AND CURRENT ROW` is much cheaper than `RANGE` for time-based windows on some engines.

### Common mistakes interviewers want you to name

1. **Trying to GROUP BY when the answer needs per-row detail.** "Show me each order with the customer's lifetime total." GROUP BY cannot keep the order row.
2. **Forgetting `ORDER BY` inside the window.** `SUM(...) OVER (PARTITION BY x)` without ORDER BY is the same total on every row. Often someone meant a running total but got the grand total.
3. **Filtering on a window column in WHERE.** You cannot. WHERE runs before windows. Use a subquery or CTE and filter on the alias in the outer SELECT.
4. **PARTITION BY too coarse.** "Top 5 products overall" needs no partition. "Top 5 products in each country" needs `PARTITION BY country`. Easy to mix up.

### Bonus follow-up the interviewer might throw

> *"What is the difference between RANK, DENSE_RANK and ROW_NUMBER?"*

* `ROW_NUMBER`: every row gets a unique number, ties broken arbitrarily.
* `RANK`: ties share a number, then it skips. `1, 2, 2, 4`.
* `DENSE_RANK`: ties share a number, no skip. `1, 2, 2, 3`.

Use `ROW_NUMBER` when you want exactly one row per "first place" (top-N-per-group). Use `RANK` or `DENSE_RANK` when ties matter, like leaderboards.
