---
id: 26
title: Delivery Idle Driver Tracking
category: System Design
topics: [streaming, H3, TTL, geospatial]
difficulty: Hard
solution: solution.md
---

# Problem 26 — Delivery Idle Driver Tracking

**Scenario:**
A food delivery company has 30,000 active drivers in a city. The dispatch system needs to know, in near real time, which drivers are currently idle and where they are, so it can offer them the next order. "Idle" means online, not on a trip, and not on a break. The data must be no more than 10 seconds stale, and dispatch must be able to query "show me all idle drivers within 1.5 km of this restaurant" in well under a second.

In the interview, the question is:

> Design how a delivery company knows in near real time which drivers are idle and where they are.

---

### Your Task:

1. Decide what state needs to be tracked, and where.
2. Pick a streaming pipeline.
3. Pick a spatial index for "drivers near point X."
4. Cover the failure modes: app crash, no GPS, off-trip-but-not-really.
5. Sketch how dispatch queries this.

---

### What a Good Answer Covers:

* A driver state machine and how it changes.
* Last-known-location store with TTL.
* Geospatial query (geohash or H3 neighbor lookup).
* The "stale driver" problem and how to expire safely.
* Why you do not put this in your warehouse.
