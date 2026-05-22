#!/usr/bin/env python3
"""
Rolling Average Temperature Processor
Author: Amirul Islam
Description:
    Continuously reads sensor readings from a stream and prints
    a rolling average over the last 3 readings for each sensor.
"""

import sys
from collections import defaultdict, deque
from typing import Deque, Dict


def compute_rolling_average(file_stream=sys.stdin) -> None:
    """
    Reads sensor data from a stream and prints rolling averages
    of the last 3 readings per sensor.

    Expected input line format:
        <timestamp> <sensor_id> <temperature>
    """
    # Use maxlen=3 to automatically maintain a rolling window
    sensor_readings: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=3))

    for line_num, line in enumerate(file_stream, 1):
        parts = line.strip().split()
        if len(parts) != 3:
            # skip malformed lines
            continue

        timestamp, sensor_id, temp_str = parts
        try:
            temperature = float(temp_str)
        except ValueError:
            # skip bad temperature values
            continue

        # Update rolling window for the sensor
        sensor_readings[sensor_id].append(temperature)

        # Only print average when we have 3 readings
        if len(sensor_readings[sensor_id]) == 3:
            avg_temp = sum(sensor_readings[sensor_id]) / 3
            print(f"{timestamp} {sensor_id} {avg_temp:.2f}")


def main():
    print("Reading sensor data... (Ctrl+C to stop)")
    try:
        compute_rolling_average()
    except KeyboardInterrupt:
        print("\nStopping stream. Goodbye!")


if __name__ == "__main__":
    main()
