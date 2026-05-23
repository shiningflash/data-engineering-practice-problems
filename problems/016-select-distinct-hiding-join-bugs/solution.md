## Solution 16: SELECT DISTINCT Hiding Join Bugs

### Short version you can say out loud

> The duplicates are not really duplicates. They are real rows produced by joining a table to another table that has multiple matching rows. DISTINCT silently collapses them, which feels like a fix, but it also collapses things that genuinely should be separate. Two rows that look the same in the selected columns might come from different orders, different timestamps, different reasons. The right fix is to think about the **grain** of each table in the join, and either filter, aggregate, or use a semi-join so each row appears at most once on purpose.

### Where the duplicates come from

```
orders                       order_items
─────────────                ─────────────────
id │ customer_id             order_id │ product
1  │ 100                     1        │ apple
2  │ 100                     1        │ banana
3  │ 200                     2        │ apple
                             3        │ apple
                             3        │ apple

SELECT o.id, o.customer_id
FROM orders o
JOIN order_items i ON i.order_id = o.id;

Result:
id │ customer_id
1  │ 100          ← order 1 has 2 items, so it shows twice
1  │ 100
2  │ 100
3  │ 200          ← order 3 has 2 items of the same product
3  │ 200
```

The analyst sees order 1 twice and thinks "I need DISTINCT." But the row repetition is correct given the join. It is just that they joined a one-row-per-order table to a one-row-per-item table, so the result has one row per item.

The bug is the *choice of join*, not a duplicate problem.

### Why DISTINCT is the dangerous fix

```sql
SELECT DISTINCT o.id, o.customer_id
FROM orders o
JOIN order_items i ON i.order_id = o.id;
```

This returns:
```
id │ customer_id
1  │ 100
2  │ 100
3  │ 200
```

Looks clean. But two real risks:

1. **It hides intent.** Three months later, someone adds `i.product` to the SELECT. Now DISTINCT does not collapse the rows anymore, the numbers explode, nobody understands why.
2. **It can collapse rows that should differ.** If you wrote `SELECT DISTINCT customer_id, country` and a customer has two countries in your history (they moved), you silently lose the second one.
3. **It hides bugs.** Imagine the join condition was wrong. Without DISTINCT, you would have seen huge duplication and known something was off. With DISTINCT, the numbers just quietly drift.

### The right way to think about it

Every table has a **grain**: the level at which one row means one thing. Examples:

* `customers` grain: one row per customer.
* `orders` grain: one row per order.
* `order_items` grain: one row per item within an order.
* `meter_reads` grain: one row per meter per 15-minute interval.

When you join, the result has the grain of the **finest** table in the join. If you want one row per customer in the final result, you cannot join straight to `order_items`. You have to **aggregate first** or use a **semi-join**.

### Fix 1: Aggregate before joining

If the analyst wanted "one row per order with the number of items," aggregate `order_items` first:

```sql
WITH items_per_order AS (
  SELECT order_id, COUNT(*) AS item_count
  FROM order_items
  GROUP BY order_id
)
SELECT o.id, o.customer_id, COALESCE(i.item_count, 0) AS item_count
FROM orders o
LEFT JOIN items_per_order i ON i.order_id = o.id;
```

Now the join is one to one. No duplicates. No DISTINCT.

### Fix 2: Use EXISTS (semi-join)

If the analyst wanted "all orders that have at least one item," they do not need to join at all:

```sql
SELECT o.id, o.customer_id
FROM orders o
WHERE EXISTS (
  SELECT 1
  FROM order_items i
  WHERE i.order_id = o.id
);
```

`EXISTS` stops at the first match. It does not multiply rows. This is called a semi-join. It is exactly the right tool when the question is "does any matching row exist," and most engines optimize it well.

The opposite, `NOT EXISTS`, finds orders with no items at all.

### Fix 3: Window or row_number filter

Sometimes you genuinely want "one row per group, but I need columns from the child table too." Use `ROW_NUMBER`:

```sql
SELECT id, customer_id, product
FROM (
  SELECT o.id, o.customer_id, i.product,
         ROW_NUMBER() OVER (PARTITION BY o.id ORDER BY i.created_at) AS rn
  FROM orders o
  JOIN order_items i ON i.order_id = o.id
) ranked
WHERE rn = 1;
```

This says "for each order, keep only the first item." Explicit, intentional, and the next reader knows exactly what you meant.

### A useful sanity check

If your query returns N rows but the table you said you wanted "one row per X" has N rows that don't match, something is wrong. Before sharing a result, do a quick row count check:

```sql
SELECT COUNT(*), COUNT(DISTINCT id) FROM result;
```

If these differ, you have duplicates you did not expect. Either fix the query or be explicit about why duplicates are intended.

### Common mistakes interviewers want you to name

1. **DISTINCT as a habit, not a decision.** Sprinkled because the result looked off, not because the question asked for unique rows.
2. **DISTINCT on a query you later edit.** It only worked because the SELECT list was narrow. Add a column, it stops working.
3. **DISTINCT to "fix" a many-to-many join.** The real fix is to aggregate or filter.
4. **Counting users with DISTINCT user_id** in a query that already has duplicates from joins. The count is right, but the rest of the query may be carrying wrong totals from the same duplication.
5. **Not understanding grain.** This is the deeper issue. Once you can say the grain of each table out loud, the DISTINCT problem disappears.

### Bonus follow-up the interviewer might throw

> *"When IS DISTINCT actually the right tool?"*

When you genuinely have a set, not a multiset, and you want to deduplicate it. For example:

* Listing the unique countries that appeared in a column.
* Building a deduplicated list of email addresses from multiple source files where the same address really might appear twice and you want it once.

The key is intent: you should be able to say out loud "I expect duplicates here and I want one of each." If the answer is "I just don't want the join to multiply rows," DISTINCT is the wrong fix.
