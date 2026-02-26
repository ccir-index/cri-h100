"""
CRI-H100 Independent Verification Script
=========================================
Allows any third party to independently reproduce a published CRI-H100
index value from the raw data snapshots in this repository.

This is the open-methodology guarantee: given the same input data and
this script, any counterparty can verify any published index value.

Usage:
    python verify.py --end-date YYYY-MM-DD

Example:
    python verify.py --end-date 2026-03-01

    Reproducing CRI-H100 for week ending 2026-03-01
    --------------------------------------------------
    Day 2026-02-23: 47 obs → 45 after outlier removal, median $1.8420
    Day 2026-02-24: 51 obs → 49 after outlier removal, median $1.8210
    ...
    Window median (all observations): $1.8340
    Published value:                  $1.8340
    MATCH ✓
"""

import argparse
import csv
import json
import statistics
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Must match CCIR Methodology v1.0 exactly
OUTLIER_SIGMA        = 2.5
WINDOW_DAYS          = 7
MIN_OBSERVATIONS_DAY = 10

RAW_DATA_DIR  = Path("data/raw")
INDEX_OUTPUT  = Path("outputs/cri-h100-index.csv")


def load_prices(date_str: str):
    path = RAW_DATA_DIR / f"{date_str}.csv"
    if not path.exists():
        return None
    prices = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            try:
                prices.append(float(row["dph_per_gpu"]))
            except (KeyError, ValueError):
                continue
    return prices if prices else None


def remove_outliers(prices: list):
    if len(prices) < 4:
        return prices, 0
    sorted_p = sorted(prices)
    trim_n   = max(1, int(len(sorted_p) * 0.10))
    trimmed  = sorted_p[trim_n:-trim_n]
    t_mean   = statistics.mean(trimmed)
    stdev    = statistics.stdev(prices)
    if stdev == 0:
        return prices, 0
    threshold = OUTLIER_SIGMA * stdev
    cleaned   = [p for p in prices if abs(p - t_mean) <= threshold]
    return cleaned, len(prices) - len(cleaned)


def get_published_value(end_date: str):
    if not INDEX_OUTPUT.exists():
        return None
    with open(INDEX_OUTPUT, newline="") as f:
        for row in csv.DictReader(f):
            if row["end_date"] == end_date:
                val = row.get("cri_h100")
                return float(val) if val else None
    return None


def verify(end_date: str):
    print(f"\nReproducing CRI-H100 — week ending {end_date}")
    print("-" * 52)

    end   = datetime.strptime(end_date, "%Y-%m-%d").date()
    dates = [(end - timedelta(days=i)).strftime("%Y-%m-%d")
             for i in range(WINDOW_DAYS - 1, -1, -1)]

    all_prices = []
    valid_days = 0

    for date_str in dates:
        raw = load_prices(date_str)

        if raw is None:
            print(f"  {date_str}: MISSING")
            continue

        if len(raw) < MIN_OBSERVATIONS_DAY:
            print(f"  {date_str}: LOW CONFIDENCE ({len(raw)} obs < {MIN_OBSERVATIONS_DAY} minimum)")
            continue

        cleaned, n_removed = remove_outliers(raw)
        if not cleaned:
            print(f"  {date_str}: EMPTY after outlier removal")
            continue

        day_median = statistics.median(cleaned)
        all_prices.extend(cleaned)
        valid_days += 1
        print(f"  {date_str}: {len(raw)} obs → {len(cleaned)} after outlier removal "
              f"({n_removed} removed), median ${day_median:.4f}")

    print()

    if not all_prices:
        print("ERROR: No valid observations. Cannot reproduce index value.")
        sys.exit(1)

    reproduced = round(statistics.median(all_prices), 4)
    published  = get_published_value(end_date)

    print(f"  Reproduced value: ${reproduced:.4f}")

    if published is None:
        print(f"  Published value:  NOT FOUND in {INDEX_OUTPUT}")
        print(f"\n  Cannot verify — no published value found for {end_date}.")
        sys.exit(1)

    print(f"  Published value:  ${published:.4f}")
    print()

    if reproduced == published:
        print(f"  MATCH ✓  CRI-H100 = ${reproduced:.4f} independently verified.")
        sys.exit(0)
    else:
        diff = abs(reproduced - published)
        print(f"  MISMATCH ✗  Difference: ${diff:.6f}")
        print(f"  If this is unexpected, check raw data integrity and methodology version.")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Independently verify a CRI-H100 index value")
    parser.add_argument("--end-date", required=True, help="Week-ending date (YYYY-MM-DD)")
    args = parser.parse_args()
    verify(args.end_date)
