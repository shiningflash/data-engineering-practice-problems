#!/usr/bin/env python3
"""
Log Analyzer: Count sensor errors efficiently from large log files.
Author: Amirul Islam
"""

import heapq
from collections import defaultdict
from typing import Dict

LOG_FILE_PATH = "../data/sensor_data.log"


def analyze_log(file_path: str) -> Dict[str, Dict[str, int]]:
    """
    Analyzes a large sensor log file and returns OK/error counts per sensor.
    """
    counts = defaultdict(lambda: {"ok": 0, "error": 0})

    try:
        with open(file_path, "r") as file:
            for line_num, line in enumerate(file, 1):
                parts = line.strip().split()
                if len(parts) != 3:
                    # skip malformed line but log it in real pipeline
                    continue

                _, sensor_id, status = parts
                status = status.upper()
                if status == "OK":
                    counts[sensor_id]["ok"] += 1
                elif status == "ERROR":
                    counts[sensor_id]["error"] += 1
                else:
                    # unknown status, skip or log warning
                    continue
    except FileNotFoundError:
        raise SystemExit(f"Log file not found: {file_path}")

    return counts


def print_top_errors(counts: Dict[str, Dict[str, int]], top_n: int = 5):
    """
    Prints top N sensors with the highest error counts.
    """
    # Use heapq for efficient top-N extraction
    top_sensors = heapq.nlargest(top_n, counts.items(), key=lambda x: x[1]["error"])

    print(f"Top {top_n} sensors with highest errors:\n")
    print("Sensor ID | OK Count | Error Count | Error Percentage")
    print("-" * 55)

    for sensor_id, data in top_sensors:
        total = data["ok"] + data["error"]
        error_pct = (data["error"] / total) * 100 if total > 0 else 0
        print(
            f"{sensor_id:<9} | {data['ok']:<8} | {data['error']:<11} | {error_pct:>6.2f}%"
        )


def main():
    counts = analyze_log(LOG_FILE_PATH)
    print_top_errors(counts, top_n=5)


if __name__ == "__main__":
    main()
