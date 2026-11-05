#!/usr/bin/env python3
"""Generate D-001 tables and figures from an immutable experiment run.

The script is intentionally strict:

* it reads ``manifest.json`` and verifies every recorded artifact hash before
  using a run;
* it refuses to turn a synthetic run into paper results unless
  ``--validation-only`` is passed, in which case every output is watermarked;
* a clinical run must have a C/E-signed acceptance record (by default
  ``reviews/acceptance/<run_id>.json``) whose manifest SHA256 matches the run;
  candidate or otherwise unaccepted runs are refused;
* ``--draft-unaccepted --draft-reason ...`` is the only exception: it renders a
  clinical candidate as a clearly watermarked DRAFT into ``paper/draft-runs/``;
  it never satisfies the production gate and is not for submission;
* every plotted or tabulated number is computed from the run's CSV/JSON files;
  no result number is typed into the script or the paper by hand;
* the data behind each figure is written next to the figure so every number can
  be traced to a run, a filter and a column.

Typical use after A/B deliver a clinical run::

    python scripts/make_figures.py \
        --run-dir results/clinical/<run_id> \
        --cohort data/processed/cohort.parquet \
        --audit data/processed/cohort_audit.json

Synthetic software validation only::

    python scripts/make_figures.py \
        --run-dir results/synthetic/20261102T063118_fa76f8a8 \
        --cohort data/synthetic/cohort.csv \
        --audit data/synthetic/cohort_audit.json \
        --validation-only
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

EXPECTED_METHODS = ("B0", "B1", "B2", "B3", "B4", "B5", "B6")
MAIN_METHODS = ("B2", "B3", "B4", "B5", "B6")
STRATA_ORDER = (
    "all",
    "y=0",
    "y=1",
    "missing_0_1/3",
    "missing_1/3_2/3",
    "missing_2/3_1",
)
COLORS = {
    "B0": "#7F7F7F",
    "B1": "#000000",
    "B2": "#0072B2",
    "B3": "#E69F00",
    "B4": "#D55E00",
    "B5": "#009E73",
    "B6": "#CC79A7",
}
LABELS = {
    "B0": "B0 median imputation",
    "B1": "B1 MI mean, all singletons",
    "B2": "B2 confidence",
    "B3": "B3 missingness",
    "B4": "B4 disagreement",
    "B5": "B5 confidence+missingness risk",
    "B6": "B6 risk + disagreement",
}


class ProvenanceError(RuntimeError):
    """Raised when a run cannot be used as evidence."""


ACCEPTANCE_SCHEMA_VERSION = 1
ACCEPTANCE_STATUSES = {"accepted", "accepted_with_limits"}
ACCEPTANCE_DECISIONS = {"accepted", "accepted_with_limits"}
PATIENT_COLUMNS = [
    "split_seed",
    "model",
    "M",
    "source_M",
    "scenario",
    "alpha",
    "imputation_batch",
    "method",
    "target_acceptance",
    "selection_mode",
    "set_0",
    "set_1",
    "y_true",
    "p_mean",
    "p_std",
    "patient_id",
]

# Set only while rendering an explicitly requested, unaccepted clinical draft.
# The production path never sets this and still requires a C/E acceptance record.
_DRAFT_CONTEXT = {"active": False, "reason": ""}


def validate_draft_policy(manifest: dict, draft_unaccepted: bool, draft_reason: str | None, validation_only: bool) -> None:
    if draft_unaccepted and validation_only:
        raise ProvenanceError("--draft-unaccepted and --validation-only are mutually exclusive")
    if not draft_unaccepted:
        return
    if bool(manifest.get("synthetic")):
        raise ProvenanceError("--draft-unaccepted is only for clinical runs; use --validation-only for synthetic runs")
    if not isinstance(draft_reason, str) or not draft_reason.strip():
        raise ProvenanceError("--draft-unaccepted requires a non-empty --draft-reason")


def validate_patient_override(draft_unaccepted: bool, patient_predictions_file: Path | None) -> None:
    if patient_predictions_file is not None and not draft_unaccepted:
        raise ProvenanceError(
            "--patient-predictions is only valid with --draft-unaccepted; "
            "a non-draft run must use its own patient_predictions.csv"
        )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path, block: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(block), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_default(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if math.isnan(float(value)) else float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"not JSON serializable: {type(value)!r}")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return path.name


def verify_artifact_hashes(
    run_dir: Path,
    manifest: dict,
    allow_missing: bool = False,
    missing_out: list[str] | None = None,
    tolerate_mismatch: set[str] | None = None,
) -> dict[str, str]:
    """Verify every artifact recorded in manifest.json and return normalized hashes.

    ``allow_missing`` is used only by the explicit DRAFT-candidate path, where
    large model/mask files may not be fetched; present files are still hashed.
    """
    recorded = manifest.get("artifact_hashes") or {}
    if not recorded:
        raise ProvenanceError("manifest.json has no artifact_hashes; refusing to use the run")
    verified: dict[str, str] = {}
    problems: list[str] = []
    for raw_name, expected in recorded.items():
        relative = raw_name.replace("\\", "/")
        path = run_dir / relative
        if not path.is_file():
            if allow_missing:
                if missing_out is not None:
                    missing_out.append(relative)
                continue
            problems.append(f"missing: {relative}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            if tolerate_mismatch and relative in tolerate_mismatch:
                if missing_out is not None:
                    missing_out.append(relative)
                continue
            problems.append(f"hash mismatch: {relative} (expected {expected}, got {actual})")
            continue
        verified[relative] = actual
    if problems:
        raise ProvenanceError(
            "run integrity check failed; do not use this run as evidence:\n  "
            + "\n  ".join(problems)
        )
    return verified


def ensure_synthetic_policy(manifest: dict, validation_only: bool) -> None:
    synthetic = bool(manifest.get("synthetic"))
    if synthetic and not validation_only:
        raise ProvenanceError(
            "This is a synthetic run. It is software-validation evidence only and "
            "must not be used for paper results. Re-run with --validation-only to "
            "generate clearly watermarked QA outputs."
        )
    if validation_only and not synthetic:
        raise ProvenanceError(
            "--validation-only is only valid for synthetic runs; a clinical run must "
            "be rendered without that flag."
        )


def _nonempty_text(record: dict, key: str) -> bool:
    value = record.get(key)
    return isinstance(value, str) and value.strip() != ""


def load_acceptance(
    run_dir: Path,
    manifest: dict,
    config: dict,
    acceptance_file: Path | None,
    repo_root: Path,
) -> dict | None:
    """Load and validate the C/E acceptance record for a clinical run.

    Synthetic runs never use an acceptance record (they use --validation-only).
    A clinical run without a signed record is refused: a candidate or otherwise
    unaccepted run must not be turned into paper figures.
    """
    synthetic = bool(manifest.get("synthetic"))
    if synthetic:
        if acceptance_file is not None:
            raise ProvenanceError("--acceptance-file is only valid for clinical runs")
        return None

    run_id = str(manifest.get("run_id"))
    path = Path(acceptance_file) if acceptance_file is not None else (
        repo_root / "reviews" / "acceptance" / f"{run_id}.json"
    )
    if not path.is_file():
        raise ProvenanceError(
            "Clinical runs require a C/E-signed acceptance record before figures may be "
            f"generated. Expected {path}. A candidate or unaccepted run must not be used "
            "for paper figures; see paper/d002_readiness.md."
        )
    try:
        record = load_json(path)
    except Exception as error:
        raise ProvenanceError(f"cannot parse acceptance record {path}: {error}") from error
    if not isinstance(record, dict):
        raise ProvenanceError(f"acceptance record {path} must be a JSON object")

    def require(condition: bool, message: str) -> None:
        if not condition:
            raise ProvenanceError(f"acceptance record {path}: {message}")

    require(record.get("schema_version") == ACCEPTANCE_SCHEMA_VERSION, f"schema_version must be {ACCEPTANCE_SCHEMA_VERSION}")
    require(record.get("synthetic") is False, "synthetic must be false")
    require(record.get("status") in ACCEPTANCE_STATUSES, f"status must be one of {sorted(ACCEPTANCE_STATUSES)}")
    require(record.get("run_id") == run_id, f"run_id must match {run_id!r}")
    require(
        record.get("manifest_sha256") == sha256_file(run_dir / "manifest.json"),
        "manifest_sha256 must match this run's manifest.json",
    )
    require(
        record.get("protocol_version") == config.get("protocol_version", "v1"),
        "protocol_version must match config.yaml",
    )
    if manifest.get("data_version") is not None:
        require(record.get("data_version") == manifest.get("data_version"), "data_version must match the run manifest")
    require(_nonempty_text(record, "scope"), "scope must describe what was accepted")
    require(_nonempty_text(record, "accepted_at"), "accepted_at must be a non-empty timestamp")
    signoffs = record.get("signoffs")
    require(isinstance(signoffs, dict), "signoffs must be an object with C and E entries")
    for role in ("C", "E"):
        signoff = signoffs.get(role)
        require(isinstance(signoff, dict), f"missing {role} signoff")
        require(_nonempty_text(signoff, "name"), f"{role}.name is required")
        require(_nonempty_text(signoff, "date"), f"{role}.date is required")
        require(signoff.get("decision") in ACCEPTANCE_DECISIONS, f"{role}.decision must be one of {sorted(ACCEPTANCE_DECISIONS)}")
        require(_nonempty_text(signoff, "evidence"), f"{role}.evidence is required")
    return {"path": path, "sha256": sha256_file(path), "record": record}


def load_config(run_dir: Path) -> dict:
    path = run_dir / "config.yaml"
    if not path.is_file():
        raise ProvenanceError(f"missing config snapshot: {path}")
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ProvenanceError("config.yaml did not parse to a mapping")
    return config


def _column_equals(frame: pd.DataFrame, column: str, value) -> pd.Series:
    if column not in frame.columns:
        raise ProvenanceError(f"missing column {column!r}")
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return frame[column].isna()
    series = frame[column]
    if isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool):
        numeric = pd.to_numeric(series, errors="coerce")
        return np.isclose(numeric.astype(float), float(value), rtol=0.0, atol=1e-9)
    return series == value


def subset(frame: pd.DataFrame, label: str, **conditions) -> pd.DataFrame:
    out = frame
    for column, value in conditions.items():
        out = out[_column_equals(out, column, value)]
    if out.empty:
        raise ProvenanceError(f"no rows for {label}: {conditions}")
    return out


def one(frame: pd.DataFrame, label: str, **conditions) -> pd.Series:
    rows = subset(frame, label, **conditions)
    if len(rows) != 1:
        raise ProvenanceError(f"expected exactly one row for {label}, found {len(rows)}: {conditions}")
    return rows.iloc[0]


def _get(row: pd.Series, column: str):
    return row[column] if column in row.index else None


def primary_context(config: dict) -> dict:
    seeds = list(config.get("seeds") or [])
    capacities = [float(c) for c in (config.get("capacities") or [])]
    if not seeds or not capacities:
        raise ProvenanceError("config.yaml must define seeds and capacities")
    primary_capacity = 0.60 if any(np.isclose(c, 0.60) for c in capacities) else capacities[len(capacities) // 2]
    return {
        "split_seed": seeds[0],
        "model": "LR",
        "M": int(config.get("M", 10)),
        "source_M": int(config.get("M", 10)),
        "alpha": float(config.get("alpha", 0.10)),
        "scenario": "S0",
        "capacity": float(primary_capacity),
        "capacities": capacities,
        "scenarios": list(config.get("scenarios") or []),
        "seeds": seeds,
        "protocol_version": config.get("protocol_version", "v1"),
    }


def prepare_out_dir(out_dir: Path, overwrite: bool) -> None:
    if out_dir.exists() and any(out_dir.iterdir()) and not overwrite:
        raise ProvenanceError(
            f"output directory is not empty: {out_dir}. Use --overwrite to replace "
            "previously generated tables/figures."
        )
    out_dir.mkdir(parents=True, exist_ok=True)


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8")


def _load_csv_path(path: Path, usecols: list[str] | None = None) -> pd.DataFrame:
    if not path.is_file():
        raise ProvenanceError(f"missing result file: {path}")
    if usecols:
        try:
            return pd.read_csv(path, usecols=usecols)
        except ValueError:
            return pd.read_csv(path)
    return pd.read_csv(path)


def _load_csv(run_dir: Path, name: str, usecols: list[str] | None = None) -> pd.DataFrame:
    return _load_csv_path(run_dir / name, usecols=usecols)


def _assert_single_run(frame: pd.DataFrame, manifest: dict) -> None:
    if "run_id" in frame.columns:
        run_ids = set(frame["run_id"].dropna().astype(str))
        if run_ids != {str(manifest["run_id"])}:
            raise ProvenanceError(f"run_id mismatch in result table: {sorted(run_ids)}")
    if "synthetic" in frame.columns:
        values = set(frame["synthetic"].dropna().astype(bool))
        if values != {bool(manifest.get("synthetic"))}:
            raise ProvenanceError(
                "result table synthetic flag does not match manifest: "
                f"{values} vs {bool(manifest.get('synthetic'))}"
            )


def _status_rows(status: pd.DataFrame, ctx: dict, method: str) -> pd.Series | None:
    frame = status
    for column, value in (
        ("split_seed", ctx["split_seed"]),
        ("model", ctx["model"]),
        ("source_M", ctx["source_M"]),
        ("alpha", ctx["alpha"]),
        ("method", method),
    ):
        frame = frame[_column_equals(frame, column, value)]
    expected_m = 1 if method == "B0" else ctx["M"]
    frame = frame[_column_equals(frame, "M", expected_m)]
    if frame.empty:
        return None
    return frame.iloc[0]


def build_main_table(metrics: pd.DataFrame, status: pd.DataFrame, ctx: dict) -> pd.DataFrame:
    # B0 is a single-imputation baseline (M=1) while B1-B6 use the primary MI
    # task (M=ctx['M']).  Filter on the shared context first and choose M per
    # method; filtering globally on M would silently drop B0.
    main = subset(
        metrics,
        "primary condition",
        split_seed=ctx["split_seed"],
        model=ctx["model"],
        source_M=ctx["source_M"],
        scenario=ctx["scenario"],
        alpha=ctx["alpha"],
        imputation_batch=0,
    )
    rows = []
    for method in EXPECTED_METHODS:
        status_row = _status_rows(status, ctx, method)
        method_status = str(status_row["status"]) if status_row is not None else "unavailable"
        raw_reason = str(status_row["reason"]) if status_row is not None else "no method_status row"
        reason = "" if raw_reason in ("available", "nan", "None") else raw_reason
        conditions = dict(method=method, selection_mode="batch")
        if method == "B0":
            conditions["M"] = 1
            conditions["target_acceptance"] = None
        elif method == "B1":
            conditions["M"] = ctx["M"]
            conditions["target_acceptance"] = None
        else:
            conditions["M"] = ctx["M"]
            conditions["target_acceptance"] = ctx["capacity"]
        try:
            row = one(main, f"main {method}", **conditions)
        except ProvenanceError:
            rows.append(
                dict(
                    method=method,
                    status=method_status,
                    reason=reason,
                    target_acceptance=None if method in ("B0", "B1") else ctx["capacity"],
                )
            )
            continue
        rows.append(
            dict(
                method=method,
                status=method_status if method not in ("B0", "B1") else "available",
                reason=reason,
                target_acceptance=_get(row, "target_acceptance"),
                n=_get(row, "n"),
                positives=_get(row, "positives"),
                base_rate=_get(row, "base_rate"),
                accepted=_get(row, "accepted"),
                acceptance=_get(row, "acceptance"),
                selective_risk=_get(row, "selective_risk"),
                dangerous_miss=_get(row, "dangerous_miss"),
                negative_residual=_get(row, "negative_residual"),
                coverage=_get(row, "coverage"),
                auroc=_get(row, "auroc"),
                auprc=_get(row, "auprc"),
                pool_size=_get(row, "pool_size"),
                capacity_shortfall=_get(row, "capacity_shortfall"),
            )
        )
    return pd.DataFrame(rows)


def primary_risk_data(metrics: pd.DataFrame, ctx: dict) -> pd.DataFrame:
    """All capacities for the primary risk-acceptance figure (B0-B4, batch mode)."""
    frame = subset(
        metrics,
        "primary risk-acceptance data",
        split_seed=ctx["split_seed"],
        model=ctx["model"],
        source_M=ctx["source_M"],
        scenario=ctx["scenario"],
        alpha=ctx["alpha"],
        imputation_batch=0,
        selection_mode="batch",
    )
    keep = frame["method"].isin(["B0", "B1", "B2", "B3", "B4"])
    frame = frame[keep].copy()
    is_b0 = frame["method"] == "B0"
    frame = frame[(is_b0 & (pd.to_numeric(frame["M"], errors="coerce") == 1)) | (~is_b0 & (pd.to_numeric(frame["M"], errors="coerce") == ctx["M"]))]
    columns = [
        "method",
        "M",
        "target_acceptance",
        "n",
        "accepted",
        "acceptance",
        "selective_risk",
        "dangerous_miss",
        "negative_residual",
        "coverage",
        "pool_size",
        "capacity_shortfall",
    ]
    return frame[[c for c in columns if c in frame.columns]].sort_values(
        ["method", "target_acceptance"], na_position="first"
    )


def build_contrast_table(bootstrap: pd.DataFrame, ctx: dict) -> pd.DataFrame:
    rows = []
    for comparison in ("B4-B2", "B6-B5"):
        try:
            frame = subset(
                bootstrap,
                f"primary contrast {comparison}",
                split_seed=ctx["split_seed"],
                model=ctx["model"],
                M=ctx["M"],
                source_M=ctx["source_M"],
                scenario=ctx["scenario"],
                alpha=ctx["alpha"],
                imputation_batch=0,
                comparison=comparison,
                target_acceptance=ctx["capacity"],
            )
        except ProvenanceError:
            # B5/B6 can be unavailable by the prespecified error-count gate.
            continue
        for mode in ("batch", "frozen"):
            try:
                row = one(frame, f"contrast {comparison} {mode}", selection_mode=mode)
            except ProvenanceError:
                continue
            rows.append(
                dict(
                    comparison=comparison,
                    target_acceptance=ctx["capacity"],
                    selection_mode=mode,
                    risk_difference=_get(row, "risk_difference"),
                    ci_low=_get(row, "ci_low"),
                    ci_high=_get(row, "ci_high"),
                    valid=_get(row, "valid"),
                    invalid=_get(row, "invalid"),
                    capacity_recomputed=_get(row, "capacity_recomputed"),
                )
            )
    return pd.DataFrame(rows)


def build_scenario_table(metrics: pd.DataFrame, ctx: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = subset(
        metrics,
        "scenario slate",
        model=ctx["model"],
        M=ctx["M"],
        source_M=ctx["source_M"],
        alpha=ctx["alpha"],
        imputation_batch=0,
        target_acceptance=ctx["capacity"],
        selection_mode="batch",
    )
    rows = []
    for scenario in ctx["scenarios"]:
        for seed in ctx["seeds"]:
            try:
                b2 = one(frame, f"B2 {scenario} {seed}", split_seed=seed, scenario=scenario, method="B2")
                b4 = one(frame, f"B4 {scenario} {seed}", split_seed=seed, scenario=scenario, method="B4")
            except ProvenanceError:
                continue
            row = dict(
                scenario=scenario,
                split_seed=seed,
                B2_selective_risk=_get(b2, "selective_risk"),
                B4_selective_risk=_get(b4, "selective_risk"),
                B4_minus_B2=_get(b4, "selective_risk") - _get(b2, "selective_risk"),
                B2_acceptance=_get(b2, "acceptance"),
                B4_acceptance=_get(b4, "acceptance"),
                B2_pool_size=_get(b2, "pool_size"),
                B4_pool_size=_get(b4, "pool_size"),
            )
            try:
                b5 = one(frame, f"B5 {scenario} {seed}", split_seed=seed, scenario=scenario, method="B5")
                b6 = one(frame, f"B6 {scenario} {seed}", split_seed=seed, scenario=scenario, method="B6")
                row.update(
                    B5_selective_risk=_get(b5, "selective_risk"),
                    B6_selective_risk=_get(b6, "selective_risk"),
                    B6_minus_B5=_get(b6, "selective_risk") - _get(b5, "selective_risk"),
                )
            except ProvenanceError:
                row.update(
                    B5_selective_risk=None,
                    B6_selective_risk=None,
                    B6_minus_B5=None,
                )
            rows.append(row)
    per_seed = pd.DataFrame(rows)
    summary_rows = []
    for scenario in ctx["scenarios"]:
        part = per_seed[per_seed["scenario"] == scenario] if not per_seed.empty else per_seed
        for comparison, column in (("B4-B2", "B4_minus_B2"), ("B6-B5", "B6_minus_B5")):
            values = pd.to_numeric(part[column], errors="coerce").dropna() if not part.empty else pd.Series(dtype=float)
            if values.empty:
                continue
            summary_rows.append(
                dict(
                    scenario=scenario,
                    comparison=comparison,
                    seeds=len(values),
                    mean=float(values.mean()),
                    min=float(values.min()),
                    max=float(values.max()),
                )
            )
    return per_seed, pd.DataFrame(summary_rows)


def build_coverage_table(coverage: pd.DataFrame, ctx: dict) -> pd.DataFrame:
    frame = subset(
        coverage,
        "coverage primary",
        split_seed=ctx["split_seed"],
        model=ctx["model"],
        source_M=ctx["source_M"],
        scenario=ctx["scenario"],
        alpha=ctx["alpha"],
        imputation_batch=0,
    )
    # The median baseline is M=1; the MI methods are M=ctx['M'].
    is_mi = frame["predictor"] == "MI"
    frame = frame[
        (is_mi & (pd.to_numeric(frame["M"], errors="coerce") == ctx["M"]))
        | (~is_mi & (pd.to_numeric(frame["M"], errors="coerce") == 1))
    ]
    frame = frame[frame["stratum"].isin(STRATA_ORDER)].copy()
    frame["stratum"] = pd.Categorical(frame["stratum"], categories=STRATA_ORDER, ordered=True)
    return frame.sort_values(["predictor", "stratum"])[
        ["predictor", "stratum", "n", "covered", "coverage"]
    ].reset_index(drop=True)


def build_stability_table(stability: pd.DataFrame, ctx: dict) -> pd.DataFrame:
    frame = subset(
        stability,
        "stability primary",
        split_seed=ctx["split_seed"],
        model=ctx["model"],
        source_M=ctx["source_M"],
        alpha=ctx["alpha"],
        scenario=ctx["scenario"],
    )
    rows = []
    for method in EXPECTED_METHODS:
        method_frame = frame[frame["method"] == method]
        method_frame = method_frame[
            _column_equals(method_frame, "M", 1 if method == "B0" else ctx["M"])
        ]
        if method_frame.empty:
            continue
        if method in ("B0", "B1"):
            method_frame = method_frame[_column_equals(method_frame, "target_acceptance", None)]
            modes = ("batch",)
        else:
            method_frame = method_frame[_column_equals(method_frame, "target_acceptance", ctx["capacity"])]
            modes = ("batch", "frozen")
        for mode in modes:
            part = method_frame[_column_equals(method_frame, "selection_mode", mode)]
            values = pd.to_numeric(part["disagreement"], errors="coerce").dropna()
            if values.empty:
                continue
            rows.append(
                dict(
                    method=method,
                    selection_mode=mode,
                    mean_disagreement=float(values.mean()),
                    min_disagreement=float(values.min()),
                    max_disagreement=float(values.max()),
                    pairs=int(len(values)),
                )
            )
    return pd.DataFrame(rows)


def cohort_tables(cohort_path: Path, audit_path: Path, config: dict, manifest: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    if cohort_path.suffix.lower() in {".parquet", ".pq"}:
        cohort = pd.read_parquet(cohort_path)
    else:
        cohort = pd.read_csv(cohort_path)
    audit = load_json(audit_path)
    if bool(audit.get("synthetic")) != bool(manifest.get("synthetic")):
        raise ProvenanceError(
            "cohort audit synthetic flag does not match the run manifest; refusing to combine them"
        )
    if "y_true" not in cohort.columns:
        raise ProvenanceError("cohort table must contain y_true")
    sites = sorted(cohort["site"].dropna().astype(str).unique()) if "site" in cohort.columns else ["all"]
    exclusions = audit.get("exclusion_counts") or {}
    summary_rows = []
    for site in sites:
        part = cohort if site == "all" else cohort[cohort["site"].astype(str) == site]
        positives = int(part["y_true"].sum())
        summary_rows.append(
            dict(
                site=site,
                n=int(len(part)),
                positives=positives,
                base_rate=float(part["y_true"].mean()) if len(part) else None,
                included=exclusions.get("included"),
                excluded=exclusions.get("excluded"),
                data_version=audit.get("data_version"),
                protocol_version=audit.get("protocol_version"),
                synthetic=bool(audit.get("synthetic")),
                warning=audit.get("warning", ""),
            )
        )
    summary = pd.DataFrame(summary_rows)
    features = [f for f in (config.get("features") or []) if f in cohort.columns]
    rows = []
    for feature in features:
        row = dict(
            feature=feature,
            overall_missing=float(cohort[feature].isna().mean()),
            n=int(len(cohort)),
        )
        for site in sites:
            if site == "all":
                continue
            part = cohort[cohort["site"].astype(str) == site]
            row[f"missing_site_{site}"] = float(part[feature].isna().mean()) if len(part) else None
        rows.append(row)
    missingness = pd.DataFrame(rows).sort_values("overall_missing", ascending=False).reset_index(drop=True)
    return summary, missingness


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        return (float("nan"), float("nan"))
    p = successes / total
    denominator = 1.0 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return (centre - half, centre + half)


def _watermark(fig: plt.Figure, synthetic: bool) -> None:
    if synthetic:
        fig.supxlabel(
            "SYNTHETIC SOFTWARE VALIDATION — NOT CLINICAL EVIDENCE (do not cite as a clinical result)",
            color="#B00020",
            fontsize=7.0,
            fontweight="bold",
        )
        fig.text(
            0.5,
            0.5,
            "SYNTHETIC",
            ha="center",
            va="center",
            fontsize=34,
            color="#B00020",
            alpha=0.055,
            rotation=24,
            zorder=1000,
        )
        return
    if _DRAFT_CONTEXT["active"]:
        reason = _DRAFT_CONTEXT.get("reason", "")
        suffix = f" | {reason}" if reason else ""
        fig.supxlabel(
            "DRAFT — UNACCEPTED CLINICAL CANDIDATE — NOT FOR SUBMISSION" + suffix,
            color="#B00020",
            fontsize=6.8,
            fontweight="bold",
        )
        fig.text(
            0.5,
            0.5,
            "DRAFT",
            ha="center",
            va="center",
            fontsize=34,
            color="#B00020",
            alpha=0.055,
            rotation=24,
            zorder=1000,
        )


def _style() -> None:
    plt.rcParams.update(
        {
            "font.size": 8.5,
            "axes.titlesize": 9.5,
            "axes.labelsize": 8.5,
            "legend.fontsize": 7.5,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def _save(fig: plt.Figure, out_dir: Path, stem: str, formats: list[str], synthetic: bool) -> list[Path]:
    _watermark(fig, synthetic)
    paths = []
    for extension in formats:
        path = out_dir / f"{stem}.{extension}"
        fig.savefig(path, bbox_inches="tight")
        paths.append(path)
    plt.close(fig)
    return paths


def figure_risk_acceptance(metrics: pd.DataFrame, bootstrap: pd.DataFrame, ctx: dict, out_dir: Path, formats: list[str], synthetic: bool) -> list[Path]:
    primary = subset(
        metrics,
        "primary risk-acceptance slice",
        split_seed=ctx["split_seed"],
        model=ctx["model"],
        source_M=ctx["source_M"],
        scenario=ctx["scenario"],
        alpha=ctx["alpha"],
        imputation_batch=0,
    )
    fig, (ax1, ax2) = plt.subplots(
        1,
        2,
        figsize=(7.8, 3.3),
        gridspec_kw={"width_ratios": [1.2, 1]},
        layout="constrained",
    )
    for method in ("B2", "B3", "B4"):
        part = primary[primary["method"] == method].copy()
        part = part[_column_equals(part, "M", ctx["M"])]
        part = part[_column_equals(part, "selection_mode", "batch")]
        part = part[pd.to_numeric(part["target_acceptance"], errors="coerce").notna()]
        part = part.sort_values("target_acceptance")
        part = part[pd.to_numeric(part["acceptance"], errors="coerce").notna()]
        ax1.plot(
            pd.to_numeric(part["acceptance"]),
            pd.to_numeric(part["selective_risk"]),
            marker="o" if method != "B3" else "s",
            linewidth=1.6,
            markersize=5,
            color=COLORS[method],
            label=LABELS[method],
        )
        for _, row in part.iterrows():
            ax1.annotate(
                f"c={float(row['target_acceptance']):.2f}",
                (float(row["acceptance"]), float(row["selective_risk"])),
                textcoords="offset points",
                xytext=(5, 4),
                fontsize=6.5,
                color=COLORS[method],
            )
    for method in ("B0", "B1"):
        part = primary[primary["method"] == method]
        part = part[_column_equals(part, "M", 1 if method == "B0" else ctx["M"])]
        part = part[_column_equals(part, "selection_mode", "batch")]
        part = part[_column_equals(part, "target_acceptance", None)]
        if not part.empty:
            row = part.iloc[0]
            if pd.notna(row.get("acceptance")) and pd.notna(row.get("selective_risk")):
                ax1.scatter(
                    float(row["acceptance"]),
                    float(row["selective_risk"]),
                    marker="*" if method == "B1" else "D",
                    s=70,
                    color=COLORS[method],
                    label=LABELS[method],
                    zorder=5,
                )
    shortfall = primary[
        primary["method"].isin(["B2", "B3", "B4"])
        & _column_equals(primary, "M", ctx["M"])
        & _column_equals(primary, "selection_mode", "batch")
        & _column_equals(primary, "capacity_shortfall", True)
    ]
    if not shortfall.empty and len(shortfall) == len(
        primary[
            primary["method"].isin(["B2", "B3", "B4"])
            & _column_equals(primary, "M", ctx["M"])
            & _column_equals(primary, "selection_mode", "batch")
        ]
    ):
        ax1.text(
            0.02,
            0.98,
            "Capacity shortfall: every target exceeds the\nsingleton pool, so ranking cannot differentiate\nmethods. Do not interpret this run's contrasts.",
            transform=ax1.transAxes,
            fontsize=6.2,
            color="#B00020",
            va="top",
            ha="left",
        )
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_xlabel("Actual acceptance proportion")
    ax1.set_ylabel("Selective risk (error rate among accepted)")
    ax1.set_title("A. Risk vs acceptance")
    ax1.legend(frameon=False, loc="lower right")

    rows = bootstrap[
        (bootstrap["comparison"] == "B4-B2")
        & (_column_equals(bootstrap, "selection_mode", "batch"))
    ].copy()
    rows = rows.sort_values("target_acceptance")
    x = pd.to_numeric(rows["target_acceptance"])
    y = pd.to_numeric(rows["risk_difference"])
    low = pd.to_numeric(rows["ci_low"])
    high = pd.to_numeric(rows["ci_high"])
    yerr = np.vstack([(y - low).fillna(0).to_numpy(), (high - y).fillna(0).to_numpy()])
    ax2.axhline(0, color="#555555", linewidth=0.8)
    ax2.errorbar(x, y, yerr=yerr, fmt="o", color=COLORS["B4"], capsize=3, linewidth=1.2)
    ax2.set_xlabel("Target acceptance proportion c")
    ax2.set_ylabel("Risk difference: B4 − B2")
    ax2.set_title("B. B4 − B2 (negative favours B4)")
    ax2.set_xlim(0.3, 0.9)
    ax1.grid(axis="y", color="#DDDDDD", linewidth=0.5)
    ax2.grid(axis="y", color="#DDDDDD", linewidth=0.5)
    return _save(fig, out_dir, "fig2_risk_acceptance", formats, synthetic)


def figure_scenarios(summary: pd.DataFrame, ctx: dict, out_dir: Path, formats: list[str], synthetic: bool) -> list[Path]:
    fig, ax = plt.subplots(figsize=(3.9, 3.1), layout="constrained")
    scenarios = [s for s in ctx["scenarios"] if s in set(summary["scenario"])]
    positions = {scenario: index for index, scenario in enumerate(scenarios)}
    for comparison, color, marker in (("B4-B2", COLORS["B4"], "o"), ("B6-B5", COLORS["B6"], "s")):
        part = summary[summary["comparison"] == comparison].set_index("scenario")
        xs, means, lows, highs = [], [], [], []
        for scenario in scenarios:
            if scenario not in part.index:
                continue
            row = part.loc[scenario]
            xs.append(positions[scenario])
            means.append(float(row["mean"]))
            lows.append(float(row["min"]))
            highs.append(float(row["max"]))
        means_array = np.asarray(means)
        yerr = np.vstack([means_array - np.asarray(lows), np.asarray(highs) - means_array])
        ax.errorbar(xs, means_array, yerr=yerr, fmt=marker, capsize=3, linewidth=1.2, color=color, label=comparison)
    ax.axhline(0, color="#555555", linewidth=0.8)
    ax.set_xticks(
        range(len(scenarios)),
        [scenario + ("\nexternal" if scenario == "S4" else "") for scenario in scenarios],
    )
    ax.set_xlabel("Scenario")
    ax.set_ylabel("Risk difference (B4−B2 / B6−B5)")
    ax.set_title("Scenario robustness (mean, min–max)")
    ax.legend(frameon=False)
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.5)
    if "B6-B5" not in set(summary["comparison"]):
        ax.text(
            0.02,
            0.98,
            "B6−B5 unavailable\n(B5/B6 below the 20-error gate)",
            transform=ax.transAxes,
            fontsize=6.2,
            color="#B00020",
            va="top",
            ha="left",
        )
    return _save(fig, out_dir, "fig3_scenarios", formats, synthetic)


def figure_coverage(coverage: pd.DataFrame, ctx: dict, out_dir: Path, formats: list[str], synthetic: bool) -> list[Path]:
    fig, ax = plt.subplots(figsize=(5.4, 3.2), layout="constrained")
    predictors = [p for p in ("MI", "median") if p in set(coverage["predictor"])]
    width = 0.36
    x = np.arange(len(STRATA_ORDER))
    for offset_index, predictor in enumerate(predictors):
        values, ns = [], []
        for stratum in STRATA_ORDER:
            part = coverage[(coverage["predictor"] == predictor) & (coverage["stratum"] == stratum)]
            values.append(float(part["coverage"].iloc[0]) if not part.empty and pd.notna(part["coverage"].iloc[0]) else np.nan)
            ns.append(int(part["n"].iloc[0]) if not part.empty else 0)
        offset = (offset_index - (len(predictors) - 1) / 2) * width
        bars = ax.bar(
            x + offset,
            values,
            width=width,
            color="#0072B2" if predictor == "MI" else "#999999",
            label="MI (B1–B6)" if predictor == "MI" else "median (B0)",
        )
        for bar, n_value, value in zip(bars, ns, values):
            if n_value == 0 or not np.isfinite(value):
                ax.text(bar.get_x() + bar.get_width() / 2, 0.015, "n=0", ha="center", va="bottom", fontsize=5.8, color="#666666")
            elif value == 0:
                ax.text(bar.get_x() + bar.get_width() / 2, 0.015, f"0/{n_value}", ha="center", va="bottom", fontsize=5.8, color="#B00020")
            else:
                ax.text(bar.get_x() + bar.get_width() / 2, value + 0.012, f"n={n_value}", ha="center", va="bottom", fontsize=5.8, color="#333333")
    ax.axhline(1 - ctx["alpha"], color="#B00020", linestyle="--", linewidth=0.9, label=f"1−alpha = {1 - ctx['alpha']:.2f}")
    labels = ["all", "y=0", "y=1", "miss≤1/3", "miss 1/3–2/3", "miss>2/3"]
    ax.set_xticks(x, labels, fontsize=6.8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Original-set coverage")
    ax.set_title("Coverage by stratum (S0, primary seed)")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3)
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.5)
    return _save(fig, out_dir, "fig4_coverage", formats, synthetic)


def disagreement_data(patient_predictions: pd.DataFrame, ctx: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = subset(
        patient_predictions,
        "patient predictions",
        split_seed=ctx["split_seed"],
        model=ctx["model"],
        M=ctx["M"],
        source_M=ctx["source_M"],
        scenario=ctx["scenario"],
        alpha=ctx["alpha"],
        imputation_batch=0,
        method="B4",
        target_acceptance=ctx["capacity"],
        selection_mode="batch",
    )
    if frame["patient_id"].duplicated().any():
        raise ProvenanceError("patient_predictions is not one row per patient for the selected condition")
    singleton = frame["set_0"].astype(bool) != frame["set_1"].astype(bool)
    sub = frame[singleton].copy()
    sub["singleton_prediction"] = sub["set_1"].astype(int)
    sub["error"] = sub["singleton_prediction"] != sub["y_true"].astype(int)
    if sub.empty:
        raise ProvenanceError("no singleton predictions for the disagreement diagnostic")
    sub["quintile"] = pd.qcut(pd.to_numeric(sub["p_std"]), 5, labels=False, duplicates="drop")
    rows = []
    for quintile, part in sub.groupby("quintile", dropna=True):
        n = int(len(part))
        errors = int(part["error"].sum())
        low, high = wilson_interval(errors, n)
        rows.append(
            dict(
                quintile=int(quintile) + 1,
                n=n,
                errors=errors,
                error_rate=errors / n,
                ci_low=low,
                ci_high=high,
                p_std_min=float(part["p_std"].min()),
                p_std_max=float(part["p_std"].max()),
            )
        )
    return pd.DataFrame(rows), sub


def figure_disagreement(quintiles: pd.DataFrame, patients: pd.DataFrame, out_dir: Path, formats: list[str], synthetic: bool) -> list[Path]:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.4, 3.1), layout="constrained")
    y = quintiles["error_rate"].to_numpy(dtype=float)
    low = quintiles["ci_low"].to_numpy(dtype=float)
    high = quintiles["ci_high"].to_numpy(dtype=float)
    x = quintiles["quintile"].to_numpy(dtype=float)
    ax1.errorbar(x, y, yerr=np.vstack([y - low, high - y]), fmt="o-", color=COLORS["B4"], capsize=3)
    for _, row in quintiles.iterrows():
        offset = (4, -10) if row["error_rate"] > 0.9 else (4, 4)
        ax1.annotate(f"n={int(row['n'])}", (row["quintile"], row["error_rate"]), textcoords="offset points", xytext=offset, fontsize=6.5)
    ax1.set_xticks(quintiles["quintile"], quintiles["quintile"])
    ax1.set_xlabel("Imputation-disagreement quintile (low → high)")
    ax1.set_ylabel("Error rate among singleton predictions")
    total_errors = int(patients["error"].sum())
    total_n = int(len(patients))
    upper = float(pd.to_numeric(quintiles["ci_high"], errors="coerce").max())
    upper = 0.05 if not np.isfinite(upper) else max(0.05, min(1.0, upper * 1.15))
    ax1.set_ylim(0, upper)
    ax1.set_title("A. Error by disagreement quintile")
    ax1.text(
        0.02,
        0.98,
        f"{total_n} singleton predictions, {total_errors} errors",
        transform=ax1.transAxes,
        fontsize=6.5,
        va="top",
        ha="left",
        color="#333333",
    )
    if total_errors < 10:
        ax1.text(
            0.02,
            0.90,
            "Sparse errors; descriptive only",
            transform=ax1.transAxes,
            fontsize=6.2,
            va="top",
            ha="left",
            color="#B00020",
        )
    ax1.grid(axis="y", color="#DDDDDD", linewidth=0.5)

    correct = patients[~patients["error"].astype(bool)]
    errors = patients[patients["error"].astype(bool)]
    ax2.scatter(correct["p_mean"], correct["p_std"], s=12, alpha=0.55, color="#0072B2", label=f"correct (n={len(correct)})")
    ax2.scatter(errors["p_mean"], errors["p_std"], s=18, alpha=0.75, color="#D55E00", label=f"error (n={len(errors)})")
    ax2.set_xlabel("Mean imputation probability")
    ax2.set_ylabel("Imputation disagreement (SD)")
    ax2.set_xlim(0, 1)
    ax2.set_title("B. Singleton predictions")
    ax2.legend(frameon=False, loc="upper left")
    ax2.grid(color="#DDDDDD", linewidth=0.5)
    return _save(fig, out_dir, "fig5_disagreement", formats, synthetic)


def figure_stability(stability: pd.DataFrame, ctx: dict, out_dir: Path, formats: list[str], synthetic: bool) -> list[Path]:
    fig, ax = plt.subplots(figsize=(5.4, 3.0), layout="constrained")
    methods = [m for m in EXPECTED_METHODS if m in set(stability["method"])]
    x = np.arange(len(methods))
    width = 0.36
    for offset_index, mode in enumerate(("batch", "frozen")):
        part = stability[stability["selection_mode"] == mode].set_index("method")
        values, low_err, high_err = [], [], []
        for method in methods:
            if method in part.index:
                row = part.loc[method]
                mean = float(row["mean_disagreement"])
                values.append(mean)
                low_err.append(mean - float(row["min_disagreement"]))
                high_err.append(float(row["max_disagreement"]) - mean)
            else:
                values.append(np.nan)
                low_err.append(0)
                high_err.append(0)
        offset = (offset_index - 0.5) * width
        bars = ax.bar(
            x + offset,
            values,
            width=width,
            yerr=np.vstack([low_err, high_err]),
            capsize=2,
            color="#0072B2" if mode == "batch" else "#D55E00",
            label="batch capacity" if mode == "batch" else "frozen threshold",
        )
        for bar, value in zip(bars, values):
            if not np.isfinite(value):
                ax.text(bar.get_x() + bar.get_width() / 2, 0.005, "n/a", ha="center", va="bottom", fontsize=6, color="#666666")
    ax.set_xticks(x, methods)
    ax.set_ylabel("Disagreement rate across batches")
    ax.set_title("Test-time stability (S0, c=0.60)")
    ax.set_ylim(0, 1)
    ax.legend(frameon=False, loc="upper right")
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.5)
    return _save(fig, out_dir, "fig6_stability", formats, synthetic)


def figure_missingness(missingness: pd.DataFrame, out_dir: Path, formats: list[str], synthetic: bool) -> list[Path]:
    data = missingness.copy()
    data = data.sort_values("overall_missing", ascending=True)
    fig, ax = plt.subplots(figsize=(4.4, max(3.0, 0.13 * len(data) + 1.0)), layout="constrained")
    y = np.arange(len(data))
    ax.barh(y, data["overall_missing"], color="#0072B2", height=0.7, label="overall")
    site_columns = [c for c in data.columns if c.startswith("missing_site_")]
    markers = ("o", "s", "^", "D")
    for index, column in enumerate(site_columns):
        ax.scatter(data[column], y, marker=markers[index % len(markers)], s=12, color="#D55E00" if index == 0 else "#009E73", label=column.replace("missing_site_", "site "), zorder=4)
    ax.set_yticks(y, data["feature"], fontsize=6.5)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Missing fraction")
    ax.set_title("Feature missingness (delivered cohort)")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", color="#DDDDDD", linewidth=0.5)
    return _save(fig, out_dir, "fig1_missingness", formats, synthetic)


def build_outputs(run_dir: Path, out_dir: Path, cohort_path: Path | None, audit_path: Path | None, formats: list[str], validation_only: bool, overwrite: bool, repo_root: Path, acceptance_file: Path | None = None, draft_unaccepted: bool = False, draft_reason: str | None = None, patient_predictions_file: Path | None = None) -> dict:
    global _DRAFT_CONTEXT
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.is_file():
        raise ProvenanceError(f"missing manifest.json in {run_dir}")
    manifest = load_json(manifest_path)
    if manifest.get("run_status") != "completed":
        raise ProvenanceError(f"run_status is {manifest.get('run_status')!r}; only completed runs may be rendered")
    if str(manifest.get("run_id")) != run_dir.name:
        raise ProvenanceError("manifest run_id does not match the run directory name")
    ensure_synthetic_policy(manifest, validation_only)
    validate_draft_policy(manifest, draft_unaccepted, draft_reason, validation_only)
    config = load_config(run_dir)
    if draft_unaccepted:
        acceptance = None
        draft = True
        _DRAFT_CONTEXT = {"active": True, "reason": str(draft_reason).strip()}
    else:
        acceptance = load_acceptance(run_dir, manifest, config, acceptance_file, repo_root)
        draft = False
        _DRAFT_CONTEXT = {"active": False, "reason": ""}
    missing_artifacts: list[str] = []
    verified = verify_artifact_hashes(
        run_dir,
        manifest,
        allow_missing=draft,
        missing_out=missing_artifacts,
        tolerate_mismatch={"patient_predictions.csv"} if draft else None,
    )

    metrics = _load_csv(run_dir, "metrics.csv")
    coverage = _load_csv(run_dir, "coverage_strata.csv")
    bootstrap = _load_csv(run_dir, "bootstrap_differences.csv")
    stability = _load_csv(run_dir, "stability.csv")
    status = _load_csv(run_dir, "method_status.csv")
    validate_patient_override(draft, patient_predictions_file)
    patient_predictions = None
    patient_source = None
    patient_path = run_dir / "patient_predictions.csv"
    if patient_predictions_file is not None:
        patient_predictions = _load_csv_path(patient_predictions_file, usecols=PATIENT_COLUMNS)
        patient_source = {
            "path": display_path(patient_predictions_file, repo_root),
            "sha256": sha256_file(patient_predictions_file),
            "rows": int(len(patient_predictions)),
            "note": "DRAFT-mode pre-filtered patient-level extract; full-file hash recorded in the run manifest",
        }
    elif (
        patient_path.is_file()
        and patient_path.stat().st_size > 0
        and "patient_predictions.csv" not in missing_artifacts
    ):
        patient_predictions = _load_csv(run_dir, "patient_predictions.csv", usecols=PATIENT_COLUMNS)
    elif not draft:
        raise ProvenanceError("missing patient_predictions.csv for a non-draft run")
    for frame in (metrics, coverage, bootstrap):
        _assert_single_run(frame, manifest)

    ctx = primary_context(config)
    if ctx["protocol_version"] != manifest.get("protocol_version", ctx["protocol_version"]) and "protocol_version" in manifest:
        raise ProvenanceError("protocol version mismatch between config and manifest")
    prepare_out_dir(out_dir, overwrite)

    main = build_main_table(metrics, status, ctx)
    risk_data = primary_risk_data(metrics, ctx)
    contrasts = build_contrast_table(bootstrap, ctx)
    scenario_per_seed, scenario_summary = build_scenario_table(metrics, ctx)
    coverage_table = build_coverage_table(coverage, ctx)
    stability_table = build_stability_table(stability, ctx)
    if patient_predictions is not None:
        quintiles, patients = disagreement_data(patient_predictions, ctx)
    else:
        quintiles, patients = None, None

    artifacts: list[Path] = []
    tables_dir = out_dir / "tables"
    figures_dir = out_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    def stamp(frame: pd.DataFrame) -> pd.DataFrame:
        """Stamp every table with run_id, synthetic and draft flags for traceability."""
        out = frame.copy()
        if "run_id" not in out.columns:
            out.insert(0, "run_id", manifest.get("run_id"))
        if "synthetic" not in out.columns:
            out.insert(1, "synthetic", bool(manifest.get("synthetic")))
        if "draft" not in out.columns:
            out.insert(2, "draft", draft)
        if "draft_reason" not in out.columns:
            out.insert(3, "draft_reason", str(draft_reason).strip() if draft and draft_reason else "")
        return out

    table_specs = [
        ("table2_main_results.csv", main),
        ("table2b_primary_contrasts.csv", contrasts),
        ("table3_scenario_per_seed.csv", scenario_per_seed),
        ("table3_scenario_summary.csv", scenario_summary),
        ("table4_coverage_strata.csv", coverage_table),
        ("table5_stability.csv", stability_table),
        ("fig2_risk_acceptance_data.csv", risk_data),
        ("fig2_contrast_data.csv", contrasts),
        ("fig3_scenario_data.csv", scenario_summary),
        ("fig4_coverage_data.csv", coverage_table),
        ("fig6_stability_data.csv", stability_table),
    ]
    if quintiles is not None:
        table_specs.append(("fig5_disagreement_data.csv", quintiles))
    for name, frame in table_specs:
        path = tables_dir / name
        write_csv(stamp(frame), path)
        artifacts.append(path)

    if cohort_path is not None and audit_path is not None:
        cohort_summary, missingness = cohort_tables(cohort_path, audit_path, config, manifest)
        for name, frame in (
            ("table1_cohort_summary.csv", cohort_summary),
            ("table1_feature_missingness.csv", missingness),
            ("fig1_missingness_data.csv", missingness),
        ):
            path = tables_dir / name
            write_csv(stamp(frame), path)
            artifacts.append(path)
        artifacts.extend(figure_missingness(missingness, figures_dir, formats, bool(manifest.get("synthetic"))))
    elif cohort_path is not None or audit_path is not None:
        raise ProvenanceError("--cohort and --audit must be supplied together")

    synthetic = bool(manifest.get("synthetic"))
    artifacts.extend(figure_risk_acceptance(metrics, bootstrap, ctx, figures_dir, formats, synthetic))
    artifacts.extend(figure_scenarios(scenario_summary, ctx, figures_dir, formats, synthetic))
    artifacts.extend(figure_coverage(coverage_table, ctx, figures_dir, formats, synthetic))
    skipped = []
    if patients is not None:
        artifacts.extend(figure_disagreement(quintiles, patients, figures_dir, formats, synthetic))
    else:
        skipped.append("fig5_disagreement: patient_predictions.csv not available in the draft fetch")
    artifacts.extend(figure_stability(stability_table, ctx, figures_dir, formats, synthetic))

    output_hashes = {
        str(path.relative_to(out_dir)).replace("\\", "/"): sha256_file(path)
        for path in sorted(artifacts)
        if path.is_file()
    }
    provenance = {
        "schema_version": 1,
        "generated_at_utc": utc_now(),
        "validation_only": validation_only,
        "status": (
            "SYNTHETIC_VALIDATION"
            if synthetic
            else ("DRAFT_CANDIDATE_NOT_ACCEPTED" if draft else "ACCEPTED_CLINICAL")
        ),
        "draft_reason": str(draft_reason).strip() if draft and draft_reason else None,
        "script": {
            "path": display_path(Path(__file__).resolve(), repo_root),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "run": {
            "run_id": manifest.get("run_id"),
            "run_dir": display_path(run_dir, repo_root),
            "manifest_sha256": sha256_file(manifest_path),
            "synthetic": synthetic,
            "run_status": manifest.get("run_status"),
            "data_version": manifest.get("data_version"),
            "protocol_version": config.get("protocol_version", "v1"),
            "config_sha256": manifest.get("config_sha256"),
        },
        "acceptance": None if acceptance is None else {
            "path": display_path(acceptance["path"], repo_root),
            "sha256": acceptance["sha256"],
            "status": acceptance["record"].get("status"),
            "scope": acceptance["record"].get("scope"),
            "accepted_at": acceptance["record"].get("accepted_at"),
            "signoffs": {
                role: {
                    "decision": acceptance["record"]["signoffs"][role].get("decision"),
                    "date": acceptance["record"]["signoffs"][role].get("date"),
                }
                for role in ("C", "E")
            },
        },
        "filters": {
            "primary_seed": ctx["split_seed"],
            "model": ctx["model"],
            "M": ctx["M"],
            "alpha": ctx["alpha"],
            "primary_scenario": ctx["scenario"],
            "primary_capacity": ctx["capacity"],
            "scenarios": ctx["scenarios"],
            "seeds": ctx["seeds"],
        },
        "inputs": verified,
        "inputs_missing": missing_artifacts if draft else [],
        "patient_predictions_source": patient_source,
        "skipped": skipped,
        "outputs": output_hashes,
        "cohort": {
            "provided": cohort_path is not None,
            "cohort": display_path(cohort_path, repo_root) if cohort_path else None,
            "audit": display_path(audit_path, repo_root) if audit_path else None,
        },
        "warning": (
            "Synthetic software-validation outputs only; not clinical evidence."
            if synthetic
            else (
                "DRAFT from an unaccepted clinical run; not for submission or citation."
                if draft
                else "Clinical run with a C/E acceptance record; check the record's scope and evidence before citing."
            )
        ),
    }
    provenance_path = out_dir / "provenance.json"
    provenance_path.write_text(json.dumps(provenance, ensure_ascii=False, indent=2, default=_json_default), encoding="utf-8")
    (out_dir / "README.txt").write_text(
        (
            "Generated by scripts/make_figures.py.\n"
            f"run_id: {manifest.get('run_id')}\n"
            f"synthetic: {synthetic}\n"
            f"validation_only: {validation_only}\n"
            f"status: {provenance['status']}\n"
            f"draft_reason: {provenance['draft_reason'] or ''}\n"
            f"acceptance: {display_path(acceptance['path'], repo_root) if acceptance else ('not required (draft unaccepted)' if draft else 'not required (synthetic validation)')}\n"
            "Every table/figure here is computed from the run listed in provenance.json.\n"
            "Do not hand-edit numbers; regenerate from a new immutable run instead.\n"
            + ("\nTHIS IS SYNTHETIC SOFTWARE VALIDATION, NOT CLINICAL EVIDENCE.\n" if synthetic else "")
            + ("\nTHIS IS A DRAFT FROM AN UNACCEPTED CLINICAL RUN; NOT FOR SUBMISSION.\n" if draft else "")
        ),
        encoding="utf-8",
    )
    _DRAFT_CONTEXT = {"active": False, "reason": ""}
    return {
        "out_dir": str(out_dir),
        "tables": len([p for p in artifacts if p.parent == tables_dir]),
        "figures": len([p for p in artifacts if p.parent == figures_dir]),
        "synthetic": synthetic,
        "status": provenance["status"],
        "draft": draft,
        "draft_reason": provenance["draft_reason"],
        "provenance": str(provenance_path),
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, help="completed run directory containing manifest.json")
    parser.add_argument("--out-dir", default=None, help="output directory; defaults to paper/runs/<run_id>, paper/draft-runs/<run_id> or paper/validation/<run_id>")
    parser.add_argument("--cohort", default=None, help="delivered cohort table (CSV/Parquet) for Table 1 and Figure 1")
    parser.add_argument("--audit", default=None, help="cohort audit JSON for Table 1")
    parser.add_argument("--formats", default="pdf,png", help="comma-separated figure formats (default: pdf,png)")
    parser.add_argument("--validation-only", action="store_true", help="required to render a synthetic run; outputs are watermarked QA artifacts")
    parser.add_argument(
        "--acceptance-file",
        default=None,
        help="C/E-signed acceptance JSON for a clinical run; defaults to reviews/acceptance/<run_id>.json",
    )
    parser.add_argument(
        "--draft-unaccepted",
        action="store_true",
        help="render an unaccepted clinical candidate as DRAFT only; requires --draft-reason; never for submission",
    )
    parser.add_argument(
        "--draft-reason",
        default=None,
        help="why the unaccepted clinical candidate is being rendered (required with --draft-unaccepted)",
    )
    parser.add_argument(
        "--patient-predictions",
        default=None,
        help="DRAFT-only pre-filtered patient_predictions CSV (e.g., one condition extracted from the bundle); requires --draft-unaccepted",
    )
    parser.add_argument("--overwrite", action="store_true", help="allow replacing a non-empty output directory")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    run_dir = Path(args.run_dir).resolve()
    manifest = load_json(run_dir / "manifest.json")
    synthetic = bool(manifest.get("synthetic"))
    default_parent = "paper/validation" if synthetic else ("paper/draft-runs" if args.draft_unaccepted else "paper/runs")
    out_dir = Path(args.out_dir) if args.out_dir else (
        repo_root / default_parent / str(manifest.get("run_id"))
    )
    formats = [item.strip().lower() for item in args.formats.split(",") if item.strip()]
    allowed = {"pdf", "png", "svg"}
    if not formats or any(item not in allowed for item in formats):
        raise SystemExit(f"--formats must be a comma-separated subset of {sorted(allowed)}")
    cohort_path = Path(args.cohort).resolve() if args.cohort else None
    audit_path = Path(args.audit).resolve() if args.audit else None
    acceptance_file = Path(args.acceptance_file).resolve() if args.acceptance_file else None
    patient_predictions_file = Path(args.patient_predictions).resolve() if args.patient_predictions else None
    try:
        result = build_outputs(
            run_dir=run_dir,
            out_dir=out_dir.resolve(),
            cohort_path=cohort_path,
            audit_path=audit_path,
            formats=formats,
            validation_only=args.validation_only,
            overwrite=args.overwrite,
            repo_root=repo_root,
            acceptance_file=acceptance_file,
            draft_unaccepted=args.draft_unaccepted,
            draft_reason=args.draft_reason,
            patient_predictions_file=patient_predictions_file,
        )
    except ProvenanceError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
