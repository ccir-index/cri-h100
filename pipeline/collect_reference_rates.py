"""
CRI Reference Rate Collection — Hyperscaler & Mid-Market Rate Cards
====================================================================
Collects published/posted GPU rental rate cards from:
  - Azure  (prices.azure.com — fully public, no auth)
  - AWS    (pricing.us-east-1.amazonaws.com bulk JSON — fully public, no auth)
  - GCP    (cloudbilling.googleapis.com — requires free API key)
  - RunPod (api.runpod.io/graphql — requires free API key)

IMPORTANT — What these are and are not:
  These are POSTED RATE CARDS, not market-clearing prices. They measure the
  price a provider publishes for on-demand GPU compute. CRI-H100 (collect.py)
  measures marginal supply prices on a secondary marketplace. The spread
  between these two series is the "reliability premium" for enterprise-grade
  GPU compute. Do NOT blend these into CRI-H100 calculations.

  This file is intended for CRI-R (Reference Rate) companion series, published
  alongside CRI-H100 as contextual data — not as a benchmark input.

Governance notes:
  - Azure and AWS sources pass CCIR reproducibility standards (no credentials).
  - GCP requires a free API key (freely requestable, substantially reproducible).
  - RunPod requires a free API key (freely requestable, reproducibility conditional).
  - Adding any source as an official index input requires a Material Methodology
    Change under Governance Framework §5.2 (60-day advance notice).

Usage:
    python collect_reference_rates.py [--date YYYY-MM-DD] [--data-dir PATH]
    python collect_reference_rates.py --sources azure aws
    python collect_reference_rates.py --sources runpod --runpod-key YOUR_KEY

Environment variables (alternative to CLI flags):
    RUNPOD_API_KEY   — RunPod GraphQL API key
    GCP_API_KEY      — GCP Cloud Billing API key

Output:
    data/reference-rates/YYYY-MM-DD.json       — combined snapshot, all sources
    data/reference-rates/YYYY-MM-DD.meta.json  — provenance + SHA-256
    data/reference-rates/YYYY-MM-DD.csv        — flat CSV for analysis
"""

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AZURE_PRICING_URL = "https://prices.azure.com/api/retail/prices"
AZURE_API_VERSION = "2023-01-01-preview"

AWS_PRICING_URL = (
    "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/"
    "AmazonEC2/current/us-east-1/index.json"
)

GCP_BILLING_URL = "https://cloudbilling.googleapis.com/v1/services/6F81-5844-456A/skus"

RUNPOD_GRAPHQL_URL = "https://api.runpod.io/graphql"

# ---------------------------------------------------------------------------
# Source Configurations
# ---------------------------------------------------------------------------

# Azure: NC40ads_H100_v5 = 1x H100 SXM 80GB (40 vCPU)
AZURE_TARGETS = [
    {
        "id":          "azure-h100-eastus",
        "gpu_model":   "H100 SXM",
        "source":      "azure",
        "sku_name":    "Standard_NC40ads_H100_v5",
        "region":      "eastus",
        "gpus_per_vm": 1,
        "price_type":  "on_demand",
    },
    {
        "id":          "azure-h100-spot-eastus",
        "gpu_model":   "H100 SXM",
        "source":      "azure",
        "sku_name":    "Standard_NC40ads_H100_v5",
        "region":      "eastus",
        "gpus_per_vm": 1,
        "price_type":  "spot",
    },
    {
        "id":          "azure-a100-eastus",
        "gpu_model":   "A100 SXM",
        "source":      "azure",
        "sku_name":    "Standard_NC24ads_A100_v4",
        "region":      "eastus",
        "gpus_per_vm": 1,
        "price_type":  "on_demand",
    },
    {
        "id":          "azure-v100-eastus",
        "gpu_model":   "V100 SXM",
        "source":      "azure",
        "sku_name":    "Standard_NC6s_v3",
        "region":      "eastus",
        "gpus_per_vm": 1,
        "price_type":  "on_demand",
    },
    # H200 (Standard_ND96isr_H200_v5) not yet available in eastus — add when region support confirmed
]

