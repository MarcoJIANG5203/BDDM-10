# Results draft — historical, superseded

**Status:** Superseded by `paper/results_accepted_with_limits.md` after the 2026-11-06 accepted_with_limits record. Kept for history only. Do not use this file for the manuscript.

**Run:** `20261105T055420_02d05b15`; bundle `b-clinical-v1-20261104-r1` (SHA256 `2328d266...`); data `a-data-v1-20261104-r1`.

---

## 5.1 Cohort and missingness (DRAFT)

The delivered cohort contains 24,095 patients: 10,174 from hospital A and 13,921 from hospital B. The target outcome is observed in 95 patients overall (A 57; B 38). The 2026 internal test partition contains 1,525 patients with 8 positives. The prespecified precision gates (200 positives per site; 50 internal-test positives) are not met. `[D: Table 1 DRAFT, paper/inputs/a-data-v1-20261104-r1]`

Feature missingness is highest for Bilirubin_direct, Fibrinogen, EtCO2, TroponinI and BaseExcess; the full 36-feature table is in the DRAFT Table 1b. These are descriptive counts, not clinical conclusions.

## 5.2 Primary selective risk (DRAFT)

At the 0.60 target capacity, batch mode, primary seed 2026, the internal S0 result was:

- B2 confidence: 915 accepted, 1 error.
- B4 disagreement: 915 accepted, 2 errors.
- B4−B2 selective-risk difference: **+0.00109290** (95% paired bootstrap interval `[0.00000000, 0.00327869]`). `[D-102]`

For the external hospital (S4):

- B2: 8,352 accepted, 24 errors.
- B4: 8,352 accepted, 21 errors.
- B4−B2: **−0.00035920** `[−0.00107759, 0.00035920]`. `[D-102]`

The direction is not stable across the five seeds and scenarios. For S0, the mean B4−B2 difference over seeds was +0.00021858 (min −0.00109290, max +0.00109290); for S4 it was −0.00014368 (min −0.00047893, max +0.00011973). `[D-103]`

B5 and B6 are unavailable in both formal runs because the rule-selection partition contains 6 errors and 1,012 correct cases, below the prespecified 20/20 threshold. B6−B5 is therefore NA, not zero. `[D-101, D-102]`

## 5.3 Coverage (DRAFT)

MI original-set coverage is high overall, but **positive-class (y=1) coverage is 0/8** in the internal test; the same zero-positive pattern is reported across scenarios and seeds. Overall coverage must not be presented as positive-class safety. `[D-104]`

## 5.4 Disagreement diagnostics (DRAFT)

Among 1,388 singleton predictions at the primary condition, only 4 were errors. Error counts by disagreement quintile were 1/278, 0/277, 1/278, 0/277 and 2/278. The figure is annotated “Sparse errors; descriptive only”. This does not support a stable disagreement advantage. `[D-106, D-107]`

## 5.5 Stability (DRAFT)

Test-time three-state disagreement is reported for batch and frozen allocation in Table 5. The table is retained as a stability diagnostic, not as evidence of clinical safety. `[D-105]`

## 5.6 Summary (DRAFT)

The formal run reproduces the candidate arithmetic, but the scientific picture is limited: 57/38/8 positives, zero MI positive-class coverage, unavailable B5/B6, and an unstable B4−B2 direction. The appropriate manuscript conclusion is a limited or null finding, not a claim that imputation disagreement improves selective risk or patient safety.

---

**Do not insert these numbers into `paper/draft_v0.md` until:**

1. C’s formal-run conclusion and B/E reception are recorded;
2. `reviews/acceptance/<run_id>.json` exists and passes `scripts/make_figures.py`;
3. `paper/source_index.md` has final `S-xxx` entries;
4. D regenerates `paper/runs/<run_id>/` from the accepted run.
