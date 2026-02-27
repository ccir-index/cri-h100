# CCIR Methodology v1.1.0
## Compute Credit Index Research — CRI-H100 Index Methodology

**Version:** 1.1.0  
**Effective Date:** April 2026  
**Published by:** CCIR — Compute Credit Index Research  
**Repository:** https://github.com/ccir-index/ccir-methodology  
**Companion document:** CCIR Governance Framework v1.0  
**Contact:** research@ccir.io  

---

## Table of Contents

1. [Definitions](#1-definitions)
2. [Purpose and Scope](#2-purpose-and-scope)
3. [Index Definition](#3-index-definition)
4. [Data Source](#4-data-source)
5. [Geographic Scope](#5-geographic-scope)
6. [Quality Filters](#6-quality-filters)
7. [Outlier Removal](#7-outlier-removal)
8. [Index Calculation](#8-index-calculation)
9. [Publication Rules](#9-publication-rules)
10. [Low Confidence Flags](#10-low-confidence-flags)
11. [Known Limitations](#11-known-limitations)
12. [Audit and Verification](#12-audit-and-verification)
13. [Appendix A — Calculation Parameters Summary](#appendix-a--calculation-parameters-summary)
14. [Appendix B — Version History](#appendix-b--version-history)

---

## 1. Definitions

The following technical terms are used throughout this document.

**"Index"** means CRI-H100, as defined in Section 3.

**"Observation"** means a single per-GPU listed rental price derived from a Qualifying Listing, calculated as `dph_total / num_gpus`, expressed in USD per GPU-hour.

**"Qualifying Listing"** means a listing satisfying all eligibility criteria and quality filters set forth in Section 6.

**"Calculation Window"** means the trailing seven (7) calendar days ending on the applicable Publication Date.

**"Publication Date"** means each Thursday on which the Index is scheduled to be published.

**"Low Confidence Value"** means an Index value published with an automatic low confidence flag pursuant to the minimum sample thresholds in Section 10.

**"SHA-256 Hash"** means the output of the SHA-256 cryptographic hash function applied to a data file, used as a tamper-evident provenance record.

For governance, legal, and institutional definitions — including Administrator, Calculation Agent, Fallback Value, Material Methodology Change, Restatement, and Business Day — see the CCIR Governance Framework v1.0.

---

## 2. Purpose and Scope

### 2.1 Purpose

The Compute Credit Index (CRI) is an open-methodology benchmark designed to provide a transparent, independently verifiable reference rate for GPU compute rental prices. CRI is designed specifically for use as a reference rate in credit documents, loan covenants, collateral valuation frameworks, and structured finance instruments.

CRI is not designed for derivatives settlement. It is not a trading benchmark. It is an analytical reference standard for the GPU-backed credit market.

The absence of a standardized, independently verifiable compute rental reference rate creates material risk in GPU-backed lending. Without an agreed benchmark, lenders must rely on bilateral estimates, broker quotes, or proprietary valuations that cannot be independently verified by counterparties, trustees, or rating agencies. CRI is designed to fill this gap.

### 2.2 What CRI Measures

CRI measures the price at which H100 SXM GPU instances are listed for on-demand rental on the Vast.ai marketplace in the United States. It is a price index, not a performance index. CRI reflects listed rental rates, not executed transaction prices. The distinction between listed and executed prices is a known limitation disclosed in Section 11.2.

### 2.3 What CRI Does Not Measure

CRI does not measure:

- Executed transaction prices (actual rental agreements entered into by counterparties)
- Reserved or committed capacity pricing
- Private contract rates or enterprise pricing
- Non-US marketplace rates (to be addressed in separate regional indices)
- Hardware resale or secondary market values
- Performance-adjusted compute value (see Section 11.3)
- Hyperscaler pricing (AWS, Azure, GCP)

### 2.4 Intended Users

This Methodology document is intended for:

- Analysts and researchers seeking to understand or reproduce the Index calculation
- Rating agencies evaluating the Index for use as a reference rate
- Third parties independently verifying published Index values
- Attorneys and trustees requiring a precise technical specification for citation in legal documents

For governance, conflict of interest, fallback provisions, IP and licensing, and legal citation language, see the companion CCIR Governance Framework v1.0.

---

## 3. Index Definition

### 3.1 CRI-H100

| Field | Value |
|-------|-------|
| Full name | Compute Credit Index — H100 SXM (United States) |
| Short name | CRI-H100 |
| Unit | US dollars per GPU-hour ($/GPU-hour) |
| Precision | Four decimal places (e.g., $1.8340) |
| Publication frequency | Weekly |
| Publication day | Thursday |
| Calculation window | Trailing 7 calendar days |
| Base currency | USD |

### 3.2 Formal Definition

CRI-H100 is defined as the median price per GPU-hour, denominated in USD, of Qualifying Listings for H100 SXM on-demand GPU rental on the Vast.ai marketplace in the United States, calculated over a trailing 7-day Calculation Window, after application of quality filters and outlier removal as specified in Sections 6 and 7 of this Methodology.

### 3.3 Version Binding

Any reference to CRI-H100 in a legal document, credit agreement, or covenant should specify the methodology version in effect at the time of execution. Contracts citing a specific version will be governed by that version's methodology regardless of subsequent updates. For change control provisions and suggested citation language, see the CCIR Governance Framework v1.0.

---

## 4. Data Source

### 4.1 Primary Data Source

| Field | Value |
|-------|-------|
| Source | Vast.ai GPU marketplace |
| API endpoint | `https://console.vast.ai/api/v0/bundles/` |
| Authentication required | No |
| Access method | Public HTTP API, no API key required |

Vast.ai operates a public GPU rental marketplace where compute providers list GPU instances for on-demand rental. The API endpoint used by CCIR returns all currently available (unrented, rentable) listings matching specified query parameters.

### 4.2 Why Vast.ai

Vast.ai was selected as the primary data source for the following reasons:

**Reproducibility.** The Vast.ai API requires no authentication. Any counterparty, attorney, rating agency, trustee, or third party can independently query the same API and reproduce CCIR's inputs without any data licensing agreement, proprietary access, or commercial relationship with CCIR. This is the foundational requirement for a credit reference rate.

**Transparency.** Listing data includes provider reliability scores, geographic information, hardware specifications, and pricing — sufficient to apply meaningful, verifiable quality filters.

**Market representation.** Vast.ai is among the largest public GPU rental marketplaces by listing volume. While it does not represent the entire GPU rental market, it provides a reproducible proxy for on-demand spot market pricing in the absence of an industry-wide transaction reporting standard.

**Open access permanence.** CCIR has no contractual relationship with Vast.ai. The data is publicly available. CCIR's independence from any single data provider is structural, not contractual.

### 4.3 Source Limitations

Vast.ai represents one marketplace. CRI-H100 v1.1 does not incorporate data from other marketplaces (RunPod, CoreWeave, Lambda Labs, or others). The Index reflects Vast.ai marketplace dynamics, which may differ from broader market rates. See Section 11.1.

### 4.4 Data Source Roadmap

CCIR intends to expand CRI to include additional data sources in future methodology versions, beginning with authenticated marketplace sources. Any such expansion constitutes a Material Methodology Change subject to the change control provisions in the CCIR Governance Framework v1.0.

---

## 5. Geographic Scope

### 5.1 Coverage

CRI-H100 v1.1 covers United States listings only. A listing is classified as United States if its `geolocation` field, as returned by the Vast.ai API, ends with `, US`.

### 5.2 Rationale

US-only scope was selected because:

- The majority of GPU-backed credit agreements governed by US law involve US-domiciled collateral
- US rental rates and non-US rental rates may reflect different supply and demand dynamics warranting separate indices
- A single-geography index is simpler to interpret and less susceptible to currency and cross-jurisdictional regulatory variation

### 5.3 Regional Expansion

CCIR intends to publish separate regional indices (CRI-H100-EU, CRI-H100-APAC) in future versions. Regional indices will use identical methodology applied to their respective geographies and will be treated as separate indices, not updates to CRI-H100.

---

## 6. Quality Filters

The following filters are applied to raw listings before index calculation. All filters are applied sequentially in the order listed. A listing must satisfy all filters to become a Qualifying Listing.

### 6.1 GPU Model Filter

Only listings with `gpu_name` equal to `H100 SXM` are included. Listings for H100 PCIe, H100 NVL, or other H100 variants are excluded. This filter ensures the Index measures a consistent hardware specification.

### 6.2 Availability Filter

Only listings where both conditions are met are included:
- `rentable` equals `true`
- `rented` equals `false`

This ensures the Index reflects currently available capacity at the listed price.

### 6.3 Reliability Filter

Only listings with a provider reliability score (`reliability2`) of 0.90 or greater are included. The reliability score is a composite metric published by Vast.ai reflecting provider uptime and fulfillment history. Listings below this threshold are excluded as unreliable proxies for market rate.

### 6.4 Minimum GPU Count Filter

Only listings with `num_gpus` greater than or equal to 1 are included.

### 6.5 Staleness Filter

Only listings with a `start_date` timestamp within the prior seven (7) calendar days are included. Listings not updated within this window are treated as stale and excluded.

**Technical note:** The Vast.ai API field originally intended for staleness filtering (`last_seen`) is not consistently populated as of the date of this Methodology. CCIR uses `start_date` as the operative staleness indicator. This substitution is logged in each daily metadata file. CCIR will revert to `last_seen` if Vast.ai restores consistent population of that field and will document any such change in the methodology changelog.

### 6.6 Geography Filter

Only listings where `geolocation` ends with `, US` are included, per Section 5.

---

## 7. Outlier Removal

### 7.1 Purpose

Outlier removal is applied to prevent anomalous listings — misconfigurations, pricing errors, or deliberate manipulation attempts — from distorting the Index value. Outlier removal is applied after quality filtering and before index calculation.

### 7.2 Standard Method

**Step 1 — Compute per-GPU price**

For each Qualifying Listing, compute:
```
Observation = dph_total / num_gpus
```

**Step 2 — Compute trimmed mean**

Sort all Observations. Remove the top 10% and bottom 10% by value. Compute the arithmetic mean of the remaining Observations. This is the trimmed mean.

**Step 3 — Compute standard deviation**

Compute the standard deviation of the full (untrimmed) Observation series.

**Step 4 — Apply threshold**

Exclude any Observation where:
```
|Observation - trimmed_mean| > 2.5 × standard_deviation
```

The remaining Observations form the cleaned series used for Index calculation.

### 7.3 Manifest Error Override

In the event that the standard outlier removal procedure fails to exclude a clearly erroneous data point — defined as an Observation deviating from the trimmed mean by more than 10 times the standard deviation — the Calculation Agent may flag the Observation for Administrator review. The Administrator may exclude such an Observation provided that:

- The exclusion is documented in the calculation audit trail
- The reason for exclusion is publicly disclosed in the publication metadata
- The exclusion does not alter any prior published value

### 7.4 Threshold Rationale

A 2.5 sigma threshold removes genuine outliers while preserving meaningful price dispersion. A tighter threshold would risk excluding legitimate price variation; a looser threshold would permit distorting Observations to influence the Index.

### 7.5 Minimum Sample Requirement

If fewer than four (4) Observations remain after quality filtering, outlier removal is not applied and the Low Confidence flag is set per Section 10.

---

## 8. Index Calculation

### 8.1 Daily Collection

CCIR collects a snapshot of Qualifying Listings from the Vast.ai API once per calendar day. Each snapshot is stored as a timestamped CSV file. A SHA-256 Hash of each CSV file is computed and recorded in an accompanying metadata JSON file at the time of collection. The collection process is fully documented in the open-source pipeline at https://github.com/ccir-index/cri-h100.

### 8.2 Weekly Index Calculation

CRI-H100 is calculated weekly as follows:

**Step 1 — Define the Calculation Window**

The Calculation Window consists of the seven (7) calendar days ending on the Wednesday immediately preceding each Thursday Publication Date, inclusive of both the start and end dates.

**Step 2 — Load daily snapshots**

For each day in the Calculation Window, load the cleaned Observation series (post quality filter, post outlier removal per Sections 6 and 7).

**Step 3 — Apply minimum daily observation threshold**

Days with fewer than ten (10) Qualifying Observations after outlier removal are excluded from the Calculation Window. Days for which no data file exists (collection failed) are treated as missing.

**Step 4 — Pool Observations**

All cleaned Observations from all included days in the Calculation Window are pooled into a single Observation series.

**Step 5 — Calculate Index value**

CRI-H100 for the week is the median of the pooled Observation series, rounded to four decimal places.

### 8.3 Why Median

The median was selected over alternative measures for the following reasons:

**Manipulation resistance.** The median is robust to extreme values and substantially more resistant to manipulation by a small number of anomalous listings than the mean.

**Interpretability.** The median is the price at which half the Qualifying market is cheaper and half is more expensive — an intuitive definition for a rental rate reference.

**Credit appropriateness.** For loan covenant and collateral valuation purposes, a robust central tendency measure is more appropriate than a volume-weighted measure that could be influenced disproportionately by large listings.

**Reproducibility.** The median requires no volume data, which has uncertain reliability in the current Vast.ai dataset.

---

## 9. Publication Rules

### 9.1 Publication Schedule

CRI-H100 is published weekly every Thursday, reflecting the Calculation Window ending on the prior Wednesday.

### 9.2 Publication Format

Each weekly publication record includes:

| Field | Description |
|-------|-------------|
| `publication_date` | Date of publication (YYYY-MM-DD) |
| `end_date` | Last day of Calculation Window |
| `window_days` | Length of Calculation Window in days |
| `cri_h100` | Index value ($/GPU-hour, 4 decimal places) |
| `n_observations` | Total Observations used in calculation |
| `valid_days` | Number of days in window meeting minimum threshold |
| `low_confidence` | Boolean flag per Section 10 |
| `min` | Minimum Observation in window |
| `max` | Maximum Observation in window |
| `mean` | Mean of pooled Observations |
| `stdev` | Standard deviation of pooled Observations |
| `ccir_version` | Methodology version (e.g., 1.1.0) |
| `calculated_utc` | UTC timestamp of calculation |

### 9.3 Publication Locations

CRI-H100 values are published to:

- `outputs/cri-h100-index.csv` in the cri-h100 GitHub repository
- The CCIR website at ccir.io

### 9.4 Append-Only Commitment

The published Index series is append-only. Once a weekly value is published, it will not be revised except under Restatement provisions set out in the CCIR Governance Framework v1.0.

---

## 10. Low Confidence Flags

### 10.1 Definition

A Low Confidence flag indicates that the published Index value is based on fewer Observations than CCIR considers sufficient for full statistical reliability. A flagged value is published rather than suppressed — suppressing values would create gaps in the historical record that create their own interpretive problems. Users should apply additional judgment when relying on Low Confidence Values.

### 10.2 Triggers

| Condition | Treatment |
|-----------|-----------|
| Fewer than 10 Observations on a given collection day | Day excluded from Calculation Window |
| Fewer than 3 valid days in the 7-day Calculation Window | Weekly value flagged as Low Confidence |
| Fewer than 4 Observations in the pooled Observation series | Weekly value flagged as Low Confidence |

### 10.3 Interpretation

A Low Confidence flag does not invalidate the Index value. It signals that the value is based on a thinner-than-normal data set and may be less representative of prevailing market rates. For guidance on handling Low Confidence Values in credit documents, see the CCIR Governance Framework v1.0.

---

## 11. Known Limitations

CCIR is committed to transparent disclosure of the limitations of CRI-H100. Each limitation below is paired with the mitigation currently in place.

### 11.1 Single Data Source

**Limitation.** CRI-H100 v1.1 is based solely on Vast.ai marketplace data. Enterprise contracts, hyperscaler pricing, private capacity agreements, and other marketplace rates are not reflected.

**Mitigation.** Vast.ai is selected because it is the largest publicly accessible, unauthenticated GPU rental data source — the most reproducible available proxy for on-demand spot pricing. CCIR discloses Observation counts with each publication. Additional data sources are a roadmap priority.

### 11.2 Listed Prices vs. Executed Prices

**Limitation.** CRI-H100 measures listed rental rates, not executed transaction prices. A listing appearing at $1.80/GPU-hour may or may not be rented at that price. The Index reflects willingness to supply at a given price, not confirmed transaction activity.

**Mitigation.** This limitation is structural to any open-data compute index at this stage of market development. Executed transaction data requires proprietary data relationships incompatible with the open-methodology requirement. CCIR will pursue executed transaction data sources in future methodology development.

### 11.3 Performance Variance (Silicon Lottery)

**Limitation.** CRI-H100 does not adjust for intra-model performance variance. Research published at the GPGPU '26 conference (Silicon Data, March 2026) documents performance variation of up to 38% within the H100 SXM model across cloud providers, driven by manufacturing variation and provider configuration. Two providers listing at the same price may offer economically different products.

**Mitigation.** CRI-H100 is explicitly defined as a price index, not a performance-adjusted compute value index. CCIR is developing CRI-H100-PA (performance-adjusted) as a separate index, pending a standardized performance benchmarking methodology.

### 11.4 Thin Market Risk

**Limitation.** The US H100 SXM market on Vast.ai is currently thin. Daily Observation counts in early 2026 are in the range of 8–20 Qualifying Listings, limiting statistical robustness and increasing sensitivity to individual listing behavior.

**Mitigation.** CCIR publishes daily Observation counts and dispersion metrics with each Index publication and applies the Low Confidence flag when Observations fall below minimum thresholds. As the GPU rental market matures and additional data sources are incorporated, Observation counts are expected to increase.

---

## 12. Audit and Verification

### 12.1 Daily Audit Trail

Each daily collection produces:

- A CSV file of Qualifying Listings (`data/raw/YYYY-MM-DD.csv`)
- A metadata JSON file (`data/raw/YYYY-MM-DD.meta.json`)

The metadata file contains: collection timestamp (UTC), API query parameters, filter parameters applied, Observation counts at each filter stage, summary statistics of the price distribution, and the SHA-256 Hash of the CSV file.

### 12.2 Weekly Calculation Audit Trail

Each weekly Index publication produces a full audit trail JSON file (`outputs/audits/cri-h100-YYYY-MM-DD.audit.json`) documenting:

- Each day in the Calculation Window and its status (included, excluded, missing)
- Observation counts before and after outlier removal for each included day
- Daily median prices
- Final pooled Observation count
- Calculated Index value
- Low Confidence flag status and reason if flagged

### 12.3 Hash Verification

The SHA-256 Hash of each daily CSV file is recorded in the metadata file and committed to the GitHub repository at the time of collection. Any modification to historical data produces a hash mismatch detectable by any third party using the open-source verification script.

### 12.4 Independent Verification

Any third party can independently reproduce any published CRI-H100 value using:

1. The raw data files in the GitHub repository
2. The verification script at `pipeline/verify.py`
3. This Methodology document

The verification script applies the identical filters, outlier removal, and calculation specified in this document and confirms whether the reproduced value matches the published value. Independent reproducibility is the foundational credibility mechanism of the Index.

---

## Appendix A — Calculation Parameters Summary

| Parameter | Value |
|-----------|-------|
| Target GPU | H100 SXM |
| Data source | Vast.ai public API |
| Geography | United States |
| Min reliability score | 0.90 |
| Min GPU count | 1 |
| Max listing age | 7 days |
| Staleness field | `start_date` (see Section 6.5) |
| Outlier removal method | Trimmed mean ± 2.5σ |
| Trim percentage | 10% each tail |
| Calculation window | Trailing 7 calendar days |
| Index statistic | Median |
| Min daily observations | 10 |
| Min valid days per window | 3 |
| Publication frequency | Weekly |
| Publication day | Thursday |
| Precision | 4 decimal places |
| Methodology version | 1.1.0 |

---

## Appendix B — Version History

| Version | Effective Date | Change Type | Summary |
|---------|---------------|-------------|---------|
| 1.0.0 | March 2026 | Initial | First publication |
| 1.1.0 | April 2026 | Minor | Separated from governance framework; companion Governance Framework v1.0 published simultaneously; manifest error override added; staleness field substitution documented |

---

*Published under Creative Commons Attribution 4.0 International (CC BY 4.0).*  
*Code implementing this methodology is published under the MIT License.*  
*For governance, legal, and institutional provisions, see the companion CCIR Governance Framework v1.0.*
