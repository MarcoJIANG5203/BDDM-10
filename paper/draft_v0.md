# Draft v0 — D-002 preparation (not for submission)

**Status:** English manuscript skeleton prepared on 2026-11-04. **No accepted clinical run exists yet.** Every `[RESULT:S-xxx]` is an unresolved placeholder; no result number in this draft may be quoted, submitted, or circulated as a finding. Synthetic and candidate-run outputs are excluded.

**Citation policy:** only the six entries in `paper/references.bib`, all metadata-verified in `paper/references_checklist.md`. The C-002 entry “MC² (MICCAI 2026)” is **not cited** because no DOI/URL could be verified. Claims marked `[CLAIM-CHECK]` require full-text confirmation before submission.

**Working title:** Imputation Disagreement for Selective Prediction under Missing Clinical Data: A Conformal Rejection Study

---

## Abstract

**Background.** Clinical prediction models routinely encounter incomplete measurements. Multiple imputation (MI) replaces each missing value with several plausible completions, so the same patient can receive different predictions across completions. Whether this imputation-induced disagreement identifies erroneous predictions better than confidence or missingness burden is unclear.

**Methods.** We use the PhysioNet/Computing in Cardiology Challenge 2019 data \cite{reyna2020early}, with a 12-hour feature window and an outcome in the subsequent 12 hours after restoring the challenge’s 6-hour label lead. Hospital A provides development, rule-selection, calibration and internal-test partitions; hospital B is held out for external testing. A stochastic chained-equation imputer generates ten completed versions per patient, and a shared logistic-regression classifier is trained across the completed records. Split conformal prediction \cite{angelopoulos2023conformal,zaffran2023conformal} defines singleton candidate sets; only singleton sets enter the automatic-decision pool. At a prespecified acceptance target, we compare ranking by confidence, missingness burden, imputation disagreement, and two error-risk models. The primary contrast is the selective-risk difference between disagreement ranking (B4) and confidence ranking (B2) at a 0.60 target; the conditional-increment contrast is B6 minus B5. We report paired patient-level bootstrap intervals, realized acceptance, dangerous misses, residual risk, and original-set coverage.

**Results.** `[RESULT:S-002]`–`[RESULT:S-008]`. The primary contrast is `[RESULT:S-003]`; the conditional increment is `[RESULT:S-004]`. Results will be reported with intervals, denominators, and capacity-shortfall status, including null or adverse findings.

**Conclusions.** `[RESULT:S-011]` The conclusion will be limited to the accepted run and will not claim clinical utility, deployment safety, or conditional coverage for accepted patients.

---

## 1 Introduction

In intensive care, measurements are collected asynchronously and incompletely. A model that predicts deterioration from the first 12 hours therefore depends on how missing values are handled. Multiple imputation is attractive because it represents uncertainty about the missing values rather than committing to one completed dataset. Its practical by-product is that predictions can vary across plausible completions: two patients with the same mean predicted risk may differ in how sensitive that risk is to the completion.

Selective prediction offers a way to defer uncertain cases to human review. Conformal prediction provides distribution-free marginal coverage for prediction sets \cite{angelopoulos2023conformal}, and recent work has connected conformal sets with cost-aware deferral in clinical triage \cite{kwon2026conformal}. Missing values complicate this pipeline: conformal prediction with missing values has been studied \cite{zaffran2023conformal}, and conformal selection has been used for clinical data imputation \cite{he2026safeimpute}. Separately, uncertainty-aware sequence models for sparse healthcare time series use imputation and weighted evidential regression \cite{vavaroutas2025squiredl}.

These lines of work leave a practical question open. Confidence and missingness answer different questions from completion sensitivity. Confidence is the model’s self-assessment; missingness describes how much data are absent; imputation disagreement describes how much the prediction moves across plausible completions. A fair comparison must hold the predictor, the imputation draws, the conformal threshold, the candidate pool and the number of automatically accepted patients fixed. It must also report what happens when the singleton pool is smaller than the target capacity.

This study asks whether imputation disagreement provides incremental information for selective prediction beyond confidence and missingness under a shared MI predictor and conformal rejection. We evaluate this question at a prespecified acceptance capacity, across natural and induced missingness, and in an external hospital. The contributions are:

1. A capacity-constrained comparison of disagreement, confidence and missingness rankings that shares the MI predictor, conformal sets, masks and accepted count.
2. A conditional-increment test using two error-risk models fitted on the rule-selection partition, with disagreement added only in the second.
3. A stress-test slate covering natural missingness, additional hidden measurements, an unavailable laboratory block, and an external hospital, plus test-time imputation stability and sensitivity analyses.
4. A reproducible evidence chain from an immutable run to every manuscript number, with a written acceptance gate before any clinical figure is generated.

