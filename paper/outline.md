# Paper outline — D-001

**Working title:** Imputation Disagreement for Selective Prediction under Missing Clinical Data: A Conformal Rejection Study

**Target:** ICBDDM 2026 Workshop 3; internal submission target 2026-11-19 18:00 Beijing time (buffer 2026-11-20). Current internal budget: 6 pages, double column; verify the official page limit and template via C-002 before typesetting.

**Status:** D-001 outline only. No clinical results exist yet. Every `[RESULT:S-xxx]` is a placeholder that must be replaced by a value generated from an accepted clinical run and recorded in `paper/source_index.md`. Synthetic values in `paper/validation/` are software-validation artifacts and must never appear in this manuscript.

---

## 0. Abstract (≈250 words)

Draft structure, one sentence per bullet:

1. **Context.** ICU prediction models see incomplete measurements; multiple imputation is often used to fill them, but the resulting predictions can vary across plausible completions.
2. **Question.** Does this imputation-induced disagreement identify erroneous predictions better than confidence or missingness burden, and does it improve selective risk at the same automatic-acceptance capacity?
3. **Design.** PhysioNet 2019; 12-hour feature window; outcome in (12, 24] hours after restoring the official 6-hour label lead; internal hospital A development/test and hospital B external test; 10 imputations; shared logistic-regression predictor; split conformal prediction; capacity-constrained selection.
4. **Primary endpoint.** Selective risk difference B4 − B2 at target acceptance c = 0.60, with paired patient bootstrap 95% interval. B6 − B5 tests conditional incremental value.
5. **Results.** `[RESULT:S-003]` for B4 − B2; `[RESULT:S-004]` for B6 − B5; report realized acceptance, dangerous misses, residual risk, coverage, and event counts alongside the effect. Never report the effect without the interval and denominators.
6. **Conclusion (conditional).** State only what the accepted clinical run supports. If there is no incremental benefit, say so and describe the conditions where disagreement is not useful. Do not claim clinical utility, deployment safety, or guaranteed conditional coverage.

---

## 1. Introduction (≈800 words)

1.1 Missingness is structural in ICU data, not a nuisance: the same patient can receive different plausible completions; a single imputation hides this sensitivity.
1.2 Existing selective-prediction practice ranks by confidence or missingness; these signals answer different questions. Confidence is model self-assessment; missingness is data quantity, not completion sensitivity.
1.3 Conformal prediction provides distribution-free marginal coverage for prediction sets, but only singleton sets enter an automatic-decision pool; selection after conformal calibration is an empirical decision problem, not a inherited guarantee.
1.4 Gap: disagreement across multiple imputations is a candidate signal, but it needs a fair comparison at the same acceptance capacity, the same predictor, the same masks, and the same calibration threshold.
1.5 Contributions:
   - C1: a capacity-constrained evaluation of imputation disagreement against confidence and missingness under a shared MI predictor and conformal sets.
   - C2: a conditional-increment test using two error-risk models (B5 vs B6), fitted on the rule-selection partition.
   - C3: a stress-test slate (natural missingness, additional 10%/30% missingness, unavailable laboratory block, external hospital) plus stability and sensitivity analyses.
   - C4: a reproducible evidence chain from immutable run to every manuscript number.

**Do not write:** "disagreement improves safety" or "disagreement is a better uncertainty measure" before the accepted clinical run. Use "we test whether".

---

## 2. Related work (≈700 words; owner C-002)

C-002 must supply verified references and a difference statement. Provisional scope, no citations inserted by D: **D has now checked the C-002 list in `paper/references_checklist.md`; seven entries are verified, including R5 (“MC²”) which C-004 supplied (MICCAI 2026 Satellite/MLMI, LNCS 17272). Only those seven may be cited.**

| Theme | What the section must establish | Source |
|---|---|---|
| Conformal prediction and selective classification | marginal coverage vs selective risk; why singleton acceptance is a decision layer | C-002 |
| Missing data and multiple imputation | MI as a practical stochastic completion; disagreement as a by-product; not a posterior guarantee | C-002 |
| Uncertainty in clinical prediction | confidence, calibration, abstention; what is already known | C-002 |
| Positioning | this study measures incremental value of disagreement at fixed capacity, not a new conformal guarantee or a new imputer | C-002 + protocol v1 |

Rules: every citation must be read at least at abstract + results/discussion level by C; record the verification scope in the literature table. D does not add unverified references to satisfy a narrative.

---

## 3. Methods (≈1,800 words)

Use `T1_统一实验说明_v1.md` and `B_方法说明_论文素材.md` as the source of truth; the English methods draft in the latter can be reused after protocol checks.

### 3.1 Cohort, labels, and splits
- PhysioNet 2019; ICU hour 12 prediction point; inputs from t ≤ 12; outcome y=1 iff 12 < t_onset ≤ 24.
- Official SepsisLabel is advanced by 6 hours; restore t_onset = t_first + 6 where a 0→1 transition is observed; exclude patients already onset by hour 12; do not invent onset for patients whose first record is already 1.
- Hospital A: stratified patient-level 60/10/15/15 train/rule-selection/calibration/internal-test; hospital B: external test. Seeds 2026–2030; 2026 primary.
- Include the flow of inclusions/exclusions and per-site positive counts in Table 1; A-001/C-001 own the audit.

