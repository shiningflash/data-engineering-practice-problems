## Solution 68: Isolation Levels in Plain Words

### Short version you can say out loud

> Isolation levels are the database's promise about what your transaction can or cannot see while other transactions are running. Read Committed says you only see committed data, but the same row can change underneath you between reads. Repeatable Read says rows you've already read stay the same for the rest of your transaction. Serializable says transactions behave as if they ran one after another, never overlapping. Stronger levels are safer but slower, and your database's default is probably not Serializable. The bug in the scenario sounds like a non-repeatable read: the report read the customer's old balance during a long SELECT, and the deposit committed in the middle.

### The three classic anomalies

```
Dirty read
──────────
T1: UPDATE accounts SET balance = 0 WHERE id = 'A';   (not committed yet)
T2: SELECT balance FROM accounts WHERE id = 'A';  → sees 0
T1: ROLLBACK;
T2 just acted on data that never officially existed.

Non-repeatable read
───────────────────
T1: SELECT balance FROM accounts WHERE id = 'A';  → 100
T2: UPDATE accounts SET balance = 500 WHERE id = 'A';  COMMIT;
T1: SELECT balance FROM accounts WHERE id = 'A';  → 500
Same row read twice in T1, two different answers.

Phantom read
────────────
T1: SELECT * FROM orders WHERE customer_id = 1;  → 3 rows
T2: INSERT INTO orders (customer_id, ...) VALUES (1, ...);  COMMIT;
T1: SELECT * FROM orders WHERE customer_id = 1;  → 4 rows
A new row "appeared" in T1's view.
```

The isolation levels are a ladder of how many of these you allow.

### The levels

| Level                | Dirty read | Non-repeatable read | Phantom read |
| -------------------- | :--------: | :-----------------: | :----------: |
| Read Uncommitted     |    yes     |         yes         |     yes      |
| Read Committed       |     no     |         yes         |     yes      |
| Repeatable Read      |     no     |         no          |     yes\*    |
| Serializable         |     no     |         no          |      no      |

(\*Postgres prevents phantoms even at Repeatable Read because of how its snapshot isolation works. The SQL standard does not require this.)

### One sentence each

* **Read Uncommitted**: you can see other transactions' uncommitted writes. Almost nobody uses this; mostly a curiosity.
* **Read Committed**: you only see data that has been committed. But other transactions' commits during your transaction become visible. Default in Postgres, Oracle.
* **Repeatable Read**: rows you have already read keep the value they had when you first read them, for the entire transaction. Default in MySQL InnoDB.
* **Serializable**: the database behaves as if transactions ran one at a time. The strongest. Slowest under contention.

### Defaults by database

| Database          | Default level     |
| ----------------- | ----------------- |
| Postgres          | Read Committed    |
| MySQL InnoDB      | Repeatable Read   |
| SQL Server        | Read Committed    |
| Oracle            | Read Committed    |

This means moving the same code between Postgres and MySQL silently changes behavior. A bug that never showed up in MySQL can appear in Postgres, or vice versa.

### Snapshot isolation: the middle ground

Modern databases (Postgres, Oracle, SQL Server with snapshot mode) use **snapshot isolation**. When your transaction begins, you get a logical snapshot of the entire database. You always see the world as it was at that instant. Writes by others are invisible until you commit and start a new transaction.

Snapshot isolation is roughly equivalent to Repeatable Read with no phantoms. It is the right default for most applications because reads never block writes and vice versa.

### Picking a level for the scenario

The team has a long-running report that reads many tables. During the report, a deposit commits. The report sometimes shows $0 because it read the balance row before the deposit and the customer's other tables after.

Options:

1. **Run the report inside a single `REPEATABLE READ` (or snapshot) transaction.** All tables in the report see the same point in time. The deposit, if it happens during the report, is either fully visible or fully invisible. Either is consistent.
2. **Move the report to a read replica with snapshot isolation.** Same idea, off the hot OLTP database.
3. **Don't run reports on OLTP.** The proper fix; reports belong in a warehouse.

For the immediate fix, option 1 is the smallest change. For the long-term fix, option 3 is the architecturally clean answer.

### The trade-off: stronger isolation costs

* **Locks.** Higher levels hold more locks (or use snapshot, which uses more memory).
* **Aborts.** Serializable can detect conflicts and abort one of the transactions, asking the application to retry.
* **Throughput.** Heavy contention at Serializable can collapse throughput. Most production apps stay at Read Committed or Snapshot.

The pragmatic rule: use the default for your database, understand its anomalies, and design code that doesn't rely on stronger guarantees than you actually have. Promote a specific transaction to Serializable only when correctness genuinely requires it (money, inventory holds, scheduling conflicts).

### A common bug pattern: lost updates

Two users edit the same record in the application:

```
User 1: read record. value = 100.
User 2: read record. value = 100.
User 1: write 150.
User 2: write 200.

User 1's write is lost; the final value is 200.
```

Read Committed allows this. Repeatable Read prevents it in some engines but not all. The application-level fix is **optimistic concurrency control**:

```sql
UPDATE record SET value = 200, version = version + 1
WHERE id = 1 AND version = 5;     -- the version we read
```

If `version` changed in between, zero rows are affected. The application sees the conflict and retries.

This pattern works at any isolation level and is often safer than relying on isolation alone.

### Common mistakes interviewers want you to name

1. **Assuming the default is Serializable.** It almost never is.
2. **Long-running transactions** at any isolation level. Lock holds, contention, deadlocks.
3. **Mixing reads from many tables outside a transaction.** Inconsistent snapshot.
4. **Switching databases without checking the default.** Different anomalies appear silently.
5. **Using Serializable everywhere** to be "safe." Throughput collapses.

### Bonus follow-up the interviewer might throw

> *"What is the difference between optimistic and pessimistic concurrency?"*

* **Pessimistic**: lock the row when you start working on it. No conflict because nobody else can change it. Slows everyone else down.
* **Optimistic**: don't lock; assume conflicts are rare. Check at commit time (via version number or row hash). On conflict, retry.

Optimistic wins when conflicts are rare and reads dominate. Pessimistic wins when conflicts are frequent or retries are expensive. Most modern applications go optimistic.
