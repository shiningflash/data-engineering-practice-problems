## Solution 71: Read Replicas and Replication Lag

### Short version you can say out loud

> A read replica is a second copy of the database that follows the primary by replaying its changes. It takes read load off the primary. The catch is replication lag: the replica is always a little behind, usually milliseconds to seconds. If a user writes to the primary and immediately reads from the replica, they may see the old state. The fix is "read after write" patterns: route writes' immediate follow-up reads to the primary, or wait until the replica catches up. Most production bugs in replica-using systems come from missing this.

### How replication works

```
        Application
           │
           │ writes
           ▼
   ┌──────────────┐
   │   PRIMARY    │
   └──────┬───────┘
          │ stream of changes (WAL / binlog)
          ▼
   ┌──────────────┐       ┌──────────────┐
   │  REPLICA 1   │  ...  │  REPLICA N   │
   └──────────────┘       └──────────────┘
          ▲                       ▲
          │                       │
          │ reads                 │ reads
       Application             Application
```

The primary writes a stream of changes (Postgres calls it WAL, MySQL calls it binlog). Each replica subscribes to this stream and replays the changes locally. Replicas are typically read-only.

### Sync vs async replication

* **Asynchronous (default in most setups)**: the primary commits and acknowledges the client before the replicas have applied the change. Fast. The replica is behind.
* **Synchronous**: the primary waits for at least one replica to confirm the change before acknowledging. Safer, slower, and the primary blocks if all replicas are unhealthy.
* **Semi-sync**: middle ground — wait briefly, then continue.

Most teams run async because the latency hit of sync is significant and the lag is usually fine.

### What replication lag actually is

It is the time between "the primary committed this change" and "the replica has applied this change." Typical numbers:

* Healthy network, light writes: tens of milliseconds.
* Heavy write spike: seconds.
* Replica that fell behind during maintenance: minutes or worse.

You can measure it (`SELECT pg_last_wal_replay_lag()` in Postgres, `SHOW SLAVE STATUS` in MySQL). Set an alert at a threshold that matters for your app.

### The "read after write" problem

The scenario:

```
T0  Client: UPDATE profile SET name = 'Amirul' WHERE id = 42;
T0+1ms  Primary commits.
T0+2ms  Client: SELECT * FROM profile WHERE id = 42;
        Router sends this to replica.
T0+2ms  Replica still on the old version. Returns 'old name'.
```

User: "I just saved! Why is it showing the old name?"

### Four ways to fix it

**1. Send the read to the primary if it's right after a write.**

The simplest pattern. The application knows it just wrote, so it routes the next N seconds of reads for that user to the primary.

```python
def write_profile(user_id, data):
    primary.execute(...)
    cache.set(f"recently_wrote:{user_id}", True, ttl=30)

def read_profile(user_id):
    if cache.get(f"recently_wrote:{user_id}"):
        return primary.query(...)
    return replica.query(...)
```

Cheap to implement, solves 95% of cases.

**2. Wait for the replica to catch up.**

After a write, the primary returns a "log position" (LSN in Postgres). The application can ask the replica "have you applied up to LSN X?" and wait until yes.

```sql
-- after write, primary returns its current LSN
SELECT pg_current_wal_lsn();   -- e.g. '0/4ABC123'

-- on the replica, before reading
SELECT pg_last_wal_replay_lsn() >= '0/4ABC123';
```

This is the strongest "read your writes" guarantee but adds latency.

**3. Session stickiness.**

Route all queries from one session (or one user, in a short window) to the same database. If they always go to the primary, no lag. If they always go to the same replica, the user at least sees a consistent view of the world.

Simple, common with connection routers and proxies.

**4. Application-level versioning.**

The application tracks the version of the user's data ("I last saw version 17"). On read, if the replica returns an older version, retry against the primary.

```python
new_version = primary.update(...)
data, ver = replica.select(...)
if ver < new_version:
    data, ver = primary.select(...)
```

Best when you want a generic mechanism that does not require a router.

### When to NOT use a replica

* **Money flows.** A transfer's confirmation page should read from the primary. Stale reads on balances cause customer escalations.
* **Auth state.** Login, password change, session creation. Lag here is a security risk in some scenarios.
* **Anything where stale data is harmful for seconds.** Permission checks right after a role change.

For these, just use the primary. The replica is for everything else.

### What the team should do for the scenario

Cheapest fix: pattern 1 (sticky to primary for N seconds after a write on the same user). Add a "recently wrote" cache, route reads to primary if set. 30-second TTL is usually enough.

Longer-term: build a small read-routing helper used everywhere, so this is centralized and not re-implemented per feature.

### Replicas for analytics

A common second use case: point your warehouse loader at the replica, not the primary. The replica handles the heavy daily read traffic without slowing down the production application. Lag of minutes is irrelevant for nightly batches.

### Multi-region replicas

Reads in Singapore, primary in Frankfurt. The Singapore replica is fast for reads (low latency to local users). Writes still go to Frankfurt (high latency from Singapore). Lag is dominated by network round trips between regions, often 100+ ms.

For write-heavy global apps, this leads to multi-primary or "Spanner-style" systems with serialized commits — much more complex. Single primary plus regional replicas is the simplest 80% solution.

### Common mistakes interviewers want you to name

1. **No "read after write" handling.** Users see their own writes lag.
2. **Routing all reads to replicas blindly.** Auth and money break.
3. **Ignoring replication lag.** A replica that fell 10 minutes behind is silently giving wrong answers.
4. **No alert on lag.** First sign of trouble is a customer complaint.
5. **Adding a replica to "scale writes."** Replicas scale reads, not writes.

### Bonus follow-up the interviewer might throw

> *"What if you need to scale writes, not just reads?"*

Replicas don't help. Options:

* **Sharding** (Problem 72): split the data across multiple primaries.
* **A different database** designed for distributed writes (Cassandra, CockroachDB, Spanner).
* **Workload partitioning**: move some writes to a separate database (e.g., audit logs to a separate cluster).

Each is a real project. None is "add a replica."
