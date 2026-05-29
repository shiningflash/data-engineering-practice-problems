## Solution 75: SQL vs NoSQL

### Short version you can say out loud

> "NoSQL" is not one thing. It is four different families: key-value, document, wide-column, and graph. Each fits different problems. For most new services, a normal SQL database like Postgres is still the right default. You go NoSQL when you have a specific access pattern that SQL handles poorly: massive write throughput, document-shaped data that fits naturally as JSON, key-value lookups at huge scale, or graph traversals that are awkward in SQL. The honest answer at most companies is "Postgres for the main app, plus a NoSQL store for the one or two things that need it."

### "NoSQL" is four different families

```
                       NoSQL umbrella
                       ──────────────
       ┌──────────────┬─────────────┬───────────────┬─────────┐
       ▼              ▼             ▼               ▼
   Key-Value     Document       Wide-Column      Graph
   (Redis,       (MongoDB,      (Cassandra,      (Neo4j,
   DynamoDB,     CouchDB,        Bigtable,        Neptune,
   Memcached)    Firestore)      HBase,           ArangoDB)
                                 ScyllaDB)

   Lookup by      Store JSON     Sparse columns,    Nodes and edges,
   key, get value.docs by id.    huge row scale.    fast traversal.
```

Saying "we should use NoSQL" without saying which is meaningless.

### The dimensions that matter

| Dimension                    | SQL                          | KV               | Document         | Wide-Column       | Graph            |
| ---------------------------- | ---------------------------- | ---------------- | ---------------- | ----------------- | ---------------- |
| Schema                       | Strict                       | None (opaque)    | Flexible         | Flexible          | Flexible         |
| Transactions                 | ACID, multi-row              | Single key       | Often single doc | Limited           | Limited          |
| Joins                        | Native                       | No               | No (denormalize) | No                | Native via edges |
| Range queries                | Native                       | No               | Limited          | Yes (partition)   | Limited          |
| Horizontal scale (writes)    | Harder (shard)               | Excellent        | Good             | Excellent         | Limited          |
| Operational complexity       | Medium                       | Low              | Medium           | High              | Medium           |
| Best at                      | General apps, OLTP           | Caches, sessions | App documents    | Time-series, logs | Relationships    |

### When SQL is the right call

* **General-purpose app.** Orders, users, payments, anything with multiple related entities.
* **You need transactions.** Money, inventory, anything where ACID guarantees matter.
* **You need joins.** Most reporting and business logic.
* **You don't know your access patterns yet.** SQL is forgiving. Schemas evolve.
* **Data fits on one machine, or a few.** Postgres on a beefy primary handles billions of rows fine.

For most new services, this is where you land.

### When KV is the right call

* **Pure lookup by key**, at huge scale or sub-millisecond latency.
* **Session stores** (login state).
* **Caches** (the most common NoSQL use).
* **Feature stores serving ML models** (Problem 22-style serving).
* **Pre-computed aggregates** keyed by user and date.

DynamoDB, Bigtable, Aerospike, Redis. You can put billions of items in and read them in single-digit milliseconds.

### When Document is the right call

* **Data is naturally tree-shaped**, with optional fields and arrays.
* **Schema changes frequently** and the application tolerates it.
* **You read documents whole and rarely query subfields.**

Examples: product catalogs, content management, user-facing UI state. MongoDB, Firestore, DocumentDB.

The trap: document stores look easy until you need to do cross-document analytics, and then you wish you had SQL.

### When Wide-Column is the right call

* **Massive writes**, especially time-series or event streams.
* **Reads by partition key**, often with a range on a clustering key.
* **You can model the data so reads are always "one partition."**

Cassandra, Bigtable, HBase, ScyllaDB. These are the LSM-tree (Problem 70) world. Great at write throughput; awkward for ad-hoc queries.

### When Graph is the right call

* **Relationships are the primary query**: "friends of friends," "shortest path," fraud rings.
* **SQL traversals would be deep recursive CTEs and slow.**

Neo4j, Neptune, ArangoDB. Smaller market but indispensable for the right use cases.

### What "scale" actually means

Saying "we need scale" without numbers is empty. Some milestones:

* **Postgres on a single beefy primary**: comfortable with 1-2 TB and 10,000 writes/sec.
* **Postgres with read replicas**: scales reads further, writes don't change.
* **Manual sharding (Problem 72)**: 10x writes, with care.
* **Cassandra / DynamoDB**: 100,000+ writes/sec out of the box, multi-region.
* **Bigtable**: millions of writes/sec.

For most apps, Postgres is enough until they have real revenue. Only the small minority that hit Cassandra-level write rates actually need it.

### Picking for the scenario

The team has a new service. Half want Postgres, half DynamoDB. Wrong question. The right questions:

* **What does the data look like?** Relational? Document-shaped?
* **What does the access pattern look like?** Lookups by id, ranges, joins?
* **What is the expected write volume in 1 year? In 3 years?**
* **Does it need transactions?**

For a typical new web service, the answers usually point to Postgres. DynamoDB is right when:

* The access pattern is "give me item by id" or "give me items in a partition by sort key."
* The service is serverless and wants single-digit-ms latency without operating a database.
* Write rate will reach tens of thousands per second.

Without these, the team is choosing on aesthetics, not problem.

### The "use both" pattern

Most production systems end up using both:

```
┌───────────────────────────────────────────────────────────┐
│  Application                                              │
│                                                           │
│   Postgres   ←  users, orders, payments, accounts         │
│                  (transactions, joins, the source of truth)│
│                                                           │
│   Redis      ←  session cache, hot reads                  │
│                                                           │
│   DynamoDB   ←  user activity log, feature store          │
│                                                           │
│   Elasticsearch  ←  full-text search                      │
└───────────────────────────────────────────────────────────┘
```

Each one does the job it is best at. Operationally heavier than one database, but much faster than forcing one database to do everything.

### Common mistakes interviewers want you to name

1. **Picking NoSQL "for scale" when scale is years away.**
2. **Treating NoSQL as one category.** KV and graph have nothing in common.
3. **Document store for relational data.** Joins-in-application code becomes hell.
4. **Postgres for global, write-heavy, multi-region.** Sharding is real work.
5. **Switching databases without measuring.** Most "Postgres is slow" stories are missing indexes.

### Bonus follow-up the interviewer might throw

> *"What about new databases like CockroachDB, TiDB, Spanner that claim to be both?"*

Distributed SQL databases give you SQL plus horizontal scaling. They are real and they work. The catch: they are more complex to operate, more expensive, and some SQL features are restricted (cross-region joins are slow, some isolation modes are limited). For a team that genuinely needs SQL at multi-region scale, they are great. For most teams, Postgres plus replicas plus one or two specialized stores is simpler and cheaper.
