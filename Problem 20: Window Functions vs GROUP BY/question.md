## Problem 20: Window Functions vs GROUP BY

**Scenario:**
A teammate is writing a query for a marketing dashboard. They want each row to show the order along with "this customer's total spend so far." They keep getting stuck because `GROUP BY` collapses the rows. They ask why their query keeps disappearing the order detail.

In the interview, the question is:

> Explain when you would reach for a window function instead of GROUP BY. Use an example you would actually draw on a whiteboard.

---

### Your Task:

1. Explain GROUP BY in one line.
2. Explain a window function in one line.
3. Show one small example where each is the right tool.
4. Cover the three things window functions can do that GROUP BY cannot.

---

### What a Good Answer Covers:

* GROUP BY collapses rows; window functions keep them.
* PARTITION BY vs GROUP BY.
* Running totals, ranking, lag and lead.
* The performance side: window functions are not free.
* The "use both" pattern.
