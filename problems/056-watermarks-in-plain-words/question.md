---
id: 56
title: Watermarks in Plain Words
category: Streaming
topics: [watermarks, event time, allowed lateness]
difficulty: Medium
solution: solution.md
---

# Problem 56 — Watermarks in Plain Words

**Scenario:**
The team is building a streaming pipeline that computes 5-minute windowed aggregates. Late events are common. The pipeline is using Flink, and the engineer setting it up keeps asking how to choose the watermark. They have read the docs but it has not clicked yet.

In the interview, the question is:

> What is a watermark in streaming, in plain words, and what goes wrong when you set it too tight or too loose?

---

### Your Task:

1. Explain a watermark in plain English.
2. Show what setting it too tight does.
3. Show what setting it too loose does.
4. Cover how to choose in practice.

---

### What a Good Answer Covers:

* Event time vs processing time.
* The watermark as "the system's belief about how complete a window is."
* Tight watermark: low latency but drops late events.
* Loose watermark: catches late events but delays output.
* Allowed lateness and side outputs.
