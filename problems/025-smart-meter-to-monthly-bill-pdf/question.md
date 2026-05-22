---
id: 25
title: Smart Meter to Monthly Bill PDF
category: System Design
topics: [billing, SCD2, idempotency, audit]
difficulty: Hard
solution: solution.md
---

# Problem 25 — Smart Meter to Monthly Bill PDF

**Scenario:**
You work for an energy retailer. Every month, you need to produce a bill PDF for each of 200,000 customers. The bill must reflect the customer's actual consumption (every 15 minutes), the tariff in effect for each period (which can change mid-month), taxes, fees, and any account adjustments. Regulators require the bill to be reproducible and auditable: if a customer disputes their bill, you must be able to show how each number was calculated.

In the interview, the question is:

> Design the pipeline that turns raw smart meter readings into a monthly bill PDF.

---

### Your Task:

1. Sketch the end-to-end flow.
2. Cover billing correctness in the presence of late, missing or corrected readings.
3. Show how mid-month tariff changes are handled.
4. Explain the audit trail.
5. Cover what happens when generation goes wrong.

---

### What a Good Answer Covers:

* The fact and dimension shape (Problem 10 SCD2 plays into this).
* Idempotent monthly job, by billing period.
* The "estimated reading" handling.
* PDF rendering as a separate, deterministic step.
* Sealed bills and adjustments.
