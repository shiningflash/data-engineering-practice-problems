## Solution 13: Data Lake vs Warehouse vs Lakehouse

### Short version you can say out loud

> A data lake is a big folder of files. You can dump anything in cheaply, but you have to bring your own tools to make sense of it. A warehouse is a managed database for analytics. It is fast, governed, has SQL out of the box, but costs more and is less flexible about file formats. A lakehouse is the newer idea of putting warehouse features (tables, transactions, schemas) on top of lake files, so you get most of the warehouse experience without paying warehouse prices. In real life most companies use all three at the same time, for different jobs.

### Picture it

```
DATA LAKE                       DATA WAREHOUSE
(S3, GCS, ADLS)                 (BigQuery, Snowflake, Redshift)

s3://bucket/raw/                ┌─────────────────────────────┐
  events/                       │ orders   customers   prices │
    year=2025/                  │ ─────    ─────────   ────── │
      month=05/                 │ ...      ...         ...    │
        day=14/                 │                             │
          part-001.parquet      │ managed tables, SQL,        │
          part-002.parquet      │ governance, ACID,           │
  logs/                         │ time travel, RBAC           │
  invoices/                     └─────────────────────────────┘
  random_csv_someone_uploaded/
                                Fast for analytics.
Anything goes.                  Costs more.
Cheap. Hard to govern.

                  LAKEHOUSE
                  (Delta Lake, Iceberg, Hudi on top of S3/GCS)

                  s3://bucket/curated/
                    orders/  ── managed by Iceberg/Delta
                      data/*.parquet
                      _metadata/  ── transactions, schema, snapshots

                  Warehouse-like behaviour (ACID, schema, time travel)
                  on top of cheap lake files. Query with Spark,
                  Trino, Databricks, Snowflake, BigQuery external.
```

### One paragraph each

**Data lake.** A data lake is just object storage (S3, GCS, Azure Data Lake) holding files in any format you like: CSV, JSON, Parquet, images, PDFs. It is cheap, infinitely scalable, and accepts anything. The downside is that there is no schema, no transactions, and no built-in query engine. If you want to query it, you bring your own tool (Athena, Spark, Trino). And because anyone can drop anything in, lakes can become "data swamps" without strict folder conventions and governance.

**Data warehouse.** A warehouse is a managed analytical database. You define tables, you load data in, you run SQL. The engine knows your schema, manages compression, builds statistics, handles indexes (or partitioning + clustering), enforces access control, and gives you ACID transactions. BigQuery, Snowflake, Redshift, Synapse are all in this category. Faster and friendlier than a lake for analytics, but you pay for the management.

**Lakehouse.** A lakehouse is a layer on top of a data lake that makes those files behave like warehouse tables. Three open formats lead the space: **Delta Lake**, **Apache Iceberg**, and **Apache Hudi**. They store data as Parquet files but add a metadata layer that gives you transactions, schema evolution, time travel (query the table as of last Tuesday), and updates and deletes. You get most of the warehouse experience while keeping the files open and queryable by many engines. Spark, Trino, Snowflake, BigQuery and Databricks can all read Iceberg now.

### What each one is good at

| Need                                           | Lake | Warehouse | Lakehouse |
| ---------------------------------------------- | ---- | --------- | --------- |
| Store anything cheaply, including non-tabular   | Yes  | No        | No        |
| Run SQL with sub-second latency                | No   | Yes       | Sometimes |
| ACID transactions on tables                    | No   | Yes       | Yes       |
| Time travel (query as of a past time)          | No   | Yes (limited) | Yes   |
| Schema enforcement and evolution               | No   | Yes       | Yes       |
| Multi-engine read (Spark, Trino, BigQuery, …)  | Yes  | No        | Yes       |
| Built-in governance, access control            | DIY  | Yes       | Partial   |
| Cost                                           | Lowest | Highest | Middle  |

### Where each fits in a real pipeline

```
              Raw events / files
                       │
                       ▼
                ┌───────────┐
                │  LAKE     │  raw, unprocessed, "everything that ever happened"
                └─────┬─────┘
                      │
                      ▼
                ┌───────────┐
                │ LAKEHOUSE │  cleaned, conformed, queryable, transactional
                └─────┬─────┘
                      │
                      ▼
                ┌───────────┐
                │ WAREHOUSE │  business marts, dashboards, BI
                └───────────┘
```

This three-layer setup is so common it has names: bronze (lake), silver (lakehouse), gold (warehouse), or just raw / staging / marts.

### The honest take on the "lakehouse" debate

The term is partly marketing. Databricks pushed it heavily. Critics point out that "putting a metadata layer on top of files" was already what Hive did 15 years ago. What is genuinely new is:

* The open table formats (Iceberg, Delta, Hudi) handle real ACID transactions, not just metadata.
* Cloud engines like BigQuery and Snowflake now read these formats directly, breaking the old "you have to use Spark on Databricks" lock-in.
* The economics actually work because object storage is so cheap.

So the idea is real, even if the word is overused. The practical question for a team is "do we keep growing the warehouse, or do we move some workloads onto Iceberg in our lake?" The honest answer is "depends on cost, scale, and how mixed your tooling is."

### Common confusions interviewers want you to clear up

1. **"Lake means unstructured."** Wrong. A lake can hold tidy Parquet tables. The point is *where* and *how managed*, not how messy.
2. **"Lakehouse replaces the warehouse."** Rarely true in practice. Warehouses are still better for sub-second BI on curated marts. Most teams use both.
3. **"Lake is free."** Storage is cheap, but query cost (Athena, Spark) can rival warehouse cost if you scan badly.
4. **"Iceberg is a database."** No, it is a table format spec. You still need an engine to read or write it.

### Bonus follow-up the interviewer might throw

> *"If you were starting from scratch today for a small startup, what would you pick?"*

For a small startup, the simplest answer is: land raw in cheap object storage, use a managed warehouse (BigQuery or Snowflake) for everything analytical, and only adopt Iceberg or Delta when warehouse costs become painful or you have multi-engine needs. Going lakehouse-first adds operational complexity that a five-person team usually does not need.