We do not propose a new conformal guarantee, a new imputer, or a causal explanation of missingness. The object of study is a decision-layer signal: whether disagreement across MI draws improves the ranking of patients for automatic acceptance at a fixed capacity.

---

## 2 Related Work

### 2.1 Conformal prediction and selective classification

Split conformal prediction constructs prediction sets with finite-sample marginal coverage under exchangeability \cite{angelopoulos2023conformal}. In clinical settings, coverage alone is insufficient: a retained subset can have a different error rate from the full test population, and deferral decisions have asymmetric costs. Cost-aware deferral with conformal sets has been evaluated for clinical triage under distribution shift \cite{kwon2026conformal}. Our work uses the same split-conformal construction but treats the post-calibration acceptance step as the object of study: which patients enter the automatic pool at a fixed capacity, and whether imputation disagreement improves that ranking.

### 2.2 Missing data and multiple imputation

Conformal prediction with missing values has been analyzed for impute-then-predict pipelines \cite{zaffran2023conformal}. Conformal selection has also been applied to clinical data imputation \cite{he2026safeimpute}. Our question is different in level: those works address the validity or selection of imputed values, whereas we ask whether patient-level variation across MI draws is useful for deciding which predictions to automate. We treat MI as a practical stochastic procedure with explicit clipping and reproducibility rules, not as a recovery of the true missing-data distribution.

### 2.3 Uncertainty in sparse clinical time series

Evidential deep learning with spline-based imputation and weighted observed/imputed points has been proposed for sparse healthcare time series \cite{vavaroutas2025squiredl}. That line of work estimates uncertainty within a sequence model. Our design instead fixes a shared tabular predictor and measures disagreement across repeated imputations; the two signals are related but not interchangeable.

### 2.4 Positioning

`[CLAIM-CHECK: C-002]` The closest clinical work combines conformal sets with cost-aware deferral \cite{kwon2026conformal}; the closest missing-data work studies conformal prediction or conformal imputation \cite{zaffran2023conformal,he2026safeimpute}. Our incremental question is whether imputation disagreement adds information beyond confidence and missingness at the same acceptance capacity. We do not claim to be the first to handle missing clinical data, and we do not claim that disagreement is a superior uncertainty measure in general.

> Citation note: the C-002 entry “MC² (MICCAI 2026 workshop)” has no verified DOI/URL and is intentionally omitted. It must not be added without a source.

---

## 3 Methods

### 3.1 Cohort, labels and partitions

We use the PhysioNet/Computing in Cardiology Challenge 2019 data \cite{reyna2020early}. The prediction time is ICU hour 12; inputs use observations up to and including hour 12. The challenge label is advanced by six hours relative to the dataset-defined sepsis onset. We restore onset as the first observed 0-to-1 transition plus six hours; patients already onset by hour 12 are excluded; records whose first observation is already positive are not assigned a precise onset. The outcome is `y = 1` if and only if `12 < onset <= 24`, and `y = 0` otherwise within the observation window. This is the dataset-defined endpoint, not real-time clinician adjudication.

Hospital A is split at the patient level into training (60%), rule-selection (10%), calibration (15%) and internal test (15%), stratified by outcome. Hospital B is held out entirely for external testing. Five fixed seeds (2026–2030) are used; 2026 is the primary seed. Cohort counts, exclusions and positive counts are reported in Table 1 and `[RESULT:S-001]`; the label and boundary audit is owned by A and independently checked by C.

### 3.2 Multiple imputation and shared predictor

The input space contains 34 physiological/laboratory variables plus Age and Gender, with missingness indicators for all 36 inputs. A stochastic chained-equation imputer with Bayesian ridge conditional models is fitted on training inputs only; the outcome is never passed to the imputer. Ten iterations and M=10 completed versions are used. Values generated at missing positions are clipped to the training-observed range; observed values are preserved. Variables entirely missing in training are removed from the numerical inputs while their indicators are retained.

A single logistic-regression classifier is trained on the M completed copies with weight 1/M per copy. The regularization parameter is selected from 0.1, 1 and 10 by average precision on the rule-selection partition, with ties resolved toward the smaller value. A random forest with 300 trees is used as a robustness check. For each patient, `p_mean` is the mean predicted positive probability across draws and `D` is the sample standard deviation (ddof=1); a flip indicates predictions on both sides of 0.5. Replicates are never treated as independent patients.

### 3.3 Conformal sets and capacity-constrained acceptance

The nonconformity score for candidate label `y` is `1 - p_mean(y)`. The split-conformal threshold at level `alpha = 0.10` is the `ceil((n+1)(1-alpha))`-th ordered calibration score; if the index exceeds the calibration size, the threshold is infinite. Empty and two-label sets are rejected; only singleton sets enter the automatic pool. Coverage is evaluated over all test patients, including empty sets.

