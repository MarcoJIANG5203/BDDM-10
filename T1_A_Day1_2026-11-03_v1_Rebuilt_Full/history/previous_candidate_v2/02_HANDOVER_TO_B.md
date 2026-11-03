# A-to-B Technical Handover

Prepared 2026-11-03. Status: executable candidate; C/E review pending.

## Files and joins

| File | Rows / key | Meaning |
| --- | --- | --- |
| data/X_last12.csv | one eligible record; record_id unique | 37 numeric predictors; empty cells are missing |
| data/missing_mask37.csv | identical key order | binary feature-level missing mask |
| data/observed_counts34.csv | identical key order | per-variable observed hourly counts, 0–12 |
| data/patients.csv | one eligible record | target, split and audit metadata; never pass wholesale to a model |
| data/patient_split_manifest.csv | one eligible record | fixed candidate site / target / split assignment |
| data/eligibility_audit_all_records.csv | all 40,336 source records | explicit inclusion/exclusion reason |
| data/model_feature_columns.json | configuration | training-only all-missing-feature detection and recommended subset |
| data/raw_field_dictionary.csv | 41 source columns | official English field meanings and documented units |
| data/derived_field_dictionary.csv | field definitions | target, metadata, masks and denominators |
| raw/training_setA.zip; raw/training_setB.zip | original files in local ZIPs | original bytes; local repackaging, not official downloadable ZIP releases |

Read missing numeric cells as NaN. Join exclusively on record_id, never infer pairing from filename order. IDs have a site prefix, e.g. A_p000001. Archive filenames have no site prefix; combine the archive identity and filename to recover the join ID. One raw file contributes at most one model row regardless of the number of imputations.

Use `outcome_12_24` as the binary target and `split` as the partition. Pass only the columns named in data/model_feature_columns.json to an imputer/model. `record_id` is a join key only. Never include `n_hours`, labels, first-positive hour, onset proxy, split, site or any future metadata as predictors. Keep the observation counts for auditing; adding them as model inputs would be an explicit feature-set revision.

## Fit boundaries

Fit all learned preprocessing and models on train only. Keep calibration for conformal calibration after tuning, internal_test for internal evaluation, and external_test for site-B evaluation. Do not refit an imputer on calibration or test records; transform them using the training-fitted procedure. If multiple imputations are sampled, document the training fit and inference sampling procedure, preserve record identity, and do not treat repeated imputations as independent patients.

The current split is versioned for reproducibility, not approved as the final group split. B can develop the interface now. Obtain C/E confirmation before treating it as the main experimental protocol. Do not select a different split because results look better.

## Reproduce locally

Python 3.14.7 was used. Cohort preparation, tests and report construction use the standard library; the download/source collectors additionally use requests. No account, API key, paid service or private dataset is required.

From the package root in PowerShell:

```powershell
python code/test_cohort_rules.py
python code/prepare_day1.py
python code/build_reports.py
```

To acquire the same official raw source in a new empty copy of the package:

```powershell
python code/download_official.py
python code/collect_sources.py
```

The downloader reuses verified files in existing local archives. It records failures and does not silently present a partial download as complete. The recovery utility records any later successful official-source repairs separately. Internet access is required only for acquisition. Keep the source and protocol version, split file and checksums with every experiment.

## Results B should later return

Return record_id, experiment/scenario ID, method, random seed, actual label, each imputation prediction or a documented linked array, mean prediction, disagreement score, conformal set, acceptance flag and predicted class. Include code version and parameters. These are proposed handover fields pending the absent group technical specification. Do not claim A has already produced these method outputs.
