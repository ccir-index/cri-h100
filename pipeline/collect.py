"""
CRI-H100 Data Collection
========================
Fetches H100 SXM listings from Vast.ai public API.
Applies quality filters per CCIR Methodology v1.0.
Writes timestamped daily snapshot to data/raw/.

Usage:
    python collect.py [--date YYYY-MM-DD] [--output-dir PATH]

Output:
    data/raw/YYYY-MM-DD.csv       — filtered listings snapshot
    data/raw/YYYY-MM-DD.meta.json — collection metadata and provenance hash
"""

import argparse
import csv
import hashlib
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Constants — per CCIR Methodology v1.0
# ---------------------------------------------------------------------------

VAST_API_URL        = "https://console.vast.ai/api/v0/bundles/"
TARGET_GPU          = "H100 SXM"
MIN_RELIABILITY     = 0.90
MIN_GPUS            = 1
MAX_DAYS_UNCHANGED  = 7
GEOGRAPHY           = ["US"]

QUERY = {
    "gpu_name":     {"eq": TARGET_GPU},
    "rentable":     {"eq": True},
    "rented":       {"eq": False},
    "reliability2": {"gte": MIN_RELIABILITY},
    "num_gpus":     {"gte": MIN_GPUS},
}

# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def fetch_listings(max_retries: int = 3) -> list:
    params = {"q": json.dumps(QUERY), "order": "dph_total"}
    for attempt in range(max_retries):
        try:
            r = requests.get(VAST_API_URL, params=params, timeout=30)
            r.raise_for_status()
            return r.json().get("offers", [])
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"  Attempt {attempt+1} failed: {e}. Retrying in 10s...")
                time.sleep(10)
            else:
                raise RuntimeError(f"Failed after {max_retries} attempts: {e}")


def filter_geography(listings: list) -> list:
    return [l for l in listings if str(l.get("geolocation", "")).startswith("US")]


def filter_stale(listings: list) -> list:
    cutoff = datetime.now(timezone.utc).timestamp() - (MAX_DAYS_UNCHANGED * 86400)
    return [l for l in listings if l.get("last_seen", 0) >= cutoff]


def compute_per_gpu_price(listing: dict):
    try:
        price = float(listing["dph_total"]) / int(listing["num_gpus"])
        return round(price, 6) if price > 0 else None
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return None

# ---------------------------------------------------------------------------
# Write output
# ---------------------------------------------------------------------------

def write_csv(listings: list, prices: list, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for l, p in zip(listings, prices):
        rows.append({
            "listing_id":    l.get("id"),
            "gpu_name":      l.get("gpu_name"),
            "num_gpus":      l.get("num_gpus"),
            "dph_total":     l.get("dph_total"),
            "dph_per_gpu":   p,
            "reliability":   l.get("reliability2"),
            "geolocation":   l.get("geolocation"),
            "datacenter":    l.get("datacenter", False),
            "last_seen":     l.get("last_seen"),
            "gpu_ram_gb":    l.get("gpu_ram"),
            "collected_utc": datetime.now(timezone.utc).isoformat(),
        })
    if not rows:
        return ""
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_metadata(date_str, n_raw, n_geo, n_stale, n_invalid, prices, sha256, path):
    meta = {
        "ccir_version":    "1.0.0",
        "collection_date": date_str,
        "collected_utc":   datetime.now(timezone.utc).isoformat(),
        "source":          "vast.ai public API",
        "target_gpu":      TARGET_GPU,
        "geography":       GEOGRAPHY,
        "filters": {
            "min_reliability":    MIN_RELIABILITY,
            "min_gpus":           MIN_GPUS,
            "max_days_unchanged": MAX_DAYS_UNCHANGED,
        },
        "counts": {
            "raw_fetched":        n_raw,
            "removed_geography":  n_geo,
            "removed_stale":      n_stale,
            "removed_invalid":    n_invalid,
            "final_observations": len(prices),
        },
        "price_summary": {
            "min":    round(min(prices), 4) if prices else None,
            "max":    round(max(prices), 4) if prices else None,
            "mean":   round(statistics.mean(prices), 4) if prices else None,
            "median": round(statistics.median(prices), 4) if prices else None,
            "stdev":  round(statistics.stdev(prices), 4) if len(prices) > 1 else None,
            "n":      len(prices),
        },
        "provenance": {
            "output_file": str(path),
            "sha256":      sha256,
        },
        "low_confidence":        len(prices) < 10,
        "low_confidence_reason": "fewer than 10 qualifying observations" if len(prices) < 10 else None,
    }
    meta_path = path.with_suffix(".meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  Metadata: {meta_path}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Collect CRI-H100 daily snapshot")
    parser.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--output-dir", default="data/raw")
    args = parser.parse_args()

    date_str    = args.date
    output_path = Path(args.output_dir) / f"{date_str}.csv"

    print(f"\nCRI-H100 Collection — {date_str}")
    print(f"Target: {TARGET_GPU} | Geography: US")
    print("-" * 50)

    print("Fetching from Vast.ai...")
    raw = fetch_listings()
    print(f"  Raw:               {len(raw)}")

    geo_filtered = filter_geography(raw)
    n_geo = len(raw) - len(geo_filtered)
    print(f"  Removed (non-US):  {n_geo}")

    active = filter_stale(geo_filtered)
    n_stale = len(geo_filtered) - len(active)
    print(f"  Removed (stale):   {n_stale}")

    priced = [(l, compute_per_gpu_price(l)) for l in active]
    priced = [(l, p) for l, p in priced if p is not None]
    n_invalid = len(active) - len(priced)
    print(f"  Removed (invalid): {n_invalid}")
    print(f"  Final:             {len(priced)}")

    if not priced:
        print("ERROR: No valid listings. Exiting.")
        sys.exit(1)

    if len(priced) < 10:
        print("  WARNING: LOW CONFIDENCE — fewer than 10 observations.")

    listings, prices = zip(*priced)
    listings, prices = list(listings), list(prices)

    print(f"\nWriting {output_path}...")
    sha256 = write_csv(listings, prices, output_path)
    print(f"  SHA-256: {sha256}")

    write_metadata(date_str, len(raw), n_geo, n_stale, n_invalid, prices, sha256, output_path)
    print(f"\n✓ Done. {len(prices)} observations collected.")


if __name__ == "__main__":
    main()
