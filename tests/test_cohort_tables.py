"""Checks for the D-002 cohort table / Figure 1 pipeline."""
import importlib.util
import zipfile
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("make_cohort_tables", ROOT / "scripts" / "make_cohort_tables.py")
make_cohort_tables = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(make_cohort_tables)


def test_safe_extract_rejects_parent_traversal(tmp_path):
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("../evil.txt", "x")
    with pytest.raises(make_cohort_tables.DataError, match="unsafe path"):
        make_cohort_tables.safe_extract(archive, tmp_path / "out")


def test_validate_splits_disjoint_exhaustive_and_counts():
    cohort = pd.DataFrame(
        {
            "patient_id": [f"P{i}" for i in range(1, 11)],
            "site": ["A"] * 8 + ["B"] * 2,
            "y_true": [1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        }
    )
    roles = {
        "train": ["P1", "P2", "P3", "P4"],
        "selection": ["P5"],
        "calibration": ["P6"],
        "test": ["P7", "P8"],
        "external": ["P9", "P10"],
    }
    split_counts = {
        role: {
            "n": len(ids),
            "positive": int(cohort[cohort["patient_id"].isin(ids)]["y_true"].sum()),
        }
        for role, ids in roles.items()
    }
    audit = {"split_counts": {"2026": split_counts}}
    table = make_cohort_tables.validate_splits(cohort, {2026: roles}, audit)
    assert len(table) == 5
    assert set(table["role"]) == set(make_cohort_tables.ROLES)

    overlapping = {key: list(value) for key, value in roles.items()}
    overlapping["selection"] = ["P1"]
    with pytest.raises(make_cohort_tables.DataError, match="overlap"):
        make_cohort_tables.validate_splits(cohort, {2026: overlapping}, audit)
