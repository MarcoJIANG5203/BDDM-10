#!/usr/bin/env python3
"""D-002 Table 1 / Figure 1 from the formal A data Release.

This script describes the delivered cohort; it does not read model results and
does not produce a clinical-effect figure. Outputs are explicitly stamped
``DRAFT_PENDING_ACCEPTANCE`` because the A PR may not be merged and C/E may not
have signed an acceptance record yet.

Typical use::

    python scripts/make_cohort_tables.py \
        --release-zip dist/artifacts/a-data-v1-20261104-r1.zip \
        --expected-sha256 feb69777e7c03c51d580808182a4702a2b3991a0edd552ec4d0dcbf7b1a7129c

The release ZIP must contain:
  data/processed/cohort.parquet (or cohort.csv)
  data/processed/cohort_audit.json
  splits/seed_2026.json ... seed_2030.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DRAFT_BANNER = (
    "DRAFT — formal A data release; pending PR merge and C/E acceptance; not for submission"
)
ROLES = ("train", "selection", "calibration", "test", "external")


class DataError(RuntimeError):
    """Raised when the A release cannot be used as a data-description source."""


def sha256_file(path: Path, block: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(block), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def safe_extract(zip_path: Path, dest: Path) -> None:
    dest = dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            target = (dest / info.filename).resolve()
            if target != dest and not str(target).startswith(str(dest) + os.sep):
                raise DataError(f"unsafe path in release ZIP: {info.filename}")
        archive.extractall(dest)


def find_one(root: Path, name: str, required: bool = True) -> Path | None:
    direct = root / name
    if direct.is_file():
        return direct
    matches = sorted(root.rglob(name))
    if matches:
        return matches[0]
    if required:
        raise DataError(f"cannot find {name} in {root}")
    return None


def find_cohort(root: Path) -> Path:
    parquet = find_one(root, "cohort.parquet", required=False)
    if parquet is not None:
        return parquet
    csv = find_one(root, "cohort.csv", required=False)
    if csv is not None:
        return csv
    raise DataError("cannot find cohort.parquet or cohort.csv in the release")


def load_cohort(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    return pd.read_csv(path, dtype={"patient_id": str})


def find_splits(root: Path) -> dict[int, dict]:
    files = sorted(root.rglob("seed_*.json"))
    files = [p for p in files if p.parent.name == "splits" or "split" in str(p).lower()]
    if len(files) < 5:
        files = sorted(root.rglob("seed_*.json"))
    if len(files) < 5:
        raise DataError("expected five splits/seed_*.json files")
    splits = {}
    for path in files:
        try:
            seed = int(path.stem.split("_")[-1])
        except ValueError:
            continue
        splits[seed] = read_json(path)
    if len(splits) < 5:
        raise DataError("could not parse five split seeds")
    return dict(sorted(splits.items()))


def verify_file_hashes(root: Path, audit: dict) -> dict[str, str]:
    recorded = audit.get("file_sha256") or {}
    verified = {}
    problems = []
    for relative, expected in recorded.items():
        path = root / relative.replace("\\", "/")
        if not path.is_file():
            continue
        actual = sha256_file(path)
        if actual != expected:
            problems.append(f"{relative}: expected {expected}, got {actual}")
        verified[relative] = actual
    if problems:
        raise DataError("release file hash mismatch:\n  " + "\n  ".join(problems))
    if not verified:
        raise DataError("audit.json has no matching file_sha256 entries")
    return verified


def validate_cohort(cohort: pd.DataFrame, audit: dict) -> None:
    if audit.get("synthetic") is not False:
        raise DataError("audit synthetic flag is not false")
    features = list(audit.get("feature_order") or [])
    if len(features) != 36:
        raise DataError(f"expected 36 features, found {len(features)}")
    missing = [f for f in features if f not in cohort.columns]
    if missing:
        raise DataError(f"cohort is missing features: {missing}")
    for column in ("patient_id", "site", "y_true"):
        if column not in cohort.columns:
            raise DataError(f"cohort is missing {column}")
    if cohort["patient_id"].astype(str).duplicated().any():
        raise DataError("duplicate patient_id in cohort")
    if not set(cohort["y_true"].dropna().astype(int).unique()) <= {0, 1}:
        raise DataError("y_true must be binary")
    if cohort["y_true"].isna().any():
        raise DataError("y_true contains NaN")
    for site, expected in (audit.get("site_counts") or {}).items():
        part = cohort[cohort["site"].astype(str) == site]
        if len(part) != expected.get("included"):
            raise DataError(f"site {site}: cohort n does not match audit included count")
        if int(part["y_true"].sum()) != expected.get("positive"):
            raise DataError(f"site {site}: positive count does not match audit")


def validate_splits(cohort: pd.DataFrame, splits: dict[int, dict], audit: dict) -> pd.DataFrame:
    ids = set(cohort["patient_id"].astype(str))
    site = cohort.assign(_pid=cohort["patient_id"].astype(str)).set_index("_pid")["site"].astype(str)
    external_ids = set(site[site == "B"].index)
    rows = []
    for seed, roles in splits.items():
        seen = set()
        for role in ROLES:
            if role not in roles:
                raise DataError(f"seed {seed} is missing role {role}")
            role_ids = set(map(str, roles[role]))
            if not role_ids:
                raise DataError(f"seed {seed}/{role} is empty")
            if seen & role_ids:
                raise DataError(f"seed {seed}: roles overlap")
            seen |= role_ids
        if seen != ids:
            raise DataError(f"seed {seed}: splits are not exhaustive")
        if set(map(str, roles["external"])) != external_ids:
            raise DataError(f"seed {seed}: external role is not exactly hospital B")
        for role in ROLES:
            role_ids = set(map(str, roles[role]))
            part = cohort[cohort["patient_id"].astype(str).isin(role_ids)]
            expected = audit["split_counts"][str(seed)][role]
            positives = int(part["y_true"].sum())
            if len(part) != expected["n"] or positives != expected["positive"]:
                raise DataError(f"seed {seed}/{role}: counts do not match audit")
            rows.append(
                dict(
                    split_seed=seed,
                    role=role,
                    n=len(part),
                    positive=positives,
                    negative=len(part) - positives,
                    sites=",".join(sorted(part["site"].astype(str).unique())),
                )
            )
    return pd.DataFrame(rows)


def cohort_summary(cohort: pd.DataFrame, audit: dict) -> pd.DataFrame:
    rows = []
    for site in ["all"] + sorted(cohort["site"].astype(str).unique()):
        part = cohort if site == "all" else cohort[cohort["site"].astype(str) == site]
        positives = int(part["y_true"].sum())
        if site == "all":
            raw = sum(v.get("raw", 0) for v in audit["site_counts"].values())
            included = sum(v.get("included", 0) for v in audit["site_counts"].values())
            exclusions = {
                key: sum(v.get("exclusions", {}).get(key, 0) for v in audit["site_counts"].values())
                for key in ("missing_initial_hours", "insufficient_followup")
            }
        else:
            entry = audit["site_counts"][site]
            raw = entry.get("raw")
            included = entry.get("included")
            exclusions = entry.get("exclusions", {})
        rows.append(
            dict(
                site=site,
                n=int(len(part)),
                positives=positives,
                base_rate=float(part["y_true"].mean()) if len(part) else None,
                raw=raw,
                included=included,
                excluded=(raw - included) if raw is not None and included is not None else None,
                missing_initial_hours=exclusions.get("missing_initial_hours"),
                insufficient_followup=exclusions.get("insufficient_followup"),
                data_version=audit.get("data_version"),
                protocol_version=audit.get("protocol_version"),
                release_status=audit.get("release_status"),
                license_status=(audit.get("license_provenance") or {}).get("status"),
                synthetic=False,
            )
        )
    return pd.DataFrame(rows)


def feature_missingness(cohort: pd.DataFrame, audit: dict) -> pd.DataFrame:
    features = list(audit["feature_order"])
    sites = sorted(cohort["site"].astype(str).unique())
    rows = []
    for feature in features:
        row = dict(
            feature=feature,
            n=int(len(cohort)),
            overall_missing=float(cohort[feature].isna().mean()),
            data_version=audit.get("data_version"),
            synthetic=False,
        )
        for site in sites:
            part = cohort[cohort["site"].astype(str) == site]
            row[f"missing_site_{site}"] = float(part[feature].isna().mean()) if len(part) else None
        rows.append(row)
    return pd.DataFrame(rows).sort_values("overall_missing", ascending=False).reset_index(drop=True)


def style() -> None:
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


def figure_missingness(missingness: pd.DataFrame, out_dir: Path, formats: list[str], data_version: str) -> list[Path]:
    data = missingness.sort_values("overall_missing", ascending=True)
    fig, ax = plt.subplots(figsize=(4.6, max(3.0, 0.13 * len(data) + 1.2)), layout="constrained")
    y = np.arange(len(data))
    ax.barh(y, data["overall_missing"], color="#0072B2", height=0.7, label="overall")
    site_columns = [c for c in data.columns if c.startswith("missing_site_")]
    markers = ("o", "s", "^", "D")
    for index, column in enumerate(site_columns):
        ax.scatter(
            data[column],
            y,
            marker=markers[index % len(markers)],
            s=12,
            color="#D55E00" if index == 0 else "#009E73",
            label=column.replace("missing_site_", "site "),
            zorder=4,
        )
    ax.set_yticks(y, data["feature"], fontsize=6.5)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Missing fraction")
    ax.set_title("Feature missingness (formal A data release)")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", color="#DDDDDD", linewidth=0.5)
    fig.supxlabel(
        f"{DRAFT_BANNER} | {data_version}",
        color="#B00020",
        fontsize=6.8,
        fontweight="bold",
    )
    fig.text(0.5, 0.5, "DRAFT", ha="center", va="center", fontsize=36, color="#B00020", alpha=0.05, rotation=24, zorder=1000)
    paths = []
    for extension in formats:
        path = out_dir / f"fig1_missingness.{extension}"
        fig.savefig(path, bbox_inches="tight")
        paths.append(path)
    plt.close(fig)
    return paths


def prepare_out_dir(out_dir: Path, overwrite: bool) -> None:
    if out_dir.exists() and any(out_dir.iterdir()) and not overwrite:
        raise DataError(f"output directory is not empty: {out_dir}; use --overwrite")
    out_dir.mkdir(parents=True, exist_ok=True)


def build(release_zip: Path | None, data_dir: Path | None, expected_sha256: str | None, out_dir: Path | None, formats: list[str], overwrite: bool, repo_root: Path) -> dict:
    temp_dir = None
    if data_dir is not None:
        root = data_dir.resolve()
    else:
        if release_zip is None:
            raise DataError("provide --release-zip or --data-dir")
        release_zip = release_zip.resolve()
        if expected_sha256 is not None:
            actual = sha256_file(release_zip)
            if actual != expected_sha256:
                raise DataError(f"release ZIP SHA256 mismatch: expected {expected_sha256}, got {actual}")
        temp_dir = Path(tempfile.mkdtemp(prefix="a-data-release-"))
        safe_extract(release_zip, temp_dir)
        root = temp_dir

    audit_path = find_one(root, "cohort_audit.json")
    cohort_path = find_cohort(root)
    cohorts = load_cohort(cohort_path)
    audit = read_json(audit_path)
    validate_cohort(cohorts, audit)
    splits = find_splits(root)
    split_counts = validate_splits(cohorts, splits, audit)
    hashes = verify_file_hashes(root, audit)

    summary = cohort_summary(cohorts, audit)
    missingness = feature_missingness(cohorts, audit)

    if out_dir is None:
        out_dir = repo_root / "paper" / "inputs" / str(audit.get("data_version"))
    out_dir = out_dir.resolve()
    prepare_out_dir(out_dir, overwrite)
    tables_dir = out_dir / "tables"
    figures_dir = out_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    tables = {
        "table1_cohort_summary.csv": summary,
        "table1_feature_missingness.csv": missingness,
        "split_counts.csv": split_counts,
        "fig1_missingness_data.csv": missingness,
    }
    outputs = []
    for name, frame in tables.items():
        path = tables_dir / name
        frame.to_csv(path, index=False, encoding="utf-8")
        outputs.append(path)
    style()
    outputs.extend(figure_missingness(missingness, figures_dir, formats, str(audit.get("data_version"))))

    provenance = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "DRAFT_PENDING_ACCEPTANCE",
        "draft_reason": "A PR may not be merged; C/E acceptance record is not present; not for submission.",
        "release": {
            "data_version": audit.get("data_version"),
            "release_status": audit.get("release_status"),
            "source_data_version": audit.get("source_data_version"),
            "license_status": (audit.get("license_provenance") or {}).get("status"),
            "review_status": {
                key: (audit.get("human_review", {}).get(key) or {}).get("status")
                for key in (
                    "A_owner_review",
                    "C_independent_10_positive_10_negative",
                    "E_precision_decision",
                )
            },
            "zip": display_path(release_zip, repo_root) if release_zip else None,
            "zip_sha256": sha256_file(release_zip) if release_zip else None,
            "audit_sha256": sha256_file(audit_path),
            "cohort_sha256": sha256_file(cohort_path),
        },
        "script": {
            "path": display_path(Path(__file__).resolve(), repo_root),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "inputs": hashes,
        "validation": {
            "cohort_rows": int(len(cohorts)),
            "patient_id_unique": int(cohorts["patient_id"].nunique()),
            "positives": int(cohorts["y_true"].sum()),
            "features": len(audit.get("feature_order") or []),
            "split_seeds": sorted(splits),
            "roles_disjoint_exhaustive": True,
            "external_is_hospital_b": True,
        },
        "outputs": {
            str(path.relative_to(out_dir)).replace("\\", "/"): sha256_file(path)
            for path in outputs
        },
        "warning": DRAFT_BANNER,
    }
    (out_dir / "provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "README.txt").write_text(
        (
            f"Draft D-002 Table 1 / Figure 1 from {audit.get('data_version')}\n"
            f"Release status: {audit.get('release_status')}\n"
            f"License status: {(audit.get('license_provenance') or {}).get('status')}\n"
            f"Generated: {provenance['generated_at_utc']}\n"
            "This is a cohort-description draft, not a model-result figure.\n"
            "It is not final until the A PR is merged and C/E acceptance is recorded.\n"
            "Do not hand-edit numbers; regenerate from the release ZIP.\n"
        ),
        encoding="utf-8",
    )
    if temp_dir is not None:
        shutil.rmtree(temp_dir, ignore_errors=True)
    return {
        "out_dir": str(out_dir),
        "tables": len(tables),
        "figures": len([p for p in outputs if p.parent == figures_dir]),
        "status": "DRAFT_PENDING_ACCEPTANCE",
        "data_version": audit.get("data_version"),
    }


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return path.name


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-zip", default=None, help="A data Release ZIP")
    parser.add_argument("--data-dir", default=None, help="already extracted A release directory")
    parser.add_argument("--expected-sha256", default=None, help="expected SHA256 of the release ZIP")
    parser.add_argument("--out-dir", default=None, help="defaults to paper/inputs/<data_version>")
    parser.add_argument("--formats", default="pdf,png")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    formats = [item.strip().lower() for item in args.formats.split(",") if item.strip()]
    if not formats or any(item not in {"pdf", "png", "svg"} for item in formats):
        raise SystemExit("--formats must be a subset of pdf,png,svg")
    try:
        result = build(
            release_zip=Path(args.release_zip) if args.release_zip else None,
            data_dir=Path(args.data_dir) if args.data_dir else None,
            expected_sha256=args.expected_sha256,
            out_dir=Path(args.out_dir) if args.out_dir else None,
            formats=formats,
            overwrite=args.overwrite,
            repo_root=repo_root,
        )
    except DataError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
