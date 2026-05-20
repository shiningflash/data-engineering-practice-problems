## Problem 42: Tracking Subscription Plan History

**Scenario:**
A SaaS company has customers who change plans constantly: upgrade, downgrade, pause, switch billing cycle. The finance team disputes a customer's bill almost every month, and the support team needs to answer "what plan was this customer on three months ago" routinely. The current `customers.plan_id` column only stores the latest plan, which is no help.

In the interview, the question is:

> You need to track every change to a customer's subscription plan because billing disputes are common. How do you model this?

---

### Your Task:

1. Show the table design.
2. Walk through the events that update it.
3. Cover the query patterns: "what plan now," "what plan at this date," "list all changes for this customer."
4. Mention the trade-offs vs an event-only table.

---

### What a Good Answer Covers:

* A subscription-period table with valid_from / valid_to.
* The current row vs historical rows.
* The as-of join.
* The difference between this and an audit log.
* Pause and resume handling.
