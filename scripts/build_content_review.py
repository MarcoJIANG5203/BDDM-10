"""Build the aggregate CONTENT-01–03 review package from the frozen v1 inputs."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np
import pandas as pd
from scipy.stats import hypergeom

from matplotlib.patches import Patch

from scripts.make_figures import (
    load_acceptance, load_config, load_json, one, plt, sha256_file, subset,
    verify_artifact_hashes, write_csv,
)
from src.conformal import singleton_predictions
from src.metrics import evaluate
from src.selection import batch_accept, frozen_accept


ROOT = Path(__file__).resolve().parents[1]
A_BUNDLE = "a-data-v1-20261104-r1"
B_BUNDLE = "b-clinical-v1-20261104-r1"
RUN = "20261105T055420_02d05b15"
AUDIT = "reports/experiment-strengthening/exp01-a-20261110-r1"
A_COMMIT = "f0f0bfc3d61fd603c8161330914fce0180762339"
B_COMMIT = "0afaf3720b977208ae10eeed35e64b1f1ba3b091"
C_COMMIT = "c9b57bf1d3832714122b8a2b0c8e1a3e468d4c2c"
DIAGNOSTIC_RUNS = ("20261109T031529_545a3423", "20261109T031529_e842da06")
SCENARIOS = {"S0": ("A", "test"), "S4": ("B", "external")}
METHODS = ("B2", "B4")
MODES = ("batch", "frozen")
CONTEXT = dict(protocol_version="v1", run_id=RUN, synthetic=False, split_seed=2026,
               model="LR", M=10, source_M=10, alpha=0.10, imputation_batch=0)
CAPACITY = 0.60


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def blob(commit, path):
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def checked_blob(commit, path, expected, sources):
    data = blob(commit, path)
    actual = digest(data)
    require(expected is None or actual == expected, f"Source hash mismatch: {path}")
    sources[f"{commit}:{path}"] = actual
    return data


def read_csv(data):
    return pd.read_csv(io.BytesIO(data), float_precision="round_trip")


def load_inputs(args):
    registry_path = ROOT / "artifacts/registry.json"
    registry = load_json(registry_path)["bundles"]
    archives = {A_BUNDLE: args.a_archive, B_BUNDLE: args.b_archive}
    hashes = {version: sha256_file(path) for version, path in archives.items()}
    for version, actual in hashes.items():
        require(actual == registry[version]["sha256"], f"Archive hash mismatch: {version}")

    freeze_path = ROOT / registry[A_BUNDLE]["freeze_record"]
    freeze = load_json(freeze_path)
    require(freeze["formal_data_version"] == A_BUNDLE, "Unexpected A freeze version")
    frozen = {**freeze["split_sha256"], "data/processed/cohort.csv": freeze["cohort_csv_sha256"],
              "data/processed/cohort.parquet": freeze["cohort_sha256"],
              "data/processed/cohort_audit.json": freeze["delivery_audit_sha256"]}
    with ZipFile(args.a_archive) as archive:
        for name, expected in frozen.items():
            require(digest(archive.read(name)) == expected, f"A frozen member mismatch: {name}")
        cohort = pd.read_parquet(io.BytesIO(archive.read("data/processed/cohort.parquet")),
                                 columns=["patient_id", "site", "y_true"])
        split = json.loads(archive.read("splits/seed_2026.json"))
    cohort["patient_id"] = cohort.patient_id.astype(str)
    cohort = cohort.set_index("patient_id")
    require(cohort.index.is_unique, "Duplicate patient in frozen cohort")

    manifest_path = args.run_dir / "manifest.json"
    with ZipFile(args.b_archive) as archive:
        require(archive.read(f"results/clinical/{RUN}/manifest.json") == manifest_path.read_bytes(),
                "Restored manifest differs from the registered B archive")
    manifest = load_json(manifest_path)
    require(manifest["run_id"] == RUN and manifest["synthetic"] is False
            and manifest["data_version"] == A_BUNDLE, "Unexpected run identity")
    require(manifest["data_sha256"] == freeze["cohort_sha256"]
            and manifest["audit_sha256"] == freeze["delivery_audit_sha256"]
            and {f"splits/seed_{seed}.json": sha for seed, sha in manifest["split_sha256"].items()}
            == freeze["split_sha256"], "B run does not use the frozen inputs")
    acceptance = load_acceptance(args.run_dir, manifest, load_config(args.run_dir), None, ROOT)
    artifacts = verify_artifact_hashes(args.run_dir, manifest)
    provenance = dict(
        status="producer_verified_pending_independent_content_review", run_id=RUN,
        source_acceptance_status=acceptance["record"]["status"],
        acceptance_sha256=acceptance["sha256"], manifest_sha256=sha256_file(manifest_path),
        registry_sha256=sha256_file(registry_path), archive_sha256=hashes,
        freeze_record_sha256=sha256_file(freeze_path), frozen_member_sha256=frozen,
        verified_run_artifact_sha256=artifacts, pinned_source_sha256={},
        filters={**CONTEXT, "scenarios": list(SCENARIOS), "predictor": "MI", "methods": METHODS,
                 "selection_modes": MODES, "target_acceptance": CAPACITY},
        c_diagnostics_scope_commit=C_COMMIT,
    )
    return cohort, split, provenance


def background_tables(cohort, split, sources):
    manifest = json.loads(checked_blob(A_COMMIT, f"{AUDIT}/manifest.json", None, sources))
    flow, observability, roles = [
        read_csv(checked_blob(A_COMMIT, f"{AUDIT}/{name}", manifest["aggregate_sha256"][name], sources))
        for name in ("cohort_flow.csv", "target_event_observability.csv", "split_events.csv")
    ]
    fields = ["n", "target_transition_proxy", "target_onset_within_released_hours",
              "target_onset_beyond_released_hours"]
    cohort_rows = []
    for site in ("A", "B"):
        rows = flow.loc[flow.site == site, ["site", "stage", *fields]].copy()
        rows["excluded_at_stage"] = -rows.n.diff().fillna(0).astype(int)
        rows["excluded_proxy_at_stage"] = -rows.target_transition_proxy.diff().fillna(0).astype(int)
        raw, final = rows.iloc[0], rows.iloc[-1]
        site_observed = observability.loc[observability.site == site]
        excluded = site_observed.loc[site_observed.reason != "included"]
        require(raw.stage == "raw" and raw.target_transition_proxy == site_observed.target_transition_proxy.sum()
                and raw.target_onset_beyond_released_hours == site_observed.onset_beyond_released_hours.sum()
                and rows.excluded_proxy_at_stage.sum() == excluded.target_transition_proxy.sum(),
                f"Audit flow and observability disagree: {site}")
        site_cohort = cohort.loc[cohort.site == site]
        require(final.n == len(site_cohort) and final.target_transition_proxy == site_cohort.y_true.sum(),
                f"Audit and frozen cohort disagree: {site}")
        cohort_rows.append(rows)
    flow = pd.concat(cohort_rows, ignore_index=True)
    totals = flow.groupby("stage", sort=False, as_index=False).sum(numeric_only=True).assign(site="Total")
    flow = pd.concat([flow, totals[flow.columns]], ignore_index=True)
    roles = subset(roles, "audit split counts", seed=CONTEXT["split_seed"])
    for row in roles.itertuples():
        subset_cohort = cohort.loc[list(map(str, split[row.role]))]
        require(len(subset_cohort) == row.n_unique and subset_cohort.y_true.sum() == row.positive,
                f"Audit and frozen split disagree: {row.role}")

    diagnostics = []
    for run_id in DIAGNOSTIC_RUNS:
        path = f"reports/experiment-strengthening/{run_id}"
        info = json.loads(checked_blob(B_COMMIT, f"{path}/diagnostic_provenance.json", None, sources))
        data = read_csv(checked_blob(B_COMMIT, f"{path}/model_diagnostics.csv",
                                     info["output_sha256"]["model_diagnostics.csv"], sources))
        data = subset(data, "base model diagnostics", split_seed=2026, source_M=10, alpha=0.10,
                      imputation_batch=0).assign(run_id=run_id)
        for scenario in data.scenario.unique():
            site, role = SCENARIOS[scenario]
            n = one(roles, "audit split counts", role=role)
            group = data.loc[data.scenario == scenario]
            require(sorted(group.metric) == ["auprc", "auroc", "brier", "prevalence"]
                    and (group.site == site).all() and (group.n == n.n_unique).all()
                    and (group.positives == n.positive).all(), f"Wrong diagnostics context: {run_id}/{scenario}")
        diagnostics.append(data)
    models = pd.concat(diagnostics, ignore_index=True)
    models["estimate_review"] = "C-010 independently recomputed"
    models["interval_review"] = "B producer interval copied from diagnostic output"
    return flow, roles, models


def result_tables(run_dir, cohort, split):
    def artifact(name):
        return pd.read_csv(run_dir / name, float_precision="round_trip")

    metrics = artifact("metrics.csv")
    coverage = artifact("coverage_strata.csv")
    bootstrap = artifact("bootstrap_differences.csv")
    thresholds = artifact("thresholds.csv")
    columns = [*CONTEXT, "scenario", "predictor", "method", "target_acceptance", "selection_mode",
               "site", "patient_id", "y_true", "p_mean", "set_0", "set_1", "accepted", "y_pred", "score"]
    selected = []
    with pd.read_csv(run_dir / "patient_predictions.csv", usecols=columns,
                     float_precision="round_trip", dtype={"patient_id": str}, chunksize=200_000) as reader:
        for chunk in reader:
            keep = chunk.scenario.isin(SCENARIOS) & chunk.method.isin(METHODS)
            keep &= chunk.predictor.eq("MI") & chunk.target_acceptance.eq(CAPACITY)
            for name, value in CONTEXT.items():
                keep &= chunk[name].eq(value)
            selected.append(chunk.loc[keep])
    patients = pd.concat(selected, ignore_index=True)

    comparisons, pairs, flow, contrasts, random_rows = [], [], [], [], []
    for scenario, (site, role) in SCENARIOS.items():
        identities = cohort.loc[list(map(str, split[role]))].sort_index()
        reference = None
        batch_decisions = {}
        pos_cov = one(coverage, "positive coverage", **CONTEXT, scenario=scenario, predictor="MI", stratum="y=1")
        for mode in MODES:
            risks = {}
            for method in METHODS:
                keys = dict(scenario=scenario, selection_mode=mode, method=method, target_acceptance=CAPACITY)
                rows = subset(patients, "patient decisions", **keys).set_index("patient_id").sort_index()
                require(rows.index.is_unique, f"Duplicate patient: {scenario}/{mode}/{method}")
                require(rows[["site", "y_true"]].equals(identities) and rows.site.eq(site).all(),
                        f"Patients or labels differ from frozen split: {scenario}/{mode}/{method}")
                shared = rows[["p_mean", "set_0", "set_1", "y_pred"]]
                if reference is None:
                    reference = shared
                require(shared.equals(reference), f"Prediction sets or probabilities differ: {scenario}/{mode}/{method}")
                sets = rows[["set_0", "set_1"]].to_numpy(dtype=bool)
                pool, pred = singleton_predictions(sets)
                np.testing.assert_array_equal(pred, rows.y_pred)
                if mode == "batch":
                    replay = batch_accept(rows.index, pool, rows.score, CAPACITY)
                else:
                    rule = one(thresholds, "frozen threshold", split_seed=2026, model="LR", M=10,
                               source_M=10, alpha=0.10, method=method, target_acceptance=CAPACITY)
                    replay = frozen_accept(rows.index, pool, rows.score, rule)
                np.testing.assert_array_equal(replay, rows.accepted)
                result = evaluate(rows.y_true, rows.p_mean, pred, sets, replay)
                result["pool_size"] = int(pool.sum())
                official = one(metrics, "official metrics", **CONTEXT, **keys, predictor="MI")
                for name, value in result.items():
                    require(np.isclose(value, official[name], atol=1e-12, rtol=0), f"Metric mismatch: {keys}/{name}")
                y = rows.y_true.to_numpy(dtype=int)
                positive = y == 1
                covered = sets[np.arange(len(y)), y]
                pos_hit = int(covered[positive].sum())
                require(pos_hit == pos_cov.covered and result["positives"] == pos_cov.n, "Positive coverage mismatch")
                comparisons.append({**CONTEXT, **keys, "site": site, **result,
                                    "covered": int(covered.sum()), "positive_covered": pos_hit,
                                    "positive_coverage": pos_hit / result["positives"]})
                risks[method] = result["selective_risk"]
                if mode == "batch":
                    batch_decisions[method] = np.where(replay[positive], pred[positive], -1)
                    require(not np.any(batch_decisions[method] == 1), "Positive accepts need an expanded disposition table")
                    for label, mask in (("empty", ~sets.any(axis=1)), ("negative_singleton", pool & (pred == 0)),
                                        ("positive_singleton", pool & (pred == 1)), ("both_labels", sets.all(axis=1))):
                        cases = positive & mask
                        flow.append(dict(scenario=scenario, site=site, method=method, set_type=label,
                                         positives=int(cases.sum()), accepted_negative=int((cases & replay & (pred == 0)).sum()),
                                         accepted_positive=int((cases & replay & (pred == 1)).sum()),
                                         rejected=int((cases & ~replay).sum())))
                    if method == "B2":
                        random_rows.append(dict(scenario=scenario, pool_n=int(pool.sum()),
                                                pool_false_negatives=int((positive & pool & (pred == 0)).sum()),
                                                selected_n=result["accepted"]))
            contrast = one(bootstrap, "official bootstrap", **CONTEXT, scenario=scenario,
                           selection_mode=mode, target_acceptance=CAPACITY, comparison="B4-B2")
            require(np.isclose(risks["B4"] - risks["B2"], contrast.risk_difference, atol=1e-12, rtol=0),
                    f"Contrast mismatch: {scenario}/{mode}")
            contrasts.append(contrast.to_dict())
        b2, b4 = (batch_decisions[m] == 0 for m in METHODS)
        pairs.append(dict(scenario=scenario, site=site, positives=len(b2), both_missed=int((b2 & b4).sum()),
                          b2_only_missed=int((b2 & ~b4).sum()), b4_only_missed=int((~b2 & b4).sum()),
                          both_rejected=int((~b2 & ~b4).sum())))
    require(len(patients) == sum(row["n"] for row in comparisons), "Unaccounted patient rows")

    stability = subset(metrics, "five-seed external capacity", run_id=RUN, synthetic=False, model="LR", M=10,
                       source_M=10, alpha=0.10, imputation_batch=0, scenario="S4", target_acceptance=CAPACITY,
                       predictor="MI", selection_mode="frozen")
    stability = stability.loc[stability.method.isin(METHODS),
                              ["split_seed", "method", "n", "positives", "accepted", "acceptance", "accepted_false_negative"]]
    require(len(stability) == 10 and not stability.duplicated(["split_seed", "method"]).any()
            and set(stability.split_seed) == set(range(2026, 2031)), "Missing five-seed stability context")
    random_ref = pd.DataFrame(random_rows)
    random_ref["expected_false_negatives"] = random_ref.selected_n * random_ref.pool_false_negatives / random_ref.pool_n
    for name, q in (("reference_low", .025), ("reference_high", .975)):
        random_ref[name] = hypergeom.ppf(q, random_ref.pool_n, random_ref.pool_false_negatives, random_ref.selected_n).astype(int)
    return {"capacity_coverage_release": pd.DataFrame(comparisons), "paired_positive_disposition": pd.DataFrame(pairs),
            "set_to_decision_counts": pd.DataFrame(flow), "risk_contrasts": pd.DataFrame(contrasts),
            "external_frozen_stability": stability, "random_reference": random_ref}


def reliability_figure(data, contrasts, out_dir):
    colors = ("#176b87", "#bc5a24")
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5), gridspec_kw={"width_ratios": [1, 1.15, 1.15]})
    fig.subplots_adjust(left=.085, right=.97, bottom=.24, top=.76, wspace=.48)
    fig.text(.085, .925, "Prediction-set coverage and patient disposition", fontsize=17, weight="bold")
    fig.text(.085, .865, "Primary LR setting  |  Seed 2026  |  M = 10  |  α = 0.10  |  Target acceptance = 60%", fontsize=9.5)
    fig.text(.97, .925, "CONTENT REVIEW", ha="right", fontsize=9, color="#586673", weight="bold")
    positions = np.arange(4)
    labels = ["S0 / batch", "S0 / frozen", "S4 / batch", "S4 / frozen"]

    def bars(ax, pos, values, annotations, color):
        ax.barh(pos, values, height=.30, color=color)
        for y, value, label in zip(pos, values, annotations):
            ax.text(value + 2, y, label, va="center", fontsize=8)

    coverage = data.drop_duplicates("scenario")
    for offset, field, numerator, denominator, color in (
        (-.17, "coverage", "covered", "n", colors[0]),
        (.17, "positive_coverage", "positive_covered", "positives", colors[1]),
    ):
        bars(axes[0], np.arange(2) + offset, 100 * coverage[field],
             [f"{a:,}/{b:,}" for a, b in zip(coverage[numerator], coverage[denominator])], color)
    axes[0].set_yticks([0, 1], ["S0 Internal", "S4 External"])
    axes[0].set_ylim(1.65, -.65)
    def legend(ax, labels):
        ax.legend(handles=[Patch(facecolor=color, label=label) for color, label in zip(colors, labels)],
                  loc="lower center", bbox_to_anchor=(.5, -.32), ncol=2, frameon=False, fontsize=8)

    legend(axes[0], ["All patients", "True positives"])
    for i, (method, color) in enumerate(zip(METHODS, colors)):
        rows = data.loc[data.method == method]
        pos = positions + (-.17 if i == 0 else .17)
        bars(axes[1], pos, 100 * rows.acceptance,
             [f"{p:.2%} ({n:,})" for p, n in zip(rows.acceptance, rows.accepted)], color)
        bars(axes[2], pos, 100 * rows.dangerous_miss,
             [f"{a}/{b}" for a, b in zip(rows.accepted_false_negative, rows.positives)], color)
    for ax in axes[1:]:
        ax.set_yticks(positions, labels)
        ax.set_ylim(3.65, -.65)
        ax.axhline(1.5, color="#cbd5dc", linewidth=.8)
    legend(axes[1], ["B2 Confidence", "B4 Disagreement"])
    for ax, title, limit in zip(axes, ("A  Set coverage", "B  Actual acceptance", "C  False-negative releases"),
                                (130, 137, 113)):
        ax.set_title(title, loc="left", fontsize=10.5, weight="bold", pad=10)
        ax.set_xlim(0, limit)
        ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
        ax.tick_params(axis="both", length=0, labelsize=8)
        ax.grid(axis="x", color="#e4e9ed", linewidth=.7)
        ax.set_axisbelow(True)
        for spine in ax.spines.values():
            spine.set_visible(False)
    primary = contrasts.loc[contrasts.selection_mode == "batch"]
    intervals = "   |   ".join(f"{row.scenario} {100*row.risk_difference:+.3f} pp "
                               f"[{100*row.ci_low:+.3f}, {100*row.ci_high:+.3f}]"
                               for row in primary.itertuples())
    fig.text(.085, .042, f"Batch B4 − B2 selective-risk difference (95% paired interval)   {intervals}", fontsize=8.5)
    fig.savefig(out_dir / "fig_reliability.png", dpi=250)
    fig.savefig(out_dir / "fig_reliability.pdf", metadata={"CreationDate": None})
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("a-archive", "b-archive", "run-dir", "out-dir"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out_dir.exists(), f"Output already exists: {args.out_dir}")
    cohort, split, provenance = load_inputs(args)
    flow, roles, models = background_tables(cohort, split, provenance["pinned_source_sha256"])
    results = result_tables(args.run_dir, cohort, split)
    args.out_dir.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=args.out_dir.parent) as work:
        staged = Path(work) / "package"
        staged.mkdir()
        tables = {"cohort_flow": flow, "split_event_counts": roles, "base_model_context": models, **results}
        for name, data in tables.items():
            write_csv(data, staged / f"{name}.csv")
        reliability_figure(results["capacity_coverage_release"], results["risk_contrasts"], staged)
        provenance["command"] = ["python", "-m", "scripts.build_content_review", *sys.argv[1:]]
        provenance["generator_sha256"] = sha256_file(Path(__file__))
        provenance["generator_dependencies_sha256"] = {
            path: sha256_file(ROOT / path) for path in (
                "scripts/make_figures.py", "src/conformal.py", "src/metrics.py", "src/selection.py", "src/utils.py",
            )
        }
        provenance["output_sha256"] = {p.name: sha256_file(p) for p in sorted(staged.iterdir())}
        (staged / "provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        staged.rename(args.out_dir)
    print(f"Verified {len(provenance['verified_run_artifact_sha256'])} run artifacts and "
          f"{int(results['capacity_coverage_release'].n.sum())} patient decision rows. Wrote {args.out_dir}.")


if __name__ == "__main__":
    main()
