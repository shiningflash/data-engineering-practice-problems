## Problem 74: Deadlocks and Lock Escalation

**Scenario:**
The application logs are showing "deadlock detected" messages a few times an hour. Customers occasionally see failed actions. Nobody on the team has a clear sense of how to investigate or whether the deadlocks are dangerous. You are asked to explain.

In the interview, the question is:

> What is a deadlock, how do you spot one, and how do you avoid them in production?

---

### Your Task:

1. Explain deadlocks with a minimal example.
2. Show how the database detects them.
3. Cover patterns to avoid them.
4. Mention lock escalation as a related problem.

---

### What a Good Answer Covers:

* Two transactions waiting on each other in a cycle.
* Acquiring locks in a consistent order.
* Keeping transactions short.
* Reducing lock scope.
* Lock escalation (row → page → table) in some engines.
