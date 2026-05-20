## Problem 50: One Partition Always Ten Percent Smaller

**Scenario:**
You notice that one of the 200 daily partitions of an event table consistently has about 10% fewer rows than the others. The pattern repeats every week. Some teammates say "that's just normal variation, ignore it." You are not sure.

In the interview, the question is:

> One out of 200 daily partitions is always 10 percent smaller than the rest. How do you decide if it is a bug?

This is a "do not chase ghosts, but do not ignore patterns" question. The interviewer is testing your sense of when to investigate vs when to let it be.

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
