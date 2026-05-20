## Solution 21: Data Platform for an Electricity Retailer

### Volume math first (always start here)

> 200,000 meters × 96 readings per day = **19.2 million readings/day**
> About **7 billion readings/year**, or roughly **0.5 TB/year** raw (assuming ~70 bytes per reading row).

This is large but very tractable. It is not "needs Spark" territory. A modest warehouse handles this comfortably. Smart meter data is heavy in row count but small in payload, so we will lean on columnar storage and time partitioning.

### The shape of the platform

```
                                ┌──────────────────────┐
   Smart meters (200k)          │      HEAD-END SYSTEM │
   send every 15 min via        │  (vendor system that │
   the utility's protocol  ────▶│  collects from MDM,  │
   (DLMS, NB-IoT, etc.)         │  emits files / API)  │
                                └──────────┬───────────┘
                                           │
                            JSON / CSV per device per hour
                                           │
                                           ▼
                                ┌──────────────────────┐
                                │   S3 (RAW LAYER)     │
                                │  s3://meter-raw/     │
                                │   yyyy/mm/dd/hh/     │
                                └──────────┬───────────┘
                                           │
                                Triggered by S3 event
                                           │
                                           ▼
                                ┌──────────────────────┐
                                │   AWS Lambda /       │
                                │   Glue parser        │
                                │  validate, normalize │
                                └──────────┬───────────┘
                                           │ Parquet
                                           ▼
                                ┌──────────────────────┐
                                │  S3 (CURATED LAYER)  │
                                │  s3://meter-curated/ │
                                │   date=YYYY-MM-DD/   │
                                └──────────┬───────────┘
                                           │
                              dbt + Airflow (hourly)
                                           │
                                           ▼
                                ┌──────────────────────────────┐
                                │  WAREHOUSE (Redshift /       │
                                │  Snowflake / BigQuery)       │
                                │                              │
                                │  reads_15min   (raw fact)    │
                                │  reads_hourly  (rollup)      │
                                │  reads_daily   (rollup)      │
                                │  customers     (dim)         │
                                │  tariffs       (SCD2 dim)    │
                                │  bills         (mart)        │
                                └──────────┬───────────────────┘
                                           │
              ┌────────────────────────────┼────────────────────┐
              ▼                            ▼                    ▼
   ┌──────────────────┐         ┌──────────────────┐   ┌──────────────────┐
   │  Customer app    │         │  Ops dashboards  │   │  Forecasting     │
   │  reads from a    │         │  (Looker, Metab) │   │  model (Python,  │
   │  small Postgres  │         │  query warehouse │   │  reads warehouse │
   │  serving table   │         │  directly        │   │  history)        │
   │  (last 90 days)  │         │                  │   │                  │
   └──────────────────┘         └──────────────────┘   └──────────────────┘
```

### Why each piece

**S3 raw layer.** Cheap, append-only, every original file is preserved. If a downstream bug is discovered, we can reprocess everything. This is the most underrated part of the design.

**Lambda (or Glue) parser.** The volume is large but each file is small. Lambda triggered by S3 events scales naturally to 200k devices and is pay-per-invocation. The parser does three things: validate the row schema, normalize units (kWh, kW), and write Parquet to the curated layer partitioned by date.

**S3 curated layer (Parquet, partitioned).** Columnar, compressed, queryable directly by Athena if needed. Partition by `date` so backfills and date filters are cheap.

**Warehouse with three rollup tables.** The trick is to never let dashboards or the app touch the raw 15-minute fact directly. We pre-aggregate.

* `reads_15min` keeps the source of truth at full granularity. Used for billing and forecasting.
* `reads_hourly` is built nightly from `reads_15min`. Used for ops dashboards.
* `reads_daily` is built from `reads_hourly`. Used for the customer app and monthly bills.

A query that asks "show me my last 90 days of usage" hits 90 rows in `reads_daily`, not 8,640 rows in `reads_15min`.

**Customer app serving layer.** This is the one place I would not go straight to the warehouse. Warehouse queries are seconds, not milliseconds, and they are not built for thousands of concurrent users. I would push the last 90 days of `reads_daily` per customer into a small Postgres or DynamoDB serving table, refreshed nightly. The app reads from there in under 50 ms.

### Walking through each use case

