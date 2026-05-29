## Solution 72: Sharding and Picking a Shard Key

### Short version you can say out loud

> Sharding means splitting one table across multiple databases, each holding a slice of the data. The shard key decides which row goes where. The two big traps are hot shards (one shard gets most of the traffic) and resharding pain (moving rows when you grow or shrink). For a users table, hashed `user_id` is almost always the right call: it spreads writes and reads evenly, and the common query "fetch this user" is a single-shard lookup. `country` sounds reasonable but creates massive hot shards for the US or China. `created_at` is the worst: every new write hits the same shard, and old shards get cold.

### What sharding actually does

```
Before
──────
   ┌──────────────┐
   │   PRIMARY    │   2 billion rows
   └──────────────┘

After (4-way sharding)
──────────────────────
   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
   │ Shard 1│  │ Shard 2│  │ Shard 3│  │ Shard 4│
   │ ~500M  │  │ ~500M  │  │ ~500M  │  │ ~500M  │
   └────────┘  └────────┘  └────────┘  └────────┘
```

Each shard is an independent primary (often with its own replicas). A router (your application or a proxy) decides which shard a query goes to, based on the shard key.

### Hash vs range sharding

* **Hash sharding**: `shard = hash(key) % N`. Random distribution. No hot spots if the key has enough variety. Bad for range scans (`WHERE created_at BETWEEN ...` hits all shards).
* **Range sharding**: shards own ranges (`users 1-500M` on shard 1, etc.). Good for range scans. Hot spots if writes are concentrated in one range (newest rows always on the last shard).

For a users table with point lookups by id, hash sharding wins. For time-series, range sharding can be fine if writes are well-distributed.

### Evaluating the three candidates

**1. `user_id` (hash).**

* Even distribution: a random hash of integer ids spreads evenly.
* Point lookup "fetch user 1234" is one shard. Fast.
* Most queries are by `user_id`, so they hit one shard.
* Resharding hurts (every doubling of shards moves ~half the rows), but rare.

**Verdict: usually right.**

**2. `country` (hash or range).**

* Sounds neat: "all SG users together, all US users together."
* Hot shards: the US shard is huge, the Liechtenstein shard is tiny.
* Cross-country queries fan out.
* Users moving country (Problem 10 SCD2 territory) breaks the shard mapping.

**Verdict: almost always wrong for users.**

**3. `created_at` (range).**

* New writes always hit the newest shard. That shard is on fire; the others are idle.
* "Fetch user 1234" requires scanning all shards (we don't know when they joined).
* Old shards are read rarely. Wasted resources.

**Verdict: this is the textbook bad shard key.**

### My pick: hash of user_id

It is boring and it works. For a 2 billion user table:

* 32 shards × ~60M rows each.
* Each shard fits in a normal-sized Postgres primary.
* Writes spread evenly.
* The hot query path (`WHERE user_id = X`) is a single-shard lookup.

The shard count is usually a power of 2 to make remapping easier.

### The hot shard story

The classic warning: even with a "good" key, one user can be hot.

If a single user generates 50% of write traffic (a celebrity on a social app, a high-frequency trading account on a finance app), the shard that owns that user_id is overloaded.

Fixes:

* **Don't put per-event data on the user shard.** Events go on an event shard keyed by event id or hash.
* **Sub-sharding the hot user.** Their data is split further. Application has to be aware.
* **Cache aggressively.** Reads are 99% from cache; only writes hit the shard.

In a users table this is rare. Most users have similar activity. The hot-shard problem is much worse for tables like `events`, `messages`, or `transactions` if you key by user.

### Cross-shard queries

The pain of sharding is queries that need data from multiple shards.

* "Top 100 users by spend." Has to scan every shard, then merge.
* "Count of users in SG." Has to query every shard.

Patterns to mitigate:

* **Denormalize aggregates** into a separate, smaller summary table.
* **Run analytical queries against the warehouse**, not the sharded OLTP.
* **Use a fan-out + merge service** for queries that genuinely need cross-shard data.

If the application needs many cross-shard queries, sharding is the wrong tool.

### Resharding pain

Eventually, you outgrow the shard count and have to add more shards. This is the second hardest problem (after picking the key).

* **Naive remap**: `hash % N` → `hash % 2N`. About half the rows move. Painful.
* **Consistent hashing**: shards own ranges of the hash space. Adding a shard moves only one shard's worth of rows. Standard practice now.
* **Virtual shards**: 1024 "logical shards" mapped to physical shards. You move logical shards around to add capacity. Common in Vitess, MongoDB sharding.

Plan for resharding from day one. Pick a hashing scheme that makes growth cheap.

### Multi-tenant sharding

If users belong to organizations, you might key by `org_id` instead of `user_id`. All users in one org live on the same shard. This makes "all queries about my company" one-shard, which is a huge win.

But beware: a giant customer becomes a hot shard. You pay them attention, dedicate a shard, or sub-shard.

### When NOT to shard

Sharding is operationally expensive. Before you reach for it, check:

* Are read replicas enough?
* Is the bottleneck really writes, or is it badly tuned indexes / connection pool / vacuum?
* Could you move some tables to a separate database (vertical partitioning)?
* Can you archive cold data?

Many "we need to shard" conversations end with "we tuned indexes and added a replica, and it's fine for two more years."

### Common mistakes interviewers want you to name

1. **Sharding by `created_at`.** Last shard always hot.
2. **Sharding by `country`.** Skewed forever.
3. **Naive hash without consistent hashing.** Resharding moves everything.
4. **Sharding too early.** Premature complexity.
5. **Sharding without changing how queries work.** Cross-shard queries become silent slowness.

### Bonus follow-up the interviewer might throw

> *"What about distributed SQL databases like CockroachDB or Spanner? Do they make this irrelevant?"*

Partly. They auto-shard under the hood, so the application doesn't pick a key explicitly. But the same physical concerns exist: hot ranges, cross-region writes, large writes triggering rebalance. The complexity moves from your application to the database, but it doesn't vanish. For a team starting fresh today, a distributed SQL database is often a good way to avoid the manual sharding work — at the cost of running a more complex database. For teams already on Postgres or MySQL at scale, manual sharding is still the most common path.
