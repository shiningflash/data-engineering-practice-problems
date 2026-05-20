---
id: 22
title: Banking App Monthly Spending Widget
category: System Design
topics: [streaming, CDC, serving store, low latency]
difficulty: Hard
solution: solution.md
---

# Problem 22 — Banking App Monthly Spending Widget

**Scenario:**
A retail bank wants a "your spending this month" widget on the home screen of its mobile app. When the user opens the app, they should see their total spend so far this month, broken down into categories like groceries, transport, dining. It needs to feel instant. The bank has 5 million active customers and millions of transactions per day.

In the interview, the question is:

> Sketch what sits behind a "your monthly spending" widget in a banking app, where users expect it to feel instant.

---

### Your Task:

1. Decide what "feels instant" actually means and design to that.
2. Pick a storage choice for the read path and explain why.
3. Show how the data flows from a card swipe to the widget.
4. Cover the merchant-to-category problem.
5. Mention how you would handle refunds and corrections.

---

### What a Good Answer Covers:

* Read-optimized serving store, not the warehouse.
* Incremental updates per transaction (CDC or stream).
* Pre-aggregated monthly totals per (user, category).
* Idempotency and refund handling.
* Cold cache vs warm cache, and the first-of-the-month problem.
