#!/usr/bin/env python3
"""
Clean and Transform Raw Warehouse User Data
Author: Amirul Islam
Description:
    Stream large CSV data, validate and clean rows, and write cleaned output.
"""

import csv
import re
from datetime import datetime
from typing import Dict, Iterator

DIRTY_WAREHOUSE_DATA_FILE_PATH = "../data/dirty_warehouse_data.csv"
CLEANED_WAREHOUSE_DATA_FILE_PATH = "../data/cleaned_warehouse_data.csv"
INVALID_ROWS_FILE_PATH = "../data/invalid_warehouse_data.csv"

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def read_large_csv(file_path: str) -> Iterator[Dict[str, str]]:
    """Stream large CSV row by row as dictionaries."""
    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield row


def is_valid_email(email: str) -> bool:
    return EMAIL_REGEX.match(email)


def parse_date(date_str: str) -> datetime | None:
    if not date_str or date_str == "N/A":
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


def clean_row(row: Dict[str, str]) -> Dict[str, str] | None:
    """Validate and clean a single row. Returns None if invalid."""
    # Skip if email is missing or invalid
    if not row.get("email") or not is_valid_email(row["email"]):
        return None

    # Fill missing name
    row["name"] = (row.get("name") or "Unknown").strip()

    # Fill missing last_login
    row["last_login"] = (row.get("last_login") or "N/A").strip()

    # Convert total_purchases
    try:
        row["total_purchases"] = str(int(row["total_purchases"]))
    except (ValueError, TypeError):
        row["total_purchases"] = "0"

    # Validate date order
    signup = parse_date(row["signup_date"])
    last_login = parse_date(row["last_login"])
    row["is_date_valid"] = (
        "True" if signup and last_login and signup <= last_login else "False"
    )

    return row


def main():
    skipped_count = 0

    headers = [
        "user_id",
        "name",
        "email",
        "signup_date",
        "last_login",
        "total_purchases",
        "is_date_valid",
    ]

    with (
        open(
            CLEANED_WAREHOUSE_DATA_FILE_PATH, "w", newline="", encoding="utf-8"
        ) as cleaned_file,
        open(INVALID_ROWS_FILE_PATH, "w", newline="", encoding="utf-8") as invalid_file,
    ):
        writer = csv.DictWriter(cleaned_file, fieldnames=headers)
        invalid_writer = csv.DictWriter(
            invalid_file, fieldnames=headers[:-1]
        )  # no is_date_valid
        writer.writeheader()
        invalid_writer.writeheader()

        for row in read_large_csv(DIRTY_WAREHOUSE_DATA_FILE_PATH):
            cleaned = clean_row(row)
            if cleaned:
                writer.writerow(cleaned)
            else:
                skipped_count += 1
                invalid_writer.writerow(row)

    print(f"Cleaning complete. Skipped {skipped_count} invalid rows.")


if __name__ == "__main__":
    main()
