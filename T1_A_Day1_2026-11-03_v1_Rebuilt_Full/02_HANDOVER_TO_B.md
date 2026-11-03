# Full A-to-B Handover — Formal v1

Read data/processed/cohort.parquet using the existing configs/protocol_v1.yaml. CSV is also accepted, with dtype={'patient_id':str}. Use exactly the36 names and order recorded in cohort_audit.json / src/data.py:34 physiologic/laboratory inputs,Age,Gender. patient_id/site/y_true are metadata/target, never predictors. NaN remains missing. B generates its36 indicators.

Use the provided splits/seed_2026.json through seed_2030.json without reshuffling. All five roles are nonempty, mutually exclusive, exhaustive and site-consistent. train/selection contain both classes. Largest-remainder class apportionment and exact seeded shuffling are documented in the audit. No old60/20/20 split or old20261103 seed is current.

The full package includes the original raw archives at raw/training_setA.zip and raw/training_setB.zip. They are locally repackaged containers with byte-preserved official source files, not official downloadable ZIP release assets. The complete per-file manifest is sources/raw_file_manifest.csv. Official dataset version1.0.0 is from2019; the companion Critical Care Medicine article is from2020. Source inventory timestamps are not clinical collection dates.

Current extraction requires complete actual ICULOS1--24 and observed0-to-1 transitions plus6 for dataset-defined onset; first-observation-positive records are not assigned precise onset. Inputs use only hours1--12. Missing Age/Gender are allowed and no undocumented adult-only exclusion is applied. See data/processed/record_audit.csv for every original record's decision and the exact sequential exclusion order.

The root code/prepare_day1.py rebuilds the current cohort from the included raw data and sources/protocol_snapshot. Original candidate artifacts exist only under history and are explicitly superseded. B's src/data.py is a preserved read-only copy used for verification, not a rewritten scientific implementation.

C must independently inspect the10 positive/10 negative raw examples and boundary evidence and enter their own review. Current precision gates fail; E must resolve the pre-freeze precision discussion. Structural checks do not grant clinical or scientific approval. No main-method experiments were run. The full directory retains all original evidence and current replay checks for review.
