#!/usr/bin/env python3
"""
Partner CSV Merger: combine customer CSVs from many partners
into a single clean file with a standard schema.
Author: Amirul Islam
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Optional

INPUT_FOLDER = "../data/partner_csvs"
OUTPUT_FILE = "all_customers.csv"

# Standard column -> possible source names from different partners
COLUMN_MAP = {
    "customer_id": ["customer_id", "CustomerID", "cust_id"],
    "name": ["name", "Name", "full_name"],
    "email": ["email", "Email", "email_addr"],
    "signup_date": ["signup_date", "SignupDate", "joined_on"],
}

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]

STANDARD_COLUMNS = list(COLUMN_MAP.keys()) + ["source_file"]


def build_reverse_map() -> Dict[str, str]:
    """Map any known partner column name back to our standard column name."""
    reverse = {}
    for standard, options in COLUMN_MAP.items():
        for option in options:
            reverse[option.lower()] = standard
    return reverse


def parse_date(value: str) -> Optional[str]:
    """Try a few common date formats and return ISO date if one matches."""
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def normalize_row(
    row: Dict[str, str],
    reverse_map: Dict[str, str],
    source: str,
) -> Optional[Dict[str, str]]:
    """Map one raw row to the standard schema. Return None if the row is unusable."""
    clean = {col: "" for col in STANDARD_COLUMNS}

    for raw_col, value in row.items():
        if raw_col is None:
            continue
        standard = reverse_map.get(raw_col.lower())
        if standard:
            clean[standard] = (value or "").strip()

    if not clean["customer_id"] or not clean["email"]:
        return None

    if not clean["name"]:
        clean["name"] = "Unknown"

    if clean["signup_date"]:
        parsed = parse_date(clean["signup_date"])
        if parsed is None:
            return None
        clean["signup_date"] = parsed

    clean["source_file"] = source
    return clean


def iter_csv_files(folder: str) -> Iterable[Path]:
    return sorted(Path(folder).glob("*.csv"))


def merge_partner_csvs(folder: str, output_file: str) -> Dict[str, int]:
    """Read every CSV in the folder, normalize, and write one combined CSV."""
    reverse_map = build_reverse_map()
    stats = {"files": 0, "rows_in": 0, "rows_out": 0, "rows_skipped": 0}

    with open(output_file, "w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=STANDARD_COLUMNS)
        writer.writeheader()

        for path in iter_csv_files(folder):
            stats["files"] += 1
            try:
                with open(path, "r", newline="") as f:
                    reader = csv.DictReader(f)
                    for raw in reader:
                        stats["rows_in"] += 1
                        clean = normalize_row(raw, reverse_map, path.name)
                        if clean is None:
                            stats["rows_skipped"] += 1
                            continue
                        writer.writerow(clean)
                        stats["rows_out"] += 1
            except FileNotFoundError:
                continue

    return stats


def main():
    stats = merge_partner_csvs(INPUT_FOLDER, OUTPUT_FILE)
    print("Merge complete")
    print(f"  files read:    {stats['files']}")
    print(f"  rows in:       {stats['rows_in']}")
    print(f"  rows written:  {stats['rows_out']}")
    print(f"  rows skipped:  {stats['rows_skipped']}")


if __name__ == "__main__":
    main()
