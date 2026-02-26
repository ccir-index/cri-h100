# CRI-H100

**Compute Credit Index — H100 SXM (US)**

An open-methodology, independently verifiable daily index of H100 SXM GPU rental rates in the US marketplace. Published by [CCIR](https://ccir.io) per [CCIR Methodology v1.0](https://github.com/ccir-index/ccir-methodology).

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
├── pipeline/
│   ├── collect.py      # Daily data collection from Vast.ai API
│   ├── calculate.py    # Weekly index calculation
│   └── verify.py       # Independent verification script
├── data/
│   └── raw/
│       ├── YYYY-MM-DD.csv           # Daily filtered snapshots
│       └── YYYY-MM-DD.meta.json     # Collection metadata + SHA-256 hash
├── outputs/
│   ├── cri-h100-index.csv           # Append-only published index series
│   └── audits/
│       └── cri-h100-YYYY-MM-DD.audit.json  # Full calculation audit trail
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
python pipeline/verify.py --end-date 2026-03-01
```

Expected output:
```
Reproducing CRI-H100 — week ending 2026-03-01
----------------------------------------------------
  2026-02-23: 47 obs → 45 after outlier removal, median $1.8420
  ...
  Reproduced value: $1.8340
  Published value:  $1.8340
  MATCH ✓  CRI-H100 = $1.8340 independently verified.
```

---

## Methodology

**Data source:** Vast.ai public API (no authentication required)  
**Target GPU:** H100 SXM  
**Geography:** US listings only  
**Quality filters:** reliability ≥ 0.90, active listings only (last updated ≤ 7 days)  
**Outlier removal:** exclude observations > 2.5σ from trimmed mean  
**Calculation:** trailing 7-day median $/GPU-hour  
**Publication:** weekly  

Full methodology: [CCIR Methodology v1.0](https://github.com/ccir-index/ccir-methodology/blob/main/METHODOLOGY-v1.0.md)

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

research@ccir.io | [ccir.io](https://ccir.io)
