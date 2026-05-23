## Solution 25: Smart Meter to Monthly Bill PDF

### The whole flow at a glance

```
   ┌──────────────────────────┐
   │ Meter readings (15-min)  │
   │ s3://meter-raw/...       │
   └────────────┬─────────────┘
                │ parser, validation
                ▼
   ┌──────────────────────────┐
   │ Curated 15-min fact      │   (reads_15min, partitioned by date)
   └────────────┬─────────────┘
                │
                ▼
   ┌──────────────────────────────────────────────┐
   │  Billing calc job                            │
   │  (runs once per customer per billing period) │
   │                                              │
   │  Inputs:                                     │
   │   - reads_15min for the period               │
   │   - tariffs (SCD2)                           │
   │   - customers (dim)                          │
   │   - account_adjustments                      │
   │                                              │
   │  Output: one bill row + bill_lines           │
   └────────────┬─────────────────────────────────┘
                │
                ▼
   ┌──────────────────────────┐
   │  bills (sealed)          │   immutable once issued
   │  bill_lines              │
   └────────────┬─────────────┘
                │
                ▼
   ┌──────────────────────────┐
   │  PDF rendering service   │   pure function of bill_id
   │  (deterministic)         │
   └────────────┬─────────────┘
                │
                ▼
   ┌──────────────────────────┐
   │  Customer portal +       │
   │  email delivery          │
   └──────────────────────────┘
```

The principle: each step is a function of the layer beneath it. Re-run the same step on the same inputs and you get the same output. The PDF is the last and least interesting step.

### The data model

```
reads_15min  (fact, partition by date)
─────────────────────────────────────────
meter_id, read_at, kwh, quality_flag, ingested_at

customers  (dim)
─────────────────────────────────────────
customer_id, meter_id, plan_id, billing_address, ...

tariffs  (SCD Type 2 dim)
─────────────────────────────────────────
plan_id, energy_rate_per_kwh, fixed_daily_charge,
valid_from, valid_to, is_current

account_adjustments  (fact)
─────────────────────────────────────────
adjustment_id, customer_id, amount, reason, applied_on

bills  (mart, sealed)
─────────────────────────────────────────
bill_id (PK), customer_id, period_start, period_end,
kwh_total, energy_charge, fixed_charge, adjustments,
tax, total_due, issued_at, status

bill_lines  (mart)
─────────────────────────────────────────
bill_id, line_no, description, quantity, unit_price, amount
```

The `bill_lines` table is the audit trail. Every cent on the bill has a corresponding row showing exactly how it was computed.

### The billing calculation, step by step

For one customer for one billing period:

**1. Pull readings.**

```sql
SELECT read_at, kwh, quality_flag
FROM reads_15min
WHERE meter_id = @meter
  AND read_at >= @period_start
  AND read_at <  @period_end
ORDER BY read_at;
```

Expect 4 × 24 × 30 = 2880 rows for a 30-day month.

**2. Fill gaps.**

If any interval has no reading or a `missing` flag, fill with an estimate. The estimation rule is usually defined by the regulator: typically "average of the same interval over the previous N days." Mark each filled row with `quality_flag = 'estimated'`.

**3. Join to the tariff in effect at each interval.**

```sql
SELECT r.read_at, r.kwh, t.energy_rate_per_kwh
FROM readings r
JOIN tariffs t
  ON  t.plan_id = @plan_id
  AND r.read_at >= t.valid_from
  AND r.read_at <  t.valid_to;
```

This is the SCD2 "as-of" join from Problem 10. If the tariff changed mid-month, half the rows match the old rate and half match the new one, automatically.

**4. Compute the energy charge.**

```
energy_charge = sum( kwh * rate ) over all 15-min intervals
```

**5. Add the fixed daily charge.**

```
fixed_charge = days_in_period * fixed_daily_charge
```

(If the fixed daily charge changed mid-month, the same SCD2 join handles it per day.)

**6. Apply adjustments.**

```sql
SELECT SUM(amount) FROM account_adjustments
WHERE customer_id = @cust
  AND applied_on BETWEEN @period_start AND @period_end;
```

Examples: refunds, goodwill credits, late fees.

**7. Apply tax.**

Usually a flat percentage of the subtotal. Some markets have different rates for residential vs commercial.

**8. Write bill and bill_lines, sealed.**

One `bills` row plus one `bill_lines` row per category (energy, fixed, each adjustment, tax). After this, the bill is frozen. Any later correction is a new adjustment in the next billing period, not an edit.

