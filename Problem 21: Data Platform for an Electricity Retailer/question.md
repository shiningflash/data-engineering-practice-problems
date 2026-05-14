## Problem 21: Data Platform for an Electricity Retailer

**Scenario:**
A small electricity retailer has 200,000 residential customers. Every customer has a smart meter that sends one reading every 15 minutes. The business needs:

* Accurate monthly bills.
* A "your usage" page in the customer app that loads in under 2 seconds.
* Daily reports for the operations team.
* Forecasts to bid into the wholesale market.

You are the first data engineer they hire. They have AWS, a small Postgres database, and no data platform yet.

In the interview, the question is:

> Design the data platform for a small electricity retailer with 200,000 smart meters reporting every 15 minutes.

---

### Your Task:

1. Estimate the data volume so you know what you are dealing with.
2. Sketch the architecture end to end.
3. Pick the storage and processing layers, and defend each choice.
4. Walk through how each use case is served.
5. Call out two or three risks you would design for.

---

### What a Good Answer Covers:

* Back-of-envelope volume math.
* A clear ingestion path, a storage layer, a serving layer.
* Choice between batch and stream for each use case.
* How billing remains correct in the face of late data.
* How the customer app stays fast without scanning raw readings.
