## Problem 70: B-Tree vs Hash vs LSM Tree

**Scenario:**
A teammate is choosing a database for a new high-write service and is reading marketing pages comparing different storage engines. They keep seeing "B-tree" in the Postgres/MySQL docs and "LSM tree" in Cassandra/RocksDB. They ask you what these actually are and why one is used here and one there.

In the interview, the question is:

> Explain B-tree, hash index, and LSM tree in plain words. When does each one shine?

---

### Your Task:

1. Explain each structure in one paragraph.
2. Show the workload it is best at.
3. Compare on read, write, and range queries.
4. Mention real systems that use each.

---

### What a Good Answer Covers:

* B-tree as balanced sorted tree, great for range queries.
* Hash index as O(1) lookups, bad at ranges.
* LSM tree as append-only writes with periodic compaction, great for write-heavy.
* Write amplification trade-off.
* Why most databases pick one as default and offer the others.