# AWS: p5.48xlarge = 8x H100 SXM, p4d.24xlarge = 8x A100
AWS_TARGETS = [
    {
        "id":          "aws-h100-us-east-1",
        "gpu_model":   "H100 SXM",
        "source":      "aws",
        "instance":    "p5.48xlarge",
        "region":      "us-east-1",
        "gpus_per_vm": 8,
    },
    {
        "id":          "aws-a100-us-east-1",
        "gpu_model":   "A100 SXM",
        "source":      "aws",
        "instance":    "p4d.24xlarge",
        "region":      "us-east-1",
        "gpus_per_vm": 8,
    },
    {
        "id":          "aws-v100-us-east-1",
        "gpu_model":   "V100 SXM",
        "source":      "aws",
        "instance":    "p3.16xlarge",
        "region":      "us-east-1",
        "gpus_per_vm": 8,
    },
    # H200 (p5e.48xlarge) not yet available in us-east-1 — add when region support confirmed
]

# GCP: H100 and A100 GPU SKUs in us-central1
GCP_TARGETS = [
    {
        "id":          "gcp-h100-us-central1",
        "gpu_model":   "H100 SXM",
        "source":      "gcp",
        "sku_keyword": "H100",
        "region":      "us-central1",
        "spot":        False,
    },
    {
        "id":          "gcp-h100-spot-us-central1",
        "gpu_model":   "H100 SXM",
        "source":      "gcp",
        "sku_keyword": "H100",
        "region":      "us-central1",
        "spot":        True,
    },
    {
        "id":          "gcp-a100-us-central1",
        "gpu_model":   "A100 SXM",
        "source":      "gcp",
        "sku_keyword": "A100",
        "region":      "us-central1",
        "spot":        False,
    },
]

# RunPod GPU type IDs — aggregate rate card (not individual listings)
# IDs verified against RunPod GraphQL gpuTypes query 2026-03-03
RUNPOD_TARGETS = [
    {
        "id":        "runpod-h100-sxm-secure",
        "gpu_model": "H100 SXM",
        "source":    "runpod",
        "type_id":   "NVIDIA H100 80GB HBM3",
        "tier":      "secure",
    },
    {
        "id":        "runpod-h100-sxm-community",
        "gpu_model": "H100 SXM",
        "source":    "runpod",
        "type_id":   "NVIDIA H100 80GB HBM3",
        "tier":      "community",
    },
    {
        "id":        "runpod-h100-sxm-spot",
        "gpu_model": "H100 SXM",
        "source":    "runpod",
        "type_id":   "NVIDIA H100 80GB HBM3",
        "tier":      "secure_spot",
    },
    {
        "id":        "runpod-a100-sxm-secure",
        "gpu_model": "A100 SXM",
        "source":    "runpod",
        "type_id":   "NVIDIA A100-SXM4-80GB",
        "tier":      "secure",
    },
    {
        "id":        "runpod-a100-sxm-community",
        "gpu_model": "A100 SXM",
        "source":    "runpod",
        "type_id":   "NVIDIA A100-SXM4-80GB",
        "tier":      "community",
    },
    {
        "id":        "runpod-h200-sxm-secure",
        "gpu_model": "H200 SXM",
        "source":    "runpod",
        "type_id":   "NVIDIA H200",
        "tier":      "secure",
    },
    {
        "id":        "runpod-h200-sxm-community",
        "gpu_model": "H200 SXM",
        "source":    "runpod",
        "type_id":   "NVIDIA H200",
        "tier":      "community",
    },
    {
        "id":        "runpod-v100-sxm-community",
        "gpu_model": "V100 SXM",
        "source":    "runpod",
        "type_id":   "Tesla V100-SXM2-32GB",
        "tier":      "community",
    },
]

# ---------------------------------------------------------------------------
# Azure Fetcher — no auth required
# Accepts a target dict from AZURE_TARGETS.
# price_type "on_demand" → Consumption rows, no spot/low-priority/dev variants
# price_type "spot"      → Consumption rows where skuName contains "Spot"
# ---------------------------------------------------------------------------

