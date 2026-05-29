---
id: 71
title: Read Replicas and Replication Lag
category: Databases
topics: [replicas, replication lag, read after write]
difficulty: Medium
solution: solution.md
---

# Problem 71, Read Replicas and Replication Lag

**Scenario:**
A team added a Postgres read replica to take pressure off the primary. Most queries got faster. But a new bug appeared: users update their profile, then refresh the page, and see their old profile for a few seconds. The team blames a frontend cache, but the cache is fine. You suspect replication lag.

In the interview, the question is:

> What are read replicas, what is replication lag, and how do you handle "read after write" correctly?

---

### Your Task:

1. Explain read replicas in one paragraph.
2. Describe replication lag and why it exists.
3. Walk through patterns to handle "read after write."
4. Cover when you would not use replicas.

---

### What a Good Answer Covers:

* Sync vs async replication.
* Eventual consistency on the replica.
* Read-after-write consistency patterns.
* Sticky reads, primary fallback, version checks.
* Use cases that genuinely need primary reads.
