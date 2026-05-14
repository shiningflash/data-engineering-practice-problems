## Problem 14: Exactly Once Delivery

**Scenario:**
A payments engineer says their Kafka topic provides "exactly once" so the downstream job does not need any deduplication logic. The job processes a payment confirmation, and one day, a customer is charged twice. The engineer is surprised. You explain that exactly once is more subtle than it sounds.

In the interview, the question is:

> What does "exactly once" delivery mean and why is it so hard to actually guarantee in real systems?

---

### Your Task:

1. Define at most once, at least once, and exactly once in one sentence each.
2. Explain why exactly once is so hard at the system boundary.
3. Show the trick that makes "effective exactly once" possible.
4. Give a real example of where this goes wrong.

---

### What a Good Answer Covers:

* The producer / broker / consumer distinction.
* Why network and crashes force you to pick: drop or duplicate.
* The role of idempotent consumers.
* Kafka's "exactly once semantics" and what it actually covers.
* End-to-end exactly once vs in-broker exactly once.
