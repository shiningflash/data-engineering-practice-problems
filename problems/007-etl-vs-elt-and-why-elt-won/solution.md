## Solution 7: ETL vs ELT and Why ELT Won

### Short version you can say out loud

> ETL means you extract data from the source, transform it on a separate machine, then load the clean result into the warehouse. ELT means you extract the raw data, load it straight into the warehouse first, and let the warehouse do the transform. The switch happened because warehouses got cheap, fast and elastic, so it stopped making sense to maintain a separate transform server.

### The two flows side by side

```
              ETL  (the old way)
┌────────┐    ┌──────────────────┐    ┌──────────┐
│ Source │───▶│ Transform server │───▶│Warehouse │
└────────┘    │ (Python, Spark,  │    │(clean)   │
              │  Informatica…)   │    └──────────┘
              └──────────────────┘

              ELT  (the modern way)
┌────────┐    ┌──────────┐    ┌─────────────────────┐
│ Source │───▶│Warehouse │───▶│ Same warehouse runs │
└────────┘    │ (raw)    │    │ transforms (dbt,    │
              └──────────┘    │ SQL, scheduled)     │
                              └─────────────────────┘
```

### One line definitions

* **ETL**: Extract from source, Transform on a separate engine, Load into warehouse.
* **ELT**: Extract from source, Load raw into warehouse, Transform inside the warehouse.

### What actually changed

Ten years ago, the warehouse was a precious, expensive box. You did not want to land raw, messy, oversized data inside it because storage cost real money and compute was fixed. So teams ran a transform layer outside the warehouse to make the data small and clean before it ever touched the box.

Then three things changed:

1. **Storage got cheap.** Object storage and columnar warehouses made it cost almost nothing to keep raw data.
2. **Compute got elastic.** BigQuery, Snowflake, Redshift Serverless, Databricks. You only pay for what you scan or use.
3. **SQL on warehouses got really powerful.** Window functions, JSON parsing, arrays, geography, machine learning. You can do almost everything the old Python ETL did, in SQL, in the warehouse.

That made it cheaper and simpler to dump raw data in and transform with SQL. dbt arrived and gave teams a way to organize that SQL like real software (tests, dependencies, documentation), and ELT became the default.

### Why teams prefer ELT today

| Reason                          | What it means in practice                                          |
| ------------------------------- | ------------------------------------------------------------------ |
| Raw data is preserved           | You can always rebuild a transform if the business logic changes   |
| Transforms are just SQL         | Analysts can read and change them, not just engineers              |
| One platform, one bill          | No separate Spark cluster to babysit                               |
| Easy to version with dbt        | Tests, lineage and docs out of the box                             |
| Faster iteration                | A new column is a pull request, not a deploy                       |

### When ETL is still the right call

ELT is the default, but it is not always correct.

1. **Sensitive data that must never enter the warehouse.** Card numbers, raw health records, regulated PII. You strip or tokenize these *before* loading. The transform has to happen outside the warehouse.
2. **Huge volumes of useless raw data.** If 90 percent of the source is junk you will never query, you can save real money by filtering at ingest. For example, dropping debug log lines before loading.
3. **Strict compliance boundaries.** Some regulators want only the cleaned, approved version of the data in the analytical store. Raw stays in the source system.
4. **Real time enrichment.** Stream processing (Flink, Kafka Streams) transforms on the fly because waiting for a batch warehouse run is too slow.

### The hybrid that most teams actually run

In real life, it is rarely pure ELT. Most teams use:

* **Light ETL at ingest** for PII masking and obvious filtering.
* **ELT inside the warehouse** for business logic, joins, aggregates and modeling.
* **Stream processing on the side** for the few use cases that need sub-minute latency.

If the interviewer pushes you, this is the honest answer: "we say ELT, we mean ELT for the analytical layer, but we still do some transforms before landing for privacy and cost reasons."

### Bonus follow-up the interviewer might throw

> *"If raw data is in the warehouse, isn't that a security risk?"*

Yes. That is why mature ELT setups land raw data into a **restricted dataset** with row and column level access controls. Only a small group can query the raw layer. The downstream "clean" and "marts" layers are what most analysts touch. Tokenization or hashing happens at the ingest step for the truly sensitive fields, so they never appear in plaintext anywhere in the warehouse.
