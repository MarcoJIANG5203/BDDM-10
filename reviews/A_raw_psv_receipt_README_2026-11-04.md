# A raw hourly-file receipt for C — 2026-11-04 (UTC+08:00)

## Delivered evidence

This is an automated A-owned receipt for unchanged protocol v1 and data version
`a-clinical-protocol-v1-20261103-full-r1`. A separate checker reads the two
immutable source ZIPs and does not import A's extractor, B's loader/model code,
or C's label implementation. It writes evidence outside the source package.

- `scripts/verify_a_raw_psv_receipt.py`: reusable checker with `--package` and
  `--output-root` arguments.
- `reviews/A_raw_psv_receipt_2026-11-04.json`: aggregate technical result.
- `reviews/A_raw_psv_receipt_2026-11-04.log`: actual successful execution log.
- `private_receipt/raw_psv_receipt.csv`: 40,336 per-record rows, including source
  filename, SHA256, first/last ICU hours, first positive-label hour, recovered
  onset or explicit censoring, sequential exclusion reason and eligible label.
  This file belongs in the locally prepared data bundle or ignored cache.
- `tests/test_a_raw_psv_receipt.py`: nine checks covering onset12/13/24/25,
  no positive label, left censoring, delayed start, future-feature exclusion,
  retained missingness and an unrepaired gap.
- `reviews/C_supplied_scripts_replay_2026-11-04.json`: automated execution
  receipts for the unmodified C-supplied 20-case and 14-boundary scripts.

## Observed result

All 40,336 source PSV files match the stored raw inventory's bytes, SHA256 and
MD5/ETag. All 40,336 independent record-level metadata, onset, reason and label
checks match `record_audit.csv`. The 24,095 included memberships and labels match,
and all 867,420 input cells (36 per patient) exactly match the last observed
values at actual ICULOS <=12, including NaN. CSV and Parquet agree numerically
with exact comparison using round-trip CSV float parsing. All 125 original
package-manifest entries were checked before and after, with source bytes
unchanged. The original audit and five split files were not rewritten.

| Site | Raw records | Included | Positive (12,24] |
|---|---:|---:|---:|
| A | 20,336 | 10,174 | 57 |
| B | 20,000 | 13,921 | 38 |

Sequential exclusions remain initial-hours missing8,793 and insufficient
follow-up7,448. Overlapping raw diagnostics identify first-observation-positive
203/223 (A/B) and observable onset <=12 in180/103. These records were already
excluded at earlier steps. A zero later sequential exclusion count is therefore
not evidence that raw early or left-censored records do not exist. Do not add
the overlapping diagnostics to the mutually exclusive exclusion flow.

## Interpretation and recipient boundary

Recovered onset means **dataset-label-derived onset**, not separately adjudicated
clinical onset. For first-observation-positive records, recovered onset remains
unknown; the checker never assigns `first_hour + 6` as an exact onset for them.
Fifteen raw records (A2/B13) have an observed-transition-derived onset after the
last released record; this fact is exposed in the receipt and does not introduce
a new v1 exclusion. Their clinical observation status is not inferred from the
shifted label. No positive label in an ineligible/short record is not asserted
to mean that patient's true clinical course is negative.

The unchanged C 20-case script returned exit0 with20/20 matching and no listed
structure issues. The unchanged C boundary script returned exit0 with14/14
synthetic checks. Those are automated executions of C-authored code, **not a new
human C acceptance**. Its first-positive synthetic case displays onset7 while
also marking censoring; this display must not be promoted to an observed exact
onset. Its printed description of sequential exclusion zeros also does not
replace the overlapping raw counts above. No C source was edited.

This delivery closes the absence of A's raw-level receipt as a technical
material gap. C still reviews this delivery and records C's own conclusion.
The precision gates and scientific freeze are separate from executable checks;
the owner and E retain their decisions. No model was fitted or protocol,
clinical source, label, patient split, saved run or historical manifest changed.

## Re-run from the receiving repository

Keep the immutable original package in an ignored cache and use a separate
output directory. With the locked Python dependencies installed:

```powershell
python scripts/verify_a_raw_psv_receipt.py --package .artifact-cache/a-source/T1_A_Day1_2026-11-03_v1_Rebuilt_Full --output-root .artifact-cache/a-raw-receipt
python -m pytest -q tests/test_a_raw_psv_receipt.py
```

The full receipt CSV and the20-case replay log contain patient identifiers and
should stay out of ordinary Git. Only the code, tests, aggregate JSON and
non-patient-level evidence are intended for ordinary Git. The aggregate records
the receipt SHA256 so that C can check the private file before inspecting it.
This run compares preserved inventory bytes; it does not claim a fresh download
or legal resolution of the source-license discrepancy.
