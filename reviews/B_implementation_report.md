# B implementation report — 2026-11-02

Status: DONE for implementation and synthetic verification. Clinical experiments have NOT run; A has not delivered cohort, audited temporal labels or official splits.

## Scope and files

Read `T1_统一实验说明_v1.md`, `T1_技术交接约定.md`, `reviews/B_implementation_brief.md` and existing implementation plan before implementing. Added src, scripts, configs, tests, requirements and synthetic results; did not edit original root research/Chinese documents, initialize Git or commit. No implementation agents were delegated. Applied test-driven-development and verification-before-completion skills.

- `src/data.py`: official 34 physiological/lab names and Age/Gender whitelist; strict role/ID/site/schema checks; read-only CSV/Parquet loader and basic A audit consistency checks.
- `src/imputation.py`: train-only BayesianRidge IterativeImputer, posterior fitting, median initialization, exactly 10 rounds; independently seeded conditional Gaussian draws, final missing-only clipping, all 36 indicators, train-only all-missing numerical removal, train demographic rules.
- `src/models.py`: LR selection C=.1/1/10 by selection AUPRC, smaller-C ties; weighted M-copy training and fixed RF. One median B0 copy, not duplicated RF rows. B0 uses shared selected LR C and separate calibration.
- `src/conformal.py`, `selection.py`, `scenarios.py`, `metrics.py`: finite-sample conformal; singleton pool; exact capacity and frozen score/hash cutoffs; risk models; ID-stable scenarios; complete-denominator metrics, strata and paired patient bootstrap.
- `src/experiment.py`: all B0–B6/S0–S4, seeds, sensitivity flags, 5-batch stability, streaming patient/p_m/seed outputs, model persistence, failure manifest, hashes and environment.
- CLI: `scripts/create_demo_data.py`, `scripts/run_experiments.py`; configs `protocol_v1.yaml` and generated `demo.yaml`.

## Test-first evidence and verification

Initial test command `python -m pytest -q tests/test_protocol.py`: 8 failed because required behavior modules did not exist; exact evidence `reviews/B_RED.log`. Tests preceded first production implementation. Initial full pipeline then passed 8 tests (`B_GREEN_initial.log`).

Review-driven RED/GREEN cycles were also recorded:

- `B_RED_review.log`: explicit posterior-chain fitting test failed with sample_posterior=False; corrected to True and median initial strategy. Blank-ID regression was already caught with pandas3 string missing semantics, and loader now explicitly checks missing IDs before conversion.
- `B_RED_B0.log`: B0 output erroneously identified as M10; corrected to real M1 training/prediction/export. Median standard deviation is explicitly 0 because there is one deterministic draw.
- `B_RED_singleton.log`: empty/double sets had arbitrary y_pred; corrected to -1, only singleton predictions are 0/1.
- `B_RED_audit.log`: inconsistent audit included count was accepted; loader now rejects it.
- Initial reproducibility assertion detected BLAS row-order floating point differences; transform now sorts by patient ID internally and restores original row order. Exact array equality now passes.

Final command `python -m pytest -q`: **17 passed in 26.23s**, `reviews/B_GREEN.log`; this includes the parent's two independent hand-calculation checks in `tests/test_independent_audit.py`. Additional tests cover missing-only observed-value preservation, all-missing indicators, different-batch variation, mask semantics, S3's 26 lab columns, split/schema leakage, zero denominators, bootstrap duplication, M weights, unavailable risk learners, all-scenario pipeline, blank IDs, posterior chain parameters, Parquet round-trip, failure retaining streamed evidence, and test-label mutation leaving probabilities/sets/acceptance unchanged.

Installed pyarrow26.0.0 and actually tested Parquet input; install log `reviews/B_pyarrow_install.log`. `requirements-lock.txt` contains 18 precise project-related dependencies, Python version is recorded per manifest. The optional full installed-environment snapshot is `reviews/environment_full.txt`; it is not the install requirements.

## Authoritative final runs

Commands:

```powershell
python scripts/create_demo_data.py --output data/synthetic
python scripts/run_experiments.py --config configs/demo.yaml
python scripts/run_experiments.py --config configs/demo.yaml --rf --m-sensitivity --alpha-sensitivity
python scripts/run_experiments.py --config configs/protocol_v1.yaml
```

Synthetic data: 800 hospital A patients and 120 hospital B patients, A roles 60/10/15/15%, noisy binary outcomes and synthetic audit only. Selection has 80 patients. M10 and 10 posterior chain rounds are preserved; demo bootstrap uses100 rather than formal1000, and demo uses only2026 rather than formal5 seeds.

