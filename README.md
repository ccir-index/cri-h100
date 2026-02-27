# CRI-H100

**Compute Credit Index — H100 SXM (US)**

An open-methodology, independently verifiable GPU rental rate index for the US marketplace. Published by [CCIR — Compute Credit Index Research](https://ccir.io) per [CCIR Methodology v1.1.0](https://github.com/ccir-index/cri-h100/blob/main/METHODOLOGY-v1.1.0.md).

---

## What this is

CRI-H100 measures the trailing 7-day median $/GPU-hour for H100 SXM instances on the Vast.ai US marketplace. It is designed for use as a reference rate in credit documents, loan covenants, and collateral valuation — not for derivatives settlement.

Every index value in this repository is independently reproducible from the raw data using the verification script.

---

## Status

CRI-H100 is in its initial burn-in period. Daily data collection commenced February 2026. The first published index value will be announced at [ccir.io](https://ccir.io) when the minimum observation threshold is met.

---

## Multi-model data archive

CCIR collects daily snapshots across 9 GPU generations to support cross-generational depreciation curve construction. The Vast.ai API provides real-time snapshots only — historical data cannot be collected retroactively.

| Directory | GPU | Purpose |
|-----------|-----|---------|
| `data/h100-sxm-us/` | H100 SXM | Primary index — CRI-H100 |
| `data/a100-sxm-us/` | A100 SXM | Depreciation curve — A100→H100 transition |
| `data/a100-pcie-us/` | A100 PCIe | A100 variant |
| `data/h200-us/` | H200 | Next-generation transition tracking |
| `data/h200-nvl-us/` | H200 NVL | H200 variant |
| `data/h100-pcie-us/` | H100 PCIe | H100 variant |
| `data/v100-us/` | V100 | Long-horizon depreciation (2+ generations) |
| `data/l40s-us/` | L40S | Inference-class GPU market |
| `data/rtx4090-us/` | RTX 4090 | Consumer GPU market context |

Daily snapshots are archived in `data/archive/` as complete API responses across all models.

---

## Repository structure

```
cri-h100/
├── pipeline/
│   ├── collect.py      # Daily data collection from Vast.ai API (9 models)
│   ├── calculate.py    # Weekly index calculation
│   └── verify.py       # Independent verification script
├── data/
│   ├── archive/                     # Complete daily API responses (all models)
│   ├── h100-sxm-us/                # CRI-H100 primary data
│   │   ├── YYYY-MM-DD.csv          # Daily filtered snapshots
│   │   └── YYYY-MM-DD.meta.json    # Collection metadata + SHA-256 hash
│   ├── a100-sxm-us/
│   ├── a100-pcie-us/
│   ├── h200-us/
│   ├── h200-nvl-us/
│   ├── h100-pcie-us/
│   ├── v100-us/
│   ├── l40s-us/
│   └── rtx4090-us/
├── outputs/
│   ├── cri-h100-index.csv           # Append-only published index series
│   └── audits/
│       └── cri-h100-YYYY-MM-DD.audit.json  # Full calculation audit trail
├── METHODOLOGY-v1.1.0.md
├── GOVERNANCE-v1_0.md
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

Output will resemble:

```
Reproducing CRI-H100 — week ending YYYY-MM-DD
----------------------------------------------------
  YYYY-MM-DD: N obs → N after outlier removal, median $X.XXXX
  ...
  Reproduced value: $X.XXXX
  Published value:  $X.XXXX
  MATCH ✓  CRI-H100 = $X.XXXX independently verified.
```

---

## Methodology

| | |
|---|---|
| **Data source** | Vast.ai public API (no authentication required) |
| **Target GPU** | H100 SXM |
| **Geography** | US listings only |
| **Quality filters** | reliability ≥ 0.90, active listings only (last updated ≤ 7 days) |
| **Outlier removal** | exclude observations > 2.5σ from trimmed mean |
| **Calculation** | trailing 7-day median $/GPU-hour |
| **Publication** | weekly — Thursdays |

Full methodology: [CCIR Methodology v1.1.0](https://github.com/ccir-index/cri-h100/blob/main/METHODOLOGY-v1.1.0.md)

Governance framework: [CCIR Governance Framework v1.0](https://github.com/ccir-index/cri-h100/blob/main/GOVERNANCE-v1_0.md)

**Known limitation:** CRI-H100 measures listed rental rates and does not adjust for intra-model performance variance (see Silicon Data, GPGPU '26). It should be interpreted as a price index, not a performance-adjusted compute value index. A performance-adjusted variant (CRI-H100-PA) is on the CCIR development roadmap.

---

## Data provenance

Each daily snapshot includes a SHA-256 hash of the raw data file, stored in the accompanying `.meta.json` file. This creates an append-only audit trail: any modification to historical data would produce a hash mismatch detectable by any third party.

---

## License

Data and methodology: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
Code: [MIT](LICENSE)

---

## Contact

[research@ccir.io](mailto:research@ccir.io) · [ccir.io](https://ccir.io)
