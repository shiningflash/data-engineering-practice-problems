#!/usr/bin/env python3
"""
Validate and Normalize Streaming User Events (Schema Evolution Ready)
Author: Amirul Islam
Description:
    Streams JSON events line-by-line, validates and normalizes them
    against an evolving schema, and separates valid and invalid events.
Complexity:
    Time: O(n) — one pass over events.
    Space: O(1) — processes line by line.
"""

import json
from datetime import datetime
from typing import Any, Dict, Iterator

RAW_EVENTS_FILE_PATH = "../data/events.jsonl"
CLEANED_EVENTS_FILE_PATH = "../data/cleaned_events.jsonl"
INVALID_EVENTS_FILE_PATH = "../data/invalid_events.jsonl"

VALID_EVENT_TYPES = {"login", "logout", "purchase"}


def read_json_lines(file_path: str) -> Iterator[Dict[str, Any]]:
    """Stream JSON objects line by line (memory-safe)."""
    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                yield {
                    "_raw": line,
                    "error_reason": f"invalid_json_at_line_{line_number}",
                }


def is_valid_iso8601(ts: str) -> bool:
    """Check if timestamp is ISO8601-formatted."""
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def normalize_event(event: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Validate and normalize a single event.
    Returns normalized dict if valid, or None if invalid.
    Adds 'error_reason' if invalid.
    """
    # --- Validate user_id ---
    if "user_id" not in event:
        event["error_reason"] = "missing user_id"
        return None
    try:
        user_id = int(event["user_id"])
    except (ValueError, TypeError):
        event["error_reason"] = "user_id not convertible to int"
        return None

    # --- Validate event_type ---
    event_type = str(event.get("event_type", "")).lower()
    if event_type not in VALID_EVENT_TYPES:
        event["error_reason"] = f"invalid event_type '{event_type}'"
        return None

    # --- Validate timestamp ---
    timestamp = event.get("timestamp")
    if not timestamp or not is_valid_iso8601(timestamp):
        event["error_reason"] = "invalid or missing timestamp"
        return None

    # --- Normalize amount ---
    amount = 0.0
    if event_type == "purchase":
        try:
            amount = float(event.get("amount", 0.0))
        except (ValueError, TypeError):
            event["error_reason"] = "invalid amount for purchase"
            return None

    # --- Optional fields (schema evolution safe) ---
    device = event.get("device") if isinstance(event.get("device"), str) else None

    # --- Build normalized record ---
    normalized = {
        "user_id": user_id,
        "event_type": event_type,
        "timestamp": timestamp,
        "amount": round(amount, 2),
    }
    # keep optional field if present
    if device:
        normalized["device"] = device

    return normalized


def main():
    total = valid = invalid = 0

    with (
        open(CLEANED_EVENTS_FILE_PATH, "w", encoding="utf-8") as clean_f,
        open(INVALID_EVENTS_FILE_PATH, "w", encoding="utf-8") as invalid_f,
    ):
        for event in read_json_lines(RAW_EVENTS_FILE_PATH):
            total += 1

            # Handle decode errors specially
            if "_raw" in event:
                invalid += 1
                invalid_f.write(json.dumps(event, ensure_ascii=False) + "\n")
                continue

            normalized = normalize_event(event)
            if normalized:
                valid += 1
                clean_f.write(json.dumps(normalized, ensure_ascii=False) + "\n")
            else:
                invalid += 1
                invalid_f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(
        f"Validation complete. "
        f"Processed {total} events: {valid} valid, {invalid} invalid."
    )


if __name__ == "__main__":
    main()