- Final main run: `results/synthetic/20261102T062332_98484fc5`, log `reviews/B_demo_main_final.log`, manifest completed. All7 methods available; all5 scenarios present. 34,560 patient-method rows, 11,880 p_m rows, 19,280 seed rows, 320 pairwise stability rows. 60 bootstrap rows×100 resamples=6,000 valid/0 invalid. The naturally noisy LR selection had36 errors/44 correct, allowing real B5/B6 fitting. Earlier same-code main demonstration counted762 clipped final missing draws, proving clipping diagnostics are not a manufactured zero.
- Final supplement run: `results/synthetic/20261102T062332_a3f5dbb9`, log `reviews/B_demo_supplements_final.log`, completed in29.82s. All7 methods available for LR M5/10/20 alpha.1, LR M10 alpha.05, RF M10 alpha.1. RF runs S0/S2; M variants only2026/LR/S0; alpha.05 all5 core scenarios for2026/LR/M10. Five test batches apply to primary LR/M10/alpha.1 S0, as specified. Current source hashes were compared against final run manifest and all matched.
- Formal command intentionally failed because `data/processed/cohort.parquet` does not exist: `results/clinical/20261102T062332_bb913b46/manifest.json` has run_status failed, with error.log; console `reviews/B_clinical_expected_failure.log`. This is evidence of correct fail-closed behavior, not a clinical study result.
- Local trusted joblib reload reproduced primary S0 probabilities and frozen B4 decisions: `reviews/B_reload.log`, replay helper `reviews/_verify_reload.py`.

Earlier completed synthetic runs are retained rather than overwritten; the final run IDs above are authoritative.

## Exact API and semantics

`data.load_cohort(config, seed) -> (frame indexed by patient_id, splits, audit)`. `validate_cohort(frame,splits,features)` rejects overlap, omissions, unknown/global duplicate IDs and wrong sites. Fixed `FEATURES` list is exported. Loader only selects these features for algorithms; additional dataframe metadata cannot enter the model. Clinical input audit must contain protocol_version=v1, feature_window_end=12, outcome_window="(12,24]", label_shift_hours=6, nonempty data_version, site_meanings with exactly A/B, and exclusion_counts containing nonnegative integer input/included/excluded; included equals cohort rows and input equals included+excluded. Only A/C can establish correctness of original hourly windows and labels.

`PosteriorImputer(rounds=10,split_seed=2026).fit(X_train)` accepts no labels. `transform(X,ids,M=10,role='test',batch=0,posterior=True) -> (draws[M,N,P],per-column clipping diagnostics,seed rows)`. Numerical output columns are `output_columns_`, followed by36 original missing indicators; dropped train-all-missing physiology appears in `dropped_columns_`. Age/Gender fully missing in train is an error. Observed values are always preserved even outside train bounds. Only final missing fills are clipped; diagnostic denominator is final missing fills across draws, not chain intermediate updates. A dropped column has no numerical fills and its clipping fraction is null.

Each per-patient stream uses uint32 first4 SHA256 bytes, big endian, of JSON `[split_seed,role,str(patient_id),batch,draw]`; seed rows and role/context are exported. Scenarios intentionally share streams for a given patient/role/batch/draw; mask generation separately hashes seed/mask/scenario/ID. Patient-ID sorting ensures order-independent floating-point execution, no per-patient imputer deepcopy. All methods share MI draws and one fitted classifier. This is practical conditional Gaussian posterior sampling with final clipping, not a validated true clinical missing-data posterior.

`models.fit_classifier(draws,y,C=1,model='LR',seed=2026)`, `choose_classifier(train,y_train,selection,y_selection,seed)`, `predict_draws(model,draws)` return p_m/p_mean/sample-p_std/flip. Weights1/M sum to one per patient. Scaling fits only training copies. Median B0 is deterministic M1; its p_std=0 and flip=False.

`conformal.calibrate(p,y,alpha=.1)` uses ceil((n+1)*(1-alpha)), inf when out of bounds. `prediction_sets(p,q)` returns N×2 booleans. `singleton_predictions(sets)` returns pool and prediction, with -1 for non-singletons. Coverage includes every patient.

`selection.batch_accept(ids,pool,score,capacity,copy_keys=None)` uses floor(c*N), cap by pool count; low score/hash ID order and per-copy bootstrap tie key. `fit_threshold` records threshold and hash cutoff, using final calibration q on selection to define the pool (this dependency is explicitly recorded); `frozen_accept` never retunes on test. Entire candidate pool is accepted when selection pool is insufficient, with inf threshold. Risk learners standardize all selection patients and use C1 LR to predict base .5-threshold errors, requiring at least20 errors and20 correct; otherwise status table has unavailable reason and there are no invented patient predictions.

