# A input for the data and preprocessing section — 2026-11-04

Status: candidate methods material; personal/recipient acceptance and formal data freeze remain pending. This is A's input for D, not an accepted clinical result section.

We used the complete public training release of the PhysioNet/Computing in Cardiology Challenge 2019, version 1.0.0 (dataset DOI 10.13026/v64v-d857,2019). The companion publication appeared in Critical Care Medicine in 2020,48(2):210–217 (DOI 10.1097/CCM.0000000000004145). Source A and B correspond to BIDMC and Emory. The analysis unit is one released subject-record file; cross-stay person linkage is unavailable.

The prespecified prediction landmark is actual ICU hour 12, with the target outcome in (12,24]. Raw hourly data are checked for schema, contiguous integer ICULOS, duplicated/missing hours and monotone binary labels. The cohort requires observed hours 1–24. For observed 0-to-1 label transitions, dataset-defined onset is recovered as the first positive ICU hour plus 6; first-record-positive onset remains left censored. Inputs are the last observed value at ICU hour<=12 for 34 physiology/laboratory variables plus Age and Gender; missing values are retained. Site, ID, shifted labels, future measurements and stay duration are excluded from predictors. No extra adult-only criterion is introduced.

Hospital A is stratified 60/10/15/15 into train, selection, calibration and internal test; all B records form external test. Seeds 2026–2030 are fixed, with 2026 primary. No labels, split, endpoint or algorithm are altered in this closeout. The original v1 candidate audit reports 24,095 included records (A 10,174/B 13,921) and 57/38 target positives; internal test has 8 positives. The 200/200/50 project event gates are unmet. These candidate counts and review status must accompany any use; they are not proof of adequate precision or clinical safety.

The complete-hour rule restricts the target population. Missing and erroneous source measurements are not silently repaired. The clinical labels are source-derived and are not independently clinically adjudicated by automated integrity checks. The original license file and current source metadata disagree; the dated licensing evidence and clarification status must be retained until resolved.

Evidence: `reports/A_001_validation_2026-11-03_EN.md`, `reviews/A_raw_psv_receipt_2026-11-04.json`, and `handoffs/A/2026-11-04_A-001_closeout_EN.md`. D should integrate these methods only with explicit data/run version and actual C/E acceptance status.
