## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-11-03, Beijing time (UTC+08:00)
- Verification Status: VERIFIED for A raw-to-cohort technical checks; ANALYZED for B's supplied trial summaries
- Version Label: A-001-review-20261103-r1
- Data Version: a-clinical-protocol-v1-20261103-full-r1
- Authority: AI-assisted work prepared for A; no personal owner signature, C acceptance, clinical adjudication, or E freeze is asserted.

## Conclusion and scope

The supplied full A delivery is technically consistent with the supplied protocol-v1 contract and B branch snapshot. Recalculation from all 40,336 raw files found no discrepancy in cohort membership, sequential exclusion reasons, the 24,095 included labels, or 867,420 feature cells, with missing values compared explicitly. This establishes agreement with the specified transformation, not independent correctness of the source clinical diagnoses.

No data rebuild is justified by a discovered implementation defect in this audit. The prespecified event-count gates remain unmet. The current data, labels, splits, original manifests, and B trial must be retained. Decisions about a new endpoint, eligibility rule, or formal freeze belong to the team and must acknowledge that internal and external trial results have already been inspected.

The full A archive was used, including raw records and historical provenance. This review is an additive verification delivery; it does not replace the full dataset with a reduced edition.

## Inputs and provenance

| Input | Identity |
|---|---|
| Supplied A ZIP | T1_A_Day1_2026-11-03_v1_Rebuilt_Full.zip; 50,674,324 bytes |
| A ZIP SHA256 | a57d16dc5432b2e2518bc5f754b706c60de7b94d3fb496870687d4a564770cb1 |
| Supplied B ZIP | BDDM-10-b-core-methods-experiments.zip; 37,327,148 bytes |
| B ZIP SHA256 | 6ce44807b8b697b0a4b95e3902d27b31002806196bf1cd573ddf1a65829cd779 |
| B ZIP embedded commit comment | 54f8342cb8a8d0c6653ae35aefa3ea57da4e26a9 |
| A source commit recorded by B | ec8fd750cc17038bb0a73c37e1537a1e7a4d780e |
| B candidate run | 20261103T122334_93a9a266 |

The B ZIP comment is observed archive metadata, not a new authenticated Git fetch. The source A commit is B's recorded provenance. Exact A input hashes were compared with B's supplied run manifest. No assertion is made that the remote branch has remained unchanged since these ZIPs were downloaded.

Evidence: [machine-readable audit](../reviews/A_001_verification_2026-11-03.json), [population flow](../reviews/A_001_population_flow_2026-11-03.csv), [execution receipts](../reviews/A_001_execution_receipts_2026-11-03.json), and [read-only audit script](../scripts/verify_a001_delivery.py).

## Protocol and extraction verification

1. Each raw file has the expected 41-column schema. Hours are finite positive integers, strictly contiguous and nonduplicate; labels are binary and monotone. Every included record contains actual ICULOS hours 1 through 24.
2. The independent audit derives onset only from an observed 0-to-1 transition: actual first-positive ICU hour plus six. A first-observation-positive record retains unknown exact onset. Neither row numbering nor the shifted positive label itself is substituted for the onset.
3. The target is exactly `12 < onset <= 24`. Inputs use only the latest observed value at actual ICU hour <=12. All 36 inputs, including Age and Gender, are checked; missing values remain missing. No future measurement, site, ID, ICULOS, Unit1/2, HospAdmTime, or label becomes a predictor.
4. The written v1 specifies no additional adult-only filter. Missing Age/Gender is allowed. The current implementation follows these choices rather than adding eligibility criteria.
5. All five seed files match the declared deterministic split algorithm exactly. Roles are disjoint, exhaustive, and nonempty; A is split 60/10/15/15 within outcome class and B is entirely external. Train and selection each contain both classes.
6. B's supplied current reader was invoked for seeds 2026–2030 with both CSV and Parquet: ten calls passed. The two input formats match exactly using round-trip CSV parsing for the independent content comparison.
7. Six independently specified boundary cases cover onset 12/13/24/25, no positive label, and left-censored first positivity; included cases additionally check future-value exclusion and retained NaN. A's original 15 boundary/split tests also passed separately.
8. Twenty retained actual review files (10 positive, 10 negative; balanced across sites) match their original raw ZIP entries and their cohort labels/features. This is automated verification of review materials, not C's independent human reading.

## Population flow and event loss

Counts below were independently recomputed from raw files. `Observed target onset` refers to a recoverable onset in `(12,24]`, even for records that fail eligibility; such excluded records are not proposed as additional cohort members.

| Site | Sequential population | Records | Any observed positive label | Observed target onset |
|---|---|---:|---:|---:|
| A | Raw | 20,336 | 1,790 | 334 |
| A | Starts at actual ICU hour 1 | 12,839 | 1,216 | 241 |
| A | Full hours 1–24 / final included | 10,174 | 730 | 57 |
| B | Raw | 20,000 | 1,142 | 152 |
| B | Starts at actual ICU hour 1 | 18,704 | 1,059 | 143 |
| B | Full hours 1–24 / final included | 13,921 | 638 | 38 |

The mutually exclusive exclusion counts are 8,793 missing-initial-hour records (A 7,497/B 1,296), followed by 7,448 insufficient-follow-up records (A 2,665/B 4,783). Total excluded is 16,241. Later sequential exclusion categories are zero because those patients have already failed earlier rules. Across all raw records, the overlapping diagnostics nevertheless find 283 observed onsets at or before12 and 426 first-record-positive cases. These overlapping counts must not be added to the sequential flow.

