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
* Dashboards that stop updating without errors, etc.

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

> Each problem is small enough to solve in hours, but real enough to prepare you for production.

---

## Getting Started

```bash
# 1. Set up your environment
python -m venv venv && source venv/bin/activate

# 2. Use Python 3.10+
# 3. Browse PROBLEMS.md for the full index, or open any folder in problems/.
#    Each problem lives in problems/NNN-slug/ and contains:
#      - question.md   (problem statement, with YAML frontmatter)
#      - solution.md   (written walkthrough)  OR  solution.py (runnable code)
```

Inputs live in `data/`, outputs are generated beside them for easy inspection. Data files are excluded intentionally to keep the repo lightweight.

### Repo layout

```
problems/
  001-log-file-error-analysis/
    question.md
    solution.py
  ...
data/                # sample input files (gitignored where large)
scripts/
  build_index.py     # regenerates PROBLEMS.md from question.md frontmatter
PROBLEMS.md          # generated index — do not edit by hand
```

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
