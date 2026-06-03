---
id: 90
title: OpenLineage and Data Discovery
category: System Design
topics: [OpenLineage, DataHub, OpenMetadata, catalog]
difficulty: Medium
interview_value: optional
learn_order: 89
solution: solution.md
---

# Problem 90, OpenLineage and Data Discovery

**Scenario:**
The company has 4,000 tables across three warehouses and two lakes. A new analyst takes a week to find the "right" customers table because there are nine of them with similar names. A data engineer wastes an afternoon trying to figure out who owns a table before they refactor it. The CTO has heard "data catalog" and "data discovery" and wants to know what to actually buy or build.

In the interview, the question is:

> What is a data catalog, what does OpenLineage have to do with it, and how would you stand one up for a 4,000-table organisation?

---

### Your Task:

1. Define the data catalog and the three things it must do (search, lineage, ownership).
2. Explain OpenLineage as the open standard for emitting lineage events.
3. Compare the main options (DataHub, OpenMetadata, Atlan, Collibra, homegrown).
4. Walk through the rollout: pilot, expand, govern.
5. Cover the failure mode where the catalog rots.

---

### What a Good Answer Covers:

* Search-by-name and search-by-meaning (semantic search over columns and tags).
* Lineage at table and column level.
* Owner and freshness metadata as first-class.
* The open-source vs vendor decision in 2026.
* Why the catalog dies without a "register or it does not exist" policy.
