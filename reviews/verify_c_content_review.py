"""Recompute v1 content-review tables with the C-006 protocol implementation."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import subprocess
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd

from verify_c_formal_runs import batch_accept, frozen_accept, paired_bootstrap, stable_seed, tie_bytes


ROOT = Path(__file__).resolve().parents[1]
A_VERSION = "a-data-v1-20261104-r1"
B_VERSION = "b-clinical-v1-20261104-r1"
RUN = "20261105T055420_02d05b15"
SCENARIO_ROLES = {"S0": ("A", "test"), "S4": ("B", "external")}
METHODS = ("B2", "B4")
SEEDS = tuple(range(2026, 2031))
CAPACITY = 0.60
PREDICTION_CONTEXT = dict(protocol_version="v1", run_id=RUN, synthetic=False, model="LR",
                          M=10, source_M=10, alpha=0.10, imputation_batch=0)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def csv(path, **kwargs):
    return pd.read_csv(path, float_precision="round_trip", **kwargs)


def where(frame, **values):
    return frame.loc[frame[list(values)].eq(pd.Series(values)).all(axis=1)]


def same_rows(expected, actual, keys, name):
    left = pd.DataFrame(expected)
    right = pd.DataFrame(actual)
    check(not left.duplicated(keys).any() and not right.duplicated(keys).any(), f"{name}: duplicate key")
    pd.testing.assert_frame_equal(
        left.sort_values(keys).reset_index(drop=True), right[left.columns].sort_values(keys).reset_index(drop=True),
        check_dtype=False, check_exact=False, rtol=0, atol=1e-12, obj=name,
    )


def verify_sources(args):
    provenance = json.loads((args.package / "provenance.json").read_bytes())
    registry = json.loads((ROOT / "artifacts/registry.json").read_bytes())["bundles"]
    archive_digests = {A_VERSION: sha256(args.a_archive), B_VERSION: sha256(args.b_archive)}
    for version, actual in archive_digests.items():
        check(actual == registry[version]["sha256"] == provenance["archive_sha256"][version], version)

    freeze_path = ROOT / registry[A_VERSION]["freeze_record"]
    freeze = json.loads(freeze_path.read_bytes())
    frozen = {**freeze["split_sha256"], "data/processed/cohort.parquet": freeze["cohort_sha256"],
              "data/processed/cohort.csv": freeze["cohort_csv_sha256"],
              "data/processed/cohort_audit.json": freeze["delivery_audit_sha256"]}
    check(sha256(freeze_path) == provenance["freeze_record_sha256"]
          and frozen == provenance["frozen_member_sha256"], "Freeze identity")
    with ZipFile(args.a_archive) as archive:
        for name, expected in frozen.items():
            check(hashlib.sha256(archive.read(name)).hexdigest() == expected, name)
        cohort = pd.read_parquet(io.BytesIO(archive.read("data/processed/cohort.parquet")),
                                 columns=["patient_id", "site", "y_true"])
        split = {seed: json.loads(archive.read(f"splits/seed_{seed}.json")) for seed in SEEDS}
    cohort["patient_id"] = cohort.patient_id.astype(str)
    cohort = cohort.set_index("patient_id")
    check(cohort.index.is_unique, "Frozen cohort IDs")

    manifest_file = args.run_dir / "manifest.json"
    manifest = json.loads(manifest_file.read_bytes())
    check(manifest["run_id"] == RUN and manifest["synthetic"] is False
          and manifest["data_version"] == A_VERSION, "Run identity")
    check(manifest["data_sha256"] == frozen["data/processed/cohort.parquet"]
          and manifest["audit_sha256"] == frozen["data/processed/cohort_audit.json"]
          and {f"splits/seed_{seed}.json": value for seed, value in manifest["split_sha256"].items()}
          == freeze["split_sha256"], "Run frozen input binding")
    with ZipFile(args.b_archive) as archive:
        check(archive.read(f"results/clinical/{RUN}/manifest.json") == manifest_file.read_bytes(), "B archive manifest")
    acceptance_file = ROOT / "reviews/acceptance" / f"{RUN}.json"
    acceptance = json.loads(acceptance_file.read_bytes())
    check(sha256(manifest_file) == acceptance["manifest_sha256"] == provenance["manifest_sha256"]
          and sha256(acceptance_file) == provenance["acceptance_sha256"], "Existing acceptance binding")
    artifacts = {name.replace("\\", "/"): value for name, value in manifest["artifact_hashes"].items()}
    check(artifacts == provenance["verified_run_artifact_sha256"], "Producer artifact manifest binding")
    for name, expected in artifacts.items():
        check(sha256(args.run_dir / name) == expected, f"Run file {name}")
    generated = {path.name for path in args.package.iterdir() if path.suffix in (".csv", ".pdf", ".png")}
    check(generated == set(provenance["output_sha256"]), "Package artifact inventory")
    for name, expected in provenance["output_sha256"].items():
        check(sha256(args.package / name) == expected, f"Review output {name}")
    return cohort, split, provenance, archive_digests


def verify_background(folder, cohort, split, provenance):
    source = {}
    for ref, expected in provenance["pinned_source_sha256"].items():
        data = subprocess.check_output(["git", "show", ref], cwd=ROOT)
        check(hashlib.sha256(data).hexdigest() == expected, ref)
        source[ref.split(":", 1)[1]] = data

    audit_dir = "reports/experiment-strengthening/exp01-a-20261110-r1"
    audit = json.loads(source[f"{audit_dir}/manifest.json"])
    for name in ("cohort_flow.csv", "split_events.csv", "target_event_observability.csv"):
        check(hashlib.sha256(source[f"{audit_dir}/{name}"]).hexdigest() == audit["aggregate_sha256"][name], name)
    flow = csv(io.BytesIO(source[f"{audit_dir}/cohort_flow.csv"]))
    count_cols = ["n", "target_transition_proxy", "target_onset_within_released_hours", "target_onset_beyond_released_hours"]
    flow = flow[["site", "stage", *count_cols]].copy()
    for field, name in (("n", "excluded_at_stage"), ("target_transition_proxy", "excluded_proxy_at_stage")):
        flow[name] = -flow.groupby("site")[field].diff().fillna(0)
    total = flow.groupby("stage").sum(numeric_only=True).reset_index().assign(site="Total")
    same_rows(pd.concat([flow, total]), csv(folder / "cohort_flow.csv"), ["site", "stage"], "cohort flow")
    observability = csv(io.BytesIO(source[f"{audit_dir}/target_event_observability.csv"]))
    for site in ("A", "B"):
        site_flow = where(flow, site=site)
        observed = where(observability, site=site)
        frozen_labels = where(cohort, site=site).y_true
        check(site_flow.iloc[-1].n == len(frozen_labels)
              and site_flow.iloc[-1].target_transition_proxy == frozen_labels.sum()
              and site_flow.iloc[0].target_transition_proxy == observed.target_transition_proxy.sum()
              and site_flow.iloc[0].target_onset_beyond_released_hours == observed.onset_beyond_released_hours.sum(),
              f"Cohort counts and event observability {site}")
    all_roles = [str(patient) for ids in split[2026].values() for patient in ids]
    check(len(all_roles) == len(set(all_roles)) and set(all_roles) == set(cohort.index), "Frozen role disjointness")
    roles = []
    for role, ids in split[2026].items():
        y = cohort.loc[list(map(str, ids)), "y_true"]
        roles.append(dict(seed=2026, role=role, n_unique=len(y), positive=int(y.sum()),
                          negative=int((y == 0).sum()), prevalence=float(y.mean())))
    same_rows(roles, csv(folder / "split_event_counts.csv"), ["role"], "split event counts")
    same_rows(roles, where(csv(io.BytesIO(source[f"{audit_dir}/split_events.csv"])), seed=2026),
              ["role"], "A split event counts")

    diagnoses = []
    for path, data in source.items():
        if path.endswith("/model_diagnostics.csv"):
            folder_path = path.rsplit("/", 1)[0]
            receipt = json.loads(source[f"{folder_path}/diagnostic_provenance.json"])
            check(hashlib.sha256(data).hexdigest() == receipt["output_sha256"]["model_diagnostics.csv"], path)
            diagnoses.append(where(csv(io.BytesIO(data)), split_seed=2026, source_M=10, alpha=0.1,
                                   imputation_batch=0).assign(run_id=receipt["run_id"]))
    diagnostics = pd.concat(diagnoses)
    check(len(diagnostics) == 12, "Model diagnostic context count")
    same_rows(diagnostics, csv(folder / "base_model_context.csv"),
              ["run_id", "scenario", "metric"], "model estimates and source intervals")
    return len(flow) + len(total), len(roles), len(diagnostics)


def read_patient_decisions(run_dir):
    columns = [*PREDICTION_CONTEXT, "split_seed", "scenario", "predictor", "method",
               "target_acceptance", "selection_mode", "patient_id", "site", "y_true", "p_mean", "p_std",
               "set_0", "set_1", "y_pred", "score", "accepted", "q"]
    kept = []
    with csv(run_dir / "patient_predictions.csv", usecols=columns, dtype={"patient_id": str}, chunksize=200_000) as reader:
        for chunk in reader:
            eligible = where(chunk, **PREDICTION_CONTEXT, predictor="MI", target_acceptance=CAPACITY)
            primary = eligible.split_seed.eq(2026) & eligible.scenario.isin(SCENARIO_ROLES)
            stability = eligible.split_seed.isin(SEEDS[1:]) & eligible.scenario.eq("S4") & eligible.selection_mode.eq("frozen")
            kept.append(eligible.loc[(primary | stability) & eligible.method.isin(METHODS)])
    return pd.concat(kept, ignore_index=True)


def finite_pool_reference(pool_n, pool_errors, selected_n):
    """Compute the exact discrete central quantiles by summing combinatorial masses."""
    weights = [math.comb(pool_errors, j) * math.comb(pool_n - pool_errors, selected_n - j)
               for j in range(max(0, selected_n - pool_n + pool_errors), min(pool_errors, selected_n) + 1)]
    offset = max(0, selected_n - pool_n + pool_errors)
    denominator = math.comb(pool_n, selected_n)
    check(sum(weights) == denominator, "Hypergeometric probability mass")
    low = high = None
    cumulative = 0
    for j, weight in enumerate(weights, start=offset):
        cumulative += weight
        if low is None and cumulative * 40 >= denominator:
            low = j
        if cumulative * 40 >= 39 * denominator:
            high = j
            break
    return dict(pool_n=pool_n, pool_false_negatives=pool_errors, selected_n=selected_n,
                expected_false_negatives=selected_n * pool_errors / pool_n, reference_low=low, reference_high=high)


def verify_results(args, cohort, split):
    patients = read_patient_decisions(args.run_dir)
    rules = where(csv(args.run_dir / "thresholds.csv"), model="LR", M=10, source_M=10,
                  alpha=0.10, target_acceptance=CAPACITY)
    result_keys = ["scenario", "selection_mode", "method"]
    main, stable, flows, pairs, reference, intervals = [], [], [], [], [], []
    conditions = ["split_seed", "scenario", "selection_mode"]
    for (seed, scenario, mode), group in patients.groupby(conditions, sort=False):
        site, role = SCENARIO_ROLES[scenario]
        if mode not in ("batch", "frozen"):
            raise ValueError(f"Invalid mode {mode}")
        check(set(group.method) == set(METHODS), "Paired methods")
        b2, b4 = (where(group, method=method) for method in METHODS)
        ids = b2.patient_id.tolist()
        check(ids == b4.patient_id.tolist() and len(ids) == len(set(ids)) and set(ids) == set(map(str, split[seed][role])),
              f"Patient alignment {seed}/{scenario}/{mode}")
        frozen_labels = cohort.loc[ids]
        y = frozen_labels.y_true.to_numpy()
        check(frozen_labels.site.eq(site).all(), f"Frozen hospital {scenario}")
        p = b2.p_mean.to_numpy()
        check(np.array_equal(p, b4.p_mean.to_numpy()), "Shared probability predictor")
        ties = np.array([tie_bytes(patient_id) for patient_id in ids], dtype="S32")
        positives = y == 1
        releases = {}
        for method, frame in zip(METHODS, (b2, b4)):
            rule = where(rules, split_seed=seed, method=method)
            check(len(rule) == 1, f"Unique threshold {seed}/{method}")
            rule = rule.iloc[0]
            set0, set1 = p <= rule.q, (1 - p) <= rule.q
            pool = set0 ^ set1
            pred = np.where(pool, set1.astype(int), -1)
            for expected, column in ((y, "y_true"), (set0, "set_0"), (set1, "set_1"), (pred, "y_pred")):
                np.testing.assert_array_equal(expected, frame[column])
            check(frame.site.eq(site).all() and frame.q.eq(rule.q).all(), "Hospital or conformal threshold mismatch")
            scores = frame.score.to_numpy()
            np.testing.assert_allclose(scores, 1 - np.maximum(p, 1 - p) if method == "B2" else frame.p_std,
                                       atol=1e-12, rtol=0)
            selected = (batch_accept(pool, scores, CAPACITY, ties) if mode == "batch"
                        else frozen_accept(pool, scores, rule.threshold, bytes.fromhex(rule.tie_hash), ties))
            np.testing.assert_array_equal(selected, frame.accepted)
            releases[method] = selected
            hit = np.where(positives, set1, set0)
            negative = selected & (pred == 0)
            missed = negative & positives
            n, npos, naccept = len(y), int(positives.sum()), int(selected.sum())
            counts = dict(method=method, n=n, positives=npos, accepted=naccept, acceptance=naccept/n,
                          accepted_false_negative=int(missed.sum()))
            if scenario == "S4" and mode == "frozen":
                stable.append(dict(split_seed=int(seed), **counts))
            if seed == 2026:
                main.append(dict(scenario=scenario, selection_mode=mode, site=site, **counts,
                                 accepted_errors=int((selected & (pred != y)).sum()), accepted_negative=int(negative.sum()),
                                 pool_size=int(pool.sum()), covered=int(hit.sum()), positive_covered=int((hit & positives).sum()),
                                 coverage=float(hit.mean()), positive_coverage=float(hit[positives].mean()),
                                 selective_risk=float((pred[selected] != y[selected]).mean()),
                                 dangerous_miss=float(missed.sum()/npos), negative_residual=float(missed.sum()/negative.sum()),
                                 base_rate=npos/n))
            if seed == 2026 and mode == "batch":
                for name, subset in (("empty", ~set0 & ~set1), ("negative_singleton", set0 & ~set1),
                                     ("positive_singleton", ~set0 & set1), ("both_labels", set0 & set1)):
                    cases = subset & positives
                    flows.append(dict(scenario=scenario, site=site, method=method, set_type=name,
                                      positives=int(cases.sum()), accepted_negative=int((cases & negative).sum()),
                                      accepted_positive=int((cases & selected & (pred == 1)).sum()),
                                      rejected=int((cases & ~selected).sum())))
        if seed != 2026:
            continue
        if mode == "batch":
            left, right = (releases[m][positives] for m in METHODS)
            check(not np.any((left | right) & (pred[positives] == 1)), "Pair categories require expansion")
            pairs.append(dict(scenario=scenario, site=site, positives=int(positives.sum()),
                              both_missed=int((left & right).sum()), b2_only_missed=int((left & ~right).sum()),
                              b4_only_missed=int((~left & right).sum()), both_rejected=int((~left & ~right).sum())))
            reference.append(dict(scenario=scenario, **finite_pool_reference(
                int(pool.sum()), int((positives & (pred == 0)).sum()), int(releases["B2"].sum()))))
        fixed = dict(fixed_a=releases["B4"], fixed_b=releases["B2"]) if mode == "frozen" else {}
        seed_boot = stable_seed(2026, scenario, "B4", "B2", CAPACITY, mode)
        estimate = (pred[releases["B4"]] != y[releases["B4"]]).mean() - (pred[releases["B2"]] != y[releases["B2"]]).mean()
        intervals.append(dict(scenario=scenario, selection_mode=mode, risk_difference=float(estimate),
                              resample_size=len(y), capacity_recomputed=mode == "batch", **paired_bootstrap(
                                  y, pred, pool, b4.score, b2.score, CAPACITY, 1000, seed_boot, ties, **fixed)))

    check([len(x) for x in (main, stable, flows, pairs, reference, intervals)] == [8, 10, 16, 2, 2, 4], "Expected result rows")
    for table, expected, keys in (
        ("capacity_coverage_release", main, result_keys), ("external_frozen_stability", stable, ["split_seed", "method"]),
        ("set_to_decision_counts", flows, ["scenario", "method", "set_type"]),
        ("paired_positive_disposition", pairs, ["scenario"]), ("random_reference", reference, ["scenario"]),
        ("risk_contrasts", intervals, ["scenario", "selection_mode"]),
    ):
        same_rows(expected, csv(args.package / f"{table}.csv"), keys, table)
    official = where(csv(args.run_dir / "metrics.csv"), **PREDICTION_CONTEXT, split_seed=2026,
                     predictor="MI", target_acceptance=CAPACITY)
    official = official.loc[official.scenario.isin(SCENARIO_ROLES) & official.method.isin(METHODS)]
    package = csv(args.package / "capacity_coverage_release.csv")
    same_rows(official[official.columns.intersection(package.columns)], package, result_keys, "formal metrics")
    original = where(csv(args.run_dir / "bootstrap_differences.csv"), **PREDICTION_CONTEXT, split_seed=2026,
                     target_acceptance=CAPACITY, comparison="B4-B2")
    same_rows(intervals, original.loc[original.scenario.isin(SCENARIO_ROLES)], ["scenario", "selection_mode"], "formal intervals")
    statuses = where(csv(args.run_dir / "method_status.csv"), split_seed=2026, model="LR", M=10, source_M=10, alpha=0.10)
    statuses = statuses.loc[statuses.method.isin(["B5", "B6"])]
    check(len(statuses) == 2 and statuses.status.eq("unavailable").all()
          and statuses.reason.str.startswith("unavailable: 6 errors, 1012 correct;").all(), "B5/B6 status")
    return dict(decision_rows=len(patients), primary_decision_rows=sum(row["n"] for row in main),
                primary_contexts=len(main), stability_contexts=len(stable), flow_rows=len(flows),
                pair_tables=pairs, random_reference=reference, paired_intervals=intervals)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("a-archive", "b-archive", "run-dir", "package"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cohort, split, provenance, archives = verify_sources(args)
    flow, roles, diagnostics = verify_background(args.package, cohort, split, provenance)
    result = verify_results(args, cohort, split)
    summary = dict(status="technical_recheck_passed_pending_named_reviewer_signoff", run_id=RUN,
                   review_provenance_sha256=sha256(args.package / "provenance.json"),
                   claims_sha256=sha256(args.package / "claims_and_evidence.md"),
                   archive_sha256=archives, frozen_member_count=len(provenance["frozen_member_sha256"]),
                   run_artifact_count=len(provenance["verified_run_artifact_sha256"]),
                   package_artifact_count=len(provenance["output_sha256"]), cohort_flow_rows=flow,
                   split_role_rows=roles, diagnostic_rows=diagnostics, **result)
    data = json.dumps(summary, indent=2, allow_nan=False) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(data)
    print(data, end="")


if __name__ == "__main__":
    main()
