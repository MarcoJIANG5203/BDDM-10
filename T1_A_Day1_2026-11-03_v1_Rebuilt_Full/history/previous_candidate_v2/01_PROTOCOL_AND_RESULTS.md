# Candidate Cohort Protocol and Actual Day-One Results

Version: candidate_v2. Prepared: 2026-11-03. Status: pending C label review and E protocol confirmation.

## Evidence, inherited plan, and new implementation choices

**Source facts:** The official release is [PhysioNet Challenge 2019, version 1.0.0](https://physionet.org/content/challenge-2019/1.0.0/), published 2019-08-05. It supplies hourly subject files with a label shifted six hours before dataset-defined onset. The [original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6964870/) identifies sites A and B as Beth Israel Deaconess Medical Center and Emory University Hospital. Public file IDs do not supply cross-stay person linkage. Accordingly, the implemented unit is a released subject/ICU-record file; person-level deduplication cannot be independently established.

**Inherited from the supplied group plan:** use information from the first 12 ICU hours, assess the subsequent period through hour 24, use one hospital for development and another for external validation, and preserve missingness. The supplied plan is user-provided project context, not external scientific evidence or independent approval of unspecified rules.

**New candidate choices:** age >=18, contiguous hourly axis using actual ICULOS, observation through hour 24 for both outcome classes, last-observed aggregation, A development / B external, and the 60/20/20 A split. These choices were implemented to produce a concrete reviewable handover; they are not official challenge rules and not recorded group approvals.

## Cohort and labels

Apply the following sequentially. The audit stores one primary exclusion reason per source record; therefore exclusion counts are mutually exclusive and depend on this order.

1. Require the expected 41-column schema and parseable numerical/NaN entries; disallow infinity.
2. Require positive integer ICULOS with increments of one. The first observed hour may exceed one. Use actual ICU hours rather than row position.
3. Require nonmissing binary labels with no 1-to-0 reversal.
4. Require observation covering the landmark: first observed ICULOS <=12 and last observed ICULOS >=12. Absent leading hours remain unavailable; they are counted as missing in the fixed 12-hour window.
5. Require an observed age >=18 using only hours 1–12.
6. Mark a positive label at the first observed row as left-censored and exclude it from this incident-onset cohort.
7. For an observed zero-to-one transition at ICU hour h, define the **dataset-label-derived hourly onset proxy** as h+6. Exclude proxy onset <=12.
8. Require last observed ICULOS >=24 in both classes, regardless of the number of rows.
9. Set y=1 if 12 < proxy onset <=24; otherwise y=0. Thus first-positive label hours 7–18 map to a positive target. A later onset is negative for this fixed horizon. An all-zero full record is negative for this observed horizon.

Do not exclude all records with any positive label before hour 12: that would incorrectly discard incident onsets at hours 13–18. The first-positive-plus-six computation is consistent with the six-hour offset in the [official evaluation code](https://raw.githubusercontent.com/physionetchallenges/evaluation-2019/master/evaluate_sepsis_score.py), but remains an hourly proxy rather than independently adjudicated clinical onset. The public columns do not contain the complete antibiotics/culture history needed to rebuild the clinical definition. Sepsis-3 itself is the [2016 consensus definition](https://pubmed.ncbi.nlm.nih.gov/26903338/).

## Actual flow

| site | stage | n_records |
| --- | --- | --- |
| A | invalid_schema_or_values | 0 |
| A | invalid_time_axis | 0 |
| A | invalid_label_sequence | 0 |
| A | insufficient_history_12h | 418 |
| A | nonadult_or_age_unknown | 0 |
| A | left_censored_onset | 14 |
| A | onset_at_or_before_12h | 131 |
| A | insufficient_followup_24h | 3567 |
| A | included | 16206 |
| B | invalid_schema_or_values | 0 |
| B | invalid_time_axis | 0 |
| B | invalid_label_sequence | 0 |
| B | insufficient_history_12h | 532 |
| B | nonadult_or_age_unknown | 20 |
| B | left_censored_onset | 1 |
| B | onset_at_or_before_12h | 74 |
| B | insufficient_followup_24h | 4533 |
| B | included | 14840 |

Every input record appears in data/eligibility_audit_all_records.csv, including exclusions. Ineligible records receive split=excluded; no excluded record enters X_last12.csv.

### Time-axis correction and endpoint feasibility

Direct inspection found that 7497 A records and 1296 B records start after hour 1. All raw records passed the revised contiguous-integer-hour check. Candidate v2 uses actual ICULOS values, never re-labels row 1 as ICU hour 1, and records first_observed_hour, last_observed_hour and history_rows_observed. The initial stricter v1 snapshot was preserved internally; its numbers are superseded.

| site | known_transition_onsets_12_24_before_other_filters | retained_positive | known_positive_excluded_for_followup_24h | known_positive_excluded_for_other_reasons |
| --- | --- | --- | --- | --- |
| A | 334 | 78 | 256 | 0 |
| B | 152 | 40 | 112 | 0 |

The complete-24-hour rule excludes records with target-window label-derived onset proxies whose observation ends before hour24. Of these excluded records, A has 0 and B has 1 with the inferred proxy itself beyond the last observed hour; these must not be described as directly observed clinical events. C/E must decide whether the scientific estimand should instead retain ascertainable positive endpoints with shorter post-event follow-up while requiring horizon ascertainment for negatives, or use a censoring-aware design. Such a change requires a new version and reassessment of selection/censoring bias; no alternative was silently promoted because it increased positive counts. The current candidate must not be described as finalized or statistically adequate.

## Actual candidate split and target prevalence

| scope | n_records | positive | negative | positive_fraction |
| --- | --- | --- | --- | --- |
| site_A | 16206 | 78 | 16128 | 0.004813 |
| site_B | 14840 | 40 | 14800 | 0.002695 |
| train | 9722 | 46 | 9676 | 0.004732 |
| calibration | 3240 | 15 | 3225 | 0.004630 |
| internal_test | 3244 | 17 | 3227 | 0.005240 |
| external_test | 14840 | 40 | 14800 | 0.002695 |

Within each A outcome class, sort by SHA256("20261103|record_id"). Allocate the first floor(0.6*n) records to train, the next floor(0.2*n) to calibration and the remainder to internal_test. Assign every eligible B record to external_test. The split manifest is deterministic and should be reused unchanged across all downstream strategies. No performance-dependent selection was used. If tuning is needed, perform it only within train, e.g. cross-validation; do not use conformal calibration or either test set for model/threshold selection.

## Predictor construction and missingness

Each retained record has 34 time-varying inputs plus Age, Gender and HospAdmTime. Each is the last nonmissing value observed during ICU hours 1–12; a feature stays missing if never observed in that window. No backward filling from later hours, outcome balancing, imputation, scaling, clipping, or normal-value substitution was performed. Raw values, including possible errors, remain in the source archives.

- `X_last12.csv`: 37 predictors plus record_id join key.
- `missing_mask37.csv`: 1=missing predictor; 0=observed predictor.
- `observed_counts34.csv`: observed hourly cells among 12 for each dynamic input.
- Feature missing fraction: missing predictors / 37.
- Hourly dynamic missing fraction: missing hourly cells / (12*34).

Actual mean feature missing fractions: A=0.367186, B=0.454050. Actual mean hourly dynamic missing fractions: A=0.791821, B=0.805064. Per-feature and per-split values are saved in reports/feature_missingness37.csv and reports/hourly_missingness34.csv.

Training-all-missing columns: **EtCO2**. These columns cannot be learned by a training-only imputer. The master table retains all 37 columns; data/model_feature_columns.json identifies the recommended training-derived model subset. Apply that same subset to calibration and both test sets. Do not use B availability to choose inputs.

Unit1 and Unit2 are omitted as site-dependent administrative inputs; ICULOS is a fixed landmark rather than a model input. Label, future length of stay, onset time, site and split are metadata, never predictors. Aggregate last-value missingness differs from hourly missingness; the two measures must not be interchanged. Leading hours absent from the file and recorded NaN cells both count as unavailable for this denominator; history_rows_observed distinguishes absent leading rows. The current candidate operates on aggregated tabular features; imputing full hourly sequences would require an explicit protocol change and fresh version.

## Limits and downstream implications

- Requiring follow-up through hour 24 avoids silently treating early-ended records as full-horizon negatives, but selects patients with longer observed ICU stays. The resulting estimand is conditional on this cohort and is not all ICU admissions. An early-discharge/competing-event alternative would be a different protocol, not a silent relabeling.
- This fixed-landmark study differs from the original hourly early-warning challenge. Do not compare its metrics directly with official challenge leaderboard scores.
- The six-hour label correction does not establish exact clinical event timing; first-row positives are left-censored. The hourly boundary convention must be reported.
- Only original missingness was processed today. Extra random missingness and unavailable laboratory panels belong to the later experiments. Preserve this split and apply each scenario identically to competing strategies.
- External-site differences may invalidate exchangeability assumptions. No external finite-sample conformal coverage guarantee is claimed. Calibration and strategy selection must not fit on B.
- Extremely sparse features and possible unit/documentation inconsistencies require review before clinical range filters. In particular, documented FiO2 percent units coexist with fractional-looking raw values. No conversion was guessed. Raw documentation units are preserved as source metadata, not clinically validated units.
- Today supplies data and audit evidence; it supplies no evidence that prediction disagreement improves accuracy or that the method has clinical benefit. No inferential statistics, confidence intervals or model performance results were manufactured. Review the positive counts in calibration and internal_test before freezing the endpoint; these counts alone do not establish adequate statistical precision.
