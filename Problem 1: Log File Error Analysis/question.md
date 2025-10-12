### Problem 1: Log File Error Analysis

**Scenario:**
You have a huge log file from an IoT platform. Each line follows this structure:

```
2025-10-11T13:45:20Z sensor_12 OK
2025-10-11T13:45:21Z sensor_45 ERROR
2025-10-11T13:45:22Z sensor_12 ERROR
2025-10-11T13:45:25Z sensor_99 OK
...
```

Each line contains:

* A timestamp (ISO format)
* A sensor ID
* A status (`OK` or `ERROR`)

The file can be **very large (10+ GB)** — so you **cannot load it fully into memory**.

---

### Task:

Write a **Python program** that:

1. Reads the log file efficiently (without loading the entire file).
2. Counts how many times each sensor reported `ERROR`.
3. Prints the **top 5 sensors** with the highest error counts.

**Bonus (Optional):**

* Print both count and percentage of total errors for each top sensor.
* Your code should work even if the file is extremely large.

---

💡 **Tips:**

* Think about streaming/iterative processing.
* Consider using `Counter`, `heapq`, or generator patterns.
* Clean and readable code matters as much as correctness.

---
