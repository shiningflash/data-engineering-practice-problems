## Solution 73: Database Connection Pooling

### Short version you can say out loud

> Each Postgres connection is a separate backend process with its own memory. A few hundred connections is fine; a few thousand crushes the database. A connection pool keeps a small set of long-lived connections and hands them out to application requests as needed. The right pool size is small, often somewhere around 2 to 4 times the database's CPU core count, not "as many as we have requests." Raising max_connections to 1000 is rarely the answer because the database cannot actually serve 1000 concurrent queries — they just queue and fight for resources.

### Why a Postgres connection is expensive

Postgres uses one process per connection:

* Each connection forks a backend process.
* Each backend allocates ~10 MB of memory at minimum (work_mem, temp buffers, etc.).
* The OS schedules every backend even when idle.

100 connections = ~1 GB just for backends, mostly idle. 1000 connections = ~10 GB, plus serious context-switch overhead. The database spends more time managing connections than serving queries.

(MySQL is lighter per connection, using threads instead of processes, but the principle holds.)

### What a pool actually does

```
WITHOUT a pool
──────────────
App request 1  → open new connection → query → close
App request 2  → open new connection → query → close
...
1000 concurrent requests = 1000 connections.

WITH a pool
───────────
                     ┌─────────────────────────────┐
   1000 requests ──▶ │  Pool: 20 long-lived conns  │ ◀── 20 DB conns
                     │  Idle requests wait briefly │
                     └─────────────────────────────┘
```

The pool keeps a small set of connections open. Application requests borrow a connection, run the query, and return it. Requests that arrive when all connections are busy wait briefly.

Three big wins:

* The database is never overloaded.
* Connection creation cost (TLS, auth) is paid once, not per request.
* Predictable resource use under spikes.

### Where the pool lives

Two options.

**1. Application-side pool** (a library like HikariCP, SQLAlchemy's pool, asyncpg).

* Each app process has its own pool.
* Simple to set up.
* Total connections = pool_size × number_of_app_processes. Easy to overshoot.

**2. External proxy** (PgBouncer, PgCat, Odyssey, RDS Proxy).

* All app processes connect to the proxy.
* The proxy multiplexes onto a small set of real database connections.
* Best for "many small services" or serverless workloads.

For a small app, application-side pool is enough. For 50 services or 100 Lambda functions hitting one database, PgBouncer in front is almost mandatory.

### Transaction vs session pooling

PgBouncer offers three modes; the two that matter:

* **Session pooling**: a backend connection is held for the entire session. Safe but no multiplexing benefit.
* **Transaction pooling**: a backend connection is held only for one transaction. Multiplexes many app sessions onto few backends. Far higher throughput.

Transaction pooling is the win, but it requires the application not to use session-level features (prepared statements without protocol support, `SET` for the session, `LISTEN`/`NOTIFY`). Most modern code is fine; check before turning it on.

### How to size the pool

The most useful rule of thumb (HikariCP's, validated empirically): **pool_size ≈ (cores × 2) + effective_spindle_count**. For a modern SSD-backed cloud database with 8 cores, that's roughly 16-20 connections.

The intuition: the database can only truly run one query per core at a time. More connections than that just queue. Two-times CPU accounts for I/O wait, giving the CPU something to do while one query waits.

For most teams: pool of 10-30 is the right answer, not 1000.

### Why "raise max_connections" is rarely the fix

Raising max_connections from 100 to 1000 lets more apps connect, but the database still has only 8 cores. So:

* 1000 connections eat ~10 GB of memory just to exist.
* Queries pile up in the database, not in the application.
* Lock contention rises.
* Slow queries get even slower.

The "too many connections" error is usually a sign that the application pool is too large or that connections are leaking (held open after a request, never returned). Fixing those is cheaper than raising the limit.

### Diagnosing the scenario

The team has intermittent "too many connections" errors. The investigation order:

1. **Are connections leaking?** Check `pg_stat_activity` for connections in `idle in transaction` state for a long time. That is a leak.
2. **Is the application pool too large?** If each app has a 100-connection pool and there are 5 app instances, you have 500 connections trying to live on a 100-cap database.
3. **Is a single endpoint holding connections too long?** A slow query that ties up a connection for 5 seconds blocks others.
4. **Is there no pooler?** Each request opens a new connection. Add PgBouncer in front, problem disappears.

Almost every "too many connections" incident is one of these four.

### A note on serverless

Lambda, Cloud Functions, and Cloud Run can spin up thousands of instances during a spike. Each instance might want one or a few connections. The database gets crushed.

The pattern that works:

* Put a connection pooler (PgBouncer, RDS Proxy, Cloud SQL Auth Proxy) between serverless and database.
* Each function instance connects to the pooler.
* The pooler holds the much smaller set of real database connections.

This is the only way serverless and a relational database coexist at scale.

### Common mistakes interviewers want you to name

1. **Raising max_connections instead of investigating.** Treats the symptom.
2. **Oversized application pools.** Each microservice has 100 connections; the database is at 5000.
3. **No pool at all.** Every request opens fresh, slow.
4. **Connections held during external API calls.** A 3-second external call holds a database connection for 3 seconds for no reason.
5. **Transaction pool mode with session-level state.** Subtle bugs around `SET` or prepared statements.

### Bonus follow-up the interviewer might throw

> *"What is a healthy pool utilization in production?"*

* **Under ~50%**: pool is fine.
* **50-80%**: getting warm. Watch.
* **Above 80%**: requests start waiting; latency rises.
* **At 100%**: requests fail or time out.

Alert at 80% sustained, page at 95%. The fix is usually slow queries holding connections, not "add more connections." If usage is real and sustained, increase the pool size by 25%, and look at vertical scaling on the database.
