# 🧩 Data Engineering Practice Problems

> After solving 1,500+ problems on LeetCode and Codeforces, I realized —
> **none of them prepared me for broken CSVs, delayed Kafka messages, or JSONs that lie.**

This repo is for engineers who’ve had enough of toy problems. It’s a collection of **real-world data engineering scenarios** — short, practical exercises inspired by what actually breaks in production.

---

## Why I Built This

Most practice problems test logic.
Production tests resilience.

In production, problems don’t come with test cases — they come with missing data, bad assumptions, and time pressure.

So I started collecting real scenarios I’ve seen:

* Kafka topics that send data hours late,
* CSVs with 2 million rows and 6 different date formats,
* JSON events with new fields added mid-release,
* ETL jobs that “succeed” but quietly skip records,
* Dashboards that stop updating without errors.

Each one became a small, reproducible exercise — so others can learn the same lessons without the 2 a.m. panic.

---

## What’s Inside

| Category                 | Scenario                                         | What You’ll Practice                         |
| :----------------------- | :----------------------------------------------- | :------------------------------------------- |
|  **Late Data**           | 10 GB of IoT logs arriving out of order          | Handle streaming delays without duplication  |
|  **Schema Drift**        | JSON events adding new fields mid-release        | Validate and evolve safely                   |
|  **ETL Reliability**     | Long-running jobs silently skipping records      | Detect silent corruptions before they spread |
|  **Data Hygiene**        | Partner CSVs with missing headers and fake nulls | Clean data in one pass and log every fix     |
|  **Rolling Analytics**   | Continuous sensor feeds with infinite rows       | Keep rolling metrics in memory without dying |

And many more coming ...

Each problem is small enough to solve in hours,
but real enough to prepare you for production.

---

## Getting Started

```bash
python -m venv venv && source venv/bin/activate
```

Use **Python 3.10+**,
open any `question.md`, and try the problem yourself before checking the `solution.py`.

All examples are designed for streaming-safe, memory-aware patterns.

---

## How to Contribute

If you’ve debugged a broken pipeline,
caught a silent bug before it spread,
built a clever patch that saved a release
or found a way to clean a 5 GB CSV in one pass —
your story belongs here.

Add a new scenario, or improve an existing one.
See the [Contribution Guide](CONTRIBUTION.md) for details.

---

> **The goal isn’t to practice coding.**
> It’s to practice *judgment* — the kind that keeps systems running when logic alone isn’t enough.

⭐ Star the repo if you’ve ever learned more from production than from tutorials.
