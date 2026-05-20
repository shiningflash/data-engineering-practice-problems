## Solution 38: Store Partner Files in S3 or the Warehouse?

### Short version you can say out loud

> Both. The standard pattern is "land raw files in S3, load curated tables into the warehouse." S3 is the audit trail and the safety net for reprocessing. The warehouse is where analytics actually happens. Loading directly into the warehouse without keeping the raw file is the failure mode you want to avoid, because it makes reprocessing painful and audit impossible. The cases where you skip S3 are rare and small-volume.

### Questions I would ask first

Before answering, I want to know:

1. **Do we keep the raw file for audit or compliance?** If yes, S3 is non-negotiable.
2. **How often will we need to reprocess?** If schemas evolve or transforms change, having the raw file saves hours.
3. **What does "the warehouse" cost vs S3?** Big difference at scale.
4. **Who else will read the raw file?** Other teams, ML pipelines, debugging.
5. **How structured is the data?** Clean tabular CSV is easy to load directly; nested or messy JSON is not.

For the 30 GB / 50 files / daily scenario, the answer is clearly **land in S3 first, then load curated parts into the warehouse**.

### The standard pattern

```
Partner SFTP
     │
     │ scheduled pull (or partner pushes)
     ▼
┌──────────────────────────┐
│  S3 (raw zone)           │   immutable, append-only,
│  s3://partner-raw/       │   partitioned by date
│    date=2025-05-14/      │
│      file_001.csv        │
│      file_002.csv        │
│      ...                 │
└──────────┬───────────────┘
           │
           │ scheduled load job
           ▼
┌──────────────────────────┐
│  Warehouse (raw layer)   │   one-to-one mirror,
│  raw.partner_xxx         │   schema enforced, partitioned
└──────────┬───────────────┘
           │
           │ dbt transforms
           ▼
┌──────────────────────────┐
│  Warehouse (marts)       │   business-ready, joined,
│  marts.customers, etc.   │   aggregated
└──────────────────────────┘
```

Three layers. Each one has a clear purpose, and you can rebuild every layer below from the layer above.

### Why S3 first

* **Cheap.** ~$0.023/GB/mo on S3 vs much more in many warehouses for raw storage at the same bytes. For 30 GB/day × 365 days = ~11 TB/year. On S3 that is ~$250/year. In a warehouse the same volume costs many times more, especially if columnar compression cannot help the raw shape.
* **Reprocessable.** If a transform bug ships, we can reload from S3. If the file landed only in the warehouse and the load mangled it, the original is gone.
* **Auditable.** "Show me exactly what the partner sent us on May 14" is a one-line answer from S3.
* **Multi-consumer.** Other teams (ML, ad-hoc Python) can read S3 directly with Athena, BigQuery external tables, or Spark.

### Why also load into the warehouse

* SQL is the lingua franca of analysts.
* The warehouse is built for fast scans, joins, and aggregates.
* dbt models, dashboards, and metric definitions live there.
* External tables (BigQuery external, Athena, Snowflake external stages) work but are slower and less optimized than native warehouse tables.

The raw warehouse table is a near-copy of the file, with proper types and a partition column. It is what dbt builds models on top of.

### Schema evolution: the S3-first payoff

A few months in, the partner adds a new column. With raw files in S3:

1. Update the warehouse raw table schema to include the new column.
2. Backfill from S3 (the historical files have the new column once it started appearing).
3. Existing transforms continue to work because the column is nullable for older dates.

With warehouse-only:

1. New column appears. Load might fail silently or coerce. You realize a week later.
2. The old data does not have the column at all. No way to backfill.

The S3 raw layer is the only reason schema evolution feels manageable in real pipelines.

### When I would consider loading directly to the warehouse

There are a few cases where the S3 step is overkill:

* **Tiny files** (a few MB), low frequency (weekly), and you have a clear lineage in the warehouse itself.
* **Highly structured database extracts** (a daily CDC dump from Postgres) where the warehouse load tool already keeps a snapshot.
* **Sensitive data** that legally cannot land in object storage until cleaned. Then a transient stream loads, cleans, and writes both raw-cleaned and curated.

For 30 GB/day of partner CSV, none of these apply.

### File layout I would actually use

```
s3://partner-raw/source=partner_a/date=2025-05-14/
  ingested_at=2025-05-14T05-12-03Z/
    customers.csv
    orders.csv
    products.csv
  _manifest.json     ← list of files in this batch, with sizes/hashes
  _SUCCESS           ← written last, only when all files landed
```

Two practical details:

* `_SUCCESS` marker so consumers only process complete batches.
* `_manifest.json` with file hashes catches partial or corrupt uploads.

### Cost rough math

For the scenario: 30 GB × 365 = ~11 TB/year on S3 ≈ $250/year. Trivial.

Loaded to the warehouse: depends on the warehouse and pricing model, but typically 5-20x that for raw storage, and you also pay for compression overhead and metadata.

Plus, warehouse storage is much harder to delete safely. S3 has clear lifecycle rules: after N months, transition to cheaper tiers; after Y months, delete.

### What about CSV-specific concerns

CSVs are the worst format for the warehouse:

* No types until parsed.
* Quoting rules vary.
* Different files may have different headers.

The standard pattern: land CSV in S3. The load step converts to Parquet on the way to the warehouse, or uses a `LOAD CSV` with explicit schema. Either way, the warehouse never deals with raw CSV strings at query time.

### Common mistakes interviewers want you to name

1. **Skipping S3 to "save time."** Saves hours, costs days when reprocessing.
2. **Putting raw in the warehouse and considering it the source of truth.** It is a derivative.
3. **Deleting raw S3 files after loading.** Loses the audit trail.
4. **No partitioning on the S3 path.** Future reprocess scans all data.
5. **No `_SUCCESS` marker.** Consumer reads partial uploads.

### Bonus follow-up the interviewer might throw

> *"What if the partner only sends parquet files, beautifully partitioned?"*

Even better. Skip the conversion step. Land in S3, then use external tables in the warehouse if the warehouse supports them well. You may not even need to "load" into the warehouse for some use cases; external tables on parquet can be fine. The raw-in-S3 principle still applies.
