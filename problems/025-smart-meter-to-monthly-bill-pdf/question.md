---
id: 25
title: Smart Meter to Monthly Bill PDF
category: System Design
topics: [billing, SCD2, idempotency, audit]
difficulty: Hard
solution: solution.md
---

# Problem 25, Smart Meter to Monthly Bill PDF

**Scenario:**
You work for an energy retailer. Every month you produce a bill PDF for each of 200,000 customers. The bill has to reflect actual consumption (one reading every 15 minutes), the tariff in effect for each period (which can change mid-month), taxes, fees, and any account adjustments. Regulators want the bill to be reproducible and auditable. If a customer disputes their bill, you need to show exactly how each number was computed.

In the interview, the question is:

> Design the pipeline that turns raw smart meter readings into a monthly bill PDF.

---

### Your Task:

1. Sketch the end-to-end flow.
2. Cover billing correctness when readings arrive late, are missing, or get corrected.
3. Show how mid-month tariff changes are handled.
4. Explain the audit trail.
5. Cover what happens when generation goes wrong.

---

### What a good answer covers:

* The fact and dimension shape (Problem 10 SCD2 feeds into this).
* An idempotent monthly job, keyed by billing period.
* How estimated readings are handled.
* PDF rendering as a separate, deterministic step.
* Sealed bills and adjustments.
