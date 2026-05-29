## Solution 70: B-Tree vs Hash vs LSM Tree

### Short version you can say out loud

> B-trees are balanced sorted trees on disk. They are great for both point lookups and range queries, which is why Postgres, MySQL InnoDB, and SQL Server use them as the default. Hash indexes are O(1) lookups but cannot do ranges and cannot sort. LSM trees write everything in append-only sorted batches and merge them in the background. They are amazing for write-heavy workloads but read latency is more variable. Cassandra, RocksDB, LevelDB, ScyllaDB, and many others use LSM. Choosing between them is mostly about your read/write ratio and whether you need range scans.

### The three structures, drawn

```
B-TREE
──────
Balanced tree of sorted keys. Reads walk down the tree (~3-5 disk reads).
Range queries walk the leaves in order.

             [50]
           /      \
        [20,30]  [70,80]
        /  |  \   / | \
       10 25 35 60 75 90

Best for: read-heavy and balanced workloads, range queries.
Trade-off: writes touch the tree; updates can require rebalancing.


HASH INDEX
──────────
Hash(key) → bucket → row.

Key "alice@x.com" → hash → bucket 7 → row at byte offset 8421984

Best for: pure equality lookups.
Bad at: ranges (no order), prefix searches.


LSM TREE (Log-Structured Merge)
───────────────────────────────
Writes go to memory (memtable). When full, flushed to disk as a sorted
file (SSTable). New SSTables accumulate; background process merges
them into larger, fewer SSTables (compaction).

Memory    [memtable: latest writes, sorted]
   │ flush
   ▼
Disk      L0: [sst-1] [sst-2] [sst-3]   (recent, small)
          L1: [sst-A] [sst-B]            (compacted, larger)
          L2: [sst-X]                    (very large, infrequent)

Best for: write-heavy workloads.
Reads must check multiple SSTables (bloom filters help).
```

### Side by side

| Property             | B-tree                  | Hash index           | LSM tree                  |
| -------------------- | ----------------------- | -------------------- | ------------------------- |
| Point lookup         | O(log N) — fast         | O(1) — fastest       | O(log N) per level — fast |
| Range scan           | Excellent               | No                   | Good                      |
| Sequential write     | Slow (random IO)        | Slow                 | Fast (sequential IO)      |
| Random write         | Medium                  | Medium               | Fast (append)             |
| Write amplification  | Medium                  | Medium               | High (compaction)         |
| Read amplification   | Low                     | Low                  | Higher (check many SSTs)  |
| Space amplification  | Low (in-place)          | Low                  | Higher (multiple copies)  |
| Used by              | Postgres, MySQL, SQL Server, SQLite | Some specialized | Cassandra, RocksDB, LevelDB, ScyllaDB, DynamoDB |

### When B-tree shines

* Mixed workload: more reads than writes, or balanced.
* Range scans (`WHERE created_at BETWEEN ...`, `ORDER BY ... LIMIT 100`).
* Strong consistency needs (most B-tree systems are single-leader, ACID).
* Most OLTP applications.

### When Hash shines

* Pure equality lookups, no ranges (think a session cache).
* In-memory data structures (Python dicts, Redis HSET).
* Postgres has a hash index type but it is rarely used because B-tree covers the same case plus more.

### When LSM shines

* Write throughput is the bottleneck (millions of writes/sec).
* Time-series, logs, metrics, event streams.
* Multi-region or multi-tenant systems with heavy ingest.
* Workloads where range scans on partition keys are normal.

### The compaction trade-off

LSM's strength (fast writes) comes with the cost of compaction:

* Writes are sequential and fast.
* But the system must periodically merge SSTables in the background.
* That compaction reads and rewrites data many times over its life. This is "write amplification."

In practice, an LSM may write the same byte to disk 5-20 times across its lifetime. The benefit is that the foreground write path stays fast and predictable.

This is also why LSM systems care a lot about disk durability rating (SSD endurance) — they write more.

### A common confusion: "isn't Postgres an LSM?"

No, Postgres is a B-tree-based MVCC database. New row versions are written in place, with a hidden transaction id (xmin/xmax). Old versions are cleaned up by vacuum.

People confuse it with LSM because both use write-ahead logs (WAL). WAL is a durability technique, not a storage structure. B-tree, LSM, and hash-based engines all use a WAL.

### Which would I pick for the scenario

The teammate is choosing for "high-write." A few clarifying questions:

* What does the read pattern look like? Random key lookups, or scans?
* Is there a need for SQL joins?
* How critical is sub-millisecond read latency?

Recommendation matrix:

| If they need ...                                          | Pick                |
| --------------------------------------------------------- | ------------------- |
| SQL, transactions, joins, plus moderate write rate        | Postgres / MySQL    |
| Massive write throughput, multi-region, simple queries    | Cassandra / Scylla  |
| KV store with predictable latency, embeddable             | RocksDB / LevelDB   |
| Time-series with cheap retention                          | Specialized TSDB (which use LSM under the hood) |

"High-write" alone is not enough. Read shape and consistency needs decide.

### Common mistakes interviewers want you to name

1. **Picking LSM for SQL workloads.** Joins on LSM stores are awkward.
2. **Hash indexes for range queries.** Doesn't work, period.
3. **Ignoring write amplification.** SSDs wear out faster on LSM-heavy workloads.
4. **Assuming "NoSQL is faster."** Depends entirely on the workload.
5. **Treating these as exclusive.** Many databases let you choose an index type per table or column.

### Bonus follow-up the interviewer might throw

> *"What about LSM-tree systems that also support SQL, like ScyllaDB or CockroachDB?"*

They exist and they work. ScyllaDB and Cassandra speak SQL-ish (CQL) but with restrictions. CockroachDB and TiDB layer a SQL engine on top of an LSM key-value store (RocksDB or similar). They give you SQL + horizontal scalability + LSM write throughput, but the joins and transactions still have constraints. For most teams, a Postgres replica plus a separate Cassandra for the write-heavy part is simpler than running a brand new distributed SQL system.