### 3.2 Multiple imputation and shared predictor
- 34 physiological/laboratory variables + Age + Gender; 36 inputs with missingness indicators.
- Stochastic chained equations, Bayesian ridge conditional models, 10 iterations, M=10; fit on training inputs only; outcome never enters the imputer.
- Clip generated values at missing positions to training observed ranges; preserve observed values.
- One shared logistic-regression classifier trained on M completed copies with weight 1/M; C selected from 0.1/1/10 by rule-selection AUPRC; random forest (300 trees) as robustness check.
- p̄ = mean(p_m), D = sample SD (ddof=1), flip = predictions on both sides of 0.5.

### 3.3 Conformal sets and acceptance
- Score s(x,y)=1−p̄(y|x); split conformal at α=0.10 (0.05 sensitivity); finite-sample index k=ceil((n+1)(1−α)).
- Empty and two-label sets are rejected; only singleton sets enter the automatic pool.
- Capacity-constrained batch evaluation: c ∈ {0.40, 0.60, 0.80}, K=min(floor(cN), N_single); B2–B6 share pool and K; ties by fixed patient-ID hash; no labels in ranking.
- Report capacity shortfall and realized acceptance; do not describe batch allocation as a fixed per-patient deployment rule.
- Frozen-threshold deployment evaluation as a secondary analysis; realized acceptance may differ.

### 3.4 Comparators
Table of B0–B6 with ranking scores and the role of each; B0 uses median imputation and its own conformal calibration; B1 accepts all singletons; B2 confidence; B3 missingness; B4 disagreement; B5/B6 error-risk models on the rule-selection partition (C=1; 20-error/20-correct minimum; otherwise report unavailable).

### 3.5 Metrics and uncertainty
- Acceptance, selective risk, dangerous miss, negative residual risk, original-set coverage; zero denominators are NA with counts.
- Primary contrast B4−B2 at c=0.60; conditional increment B6−B5; paired patient bootstrap 1,000 resamples, re-ranking within each resample; 95% percentile interval.
- Five seeds describe full-pipeline stability; they are not five independent clinical cohorts.
- Coverage strata by class and missingness tertiles; report n and covered counts.

### 3.6 Stress tests and sensitivity
- S0 natural missingness; S1/S2 hide 10%/30% of originally observed physiological values at test time; S3 hides the laboratory block; S4 external hospital natural missingness.
- Same patients, same masks across methods; retrain nothing at test time; recompute indicators after hiding.
- Sensitivity: RF on S0/S2; M=5/20 on S0; α=0.05 on the primary seed; five test-imputation batches for decision stability.

### 3.7 Reproducibility
- Immutable run directory; manifest with source/data/split hashes; `scripts/make_figures.py` verifies artifact hashes and writes provenance.
- Every manuscript number maps to `paper/source_index.md` and a generated table/figure-data CSV.

---

## 4. Experimental setup (≈500 words)

- Data version, cohort size, positive counts, missingness summary: `[RESULT:S-001]`, `[RESULT:S-009]`.
- Run IDs, config hashes, environment, seeds, compute time: cite the accepted run manifest; do not copy numbers from chat.
- Primary seed 2026; 2027–2030 stability; M=10; α=0.10; LR primary; RF robustness.
- State explicitly that synthetic runs are excluded from all paper results.

---

## 5. Results (≈1,500 words)

Each subsection starts with the question, then the table/figure, then the interpretation. Do not reorder results to hide a null or adverse scenario.

### 5.1 Cohort and missingness (Table 1, Figure 1)
- Per-site n, positives, base rate, exclusions; feature missingness.
- `[RESULT:S-001]`, `[RESULT:S-009]`.
- Check: no patient appears in more than one split; hospital identity correct; labels restored before freezing.

### 5.2 Primary selective risk (Table 2, Table 2b, Figure 2)
- At c=0.60, report B0–B6 selective risk, realized acceptance, dangerous miss, residual risk, coverage, pool size, shortfall.
- Primary effect `[RESULT:S-003]`; conditional increment `[RESULT:S-004]`.
- Interpret negative differences as lower selective risk for B4 (or B6); always pair with the interval and the realized acceptance.
- If the singleton pool is below the target, report the shortfall and do not interpret ranking differences.

### 5.3 Missingness and external stress tests (Table 3, Figure 3)
- B4−B2 and B6−B5 across S0–S4, mean and min–max over seeds; S4 is external, not a pooled sample.
- Report any scenario where the direction reverses or the interval crosses zero; do not select only favourable scenarios.
- `[RESULT:S-005]`.

### 5.4 Coverage (Table 4, Figure 4)
- Original-set marginal coverage overall and by class/missingness stratum; include empty sets in the denominator.
- State that coverage is not conditional safety for the accepted subset; accepted-subset risk remains empirical.
- `[RESULT:S-006]`.