At target acceptance `c` in {0.40, 0.60, 0.80}, the number accepted is `K = min(floor(cN), N_single)`, where `N` is the test size and `N_single` is the singleton-pool size. B2–B6 share the pool and `K`. Ties are broken by a fixed hash of patient identifiers, never by labels. If the pool is smaller than the target, the actual accepted count and shortfall are reported; accepting the whole pool must not be interpreted as a ranking difference. A frozen-threshold deployment analysis is reported separately, and its realized acceptance may differ.

### 3.4 Comparators

| ID | Strategy | Ranking score |
|---|---|---|
| B0 | Training-median imputation + same classifier + independent conformal calibration | none (accept all singletons) |
| B1 | MI mean + conformal, accept all singletons | none |
| B2 | Confidence | `1 - max(p_mean, 1 - p_mean)` ascending |
| B3 | Missingness burden | fraction missing among the 34 physiological variables, ascending |
| B4 | Imputation disagreement | `D` ascending |
| B5 | Error-risk model | logistic regression on confidence and missingness, fitted on the rule-selection partition |
| B6 | Error-risk model with disagreement | B5 inputs plus `D` |

B5/B6 use all rule-selection patients, the base classification error at `p_mean >= 0.5` as the target, L2 logistic regression with C=1, and no additional tuning. If the rule-selection partition has fewer than 20 errors or fewer than 20 correct predictions, the model is unavailable and the conditional-increment conclusion is limited accordingly.

### 3.5 Metrics and uncertainty

Acceptance is the number accepted divided by all test patients. Selective risk is the number of accepted errors divided by the number accepted. Dangerous miss is the number of true positives that are accepted and predicted negative, divided by all true positives. Negative residual risk is the number of true positives among accepted negative predictions, divided by accepted negative predictions. Original-set coverage is the fraction of patients whose true label is in the original conformal set. Zero denominators are reported as NA with counts.

The primary contrast is B4 minus B2 selective risk at c=0.60; negative values favor B4. The conditional increment is B6 minus B5. Intervals use 1,000 patient-level paired bootstrap resamples; capacity allocation is recomputed within each resample, preserving paired method outputs. Five seeds describe full-pipeline stability and are not five independent clinical cohorts. Coverage is also reported by class and missingness stratum.

### 3.6 Missingness stress tests and sensitivity analyses

S0 is natural missingness. S1 and S2 additionally hide 10% and 30% of originally observed physiological values at test time. S3 hides the laboratory block (official columns 9–34). S4 is the external hospital with natural missingness. Training and calibration remain at S0; the same patients and masks are shared across methods; indicators and missingness fractions are recomputed after hiding. Stress tests are not causal models of missingness mechanisms.

Sensitivity analyses include a random forest on S0/S2, M=5/20 on S0, alpha=0.05 on the primary seed, and five test-imputation batches for three-state decision stability. These are secondary and do not replace the primary contrast.

### 3.7 Reproducibility and evidence chain

Each run is immutable and stores a manifest with source, data and split hashes. `scripts/make_figures.py` verifies the manifest and every artifact hash, refuses synthetic runs unless explicitly rendered as watermarked QA, and refuses clinical runs without a C/E-signed acceptance record matching the run’s manifest. Every manuscript number maps to `paper/source_index.md` and a generated table or figure-data CSV. No result number is typed by hand.

---

## 4 Experimental Setup

Data version, cohort size, positive counts and missingness summaries: `[RESULT:S-001]`, `[RESULT:S-009]`. Run identifier, config hash, environment and compute time: `[RESULT:S-012]` and the accepted run manifest. The primary analysis uses seed 2026, logistic regression, M=10 and alpha=0.10; seeds 2027–2030 are stability checks. Synthetic runs and the B candidate matrix are not used as paper results.

---

## 5 Results

> All subsections are placeholders. Do not insert candidate-run or synthetic numbers. Each subsection is written only after the accepted run and C’s independent audit.

### 5.1 Cohort and missingness (Table 1, Figure 1)

`[RESULT:S-001]`, `[RESULT:S-009]`. Report per-site sample size, positive counts, base rate, exclusions and feature missingness. Confirm that no patient appears in more than one partition, hospital identity is correct, and the 6-hour label restoration and 12/24-hour boundaries were checked.

### 5.2 Primary selective risk (Table 2, Table 2b, Figure 2)

`[RESULT:S-002]`, `[RESULT:S-003]`, `[RESULT:S-011]`. Report B0–B6 selective risk, realized acceptance, dangerous misses, residual risk, coverage, pool size and capacity shortfall. The primary contrast is `[RESULT:S-003]`; the conditional increment is `[RESULT:S-004]`. A negative difference means lower selective risk for B4 (or B6). If the singleton pool is below the target, report the shortfall and do not interpret ranking differences.

