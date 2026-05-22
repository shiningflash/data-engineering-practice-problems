## Solution 44: Explaining Fact Table Grain

### Short version you can say out loud

> Grain is the answer to the question "what does one row in this table mean?" If you cannot finish the sentence "one row in this table is one ____," you do not have grain pinned down yet. Every aggregation, every join, every dashboard depends on it. Get grain wrong and your numbers are off by exactly the right amount to look plausible but be misleading.

### Explaining grain to a non technical stakeholder

The way I would say it in a meeting:

> "Imagine each table is a stack of paper. Grain is what is printed on one sheet. If the sheet is 'one customer,' then there is one sheet per customer and we can count sheets to count customers. If the sheet is 'one order,' there is one per order. If the sheet is 'one item on one order,' there are many more sheets, because each order has multiple items. We have to know what one sheet is before we know what summing them up means."

A stakeholder who understands "one row = one X" is suddenly ready to ask the right questions.

### Three grains for the same business

Imagine a coffee shop chain.

**Grain: one sale.**

```
sale_id │ store │ date       │ total_amount
1       │ A     │ 2025-05-14 │ 12.50
2       │ A     │ 2025-05-14 │  7.00
```

Useful for "total revenue today per store." Not useful for "how many large lattes were sold."

**Grain: one item on one sale.**

```
sale_id │ store │ date       │ product  │ qty │ amount
1       │ A     │ 2025-05-14 │ Latte L  │ 1   │ 6.50
1       │ A     │ 2025-05-14 │ Croissant│ 2   │ 6.00
2       │ A     │ 2025-05-14 │ Coffee   │ 2   │ 7.00
```

Useful for everything the first grain can do, plus "how many lattes did we sell." More rows, more flexibility.

**Grain: one minute of sales per store.**

```
store │ minute               │ revenue │ items_sold
A     │ 2025-05-14 09:01:00  │ 23.50   │ 4
A     │ 2025-05-14 09:02:00  │ 0.00    │ 0
```

Useful for "what minute are we busiest." Not useful for "what was sale 1234."

Same business, three legitimate grains. Each one answers a different question.

### How wrong grain produces wrong numbers

Imagine the team mixes grains accidentally:

```
SELECT
  s.store,
  SUM(s.total_amount) AS revenue,
  COUNT(*) AS line_items_sold
FROM fact_sale_lines s
GROUP BY s.store;
```

`fact_sale_lines` is at the **line item** grain. So `SUM(total_amount)` may be double-counting the sale's total if every line carries the order's total. The COUNT is right (it counts line items), but the SUM is wrong.

This is the most common modeling bug. The reason it goes unnoticed: the numbers are usually "in the right ballpark," so nothing screams. You only catch it by reconciling against the source system.

The fix: each fact table should carry **only** measurements at its own grain. Order total goes on `fact_orders`, not `fact_order_lines`. Line price goes on `fact_order_lines`, not on `fact_orders`.

### Choosing grain for a new fact

Three questions:

1. **What does the dashboard or report want?** This is the only honest answer. Build to the finest grain you actually need.
2. **Is there a natural "thing that happens once" in the business?** That is usually your grain. A sale, an order, a payment, a shipment, a meter reading.
3. **What is the right time grain?** Per-event is most flexible. Per-minute or per-day is a pre-aggregation, useful when the finer grain is too big.

The default for transactional facts is "one row per event." Pre-aggregations sit on top for performance.

### Mixed grain in one table is the bug

Sometimes a fact table tries to be both order-grain and line-grain. The smell: most columns are filled in, but a few columns (like `line_id` or `quantity`) are null on some rows.

The fix is to split into two tables, each with one clear grain:

```
fact_orders        : one row per order  (order_total, customer_key, ...)
fact_order_lines   : one row per line   (order_id, product_key, qty, price)
```

If you need both in one query, join them. Do not collapse them.

### Coarser is faster, finer is more flexible

The trade-off:

* **Coarser grain** (one row per day per store) means fewer rows, faster queries. But you can never answer questions below that grain ("what was sold at 9:42 AM").
* **Finer grain** (one row per second, or per individual event) keeps every question open. But the table is huge.

The common pattern: keep the finest grain in `fact_*`, build pre-aggregates `agg_*` for the questions you ask most.

### Bridge tables for many-to-many

What if one fact has many "many-to-many" relationships? An order can have many promotions applied, a promotion can apply to many orders.

You cannot put both on the same row without violating grain. The fix:

```
fact_orders           one row per order
fact_order_promotions one row per (order, promotion) pair
```

The bridge table has its own grain. You join through it when you want "promotions per order" or "orders per promotion."

### Common mistakes interviewers want you to name

1. **No grain documented.** The new team member has to figure it out from the data.
2. **Mixed grain.** Some rows are orders, some are line items, in the same table.
3. **SUM across the wrong grain.** Counts items but sums order totals; gets a multiplied number.
4. **Building one giant table** with every possible measurement at every grain. Always wrong somewhere.
5. **Confusing time grain with entity grain.** "Per day" is a time grain. "Per order" is an entity grain. Both can apply at once.

### How I would teach this

When mentoring, I would write the grain in the first line of the table's docs:

> `fact_orders`: one row per order. An order is everything a single customer placed in one checkout, including all its line items.

And on `fact_order_lines`:

> `fact_order_lines`: one row per item on an order. A single product appears once per order, with a quantity column.

Two sentences. The whole team now reads tables the same way.

### Bonus follow-up the interviewer might throw

> *"What if the business asks 'show me both order count and line item count in one query'? Won't joining force a grain choice?"*

You join, but you have to aggregate to one grain on each side before joining. For example:

```sql
WITH orders_per_day AS (
  SELECT order_date, COUNT(*) AS orders
  FROM fact_orders GROUP BY order_date
),
lines_per_day AS (
  SELECT order_date, SUM(qty) AS items
  FROM fact_order_lines GROUP BY order_date
)
SELECT o.order_date, o.orders, l.items
FROM orders_per_day o
JOIN lines_per_day  l USING (order_date);
```

Each CTE has its own grain (per-day), then you join at the common grain. No row-multiplication.