def fetch_azure_rate(target: dict) -> dict | None:
    sku_name    = target["sku_name"]
    region      = target["region"]
    gpus        = target["gpus_per_vm"]
    price_type  = target["price_type"]   # "on_demand" or "spot"

    params = {
        "api-version": AZURE_API_VERSION,
        "$filter": (
            f"serviceName eq 'Virtual Machines' "
            f"and armSkuName eq '{sku_name}' "
            f"and armRegionName eq '{region}'"
        ),
    }
    resp = requests.get(AZURE_PRICING_URL, params=params, timeout=30)
    resp.raise_for_status()
    items = resp.json().get("Items", [])

    for item in items:
        if item.get("type") != "Consumption":
            continue
        sku_lower = item.get("skuName", "").lower()

        if price_type == "on_demand":
            # Exclude spot, low priority, and dev/test discount tiers
            if any(x in sku_lower for x in ("spot", "low priority", "dev")):
                continue
        elif price_type == "spot":
            if "spot" not in sku_lower:
                continue
        else:
            continue

        vm_price = float(item.get("unitPrice", 0))
        if vm_price == 0:
            continue

        return {
            "source_id":        target["id"],
            "source":           "azure",
            "gpu_model":        target["gpu_model"],
            "price_per_gpu_hr": round(vm_price / gpus, 6),
            "vm_price_hr":      round(vm_price, 6),
            "gpus_per_vm":      gpus,
            "region":           region,
            "sku":              sku_name,
            "price_type":       price_type,
            "rate_type":        "rate_card",
            "effective_date":   item.get("effectiveStartDate", ""),
            "reproducible":     True,
            "auth_required":    False,
            "collected_utc":    datetime.now(timezone.utc).isoformat(),
        }

    return None


# ---------------------------------------------------------------------------
# AWS Fetcher — no auth required (bulk JSON download, ~300 MB, 7-day cache)
# Accepts a target dict from AWS_TARGETS.
# ---------------------------------------------------------------------------

_aws_price_cache: dict | None = None


