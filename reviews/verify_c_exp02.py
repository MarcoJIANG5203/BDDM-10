"""C independent verification of B's EXP-02 first-stage runs (first-principles).

Re-derives the headline numbers straight from each run's patient-level
predictions and the frozen A splits, without importing B's `src` or reusing
B's `summarize_exp02.py`. Checks:

  1. run manifest / patient_predictions SHA256 integrity
  2. role isolation: S0 rows all internal (site A, `test` split), S4 rows all
     external (site B, `external` split), no ID overlap across roles
  3. counts: n, positives per scenario/batch
  4. headline metrics recomputed independently (prevalence, AUROC, AUPRC, Brier,
     mean predicted probability)
  5. agreement with B's published model_diagnostics.csv

Usage:
  python reviews/verify_c_exp02.py \
      --run results/experiment-strengthening/20261109T031529_545a3423 \
      --formal-data .artifact-cache/b002-formal \
      --reference reports/experiment-strengthening/20261109T031529_545a3423/model_diagnostics.csv \
      --output .artifact-cache/exp02/c_exp02_545a3423.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


CONTEXT = ["split_seed", "model", "source_M", "alpha", "scenario", "imputation_batch"]
ROLES = ("train", "selection", "calibration", "test", "external")


def sha256(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def mann_whitney_auroc(y, p):
    """AUROC via Mann-Whitney U (no library)."""
    pos = p[y == 1]
    neg = p[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    return float((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean())


def average_precision(y, p):
    """Average precision (area under PR curve) via rank thresholds."""
    order = np.argsort(-p)
    y = y[order].astype(float)
    if y.sum() == 0:
        return np.nan
    tp = np.cumsum(y)
    prec = tp / np.arange(1, len(y) + 1)
    return float(np.sum(prec[y == 1]) / y.sum())


def brier(y, p):
    return float(np.mean((y - p) ** 2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--formal-data", required=True, type=Path)
    ap.add_argument("--reference", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    checks = []
    def check(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    run = args.run
    manifest_file = run / "manifest.json"
    predictions_file = run / "patient_predictions.csv"

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    check("run_manifest_present", True)
    if "artifact_hashes" in manifest and predictions_file.name in manifest["artifact_hashes"]:
        expected = manifest["artifact_hashes"][predictions_file.name]
        actual = sha256(predictions_file)
        check("patient_predictions_sha256", actual == expected, actual)

    data = pd.read_csv(predictions_file, usecols=CONTEXT + ["patient_id", "site", "method", "predictor", "y_true", "p_mean"])
    data = data[(data.method == "B1") & (data.predictor == "MI")]
    check("one_MI_row_per_context_patient",
          not data.duplicated(CONTEXT + ["patient_id"]).any(), f"{len(data)} rows")
    check("binary_labels", data.y_true.isin([0, 1]).all())
    check("probabilities_in_01", data.p_mean.between(0, 1).all())

    # Frozen splits: role isolation per seed 2026.
    splits = {}
    split_path = args.formal_data / "splits" / "seed_2026.json"
    if split_path.is_file():
        splits = json.loads(split_path.read_text(encoding="utf-8"))
        check("split_roles_present", set(splits) == set(ROLES))
        all_ids = [pid for v in splits.values() for pid in v]
        check("split_no_overlap", len(all_ids) == len(set(all_ids)))

    result = {"checks": checks, "rows": []}
    for (seed, model, srcM, alpha, scenario, batch), grp in data.groupby(CONTEXT):
        expected_site = "B" if scenario == "S4" else "A"
        site_ok = grp.site.eq(expected_site).all()
        check(f"site_identity_{scenario}_b{batch}", bool(site_ok),
              f"{int((~grp.site.eq(expected_site)).sum())} mismatches")
        if splits:
            expected_role = "external" if scenario == "S4" else "test"
            role_ids = set(splits.get(expected_role, []))
            match = set(grp.patient_id) == role_ids
            check(f"split_membership_{scenario}_b{batch}", bool(match),
                  f"run {len(set(grp.patient_id))} vs split {len(role_ids)}")
        y = grp.sort_values("patient_id").y_true.to_numpy()
        p = grp.sort_values("patient_id").p_mean.to_numpy()
        n = len(y)
        pos = int(y.sum())
        row = {
            "scenario": scenario, "batch": int(batch), "model": model,
            "n": n, "positives": pos,
            "prevalence": float(y.mean()),
            "mean_probability": float(p.mean()),
            "auroc": mann_whitney_auroc(y, p),
            "auprc": average_precision(y, p),
            "brier": brier(y, p),
        }
        result["rows"].append(row)

    # Compare with B's published diagnostics (batch 0 only, the headline rows).
    ref = pd.read_csv(args.reference)
    ref = ref[ref.imputation_batch == 0]
    for row in result["rows"]:
        if row["batch"] != 0:
            continue
        m = ref[(ref.scenario == row["scenario"]) & (ref.metric == "auroc")]
        if len(m):
            check(f"auroc_match_{row['scenario']}",
                  abs(m.iloc[0].estimate - row["auroc"]) < 1e-9,
                  f"C {row['auroc']:.6f} vs B {m.iloc[0].estimate:.6f}")
        m = ref[(ref.scenario == row["scenario"]) & (ref.metric == "brier")]
        if len(m):
            check(f"brier_match_{row['scenario']}",
                  abs(m.iloc[0].estimate - row["brier"]) < 1e-9,
                  f"C {row['brier']:.6f} vs B {m.iloc[0].estimate:.6f}")
        m = ref[(ref.scenario == row["scenario"]) & (ref.metric == "prevalence")]
        if len(m):
            check(f"prevalence_match_{row['scenario']}",
                  abs(m.iloc[0].estimate - row["prevalence"]) < 1e-9,
                  f"C {row['prevalence']:.6f} vs B {m.iloc[0].estimate:.6f}")
        m = ref[(ref.scenario == row["scenario"]) & (ref.metric == "auprc")]
        if len(m):
            check(f"auprc_match_{row['scenario']}",
                  abs(m.iloc[0].estimate - row["auprc"]) < 1e-9,
                  f"C {row['auprc']:.6f} vs B {m.iloc[0].estimate:.6f}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8", newline="\n")
    passed = sum(1 for c in checks if c["pass"])
    print(f"C EXP-02 verification ({run.name}): {passed}/{len(checks)} checks passed.")
    for c in checks:
        print(f"  [{'PASS' if c['pass'] else 'FAIL'}] {c['check']} {c['detail']}")
    print(json.dumps(result["rows"], indent=2))


if __name__ == "__main__":
    main()