### 5.3 Missingness and external stress tests (Table 3, Figure 3)

`[RESULT:S-005]`. Report B4−B2 and B6−B5 across S0–S4, with mean and min–max over seeds. S4 is external and is not pooled with internal scenarios. Report any direction reversal or interval crossing zero.

### 5.4 Coverage (Table 4, Figure 4)

`[RESULT:S-006]`. Report original-set marginal coverage overall and by class and missingness stratum, with empty sets in the denominator. State explicitly that marginal coverage does not guarantee conditional safety for the accepted subset.

### 5.5 Disagreement diagnostics (Figure 5)

`[RESULT:S-007]`. Report error rate by disagreement quintile among singleton predictions and the patient-level scatter of `p_mean` versus `D`. This is descriptive; quintiles are not a decision rule, and small bins carry wide intervals.

### 5.6 Test-time stability (Table 5, Figure 6)

`[RESULT:S-008]`. Report three-state disagreement across five test-imputation batches for batch and frozen allocation. Separate batch-composition effects from patient-level sensitivity.

### 5.7 Sensitivity analyses (Supplementary Tables S1–S3)

`[RESULT:S-010]`. Report random forest, M=5/20 and alpha=0.05 results with intervals and denominators. Do not promote a sensitivity result to the primary claim.

---

## 6 Discussion

`[RESULT:S-011]` The discussion will state whether disagreement adds information beyond confidence and missingness at the same capacity, with the effect size and interval rather than a significance-only claim. It will distinguish completion sensitivity from model confidence and data quantity, and it will describe conditions in which disagreement may not help: low disagreement can still accompany error, and high disagreement can reflect irreducible noise or unstable imputation rather than a recoverable decision signal.

The capacity-constrained design reflects a batch allocation problem, not a fixed per-patient deployment rule. Realized acceptance and dangerous misses matter as much as selective risk. The external hospital and missingness stress tests are empirical; standard conformal marginal coverage does not extend to the accepted subset or to shifted populations.

Limitations include: one public retrospective dataset; two hospitals; no prospective evaluation; complete 24-hour follow-up induces a restricted cohort; the 6-hour label restoration and first-observation-positive handling limit onset precision; MI is a practical stochastic procedure, not a true posterior; the analysis uses a single tabular predictor family with a random-forest robustness check; capacity evaluation is batch-level; missingness scenarios are stress tests, not causal mechanisms; and event counts may limit precision and the availability of B5/B6. `[CLAIM-CHECK: C-001/C-003]`

We do not claim clinical benefit, deployment readiness, cost-effectiveness, or that disagreement is universally superior to confidence or missingness.

---

## 7 Conclusion

`[RESULT:S-011]` The conclusion will answer the prespecified question for the accepted run, including a null result if applicable. It will state one requirement for future work—prospective evaluation with prespecified capacity and per-site calibration—without introducing new numbers.

---

## Statements

**Reproducibility.** Code, configurations, tests and run manifests are versioned; large artifacts are distributed with SHA256 checks. Figures and tables are regenerated by `scripts/make_figures.py` from an immutable run and a signed acceptance record.

**Data availability.** PhysioNet 2019 data are available under the dataset’s access terms; no raw patient data are included in the repository.

**Ethics.** Secondary analysis of de-identified public data under the dataset’s data use agreement.

**AI use disclosure.** Follow the workshop rule verified by C-002; disclose assistance if required.

**Author contributions.** A: data and labels; B: methods and experiments; C: literature and independent audit; D: figures and manuscript integration; E: coordination and integrity. The corresponding author is confirmed by the group.

---

## Internal draft checklist (not part of the manuscript)

| Item | Status |
|---|---|
| Abstract structure and placeholders | Drafted |
| Introduction | Drafted without clinical numbers |
| Related Work | Drafted with six verified citations; R5 excluded |
| Methods | Drafted from protocol/B material; no results |
| Results | Placeholder headings only |
| Discussion/Limitations | Drafted; final claims pending accepted run |
| References | `paper/references.bib` (6 verified entries) |
| Citation claims | R1/R3 claim-level details still require full-text checks |
| Figures/tables | `paper/figure_list.md`; generated only after acceptance |
| Accepted clinical run | **MISSING** |
| C/E acceptance record | **MISSING** |
| C-002 verified citation list | **PARTIAL** (metadata verified; R5 missing; R1/R3 claim details pending) |

**Do not submit this draft.** Replace every `[RESULT:S-xxx]` only from the accepted run, update `paper/source_index.md`, and obtain C’s numeric/citation check and the C/E acceptance record first.