def _load_aws_prices(data_dir: Path) -> dict:
    global _aws_price_cache
    if _aws_price_cache:
        return _aws_price_cache

    cache_path = data_dir / "aws_price_cache" / "ec2-us-east-1.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    need_refresh = (
        not cache_path.exists()
        or (datetime.now().timestamp() - cache_path.stat().st_mtime) > 7 * 86400
    )
    if need_refresh:
        print("      Downloading AWS EC2 price list (~200-400MB, up to 60s)...")
        r = requests.get(AWS_PRICING_URL, stream=True, timeout=180)
        r.raise_for_status()
        with open(cache_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
        print(f"      Cached: {cache_path}")

    print("      Loading AWS price cache...", end=" ", flush=True)
    with open(cache_path, "r", encoding="utf-8") as f:
        _aws_price_cache = json.load(f)
    print("done")
    return _aws_price_cache


def fetch_aws_rate(target: dict, data_dir: Path) -> dict | None:
    instance_type = target["instance"]
    gpus          = target["gpus_per_vm"]
    region        = target["region"]

    data     = _load_aws_prices(data_dir)
    products = data.get("products", {})
    terms    = data.get("terms", {}).get("OnDemand", {})

    for sku_id, product in products.items():
        a = product.get("attributes", {})
        if (
            a.get("instanceType")    != instance_type
            or a.get("operatingSystem") != "Linux"
            or a.get("tenancy")         != "Shared"
            or a.get("capacitystatus")  != "Used"
        ):
            continue

        for term_val in terms.get(sku_id, {}).values():
            for pd_val in term_val.get("priceDimensions", {}).values():
                price = float(pd_val.get("pricePerUnit", {}).get("USD", 0))
                desc  = pd_val.get("description", "")
                # Skip $0 Capacity Block SKUs that share the same filter attributes
                if price == 0 or "Capacity Block" in desc:
                    continue
                return {
                    "source_id":        target["id"],
                    "source":           "aws",
                    "gpu_model":        target["gpu_model"],
                    "price_per_gpu_hr": round(price / gpus, 6),
                    "vm_price_hr":      round(price, 6),
                    "gpus_per_vm":      gpus,
                    "region":           region,
                    "sku":              instance_type,
                    "price_type":       "on_demand",
                    "rate_type":        "rate_card",
                    "effective_date":   "",
                    "reproducible":     True,
                    "auth_required":    False,
                    "collected_utc":    datetime.now(timezone.utc).isoformat(),
                }

    return None

# ---------------------------------------------------------------------------
# GCP Fetcher — free API key required
# ---------------------------------------------------------------------------

# GCP SKU description exclusion terms — filters out non-standard pricing tiers
_GCP_EXCLUDE = ("Commitment", "DWS", "Reserved", "Plus", "Mega", "Calendar")

# Cached SKU list — fetched once per run, shared across all targets
_gcp_sku_cache: list | None = None


def _load_gcp_skus(api_key: str) -> list:
    global _gcp_sku_cache
    if _gcp_sku_cache is not None:
        return _gcp_sku_cache

    params = {"key": api_key, "pageSize": 5000}
    all_skus, url = [], GCP_BILLING_URL
    while url:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        all_skus.extend(data.get("skus", []))
        npt = data.get("nextPageToken")
        params = {"key": api_key, "pageSize": 5000, "pageToken": npt} if npt else {}
        url = GCP_BILLING_URL if npt else None

    _gcp_sku_cache = all_skus
    return all_skus


def fetch_gcp_rate(target: dict, api_key: str) -> dict | None:
    if not api_key:
        return None
    try:
        all_skus = _load_gcp_skus(api_key)

        keyword = target["sku_keyword"]   # e.g. "H100" or "A100"
        region  = target["region"]        # e.g. "us-central1"
        is_spot = target["spot"]

        # Prefer 80GB variant when available (matches Vast.ai SXM inventory)
        prefer_80gb = keyword in ("H100", "A100")

        def sku_matches(s):
            desc = s.get("description", "")
            if keyword not in desc:
                return False
            if region not in s.get("serviceRegions", []):
                return False
            # Spot filter
            if is_spot and "Spot Preemptible" not in desc:
                return False
            if not is_spot and ("Preemptible" in desc or "Spot" in desc):
                return False
            # Exclude non-standard pricing tiers
            if any(x in desc for x in _GCP_EXCLUDE):
                return False
            return True

        matches = [s for s in all_skus if sku_matches(s)]

        if not matches:
            print(f"      WARN: No GCP SKU for {target['id']}")
            return None

        # Prefer 80GB SKU when multiple matches
        if prefer_80gb and len(matches) > 1:
            matches_80 = [s for s in matches if "80GB" in s.get("description", "")]
            if matches_80:
                matches = matches_80

        sku = matches[0]
        tiers = (sku.get("pricingInfo", [{}])[0]
                    .get("pricingExpression", {})
                    .get("tieredRates", [{}]))
        up = tiers[0].get("unitPrice", {}) if tiers else {}

        # GCP price = units (integer dollars) + nanos (fractional, 1e-9)
        units    = int(up.get("units") or 0)
        nanos    = int(up.get("nanos") or 0)
        price_hr = round(units + nanos / 1e9, 6)

        price_type = "spot_posted" if is_spot else "on_demand"
        return {
            "source_id":        target["id"],
            "source":           "gcp",
            "gpu_model":        target["gpu_model"],
            "price_per_gpu_hr": price_hr,
            "vm_price_hr":      None,
            "gpus_per_vm":      None,
            "region":           region,
            "sku":              sku.get("skuId"),
            "price_type":       price_type,
            "rate_type":        price_type,
            "effective_date":   (sku.get("pricingInfo", [{}])[0]
                                    .get("effectiveTime")),
            "reproducible":     True,
            "auth_required":    True,
            "collected_utc":    datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        print(f"      ERROR: GCP {target['id']}: {e}")
        return None


# ---------------------------------------------------------------------------
# RunPod Fetcher — free API key required
# GOVERNANCE NOTE: Returns aggregate rate card, not individual listings.
# ---------------------------------------------------------------------------

RUNPOD_QUERY = """
query {
  gpuTypes {
    id displayName memoryInGb
    secureCloud communityCloud
    securePrice communityPrice
    secureSpotPrice communitySpotPrice
    oneWeekPrice oneMonthPrice threeMonthPrice sixMonthPrice oneYearPrice
  }
}
"""

_runpod_cache: list | None = None


def fetch_runpod_rate(target: dict, api_key: str) -> dict | None:
    global _runpod_cache
    if not api_key:
        return None

    tier_field = {
        "secure":        "securePrice",
        "community":     "communityPrice",
        "secure_spot":   "secureSpotPrice",
        "community_spot":"communitySpotPrice",
    }

    try:
        if _runpod_cache is None:
            r = requests.post(
                RUNPOD_GRAPHQL_URL,
                params={"api_key": api_key},
                json={"query": RUNPOD_QUERY},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            r.raise_for_status()
            _runpod_cache = r.json().get("data", {}).get("gpuTypes", [])

        type_id = target["type_id"]
        match = next((g for g in _runpod_cache if g.get("id") == type_id), None)
        if not match:
            # Fallback: contains match on key substring
            match = next((g for g in _runpod_cache
                         if type_id[:10] in g.get("id", "")), None)
        if not match:
            print(f"      WARN: RunPod type '{type_id}' not found")
            return None

        field = tier_field.get(target["tier"])
        price = match.get(field)
        if price is None:
            print(f"      WARN: RunPod field '{field}' is null for {target['id']}")
            return None

        return {
            "source_id":        target["id"],
            "source":           "runpod",
            "gpu_model":        target["gpu_model"],
            "price_per_gpu_hr": round(float(price), 6),
            "vm_price_hr":      None,
            "gpus_per_vm":      1,
            "region":           "global",
            "sku":              match.get("id"),
            "price_type":       target["tier"],
            "effective_date":   None,
            "rate_type":        "rate_card_posted",
            "reproducible":     True,
            "auth_required":    True,
        }
    except Exception as e:
        print(f"      ERROR: RunPod {target['id']}: {e}")
        return None


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

CSV_FIELDS = [
    "source_id", "source", "gpu_model", "price_per_gpu_hr",
    "vm_price_hr", "gpus_per_vm", "region", "sku",
    "price_type", "rate_type", "effective_date",
    "reproducible", "auth_required", "collected_utc",
]


def write_outputs(results: list, date_str: str, data_dir: Path) -> str:
    out_dir = data_dir / "reference-rates"
    out_dir.mkdir(parents=True, exist_ok=True)
    collected_utc = datetime.now(timezone.utc).isoformat()
    for r in results:
        r["collected_utc"] = collected_utc

    archive = {
        "collection_date": date_str,
        "collected_utc":   collected_utc,
        "source_type":     "reference_rate_cards",
        "description":     (
            "Posted/published GPU rental rate cards from hyperscalers and "
            "mid-market platforms. Rate cards only — not market-clearing prices. "
            "Intended as CRI-R companion reference series, not CRI-H100 inputs."
        ),
        "results": results,
    }
    json_path = out_dir / f"{date_str}.json"
    raw = json.dumps(archive, separators=(",", ":"), sort_keys=True).encode()
    with open(json_path, "wb") as f:
        f.write(raw)
    sha256 = hashlib.sha256(raw).hexdigest()

    meta = {
        "ccir_version":    "1.1.0",
        "collection_date": date_str,
        "collected_utc":   collected_utc,
        "series_type":     "CRI-R (Reference Rate Companion)",
        "sources":         sorted({r["source"] for r in results}),
        "n_results":       len(results),
        "governance_note": (
            "These rate cards are companion reference data, not an IOSCO-compliant "
            "benchmark. Azure and AWS require no authentication and are independently "
            "reproducible. GCP and RunPod require a freely obtainable API key."
        ),
        "provenance": {"output_file": str(json_path), "sha256": sha256},
    }
    with open(out_dir / f"{date_str}.meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    with open(out_dir / f"{date_str}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(results)

    return sha256


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Collect CRI-R reference rate cards (hyperscalers + RunPod)"
    )
    parser.add_argument("--date",       default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--data-dir",   default=str(Path(__file__).resolve().parent.parent / "data"))
    parser.add_argument("--sources",    nargs="*",
                        default=["azure", "aws", "gcp", "runpod"],
                        choices=["azure", "aws", "gcp", "runpod"])
    parser.add_argument("--runpod-key", default=os.environ.get("RUNPOD_API_KEY", ""))
    parser.add_argument("--gcp-key",    default=os.environ.get("GCP_API_KEY", ""))
    args = parser.parse_args()

    date_str = args.date
    data_dir = Path(args.data_dir)
    sources  = set(args.sources)

    print(f"\nCRI Reference Rate Collection — {date_str}")
    print(f"Sources requested: {sorted(sources)}")
    print("=" * 60)
    print("REMINDER: These are rate cards, not CRI-H100 market inputs.\n")

    results = []

    if "azure" in sources:
        print("[Azure] Fetching on-demand rate cards (no auth required)...")
        for t in AZURE_TARGETS:
            print(f"  {t['id']}...", end=" ", flush=True)
            r = fetch_azure_rate(t)
            if r:
                results.append(r)
                print(f"${r['price_per_gpu_hr']:.4f}/GPU-hr")
            else:
                print("no data")
            time.sleep(0.4)

    if "aws" in sources:
        print("\n[AWS] Fetching on-demand rate cards (bulk JSON, no auth required)...")
        for t in AWS_TARGETS:
            print(f"  {t['id']}...", end=" ", flush=True)
            r = fetch_aws_rate(t, data_dir)
            if r:
                results.append(r)
                print(f"${r['price_per_gpu_hr']:.4f}/GPU-hr")
            else:
                print("no data")

    if "gcp" in sources:
        if not args.gcp_key:
            print("\n[GCP] SKIPPED — set GCP_API_KEY env var or pass --gcp-key")
        else:
            print("\n[GCP] Fetching rate cards (free API key)...")
            for t in GCP_TARGETS:
                print(f"  {t['id']}...", end=" ", flush=True)
                r = fetch_gcp_rate(t, args.gcp_key)
                if r:
                    results.append(r)
                    print(f"${r['price_per_gpu_hr']:.4f}/GPU-hr")
                else:
                    print("no data")
                time.sleep(0.3)

    if "runpod" in sources:
        if not args.runpod_key:
            print("\n[RunPod] SKIPPED — set RUNPOD_API_KEY env var or pass --runpod-key")
        else:
            print("\n[RunPod] Fetching rate card (free API key, aggregate not listings)...")
            for t in RUNPOD_TARGETS:
                print(f"  {t['id']}...", end=" ", flush=True)
                r = fetch_runpod_rate(t, args.runpod_key)
                if r:
                    results.append(r)
                    print(f"${r['price_per_gpu_hr']:.4f}/GPU-hr")
                else:
                    print("no data")

    print(f"\n[Output] Writing {len(results)} results...")
    if results:
        sha256 = write_outputs(results, date_str, data_dir)
        print(f"  data/reference-rates/{date_str}.json  (SHA-256: {sha256[:16]}...)")
        print(f"  data/reference-rates/{date_str}.csv")
        print(f"  data/reference-rates/{date_str}.meta.json")

    # Summary table
    if results:
        print(f"\n{'=' * 70}")
        print(f"  {'SOURCE ID':<35} {'GPU':<10} {'RATE TYPE':<18} {'$/GPU-HR':>8}")
        print(f"  {'-' * 68}")
        for r in sorted(results, key=lambda x: (x["source"], x["gpu_model"], x["rate_type"])):
            print(f"  {r['source_id']:<35} {r['gpu_model']:<10} "
                  f"{r['rate_type']:<18} ${r['price_per_gpu_hr']:>7.4f}")

    # Spread vs CRI-H100 if today's snapshot exists
    vast_meta = data_dir / "h100-sxm-us" / f"{date_str}.meta.json"
    if vast_meta.exists():
        try:
            with open(vast_meta) as f:
                vast = json.load(f)
            cri = vast.get("price_summary", {}).get("median")
            if cri:
                print(f"\n  CRI-H100 spot median today:  ${cri:.4f}/GPU-hr")
                for src in ("aws", "azure"):
                    hit = next((r for r in results
                                if r["source"] == src
                                and "h100" in r["source_id"]
                                and r["rate_type"] == "on_demand"), None)
                    if hit:
                        spread = hit["price_per_gpu_hr"] - cri
                        print(f"  {src.upper()} on-demand:              "
                              f"${hit['price_per_gpu_hr']:.4f}/GPU-hr  "
                              f"(premium: ${spread:.4f} = {spread/cri*100:.1f}%)")
        except Exception:
            pass
    print()


if __name__ == "__main__":
    main()
