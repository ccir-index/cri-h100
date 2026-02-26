"""
CRI-H100 Index Calculator
=========================
Computes the weekly CRI-H100 index value from daily raw snapshots.
Applies outlier removal per CCIR Methodology v1.0.
Appends result to the published index series CSV.

Usage:
    python calculate.py [--end-date YYYY-MM-DD] [--window 7]

Output:
    outputs/cri-h100-index.csv         — append-only published index series
    outputs/cri-h100-YYYY-MM-DD.audit.json — full calculation audit trail
"""

import argparse
import csv
import json
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants — per CCIR Methodology v1.0
# ---------------------------------------------------------------------------

OUTLIER_SIGMA        = 2.5
WINDOW_DAYS          = 7
MIN_OBSERVATIONS_DAY = 10    # Minimum to include a day in window
MIN_VALID_DAYS       = 3     # Minimum valid days to publish; else low-confidence flag

RAW_DATA_DIR   = Path("data/raw")
INDEX_OUTPUT   = Path("outputs/cri-h100-index.csv")
AUDIT_DIR      = Path("outputs/audits")

# ---------------------------------------------------------------------------
# Load daily data
# ---------------------------------------------------------------------------

def load_daily_prices(date_str: str):
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


def load_daily_meta(date_str: str):
    path = RAW_DATA_DIR / f"{date_str}.meta.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)

# ---------------------------------------------------------------------------
# Outlier removal — per CCIR Methodology v1.0
# ---------------------------------------------------------------------------

def remove_outliers(prices: list, sigma: float = OUTLIER_SIGMA):
    """
    1. Compute trimmed mean (drop top/bottom 10%)
    2. Compute stdev of full series
    3. Remove observations > sigma * stdev from trimmed mean
    Returns (cleaned_prices, n_removed)
    """
    if len(prices) < 4:
        return prices, 0

    sorted_p = sorted(prices)
    trim_n   = max(1, int(len(sorted_p) * 0.10))
    trimmed  = sorted_p[trim_n:-trim_n]
    t_mean   = statistics.mean(trimmed)
    stdev    = statistics.stdev(prices)

    if stdev == 0:
        return prices, 0

    threshold = sigma * stdev
    cleaned   = [p for p in prices if abs(p - t_mean) <= threshold]
    return cleaned, len(prices) - len(cleaned)

# ---------------------------------------------------------------------------
# Index calculation
# ---------------------------------------------------------------------------

def calculate(end_date: str, window_days: int = WINDOW_DAYS) -> dict:
    end   = datetime.strptime(end_date, "%Y-%m-%d").date()
    dates = [(end - timedelta(days=i)).strftime("%Y-%m-%d")
             for i in range(window_days - 1, -1, -1)]

    all_prices      = []
    daily_summaries = []
    valid_days      = 0

    for date_str in dates:
        raw = load_daily_prices(date_str)

        if raw is None:
            daily_summaries.append({"date": date_str, "status": "missing", "n": 0})
            continue

        if len(raw) < MIN_OBSERVATIONS_DAY:
            daily_summaries.append({"date": date_str, "status": "low_confidence",
                                     "n_raw": len(raw), "n_used": 0})
            continue

        cleaned, n_removed = remove_outliers(raw)
        if not cleaned:
            daily_summaries.append({"date": date_str, "status": "empty_after_outlier_removal",
                                     "n_raw": len(raw), "n_used": 0})
            continue

        all_prices.extend(cleaned)
        valid_days += 1
        daily_summaries.append({
            "date":      date_str,
            "status":    "included",
            "n_raw":     len(raw),
            "n_removed": n_removed,
            "n_used":    len(cleaned),
            "daily_median": round(statistics.median(cleaned), 4),
            "daily_mean":   round(statistics.mean(cleaned), 4),
        })

    # Index value
    if not all_prices:
        return {
            "end_date":      end_date,
            "index_value":   None,
            "low_confidence": True,
            "low_confidence_reason": "no valid observations in window",
            "valid_days":    0,
            "daily":         daily_summaries,
        }

    index_value  = round(statistics.median(all_prices), 4)
    low_conf     = valid_days < MIN_VALID_DAYS
    low_conf_why = f"only {valid_days} valid days in {window_days}-day window" if low_conf else None

    return {
        "ccir_version":   "1.0.0",
        "index_name":     "CRI-H100",
        "end_date":       end_date,
        "window_days":    window_days,
        "index_value":    index_value,
        "n_observations": len(all_prices),
        "valid_days":     valid_days,
        "low_confidence": low_conf,
        "low_confidence_reason": low_conf_why,
        "summary": {
            "min":   round(min(all_prices), 4),
            "max":   round(max(all_prices), 4),
            "mean":  round(statistics.mean(all_prices), 4),
            "stdev": round(statistics.stdev(all_prices), 4) if len(all_prices) > 1 else None,
        },
        "daily": daily_summaries,
        "methodology": "Trailing 7-day median $/GPU-hour, H100 SXM, US marketplace, "
                       "outlier removal at 2.5 sigma. See CCIR Methodology v1.0.",
        "calculated_utc": datetime.now(timezone.utc).isoformat(),
    }

# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------

def append_to_index(result: dict):
    INDEX_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    write_header = not INDEX_OUTPUT.exists()

    with open(INDEX_OUTPUT, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                "publication_date", "end_date", "window_days",
                "cri_h100", "n_observations", "valid_days",
                "low_confidence", "min", "max", "mean", "stdev",
                "ccir_version", "calculated_utc",
            ])
        writer.writerow([
            datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            result["end_date"],
            result["window_days"],
            result["index_value"],
            result.get("n_observations", 0),
            result.get("valid_days", 0),
            result.get("low_confidence", True),
            result.get("summary", {}).get("min"),
            result.get("summary", {}).get("max"),
            result.get("summary", {}).get("mean"),
            result.get("summary", {}).get("stdev"),
            result.get("ccir_version", "1.0.0"),
            result.get("calculated_utc"),
        ])
    print(f"  Index updated: {INDEX_OUTPUT}")


def write_audit(result: dict, end_date: str):
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    path = AUDIT_DIR / f"cri-h100-{end_date}.audit.json"
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Audit trail:   {path}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Calculate weekly CRI-H100 index")
    parser.add_argument("--end-date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--window", type=int, default=WINDOW_DAYS)
    args = parser.parse_args()

    print(f"\nCRI-H100 Calculation — week ending {args.end_date}")
    print("-" * 50)

    result = calculate(args.end_date, args.window)

    if result["index_value"] is None:
        print("ERROR: No valid observations. Cannot publish.")
        return

    print(f"  Index value:    ${result['index_value']:.4f} / GPU-hour")
    print(f"  Observations:   {result['n_observations']}")
    print(f"  Valid days:     {result['valid_days']} / {args.window}")
    if result["low_confidence"]:
        print(f"  WARNING: LOW CONFIDENCE — {result['low_confidence_reason']}")

    append_to_index(result)
    write_audit(result, args.end_date)

    print(f"\n✓ CRI-H100 = ${result['index_value']:.4f} (week ending {args.end_date})")


if __name__ == "__main__":
    main()
