## Solution 8: OLTP vs OLAP

### Short version you can say out loud

> OLTP is the database behind the app. It is built to handle many small reads and writes very fast, like "fetch this user" or "insert this order." OLAP is the database behind reporting. It is built to scan huge amounts of data and compute aggregates, like "revenue by region by month." They store data in completely different ways, which is why the same query can take 50ms in one and 50 seconds in the other.

### Picture it

```mermaid
flowchart TB
    subgraph LEFT["OLTP, row store<br/>Postgres, MySQL, SQL Server"]
        direction TB
        R1([row 1: id, name, email, ...])
        R2([row 2: id, name, email, ...])
        R3([row 3: id, name, email, ...])
        R1 -.- R2 -.- R3
    end

    subgraph RIGHT["OLAP, column store<br/>BigQuery, Snowflake, ClickHouse"]
        direction TB
        C1([id column: 1, 2, 3, ...])
        C2([name column: A, B, C, ...])
        C3([email column: a@, b@, c@, ...])
    end

    style LEFT fill:#fef3c7,stroke:#a16207,color:#713f12
    style RIGHT fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    style R1 fill:#ffffff,stroke:#a16207
    style R2 fill:#ffffff,stroke:#a16207
    style R3 fill:#ffffff,stroke:#a16207
    style C1 fill:#ffffff,stroke:#1e40af
    style C2 fill:#ffffff,stroke:#1e40af
    style C3 fill:#ffffff,stroke:#1e40af
```

Row store: best at *give me row id=42* and *insert this new order*.
Column store: best at *SUM(amount) by month* and *reading 5 columns out of 100*.

### What each one is, in one paragraph

**OLTP (Online Transaction Processing)** powers the running application. It handles thousands of tiny operations per second: insert this order, update this balance, fetch this user. The data is stored row by row, so it can quickly grab or update a complete record. It uses indexes (usually B-tree) for fast lookups by id, and it enforces ACID transactions so the business never sees a half-applied change.

**OLAP (Online Analytical Processing)** powers reporting, dashboards and analytics. It handles a small number of huge queries: total revenue by country last year, daily active users for the last 12 months. The data is stored column by column, so when you select 3 columns out of 100, it only reads those 3. It is optimised for big scans and aggregates, not for updating one row at a time.

### The same data, two storage formats

Imagine an `orders` table with columns: `id, customer_id, status, amount, country, created_at`.

A query like `SELECT SUM(amount) FROM orders WHERE country = 'SG'` does this:

* On an **OLTP row store**: read every row on disk, all six columns of each row, even though we only care about two of them. Slow.
* On an **OLAP column store**: read only the `country` and `amount` columns. The other four never touch the disk. Fast.

Now flip it. A query like `SELECT * FROM orders WHERE id = 12345`:

* On an **OLTP row store**: the B-tree index jumps straight to the row, one disk seek. Done in milliseconds.
* On an **OLAP column store**: there is no row index. The engine may scan a partition or block range. Easily 1000x slower than the OLTP version.

So neither one is "better." They are tuned for opposite workloads.

### Side by side

| Aspect | OLTP | OLAP |
| --------------------- | ----------------------------------- | ------------------------------------- |
| Typical user | The application | Analysts, BI tools, ML pipelines |
| Typical query | Read or update one row | Aggregate millions of rows |
| Storage layout | Row-oriented | Column-oriented |
| Indexes | Many (primary key, foreign keys) | Few or none (uses partition + cluster)|
| Updates and deletes | Frequent | Rare, often batch |
| Concurrency | Thousands of small transactions | Few large queries |
| ACID | Strict | Eventual or relaxed in many engines |
| Data freshness | Real time | Minutes to hours behind |
| Examples | Postgres, MySQL, SQL Server, DynamoDB | BigQuery, Snowflake, Redshift, ClickHouse |

### Why we keep them separate

The story at the top of the problem is the answer: if you run a long analytical query on the production database, you slow down the app for real users. Even if you don't, you push the database's cache out, hurting every other small query. The whole reason warehouses exist is so analytical work has its own home.

A typical company therefore runs:

```mermaid
flowchart LR
    APP([Application<br/>reads + writes])
    OLTP([OLTP database<br/>Postgres, MySQL])
    SYNC([CDC, daily batch, Fivetran])
    OLAP([OLAP warehouse<br/>BigQuery, Snowflake])
    BI([Analysts, dashboards, ML])

    APP <--> OLTP --> SYNC --> OLAP <--> BI

    style APP fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    style OLTP fill:#fef3c7,stroke:#a16207,color:#713f12
    style SYNC fill:#fed7aa,stroke:#c2410c,color:#7c2d12
    style OLAP fill:#dcfce7,stroke:#15803d,color:#14532d
    style BI fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
```

### Bonus follow-up the interviewer might throw

> *"What about HTAP, like CockroachDB or TiDB? Aren't they both?"*

HTAP (Hybrid Transactional and Analytical Processing) systems try to do both in one box, usually by keeping a row store for writes and a column store replica for analytics inside the same cluster. They work well for moderate scale and reduce operational complexity, but for very large analytical workloads most companies still keep a dedicated warehouse, because a purpose built engine like BigQuery or Snowflake is still cheaper and faster at that job.
