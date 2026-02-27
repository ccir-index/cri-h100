# CCIR Governance Framework v1.0
## Compute Credit Index Research — CRI-H100 Governance and Legal Framework

**Version:** 1.0  
**Effective Date:** April 2026  
**Published by:** CCIR — Compute Credit Index Research  
**Repository:** https://github.com/ccir-index/ccir-methodology  
**Companion document:** CCIR Methodology v1.1.0  
**Contact:** research@ccir.io  
**Governance standard:** Designed with reference to the IOSCO Principles for Financial Benchmarks (July 2013)

---

## Table of Contents

1. [Definitions](#1-definitions)
2. [Administrator and Calculation Agent Framework](#2-administrator-and-calculation-agent-framework)
3. [Conflict of Interest Policy](#3-conflict-of-interest-policy)
4. [Governance Structure](#4-governance-structure)
5. [Change Control](#5-change-control)
6. [Restatements](#6-restatements)
7. [Fallback and Benchmark Replacement](#7-fallback-and-benchmark-replacement)
8. [Administrative Discretion](#8-administrative-discretion)
9. [Data Collection and Third Party Oversight](#9-data-collection-and-third-party-oversight)
10. [Operational Resilience and Business Continuity](#10-operational-resilience-and-business-continuity)
11. [Audit and Independent Review](#11-audit-and-independent-review)
12. [Complaints Procedure](#12-complaints-procedure)
13. [Regulatory Cooperation](#13-regulatory-cooperation)
14. [Intellectual Property and Licensing](#14-intellectual-property-and-licensing)
15. [Rating Agency Disclosure Statement](#15-rating-agency-disclosure-statement)
16. [Disclaimer](#16-disclaimer)
17. [Appendix A — Suggested Legal Citation Language](#appendix-a--suggested-legal-citation-language)
18. [Appendix B — Version History](#appendix-b--version-history)
19. [Appendix C — IOSCO Principles Alignment Summary](#appendix-c--iosco-principles-alignment-summary)

---

## 1. Definitions

The following terms have the meanings set forth below. Defined terms are capitalized throughout for interpretive consistency. Technical terms specific to the index calculation (Observation, Qualifying Listing, Calculation Window, Low Confidence Value, SHA-256 Hash) are defined in the CCIR Methodology v1.1.0.

**"Administrator"** means CCIR — Compute Credit Index Research, the entity responsible for governance, oversight, and publication of the Index.

**"Calculation Agent"** means the function responsible for mechanical computation of the Index in accordance with the CCIR Methodology, whether performed internally by the Administrator or delegated to a third party pursuant to Section 2.2.

**"Index"** means CRI-H100, as defined in CCIR Methodology v1.1.0.

**"Material Methodology Change"** has the meaning set forth in Section 5.2.

**"Restatement"** means a correction to a previously published Index value pursuant to Section 6.

**"Fallback Value"** means a value determined pursuant to the fallback waterfall in Section 7.

**"Publication Date"** means each Thursday on which the Index is scheduled to be published.

**"Business Day"** means any weekday other than a U.S. federal holiday.

**"Low Confidence Value"** means an Index value published with an automatic low confidence flag as defined in CCIR Methodology v1.1.0, Section 10.

**"Primary Data Source"** means, as of this version, the Vast.ai GPU rental marketplace API, as described in Section 9.

**"Annual Benchmark Review"** means the annual assessment described in Section 4.3.

---

## 2. Administrator and Calculation Agent Framework

### 2.1 Administrator Responsibilities

The Administrator is responsible for:

- Maintaining and publishing the CCIR Methodology and this Governance Framework
- Governance oversight and version control of all CCIR documents
- Publication of Index values on each Publication Date
- Maintaining the audit trail and archival data
- Disclosing conflicts of interest and Material Methodology Changes
- Oversight of data collection and third party data sources (Section 9)
- Commissioning independent review as appropriate
- Compliance with the provisions of this Governance Framework

The Administrator does not exercise discretion in routine Index calculation. All routine computation is governed by the mechanical rules in the CCIR Methodology.

### 2.2 Calculation Agent Function

The Calculation Agent applies the mechanical rules set forth in the CCIR Methodology. The Calculation Agent:

- Has no authority to override filters, data inclusion rules, or statistical procedures except as provided in Section 8
- Must document and log any technical failure or exception
- Must escalate any non-routine determination to the Administrator for review

If the Calculation Agent function is delegated to a third party, the delegation must be documented, the delegate must be subject to oversight controls, and the delegation must be publicly disclosed.

### 2.3 Separation of Functions

The Administrator and Calculation Agent functions shall be operationally separated to the extent practicable. Routine calculation shall not be subject to discretionary override by any person with a financial interest in the Index value.

### 2.4 Data Input Design

CRI-H100 is calculated exclusively from publicly available data obtained through automated collection from the Primary Data Source. No submissions from market participants are solicited or accepted. This design eliminates the category of conflicts of interest inherent in submission-based benchmarks — the governance challenge that prompted the IOSCO Principles for Financial Benchmarks following the LIBOR manipulation scandal.

The data input hierarchy for routine Index determination is:

1. **Automated API collection** per the published Methodology (no discretion exercised)
2. **Manifest Error Override** by the Administrator under Section 8.2 (discretion exercised, documented, and disclosed)
3. **Fallback provisions** per Section 7 (triggered by data unavailability, not discretion)

Expert judgement is not applied in routine Index determination. The only circumstance in which the Administrator exercises discretion over data inputs is the Manifest Error Override, which is subject to the documentation and disclosure requirements of Section 8.3.

---

## 3. Conflict of Interest Policy

### 3.1 Independence Commitment

The Administrator maintains policies designed to preserve the independence and integrity of the Index, including:

- Separation between governance and any commercial activities that could benefit from a particular Index value
- Disclosure of material economic interests in GPU rental markets, GPU hardware markets, or GPU-backed financial instruments
- Recusal procedures for board members or personnel with conflicts

### 3.2 Prohibited Conduct

The Administrator shall not:

- Trade GPU rental contracts or GPU-backed financial instruments based on non-public Index data
- Alter Index methodology or calculation to benefit any single market participant
- Suppress a published value due to anticipated market impact
- Accept payment from any party in exchange for favorable treatment in the Index calculation

### 3.3 Structural Disclosure

CCIR derives commercial benefit from Index adoption through advisory services, administrator services, and pre-transaction audit coordination as described in Section 14. This creates an indirect interest in the Index being cited in credit documents, though not in any particular Index value or direction. This structural interest is managed by: (a) the open-methodology commitment, which permits any party to independently verify any published value; (b) the prohibition on discretionary override by any person with a financial interest; (c) the Oversight Board's independence from commercial operations (once constituted); and (d) the rules-based calculation design, which removes discretion from routine Index determination.

### 3.4 Disclosure

All Material Methodology Changes shall be publicly disclosed with effective date, rationale, and a description of expected impact on Index values before taking effect. Conflict of interest disclosures shall be maintained and made available upon request.

---

## 4. Governance Structure

### 4.1 Administrator

CCIR serves as Administrator. The Administrator is responsible for maintaining the Index in accordance with the CCIR Methodology and the provisions of this Governance Framework.

### 4.2 Oversight Board

CCIR intends to establish an independent Oversight Board consisting of three (3) to five (5) members drawn from the structured finance, credit, technology, and legal sectors. The Board shall:

- Conduct annual methodology review
- Approve Material Methodology Changes
- Review conflict of interest disclosures
- Review audit summaries
- Provide oversight of the Administrator's compliance with this Governance Framework

Board members shall not participate in routine Index calculation or commercial operations of CCIR. The governance charter and Board composition will be published at ccir.io when constituted. CCIR commits to establishing the Board within twelve (12) months of the first Index publication.

Pending constitution of the Oversight Board, CCIR will seek to appoint one or two external advisors with relevant structured finance, credit, or technology expertise to provide interim oversight challenge on methodology decisions. The names and qualifications of interim advisors will be published at ccir.io.

### 4.3 Annual Benchmark Review

At least once per calendar year, the Administrator shall conduct and publish an Annual Benchmark Review assessing:

**Data sufficiency:**
- Daily and weekly Observation count trends (growing, stable, declining)
- Coverage ratio (Qualifying Listings as percentage of total H100 SXM listings)
- Confidence interval widths and their trend over time
- A formal determination of whether data sufficiency supports the Index's current use cases (informational reference, covenant trigger, ABS waterfall reference)

**Market representativeness:**
- Price comparison with non-Vast.ai sources where available
- Assessment of whether the Primary Data Source continues to reflect the on-demand secondary marketplace
- Identification of structural market changes that may affect Index design

**Data source viability:**
- Continued availability and reliability of the Vast.ai API
- Assessment of any changes to Vast.ai's listing practices, terms of service, or market position
- Evaluation of candidate supplementary data sources

**Governance compliance:**
- Summary of Material Methodology Changes and Non-Material Changes during the review period
- Summary of Manifest Error Overrides and Restatements
- Summary of complaints received and resolved (Section 12)
- Conflict of interest review

The Annual Benchmark Review shall be published at ccir.io and in the GitHub repository. A draft of findings shall be made available for stakeholder comment for a period of not less than fourteen (14) calendar days before finalization.

---

## 5. Change Control

### 5.1 Methodology Versioning

CCIR Methodology documents follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** version changes indicate Material Methodology Changes that may cause the Index value to differ from prior versions
- **MINOR** version changes indicate additions or clarifications that do not materially affect Index values
- **PATCH** version changes indicate corrections of errors or ambiguities without changing the calculation

### 5.2 Material Methodology Changes

The following constitute Material Methodology Changes requiring a MAJOR version increment and sixty (60) calendar days' advance public notice:

- Changes to the index calculation method (e.g., mean replacing median)
- Changes to the primary data source or the addition of new data sources
- Changes to the geographic scope of the Index
- Changes to quality filter thresholds
- Changes to the outlier removal methodology
- Changes to the publication window, frequency, or schedule
- Changes to the fallback or benchmark replacement waterfall

### 5.3 Non-Material Changes

The following constitute non-material changes requiring fourteen (14) calendar days' advance notice and a MINOR or PATCH version increment:

- Clarifications to existing methodology language that do not change the calculation
- Addition of new known limitations
- Updates to contact information or publication locations
- Bug fixes in calculation code that do not affect Index values
- Updates to this Governance Framework that do not affect index calculation

### 5.4 Change Process

All proposed changes will be:

1. Published as a draft in the GitHub repository with a public comment period of not less than the applicable notice period
2. Announced to registered users via research@ccir.io
3. Subject to a stakeholder consultation period of not less than thirty (30) calendar days for Material Methodology Changes, during which written comments will be accepted via research@ccir.io and the GitHub repository. CCIR will publish a summary of comments received and the Administrator's response to substantive comments.
4. Approved by the Oversight Board for Material Methodology Changes (once the Board is constituted)
5. Effective only after the applicable notice period has elapsed

---

## 6. Restatements

### 6.1 Restatement Conditions

A published Index value may be restated only if:

- A material data error is discovered, such as a corrupted data file producing a hash mismatch
- A calculation error inconsistent with the published Methodology is identified

### 6.2 Restatement Process

Any Restatement will be published with:

- The original published value
- The restated value
- The date the error was discovered
- The reason for restatement
- The date of restatement

Restatements will be announced via the CCIR GitHub repository and research@ccir.io.

### 6.3 Restatement Limitation

No Restatement shall be made more than ninety (90) calendar days after the original Publication Date except in cases of fraud or data corruption affecting the integrity of the historical record.

---

## 7. Fallback and Benchmark Replacement

### 7.1 Missed Publication — Operational Waterfall

If CRI-H100 is not published on a scheduled Publication Date due to operational failure, the following waterfall applies:

**Level 1 — Delayed publication**  
CCIR will publish the Index as soon as practicable following the disruption, with a note explaining the delay. A delayed publication within five (5) Business Days of the scheduled date is treated as the scheduled Publication Date for all purposes.

**Level 2 — Prior value**  
If publication is delayed beyond five (5) Business Days, the most recently published non-flagged CRI-H100 value may be used as the Fallback Value for the missed period.

**Level 3 — Interpolation**  
If two successive weekly publications are missed, parties may agree to interpolate linearly between the last published value and the next published value when publication resumes.

**Level 4 — Benchmark replacement**  
If CRI-H100 is unavailable for more than thirty (30) consecutive calendar days, the benchmark replacement waterfall in Section 7.2 applies.

### 7.2 Benchmark Replacement Waterfall

The following waterfall is designed for inclusion in indentures and credit agreements. It applies if CRI-H100 is permanently discontinued or has been unavailable for more than thirty (30) consecutive calendar days:

**Step 1 — Successor Index**  
Any successor index published by CCIR using a substantially similar methodology. CCIR will designate a Successor Index in any discontinuation notice provided pursuant to Section 10.4.

**Step 2 — Comparable Public Marketplace Index**  
A publicly reproducible GPU rental price index published by an independent third party meeting transparency and reproducibility standards substantially similar to those of CRI-H100.

**Step 3 — Independent Determination**  
An index value determined by an independent third-party calculation agent using publicly reproducible listing data from one or more GPU rental marketplaces and a median methodology substantially similar to CRI-H100, as determined by the relevant trustee or calculation agent under the applicable transaction documents.

**Step 4 — Last Available Value**  
The most recently published non-flagged CRI-H100 value, used until a successor benchmark is identified or the transaction matures.

Replacement pursuant to Steps 2 through 4 shall not require the consent of noteholders unless explicitly required by the applicable transaction documents.

### 7.3 Low Confidence Values in Credit Documents

Users incorporating CRI-H100 into credit documents should consider specifying how Low Confidence Values are handled. Options include:

- Using the prior non-flagged value for the Low Confidence period
- Widening collateral haircut bands when the Index is flagged
- Treating a Low Confidence period exceeding a specified duration as triggering Level 2 of the operational waterfall

Suggested credit agreement language is provided in Appendix A.

### 7.4 Data Source Disruption

If the Vast.ai API is unavailable on a given collection day, that day is treated as missing in the Calculation Window. The Index may still be calculated from remaining days in the window. If the Vast.ai API is unavailable for the entire seven-day Calculation Window, the Low Confidence flag is set and Level 2 of the operational waterfall applies.

---

## 8. Administrative Discretion

### 8.1 Rules-Based Index

CRI-H100 is a rules-based Index. The Calculation Agent applies mechanical rules with no discretion in routine calculation.

### 8.2 Permitted Discretion

Discretion is permitted only in the following limited circumstances:

- Correction of a manifest computational error identified after publication
- Exclusion of an Observation under the manifest error override in CCIR Methodology v1.1.0, Section 7.3
- Technical data corruption rendering a daily snapshot unreliable
- Implementation of a Board-approved Material Methodology Change

### 8.3 Documentation Requirements

All exercises of discretion must be:

- Documented in writing at the time of exercise
- Recorded in the calculation audit trail
- Publicly disclosed if material to the published Index value
- Reviewed by the Administrator if exercised by the Calculation Agent

### 8.4 No Retroactive Alteration

No exercise of discretion shall retroactively alter a prior published Index value except as expressly permitted under the Restatement provisions of Section 6.

---

## 9. Data Collection and Third Party Oversight

### 9.1 Data Collection Process

Index data is collected through automated daily queries of the Primary Data Source (Vast.ai API) using the parameters and schedule specified in CCIR Methodology v1.1.0. The collection process operates without manual intervention in routine operation.

### 9.2 Internal Controls over Data Collection

The following controls are applied to the data collection and calculation process:

**Collection integrity:**
- Each daily snapshot is timestamped and hashed (SHA-256) at the time of collection
- The hash is committed to the public GitHub repository, creating a tamper-evident record
- Raw data files are archived in append-only storage

**Automated validation:**
- The collection pipeline validates API response structure and completeness before processing
- Quality filters and outlier removal are applied programmatically per the published Methodology
- The pipeline logs all filter exclusions with reasons

**Error handling:**
- API failures are logged with timestamps and error codes
- Partial data collection (fewer collection days than expected in the Calculation Window) triggers the Low Confidence flag
- Complete data source unavailability triggers the fallback provisions of Section 7.4

**Access controls:**
- The production data collection pipeline operates on dedicated infrastructure
- Configuration changes to the collection pipeline are version-controlled in the GitHub repository

### 9.3 Third Party Data Source Oversight

CRI-H100 depends on Vast.ai as the Primary Data Source. While Vast.ai is not a data submitter in the traditional benchmark sense (CCIR collects data from Vast.ai's public API without Vast.ai's direct involvement in the Index), disruption to or degradation of the Vast.ai platform could materially affect the Index. The Administrator monitors the Primary Data Source through:

**Operational monitoring:**
- Daily tracking of API availability and response consistency
- Monitoring of Observation counts for signs of market migration or platform changes
- Monitoring of the coverage ratio (Qualifying Listings as percentage of total listings)

**Change detection:**
- Monitoring of Vast.ai's terms of service, API documentation, and public communications for changes that could affect data collection or Index integrity
- Assessment of any changes to Vast.ai's listing practices, fee structure, or provider qualification requirements

**Trigger events requiring Administrator assessment:**
- Vast.ai API unavailability exceeding 48 hours
- Observation counts declining below the minimum viable observation count (MVOC) for three consecutive weeks
- Changes to Vast.ai's terms of service that restrict or condition API access
- Evidence of coordinated listing behavior or artificial price patterns on the platform
- Vast.ai corporate events (acquisition, restructuring, discontinuation) that could affect platform continuity

The results of Third Party Data Source monitoring shall be included in the Annual Benchmark Review (Section 4.3).

---

## 10. Operational Resilience and Business Continuity

### 10.1 Data Retention

CCIR shall retain all data inputs, calculation records, audit trail documentation, governance records, and correspondence related to Index determinations for a minimum of five (5) years from the date of each Index publication. Specific retention practices include:

- Daily snapshots stored with SHA-256 Hash in append-only archival storage
- The GitHub repository serves as the primary public archive
- CCIR maintains redundant copies of all historical data in geographically separate locations

### 10.2 Business Continuity Plan

CCIR maintains a Business Continuity Plan addressing infrastructure outages, data source interruption, personnel unavailability, and cybersecurity incidents. In the event of any disruption, fallback procedures in Section 7 apply. CCIR will communicate the nature and expected duration of any disruption via research@ccir.io and the GitHub repository within two (2) Business Days of becoming aware of the disruption.

The open-source pipeline and public data source are designed so that any qualified party could continue Index production if the current Administrator were unavailable. The complete calculation code, methodology documentation, and historical data are publicly available in the GitHub repository. This design provides inherent business continuity beyond the Administrator's own operational resilience.

### 10.3 Force Majeure

CCIR shall not be liable for failure to publish due to events beyond reasonable control, including natural disasters, war, cyberattack, governmental action, or prolonged data source outage. Publication shall resume as soon as practicable. Force majeure events will be disclosed publicly.

### 10.4 Permanent Discontinuation

In the event CCIR determines to permanently discontinue CRI-H100, CCIR will:

- Provide a minimum of ninety (90) calendar days' notice via the GitHub repository and research@ccir.io
- Designate a Successor Index where possible
- Publish a final Index value on the scheduled discontinuation date
- Archive all historical data and methodology documents permanently in the GitHub repository
- Maintain research@ccir.io as a contact address for a minimum of two (2) years following discontinuation

---

## 11. Audit and Independent Review

### 11.1 Audit Trail

Each weekly Index publication includes a full calculation audit trail as specified in CCIR Methodology v1.1.0, Section 12. The audit trail is publicly accessible via the GitHub repository.

### 11.2 Independent Review

The Administrator may commission independent third-party review of calculation reproducibility, data integrity, and governance compliance. A summary of findings shall be published at ccir.io.

CCIR commits to commissioning an independent audit prior to the closing of any transaction that formally references CRI-H100 in its offering documents.

### 11.3 Annual Governance Review

The Oversight Board (once constituted) shall conduct an annual governance review covering methodology integrity, conflict of interest compliance, audit findings, and the Annual Benchmark Review described in Section 4.3.

### 11.4 Annual Independent Governance Audit

Beginning no later than twelve (12) months after the first Index publication, the Administrator shall commission an annual independent review of governance compliance. The review shall assess whether the Administrator has followed its published procedures, including the provisions of this Governance Framework and the CCIR Methodology. The scope, findings, and any remedial actions shall be summarized and published at ccir.io. This review is separate from the pre-transaction audit described in Section 11.2 and serves the ongoing governance assurance function.

---

## 12. Complaints Procedure

### 12.1 Scope

Any person may submit a complaint regarding the calculation, publication, governance, or methodology of the Index. Complaints may relate to suspected errors in published values, methodology concerns, conflicts of interest, data quality issues, or any other matter related to the Index.

### 12.2 Submission

Complaints shall be submitted in writing to research@ccir.io or as an issue on the CCIR GitHub repository. Complaints should include: the complainant's name and contact information (anonymous complaints will be accepted but may limit CCIR's ability to respond), the specific concern, any supporting evidence, and the remedy sought.

### 12.3 Acknowledgment and Investigation

CCIR will acknowledge receipt of a complaint within five (5) Business Days. The Administrator will evaluate the complaint and conduct such investigation as is warranted by the nature and substance of the concern. For complaints involving a specific published Index value, the investigation will include review of the relevant data snapshot, calculation audit trail, and methodology application.

### 12.4 Response

CCIR will provide a substantive written response to the complainant within thirty (30) Business Days of receipt. If the investigation requires additional time, CCIR will notify the complainant of the expected timeline. The response will include the Administrator's findings and any corrective action taken or planned.

### 12.5 Escalation

Complaints that the Administrator determines to be material — including complaints alleging systematic calculation errors, conflicts of interest, or methodology deficiencies — shall be escalated to the Oversight Board (once constituted) for independent review. The Board's determination shall be final.

### 12.6 Record Keeping

CCIR shall maintain a record of all complaints received, the investigation conducted, and the outcome, for a minimum of five (5) years. An anonymized summary of complaints received and their resolution shall be included in the Annual Benchmark Review (Section 4.3).

---

## 13. Regulatory Cooperation

CCIR will cooperate with relevant regulatory authorities upon request, including making available all data inputs, calculation records, audit trails, governance documentation, and correspondence related to Index determinations. CCIR's open-methodology design means that the majority of relevant information is already publicly accessible via the GitHub repository.

CCIR will respond to regulatory inquiries within ten (10) Business Days of receipt. Where a regulatory request requires production of non-public records, CCIR will comply to the extent required by applicable law and will notify affected parties where legally permitted.

CRI-H100 is not currently subject to benchmark regulation under the EU Benchmarks Regulation (BMR), the UK BMR, or equivalent regulatory frameworks. If CRI-H100 becomes subject to benchmark regulation in any jurisdiction, CCIR will take reasonable steps to comply with applicable requirements and will disclose its regulatory status in this Governance Framework.

---

## 14. Intellectual Property and Licensing

### 14.1 Ownership

All intellectual property rights in the Index, including the Index name, the CCIR Methodology, this Governance Framework, and historical Index data, are owned by CCIR — Compute Credit Index Research.

### 14.2 Permitted Use Without License

The following uses are explicitly permitted without requiring a commercial license from CCIR:

- Reference citation of CRI-H100 in loan agreements, indentures, credit documents, and legal instruments
- Academic citation and research use
- Independent reproduction of Index values using the open-source verification tools
- Journalistic and analytical reference

Reference citation in publicly offered or rated structured finance transactions requires advance written notification to CCIR at research@ccir.io to ensure timely completion of the pre-transaction audit commitment in Section 11.2. This notification requirement does not constitute a license fee or paywall; it is an operational coordination mechanism.

### 14.3 Uses Requiring License

The following uses require a commercial license from CCIR:

- Branded redistribution of Index data as a commercial data product
- Incorporation of CRI-H100 Index values or historical data into a commercial data platform, API, or aggregation service offered to third parties
- Creation of derivative financial products (e.g., swaps, forwards, structured notes, futures contracts) that formally reference CRI-H100 as a settlement benchmark
- White-labeling or sublicensing the Index under a different name

Licensing inquiries should be directed to research@ccir.io.

### 14.4 Open-Source Code and Documentation

The pipeline code implementing the Methodology is published under the MIT License at https://github.com/ccir-index/cri-h100. The Methodology document and this Governance Framework are published under Creative Commons Attribution 4.0 International (CC BY 4.0). These open licenses apply to the code and documentation, not to the Index data or the CCIR brand.

---

## 15. Rating Agency Disclosure Statement

This section is provided to assist rating agencies in evaluating CRI-H100 for use as a reference rate in rated structured finance transactions.

### 15.1 Index Characteristics

| Characteristic | Description |
|----------------|-------------|
| Index type | Price index (listed rates, not executed transactions) |
| Data source | Single public marketplace (Vast.ai, US) |
| Market depth | Thin (8–20 qualifying listings per day as of early 2026) |
| Calculation method | Trailing 7-day median $/GPU-hour |
| Outlier protection | Trimmed mean ± 2.5σ |
| Manipulation resistance | Median-based; append-only; public audit trail |
| Reproducibility | Fully open-source; independently verifiable by any third party |
| Governance | Rules-based; IOSCO-referenced; independent Oversight Board in formation |
| Audit | Annual independent governance audit committed; pre-transaction audit available on request |
| Complaints | Written complaints procedure with 30-Business Day response commitment |
| Regulatory cooperation | Committed to cooperate with regulatory authorities upon request |

### 15.2 Material Risk Disclosures for Rating Analysis

**Single-source concentration.** CRI-H100 relies on a single public marketplace. Disruption to that marketplace would trigger the fallback provisions in Section 7 but represents a data source concentration risk that rating agencies should consider. Third party data source oversight practices are described in Section 9.3.

**Listed vs. executed price basis.** The Index measures listed prices, not executed transaction prices. In a distressed collateral scenario, realized liquidation prices may differ materially from the CRI-H100 listed rate. Users should apply appropriate haircuts to CRI-H100 when modeling collateral liquidation values.

**Thin market.** Current Observation counts are low. CCIR applies and discloses the Low Confidence flag when counts fall below minimum thresholds. Rating agencies should monitor Observation counts as a measure of Index reliability over time. The Annual Benchmark Review (Section 4.3) includes a formal data sufficiency assessment.

**Performance variance.** The Index does not adjust for intra-model GPU performance variance. See CCIR Methodology v1.1.0, Section 11.3.

**Market immaturity.** The GPU rental market is evolving rapidly. The historical CRI-H100 price series is short. Rating agencies should apply conservative assumptions regarding rate stability and consider stress scenarios reflecting rapid market price movement.

### 15.3 Haircut Guidance

CCIR does not provide haircut recommendations, as appropriate haircuts depend on transaction-specific factors including loan-to-value ratios, collateral concentration, lender recourse provisions, and portfolio performance characteristics. CCIR recommends that rating agencies and lenders conduct independent collateral valuation analysis accounting for the limitations disclosed in the CCIR Methodology and this Section 15.

---

## 16. Disclaimer

CRI-H100 is published for informational and reference purposes. The Index does not constitute an offer, recommendation, or investment advice. No fiduciary relationship is created between CCIR and any market participant, trustee, issuer, or investor by reason of use of or reliance on the Index.

CCIR makes no representation that CRI-H100 reflects the price at which any particular GPU rental transaction could be executed, or the liquidation value of any GPU collateral portfolio.

CCIR uses commercially reasonable efforts to ensure the accuracy and completeness of CRI-H100 but does not warrant that the Index is free from errors, omissions, or interruptions. The Index may be volatile due to thin market conditions and concentration in the primary data source.

Users of CRI-H100 in credit documents, covenants, or valuation frameworks should conduct their own due diligence and obtain independent legal and financial advice. CCIR is not responsible for any loss or damage arising from reliance on CRI-H100.

The Index is provided "as is" without warranty of any kind, express or implied.

---

## Appendix A — Suggested Legal Citation Language

### A.1 Standard Reference Rate Definition

For use in credit agreements, indentures, and loan documents:

> "**Rental Rate Reference**" means, for any determination date, CRI-H100 as defined in CCIR Methodology v1.1.0, published by Compute Credit Index Research at https://github.com/ccir-index/ccir-methodology/blob/main/METHODOLOGY-v1.1.0.md, representing the trailing 7-day median $/GPU-hour for H100 SXM on-demand rental listings on the Vast.ai US marketplace, published weekly on Thursdays pursuant to the CCIR Governance Framework v1.0. If the Rental Rate Reference for any week is published as a Low Confidence Value, the Rental Rate Reference for such week shall be the most recently published non-Low Confidence CRI-H100 value.

### A.2 Fallback Language

> In the event that the Rental Rate Reference is not published on any scheduled Publication Date, the Rental Rate Reference for such period shall be determined pursuant to the fallback waterfall set forth in Section 7.1 of the CCIR Governance Framework v1.0. In the event that no CRI-H100 value has been published within the prior thirty (30) calendar days, the Rental Rate Reference shall be determined pursuant to the benchmark replacement waterfall set forth in Section 7.2 of the CCIR Governance Framework v1.0.

### A.3 Material Change Notification

> The Borrower shall notify the Lender within five (5) Business Days of receiving notice of any Material Methodology Change (as defined in the CCIR Governance Framework v1.0) affecting CRI-H100. If a Material Methodology Change results in a change to the Rental Rate Reference of more than [●]% relative to the prior methodology, the parties shall negotiate in good faith to agree an alternative Rental Rate Reference within thirty (30) days of the effective date of such change.

### A.4 Low Confidence Handling (Optional)

> Notwithstanding the foregoing, in the event that CRI-H100 is published as a Low Confidence Value for [●] or more consecutive weeks, the Rental Rate Reference shall be the most recently published non-Low Confidence CRI-H100 value until a non-Low Confidence value is next published.

---

## Appendix B — Version History

| Version | Effective Date | Change Type | Summary |
|---------|---------------|-------------|---------|
| 1.0 | April 2026 | Initial | First publication; establishes Administrator/Calculation Agent framework, governance structure, change control, fallback waterfall, data collection and third party oversight, complaints procedure, regulatory cooperation, IP and licensing, rating agency disclosure. Designed with reference to IOSCO Principles for Financial Benchmarks (2013). |

---

## Appendix C — IOSCO Principles Alignment Summary

This Governance Framework is designed with reference to the IOSCO Principles for Financial Benchmarks (July 2013). The following table summarizes the alignment of the Framework with each principle. A detailed self-assessment is available from CCIR upon request.

| Principle | Description | Primary Reference |
|-----------|-------------|-------------------|
| 1. Overall Responsibility | Administrator responsibility | §§1–2 |
| 2. Third Party Oversight | Oversight of data sources | §9.3 |
| 3. Conflicts of Interest | COI policies and disclosure | §3 |
| 4. Control Framework | Controls over determination process | §§2, 8, 9.2 |
| 5. Internal Oversight | Oversight function | §§4.2, 4.3, 11.3 |
| 6. Benchmark Design | Accurate representation of measured interest | CCIR Methodology §§5–6 |
| 7. Data Sufficiency | Adequate data for the benchmark | §4.3, CCIR Methodology §7.5 |
| 8. Hierarchy of Data Inputs | Prioritization of inputs | §2.4 |
| 9. Transparency of Determinations | Published procedures and error handling | §§6, 8, 9.2 |
| 10. Periodic Review | Review of underlying conditions | §4.3 |
| 11. Content of Methodology | Published methodology | CCIR Methodology v1.1.0 |
| 12. Changes to Methodology | Change procedures and consultation | §5 |
| 13. Transition | Cessation and replacement provisions | §§7, 10.4 |
| 14. Submitter Code of Conduct | Not applicable (no submissions) | §2.4 |
| 15. Internal Controls | Controls over data collection | §9.2 |
| 16. Complaints Procedures | Complaints handling | §12 |
| 17. Audits | Independent audit and review | §11 |
| 18. Audit Trail | Record retention | §§10.1, 11.1 |
| 19. Regulatory Cooperation | Cooperation with authorities | §13 |

---

*This document is published under Creative Commons Attribution 4.0 International (CC BY 4.0).*  
*For the technical index calculation specification, see the companion CCIR Methodology v1.1.0.*
