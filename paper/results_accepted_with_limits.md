# Results — ACCEPTED_WITH_LIMITS (bounded descriptive draft)

**Status:** `ACCEPTED_WITH_LIMITS` for arithmetic/protocol fidelity and **bounded descriptive writing** from run `20261105T055420_02d05b15` (C/E acceptance, 2026-11-06). This is **not** final manuscript/PDF acceptance and does **not** authorize safety or superiority claims. The supplement run `20261105T055445_54dd08de` is also accepted with limits; D has not yet generated Tables S1–S3.

**Run:** `20261105T055420_02d05b15`; acceptance `reviews/acceptance/20261105T055420_02d05b15.json`; bundle `b-clinical-v1-20261104-r1` (SHA256 `2328d266...`).

---

## 5.1 Cohort

The delivered cohort contains 24,095 patients: 10,174 from hospital A and 13,921 from hospital B. The target outcome is observed in 95 patients overall (A 57; B 38). The 2026 internal test partition contains 1,525 patients with 8 positives. The prespecified precision gates (200 positives per site; 50 internal-test positives) are not met, so all results are limited to a finite-event analysis. `[S-001, S-009]`

Feature missingness is highest for Bilirubin_direct, Fibrinogen, EtCO2, TroponinI and BaseExcess; full values are in Table 1b. `[S-009]`

## 5.2 Primary selective risk

At the 0.60 target capacity, batch mode, primary seed 2026, S0:

- B2 confidence: 915 accepted, 1 error.
- B4 disagreement: 915 accepted, 2 errors.
- B4−B2 selective-risk difference: **+0.00109290** (95% paired bootstrap interval `[0.00000000, 0.00327869]`). `[S-002, S-003]`

At the external hospital (S4):

- B2: 8,352 accepted, 24 errors.
- B4: 8,352 accepted, 21 errors.
- B4−B2: **−0.00035920** `[−0.00107759, 0.00035920]`. `[S-005, S-013]`

The direction is unstable across seeds and scenarios; the result does not support a stable advantage for B4. `[S-005]`

B5 and B6 are unavailable because the rule-selection partition has 6 errors and 1,012 correct cases, below the 20/20 threshold. B6−B5 is NA, not zero. `[S-002, S-004]`

## 5.3 Scenario robustness

Across S0–S4 and five seeds, the B4−B2 difference is small and changes sign. For S0, the mean difference is +0.00021858 (min −0.00109290, max +0.00109290); for S4 it is −0.00014368 (min −0.00047893, max +0.00011973). `[S-005]`

## 5.4 Coverage

MI original-set coverage is high overall (about 0.907 in the primary S0 condition), but **positive-class (y=1) coverage is 0/8**. Overall coverage must not be presented as positive-class safety or as evidence that high-risk patients are protected. `[S-006]`

## 5.5 Disagreement diagnostics

Among 1,388 singleton predictions at the primary condition, only 4 are errors. Error counts by disagreement quintile are 1/278, 0/277, 1/278, 0/277 and 2/278. The figure is annotated “Sparse errors; descriptive only.” `[S-007]`

## 5.6 Stability

Test-time three-state disagreement is reported for batch and frozen allocation in Table 5. It is a stability diagnostic, not evidence of clinical safety. `[S-008]`

## 5.7 Sensitivity analyses

The supplement run `20261105T055445_54dd08de` is accepted with limits for RF (S0/S2), M=5/10/20 (S0) and alpha=.05 (S0/S2). Tables S1–S3 are generated under `paper/runs/20261105T055445_54dd08de/tables/` and bound to `S-010`; report them as sensitivity analyses, not as primary or safety evidence. `[S-010]`

## 5.8 Summary

The formal run reproduces the candidate arithmetic, but the scientific picture is limited: 57/38/8 positives, zero MI positive-class coverage, unavailable B5/B6, and an unstable B4−B2 direction. The defensible conclusion is a limited or null finding, not a claim that imputation disagreement improves selective risk or patient safety.

---

**Boundary:** acceptance scope explicitly excludes final manuscript/PDF and submission acceptance. This file may be used for bounded descriptive writing and figure/table integration only; C/E final consistency review and A license resolution remain required before submission.
