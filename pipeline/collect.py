"""
CRI Data Collection — Multi-Model Archive
==========================================
Fetches GPU rental listings from the Vast.ai public API for each
configured GPU model separately, then combines all responses into
a single daily archive.

The Vast.ai API caps results on broad queries, so targeted per-model
queries are necessary to get complete listing data for each GPU type.

Usage:
    python collect.py [--date YYYY-MM-DD] [--data-dir PATH]

Output:
    data/archive/YYYY-MM-DD.json           — combined raw API responses (all models)
    data/archive/YYYY-MM-DD.meta.json      — archive provenance + SHA-256
    data/h100-sxm-us/YYYY-MM-DD.csv       — filtered CRI-H100 snapshot
    data/h100-sxm-us/YYYY-MM-DD.meta.json — collection metadata
    data/a100-sxm-us/YYYY-MM-DD.csv       — filtered A100 snapshot
    (additional model directories as configured)
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
# Constants
# ---------------------------------------------------------------------------

VAST_API_URL       = "https://console.vast.ai/api/v0/bundles/"
MAX_DAYS_UNCHANGED = 7

# ---------------------------------------------------------------------------
# GPU Model Configurations
# ---------------------------------------------------------------------------
# Each model config defines the API query and local filters for one index.
# Adding a new model = adding one dict to this list.

GPU_MODELS = [
    {
        "id":              "h100-sxm-us",
        "index_name":      "CRI-H100",
        "gpu_name":        "H100 SXM",
        "geography":       "US",
        "min_reliability":  0.90,
        "min_gpus":         1,
        "primary":          True,
    },
    {
        "id":              "a100-sxm-us",
        "index_name":      "CRI-A100",
        "gpu_name":        "A100 SXM",
        "geography":       "US",
        "min_reliability":  0.90,
        "min_gpus":         1,
        "primary":          False,
    },
    {
        "id":              "a100-pcie-us",
        "index_name":      "CRI-A100-PCIe",
        "gpu_name":        "A100 PCIE",
        "geography":       "US",
        "min_reliability":  0.90,
        "min_gpus":         1,
        "primary":          False,
    },
    {
        "id":              "h200-us",
        "index_name":      "CRI-H200",
        "gpu_name":        "H200",
        "geography":       "US",
        "min_reliability":  0.90,
        "min_gpus":         1,
        "primary":          False,
    },
    {
        "id":              "h200-nvl-us",
        "index_name":      "CRI-H200-NVL",
        "gpu_name":        "H200 NVL",
        "geography":       "US",
        "min_reliability":  0.90,
        "min_gpus":         1,
        "primary":          False,
    },
    {
        "id":              "h100-pcie-us",
        "index_name":      "CRI-H100-PCIe",
        "gpu_name":        "H100 PCIE",
        "geography":       "US",
        "min_reliability":  0.90,
        "min_gpus":         1,
        "primary":          False,
    },
    {
        "id":              "v100-us",
        "index_name":      "CRI-V100",
        "gpu_name":        "Tesla V100",
        "geography":       "US",
        "min_reliability":  0.90,
        "min_gpus":         1,
        "primary":          False,
    },
    {
        "id":              "l40s-us",
        "index_name":      "CRI-L40S",
        "gpu_name":        "L40S",
        "geography":       "US",
        "min_reliability":  0.90,
        "min_gpus":         1,
        "primary":          False,
    },
    {
        "id":              "rtx4090-us",
        "index_name":      "CRI-4090",
        "gpu_name":        "RTX 4090",
        "geography":       "US",
        "min_reliability":  0.90,
        "min_gpus":         1,
        "primary":          False,
    },
]

# ---------------------------------------------------------------------------
# Fetch — per-model API queries
# ---------------------------------------------------------------------------

def fetch_model_listings(gpu_name: str, max_retries: int = 3) -> list:
    """
    Fetch all listings for a specific GPU model.
    Uses server-side gpu_name filter to get complete results.
    Requests both rented and unrented to capture utilization data.
    """
    query = {
        "gpu_name":  {"eq": gpu_name},
        "rentable":  {"eq": True},
    }
    params = {"q": json.dumps(query), "order": "dph_total"}

    for attempt in range(max_retries):
        try:
            r = requests.get(VAST_API_URL, params=params, timeout=30)
            r.raise_for_status()
            return r.json().get("offers", [])
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"      Attempt {attempt + 1} failed: {e}. Retrying in 10s...")
                time.sleep(10)
            else:
                print(f"      ERROR: Failed after {max_retries} attempts: {e}")
                return []

# ---------------------------------------------------------------------------
# Archive — saves combined responses for all models
# ---------------------------------------------------------------------------

def write_archive(all_offers: dict, date_str: str, data_dir: Path) -> str:
    """
    Write combined API responses to archive.
    all_offers: dict of {gpu_name: [offers list]}
    Returns SHA-256 hash.
    """
    archive_dir = data_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    archive_data = {
        "collection_date": date_str,
        "collected_utc":   datetime.now(timezone.utc).isoformat(),
        "source":          "vast.ai public API",
        "description":     "Per-model API queries combined. All geographies, "
                           "rented and unrented. Primary archival record.",
        "models_queried":  list(all_offers.keys()),
        "offers_by_model": all_offers,
    }

    archive_path = archive_dir / f"{date_str}.json"
    raw_bytes = json.dumps(archive_data, separators=(",", ":"), sort_keys=True).encode()

    with open(archive_path, "wb") as f:
        f.write(raw_bytes)

    sha256 = hashlib.sha256(raw_bytes).hexdigest()

    # Archive metadata
    total_offers = sum(len(v) for v in all_offers.values())
    counts_by_model = {k: len(v) for k, v in all_offers.items()}

    meta = {
        "ccir_version":    "1.1.0",
        "collection_date": date_str,
        "collected_utc":   datetime.now(timezone.utc).isoformat(),
        "source":          "vast.ai public API",
        "archive_type":    "combined_per_model_queries",
        "description":     "Per-model API queries combined into single archive. "
                           "All geographies, rented and unrented.",
        "counts": {
            "total_offers":   total_offers,
            "models_queried": len(all_offers),
            "by_gpu_model":   dict(sorted(counts_by_model.items(), key=lambda x: -x[1])),
        },
        "provenance": {
            "output_file": str(archive_path),
            "sha256":      sha256,
        },
    }
    meta_path = archive_dir / f"{date_str}.meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    return sha256

# ---------------------------------------------------------------------------
# Model-specific filtering (applied to the model's own API results)
# ---------------------------------------------------------------------------

def filter_for_model(offers: list, model_config: dict) -> tuple:
    """
    Apply quality filters to a model's API results.
    GPU name match is already done by the API query.
    Returns (filtered_listings, prices, filter_counts).
    """
    geography       = model_config["geography"]
    min_reliability = model_config["min_reliability"]
    min_gpus        = model_config["min_gpus"]
    geo_suffix      = f", {geography}"
    cutoff          = datetime.now(timezone.utc).timestamp() - (MAX_DAYS_UNCHANGED * 86400)

    counts = {
        "api_returned":      len(offers),
        "removed_rented":    0,
        "removed_geography": 0,
        "removed_reliability": 0,
        "removed_min_gpus":  0,
        "removed_stale":     0,
        "removed_invalid_price": 0,
        "final_observations": 0,
    }

    filtered = []
    for o in offers:
        if o.get("rented", False):
            counts["removed_rented"] += 1
            continue
        geo = str(o.get("geolocation", ""))
        if not (geo.endswith(geo_suffix) or geo == geo_suffix):
            counts["removed_geography"] += 1
            continue
        if (o.get("reliability2") or 0) < min_reliability:
            counts["removed_reliability"] += 1
            continue
        if (o.get("num_gpus") or 0) < min_gpus:
            counts["removed_min_gpus"] += 1
            continue
        if (o.get("start_date") or 0) < cutoff:
            counts["removed_stale"] += 1
            continue
        filtered.append(o)

    # Compute per-GPU prices
    results = []
    prices  = []
    for o in filtered:
        try:
            price = float(o["dph_total"]) / int(o["num_gpus"])
            if price > 0:
                results.append(o)
                prices.append(round(price, 6))
            else:
                counts["removed_invalid_price"] += 1
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            counts["removed_invalid_price"] += 1

    counts["final_observations"] = len(results)
    return results, prices, counts


def write_model_snapshot(listings: list, prices: list, model_config: dict,
                         filter_counts: dict, date_str: str,
                         data_dir: Path, archive_sha256: str):
    """Write filtered CSV and metadata for one GPU model."""
    model_dir = data_dir / model_config["id"]
    model_dir.mkdir(parents=True, exist_ok=True)

    csv_path = model_dir / f"{date_str}.csv"

    # Write CSV
    rows = []
    for listing, price in zip(listings, prices):
        rows.append({
            "listing_id":    listing.get("id"),
            "gpu_name":      listing.get("gpu_name"),
            "num_gpus":      listing.get("num_gpus"),
            "dph_total":     listing.get("dph_total"),
            "dph_per_gpu":   price,
            "reliability":   listing.get("reliability2"),
            "geolocation":   listing.get("geolocation"),
            "datacenter":    listing.get("datacenter", False),
            "last_seen":     listing.get("last_seen"),
            "gpu_ram_gb":    listing.get("gpu_ram"),
            "collected_utc": datetime.now(timezone.utc).isoformat(),
        })

    fieldnames = [
        "listing_id", "gpu_name", "num_gpus", "dph_total",
        "dph_per_gpu", "reliability", "geolocation", "datacenter",
        "last_seen", "gpu_ram_gb", "collected_utc",
    ]

    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        if rows:
            w.writerows(rows)

    csv_sha256 = hashlib.sha256(csv_path.read_bytes()).hexdigest()

    # Price summary
    price_summary = {
        "min":    round(min(prices), 4) if prices else None,
        "max":    round(max(prices), 4) if prices else None,
        "mean":   round(statistics.mean(prices), 4) if prices else None,
        "median": round(statistics.median(prices), 4) if prices else None,
        "stdev":  round(statistics.stdev(prices), 4) if len(prices) > 1 else None,
        "n":      len(prices),
    }

    # Metadata
    meta = {
        "ccir_version":    "1.1.0",
        "index_name":      model_config["index_name"],
        "model_id":        model_config["id"],
        "collection_date": date_str,
        "collected_utc":   datetime.now(timezone.utc).isoformat(),
        "source":          "vast.ai public API",
        "target_gpu":      model_config["gpu_name"],
        "geography":       model_config["geography"],
        "filters": {
            "min_reliability":    model_config["min_reliability"],
            "min_gpus":           model_config["min_gpus"],
            "max_days_unchanged": MAX_DAYS_UNCHANGED,
        },
        "counts":        filter_counts,
        "price_summary": price_summary,
        "provenance": {
            "output_file":    str(csv_path),
            "sha256":         csv_sha256,
            "archive_sha256": archive_sha256,
        },
        "low_confidence":        len(prices) < 10,
        "low_confidence_reason": "fewer than 10 qualifying observations" if len(prices) < 10 else None,
    }

    meta_path = model_dir / f"{date_str}.meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    return len(prices)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Collect CRI daily snapshots (all models)")
    parser.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--data-dir",
                        default=str(Path(__file__).resolve().parent.parent / "data"))
    parser.add_argument("--models", nargs="*", default=None,
                        help="Model IDs to process (default: all). "
                             "E.g. --models h100-sxm-us a100-sxm-us")
    args = parser.parse_args()

    date_str = args.date
    data_dir = Path(args.data_dir)
    model_ids = args.models

    # Select models
    if model_ids:
        models = [m for m in GPU_MODELS if m["id"] in model_ids]
        if not models:
            print(f"ERROR: No matching models for {model_ids}")
            print(f"Available: {[m['id'] for m in GPU_MODELS]}")
            sys.exit(1)
    else:
        models = GPU_MODELS

    print(f"\nCRI Data Collection — {date_str}")
    print(f"Models: {[m['id'] for m in models]}")
    print("=" * 60)

    # ---------------------------------------------------------------
    # Step 1: Fetch per-model from API
    # ---------------------------------------------------------------
    print(f"\n[1] Fetching listings from Vast.ai...")
    all_offers = {}
    total_fetched = 0

    for model in models:
        gpu_name = model["gpu_name"]
        print(f"    {gpu_name}...", end=" ", flush=True)
        offers = fetch_model_listings(gpu_name)
        all_offers[gpu_name] = offers
        total_fetched += len(offers)
        rented = sum(1 for o in offers if o.get("rented", False))
        unrented = len(offers) - rented
        print(f"{len(offers)} offers ({unrented} available, {rented} rented)")

    print(f"    Total: {total_fetched} offers across {len(models)} models")

    # ---------------------------------------------------------------
    # Step 2: Archive combined responses
    # ---------------------------------------------------------------
    print(f"\n[2] Archiving combined responses...")
    archive_sha256 = write_archive(all_offers, date_str, data_dir)
    print(f"    Archive: data/archive/{date_str}.json")
    print(f"    SHA-256: {archive_sha256}")

    # ---------------------------------------------------------------
    # Step 3: Filter and write per-model snapshots
    # ---------------------------------------------------------------
    print(f"\n[3] Filtering per-model snapshots...")

    results_summary = []
    for model in models:
        gpu_name = model["gpu_name"]
        offers = all_offers.get(gpu_name, [])
        listings, prices, counts = filter_for_model(offers, model)
        n = write_model_snapshot(listings, prices, model, counts,
                                date_str, data_dir, archive_sha256)

        tag = " -- CRI-H100 (primary)" if model["primary"] else ""
        status = ""
        if n == 0:
            status = " [NO DATA]"
        elif n < 10:
            status = " [LOW CONFIDENCE]"

        print(f"    {model['id']}: {n} observations{status}{tag}")
        results_summary.append({"model": model["id"], "n": n})

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------
    primary = [m for m in models if m["primary"]]
    if primary:
        primary_id = primary[0]["id"]
        primary_n  = next((r["n"] for r in results_summary if r["model"] == primary_id), 0)
        print(f"\n{'=' * 60}")
        print(f"Done. Archive: {total_fetched} total offers across {len(models)} models.")
        print(f"  CRI-H100 ({primary_id}): {primary_n} qualifying observations.")
        if primary_n < 10:
            print(f"  WARNING: LOW CONFIDENCE — fewer than 10 observations.")
    else:
        print(f"\nDone. Archive: {total_fetched} total offers.")


if __name__ == "__main__":
    main()
