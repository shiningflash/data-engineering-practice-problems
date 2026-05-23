## Solution 41: Tables for an Airbnb Like App

### Short version you can say out loud

> Two layers. The OLTP layer is normalized: one row per real-world thing, foreign keys between them. The warehouse layer is a star schema: bookings are the main fact, and users, listings, dates, and locations are dimensions. The trade-offs all show up around things that change over time: prices, listing descriptions, host status. Those need a date dimension or an SCD2 history table so historical reports stay correct.

### Entities in the OLTP layer

```
users
─────────────────────────────────
user_id (PK)
email, name, joined_at, country
is_host (bool)

listings
─────────────────────────────────
listing_id (PK)
host_id (FK → users.user_id)
title, description, city, country, lat, lng
property_type, max_guests, num_bedrooms
created_at

listing_amenities       (one row per amenity per listing)
─────────────────────────────────
listing_id, amenity        (composite PK)

calendar
─────────────────────────────────
listing_id, date           (composite PK)
is_available (bool)
nightly_price (cents)
minimum_stay
updated_at

bookings
─────────────────────────────────
booking_id (PK)
listing_id (FK)
guest_id   (FK)
checkin_date, checkout_date
num_guests
total_price_cents
status   (requested, confirmed, cancelled, completed)
created_at, cancelled_at

payments
─────────────────────────────────
payment_id (PK)
booking_id (FK)
amount_cents, currency
type (charge, refund, payout)
status (pending, succeeded, failed)
created_at

reviews
─────────────────────────────────
review_id (PK)
booking_id (FK)
reviewer_id, reviewee_id
rating, body
created_at
```

Three things worth pointing out:

1. The calendar is one row per (listing, date). Each night has its own price and availability. This is the "varies over time" pattern.
2. A booking can have multiple payments: one charge, one refund, one host payout. So `payments` is a child of `bookings`, not 1:1.
3. Reviews go both ways. Guest reviews host, host reviews guest. One booking can produce two reviews.

### Why the calendar is separate

The first instinct is to put `price` and `available` on `listings`. That breaks the moment a host wants different prices on different nights. So the calendar is its own table, grain = (listing, date). This is the most common modeling decision in Airbnb-like apps. Get it wrong and pricing reports lie forever.

The price the guest pays gets frozen at booking time into `bookings.total_price_cents`. If the host changes the price later, old bookings keep their original total. The calendar is "what's for sale today," not "history of prices charged."

If you also need a price history (say, to analyze price changes), keep a `calendar_history` table or use SCD2 on `calendar`.

### The warehouse layer

```
                 ┌──────────────────┐
                 │  dim_date        │
                 │  date, dow, ...  │
                 └────────┬─────────┘
                          │
                          │
   ┌─────────────┐        │        ┌──────────────────┐
   │ dim_user    │        │        │ dim_listing      │
   │ (guest +    │        │        │ (SCD2: title,    │
   │  host)      │        │        │  type, location) │
   └─────┬───────┘        │        └────────┬─────────┘
         │                ▼                 │
         │     ┌──────────────────────┐     │
         └────▶│  fact_booking        │◀────┘
               │  ──────────────────  │
               │  booking_id (DD)     │
               │  guest_key (FK)      │
               │  host_key  (FK)      │
               │  listing_key (FK)    │
               │  booked_date_key     │
               │  checkin_date_key    │
               │  checkout_date_key   │
               │  nights, guests      │
               │  total_price_cents   │
               │  status              │
               └──────────────────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
   ┌────────────────┐        ┌──────────────────┐
   │ fact_payment   │        │ fact_review      │
   │ booking_key,   │        │ booking_key,     │
   │ amount, type,  │        │ rating, body,    │
   │ date_key       │        │ direction        │
   └────────────────┘        └──────────────────┘
```

* `fact_booking` has grain "one row per booking." This is the most queried table.
* `dim_listing` is SCD2: when a listing's title or property type changes, the old version sticks around so old reports show the listing as it was.
* `dim_user` is one table for both hosts and guests. A single user can be both. The `is_host` flag is a label, not a separate entity.
* `dim_date` is the conventional date dimension with year, quarter, month, day-of-week, is-holiday, etc.
* `fact_payment` has grain "one row per payment event." Cancellations and refunds are negative entries.
* `fact_review` has grain "one row per review."

