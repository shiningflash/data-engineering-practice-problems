---
id: 54
title: Just Throw More Memory At It
category: Cost & Performance
topics: [upsize, plan inspection, optimization]
difficulty: Medium
solution: solution.md
---

# Problem 54 — Just Throw More Memory At It

**Scenario:**
A senior engineer hits a slow query in Snowflake (or a Spark job that's running out of memory) and proposes "let's just throw more memory at it. Upsize the warehouse to a 2X-Large, or bump the executor memory to 32 GB." The fix is real and works. But it triples the cost.

In the interview, the question is:

> A senior engineer says "just throw more memory at it." What questions would you ask before agreeing?

This is testing your reflex to dig before scaling.

---

### Your Task:

1. Acknowledge the move; it's not always wrong.
2. List the questions you would ask.
3. Walk through the cheaper alternatives.
4. Cover when you would actually agree.

---

### What a Good Answer Covers:

* Why upsizing works (less spill, more parallel).
* The cost trade.
* The cheaper alternatives almost always exist.
* When upsize is the right call (one-time, large, no time to optimize).
* The cultural side: don't dunk on the senior engineer.