Among included patients, 1,368 have an observed positive label at some time, but 1,273 have recoverable onset after 24 (A 673/B 600). Only95 lie in the target interval (A 57/B 38). An eventual positive label is therefore not interchangeable with the prespecified landmark outcome. Reclassifying after 24 events as positive would change the endpoint.

These are descriptive eligibility and timing facts. They do not identify a causal mechanism for B's weak discrimination or instability. Complete24-hour follow-up selects a restricted population, and results must not be generalized to all ICU admissions.

## Fixed split and precision review

| Role, seed 2026 | Patients | Positive | Negative |
|---|---:|---:|---:|
| A train | 6,104 | 34 | 6,070 |
| A selection | 1,018 | 6 | 1,012 |
| A calibration | 1,527 | 9 | 1,518 |
| A internal test | 1,525 | 8 | 1,517 |
| B external | 13,921 | 38 | 13,883 |

All five seeds have these class counts with different assigned A patients. A 57 and B 38 each fail the 200-positive gate; internal test 8 fails the 50-positive gate in every seed. Repeating the same patients over seeds or imputation batches does not create independent positive events. No significance or clinical safety claim follows from passing interface or hash checks.

## Relationship to B's trial

The supplied trial manifest's data, audit, and seed 2026 hashes match this A package. All 13 recorded scientific/runner source hashes match the supplied B snapshot. Available small trial artifacts were checked against their recorded hashes; the exact count is in the machine-readable audit.

B reports MI positive-class set coverage 0/8 internally and 0/38 externally, selection errors 6, and unavailable B5/B6. Its numerical threshold statement is algebraically consistent: `q=0.010980572824885326` implies inclusion of class 1 only if `p >= 0.9890194271751147`; `ceil((1527+1)*0.9)=1376`. This does not independently validate saved patient probabilities or all bootstrap intervals.

The original B clinical run/Release was not supplied in the two ZIPs. This A audit does not claim a fresh patient-level replay of B's 120 metrics, 12 bootstrap intervals, model, or five-batch stability. Those remain B-reported evidence for C to independently check. The formal five-seed/five-scenario experiment is not complete merely because this candidate was run.

## Statistical fallacy scan

Coverage: 11/11 categories considered within this A verification and the supplied B summaries. This is bounded review coverage, not proof that all possible biases have been excluded.

| Category | Finding / limitation |
|---|---|
| Simpson's paradox | Hospitals retained separately; B main effect directions differ across S0/S4. No pooled advantage claimed; other subgroup reversals not exhaustively evaluated. |
| Ecological fallacy | Aggregate source/eligibility counts do not establish an individual patient's clinical cause or safety. |
| Berkson's paradox | ICU and complete-follow-up eligibility restrict sampling; external population claims remain limited. |
| Collider bias | No causal adjustment analysis performed; conditioning on future24-hour follow-up could induce selection and is not ruled out by this audit. |
| Base-rate neglect | Class counts and zero positive coverage must accompany overall coverage; overall coverage cannot establish positive-class protection. |
| Regression to the mean | No pre/post intervention effect evaluated. Changing the task after viewing a poor trial would require separate assessment. |
| Survivorship bias | Full 24-hour availability is a selection condition; excluded cases and event counts are explicitly retained in the audit. |
| Look-elsewhere effect | This audit selects no favorable seed, batch, or capacity; multiple B exploratory comparisons are not confirmatory evidence. |
| Garden of forking paths | v1 remains unchanged. Any redesign must disclose that internal/external outcomes were viewed and preserve old results. |
| Correlation versus causation | Observed timing loss, clipping, score correlation, and instability are descriptive; no clinical causal explanation established. |
| Reverse causality | Input cutoff is verified at 12. Source diagnoses and treatment pathways are not clinically adjudicated; causal temporal interpretation remains outside scope. |

## Required next actions

- A: review this technical record and explicitly provide personal owner confirmation if appropriate. The present report is completed automated work, not an invented signature.
- C: independently read the 20 actual raw cases and boundary rules, record findings and corrections, then independently audit B's original results as requested by C-001/C-003.
- E with A/B/C: record a written precision/task/freeze decision. If v1 is retained, state the limited-event and zero-positive-coverage boundaries. If a new protocol is chosen, record the reason and prior result exposure, increment the version, then rebuild and independently review; do not silently relabel or re-split v1.
- A/E: attach the [source-provenance correction](../docs/A_001_source_provenance_correction_EN.md). The archive's CC BY-only description is incomplete because its preserved LICENSE.txt is ODbL while the landing page states CC BY 4.0. Preserve both observations before selecting formal redistribution metadata.
- Publish/register an official data Release only after the outstanding decisions. This run prepares files locally and does not change the remote PR, registry publication state, or frozen data status.

## Primary sources

Dataset identity, counts, schema and six-hour label definition were checked at [PhysioNet v1.0.0](https://physionet.org/content/challenge-2019/1.0.0/) on 2026-11-03. The dataset publication is 2019-08-05, DOI 10.13026/v64v-d857. The companion journal issue is 2020 Feb;48(2):210–217, DOI 10.1097/CCM.0000000000004145, verified at [PubMed](https://pubmed.ncbi.nlm.nih.gov/31939789/). The original source labels are not independently clinically adjudicated by this audit.
