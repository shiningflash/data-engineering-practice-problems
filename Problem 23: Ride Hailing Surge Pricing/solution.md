## Solution 23: Ride Hailing Surge Pricing

### What we are really computing

> A real-time ratio between **demand** (ride requests being created) and **supply** (available drivers) inside a small area, smoothed over a few minutes, mapped to a price multiplier between 1.0x and some cap like 3.0x.

The math is simple. The hard parts are: bucketing the map into "areas," keeping the price stable enough that it doesn't whiplash, and getting it to riders and drivers fast enough.

### The architecture

```
   ┌───────────────────┐        ┌────────────────────┐
   │ Rider app         │        │ Driver app         │
   │ "request ride"    │        │ "online / idle /   │
   │ events            │        │  on trip" events   │
   └─────────┬─────────┘        └──────────┬─────────┘
             │ Kafka topic                 │ Kafka topic
             │ ride_requests               │ driver_status
             ▼                             ▼
   ┌─────────────────────────────────────────────────┐
   │            Stream processor (Flink)             │
   │                                                 │
   │  1. Map GPS → H3 hex (resolution 8 or 9)        │
   │  2. Per hex, 3-minute sliding window:           │
   │       requests  = count of ride_requests        │
   │       supply    = unique drivers idle in window │
   │  3. Compute raw_multiplier = f(requests, supply)│
   │  4. Smooth with EMA over last 3 windows         │
   │  5. Snap to allowed price tiers (1.0, 1.25, …)  │
   └─────────────┬───────────────────────────────────┘
                 │
                 ▼
   ┌─────────────────────────────────────────────────┐
   │   Pricing store (Redis or Bigtable)             │
   │   Key:   h3_hex                                 │
   │   Value: { multiplier, valid_until, updated_at }│
   │   TTL:   60 seconds (fail-safe to 1.0x)         │
   └─────────────┬───────────────────────────────────┘
                 │
        ┌────────┴───────────────┐
        ▼                        ▼
   ┌─────────────┐      ┌────────────────────┐
   │ Pricing API │      │ Driver heatmap API │
   │ (rider quote│      │ (where to drive)   │
   │  + final    │      │                    │
   │  price)     │      │                    │
   └─────────────┘      └────────────────────┘
```

### Bucketing the map: H3 hexagons

I would use Uber's open-source H3 library to convert latitude and longitude into a hex cell. H3 is what Uber actually uses for this. Two reasons:

1. **Hexagons have equal distance to all neighbors**, unlike squares. So "the cell next door" means the same thing in every direction. This matters when you're balancing supply across cells.
2. **Multiple resolutions** are built in. Resolution 8 is about 0.74 km² per cell (a neighborhood). Resolution 9 is about 0.10 km² (a few blocks). I would start at 8.

```python
import h3
hex_id = h3.geo_to_h3(latitude, longitude, resolution=8)
# Returns a string like '88283082a3fffff'
```

Per minute math: with ~10,000 active hexes in a big city × one update per 30 seconds = roughly 20,000 writes per minute. Trivial for Redis or Bigtable.

### The pricing function

A simple, defensible formula:

```
raw_ratio  = max(1.0, requests / max(supply, 1))

raw_mult   = 1.0 + α * (raw_ratio - 1)            (α tunes aggressiveness)

smoothed   = 0.5 * smoothed_prev + 0.5 * raw_mult  (exponential smoothing)

final_mult = nearest_allowed_tier(smoothed)        (1.0, 1.25, 1.5, 2.0, 3.0)
final_mult = min(final_mult, cap)                  (cap = 3.0x in most markets)
```

Three things this gives us:

* If demand equals supply, multiplier is 1.0x. No surge.
* If demand is 2x supply, multiplier rises but not violently.
* Smoothing prevents the price from jumping every 30 seconds.
* Snapping to allowed tiers makes the UI honest. We never show "1.317x" to a rider.

### The smoothing problem

Without smoothing, the price flickers between tiers as drivers come and go. Riders and drivers both hate this. Two mechanisms:

