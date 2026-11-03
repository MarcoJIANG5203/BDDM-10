# C/E Review Items and Day-One Progress

Prepared 2026-11-03. No teammate message was sent. These are local review materials.

## Completed by the automated A work

All public training files were obtained from the official source. The candidate cohort, exclusions, label audit fields, missingness tables, and deterministic split manifest were generated from actual records. There are 16206 eligible A records (78 positives) and 14840 eligible B records (40 positives) under candidate v2. No training or main-method results are included.

## Review and decisions still required

| Owner | Review item | Current state |
| --- | --- | --- |
| E | Supply the missing unified experiment specification and technical handover agreement | Not found in the supplied plan's directory or scoped project search |
| C | Independently verify labels, hour-axis convention, onset +6, first-row positives, and sample audit records | Pending human review; automated boundary checks passed |
| C and E | Confirm the (12,24] hourly-onset proxy target and the last-observed-ICULOS >=24 rule for both classes | Candidate implemented; not signed off |
| C and E | Resolve loss of known positives under complete24h follow-up and assess calibration/test positive counts | Mandatory feasibility decision before main-study rule freezing; see reports/endpoint_feasibility.csv |
| E | Confirm adult filter, last-observed aggregation, selected 37-column table and train-only all-missing-column policy | Candidate implemented; not signed off |
| E | Confirm A development / B external, 60/20/20 split, seed and tuning within train | Candidate manifest saved; not signed off |
| A and B | Confirm the reader joins by record_id and respects missing-value and fit boundaries | Handover prepared; B integration not executed |

If a rule changes, preserve the previous version, create a new version, regenerate the cohort/split and rerun all affected downstream experiments. Do not manually edit outcomes or move individual records.

## Local automated and source checks

- All clinical bytes matched official S3 size / single-part ETag MD5. Local SHA-256 hashes were also recorded. The official root SHA256SUMS covers license/utility diagrams, not the clinical files; no official published clinical SHA-256 is claimed.
- Fifteen synthetic tests cover shifted-label boundaries, early/left-censored onset, 24-hour follow-up, gaps in the time axis and delayed-start records, nonadult exclusion, missingness, nonmonotone labels and future-predictor leakage.
- Twelve full-cohort invariants passed. These are software checks, not institutional or clinical adjudication.
- A separate audit rechecked all 40,336 archived files, independently recomputed predictors/labels/masks/counts for 64 selected cohort records, and independently recomputed every split assignment. See reports/independent_package_checks.json.
- A separate native agent read the source code and tests and reported no actionable implementation/leakage error under the stated protocol. It did not execute a second full pipeline run. No cross-model validation or human sign-off is claimed.
- Dataset 2019 and article 2020 were checked separately. Source record and bibliography are included. A Retraction Watch database screen and final conference reference-format audit were not performed.

## English daily update ready to copy

2026-11-03 | A | Completed official acquisition of 40,336 public ICU record files, file-integrity checks, candidate cohort preparation, exclusion counts, missingness summaries and deterministic split manifest. Candidate eligible cohort: A=16206 (78 positive), B=14840 (40 positive). | Files: T1_A_Day1_2026-11-03/00_START_HERE.md; data/; reports/; sources/. | Open issues: the referenced group specifications are unavailable; C label review and E confirmation of candidate protocol choices are pending. | Next: incorporate confirmed rules, version any changes, and connect the data interface with B toward the 6 November end-to-end milestone.
