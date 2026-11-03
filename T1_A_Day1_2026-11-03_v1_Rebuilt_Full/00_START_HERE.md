# T1 A Day-One — Full Protocol-v1 Rebuild

Prepared3 November2026. Full scientific data version: a-clinical-protocol-v1-20261103-full-r1.

This edition was rebuilt from the original complete T1_A_Day1_2026-11-03 folder, not from the smaller GitHub upload edition. Both original raw archives, every official source asset, full acquisition inventories and per-record checksums remain included. The original folder was not modified. Previous candidate data, old37-input masks, old splits, reports and code are preserved in history/previous_candidate_v2 and must not be used as current formal-v1 data.

## Current formal-v1 delivery

- data/processed/cohort.parquet and cohort.csv: one record per string patient_id, site, y_true and36 ordered predictors. No HospAdmTime.
- data/processed/cohort_audit.json: real exclusions/counts, source/code hashes, data version, full-hour policy and pending reviews.
- splits/seed_2026.json through seed_2030.json: A stratified60/10/15/15 train/selection/calibration/test; all B external.
- data/processed/record_audit.csv and excluded_records.csv: all original records and sequential decisions.
- data/processed/review_10_positive_10_negative.csv and review_cases/:20 true source examples, source bytes and checksums for C review.
- data/diagnostics/:36-feature missing masks and34-feature hourly observation counts. These are auxiliary; B generates its own36 indicators.
- reports/: updated cohort flow, five-seed counts, missingness, replay and original-full-preservation evidence.
- raw/: all40,336 original clinical files in the unchanged two local ZIP containers.
- sources/: complete English official research sources, license, citation-year verification, inventories and checksum evidence. sources/protocol_snapshot preserves the group's original normative documents byte for byte in their original language.

## Verified result and open gates

Actual current cohort: A10,174 records/57 positives; B13,921 records/38 positives; total24,095. Main-seed internal test has1,525 records/8 positives.

The full-edition B loader passes10 invocations (5seeds x Parquet/CSV). Fifteen A boundary/split tests pass in this edition. The underlying full repository suite previously passed47 tests. A full standalone rebuild produces32 identical generated data/split/audit hashes. Every meaningful original full-package file has been checked for exact preservation at its current or historical path.

**Interface and computational checks PASS. The protocol's precision gates FAIL (each site needs200 positives; internal test needs50). C's independent human review and E's precision/freeze decision remain PENDING. No approved final clinical dataset, trained model result or scientific acceptance is claimed.**

## Reproduce from this full directory

Use an environment with requirements-lock.txt dependencies installed. The full archive contains all needed raw inputs and the normative source snapshot; no new clinical-data download or Git checkout is required:

```powershell
python code/prepare_day1.py
python code/build_full_reports.py
python scripts/verify_a_handover_v1.py
python -m pytest -q tests/test_a_cohort_v1.py
```

All current commands use actual ICU hours1--24 for eligibility and only hours1--12 for predictors. Never run historical code against current data. Current key columns and B interface details are in02_HANDOVER_TO_B.md. The scientific definitions and remaining limits are in01_PROTOCOL_AND_RESULTS.md. C's unfilled review form is03_C_E_REVIEW_AND_DAILY_UPDATE.md.

This complete package is a local deliverable; it has not been uploaded to GitHub or published as a Release. It preserves the previously reported precision issue rather than inventing patients to satisfy a threshold.
