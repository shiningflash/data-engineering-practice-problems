## Solution 26: Delivery Idle Driver Tracking

### The shape of the system

```
Driver app                          Trip system
sends ping every 5 sec              emits trip events
  │                                   │
  ▼                                   ▼
 ─────────────────────────────────────────────
                 Kafka
   ┌─────────────┐    ┌──────────────────┐
   │ driver_ping │    │ trip_status      │
   │ topic       │    │ topic            │
   └──────┬──────┘    └────────┬─────────┘
          │                    │
          └────────┬───────────┘
                   ▼
   ┌────────────────────────────────────────┐
   │  Stream processor (Flink)              │
   │                                        │
   │  Keyed by driver_id, holds the state:  │
   │    online | on_trip | break | offline  │
   │  Updated by pings + trip events.       │
   │                                        │
   │  For idle drivers, emits to            │
   │  the "idle drivers" store keyed by H3. │
   └────────────────┬───────────────────────┘
                    │
                    ▼
   ┌─────────────────────────────────────────┐
   │  Live driver store                      │
   │   Redis / DragonflyDB / Aerospike       │
   │                                         │
   │   Per-driver hash: { state, lat, lng,   │
   │                       h3, last_ping }   │
   │   TTL: 60 sec (auto-expire stale)       │
   │                                         │
   │   Index: H3 -> set of driver_ids        │
   └────────────────┬────────────────────────┘
                    │
                    ▼
   ┌─────────────────────────────────────────┐
   │  Dispatch service                       │
   │  Query: "idle drivers within 1.5 km     │
   │  of (lat, lng)"                         │
   │  → resolves to hex + neighbors,         │
   │    reads sets, returns up to N drivers  │
   └─────────────────────────────────────────┘
```

### The driver state machine

Drivers move between a few states:

```
       login         start_trip
offline ────▶ online ────────▶ on_trip
   ▲           ▲ ▲              │
   │           │ │  end_trip    │
   │   logout  │ └──────────────┘
   └───────────┘
               break_start ┌─▶ break ─┐ break_end
                           │          ▼
                           └─── back to online
```

Only `online` is idle. The stream processor maintains this state per driver from two streams:

* `driver_ping` (every 5 sec, with location, app says "online or break")
* `trip_status` (`trip_started`, `trip_completed`)

The processor's keyed state per driver holds: `state`, `last_lat`, `last_lng`, `last_ping_at`. Each event updates the state.

### Why streaming, not a database

You could have the app write directly to Postgres. Don't.

* 30,000 drivers × 1 write per 5 sec = 6,000 writes/sec. That's hot.
* Trips happen continuously. Writes amplify.
* Locking and ACID overhead destroys throughput.

A stream + an in-memory store handles this comfortably.

### The location index

For "drivers within 1.5 km of point X," we need a spatial index. Two practical choices:

**H3 hex grid (recommended).** Resolution 9 (~0.10 km² hexes) or 8 (~0.74 km²). Each driver's location maps to a hex. A query for "within 1.5 km" expands to "this hex and its neighbors up to N rings."

```python
import h3
center = h3.geo_to_h3(lat, lng, resolution=9)
nearby = h3.k_ring(center, 3)   # this hex and rings 1..3
```

Then we read all drivers whose stored hex is in `nearby` and filter by exact distance.

**Geohash.** Same idea with rectangular cells. Works fine for moderate scale. H3 wins on neighbor math.

### The store layout

In Redis terms:

```
# per-driver state
HSET driver:42 state online lat 1.3245 lng 103.8512 h3 89...3fff last_ping 1715680000
EXPIRE driver:42 60

# per-hex index of idle drivers
SADD idle_drivers:h3:89...3fff 42 91 132
EXPIRE idle_drivers:h3:89...3fff 60
```

The TTL is the key safety. If a driver disappears (app crash, dead battery), their entries expire within 60 seconds. We do not need a separate cleanup job.

When the stream processor updates a driver:

* Move them out of the old hex set if they moved.
* Add them to the new hex set if they are still idle.
* Refresh the per-driver hash.

If the driver starts a trip, remove them from any hex set. They are no longer idle.

### Query path for dispatch

When a new order comes in at the restaurant location:

1. Compute the restaurant's H3 hex.
2. Get the `k_ring` of hexes covering the search radius (1.5 km is roughly k=3 at resolution 9).
3. Read the `idle_drivers:h3:*` sets for each hex (one Redis MGET).
4. Hydrate each driver's lat/lng from `driver:<id>` hashes.
5. Compute exact distance, filter by 1.5 km, sort by distance.
6. Return the top N.

Total latency: usually 5-20 ms.

### Handling failure modes

**App crashes.** Pings stop. After 60 seconds the TTL fires and the driver disappears from queries. No bad dispatch.

**No GPS / bad GPS.** Pings still arrive with a quality flag. The stream processor flags poor-quality positions and either holds the last good location for up to 30 seconds or drops the driver out of idle.

**Driver says "online" but they're actually on a trip.** The trip system is the source of truth for `on_trip`. The processor uses trip events to override the app's claim. If a trip event says `trip_started`, we set the driver to `on_trip` regardless of what the ping says.

**Network split between app and dispatch.** The driver shows online for the duration of the TTL, then disappears. Dispatch sees a smaller pool and offers fewer matches, which is the right failure mode.

**Stream processor crash.** Flink resumes from checkpoint. State is reconstructed. The store may briefly hold stale records, but the TTL bounds it.

### Why not just query the warehouse?

* Latency. Warehouse queries are seconds.
* Cost. Per-query cost adds up at thousands of dispatches per second.
* Concurrency. Warehouses are not built for the read pattern.

The warehouse is still in the picture for analytics ("how many idle drivers did we have at 6 PM yesterday?"), fed from the same Kafka topics.

### Capacity estimate

30,000 drivers × 1 ping/5 sec = 6,000 writes/sec.
Read side: dispatch queries during peak meals, maybe 200 orders/sec, each doing a small read. Trivial.
Store size: 30,000 entries × ~150 bytes = ~5 MB. Plus a hex index over maybe 5,000 hexes. Tiny.

All this fits on a single Redis cluster easily. For a 100x larger company, the same shape holds, you just shard by city or driver_id.

### What about long-running idle drivers parking somewhere?

Some drivers park and wait. They keep sending pings but never move. The system correctly counts them as idle. The dispatch service may want to prefer drivers who have been idle longer (fairness) or shorter (faster pickup). Either is a small change in the query: include `last_ping` and `idle_since` in the response, let dispatch's algorithm pick.

### Common mistakes interviewers want you to name

1. **Storing driver state in the OLTP database.** Hot row contention, slow reads.
2. **No TTL.** A crashed app means the driver is "online forever" in the store.
3. **Reading from the warehouse.** Latency and cost both blow up.
4. **Trusting the app's state claim.** Trip events must override.
5. **Spatial query that scans all drivers.** Cell-based index is essential.

### Bonus follow-up the interviewer might throw

> *"How would you change this if you wanted to predict idle drivers, not just track them?"*

Same data flows, plus the warehouse historical view. A model can learn that drivers in hex X tend to be idle at 2 PM on weekdays. Dispatch can pre-warm offers there. The live system stays the same; the prediction is just an extra hint, never the source of truth.