`scenarios.apply_scenario(X,ids,scenario,seed)` returns masked input, hidden mask, original observed/hidden/final missing statistics including per-column counts and hash. S1/S2 hide Bernoulli .1/.3 of originally observed physiology only; S3 hides official columns9–34; Age/Gender and original NaNs are untouched.

`metrics.evaluate(y,p,pred,sets,accepted)`, `coverage_strata(...)`, `paired_bootstrap(ids,y,pred,pool,score_a,score_b,capacity,repetitions=1000,seed=2026,fixed_a=None,fixed_b=None)`. Zero denominators are NaN (CSV empty). Bootstrap resamples patients jointly, then recomputes K and ordering with duplicate copies occupying separate positions. Frozen mode bootstraps saved acceptance states and records capacity_recomputed=False. Differences are B4−B2 and B6−B5; valid/invalid counts are saved. Missing strata are <=1/3, (1/3,2/3], (2/3,1].

`experiment.default_config()`, `create_demo(output,n_a=800,n_b=120)`, `run(config,rf=False,m_sensitivity=False,alpha_sensitivity=False) -> Path`.

## Output interpretation and joining

Main files: patient_predictions.csv, p_m.csv, metrics.csv, bootstrap_differences.csv, coverage_strata.csv, stability.csv, method_status.csv, thresholds.csv, model_parameters.json, clipping.json, masks.json, timing.json, imputation_seeds.csv, masks/*.csv, models/*.joblib, config.yaml, manifest.json, warnings.log/error.log. Config/source/data/audit/split and saved artifact SHA256 are recorded; timestamps have UTC and Beijing, with total elapsed seconds. Unique directories never overwrite completed runs. Patient/p_m/seed outputs stream to disk, avoiding all-run accumulation and retaining partial evidence on failure.

Patient to p_m joining keys include run_id, split_seed, scenario, model, **source_M**, M, alpha, imputation_batch, predictor, patient_id; p_m additionally has draw. `source_M` identifies the enclosing MI task (5/10/20); B0's actual M is1 even when source_M is10. B1–B6 predictor isMI; B0 predictor ismedian. Method/selection_mode/target_acceptance exist on the patient-method side, allowing all methods to reuse identical MI p_m. Non-singleton y_pred=-1 is undefined, not a positive/negative prediction. B0/B1 accept the whole singleton pool and have null target_acceptance, selection_mode=batch. Only B2–B6 have capacity and frozen evaluations. Selection/batch acceptance never receives test labels; y_true is merged only in the evaluation/export block.

## Remaining dependencies and limitations

A must deliver original-data-derived cohort,5 official split files and cohort_audit.json with data version and independently checked hourly labels/windows. No synthetic outcome/window declaration proves real temporal validity. Before clinical work A/C must verify onset restoration +6h,12/24h boundaries, inclusion/exclusion and positive event counts. The loader checks declarations and cohort consistency only.

Synthetic data exercise software behavior, availability and artifact reloading; they provide no clinical effectiveness, calibration, safety or D incremental-value evidence. Formal cohorts may make B5/B6 unavailable or candidate pools too small for target capacity; this is reported honestly. Fixed deployment thresholds inherit their documented selection-pool dependence on final q; coverage after selection or under missingness/site shift has no automatic guarantee. Formal runtime and disk usage depend on real cohort size and missingness; streaming removes accumulated patient-table memory but the train M-copy tensor and model fitting remain in memory. Persisted joblib files must only be loaded from trusted local runs. No submission or real-data experiment was performed.

## Final independent-review boundary fix (source refrozen)

The independent reviewer identified one minor edge case: all34 physiological columns entirely missing during training should delete all34 numerical columns while retaining Age/Gender and36 missingness indicators. Initial code rejected this case. Added `test_all_physiology_missing_train_keeps_demographics_and_original_indicators` first; RED command `python -m pytest -q tests/test_protocol.py -k all_physiology` failed on that explicit ValueError (`reviews/B_RED_all_missing.log`).

Limited production change to `src/imputation.py`: an empty active physiological schema now sets chain_=None and empty minimum_/maximum_/median_ arrays; posterior sequence sampling is skipped. Transform returns shape(M,N,38), with train-filled demographics and all36 original-input missing indicators. Later observed physiological values only change their indicator; they never reintroduce a numerical feature omitted by training. The hand-built test checks exact values, shape, dropped flags, zero fill counts, null clip fractions and consistency across all5 data roles.

Final verification after this fix: `python -m pytest -q tests/test_protocol.py tests/test_independent_audit.py` → **18 passed in18.96s**, log `reviews/B_GREEN_all_missing.log`. No other production functionality changed. Source frozen again. The previously listed synthetic run manifests accurately identify the preceding source hashes; the root agent is responsible for running the requested final5-seed/1000-bootstrap synthetic acceptance matrix and supplements against this boundary-fixed source. No clinical data or results were introduced.
