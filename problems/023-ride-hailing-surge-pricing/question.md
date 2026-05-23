---
id: 23
title: Ride Hailing Surge Pricing
category: System Design
topics: [streaming, H3, real-time, pricing]
difficulty: Hard
solution: solution.md
---

# Problem 23, Ride Hailing Surge Pricing

**Scenario:**
A ride hailing company wants to set a surge multiplier (1.0x, 1.5x, 2x and so on) for each small geographic area, in real time. The multiplier should rise when there are many more ride requests than available drivers in that area, and fall when supply catches up. The product team wants prices to update at most every 30 seconds, and the area should be roughly a neighborhood.

In the interview, the question is:

> Design how a ride hailing company calculates surge pricing in real time.

---

### Your Task:

1. Decide what data is needed, and how often.
2. Pick a geospatial bucketing strategy.
3. Sketch the streaming pipeline.
4. Define the pricing function.
5. Cover how the price is delivered to riders and drivers.

---

### What a Good Answer Covers:

* H3 or geohash for area buckets.
* Sliding windows on demand and supply streams.
* The smoothing problem (avoid jumpy prices).
* A pricing store keyed by area and time.
* Fairness, abuse, and the "is this legal here" angle.
