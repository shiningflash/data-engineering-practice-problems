---
id: 12
title: Parquet vs CSV vs JSON
category: Fundamentals
topics: [Parquet, CSV, JSON, columnar storage]
difficulty: Easy
solution: solution.md
---

# Problem 12, Parquet vs CSV vs JSON

**Scenario:**
Your team is choosing the storage format for a 5 TB events archive in S3. One engineer wants CSV "because everything reads it." Another wants JSON "because that's how the events arrive." You suggest Parquet. The team has not used it before and asks you to explain.

In the interview, the question is:

> When would you use Parquet, CSV, or JSON for storing data, and how would you explain Parquet to someone who has never heard of it?

---

### Your Task:

1. Explain the three formats in plain words.
2. Compare them on size, query speed, schema, and tooling.
3. Explain why Parquet is so popular for analytics.
4. Say when you would actually pick CSV or JSON over Parquet.

---

### What a Good Answer Covers:

* Row-oriented vs column-oriented storage.
* Compression and predicate pushdown.
* The schema-on-write vs schema-on-read difference.
* Real numbers: same dataset in CSV vs Parquet sizes.
* Honest cases where Parquet is the wrong call.
