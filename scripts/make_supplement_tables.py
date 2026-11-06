#!/usr/bin/env python3
"""Generate D-002 supplementary Tables S1-S3 from the accepted supplement run.

Inputs: the formal supplement run directory (metrics.csv, bootstrap_differences.csv,
manifest.json, config.yaml) and the C/E acceptance JSON for that run.

Outputs: table_s1_rf.csv, table_s2_m_sensitivity.csv, table_s3_alpha005.csv,
provenance.json, under paper/runs/<run_id>/tables/ by default.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("make_figures", Path(__file__).with_name("make_figures.py"))
mf = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mf)


class SupplementError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return mf.sha256_file(path)


def pick(frame: pd.DataFrame, label: str, **conditions) -> pd.Series:
    out = frame
    for column, value in conditions.items():
        if column not in out.columns:
            raise SupplementError(f"missing column {column!r} for {label}")
        if value is None:
            out = out[out[column].isna()]
        elif isinstance(value, (float, np.floating)):
            out = out[np.isclose(pd.to_numeric(out[column], errors="coerce").astype(float), float(value), rtol=0, atol=1e-9)]
        else:
            out = out[out[column] == value]
    if len(out) != 1:
        raise SupplementError(f"expected 1 row for {label}, found {len(out)}: {conditions}")
    return out.iloc[0]


def metric_row(row: pd.Series, **extra) -> dict:
    base = dict(
        kind="method",
        method=row.get("method"),
        scenario=row.get("scenario"),
        model=row.get("model"),
        M=row.get("M"),
        source_M=row.get("source_M"),
        alpha=row.get("alpha"),
        target_acceptance=row.get("target_acceptance"),
        selection_mode=row.get("selection_mode"),
        n=row.get("n"),
        positives=row.get("positives"),
        accepted=row.get("accepted"),
        acceptance=row.get("acceptance"),
        selective_risk=row.get("selective_risk"),
        dangerous_miss=row.get("dangerous_miss"),
        negative_residual=row.get("negative_residual"),
        coverage=row.get("coverage"),
        pool_size=row.get("pool_size"),
        capacity_shortfall=row.get("capacity_shortfall"),
        comparison=None,
        risk_difference=None,
        ci_low=None,
        ci_high=None,
        valid=None,
        invalid=None,
    )
    base.update(extra)
    return base


def contrast_row(row: pd.Series, **extra) -> dict:
    base = dict(
        kind="contrast",
        method="B4-B2",
        scenario=row.get("scenario"),
        model=row.get("model"),
        M=row.get("M"),
        source_M=row.get("source_M"),
        alpha=row.get("alpha"),
        target_acceptance=row.get("target_acceptance"),
        selection_mode=row.get("selection_mode"),
        n=None,
        positives=None,
        accepted=None,
        acceptance=None,
        selective_risk=None,
        dangerous_miss=None,
        negative_residual=None,
        coverage=None,
        pool_size=None,
        capacity_shortfall=None,
        comparison="B4-B2",
        risk_difference=row.get("risk_difference"),
        ci_low=row.get("ci_low"),
        ci_high=row.get("ci_high"),
        valid=row.get("valid"),
        invalid=row.get("invalid"),
    )
    base.update(extra)
    return base


def build(run_dir: Path, acceptance_file: Path, out_dir: Path, overwrite: bool) -> dict:
    run_dir = run_dir.resolve()
    manifest = mf.load_json(run_dir / "manifest.json")
    if manifest.get("run_status") != "completed" or bool(manifest.get("synthetic")):
        raise SupplementError("supplement run must be completed and synthetic=false")
    if str(manifest.get("run_id")) != run_dir.name:
        raise SupplementError("manifest run_id does not match run directory")
    config = mf.load_config(run_dir)
    acceptance = mf.load_acceptance(run_dir, manifest, config, acceptance_file, ROOT)
    verified = mf.verify_artifact_hashes(run_dir, manifest)

    metrics = pd.read_csv(run_dir / "metrics.csv")
    bootstrap = pd.read_csv(run_dir / "bootstrap_differences.csv")
    for frame in (metrics, bootstrap):
        values = set(frame["synthetic"].dropna().astype(bool))
        if values != {False}:
            raise SupplementError("supplement metrics/bootstrap synthetic flag is not false")

    def add_contrasts(rows: list[dict], *, model: str, M: int, source_M: int, alpha: float, scenario: str) -> None:
        for mode in ("batch", "frozen"):
            try:
                row = pick(
                    bootstrap,
                    f"B4-B2 {model} M{M} source{source_M} alpha{alpha} {scenario} {mode}",
                    model=model,
                    M=M,
                    source_M=source_M,
                    alpha=alpha,
                    scenario=scenario,
                    comparison="B4-B2",
                    target_acceptance=0.6,
                    selection_mode=mode,
                )
            except SupplementError:
                continue
            rows.append(contrast_row(row))

    # S1: RF S0/S2 at alpha=.1, M=10, target .6, batch.
    s1 = []
    for scenario in ("S0", "S2"):
        for method in ("B0", "B1", "B2", "B3", "B4"):
            m_value = 1 if method == "B0" else 10
            target = None if method in ("B0", "B1") else 0.6
            row = pick(
                metrics,
                f"S1 {scenario} {method}",
                model="RF",
                M=m_value,
                source_M=10,
                alpha=0.1,
                scenario=scenario,
                method=method,
                target_acceptance=target,
                selection_mode="batch",
                imputation_batch=0,
            )
            s1.append(metric_row(row))
        add_contrasts(s1, model="RF", M=10, source_M=10, alpha=0.1, scenario=scenario)

    # S2: M=5/20 vs 10 at S0, alpha=.1, target .6, batch.
    s2 = []
    for source_m in (5, 10, 20):
        for method in ("B0", "B1", "B2", "B3", "B4"):
            m_value = 1 if method == "B0" else source_m
            target = None if method in ("B0", "B1") else 0.6
            row = pick(
                metrics,
                f"S2 source_M{source_m} {method}",
                model="LR",
                M=m_value,
                source_M=source_m,
                alpha=0.1,
                scenario="S0",
                method=method,
                target_acceptance=target,
                selection_mode="batch",
                imputation_batch=0,
            )
            s2.append(metric_row(row))
        add_contrasts(s2, model="LR", M=source_m, source_M=source_m, alpha=0.1, scenario="S0")

    # S3: alpha=.05, S0/S2, M=10, target .6, batch.
    s3 = []
    for scenario in ("S0", "S2"):
        for method in ("B0", "B1", "B2", "B3", "B4"):
            m_value = 1 if method == "B0" else 10
            target = None if method in ("B0", "B1") else 0.6
            row = pick(
                metrics,
                f"S3 {scenario} {method}",
                model="LR",
                M=m_value,
                source_M=10,
                alpha=0.05,
                scenario=scenario,
                method=method,
                target_acceptance=target,
                selection_mode="batch",
                imputation_batch=0,
            )
            s3.append(metric_row(row))
        add_contrasts(s3, model="LR", M=10, source_M=10, alpha=0.05, scenario=scenario)

    out_dir = out_dir.resolve()
    if out_dir.exists() and any(out_dir.iterdir()) and not overwrite:
        raise SupplementError(f"output directory is not empty: {out_dir}; use --overwrite")
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    stamp = dict(run_id=manifest.get("run_id"), synthetic=False, status="ACCEPTED_WITH_LIMITS")
    outputs = []
    for name, rows in (
        ("table_s1_rf.csv", s1),
        ("table_s2_m_sensitivity.csv", s2),
        ("table_s3_alpha005.csv", s3),
    ):
        frame = pd.DataFrame(rows)
        for key, value in stamp.items():
            frame.insert(0, key, value)
        path = tables_dir / name
        frame.to_csv(path, index=False, encoding="utf-8")
        outputs.append(path)

    provenance = {
        "schema_version": 1,
        "status": "ACCEPTED_WITH_LIMITS",
        "run_id": manifest.get("run_id"),
        "manifest_sha256": sha256(run_dir / "manifest.json"),
        "acceptance": {
            "path": mf.display_path(acceptance["path"], ROOT),
            "sha256": acceptance["sha256"],
            "status": acceptance["record"].get("status"),
            "scope": acceptance["record"].get("scope"),
            "accepted_at": acceptance["record"].get("accepted_at"),
        },
        "inputs": verified,
        "outputs": {str(path.relative_to(out_dir)).replace("\\", "/"): sha256(path) for path in outputs},
        "tables": ["S1 RF", "S2 M=5/10/20", "S3 alpha=.05"],
        "limitations": [
            "B5/B6 unavailable; no B6-B5 contrast",
            "positive-class coverage zero",
            "finite-event protocol v1 only",
            "acceptance is not final manuscript/PDF acceptance",
        ],
    }
    (out_dir / "provenance_supplement.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "out_dir": str(out_dir),
        "tables": len(outputs),
        "run_id": manifest.get("run_id"),
        "status": "ACCEPTED_WITH_LIMITS",
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--acceptance-file", required=True)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    run_dir = Path(args.run_dir).resolve()
    out_dir = Path(args.out_dir).resolve() if args.out_dir else ROOT / "paper" / "runs" / run_dir.name
    try:
        result = build(run_dir, Path(args.acceptance_file).resolve(), out_dir, args.overwrite)
    except (SupplementError, mf.ProvenanceError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
