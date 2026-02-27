# CRI-H100

**Compute Credit Index — H100 SXM (US)**

An open-methodology, independently verifiable weekly index of H100 SXM GPU rental rates in the US marketplace. Published by [CCIR](https://ccir.io) per [CCIR Methodology v1.1](https://github.com/ccir-index/ccir-methodology).

---

## What this is

CRI-H100 measures the trailing 7-day median $/GPU-hour for H100 SXM instances on the Vast.ai US marketplace. It is designed for use as a reference rate in credit documents, loan covenants, and collateral valuation — not for derivatives settlement.

Every index value in this repository is independently reproducible from the raw data using the verification script.

---

## Latest value

See [`outputs/cri-h100-index.csv`](/ccir-index/cri-h100/blob/main/outputs/cri-h100-index.csv) for the full published series.

---

## Repository structure

```
cri-h100/
├── pipeline/
│   ├── collect.py        # Daily data collection (all models, full archive)
│   ├── calculate.py      # Weekly index calculation
│   └── verify.py         # Independent verification script
├── data/
│   ├── archive/          # ★ Complete daily API responses (all GPUs, all regions)
│   │   ├── YYYY-MM-DD.json          # Full raw Vast.ai response
│   │   └── YYYY-MM-DD.meta.json     # Archive provenance + SHA-256
│   ├── h100-sxm-us/     # Filtered snapshots for CRI-H100 (primary index)
│   │   ├── YYYY-MM-DD.csv
│   │   └── YYYY-MM-DD.meta.json
│   ├── a100-sxm-us/     # Filtered snapshots for future CRI-A100
│   │   ├── YYYY-MM-DD.csv
│   │   └── YYYY-MM-DD.meta.json
│   ├── a100-pcie-us/    # A100 PCIe variant
│   ├── h200-sxm-us/     # H200 SXM (when listings appear)
│   ├── h100-pcie-us/    # H100 PCIe variant
│   ├── v100-us/         # V100 (long-horizon depreciation data)
│   └── l40s-us/         # L40S (inference-class GPU)
├── outputs/
│   ├── cri-h100-index.csv           # Append-only published index series
│   └── audits/
│       └── cri-h100-YYYY-MM-DD.audit.json
├── requirements.txt
└── README.md
```

### Data architecture

The collection pipeline makes one API call per day and saves two things:

1. **`data/archive/`** — The complete, unfiltered API response. Every GPU model, every geography, rented and unrented listings. This is the primary archival record. Every day of archive data is irreplaceable — the Vast.ai API returns only a real-time snapshot with no historical endpoint. Data collected today cannot be recovered retroactively.

2. **`data/{model-id}/`** — Filtered snapshots for each GPU model, produced by applying CCIR quality filters to the archived response. These are the inputs to index calculation. CRI-H100 (`h100-sxm-us`) is the published index. Other models are collected prospectively for future indices and cross-generational depreciation analysis.

---

## Reproducing any index value

Any third party can independently verify any published CRI-H100 value:

```
git clone https://github.com/ccir-index/cri-h100
cd cri-h100
pip install -r requirements.txt
python pipeline/verify.py --end-date 2026-03-01
```

Expected output:

```
Reproducing CRI-H100 — week ending 2026-03-01
----------------------------------------------------
  2026-02-23: 47 obs → 45 after outlier removal, median $1.8420 [hash ✓]
  ...
  Reproduced value: $1.8340
  Published value:  $1.8340
  MATCH ✓  CRI-H100 = $1.8340 independently verified.
```

---

## Collected GPU models

| Model ID | GPU | Index | Status |
|----------|-----|-------|--------|
| `h100-sxm-us` | H100 SXM | CRI-H100 | **Published weekly** |
| `a100-sxm-us` | A100 SXM | CRI-A100 | Collecting (future index) |
| `a100-pcie-us` | A100 PCIe | — | Collecting |
| `h200-sxm-us` | H200 SXM | CRI-H200 | Collecting (when available) |
| `h100-pcie-us` | H100 PCIe | — | Collecting |
| `v100-us` | V100 | — | Collecting (depreciation baseline) |
| `l40s-us` | L40S | — | Collecting |

Cross-generational data (A100, V100) is essential for constructing the market-derived depreciation curves described in CCIR Working Paper 2026-01.

---

## Methodology

**Data source:** Vast.ai public API (no authentication required)
**Primary index GPU:** H100 SXM
**Geography:** US listings only
**Quality filters:** reliability ≥ 0.90, active listings only (last updated ≤ 7 days)
**Outlier removal:** exclude observations > 2.5σ from trimmed mean
**Calculation:** trailing 7-day median $/GPU-hour
**Publication:** weekly (Thursdays)

Full methodology: [CCIR Methodology v1.1](https://github.com/ccir-index/ccir-methodology/blob/main/METHODOLOGY-v1.1.0.md)
Governance: [CCIR Governance Framework v1.0](https://github.com/ccir-index/ccir-methodology/blob/main/GOVERNANCE-v1.0.md)

**Known limitation:** CRI-H100 measures listed rental rates and does not adjust for intra-model performance variance (see Silicon Data, GPGPU '26). It should be interpreted as a price index, not a performance-adjusted compute value index. A performance-adjusted variant (CRI-H100-PA) is on the CCIR development roadmap.

---

## Data provenance

Each daily snapshot includes a SHA-256 hash of the data file, stored in the accompanying `.meta.json`. The archive also records the SHA-256 of the complete API response. This creates an append-only, tamper-evident audit trail: any modification to historical data produces a hash mismatch detectable by any third party. The verification script (`verify.py`) checks hashes automatically.

---

## License

Data and methodology: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
Code: [MIT](/ccir-index/cri-h100/blob/main/LICENSE)

---

## Contact

[research@ccir.io](mailto:research@ccir.io) | [ccir.io](https://ccir.io)
