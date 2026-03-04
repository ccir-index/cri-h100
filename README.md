# CRI-H100
**Compute Credit Index — H100 SXM (US)**

An open-methodology, independently verifiable weekly index of H100 SXM GPU rental rates in the US marketplace. Published by [CCIR](https://ccir.io) per [CCIR Methodology v1.1.0](https://github.com/ccir-index/ccir-methodology/blob/main/METHODOLOGY-v1.1.0.md).

CCIR does not operate a GPU rental marketplace and has no commercial interest in GPU rental prices. CRI-H100 is calculated exclusively from public API data — no submissions, no proprietary feeds, no terminal subscription required. See [Governance Framework §§3.1 and 3.5](https://github.com/ccir-index/ccir-methodology/blob/main/GOVERNANCE-v1_0.md) for the full structural independence disclosure.

---

## What this is

CRI-H100 measures the trailing 7-day median $/GPU-hour for H100 SXM instances on the Vast.ai US marketplace. It is designed for use as a reference rate in credit documents, loan covenants, and collateral valuation — not for derivatives settlement.

Every index value in this repository is independently reproducible from the raw data using the verification script.

---

## Latest value

See [`outputs/cri-h100-index.csv`](outputs/cri-h100-index.csv) for the full published series.

---

## Repository structure

```
cri-h100/
├── .github/workflows/
│   └── collect.yml                          # GitHub Actions daily collection
├── pipeline/
│   ├── collect.py                           # Daily data collection from Vast.ai API
│   ├── calculate.py                         # Weekly index calculation
│   ├── verify.py                            # Independent verification script
│   └── collect_reference_rates.py          # Weekly CRI-R rate card collection
├── data/
│   ├── archive/                             # Complete daily API responses (all models)
│   │   ├── YYYY-MM-DD.json
│   │   └── YYYY-MM-DD.meta.json
│   ├── h100-sxm-us/                         # Filtered snapshots — CRI-H100 (primary index)
│   │   ├── YYYY-MM-DD.csv                   # Daily filtered snapshots
│   │   └── YYYY-MM-DD.meta.json             # Collection metadata + SHA-256 hash
│   ├── a100-sxm-us/                         # A100 SXM — depreciation curve data
│   ├── h200-us/                             # H200 — next-generation transition data
│   ├── v100-us/                             # V100 — long-horizon depreciation data
│   ├── [other model directories]/
│   └── reference-rates/                     # CRI-R companion series (posted rate cards)
│       ├── YYYY-MM-DD.json                  # Combined snapshot — all sources
│       ├── YYYY-MM-DD.csv                   # Flat CSV for analysis
│       └── YYYY-MM-DD.meta.json             # Provenance + SHA-256
├── outputs/
│   ├── cri-h100-index.csv                   # Append-only published index series
│   └── audits/
│       └── cri-h100-YYYY-MM-DD.audit.json   # Full calculation audit trail
├── requirements.txt
└── README.md
```

---

## Reproducing any index value

Any third party can independently verify any published CRI-H100 value:

```bash
git clone https://github.com/ccir-index/cri-h100
cd cri-h100
pip install -r requirements.txt
python pipeline/verify.py --end-date YYYY-MM-DD
```

The `--end-date` flag is the Wednesday ending the calculation window (the day before Thursday publication). The script queries the same Vast.ai public API endpoint used in the original collection, applies the published filters, and compares the reproduced median against the published value and SHA-256 hashes. See [REPRODUCIBILITY.md](https://github.com/ccir-index/ccir-methodology/blob/main/REPRODUCIBILITY.md) for the full verification walkthrough.

---

## Methodology

| | |
|---|---|
| **Data source** | Vast.ai public API (no authentication required) |
| **Target GPU** | H100 SXM |
| **Geography** | US listings only |
| **Quality filters** | Reliability ≥ 0.90, active within 7 days, unrented, ≥ 1 GPU |
| **Outlier removal** | Exclude observations > 2.5σ from trimmed mean |
| **Calculation** | Trailing 7-day median $/GPU-hour |
| **Publication** | Weekly — Thursdays |

Full specification: [CCIR Methodology v1.1.0](https://github.com/ccir-index/ccir-methodology/blob/main/METHODOLOGY-v1.1.0.md)

**Known limitation:** CRI-H100 measures listed rental rates and does not adjust for intra-model performance variance (see Silicon Data, GPGPU '26). It should be interpreted as a price index, not a performance-adjusted compute value index. A performance-adjusted variant (CRI-H100-PA) is on the CCIR development roadmap.

---

## CRI-R — Reference Rate Companion Series

CRI-R collects weekly posted rate cards from hyperscalers and mid-market platforms and publishes them at `data/reference-rates/`. It is **not** an input to CRI-H100 and is **not** an IOSCO-compliant benchmark. It exists to quantify the **reliability premium** — the spread between CRI-H100 (Tier 3 marginal spot) and what the market charges for managed infrastructure, guaranteed capacity, and enterprise SLAs.

| Source | Auth Required | Tier | Models |
|--------|--------------|------|--------|
| Azure (prices.azure.com) | None | Tier 1 | H100, A100, V100 |
| AWS (pricing.us-east-1.amazonaws.com) | None | Tier 1 | H100, A100, V100 |
| GCP (cloudbilling.googleapis.com) | Free API key | Tier 1 | H100, A100 |
| RunPod (api.runpod.io/graphql) | Free API key | Tier 2 | H100, A100, H200 |

**Coverage:** 4 platforms · 18 rate points per collection · updated weekly

Azure and AWS sources require no credentials and are fully independently reproducible. GCP and RunPod require a freely obtainable API key; the requirement is disclosed in each `.meta.json` file.

Adding any CRI-R source as an official CRI-H100 benchmark input requires a Material Methodology Change under Governance Framework §5.2 (60-day advance notice).

---

## Data provenance

Each daily snapshot includes a SHA-256 hash of the raw data file, stored in the accompanying `.meta.json` file. This creates an append-only audit trail: any modification to historical data would produce a hash mismatch detectable by any third party.

---

## License

Data and methodology: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · Code: [MIT](LICENSE)

---

## Contact

[research@ccir.io](mailto:research@ccir.io) | [ccir.io](https://ccir.io)
