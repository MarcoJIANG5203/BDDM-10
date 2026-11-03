> Full edition: all original raw/source assets are included; use the current root code/prepare_day1.py entry point. The underlying protocol-v1 scientific rules are unchanged.

# A-to-B Protocol-v1 Rebuild — 3 November 2026

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run and validate
- Protocol: v1, dated 2026-11-02
- Data version: a-clinical-protocol-v1-20261103-full-r1
- Verification Status: VERIFIED (computational reproducibility only; C/E acceptance pending)
- Delivery status: LOCAL PREPARED; not published, independently accepted, or frozen

## Conformance result

The previous candidate v2 is superseded for B's formal v1 input. This is a rebuild from original hourly records, not a rename of the old data. The full unified protocol was available in the cloned repository and was read before rebuilding. Its SHA-256, the B reader hash, and source repository commit are recorded in cohort_audit.json.

The rebuilt interface matches the supplied contract: one record per globally unique string patient_id; site A/B; y_true binary; exactly 36 ordered inputs; no HospAdmTime; missing values retained; five fixed mutually exclusive roles; seeds2026--2030. B creates missing indicators. No all-missing source feature is removed by A; B must apply its training-only policy while retaining indicators.

**Interface PASS does not mean formal scientific acceptance. Both hospital positive-count gates and the internal-test gate FAIL. C's independent human review and E's precision/freeze decision are pending. No clinical performance run was performed.**

## Data files

- data/processed/cohort.parquet: default input for the existing configs/protocol_v1.yaml.
- data/processed/cohort.csv: accepted alternate input; read patient_id as a string. Change only data_path in a copied config when using CSV.
- data/processed/cohort_audit.json: actual counts, missingness file links via hashes, protocol/data/code/source hashes, hospital meanings, and explicit pending reviews.
- splits/seed_2026.json through seed_2030.json: exact train/selection/calibration/test/external lists. B must not re-split.
- data/processed/record_audit.csv: all40,336 raw file decisions, time axis and label transition metadata.
- data/processed/excluded_records.csv: each excluded raw record, exactly one sequential reason.
- data/processed/feature_missingness.csv: all36 features, separately by hospital.
- data/processed/review_10_positive_10_negative.csv and review_cases/: 10 true target positives and10 negatives (five of each per site), with byte-preserved original raw evidence, checksums and pending C review. Programmatic checks are separate from manual attestation.

## Exact scientific rules and migration

1. Parse and validate hourly schema, positive-integer contiguous ICULOS and binary monotone labels. Do not repair abnormal time axes or labels by guessing.
2. Require the first recorded ICU hour to be1 and observation through24, with no missing hourly rows. This enforces the full protocol's hours1--24 rule. Delayed-start records are excluded, not padded into eligibility. This differs materially from the earlier permissive candidate.
3. Exclude first-observation-positive records without assigning an exact onset. For observed0-to-1 transitions use actual ICU hour+6; exclude onset<=12 and set y_true=1 iff12<onset<=24. These are dataset-defined onset proxies, not independent clinical adjudication.
4. Extract the last available observation at hours1--12 for the34 physiologic/laboratory fields and Age/Gender. Retain NaN. No future backfill, imputation, clipping, balancing or training. Do not add an age>=18 eligibility rule: it is not in the supplied formal v1 specification. Nonbinary observed input Gender is excluded and counted separately; missing Gender is accepted.
5. Within each A outcome class, begin with sorted IDs, shuffle using Python random.Random(seed), then apportion60/10/15/15 with largest remainders; ties follow train/selection/calibration/test order. Assign all retained B records to external. Rounding is explicit, not selected for performance. The same five seeds are retained even when counts are small.

Mappings: record_id becomes patient_id; outcome_12_24 becomes y_true; HospAdmTime is removed. Old manifests using60/20/20 or seed20261103 are not reused. This is a new data version aligned to the actual v1 rules; protocol_version was not merely changed to hide a different algorithm.

## Actual counts and precision gates

| Site | Raw records | Included | Positive | Required positive count | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| A | 20336 | 10174 | 57 | 200 | FAIL |
| B | 20000 | 13921 | 38 | 200 | FAIL |

Total input=40336; included=24095; excluded=16241. Counts are nonnegative integers and input=included+excluded. Sequential reasons: invalid hourly records=0; missing initial hours=8793; insufficient follow-up=7448; first-observation-positive=0; observed onset<=12=0; invalid input demographics=0. A zero in a later exclusion category is a true sequential count, not evidence that no such condition exists among records already excluded earlier.

| Role, seed2026 | Records | Positive |
| --- | ---: | ---: |
| train | 6104 | 34 |
| selection | 1018 | 6 |
| calibration | 1527 | 9 |
| test | 1525 | 8 |
| external | 13921 | 38 |

All five seeds have the same stratum sizes and different assignments. Internal test has8 positives, below the required50. Selection has6 positives and calibration9. The cohort meets the mechanical contract but must not be described as adequately powered or approved. The full protocol already states the complete-follow-up population restriction; any time-window/eligibility change to improve precision must be discussed and versioned by the group before freezing, not chosen from test performance. No endpoint was broadened automatically.

## Validation

- B's actual src/data.py load_cohort was invoked10 times: five seeds x Parquet/CSV; all passed. B's data.py/models.py were not modified.
- Independently checked all20 review cases against original raw hourly files, targets and36 last-observed inputs.
- Full repository suite:47 passed in42.36s (32 existing tests plus15 new A boundary/split cases). These include onset12/13/24/25 boundaries, left-censoring, delayed starts, short follow-up, missing demographics, future-value isolation, invalid hour/label sequences and five-seed splitting.
- Exact data hashes and source/code hashes are saved. See reviews/A_interface_validation.json, reviews/A_test_result.json and reviews/A_reproducibility.json.

## Rebuild / validate commands

Run from the existing repository with its requirements-lock.txt environment and the two original archives in physionet2019_original/:

```powershell
python code/prepare_day1.py
python scripts/verify_a_handover_v1.py
python -m pytest -q
```

The CSV patient_id must be read using dtype={'patient_id':str}. The Parquet file carries a string ID column. For matrix construction use the exact FEATURES whitelist in src/data.py, not every numeric column. B generates36 missing indicators.

## Sources and remaining review

Source dataset: [PhysioNet Challenge2019 v1.0.0](https://physionet.org/content/challenge-2019/1.0.0/), published2019, DOI10.13026/v64v-d857; source bytes preserved. Companion article: [Reyna et al., Critical Care Medicine48(2):210--217,2020](https://pubmed.ncbi.nlm.nih.gov/31939789/), DOI10.1097/CCM.0000000000004145. Retain CC BY4.0 attribution. Missing/erroneous raw measurements were preserved in the source release; no blanket clinical-cleanliness claim is made.

C must independently inspect the20 cases and boundary evidence and record their own acceptance; A owner review is also pending. E must resolve failed precision gates before freezing. B's passing interface test cannot replace these decisions. Released subject-file IDs do not establish cross-stay person deduplication. These are explicit remaining limits, not silently completed checks.

Per repository policy, processed clinical files and splits are bundled for Release distribution, not staged as ordinary Git data. The local bundle is prepared only; no new Release, remote commit or push was made in this rebuild. The previously uploaded raw-data commit is preserved.
