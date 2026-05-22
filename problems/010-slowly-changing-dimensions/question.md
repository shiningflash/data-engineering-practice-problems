---
id: 10
title: Slowly Changing Dimensions
category: Fundamentals
topics: [SCD, dimensions, history, dbt snapshot]
difficulty: Medium
solution: solution.md
---

# Problem 10 — Slowly Changing Dimensions

**Scenario:**
A billing team runs a report that says "total revenue per region per month." A customer who lived in Singapore last year moved to Malaysia in March. The report now shows all of their historical revenue under Malaysia, including invoices from when they were still in Singapore. The finance lead is upset because the regional numbers for 2024 just silently changed.

This is the classic slowly changing dimension problem.

In the interview, the question is:

> What is a slowly changing dimension and why does it matter when the business asks "what did this customer look like last year"?

---

### Your Task:

1. Explain what a slowly changing dimension (SCD) is.
2. Describe the common SCD types (Type 1, Type 2, Type 3) in plain words.
3. Show a small example table for each.
4. Explain which type you would pick for a customer's address and why.

---

### What a Good Answer Covers:

* The difference between a fact and a dimension (briefly).
* Why "current state" is not enough.
* The trade-off between storage and history.
* Type 2 as the most common real-world answer.
* The "as-of" join pattern.
