"""Checks for the D-001 figure pipeline.

These tests do not render figures; they cover the provenance guards and the
per-method M selection that previously could silently drop B0 (M=1) or the
median coverage baseline.
"""
import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("make_figures", ROOT / "scripts" / "make_figures.py")
make_figures = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(make_figures)


def test_synthetic_policy_requires_explicit_validation_flag():
    with pytest.raises(make_figures.ProvenanceError):
        make_figures.ensure_synthetic_policy({"synthetic": True}, validation_only=False)
    make_figures.ensure_synthetic_policy({"synthetic": True}, validation_only=True)
    make_figures.ensure_synthetic_policy({"synthetic": False}, validation_only=False)
    with pytest.raises(make_figures.ProvenanceError):
        make_figures.ensure_synthetic_policy({"synthetic": False}, validation_only=True)


def test_artifact_hash_verification_detects_tampering(tmp_path):
    path = tmp_path / "metrics.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")
    manifest = {"artifact_hashes": {"metrics.csv": make_figures.sha256_file(path)}}
    verified = make_figures.verify_artifact_hashes(tmp_path, manifest)
    assert verified["metrics.csv"] == manifest["artifact_hashes"]["metrics.csv"]
    path.write_text("a,b\n1,3\n", encoding="utf-8")
    with pytest.raises(make_figures.ProvenanceError, match="hash mismatch"):
        make_figures.verify_artifact_hashes(tmp_path, manifest)


def test_primary_context_uses_protocol_capacity_and_first_seed():
    context = make_figures.primary_context(
        {
            "seeds": [2026, 2027],
            "M": 10,
            "alpha": 0.1,
            "capacities": [0.4, 0.6, 0.8],
            "scenarios": ["S0", "S1"],
        }
    )
    assert context["split_seed"] == 2026
    assert context["capacity"] == 0.6
    assert context["M"] == 10


def _metric_row(method, m_value, target, accepted):
    return {
        "split_seed": 2026,
        "model": "LR",
        "M": m_value,
        "source_M": 10,
        "scenario": "S0",
        "alpha": 0.1,
        "imputation_batch": 0,
        "selection_mode": "batch",
        "method": method,
        "target_acceptance": target,
        "n": 120,
        "positives": 61,
        "base_rate": 61 / 120,
        "accepted": accepted,
        "acceptance": accepted / 120,
        "selective_risk": 0.5,
        "dangerous_miss": 0.1,
        "negative_residual": 0.2,
        "coverage": 0.9,
        "auroc": 0.7,
        "auprc": 0.4,
        "pool_size": 60,
        "capacity_shortfall": False,
    }


def test_main_table_keeps_b0_with_m1():
    metrics = pd.DataFrame(
        [_metric_row("B0", 1, None, 19)]
        + [_metric_row("B1", 10, None, 11)]
        + [_metric_row(method, 10, 0.6, 11) for method in ("B2", "B3", "B4", "B5", "B6")]
    )
    status = pd.DataFrame(
        [
            {
                "split_seed": 2026,
                "model": "LR",
                "M": 1 if method == "B0" else 10,
                "source_M": 10,
                "alpha": 0.1,
                "method": method,
                "status": "available",
                "reason": "available",
            }
            for method in ("B0", "B1", "B2", "B3", "B4", "B5", "B6")
        ]
    )
    context = {
        "split_seed": 2026,
        "model": "LR",
        "M": 10,
        "source_M": 10,
        "alpha": 0.1,
        "scenario": "S0",
        "capacity": 0.6,
    }
    table = make_figures.build_main_table(metrics, status, context)
    b0 = table[table["method"] == "B0"].iloc[0]
    assert b0["accepted"] == 19
    assert pd.isna(b0["target_acceptance"])
    assert table[table["method"] == "B4"].iloc[0]["accepted"] == 11


