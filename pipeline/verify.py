"""
CRI-H100 Independent Verification Script
=========================================
Allows any third party to independently reproduce a published CRI-H100
index value from the raw data snapshots in this repository.

This is the open-methodology guarantee: given the same input data and
this script, any counterparty can verify any published index value.

Usage:
    python verify.py --end-date YYYY-MM-DD [--model h100-sxm-us]

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
import hashlib
import json
import statistics
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Must match CCIR Methodology v1.1 exactly
OUTLIER_SIGMA        = 2.5
WINDOW_DAYS          = 7
MIN_OBSERVATIONS_DAY = 10

DATA_DIR      = Path("data")
INDEX_OUTPUT  = Path("outputs/cri-h100-index.csv")

MODEL_CONFIGS = {
    "h100-sxm-us":  {"index_name": "CRI-H100",      "data_subdir": "h100-sxm-us",
                      "index_csv": "outputs/cri-h100-index.csv"},
    "a100-sxm-us":  {"index_name": "CRI-A100",       "data_subdir": "a100-sxm-us",
                      "index_csv": "outputs/cri-a100-index.csv"},
    "a100-pcie-us": {"index_name": "CRI-A100-PCIe",  "data_subdir": "a100-pcie-us",
                      "index_csv": "outputs/cri-a100-pcie-index.csv"},
    "h200-us":      {"index_name": "CRI-H200",       "data_subdir": "h200-us",
                      "index_csv": "outputs/cri-h200-index.csv"},
    "h200-nvl-us":  {"index_name": "CRI-H200-NVL",   "data_subdir": "h200-nvl-us",
                      "index_csv": "outputs/cri-h200-nvl-index.csv"},
    "h100-pcie-us": {"index_name": "CRI-H100-PCIe",  "data_subdir": "h100-pcie-us",
                      "index_csv": "outputs/cri-h100-pcie-index.csv"},
    "v100-us":      {"index_name": "CRI-V100",        "data_subdir": "v100-us",
                      "index_csv": "outputs/cri-v100-index.csv"},
    "l40s-us":      {"index_name": "CRI-L40S",        "data_subdir": "l40s-us",
                      "index_csv": "outputs/cri-l40s-index.csv"},
    "rtx4090-us":   {"index_name": "CRI-4090",        "data_subdir": "rtx4090-us",
                      "index_csv": "outputs/cri-4090-index.csv"},
}


def load_prices(model_dir: Path, date_str: str):
    path = model_dir / f"{date_str}.csv"
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


def verify_hash(model_dir: Path, date_str: str):
    """Verify SHA-256 hash of daily snapshot against recorded metadata."""
    csv_path  = model_dir / f"{date_str}.csv"
    meta_path = model_dir / f"{date_str}.meta.json"

    if not csv_path.exists() or not meta_path.exists():
        return None  # Can't verify

    actual_hash = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    with open(meta_path) as f:
        meta = json.load(f)
    recorded_hash = meta.get("provenance", {}).get("sha256")

    if recorded_hash is None:
        return None
    return actual_hash == recorded_hash


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


def get_published_value(index_csv: Path, end_date: str, value_col: str = None):
    if not index_csv.exists():
        return None
    with open(index_csv, newline="") as f:
        for row in csv.DictReader(f):
            if row["end_date"] == end_date:
                # Try model-specific column, fall back to common names
                for col in [value_col, "index_value", "cri_h100"]:
                    if col and col in row:
                        val = row[col]
                        return float(val) if val else None
    return None


def verify(end_date: str, model_id: str = "h100-sxm-us"):
    config     = MODEL_CONFIGS[model_id]
    index_name = config["index_name"]
    model_dir  = DATA_DIR / config["data_subdir"]
    index_csv  = Path(config["index_csv"])

    print(f"\nReproducing {index_name} — week ending {end_date}")
    print(f"Data source: {model_dir}")
    print("-" * 52)

    end   = datetime.strptime(end_date, "%Y-%m-%d").date()
    dates = [(end - timedelta(days=i)).strftime("%Y-%m-%d")
             for i in range(WINDOW_DAYS - 1, -1, -1)]

    all_prices = []
    valid_days = 0
    hash_failures = 0

    for date_str in dates:
        # Verify data integrity
        hash_ok = verify_hash(model_dir, date_str)
        hash_status = ""
        if hash_ok is True:
            hash_status = " [hash ✓]"
        elif hash_ok is False:
            hash_status = " [HASH MISMATCH ✗]"
            hash_failures += 1

        raw = load_prices(model_dir, date_str)

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
              f"({n_removed} removed), median ${day_median:.4f}{hash_status}")

    print()

    if hash_failures > 0:
        print(f"  WARNING: {hash_failures} day(s) had hash mismatches — data may have been modified.")
        print()

    if not all_prices:
        print("ERROR: No valid observations. Cannot reproduce index value.")
        sys.exit(1)

    reproduced = round(statistics.median(all_prices), 4)
    published  = get_published_value(index_csv, end_date)

    print(f"  Reproduced value: ${reproduced:.4f}")

    if published is None:
        print(f"  Published value:  NOT FOUND in {index_csv}")
        print(f"\n  Cannot verify — no published value found for {end_date}.")
        print(f"  Reproduced {index_name} = ${reproduced:.4f}")
        sys.exit(1)

    print(f"  Published value:  ${published:.4f}")
    print()

    if reproduced == published:
        print(f"  MATCH ✓  {index_name} = ${reproduced:.4f} independently verified.")
        sys.exit(0)
    else:
        diff = abs(reproduced - published)
        print(f"  MISMATCH ✗  Difference: ${diff:.6f}")
        print(f"  If this is unexpected, check raw data integrity and methodology version.")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Independently verify a CRI index value")
    parser.add_argument("--end-date", required=True, help="Week-ending date (YYYY-MM-DD)")
    parser.add_argument("--model", default="h100-sxm-us",
                        choices=list(MODEL_CONFIGS.keys()),
                        help="Model ID to verify (default: h100-sxm-us)")
    args = parser.parse_args()
    verify(args.end_date, args.model)