### Trade-offs

#### 1. Is a cancelled booking still a row in fact_booking?

Yes. It's a booking that existed. The `status` field tells you it was cancelled. If you remove it, queries like "how many cancellations this month" stop working. Aggregations on `status = 'completed'` filter out the cancellations naturally.

#### 2. Should the warehouse store the calendar or just the booking?

Both. The booking is what happened. The calendar is what was offered. Analysts want both: "what was the average listed price last summer" needs the calendar; "what was the average paid price last summer" needs the booking.

I'd model `fact_calendar_day` at grain (listing, date) with `is_available`, `nightly_price`. It's large but extremely useful for pricing analytics.

#### 3. Multi-currency

`bookings.total_price_cents` is in the guest's local currency. To compare across countries, you need conversion. Two options:

* Store `total_usd_cents` too, computed at booking time using that day's FX rate.
* Store an `fx_rates` daily table and join when reporting.

The first is simpler for reporting; the second is more accurate over long histories. I'd do both: freeze the USD value at booking time for fast queries, and keep the FX rate for audit.

#### 4. Reviews from both directions

Two reviews per booking (guest of host, host of guest) are different rows in `fact_review`. The `direction` column distinguishes them. Average ratings differ by direction, so treat them separately.

### Where the SCD2 hides

Three places change over time and need SCD2:

* Listings. Hosts edit the title, photos, even the property type. Old bookings should still show the listing as the guest saw it at booking time.
* Listing prices. The calendar already gives a per-date price, so SCD2 is less critical here. But the price the host *had set* before the guest booked is sometimes useful.
* Users (hosts). Verified status, business account status changes. Reports about "verified hosts" should know whether the host was verified at the time of the booking, not now.

### What an analyst query looks like

```sql
-- Average revenue per night by city, last quarter
SELECT
  l.city,
  SUM(b.total_price_cents) / SUM(b.nights) / 100.0 AS revenue_per_night
FROM fact_booking b
JOIN dim_listing l
  ON l.listing_key = b.listing_key
JOIN dim_date d
  ON d.date_key = b.checkin_date_key
WHERE d.date >= '2025-01-01'
  AND d.date <  '2025-04-01'
  AND b.status IN ('completed')
GROUP BY l.city
ORDER BY revenue_per_night DESC;
```

The dimensions (`dim_listing`, `dim_date`) provide the filter and grouping columns. The fact (`fact_booking`) provides the measurement.

### Patterns I wouldn't regret

* One booking, one row. Never split a single booking across many rows in the booking fact.
* Surrogate keys. Every dim has an integer surrogate. SCD2 versions use different surrogates for the same natural id.
* Always keep a `created_at` and an `updated_at`. Backfills depend on these.
* Soft delete. Bookings are never hard-deleted. They go to `cancelled` status.

### Common mistakes interviewers want you to name

1. Price as a column on `listings`. Breaks the moment per-date pricing arrives.
2. Storing `total_price` as a float. Use integer cents. Always.
3. Mixing facts and dimensions (Problem 43).
4. Forgetting reviews can go both ways.
5. Not using SCD2 on `listings` when title or category changes.
6. No FX rate snapshot. Multi-currency analytics drift over years.

### Bonus follow-up the interviewer might throw

> *"How would you redesign this if Airbnb added 'experiences' (tours and activities) alongside stays?"*

Two paths:

1. Same fact table, polymorphic. Add `booking_type` (stay vs. experience) and an `experience_key` next to `listing_key`. Half the columns will be null for the other type. Simple but messy.
2. Separate fact tables. `fact_stay_booking` and `fact_experience_booking`, each with its own dimensions. Cleaner per use case but harder for "total revenue across all booking types" queries.

I'd go with separate facts and create a `fact_booking_unified` view that UNIONs them with shared columns for the cross-type queries. Best of both.
