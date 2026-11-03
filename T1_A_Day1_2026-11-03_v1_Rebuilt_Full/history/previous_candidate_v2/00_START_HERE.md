# T1 — A Day-One Data Handover

Date: 3 November 2026 (Hong Kong / Beijing time, UTC+08:00). Deliverable language: English.

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run (data acquisition and cohort preparation)
- Origin Date: 2026-11-03
- Verification Status: UNVERIFIED
- Version Label: T1_A_day1_candidate_v2

The ARS status above means that an independent full reproducibility re-run has not been completed. Actual downloads, numerical checks and synthetic edge-case tests are documented below; this status is not a claim that the raw source is unknown.

## What has actually been completed

- Downloaded **all 40,336 public records** directly from the official PhysioNet Open S3 bucket documented on the [versioned dataset page](https://physionet.org/content/challenge-2019/1.0.0/).
- Verified every clinical file against its official S3 object size and single-part ETag/MD5. Recorded a local SHA-256 for every file. Preserved original file bytes inside local ZIP containers.
- Built the eligibility audit, patient-level candidate cohort, 37-column input matrix, missing-value mask, observation counts, and reproducible split manifest.
- Calculated actual exclusions, target positives/negatives, hourly missingness, and aggregate-feature missingness.
- Tested 15 clinically relevant boundary/leakage cases; checked 12 full-cohort invariants. Saved source metadata, license, English accepted manuscript, and citations with the dataset/article years separated.

## Actual counts under candidate protocol v2

| scope | n_records | positive | negative | positive_fraction |
| --- | --- | --- | --- | --- |
| site_A | 16206 | 78 | 16128 | 0.004813 |
| site_B | 14840 | 40 | 14800 | 0.002695 |
| train | 9722 | 46 | 9676 | 0.004732 |
| calibration | 3240 | 15 | 3225 | 0.004630 |
| internal_test | 3244 | 17 | 3227 | 0.005240 |
| external_test | 14840 | 40 | 14800 | 0.002695 |

Positive fraction is positive / n_records. These are derived study counts, not numbers copied from the source-release description.

The source release contains A=20,336 and B=20,000 files. The numbers with any positive label anywhere in the full record are A=1790 and B=1142. Those whole-record counts are **not** the 12–24-hour target counts.

## Open these files in order

1. [01_PROTOCOL_AND_RESULTS.md](01_PROTOCOL_AND_RESULTS.md): exact candidate rules, exclusions, counts, and limitations.
2. [02_HANDOVER_TO_B.md](02_HANDOVER_TO_B.md): data files, safe input columns, and reproducible commands.
3. [03_C_E_REVIEW_AND_DAILY_UPDATE.md](03_C_E_REVIEW_AND_DAILY_UPDATE.md): review items, unresolved group decisions, and an English progress update.
4. [sources/SOURCE_REGISTER.md](sources/SOURCE_REGISTER.md): authoritative English sources, years, evidence scope and access notes.
5. [data/raw_field_dictionary.csv](data/raw_field_dictionary.csv) and [data/derived_field_dictionary.csv](data/derived_field_dictionary.csv): field meanings.

## What remains a group decision

The two group documents referenced in the supplied execution plan were not present in its directory. To keep work moving, this package implements a **candidate** definition and split, saved in [protocol_candidate_v2.json](protocol_candidate_v2.json). C has not signed off the labels; E has not confirmed the added study choices. No sign-off or message to teammates has been fabricated or sent.

The deliverable is ready for review and B's interface development. Formal rule freezing awaits C/E confirmation. Model training and the multiple-imputation/conformal/rejection experiments are later milestones and have not been run as part of today's data preparation.

**Material feasibility finding:** the candidate complete-24-hour rule retains only 78 A positives and 40 B positives. Review reports/endpoint_feasibility.csv before freezing the task. Main-study feasibility and precision are not established by the total record count.
