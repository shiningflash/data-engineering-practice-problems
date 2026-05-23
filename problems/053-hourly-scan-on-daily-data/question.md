---
id: 53
title: Hourly Scan on Daily Data
category: Cost & Performance
topics: [summary tables, MV, refresh, BI tool]
difficulty: Easy
solution: solution.md
---

# Problem 53, Hourly Scan on Daily Data

**Scenario:**
A dashboard refreshes every hour. The underlying data only changes once a day, at 6 AM. The query scans 5 TB each hour, so 120 TB per day, ~$750 a month at on-demand rates. The team built it that way "because the dashboard tool's default is hourly." They do not want to break the dashboard.

In the interview, the question is:

> A team is scanning a 5 TB table every hour for a dashboard that only changes once a day. How do you fix this without disturbing their workflow?

---

### Your Task:

1. List the three or four fix options.
2. Pick one, defend.
3. Cover how to keep the user experience identical.
4. Mention longer term checks.

---

### What a Good Answer Covers:

* Materialized view or scheduled summary table.
* Caching at the BI layer.
* Daily refresh schedule.
* Storage savings vs compute savings.
