# Data Engineering Practice Problems

I built this repository for the engineers who learned resilience from production fires, not from puzzle sites. The most valuable lessons in my career came from midnight pipelines that failed silently, logs that refused to make sense, and dashboards that drifted off because of a single delayed event. This repo collects those “real-life” scenarios so you can practice spotting and fixing issues before they wake you up after hours.

## Why This Exists

> LeetCode sharpens logic. Production sharpens judgment. The goal here is to practice the kind of messy, high-impact problems that shape real engineers.

- Understand how systems behave under stress: late data, schema drift, skewed loads, exploding file sizes.
- Practice debugging when requirements are vague and documentation is thin.
- Build confidence handling pipelines when no one else is watching.

If this resonates, connect with me on LinkedIn for new stories and lessons, and keep an eye on this project as it grows.

## What You’ll Practice

- **Streaming resilience:** delayed events, out-of-order records, backpressure.
- **Schema evolution:** contracts that shift mid-flight, optional fields, versioning.
- **Pipeline reliability:** long-running ETL, intermittent failures, silent corruptions.
- **Operational debugging:** log sleuthing, anomaly detection, metric-driven triage.
- **Scalable data prep:** large file handling, incremental computation, memory-aware transforms.

## Example Scenarios

| Theme | Scenario | Takeaway |
| --- | --- | --- |
| Streaming quality | 10 GB of IoT logs with latent error bursts | Detect top offenders without loading the file into memory |
| Rolling analytics | Temperature feeds that never stop | Maintain rolling averages with minimal state |
| Warehouse hygiene | Partner CSVs that lie about their schema | Clean data in a single pass, isolate invalid rows, log decisions |
| Event validation | JSON payloads that evolve mid-release | Normalise events safely, surface actionable validation errors |

New problems will continue to land across ingestion, orchestration, monitoring, and storage optimisation.

## Get Started Quickly

- Use Python 3.10 or newer (create an isolated env with `python -m venv venv && source venv/bin/activate`).
- Browse any `question.md` to understand the brief, then try building your own solution.
- Compare with the provided `solution.py` when you’re ready—each script uses streaming-friendly patterns and minimal dependencies.
- Sample inputs live in `data/`; outputs are generated alongside them so you can inspect results instantly.

## How to Contribute

This repository grows through shared experience. You can add new prompts, improve reference implementations, or drop in datasets that mimic real production quirks. Read the [Contribution Guide](CONTRIBUTION.md) for the structure, naming conventions, and review checklist.

If these problems help you level up, please star the repo and share it. The best way to grow in engineering is to learn together—and to document the scars along the way.