### Idempotency

The job is keyed by `(customer_id, period_start, period_end)`. Re-running it for the same key:

* DELETEs any draft bill_lines for that key.
* Recomputes from current `reads_15min` and `tariffs`.
* If a bill with that key is `status = 'issued'`, the job refuses to overwrite. You can only correct via an adjustment.

Pseudocode:

```python
def compute_bill(customer_id, period_start, period_end):
    existing = bills.get(customer_id, period_start)
    if existing and existing.status == 'issued':
        raise BillAlreadyIssued(existing.bill_id)

    # idempotent re-compute
    delete_lines_for(customer_id, period_start)
    lines = build_lines(customer_id, period_start, period_end)
    write_lines(lines)
    write_bill(summary_of(lines), status='draft')
```

### Late and corrected readings

This is where the design pays off.

* If readings for May 10 arrive late on May 14, the curated layer rebuilds the May 10 partition.
* If May's bill has not been issued yet, the next run of the billing job picks up the new numbers naturally. No special code.
* If the bill was already issued, the change creates an `account_adjustment` row to apply in the next billing cycle. The regulator sees a clean trail: "your May bill was X. On June 5 we received corrected readings for May 10. We credited Y dollars on your June bill."

Much cleaner than editing a sealed bill, which would break audits.

### Mid-month tariff changes

These happen often (price reviews, customer plan switches). Handled by:

* The `tariffs` table is SCD Type 2.
* The as-of join in step 3 matches each 15-minute reading to the rate that was in force at that exact moment.
* Bill lines show "Energy 1-15 May at 0.18/kWh" and "Energy 16-31 May at 0.22/kWh" separately, so the customer can see what changed.

### Auditability

The audit trail is the `bill_lines` table plus a snapshot of the inputs. Three pieces:

1. The bill itself (issued, sealed).
2. `bill_lines` showing every component.
3. A reading snapshot. At bill time we record a `reads_snapshot_id` pointing to the version of the curated reads we used. If a later correction changes the readings, the snapshot still shows what we billed on.

A dispute conversation looks like: "Your May energy charge of $XX comes from these 2,880 readings, totaling YYY kWh, at the rates shown in lines 1 and 2. The estimated readings are flagged on line 3."

### PDF rendering

The PDF service is a pure function of the `bill_id`. It reads the bill and `bill_lines` and renders. It computes nothing. If we change the PDF template, every old bill can be re-rendered to the new look without changing any numbers.

Two practical patterns:

* PDFs are written to S3 with a deterministic name: `bills/{customer_id}/{period}/{bill_id}.pdf`.
* The PDF carries a small footer like "Bill ID: B-2025-05-12345" so the support team can find the source data instantly.

### What happens when generation fails

Failure modes I'd design for:

* Missing readings for the period. Job pauses, alerts ops, no bill is generated.
* PDF rendering crashes. Bill row exists, no PDF. The PDF service retries; if it never works, ops gets paged.
* Wrong tariff applied (config error). All bills for the period get re-generated. Since they are not yet `issued`, the job can do this idempotently.
* Adjustment job double-fires. Each adjustment has a unique id; the bill query SUMs over DISTINCT ids.

### Why split the job per customer

Two reasons:

* Parallelism. 200,000 customers at ~1 second per bill is 56 hours sequentially. With 200 workers in parallel, ~17 minutes.
* Isolation. One customer's bug doesn't poison the rest. If the bill job for customer 12345 fails, the other 199,999 still go out.

A simple orchestrator (Airflow with dynamic task mapping, or a queue of customer ids) is enough.

### Common mistakes interviewers want you to name

1. Editing a sealed bill when a correction arrives. Use adjustments.
2. Not handling SCD2 tariffs. Mid-month tariff changes get billed wrong.
3. Computing during PDF rendering. A template change later silently changes old totals.
4. No quality flag for estimates. Auditors require "what was measured vs estimated."
5. Ignoring per-customer time zones when defining the billing period.

### Bonus follow-up the interviewer might throw

> *"How would you parallelize this for 5 million customers?"*

Same architecture, more parallelism. Two changes worth mentioning:

* Run the billing job on Spark or BigQuery instead of Python-per-customer. The "per customer" loop becomes SQL with `GROUP BY customer`.
* The PDF render service stays per-customer but moves behind a queue with a thousand workers.

Five million bills at ~0.5 seconds each, 1,000 workers, is roughly 40 minutes of wall clock.
