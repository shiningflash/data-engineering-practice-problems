## Solution 67: Transactions and ACID

### Short version you can say out loud

> A transaction is a group of database operations that the database treats as one unit: either every operation happens, or none does. ACID is four guarantees the database gives you about that unit. Atomicity says all or nothing. Consistency says the database moves from one valid state to another valid state. Isolation says two transactions running at the same time don't see each other's half-finished work. Durability says once the database tells you "committed," the data survives a power cut. The bank transfer is the canonical example because it shows how all four matter.

### The bank transfer story

```
WITHOUT a transaction
─────────────────────
UPDATE accounts SET balance = balance - 100 WHERE id = 'A';
-- crash here
UPDATE accounts SET balance = balance + 100 WHERE id = 'B';

Account A is down $100, account B never got it. Money is gone.

WITH a transaction
──────────────────
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 'A';
  -- crash here
  UPDATE accounts SET balance = balance + 100 WHERE id = 'B';
COMMIT;

The crash before COMMIT rolls back both updates. The database is unchanged.
```

That is atomicity in one picture.

### A walk through ACID

**A — Atomicity.**

All operations in the transaction succeed, or none of them do. Partial transactions never visible. If anything fails before `COMMIT`, the database undoes everything.

> Concrete: bank transfer above. The crash mid-way leaves the database as if the transaction never started.

**C — Consistency.**

The transaction moves the database from one valid state to another valid state. "Valid" means all constraints (foreign keys, uniqueness, check constraints) hold. The database refuses to commit if a constraint would break.

> Concrete: a `CHECK (balance >= 0)` constraint. If the first update would leave the account negative, the transaction fails before committing. The other update never happens.

This is the letter most people misunderstand. C does not mean "your business logic is correct." It means "constraints you declared are enforced." Your business logic is your problem.

**I — Isolation.**

Two transactions running at the same time don't see each other's uncommitted changes. The classic example is two ATMs withdrawing from the same account.

> Concrete: ATM 1 reads balance $200, decides to subtract $100. ATM 2 also reads balance $200 (before ATM 1 commits), also decides to subtract $100. Without isolation, both succeed and the account is at $100 instead of $0.

Isolation has levels (Problem 68). Stronger isolation is safer but slower.

**D — Durability.**

Once `COMMIT` returns, the change survives a crash. The database writes to a log (write-ahead log, redo log) before saying "committed." If the machine dies, the log is replayed on restart.

> Concrete: bank transfer commits at 12:00:00. Power cut at 12:00:01. When the server comes back up, the transfer is still there.

### How a transaction actually flows in code

```python
with connection.cursor() as cur:
    try:
        cur.execute("BEGIN;")
        cur.execute("UPDATE accounts SET balance = balance - 100 WHERE id = %s", ['A'])
        cur.execute("UPDATE accounts SET balance = balance + 100 WHERE id = %s", ['B'])
        cur.execute("COMMIT;")
    except Exception:
        cur.execute("ROLLBACK;")
        raise
```

Or, in most modern libraries, a context manager:

```python
with conn:
    cur.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 'A'")
    cur.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 'B'")
# auto commit on success, auto rollback on exception
```

Two rules:

1. Always wrap multi-step changes that have to be all-or-nothing in a transaction.
2. Always handle the exception path so a failed transaction is rolled back, not left dangling.

### What happens when you don't use them

* **Lost updates.** Two concurrent writers overwrite each other.
* **Phantom states.** A reader sees a record that no longer exists, or doesn't see one that does.
* **Inconsistent reads.** Same row read twice in the same operation returns different values.
* **Partial failures.** The bank-transfer money-vanishing problem.

These bugs are not theoretical. They appear in real systems and look like flaky tests, intermittent customer complaints, or off-by-one accounting.

### Where ACID is relaxed in practice

Modern systems often trade some ACID for scale.

* **Eventual consistency** (Cassandra, DynamoDB by default): writes propagate asynchronously across replicas. You may read a stale value briefly. Gains: huge write throughput, multi-region availability.
* **Read replicas** (Postgres, MySQL): the primary is ACID; the read replica is consistent eventually (replication lag, Problem 71).
* **NoSQL "eventually consistent" reads** are the same idea.
* **At-least-once delivery** in event streams (Problem 14) is the messaging analog: durability without atomicity across messages.

These choices are deliberate. They make sense when the application can tolerate staleness or when full ACID across many machines is prohibitive.

### When you genuinely need full ACID

* Money, billing, balances.
* Inventory at checkout.
* Anything regulated (audit, healthcare).
* Anything where "show the customer a wrong number" has serious cost.

For everything else, you can often relax one of the letters and gain scale or speed. But you have to know which letter you are giving up.

### Common mistakes interviewers want you to name

1. **Treating C as "my business logic is right."** It is about declared constraints.
2. **Forgetting to wrap multi-step writes in a transaction.** Most "money vanished" bugs are this.
3. **Long-running transactions.** Hold locks, slow everyone else down.
4. **Not handling rollback.** Failed transactions stay open, hogging resources.
5. **Assuming all databases give the same isolation by default.** They don't (Problem 68).

### Bonus follow-up the interviewer might throw

> *"What is the difference between ACID and BASE?"*

BASE stands for Basically Available, Soft state, Eventually consistent. It is the opposite philosophy: trade strict consistency for scale and availability. Cassandra, DynamoDB, S3 are BASE systems. They give massive throughput and multi-region resilience, but a read right after a write may not see the write yet.

The right answer in a real architecture is rarely "ACID everywhere" or "BASE everywhere." It is "ACID where it matters (money, identity, inventory), BASE where it scales (analytics, social feeds, logs)."
