---
id: 2
title: Rolling Average of Sensor Readings
category: Streaming
topics: [rolling window, deque, IoT sensors, real-time]
difficulty: Easy
solution: solution.py
---

# Problem 2, Rolling Average of Sensor Readings

**Scenario:**
You are building a data pipeline for IoT sensors (like BESS, PV inverters, weather stations).
Each sensor sends temperature data every few seconds in this format:

```
2025-10-11T13:45:20Z sensor_1 25.4
2025-10-11T13:45:25Z sensor_1 26.1
2025-10-11T13:45:30Z sensor_2 22.8
2025-10-11T13:45:35Z sensor_1 27.0
2025-10-11T13:45:40Z sensor_2 23.4
...
```

Each line has:

* timestamp (ISO8601)
* sensor_id
* temperature (float, degrees C)

The stream never ends. Input could be a file, MQTT, or Kafka, but treat it as continuous input.

---

### Task:

Write a Python program that:

1. Continuously reads incoming sensor data, line by line.
2. For each sensor, keeps a rolling average temperature over the last 3 readings.
3. Each time a new reading arrives, prints:

 ```
 <timestamp> <sensor_id> <rolling_average>
 ```

 Example:

 ```
 2025-10-11T13:45:35Z sensor_1 26.17
 ```

---

### Bonus Challenges:

* Make it memory efficient. Don't store all history.
* Handle many sensors dynamically.
* Handle malformed lines without crashing.
* Make the code easy to extend to a real streaming consumer (Kafka, MQTT).

---

**Tips:**

* Think about how to store only the last 3 values per sensor.
* A `deque` works well here, or a list with slicing.
* Aim for clean, production-like structure, not just working code.

---
