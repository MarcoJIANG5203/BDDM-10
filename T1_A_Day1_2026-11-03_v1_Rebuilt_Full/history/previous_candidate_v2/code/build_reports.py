"""Build English handover documents from actual pipeline outputs."""
import csv
import json
from pathlib import Path
import platform
import importlib.metadata

ROOT=Path(__file__).resolve().parents[1]

def save(name,text): (ROOT/name).write_text(text.strip()+'\n',encoding='utf-8')
def table(rows,cols):
    return '| '+' | '.join(cols)+' |\n| '+' | '.join('---' for _ in cols)+' |\n'+'\n'.join('| '+' | '.join(str(r[c]) for c in cols)+' |' for r in rows)

def main():
 s=json.loads((ROOT/'reports/summary.json').read_text())
 ds=json.loads((ROOT/'sources/download_status.json').read_text())
 assert ds['downloaded_verified_files']==40336 and not ds['failures']
 scopes={r['scope']:r for r in s['cohorts']}
 a,b=scopes['site_A'],scopes['site_B']
 flow=table(s['flow'],['site','stage','n_records'])
 counts=table([{**r,'positive_fraction':f"{r['positive_fraction']:.6f}"} for r in s['cohorts']],['scope','n_records','positive','negative','positive_fraction'])
 feasibility=table(s['endpoint_feasibility'],['site','known_transition_onsets_12_24_before_other_filters','retained_positive','known_positive_excluded_for_followup_24h','known_positive_excluded_for_other_reasons'])
 save('00_START_HERE.md',f'''
# T1 — A Day-One Data Handover

Date: 3 November 2026 (Hong Kong / Beijing time, UTC+08:00). Deliverable language: English.

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run (data acquisition and cohort preparation)
- Origin Date: 2026-11-03
- Verification Status: UNVERIFIED
- Version Label: T1_A_day1_candidate_v2

The ARS status above means that an independent full reproducibility re-run has not been completed. Actual downloads, numerical checks and synthetic edge-case tests are documented below; this status is not a claim that the raw source is unknown.

## What has actually been completed

- Downloaded **all 40,336 public records** directly from the official PhysioNet Open S3 bucket documented on the [versioned dataset page](https://physionet.org/content/challenge-2019/1.0.0/).
- Verified every clinical file against its official S3 object size and single-part ETag/MD5. Recorded a local SHA-256 for every file. Preserved original file bytes inside local ZIP containers.
- Built the eligibility audit, patient-level candidate cohort, 37-column input matrix, missing-value mask, observation counts, and reproducible split manifest.
- Calculated actual exclusions, target positives/negatives, hourly missingness, and aggregate-feature missingness.
- Tested 15 clinically relevant boundary/leakage cases; checked 12 full-cohort invariants. Saved source metadata, license, English accepted manuscript, and citations with the dataset/article years separated.

## Actual counts under candidate protocol v2

{counts}

Positive fraction is positive / n_records. These are derived study counts, not numbers copied from the source-release description.

The source release contains A=20,336 and B=20,000 files. The numbers with any positive label anywhere in the full record are A={s['source_ever_positive_counts']['A']} and B={s['source_ever_positive_counts']['B']}. Those whole-record counts are **not** the 12–24-hour target counts.

## Open these files in order

1. [01_PROTOCOL_AND_RESULTS.md](01_PROTOCOL_AND_RESULTS.md): exact candidate rules, exclusions, counts, and limitations.
2. [02_HANDOVER_TO_B.md](02_HANDOVER_TO_B.md): data files, safe input columns, and reproducible commands.
3. [03_C_E_REVIEW_AND_DAILY_UPDATE.md](03_C_E_REVIEW_AND_DAILY_UPDATE.md): review items, unresolved group decisions, and an English progress update.
4. [sources/SOURCE_REGISTER.md](sources/SOURCE_REGISTER.md): authoritative English sources, years, evidence scope and access notes.
5. [data/raw_field_dictionary.csv](data/raw_field_dictionary.csv) and [data/derived_field_dictionary.csv](data/derived_field_dictionary.csv): field meanings.

## What remains a group decision

The two group documents referenced in the supplied execution plan were not present in its directory. To keep work moving, this package implements a **candidate** definition and split, saved in [protocol_candidate_v2.json](protocol_candidate_v2.json). C has not signed off the labels; E has not confirmed the added study choices. No sign-off or message to teammates has been fabricated or sent.

The deliverable is ready for review and B's interface development. Formal rule freezing awaits C/E confirmation. Model training and the multiple-imputation/conformal/rejection experiments are later milestones and have not been run as part of today's data preparation.

**Material feasibility finding:** the candidate complete-24-hour rule retains only {a['positive']} A positives and {b['positive']} B positives. Review reports/endpoint_feasibility.csv before freezing the task. Main-study feasibility and precision are not established by the total record count.
''')
 save('01_PROTOCOL_AND_RESULTS.md',f'''
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

{flow}

Every input record appears in data/eligibility_audit_all_records.csv, including exclusions. Ineligible records receive split=excluded; no excluded record enters X_last12.csv.

### Time-axis correction and endpoint feasibility

Direct inspection found that {s['time_axis_start_after_1_counts']['A']} A records and {s['time_axis_start_after_1_counts']['B']} B records start after hour 1. All raw records passed the revised contiguous-integer-hour check. Candidate v2 uses actual ICULOS values, never re-labels row 1 as ICU hour 1, and records first_observed_hour, last_observed_hour and history_rows_observed. The initial stricter v1 snapshot was preserved internally; its numbers are superseded.

{feasibility}

The complete-24-hour rule excludes records with target-window label-derived onset proxies whose observation ends before hour24. Of these excluded records, A has {s['endpoint_feasibility'][0]['excluded_followup_with_proxy_after_last_observation']} and B has {s['endpoint_feasibility'][1]['excluded_followup_with_proxy_after_last_observation']} with the inferred proxy itself beyond the last observed hour; these must not be described as directly observed clinical events. C/E must decide whether the scientific estimand should instead retain ascertainable positive endpoints with shorter post-event follow-up while requiring horizon ascertainment for negatives, or use a censoring-aware design. Such a change requires a new version and reassessment of selection/censoring bias; no alternative was silently promoted because it increased positive counts. The current candidate must not be described as finalized or statistically adequate.

## Actual candidate split and target prevalence

{counts}

Within each A outcome class, sort by SHA256("20261103|record_id"). Allocate the first floor(0.6*n) records to train, the next floor(0.2*n) to calibration and the remainder to internal_test. Assign every eligible B record to external_test. The split manifest is deterministic and should be reused unchanged across all downstream strategies. No performance-dependent selection was used. If tuning is needed, perform it only within train, e.g. cross-validation; do not use conformal calibration or either test set for model/threshold selection.

## Predictor construction and missingness

Each retained record has 34 time-varying inputs plus Age, Gender and HospAdmTime. Each is the last nonmissing value observed during ICU hours 1–12; a feature stays missing if never observed in that window. No backward filling from later hours, outcome balancing, imputation, scaling, clipping, or normal-value substitution was performed. Raw values, including possible errors, remain in the source archives.

- `X_last12.csv`: 37 predictors plus record_id join key.
- `missing_mask37.csv`: 1=missing predictor; 0=observed predictor.
- `observed_counts34.csv`: observed hourly cells among 12 for each dynamic input.
- Feature missing fraction: missing predictors / 37.
- Hourly dynamic missing fraction: missing hourly cells / (12*34).

Actual mean feature missing fractions: A={a['mean_feature_missing_fraction']:.6f}, B={b['mean_feature_missing_fraction']:.6f}. Actual mean hourly dynamic missing fractions: A={a['mean_hourly_dynamic_missing_fraction']:.6f}, B={b['mean_hourly_dynamic_missing_fraction']:.6f}. Per-feature and per-split values are saved in reports/feature_missingness37.csv and reports/hourly_missingness34.csv.

Training-all-missing columns: **{', '.join(s['training_all_missing_features']) or 'none'}**. These columns cannot be learned by a training-only imputer. The master table retains all 37 columns; data/model_feature_columns.json identifies the recommended training-derived model subset. Apply that same subset to calibration and both test sets. Do not use B availability to choose inputs.

Unit1 and Unit2 are omitted as site-dependent administrative inputs; ICULOS is a fixed landmark rather than a model input. Label, future length of stay, onset time, site and split are metadata, never predictors. Aggregate last-value missingness differs from hourly missingness; the two measures must not be interchanged. Leading hours absent from the file and recorded NaN cells both count as unavailable for this denominator; history_rows_observed distinguishes absent leading rows. The current candidate operates on aggregated tabular features; imputing full hourly sequences would require an explicit protocol change and fresh version.

## Limits and downstream implications

- Requiring follow-up through hour 24 avoids silently treating early-ended records as full-horizon negatives, but selects patients with longer observed ICU stays. The resulting estimand is conditional on this cohort and is not all ICU admissions. An early-discharge/competing-event alternative would be a different protocol, not a silent relabeling.
- This fixed-landmark study differs from the original hourly early-warning challenge. Do not compare its metrics directly with official challenge leaderboard scores.
- The six-hour label correction does not establish exact clinical event timing; first-row positives are left-censored. The hourly boundary convention must be reported.
- Only original missingness was processed today. Extra random missingness and unavailable laboratory panels belong to the later experiments. Preserve this split and apply each scenario identically to competing strategies.
- External-site differences may invalidate exchangeability assumptions. No external finite-sample conformal coverage guarantee is claimed. Calibration and strategy selection must not fit on B.
- Extremely sparse features and possible unit/documentation inconsistencies require review before clinical range filters. In particular, documented FiO2 percent units coexist with fractional-looking raw values. No conversion was guessed. Raw documentation units are preserved as source metadata, not clinically validated units.
- Today supplies data and audit evidence; it supplies no evidence that prediction disagreement improves accuracy or that the method has clinical benefit. No inferential statistics, confidence intervals or model performance results were manufactured. Review the positive counts in calibration and internal_test before freezing the endpoint; these counts alone do not establish adequate statistical precision.
''')
 save('02_HANDOVER_TO_B.md','''
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
''')
 save('03_C_E_REVIEW_AND_DAILY_UPDATE.md',f'''
# C/E Review Items and Day-One Progress

Prepared 2026-11-03. No teammate message was sent. These are local review materials.

## Completed by the automated A work

All public training files were obtained from the official source. The candidate cohort, exclusions, label audit fields, missingness tables, and deterministic split manifest were generated from actual records. There are {a['n_records']} eligible A records ({a['positive']} positives) and {b['n_records']} eligible B records ({b['positive']} positives) under candidate v2. No training or main-method results are included.

## Review and decisions still required

| Owner | Review item | Current state |
| --- | --- | --- |
| E | Supply the missing unified experiment specification and technical handover agreement | Not found in the supplied plan's directory or scoped project search |
| C | Independently verify labels, hour-axis convention, onset +6, first-row positives, and sample audit records | Pending human review; automated boundary checks passed |
| C and E | Confirm the (12,24] hourly-onset proxy target and the last-observed-ICULOS >=24 rule for both classes | Candidate implemented; not signed off |
| C and E | Resolve loss of known positives under complete24h follow-up and assess calibration/test positive counts | Mandatory feasibility decision before main-study rule freezing; see reports/endpoint_feasibility.csv |
| E | Confirm adult filter, last-observed aggregation, selected 37-column table and train-only all-missing-column policy | Candidate implemented; not signed off |
| E | Confirm A development / B external, 60/20/20 split, seed and tuning within train | Candidate manifest saved; not signed off |
| A and B | Confirm the reader joins by record_id and respects missing-value and fit boundaries | Handover prepared; B integration not executed |

If a rule changes, preserve the previous version, create a new version, regenerate the cohort/split and rerun all affected downstream experiments. Do not manually edit outcomes or move individual records.

## Local automated and source checks

- All clinical bytes matched official S3 size / single-part ETag MD5. Local SHA-256 hashes were also recorded. The official root SHA256SUMS covers license/utility diagrams, not the clinical files; no official published clinical SHA-256 is claimed.
- Fifteen synthetic tests cover shifted-label boundaries, early/left-censored onset, 24-hour follow-up, gaps in the time axis and delayed-start records, nonadult exclusion, missingness, nonmonotone labels and future-predictor leakage.
- Twelve full-cohort invariants passed. These are software checks, not institutional or clinical adjudication.
- A separate audit rechecked all 40,336 archived files, independently recomputed predictors/labels/masks/counts for 64 selected cohort records, and independently recomputed every split assignment. See reports/independent_package_checks.json.
- A separate native agent read the source code and tests and reported no actionable implementation/leakage error under the stated protocol. It did not execute a second full pipeline run. No cross-model validation or human sign-off is claimed.
- Dataset 2019 and article 2020 were checked separately. Source record and bibliography are included. A Retraction Watch database screen and final conference reference-format audit were not performed.

## English daily update ready to copy

2026-11-03 | A | Completed official acquisition of 40,336 public ICU record files, file-integrity checks, candidate cohort preparation, exclusion counts, missingness summaries and deterministic split manifest. Candidate eligible cohort: A={a['n_records']} ({a['positive']} positive), B={b['n_records']} ({b['positive']} positive). | Files: T1_A_Day1_2026-11-03/00_START_HERE.md; data/; reports/; sources/. | Open issues: the referenced group specifications are unavailable; C label review and E confirmation of candidate protocol choices are pending. | Next: incorporate confirmed rules, version any changes, and connect the data interface with B toward the 6 November end-to-end milestone.
''')
 save('sources/SOURCE_REGISTER.md','''
# Source Register and Year Verification

Checked on 2026-11-03, Hong Kong time. All listed source documents are in English. Sources were chosen for provenance and relevance; original release/definition years are retained rather than replaced with recent-looking years.

| ID | Source / year or version | What it supports | Official channel |
| --- | --- | --- | --- |
| S1 | Reyna et al., dataset, 2019, v1.0.0; published 2019-08-05 | Release identity, schema, six-hour label offset, release counts, open access, license and documented S3 acquisition channel | [PhysioNet](https://physionet.org/content/challenge-2019/1.0.0/); [DOI](https://doi.org/10.13026/v64v-d857) |
| S2 | Reyna et al., journal article, 2020; Critical Care Medicine 48(2):210–217 | Hospital identities, collection context, record truncation and challenge methodology | [PubMed](https://pubmed.ncbi.nlm.nih.gov/31939789/); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6964870/); [publisher DOI](https://doi.org/10.1097/CCM.0000000000004145) |
| S3 | PhysioNet Challenges, evaluation-2019 repository; retrieved 2026-11-03 | Code uses first positive label index plus six for its onset reference; supports offset interpretation, not independent clinical adjudication | [Official GitHub code](https://github.com/physionetchallenges/evaluation-2019/blob/master/evaluate_sepsis_score.py) |
| S4 | Singer et al., 2016; JAMA 315(8):801–810 | Original Sepsis-3 clinical definition, not the newly constructed fixed-landmark endpoint | [PubMed](https://pubmed.ncbi.nlm.nih.gov/26903338/); [DOI](https://doi.org/10.1001/jama.2016.0287) |
| S5 | Dataset license, CC BY 4.0 | Attribution and source-data reuse terms | [Official license](https://physionet.org/files/challenge-2019/1.0.0/LICENSE.txt) |
| S6 | Official training directories and PhysioNet Open S3 objects; snapshot 2026-11-03 | Actual acquired records, inventory sizes and ETag integrity observations | [Training directory](https://physionet.org/files/challenge-2019/1.0.0/training/); [S3 inventory endpoint](https://physionet-open.s3.amazonaws.com/?list-type=2&prefix=challenge-2019%2F1.0.0%2Ftraining%2F) |

## Year discrepancy and correction

The dataset citation is **2019**. The accompanying journal article is **2020**, February issue, volume 48, issue 2, pages 210–217. The PhysioNet page contains an older line labeling the original article 2019, while PubMed, PMC issue metadata and the publisher identify the journal issue as 2020. The article's copyright year and a repository manuscript upload in 2019 must not replace its journal publication year. The title still contains “Challenge 2019”; that is the challenge name, not the journal publication year.

The stored journal_accepted_manuscript.pdf is the official repository manuscript asset uploaded in 2019, not a claim to be the final publisher-layout PDF. The bibliography identifies the final journal reference separately. S3 object LastModified dates are infrastructure metadata, not data collection or dataset publication years. The source article describes data accumulated over the preceding decade; exact per-record calendar dates are not supplied in these files and have not been invented.

## Local evidence and access limits

Source assets and retrieval receipts are stored beside this register. The source collector obtained the PhysioNet page, license, published root checksum file, official evaluation code, PubMed records and official accepted manuscript. PMC HTML returned HTTP 403 to the shell collector; its full text was read through the browsing tool, but no local full-text HTML copy is claimed. The accepted manuscript provides an additional official English asset.

The old archive-download link on the dataset page returned HTTP 404. Acquisition instead used the official, publicly documented PhysioNet Open S3 bucket. No third-party dataset mirror, Kaggle copy, unofficial Chinese translation, credentials or patient-data upload was used.

## Attribution and transformations

Source dataset: Reyna et al. (2019), PhysioNet, version 1.0.0, DOI 10.13026/v64v-d857, CC BY 4.0. See [license text](LICENSE.txt). The raw files retain their original bytes. The local ZIP containers, filtered candidate cohort, label-derived endpoint, aggregated inputs, masks, split manifest and reports are new transformations produced on 2026-11-03. Preserve this attribution and the transformation notice when sharing.

## Reference-ready records

[1] M. Reyna, C. Josef, R. Jeter, S. Shashikumar, B. Moody, M. B. Westover, A. Sharma, S. Nemati, and G. D. Clifford, “Early Prediction of Sepsis from Clinical Data: The PhysioNet/Computing in Cardiology Challenge 2019,” PhysioNet, version 1.0.0, 2019, doi: 10.13026/v64v-d857.

[2] M. A. Reyna, C. S. Josef, R. Jeter, S. P. Shashikumar, M. B. Westover, S. Nemati, G. D. Clifford, and A. Sharma, “Early Prediction of Sepsis From Clinical Data: The PhysioNet/Computing in Cardiology Challenge 2019,” Critical Care Medicine, vol. 48, no. 2, pp. 210–217, 2020, doi: 10.1097/CCM.0000000000004145.

[3] M. Singer et al., “The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3),” JAMA, vol. 315, no. 8, pp. 801–810, 2016, doi: 10.1001/jama.2016.0287.

Full author fields are preserved in references.bib. These are data-preparation references, not a comprehensive literature review. Final venue style, submission deadline and EI indexing have not been verified in this A data-preparation task; no publication or indexing guarantee is made.
''')
 save('sources/references.bib','''
@misc{reyna2019dataset,
 author={Reyna, Matthew and Josef, Chris and Jeter, Russell and Shashikumar, Supreeth and Moody, Benjamin and Westover, M. Brandon and Sharma, Ashish and Nemati, Shamim and Clifford, Gari D.},
 title={Early Prediction of Sepsis from Clinical Data: The {PhysioNet/Computing in Cardiology Challenge 2019}},
 year={2019}, month={aug}, publisher={PhysioNet}, note={Version 1.0.0},
 doi={10.13026/v64v-d857}, url={https://physionet.org/content/challenge-2019/1.0.0/}
}
@article{reyna2020challenge,
 author={Reyna, Matthew A. and Josef, Christopher S. and Jeter, Russell and Shashikumar, Supreeth P. and Westover, M. Brandon and Nemati, Shamim and Clifford, Gari D. and Sharma, Ashish},
 title={Early Prediction of Sepsis From Clinical Data: The {PhysioNet/Computing in Cardiology Challenge 2019}},
 journal={Critical Care Medicine}, year={2020}, volume={48}, number={2}, pages={210--217},
 doi={10.1097/CCM.0000000000004145}, url={https://pubmed.ncbi.nlm.nih.gov/31939789/}
}
@article{singer2016sepsis3,
 author={Singer, Mervyn and Deutschman, Clifford S. and Seymour, Christopher Warren and Shankar-Hari, Manu and Annane, Djillali and Bauer, Michael and Bellomo, Rinaldo and Bernard, Gordon R. and Chiche, Jean-Daniel and Coopersmith, Craig M. and Hotchkiss, Richard S. and Levy, Mitchell M. and Marshall, John C. and Martin, Greg S. and Opal, Steven M. and Rubenfeld, Gordon D. and van der Poll, Tom and Vincent, Jean-Louis and Angus, Derek C.},
 title={The Third International Consensus Definitions for Sepsis and Septic Shock ({Sepsis-3})},
 journal={JAMA}, year={2016}, volume={315}, number={8}, pages={801--810},
 doi={10.1001/jama.2016.0287}, url={https://pubmed.ncbi.nlm.nih.gov/26903338/}
}
''')
 try: requests_version=importlib.metadata.version('requests')
 except importlib.metadata.PackageNotFoundError: requests_version='not installed in current report-building environment'
 save('reports/execution_environment.json',json.dumps({'python':platform.python_version(),'platform':platform.platform(),'requests':requests_version,'preparation_dependencies':'Python standard library only','acquisition_dependencies':['requests'],'research_date_hong_kong':'2026-11-03'},indent=2))
 print('English handover documents generated from actual cohort outputs.')

if __name__=='__main__':main()
