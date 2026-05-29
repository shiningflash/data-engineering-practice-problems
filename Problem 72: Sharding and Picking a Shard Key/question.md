## Problem 72: Sharding and Picking a Shard Key

**Scenario:**
A company's main user table has grown to 2 billion rows. A single Postgres primary cannot keep up with writes. The team is planning to shard. They need to pick a shard key, and the team is split: some want `user_id`, some want `country`, some want `created_at`. You are asked to mediate.

In the interview, the question is:

> A users table grows to 2 billion rows. Pick a shard key, defend it, and tell me what could go wrong.

---

### Your Task:

1. Explain sharding in one paragraph.
2. Evaluate the three candidates.
3. Pick one, defend it.
4. Cover the failure modes of each.

---

### What a Good Answer Covers:

* Hash vs range sharding.
* Hot shards from bad keys.
* Resharding cost.
* Cross-shard queries.
* The "fan-out" trap.
