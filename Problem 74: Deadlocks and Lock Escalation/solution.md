## Solution 74: Deadlocks and Lock Escalation

### Short version you can say out loud

> A deadlock happens when two or more transactions wait on each other in a cycle: T1 holds lock A and wants lock B, T2 holds lock B and wants lock A. Neither can proceed. The database detects this and aborts one of the transactions so the others can move. Deadlocks are normal in busy systems and not dangerous as long as the application retries on the abort. They become a real problem when they happen often, because they cause user-visible failures and waste compute. The fixes are mostly about locking in a consistent order, keeping transactions short, and updating only what you need.

### The minimal example

```
Time   T1                                T2
─────────────────────────────────────────────────────────────
t1     UPDATE accounts SET balance=
       balance-100 WHERE id='A';
       (locks row A)

t2                                       UPDATE accounts SET balance=
                                         balance-50 WHERE id='B';
                                         (locks row B)

t3     UPDATE accounts SET balance=
       balance+100 WHERE id='B';
       (waits on T2 holding B)

t4                                       UPDATE accounts SET balance=
                                         balance+50 WHERE id='A';
                                         (waits on T1 holding A)

t5     DEADLOCK detected.
       Database picks a victim, aborts it.
```

T1 wanted to update A then B. T2 wanted to update B then A. They locked their first row, then waited on each other forever.

The database notices the cycle and breaks it by aborting one transaction. That transaction gets an error like "deadlock detected." The application should retry; the other transaction completes.

### How databases detect deadlocks

* **Wait-for graph**: the database tracks which transaction is waiting on which row. Every second or so, it walks the graph looking for cycles.
* **Timeout-based**: simpler systems just abort any transaction waiting longer than X seconds. Less precise but cheap.

Postgres, MySQL, and SQL Server all use wait-for graphs. Detection is fast (sub-second) and reliable.

### Avoiding deadlocks

**1. Lock in a consistent order.**

The bank transfer above is the classic. If both transactions always lock the smaller `id` first, there is no cycle.

```sql
-- always lock the smaller id first
IF :from_id < :to_id THEN
   UPDATE accounts SET ... WHERE id = :from_id;
   UPDATE accounts SET ... WHERE id = :to_id;
ELSE
   UPDATE accounts SET ... WHERE id = :to_id;
   UPDATE accounts SET ... WHERE id = :from_id;
END IF;
```

Simple convention, eliminates a whole class of deadlocks.

**2. Keep transactions short.**

A transaction that holds locks for 5 seconds is 5,000x more likely to deadlock than one that holds for 1 millisecond. Don't make external API calls inside a transaction. Don't do heavy CPU work. Open, write, commit, close.

**3. Lock only what you need.**

`SELECT ... FOR UPDATE` is sometimes used too broadly. Lock only the rows the transaction actually changes.

**4. Use the right isolation level.**

Serializable can produce more aborts than Read Committed because the conflict checks are stricter. If you don't need it, don't use it.

**5. Retry on deadlock.**

The application must catch deadlock errors and retry the transaction. This is non-negotiable in any system that uses transactions under load. Idempotent transactions retry cleanly.

```python
for attempt in range(3):
    try:
        with conn:
            do_the_transfer(conn)
        break
    except DeadlockError:
        if attempt == 2:
            raise
        time.sleep(random.uniform(0.05, 0.2))
```

A small jittered sleep before retry helps avoid immediate re-deadlock.

### Lock escalation

A related problem in SQL Server and some others (not Postgres):

When a transaction tries to lock many rows individually, the database may **escalate** the lock to a page or full table lock. The reasoning: many fine-grained locks cost more memory than one coarse-grained lock.

The side effect: a transaction that touches 10,000 rows on a table can lock the whole table briefly, blocking every other writer.

In SQL Server:

* The threshold is around 5,000 row locks.
* You can disable escalation per table.
* You can avoid it by batching updates into smaller transactions.

Postgres does not escalate row locks to table locks. It uses MVCC with row-level locks throughout. This is one reason large updates in Postgres are less disruptive than in SQL Server.

### A diagnostic for the scenario

Production is seeing a few deadlocks per hour. Steps:

1. **Read the deadlock logs.** Postgres logs the full wait-for graph; MySQL and SQL Server have similar. Identify which two queries are conflicting.
2. **Find the lock order.** If two queries lock rows in different orders, fix one of them.
3. **Check transaction duration.** A query that holds locks for seconds is the usual suspect.
4. **Confirm the application retries.** A deadlock that surfaces as a customer error means no retry logic.
5. **Measure frequency.** A few per hour with successful retries is fine. Hundreds per hour means a hot table or a hot row.

### When deadlocks are a warning sign

* **Same two queries fighting all day.** The lock-order bug, easy fix.
* **Same row deadlocking constantly.** Often a counter or a status column that everyone updates. Use atomic operations (`UPDATE counter SET value = value + 1`) instead of read-modify-write.
* **Deadlocks scaling with traffic.** A locking pattern that does not scale. Time to redesign that path.

### A few other locking surprises

* **Foreign key locks.** Updating a child row may take a shared lock on the parent. Heavy child writes can cause parent waits.
* **`SELECT FOR UPDATE` cascading.** Locking a row can lock its dependents through triggers.
* **`pg_advisory_lock` misuse.** Holding an advisory lock across a long operation locks out everyone else.

Knowing these helps you read deadlock graphs that look mysterious.

### Common mistakes interviewers want you to name

1. **No retry logic.** Deadlocks become user errors.
2. **Inconsistent lock order.** Same fix as the bank transfer.
3. **Long transactions.** External calls, big computes, anything that takes time.
4. **Updating shared counters as read-then-write.** Use a single atomic UPDATE.
5. **Ignoring lock escalation in SQL Server.** Big batches lock entire tables briefly.

### Bonus follow-up the interviewer might throw

> *"What's the difference between a deadlock and a livelock?"*

* **Deadlock**: two transactions stuck on each other. The database detects and breaks it.
* **Livelock**: two transactions keep retrying and stepping on each other forever. They don't actually wait, but they make no progress.

Livelocks come from naive retry strategies (immediate retry on conflict). The fix is jittered backoff: each retry waits a small random time. This breaks the synchronization that causes the livelock. Same idea as Ethernet collision backoff.
