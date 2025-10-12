## Problem 2: Rolling Average of Sensor Readings (Real-Time Processing)

**Scenario:**
You are building a data pipeline for IoT sensors (like BESS, PV inverters, weather stations).
Each sensor sends temperature data every few seconds to your system in this format:

```
2025-10-11T13:45:20Z sensor_1 25.4
2025-10-11T13:45:25Z sensor_1 26.1
2025-10-11T13:45:30Z sensor_2 22.8
2025-10-11T13:45:35Z sensor_1 27.0
2025-10-11T13:45:40Z sensor_2 23.4
...
```

Each line contains:

* timestamp (ISO8601)
* sensor_id
* temperature (float, °C)

The stream never ends (you can assume input comes from a file, MQTT, or Kafka — but treat it as **continuous input**).

---

### Task:

Write a Python program that:

1. Continuously reads incoming sensor data (line by line).
2. For **each sensor**, maintains a rolling average temperature over the **last 3 readings**.
3. Each time a new reading arrives, print:

   ```
   <timestamp> <sensor_id> <rolling_average>
   ```

   Example:

   ```
   2025-10-11T13:45:35Z sensor_1 26.17
   ```

---

### Bonus Challenges:

* Make it **memory efficient** (don’t store all history).
* Handle **multiple sensors** dynamically.
* Handle malformed lines gracefully.
* Ensure the code could be easily extended to a real streaming consumer (e.g., Kafka/MQTT).

---

💡 **Tips:**

* Think about how to store only the **last 3 values per sensor**.
* You’ll probably want to use a **deque** or a simple list with slicing.
* Focus on **clean, production-like structure** — not just working code.

---