1. **Exponential moving average** of the raw multiplier over the last few windows.
2. **Hysteresis**: require the change to persist for two windows before applying it. If it drops below the threshold in one window but comes back, keep the higher tier.

With both, prices are stable enough to be trustworthy and still responsive to real changes.

### Delivery to riders and drivers

* **Rider price quote**: when the rider opens the app or taps "request," the app calls the pricing API. The API looks up the hex for the pickup location and returns the multiplier. The full quote also locks the price for ~5 minutes to avoid the "price changed while I was looking" problem.
* **Driver heatmap**: drivers see a color overlay showing high-surge areas. This data is read from the same store, but they get a 1-minute-lagged version. (Showing live surge to drivers leads to them all rushing in and crashing the surge, which is bad for both sides.)

### Late and missing data

Driver status events can arrive late. A driver who went idle 90 seconds ago should count toward supply. Two protections:

* Use **event time**, not processing time, with a small watermark allowance (60 seconds).
* If a hex has near-zero supply data for more than 2 minutes (a vendor outage?), the system **fails safe to 1.0x**. We do not surge based on missing data.

### The cap and the human side

A cap (often 3x or 4x) is in the system not because of math but because regulators or politics demand it. Some cities ban surge altogether during emergencies. The pricing function should be configurable by city: cap, allowed tiers, even disabled. This config lives in a small table the stream processor refreshes hourly.

There is also a fairness layer: the surge multiplier in a hex is the same for everyone in that hex, regardless of who they are. No personalized surge. This is a policy choice that the system enforces, not a math choice.

### Hex edge effects

A pickup that is 5 meters inside hex A versus 5 meters inside hex B may see two very different prices. To smooth this, the pricing API can blend the rider's hex with its immediate neighbors:

```
multiplier = weighted_average(
  this_hex × 0.5,
  6 neighbor hexes × 0.5 / 6
)
```

This makes the price feel continuous across the map.

### Schema sketch in the pricing store

```
key: h3_8 hex id
value: {
  multiplier:   1.50,
  raw_demand:   42,
  supply:       28,
  updated_at:   "2025-05-14T20:14:30Z",
  valid_until:  "2025-05-14T20:15:30Z",
  reason:       "high_demand"
}
```

TTL of 60 seconds. If the stream processor stops writing, prices fall back to 1.0x within a minute. That is a safe failure mode.

### Risks I would call out

1. **Surge as gaming target.** Drivers go offline to spike supply numbers. We measure "available drivers in area," and we should also keep "active drivers in area" for cross-checks.
2. **Storms / events.** Sudden demand spikes from a sports game. The cap protects users, but the system also needs to recognize patterns and not panic.
3. **Latency.** Pricing API must respond in under 50 ms or the rider sees a spinner. Redis or Bigtable point reads are the right tool. No SQL warehouse here.
4. **Data freshness.** A 3-minute window plus 1-minute driver-side lag means the price is reacting to ~4-minute-old data. Acceptable. Less than that creates instability.

### What does not need to be real time

* Pay-out calculations.
* Customer support showing historical surge for a complaint.
* Pricing analytics ("how much surge happened yesterday").

All of these go through the warehouse, fed from the same Kafka topics.

### Common mistakes interviewers want you to name

1. **Using lat/lon directly as a bucket.** Cells are arbitrary, neighbor relationships break.
2. **No smoothing.** Prices oscillate every 30 seconds, riders complain.
3. **Pricing built on the warehouse.** Far too slow.
4. **No cap or fail-safe.** A pipeline glitch leaves a 7.5x surge stuck for an hour.
5. **Showing live surge to drivers.** Causes oscillation in supply too.

### Bonus follow-up the interviewer might throw

> *"How would you handle a city with very different supply/demand dynamics, like a small town?"*

Pricing parameters should be per city, possibly per hex cluster. A small town has fewer drivers and fewer requests, so the ratio is noisier. I would increase the window size (5 to 10 minutes), require larger absolute changes before triggering surge, and lower the cap. The architecture stays the same. Only the config differs.
