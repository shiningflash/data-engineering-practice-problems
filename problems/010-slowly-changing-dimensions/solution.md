## Solution 10: Slowly Changing Dimensions

### Short version you can say out loud

> A slowly changing dimension is a dimension table whose values change occasionally, not constantly. The real question is what you do when one of those values changes: do you overwrite, or do you keep history. The answer depends on whether reports need to know what the value used to be. For things like a customer's address, where past invoices need to stay correct, you almost always keep history. That is called SCD Type 2, and it is the most common pattern in real warehouses.

### Why this matters

The story above is a real failure mode. If you store only the current address, every historical query silently rewrites the past. Yesterday's report no longer matches today's, even though you only loaded new data, you did not touch the old data. That kills trust in the warehouse.

```
Without history (broken)
─────────────────────────
customer_id │ name  │ country
1001        │ Alice │ MY        ← changed from SG in March

Old invoice from January says customer 1001.
Report joins to dimension, gets MY.
The January invoice now appears under MY.
Finance: "Why did SG's January number drop?"

With history (SCD Type 2)
─────────────────────────
customer_id │ name  │ country │ valid_from │ valid_to   │ is_current
1001        │ Alice │ SG      │ 2023-01-01 │ 2025-03-15 │ false
1001        │ Alice │ MY      │ 2025-03-15 │ 9999-12-31 │ true

January invoice (date = 2025-01-20) joins to the row valid that day.
It correctly appears under SG.
```

### The classic SCD types in plain words

Type 0, never change. The value is set once and frozen. Used for things like a customer's original signup country, or the date they joined. Rare but useful.

Type 1, overwrite. When the value changes, you replace it. No history kept. Used for things where history does not matter, like a typo fix in a name.

Type 2, add a new row. When the value changes, you keep the old row and add a new one. You add columns like `valid_from`, `valid_to`, and `is_current`. Every fact joins to the dimension row that was valid at the fact's timestamp. By far the most common.

Type 3, add a column. You keep one extra column like `previous_country`. Useful when you only care about the most recent change, not the full history. Rare in modern warehouses.

There are higher types (Type 4 with mini-dimensions, Type 6 hybrid) but for interviews, knowing 1, 2 and 3 well is enough.

### Concrete shapes

Type 1 (overwrite):

```
customers
─────────────────────────────────────
customer_id │ name      │ country
1001        │ Alice Lee │ MY        ← overwritten
1002        │ Bob Khan  │ SG
```

After Alice moves, the old `SG` value is gone. Cheap to store. History lost.

Type 2 (add row, version with dates):

```
customers_history
──────────────────────────────────────────────────────────────────────
customer_id │ name      │ country │ valid_from │ valid_to   │ is_current
1001        │ Alice Lee │ SG      │ 2023-01-01 │ 2025-03-15 │ false
1001        │ Alice Lee │ MY      │ 2025-03-15 │ 9999-12-31 │ true
1002        │ Bob Khan  │ SG      │ 2024-05-10 │ 9999-12-31 │ true
```

Every change adds a new row. `valid_from` / `valid_to` mark the period it was true. `is_current` is a convenience flag so queries that want "right now" do not have to use `9999-12-31`.

Type 3 (one extra column):

```
customers
─────────────────────────────────────────────────
customer_id │ name      │ country │ previous_country
1001        │ Alice Lee │ MY      │ SG
1002        │ Bob Khan  │ SG      │ NULL
```

Tracks one prior value only. Useful for "did this customer recently move."

### How to query Type 2 (the as-of join)

This is the join pattern you will draw on the whiteboard:

```sql
SELECT
  i.invoice_id,
  i.amount,
  c.country AS country_at_invoice_time
FROM invoices i
LEFT JOIN customers_history c
  ON  c.customer_id = i.customer_id
  AND i.invoice_date >= c.valid_from
  AND i.invoice_date <  c.valid_to;
```

Two important details:

1. The interval is `[valid_from, valid_to)`. Half open. This avoids the row appearing in both the old and the new period on the exact change date.
2. You join on date inside range, not on `is_current`. Using `is_current` brings back the original bug.

### Which type to pick

| Field | Likely type | Why |
| ---------------------------- | ----------- | --------------------------------------------------------- |
| Customer address / country | Type 2 | Past invoices must keep their original region |
| Customer's display name | Type 1 | A typo fix should fix old reports too |
| Subscription plan tier | Type 2 | Revenue reporting depends on which plan they had when |
| Currency code of an account | Type 2 | Historical balances were stored in that currency |
| Most recent campaign source | Type 3 | We only care about "the one before this one" |
| Their original signup date | Type 0 | Set once, never changes |

### Common mistakes interviewers want you to name

1. Storing only current state. The "moving customer breaks historical region revenue" story.
2. Type 2 done wrong by joining on `is_current` instead of date ranges. Same bug, fancier table.
3. Overlapping validity ranges because two updates landed in the same second and you forgot to close the previous row before opening a new one.
4. Type 2 explosion when you flag too many columns as "track history." Pick the few that really need it. Otherwise the dimension grows to billions of rows for no reason.

### Bonus follow-up the interviewer might throw

> *"How would you actually build a Type 2 table in dbt?"*

dbt has a built in `snapshot` materialisation that does exactly this. You declare:

```sql
{% snapshot customers_history %}
  {{ config(
      target_schema='snapshots',
      unique_key='customer_id',
      strategy='check',
      check_cols=['country', 'plan_tier']
  ) }}
  SELECT * FROM {{ source('app', 'customers') }}
{% endsnapshot %}
```

Every time it runs, dbt diffs the source against the snapshot. New or changed rows get a fresh `dbt_valid_from` and the previous row's `dbt_valid_to` is closed. The easiest way to get Type 2 in a modern warehouse without writing the MERGE by hand.
