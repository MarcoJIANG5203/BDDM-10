# EXP-01 cohort eligibility, event attrition and precision

## Material Passport

- Origin skill and mode — academic-research-suite, experiment-agent validation
- Date — 2026-11-10, Asia/Hong_Kong
- Analysis ID — `exp01-a-20261110-r1`
- Verification — A producer raw replay and frozen identity checks passed. C independent review and E's G1 disposition are pending.
- Inputs — registered source `a-v1-full-source-20261104-r1` and frozen data `a-data-v1-20261104-r1`, protocol v1. [Input and output hashes](manifest.json)
- Context — feasibility analysis after both sites' v1 results had been seen. Primary clinical input remains the published v1 cohort. [Experiment plan](../../../collaboration/EXPERIMENT_PLAN_2026-11-08.md)

## Cohort and event flow

The replay checked all 40,336 files against the source inventory and record audit. All 24,095 included labels and 867,420 feature cells agreed with the released cohort. Eight formal freeze identities passed. A shift of six ICU hours was applied only after a recorded zero-to-one label transition. "Target transition" below denotes a recovered onset proxy in (12,24]. A recovered hour within the released record still represents a dataset label proxy. [PhysioNet Challenge 2019 data and label definition](https://physionet.org/content/challenge-2019/1.0.0/)

| Site | Source records | Raw target transitions | Lost at start-hour rule | Lost at follow-up rule | Frozen records | Frozen target events | Event retention |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 20,336 | 334 | 93 | 184 | 10,174 | 57 | 17.1% |
| B | 20,000 | 152 | 9 | 105 | 13,921 | 38 | 25.0% |
| Total | 40,336 | 486 | 102 | 289 | 24,095 | 95 | 19.5% |

The start-hour rule excludes 7,497 A and 1,296 B records. The next rule excludes 2,665 A and 4,783 B records with an observed end before hour 24. These counts are sequential and mutually exclusive. Among the 102 target transitions assigned to the start-hour rule, 23 reach hour 24 and 79 also end earlier. All 391 lost target transitions have hour 12 in their record. The recovered onset is within the recorded hours for 390 of them. The remaining one is a B-site short-follow-up case. A recovered onset after the end of follow-up is flagged separately. [Step counts and duration quantiles](cohort_flow.csv) · [First exclusion reasons](first_exclusion_reasons.csv) · [Target event observability](target_event_observability.csv)

The raw replay found zero invalid hourly records under the v1 parser, which checks consecutive integer ICU hours, duplicate hours and monotone binary labels. Later starting records have missing early time coverage. Within recorded hours, missing measurements are represented separately by feature values. The median record length was 37 hours in each site's late-start group and 19 hours in each site's short-follow-up group. The retained group had median lengths of 43 hours at A and 42 hours at B. [Feature missingness](feature_missingness.csv)

## Time boundaries and negative observation support

The 426 records positive at their first observation (203 A and 223 B) provide no exact recoverable onset. Another 283 records have a recoverable proxy at or before hour 12. Earlier eligibility filters already remove these categories, so the sequential counts at those later filters are zero. Their diagnostic counts remain visible in the observation table. [Observation support](label_observation_support.csv)

| Recovered ICU hour | Raw proxy count | Frozen result |
|---|---:|---|
| 12 | 60 | 0 retained |
| 13 | 46 | 0 retained because of earlier eligibility rules |
| 24 | 36 | 26 retained as target positives |
| 25 | 23 | 17 retained as window negatives |

The synthetic boundary tests exercise hours 12, 13, 24 and 25 on otherwise eligible records. The hour 13 rule includes a positive under that fixture even though none of the actual hour 13 cases survive the earlier eligibility filters. For the 24,000 frozen window negatives, all have full hours 1 through 24. Of these, 22,727 have no positive label in the released record and 1,273 have a recovered onset proxy after hour 24. This is follow-up evidence for the protocol's window outcome. [Boundary counts](boundary_hours.csv)

## Distinct patient IDs and precision budget

| Role, seed 2026 | Distinct IDs | Positive IDs | Positive prevalence | 95% Wilson planning width at p = 0.50 | At p = 0.90 |
|---|---:|---:|---:|---:|---:|
| Train | 6,104 | 34 | 0.557% | 31.9 pp | 20.8 pp |
| Selection | 1,018 | 6 | 0.589% | 62.5 pp | 48.8 pp |
| Calibration | 1,527 | 9 | 0.589% | 54.7 pp | 40.6 pp |
| Internal test | 1,525 | 8 | 0.525% | 57.0 pp | 42.9 pp |
| External test | 13,921 | 38 | 0.273% | 30.3 pp | 19.6 pp |

Each seed assigns every frozen ID exactly once. The five internal test memberships contain 30 distinct positive IDs in their union, with repeated membership and different fitted models. The external evaluation reuses the same 38 positive IDs. The two sites together contain 95 distinct positive source IDs. PhysioNet documents one file per subject. Released identifiers support uniqueness checks within this source, and cross-system linkage is unavailable. [Per-seed counts](split_events.csv) · [Unique IDs across seeds](unique_ids_across_seeds.csv)

The planning widths treat a single positive-class rate as a binomial proportion with independent patient outcomes and a fixed rule. The assumed rates are illustrative. They do not estimate uncertainty for model training, rule selection, calibrating a threshold, or a paired difference. Under this budget, a full width of at most 20 pp requires 93 independent positive events at p = 0.50 or 37 at p = 0.90. A full width of 10 pp requires 381 or 141 events respectively. An illustrative practical difference of 10 pp in a positive-class rate needs a paired design and decision threshold agreed with C/E. One positive event changes the internal estimate by 12.5 pp. A 9-event class-specific calibration set offers steps of 1/10 in its rank fraction. [Planning table](event_precision_budget.csv)

- **Positive coverage and false releases.** Positive coverage and false release proportions are computable on each fixed evaluation cohort. Historical MI positive coverage was 0/8 internally and 0/38 externally at seed 2026, first batch and alpha 0.10. Exact two-sided 95% binomial intervals are 0–36.9% and 0–9.25% respectively under the fixed-rule binomial model. Coverage and false releases have different numerators. [Coverage intervals](historical_positive_coverage_intervals.csv)
- **Overall selective risk and capacity.** Observed counts and paired risk differences are estimable on v1. The historical batch comparison at 60% for B4 minus B2 gives +0.109 pp internally with interval 0 to +0.328 pp, and −0.036 pp externally with interval −0.108 to +0.036 pp. These 1,000-resample widths are planning context for the existing rule only. An illustrative 1 pp practical difference is proposed for discussion. A prospective width for a revised comparison depends on jointly selected patients, the distribution of paired errors and the capacity rule. C should use paired patient-level simulation or bootstrap for that design and check sparse-error or degenerate resamples. [Historical precision](historical_selective_risk_precision.csv)
- **Conditional gain from B5/B6.** The previous selection run contains 6 errors and 1,012 correct predictions against the required 20 of each. The selection set's 6 target-positive labels and the 6 observed model errors are different counts. A new conditional gain estimate needs enough independent errors and correct cases. [Historical method status](../../clinical-v1/20261105T055420_02d05b15/method_status.csv)

## A recommendation for G1

Keep v1 as a descriptive benchmark for how its fixed rules affect eligible-patient counts, coverage and processing capacity. The eligibility and label replay is reproducible. The observed internal event count limits a claim about precise positive coverage, and the selection errors limit a conditional-gain comparison. The protocol reference counts of 200 positive events per site and 50 for the internal test are both unmet. E can use this audit to record a limited G1 scope after C reviews the inputs and agrees the precision budget.

The 288 short-follow-up transitions whose recovered onset falls within their released hours are a concrete reason to consider a future task focused on event observability at the hour 12 landmark. Such a design would need a clinically justified treatment of early discharge, death and incomplete observation and a matching definition for controls. A label shift alone cannot resolve observation after the last record. The data also show 102 target transitions with late-starting covariate history. A candidate accepting them would define a different input observation policy. Any such candidate needs a separately agreed protocol and source of independent confirmation. This audit uses only the existing v1 task.

## Validation scope

The 11-item ARS check was applied to the audit. Site-specific results address aggregation and base-rate concerns. Patient IDs are the counting unit. Eligibility-related selection, possible collider effects and survivorship restrict interpretation to the included population. Regression-to-the-mean and multiple-testing claims are outside this descriptive audit. The historical results had already informed the plan, so the analyses are exploratory and the report avoids causal or reverse-causal claims. No significance tests were used to choose a task.
