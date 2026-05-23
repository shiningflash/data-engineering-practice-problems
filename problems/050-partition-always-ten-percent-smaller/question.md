---
id: 50
title: Partition Always Ten Percent Smaller
category: Debugging
topics: [anomaly, baselines, patterns, judgement]
difficulty: Medium
solution: solution.md
---

# Problem 50, Partition Always Ten Percent Smaller

**Scenario:**
You notice that one of the 200 daily partitions of an event table consistently has about 10% fewer rows than the others. The pattern repeats every week. Some teammates say "that's just normal variation, ignore it." You're not sure.

In the interview, the question is:

> One out of 200 daily partitions is always 10 percent smaller than the rest. How do you decide if it's a bug?

This is a "don't chase ghosts, but don't ignore patterns" question. The interviewer is testing your sense of when to investigate and when to leave it alone.

---

### Your Task:

1. List the questions you would ask.
2. Walk through how to investigate cheaply.
3. Cover the most common real causes.
4. Decide when "normal variation" really is the answer.

---

### What a Good Answer Covers:

* Confirm the pattern is real (day of week effect, holidays, time zone).
* Look at the missing rows: are they a category?
* Check ingestion lag and source freshness.
* Statistical baseline.
* When to investigate and when to leave it.
