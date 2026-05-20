## Problem 41: Tables for an Airbnb Like App

**Scenario:**
You are designing the data model for an app like Airbnb. Hosts list properties. Guests search, book, pay and review. There are calendars, prices that change by date, cancellations, refunds, and multiple guests per booking. The interviewer wants to see you reason about which tables exist, what is a fact and what is a dimension, and where the trade-offs hide.

In the interview, the question is:

> Walk me through how you would design tables for an app like Airbnb. Start from the obvious entities and tell me where the trade offs hide.

---

### Your Task:

1. List the entities and their grain.
2. Draw the relationships.
3. Cover the trade-offs around bookings, prices and reviews.
4. Mention the warehouse layer on top.

---

### What a Good Answer Covers:

* Users, listings, calendars, bookings, payments, reviews.
* OLTP shape vs warehouse star schema.
* Pricing as a separate, time-varying table.
* Booking as the central fact.
* Slowly changing dimensions (listing details, host details).