### 5.5 Disagreement diagnostics (Figure 5)
- Error rate by disagreement quintile among singleton predictions (all patients, not only accepted); scatter of p̄ vs D coloured by correctness.
- Descriptive only; quintiles are not a decision rule; small bins carry wide intervals.
- `[RESULT:S-007]`.

### 5.6 Test-time stability (Table 5, Figure 6)
- Three-state disagreement across five test-imputation batches, batch vs frozen allocation; separate batch-composition effects from patient-level sensitivity.
- `[RESULT:S-008]`.

### 5.7 Sensitivity analyses (Supplementary Tables S1–S3)
- RF S0/S2; M=5/20 S0; α=0.05. Report direction and interval; do not promote a sensitivity result to the primary claim.
- `[RESULT:S-010]` (to be generated from the accepted supplement run).

---

## 6. Discussion (≈700 words)

- Principal finding: whether D adds information beyond confidence/missingness at the same capacity; state effect size and uncertainty, not just significance.
- Mechanism: why MI disagreement may help (completion-sensitive patients) and why it may not (low D can still be wrong; high D can be irreducible noise); link to Figure 5 descriptively.
- Comparison with confidence and missingness: B3 is a data-quantity signal; B2 is model self-confidence; D is completion sensitivity. They are not interchangeable.
- Clinical workflow: batch capacity allocation vs fixed per-patient thresholds; human review is a resource; report realized acceptance and dangerous misses.
- Limitations: one public dataset; two hospitals; no external prospective validation; MI is a practical stochastic procedure, not a true posterior; conformal marginal coverage does not guarantee accepted-subset safety; capacity evaluation is batch-level; label timing depends on the 6-hour restoration; missingness scenarios are stress tests, not causal mechanisms; 6-page budget limits sensitivity analyses.
- Do not claim deployment readiness, cost-effectiveness, or causal benefit.

---

## 7. Conclusion (≈200 words)

Restate the question and the accepted-run answer, including a null result if applicable. One sentence on what would be needed before clinical use (prospective evaluation, per-site calibration, workflow study). No new numbers.

---

## Statements

- **Reproducibility:** code, configs, tests, run manifests; large artifacts via Release with SHA256; figure/table regeneration command.
- **Data availability:** PhysioNet 2019 credentialed access; no raw patient data in Git.
- **Ethics:** secondary use of de-identified public data; follow the data use agreement.
- **AI use disclosure:** follow the workshop rule verified by C-002; disclose assistance if required.
- **Author contributions:** A data/labels; B methods/experiments; C literature/independent audit; D figures/manuscript integration; E coordination/integrity; corresponding author confirmed by the group.

---

## Claims ledger (paper cannot advance without an accepted source)

| Claim ID | Claim (as it will appear) | Evidence | Status |
|---|---|---|---|
| CL-1 | At c=0.60, B4 selective risk differs from B2 by `[RESULT:S-003]` | Table 2b; bootstrap CSV | Pending B-002/C audit |
| CL-2 | D provides incremental information beyond confidence+missingness: B6−B5 `[RESULT:S-004]` | Table 2b | Pending |
| CL-3 | The direction is consistent/varies across S0–S4 and hospital B | Table 3, Figure 3 | Pending |
| CL-4 | Original-set coverage is `[RESULT:S-006]`; accepted-subset safety is empirical | Table 4, Figure 4 | Pending |
| CL-5 | Test-time three-state instability is `[RESULT:S-008]` | Table 5, Figure 6 | Pending |
| CL-6 | Synthetic runs validate the pipeline only | `paper/validation/`, provenance | Available as QA only |

**Prohibited claims:** clinical benefit; improved patient safety; conditional coverage guarantee for accepted patients; superiority without interval and denominators; any number from a synthetic run; any citation not verified by C-002/C-004.

---

## Writing and review workflow

1. D maintains the outline and the figure/source indices; A/B/C supply accepted evidence, not screenshots.
2. D generates results only from an accepted run; C independently checks every number in Table 2/2b and the abstract; E checks consistency across abstract, body, figures, tables, and conclusion.
3. C-002 locks the reference list and venue requirements before the full draft.
4. D-002 gate: A-001 accepted + C-001 label/metric audit + B-002 clinical run accepted by C/E + C-002 references/venue verified.
5. Frozen results: after 2026-11-13, only error fixes or documented rechecks; no re-running to chase a narrative.

## Word budget

| Section | Target words | Notes |
|---|---:|---|
| Abstract | 250 | hard limit per venue; verify |
| Introduction | 800 | 4 paragraphs + contributions |
| Related work | 700 | C-002 verified only |
| Methods | 1,800 | shared with supplement |
| Experimental setup | 500 | may merge into Methods |
| Results | 1,500 | 6 subsections |
| Discussion | 700 | limitations explicit |
| Conclusion | 200 | no new numbers |
| **Total** | **≈6,450** | plus references, tables, figures; 6-page budget may require cuts |
