## Problem 73: Database Connection Pooling

**Scenario:**
A team's Postgres database keeps hitting "too many connections" errors during traffic spikes. The error is intermittent; under normal load the app is fine. Someone proposes "raising max_connections from 100 to 1000." You suspect that is the wrong fix.

In the interview, the question is:

> Why does connection pooling exist, how do you size a pool, and why is raising max_connections rarely the right answer?

---

### Your Task:

1. Explain what a Postgres connection costs.
2. Define a connection pool.
3. Walk through sizing.
4. Cover where the pool lives (app side vs proxy side).

---

### What a Good Answer Covers:

* Backend process per connection in Postgres.
* Memory and CPU cost per connection.
* PgBouncer and similar proxies.
* Transaction vs session pooling.
* How to compute a reasonable size.