**1. Monthly bills.**
Run a monthly job that reads `reads_15min` for the billing period for each customer, multiplies by the tariff in effect (using an SCD Type 2 `tariffs` table to handle mid-month price changes), and writes one bill row per customer per month. Bills are idempotent: rerunning the job for the same period produces the same number.

**2. The customer app "your usage" page.**
Reads from the serving table mentioned above. Last 90 days at daily grain. Loads in well under 2 seconds.

**3. Daily ops reports.**
Run on `reads_hourly` and `reads_daily`. Total energy by region, top 100 highest consuming customers, devices with no reading in the last 24 hours. All under 5 seconds in the warehouse.

**4. Forecasting for wholesale market bids.**
Read several years of `reads_15min` aggregated to hourly, train a model (Prophet, gradient boosting, or a small neural network), forecast next day. Runs nightly. Forecaster reads warehouse directly because it is a single process, not many users.

### Handling late and corrected data

Smart meter data is notoriously messy. Devices go offline, send readings late, sometimes resend corrected values. The platform has to absorb this without producing wrong bills.

Three rules:

1. **Raw layer is append-only.** Late files just land in their original date partition or a "late" partition.
2. **Curated and rollup layers are rebuilt by partition, not by row.** A late file for May 10 triggers a rebuild of May 10 in `reads_15min`, `reads_hourly`, `reads_daily`. The MERGE / overwrite pattern from Problem 9.
3. **Bills are sealed.** Once a bill is sent, the bill row is frozen. Subsequent corrections produce an *adjustment* row, not an edit. This is how regulators expect it.

```
Raw    : May 10 partition gains 32 new late readings
Curated: May 10 rebuilt (idempotent overwrite)
Rollups: May 10 hourly + daily rebuilt
Bill   : May was already sent → adjustment row
         May was not yet billed → next bill picks up the change
```

### Schema sketch

```
reads_15min  (partition by date)
─────────────────────────────────────────
meter_id      STRING
read_at       TIMESTAMP
kwh           NUMERIC
quality_flag  STRING       -- "good", "estimated", "missing"
ingested_at   TIMESTAMP

reads_hourly  (partition by date)
─────────────────────────────────────────
meter_id  STRING
hour      TIMESTAMP
kwh       NUMERIC

reads_daily  (partition by date)
─────────────────────────────────────────
meter_id  STRING
day       DATE
kwh       NUMERIC

customers  (dim)
─────────────────────────────────────────
customer_id  STRING (PK)
name, email, address, plan_id
joined_on    DATE

tariffs  (SCD Type 2)
─────────────────────────────────────────
plan_id, kwh_price, fixed_charge, valid_from, valid_to, is_current

bills  (mart)
─────────────────────────────────────────
bill_id, customer_id, period_start, period_end, kwh_total, total_due, issued_at
```

### Risks I would call out

**1. Meter clock drift.** Devices report local time, sometimes wrong. The parser must normalize to UTC and treat the device time as a hint, not truth. Bills cross day boundaries if you trust device clocks blindly.

**2. The 1-second blast at the top of every hour.** When meters dump readings on the hour, traffic spikes. S3 + Lambda absorb this, but a database ingestion path would not. Designed around this.

**3. Estimated readings.** When a meter is offline, the head-end system fills the gap with an estimate. The bill must distinguish estimated from measured (the `quality_flag` column). Regulators care about this.

**4. Schema changes from the head-end vendor.** They update their format every year. A data contract and a strict schema check at the Lambda parser stops this from corrupting the curated layer.

### What I would NOT build on day one

* A streaming pipeline. The use cases all tolerate hourly latency.
* A separate Spark cluster. The volume does not need it. The warehouse handles aggregation.
* A real-time customer-facing dashboard. Nice to have, expensive to build, not asked for.

### Bonus follow-up the interviewer might throw

> *"What changes when you grow from 200,000 to 5 million meters?"*

The shape stays the same, but a few pieces get pressure:

* Lambda parsing gets expensive. Move to a Kinesis Firehose or a small Spark Streaming job.
* `reads_15min` is now 175 billion rows/year. Stays fine in BigQuery or Snowflake, but Redshift may struggle. Time partitioning + clustering on `meter_id` is now non-negotiable.
* The serving Postgres becomes a load problem. Shard by customer prefix, or move to DynamoDB.
* Forecasting moves from one nightly model to per-region models running in parallel.

The architecture survives the growth because we kept the raw layer untouched and the rollups well defined.