def test_coverage_table_keeps_median_m1():
    rows = []
    for predictor, m_value in (("MI", 10), ("median", 1)):
        for stratum in make_figures.STRATA_ORDER:
            rows.append(
                {
                    "predictor": predictor,
                    "split_seed": 2026,
                    "model": "LR",
                    "M": m_value,
                    "source_M": 10,
                    "scenario": "S0",
                    "alpha": 0.1,
                    "imputation_batch": 0,
                    "stratum": stratum,
                    "n": 10,
                    "covered": 9,
                    "coverage": 0.9,
                }
            )
    context = {
        "split_seed": 2026,
        "model": "LR",
        "M": 10,
        "source_M": 10,
        "alpha": 0.1,
        "scenario": "S0",
    }
    table = make_figures.build_coverage_table(pd.DataFrame(rows), context)
    assert set(table["predictor"]) == {"MI", "median"}
    assert len(table) == 12


def _clinical_run(tmp_path):
    run = tmp_path / "run-1"
    run.mkdir()
    manifest = {
        "run_id": "run-1",
        "synthetic": False,
        "run_status": "completed",
        "data_version": "data-v1",
    }
    (run / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (run / "config.yaml").write_text("protocol_version: v1\n", encoding="utf-8")
    return run, manifest


def _acceptance_record(run, manifest, **overrides):
    record = {
        "schema_version": 1,
        "run_id": "run-1",
        "manifest_sha256": make_figures.sha256_file(run / "manifest.json"),
        "synthetic": False,
        "protocol_version": "v1",
        "data_version": "data-v1",
        "status": "accepted",
        "scope": "D-002 figures and tables",
        "accepted_at": "2026-11-04T00:00:00Z",
        "signoffs": {
            "C": {
                "name": "C",
                "date": "2026-11-04",
                "decision": "accepted",
                "evidence": "handoffs/C/example.md",
            },
            "E": {
                "name": "E",
                "date": "2026-11-04",
                "decision": "accepted",
                "evidence": "handoffs/E/example.md",
            },
        },
    }
    record.update(overrides)
    path = run.parent / "acceptance.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return path, record


def test_clinical_run_requires_acceptance_record(tmp_path):
    run, manifest = _clinical_run(tmp_path)
    with pytest.raises(make_figures.ProvenanceError, match="require a C/E-signed acceptance record"):
        make_figures.load_acceptance(run, manifest, {"protocol_version": "v1"}, None, tmp_path)


def test_acceptance_record_requires_c_and_e_signoffs(tmp_path):
    run, manifest = _clinical_run(tmp_path)
    path, record = _acceptance_record(run, manifest)
    del record["signoffs"]["E"]
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(make_figures.ProvenanceError, match="missing E signoff"):
        make_figures.load_acceptance(run, manifest, {"protocol_version": "v1"}, path, tmp_path)


def test_acceptance_record_must_match_manifest_hash(tmp_path):
    run, manifest = _clinical_run(tmp_path)
    path, record = _acceptance_record(run, manifest, manifest_sha256="0" * 64)
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(make_figures.ProvenanceError, match="manifest_sha256"):
        make_figures.load_acceptance(run, manifest, {"protocol_version": "v1"}, path, tmp_path)


def test_valid_acceptance_record_is_returned(tmp_path):
    run, manifest = _clinical_run(tmp_path)
    path, record = _acceptance_record(run, manifest)
    result = make_figures.load_acceptance(run, manifest, {"protocol_version": "v1"}, path, tmp_path)
    assert result is not None
    assert result["record"]["run_id"] == "run-1"
    assert result["sha256"] == make_figures.sha256_file(path)


def test_synthetic_run_rejects_acceptance_file(tmp_path):
    run = tmp_path / "run-1"
    run.mkdir()
    manifest = {"run_id": "run-1", "synthetic": True, "run_status": "completed"}
    (run / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(make_figures.ProvenanceError, match="only valid for clinical runs"):
        make_figures.load_acceptance(run, manifest, {"protocol_version": "v1"}, tmp_path / "x.json", tmp_path)


def test_wilson_interval_boundaries():
    low, high = make_figures.wilson_interval(0, 10)
    assert low < 0.01
    assert 0.25 < high < 0.30
    low, high = make_figures.wilson_interval(10, 10)
    assert 0.70 < low < 0.75
    assert high > 0.999
    assert all(pd.isna(value) for value in make_figures.wilson_interval(0, 0))
