---
id: 67
title: Transactions and ACID
category: Databases
topics: [transactions, ACID, durability, atomicity]
difficulty: Easy
solution: solution.md
---

# Problem 67, Transactions and ACID

**Scenario:**
A new engineer asks why their bank transfer code sometimes leaves $100 missing. Their code does two updates: subtract from one account, add to another. If the second update fails, the money is gone. You explain that they need a transaction. They ask what a transaction actually gives them and what each letter of ACID means.

In the interview, the question is:

> Explain transactions and ACID in plain English. What does each letter actually buy you?

---

### Your Task:

1. Explain a transaction in one sentence.
2. Walk through each letter with a concrete example.
3. Cover what happens when you don't use them.
4. Mention where ACID is relaxed in practice.

---

### What a Good Answer Covers:

* All-or-nothing as the core idea.
* Atomicity, Consistency, Isolation, Durability with real examples.
* The bank-transfer canonical example.
* Where modern systems trade ACID for performance.
* When you actually need full ACID.
