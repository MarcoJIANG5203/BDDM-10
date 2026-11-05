"""Read immutable PSV archives and write an A-owned automated receipt for C.

This checker does not import A/B extraction or model code, fit a model, alter an
input, or record human/recipient acceptance. The per-record CSV is private data:
keep it in a versioned data bundle or ignored local directory, not ordinary Git.
Requires numpy and pandas (plus parquet support) from requirements-lock.txt.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone, timedelta
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import time
import zipfile

import numpy as np
import pandas as pd


PHYSIO = "HR O2Sat Temp SBP MAP DBP Resp EtCO2 BaseExcess HCO3 FiO2 pH PaCO2 SaO2 AST BUN Alkalinephos Calcium Chloride Creatinine Bilirubin_direct Glucose Lactate Magnesium Phosphate Potassium Bilirubin_total TroponinI Hct Hgb PTT WBC Fibrinogen Platelets".split()
FEATURES = PHYSIO + ["Age", "Gender"]
HEADER = FEATURES + ["Unit1", "Unit2", "HospAdmTime", "ICULOS", "SepsisLabel"]
REASONS = ["invalid_hourly_records", "missing_initial_hours", "insufficient_followup", "first_observation_positive", "onset_at_or_before_12", "invalid_input_demographics", "included"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def optional_number(value):
    return None if value is None or value == "" else float(value)


def source_hash_manifest(package):
    result = {}
    for line in (package / "PACKAGE_SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        target = (package / relative).resolve()
        require(target.is_relative_to(package), "Package checksum path escapes input")
        require(relative not in result, "Repeated package checksum path")
        require(sha(target) == digest, f"Package checksum mismatch: {relative}")
        result[relative] = digest
    return result


def inspect_hourly(content, patient_id, site, source_filename):
    """Recompute written v1 rules using actual ICULOS, with no guessed onset."""
    result = {"patient_id": patient_id, "site": site, "source_filename": source_filename,
              "source_sha256": hashlib.sha256(content).hexdigest(),
              "source_bytes": len(content), "observed_rows": 0,
              "first_hour": None, "last_hour": None, "first_positive_hour": None,
              "recovered_onset_hour": None, "first_observation_positive": None,
              "censoring_status": "invalid_hourly_records", "onset_after_last_record": None,
              "complete_hours_1_to_24": False, "onset_at_or_before_12_diagnostic": False,
              "observed_onset_in_12_24_diagnostic": False,
              "reason": "invalid_hourly_records", "y_true": None,
              "feature_max_source_hour": None, "feature_columns_checked": 0}
    parsed = list(csv.reader(io.StringIO(content.decode("utf-8-sig")), delimiter="|"))
    if not parsed or parsed[0] != HEADER or not parsed[1:] or any(len(r) != 41 for r in parsed[1:]):
        return result, None
    try:
        values = np.asarray(parsed[1:], dtype=float)
    except ValueError:
        return result, None
    hours, labels = values[:, 39], values[:, 40]
    valid = (not np.isinf(values).any() and np.isfinite(hours).all()
             and (hours >= 1).all() and (hours == np.floor(hours)).all()
             and (np.diff(hours) == 1).all() and np.isin(labels, [0, 1]).all()
             and (np.diff(labels) >= 0).all())
    if not valid:
        return result, None
    first = np.flatnonzero(labels == 1)
    first_index = int(first[0]) if first.size else None
    left_censored = labels[0] == 1
    onset = int(hours[first_index] + 6) if first_index is not None and not left_censored else None
    status = ("left_censored_first_observation_positive" if left_censored else
              "observed_zero_to_one_transition" if first_index is not None else
              "no_positive_label_in_released_record")
    result.update(observed_rows=len(hours), first_hour=int(hours[0]), last_hour=int(hours[-1]),
                  first_positive_hour=int(hours[first_index]) if first_index is not None else None,
                  recovered_onset_hour=onset, first_observation_positive=int(left_censored),
                  censoring_status=status,
                  onset_after_last_record=bool(onset > hours[-1]) if onset is not None else None,
                  complete_hours_1_to_24=bool(hours[0] == 1 and hours[-1] >= 24),
                  onset_at_or_before_12_diagnostic=bool(onset is not None and onset <= 12),
                  observed_onset_in_12_24_diagnostic=bool(onset is not None and 12 < onset <= 24))
    if hours[0] != 1:
        result["reason"] = "missing_initial_hours"
    elif hours[-1] < 24:
        result["reason"] = "insufficient_followup"
    elif left_censored:
        result["reason"] = "first_observation_positive"
    elif onset is not None and onset <= 12:
        result["reason"] = "onset_at_or_before_12"
    else:
        prior = values[hours <= 12, :36]
        observed = [np.flatnonzero(~np.isnan(col)) for col in prior.T]
        feature_values = np.asarray([col[idx[-1]] if len(idx) else np.nan
                                     for col, idx in zip(prior.T, observed)])
        if not np.isnan(feature_values[35]) and feature_values[35] not in (0, 1):
            result["reason"] = "invalid_input_demographics"
        else:
            require(len(prior) == 12, "A v1 included record lacks exactly 12 input hours")
            result.update(reason="included", y_true=int(onset is not None and 12 < onset <= 24),
                          feature_max_source_hour=int(hours[hours <= 12][-1]),
                          feature_columns_checked=36)
            return result, feature_values
    return result, None


def verify(package, output_root):
    started = time.monotonic()
    package, output_root = package.resolve(), output_root.resolve()
    require(package.is_dir(), "Input package not found")
    require(not output_root.is_relative_to(package), "Output must be outside immutable input package")
    input_hashes_before = source_hash_manifest(package)
    manifest_file = package / "PACKAGE_SHA256SUMS.txt"
    package_manifest_before = sha(manifest_file)
    audit_path = package / "data/processed/cohort_audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    require(audit["protocol_version"] == "v1" and audit["feature_window_end"] == 12
            and audit["outcome_window"] == "(12,24]" and audit["label_shift_hours"] == 6,
            "This receipt checker is restricted to unchanged protocol v1")
    require(audit["feature_order"] == FEATURES, "Unexpected feature order")
    for relative, digest in audit["file_sha256"].items():
        require(sha(package / relative) == digest, f"Cohort-audit input hash mismatch: {relative}")
    with (package / "data/processed/record_audit.csv").open(newline="", encoding="utf-8") as stream:
        record_rows = list(csv.DictReader(stream))
    record_index = {r["patient_id"]: r for r in record_rows}
    require(len(record_index) == len(record_rows), "Repeated record-audit IDs")
    with (package / "sources/raw_file_manifest.csv").open(newline="", encoding="utf-8") as stream:
        source_rows = list(csv.DictReader(stream))
    source_index = {(r["site"], r["key"].rsplit("/", 1)[-1]): r for r in source_rows}
    require(len(source_index) == len(source_rows), "Repeated source-manifest keys")
    frame = pd.read_parquet(package / "data/processed/cohort.parquet")
    csv_frame = pd.read_csv(package / "data/processed/cohort.csv", dtype={"patient_id": "string"},
                            float_precision="round_trip")
    require(list(frame.columns) == ["patient_id", "site", "y_true"] + FEATURES, "Cohort columns")
    pd.testing.assert_frame_equal(frame, csv_frame, check_dtype=False, check_exact=True)
    require(frame.patient_id.is_unique, "Repeated cohort ID")
    cohort = frame.set_index("patient_id")
    expected_features = cohort[FEATURES].to_dict("index")
    output_root.mkdir(parents=True, exist_ok=True)
    receipt_path = output_root / "private_receipt/raw_psv_receipt.csv"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    checked = set()
    included = set()
    site_counts, reason_counts, cross_reason_counts = {}, Counter(), Counter()
    diagnostic_counts = Counter()
    raw_zip_hashes = {}
    archive_member_count = 0
    with receipt_path.open("w", newline="", encoding="utf-8") as destination:
        writer = None
        for site, expected_raw in [("A", 20336), ("B", 20000)]:
            raw_path = package / f"raw/training_set{site}.zip"
            raw_zip_hashes[raw_path.name] = sha(raw_path)
            require(raw_zip_hashes[raw_path.name] == audit["raw_archive_sha256"][raw_path.name],
                    f"Source ZIP checksum mismatch: {raw_path.name}")
            site_counter = Counter()
            with zipfile.ZipFile(raw_path) as bundle:
                names = bundle.namelist()
                require(len(names) == len(set(names)) == expected_raw, f"Source ZIP membership {site}")
                for index, name in enumerate(sorted(names)):
                    require(name.endswith(".psv") and Path(name).name == name, "Unexpected raw archive path")
                    patient_id = f"{site}_{Path(name).stem}"
                    require(patient_id not in checked, "Repeated raw patient_id")
                    checked.add(patient_id)
                    content = bundle.read(name)
                    registered = source_index[(site, name)]
                    require(len(content) == int(registered["bytes"]), f"Source length {patient_id}")
                    require(hashlib.sha256(content).hexdigest() == registered["sha256"], f"Source SHA {patient_id}")
                    require(hashlib.md5(content).hexdigest() == registered["md5"] == registered["etag"].strip('"'),
                            f"Source stored MD5/ETag {patient_id}")
                    row, feature_values = inspect_hourly(content, patient_id, site, name)
                    declared = record_index[patient_id]
                    for key in ["site", "source_filename", "reason"]:
                        require(row[key] == declared[key], f"Record audit {key} mismatch {patient_id}")
                    for key in ["observed_rows", "first_hour", "last_hour", "first_positive_hour", "first_observation_positive", "y_true"]:
                        require(row[key] == optional_number(declared[key]), f"Record audit {key} mismatch {patient_id}")
                    require(row["recovered_onset_hour"] == optional_number(declared["onset_proxy"]),
                            f"Recovered onset differs {patient_id}")
                    if feature_values is not None:
                        included.add(patient_id)
                        require(cohort.loc[patient_id, "site"] == site and cohort.loc[patient_id, "y_true"] == row["y_true"],
                                f"Cohort site/label mismatch {patient_id}")
                        saved = np.asarray([expected_features[patient_id][k] for k in FEATURES], dtype=float)
                        require(np.array_equal(saved, feature_values, equal_nan=True), f"Feature mismatch {patient_id}")
                        site_counter["included"] += 1
                        site_counter["positive"] += row["y_true"]
                    site_counter["raw"] += 1
                    reason_counts[row["reason"]] += 1
                    cross_reason_counts[(site, row["reason"])] += 1
                    for field in ["first_observation_positive", "onset_at_or_before_12_diagnostic", "onset_after_last_record", "observed_onset_in_12_24_diagnostic"]:
                        if row[field]:
                            diagnostic_counts[(site, field)] += 1
                    if writer is None:
                        writer = csv.DictWriter(destination, fieldnames=list(row))
                        writer.writeheader()
                    writer.writerow(row)
                    archive_member_count += 1
                    if (index + 1) % 5000 == 0:
                        print(f"Raw receipt site {site}: {index + 1}/{expected_raw} records checked", flush=True)
            site_counts[site] = dict(site_counter)
            print(f"Raw receipt site {site} complete: {dict(site_counter)}", flush=True)
    require(checked == set(record_index), "Raw receipt does not cover record_audit exactly")
    require(checked == {f"{s}_{Path(n).stem}" for s, n in source_index}, "Raw receipt does not cover source manifest")
    require(included == set(cohort.index), "Raw-derived cohort membership differs")
    for reason in REASONS:
        expected = audit["exclusion_counts"].get(reason, len(cohort) if reason == "included" else 0)
        require(reason_counts[reason] == expected, f"Sequential reason count differs: {reason}")
    for site, counts in site_counts.items():
        require(all(audit["site_counts"][site][key] == value for key, value in counts.items()), "Site counts differ")
        for reason in REASONS[:-1]:
            require(cross_reason_counts[(site, reason)] == audit["site_counts"][site]["exclusions"][reason], "Site exclusion count differs")
    # Verify all source and cohort files after the read, rather than rewriting an audit.
    require(source_hash_manifest(package) == input_hashes_before, "Input bytes changed during verification")
    require(sha(manifest_file) == package_manifest_before, "Original package checksum manifest changed")
    summary = {
        "status": "PASS_AUTOMATED_A_RAW_RECEIPT",
        "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "protocol_version": audit["protocol_version"], "data_version": audit["data_version"],
        "source_package": package.name,
        "source_package_manifest_sha256": package_manifest_before,
        "source_archive_sha256": raw_zip_hashes,
        "input_hashes": {relative: sha(package / relative) for relative in [
            "data/processed/cohort.parquet", "data/processed/cohort.csv", "data/processed/cohort_audit.json",
            "data/processed/record_audit.csv", "sources/raw_file_manifest.csv"]},
        "verification_code_sha256": sha(__file__),
        "raw_records_checked": archive_member_count,
        "source_sha256_md5_bytes_matches": archive_member_count,
        "record_audit_metadata_reason_label_matches": len(checked),
        "included_membership_label_and_36_feature_matches": len(included),
        "included_feature_cells_checked": len(included) * 36,
        "parquet_csv_exact_numeric_equivalence": True,
        "feature_cutoff_max_iculos": 12,
        "package_hash_entries_before_and_after": len(input_hashes_before),
        "inputs_unchanged": True,
        "site_counts": site_counts,
        "sequential_reason_counts": {reason: reason_counts[reason] for reason in REASONS},
        "overlapping_diagnostics_by_site": {
            site: {field: diagnostic_counts[(site, field)] for field in [
                "first_observation_positive", "onset_at_or_before_12_diagnostic",
                "onset_after_last_record", "observed_onset_in_12_24_diagnostic"]} for site in ["A", "B"]},
        "private_receipt": {"path": "private_receipt/raw_psv_receipt.csv", "rows": len(checked),
                            "sha256": sha(receipt_path), "ordinary_git": False},
        "human_or_recipient_acceptance": False,
        "C_raw_receipt_review": "PENDING_C_REVIEW_OF_THIS_DELIVERY",
        "clinical_ground_truth_adjudication": False,
        "models_fitted": False, "labels_splits_or_raw_files_changed": False,
        "limits": [
            "Independent implementation of written v1 rules, not independent clinical adjudication.",
            "Recovered onset is label-derived; first-observation-positive has no fabricated exact onset.",
            "Early-onset and left-censored diagnostics overlap earlier sequential exclusions.",
            "No positive label outside an eligible record is not a universal no-sepsis assertion.",
            "Source MD5/ETag and SHA256 match the preserved inventory; this is not a fresh network download.",
            "No patient-level CSV or source PSV is intended for ordinary Git."] ,
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__},
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    report = output_root / "reviews/A_raw_psv_receipt_2026-11-04.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(summary, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")
    print(f"PASS: {len(checked)} raw records; {len(included)} included labels/36 features; source inputs unchanged", flush=True)
    print(f"Private per-record receipt: {receipt_path}", flush=True)
    print(f"Aggregate report: {report}", flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path, help="Immutable A full-r1 package root")
    parser.add_argument("--output-root", required=True, type=Path, help="Separate receipt output directory")
    args = parser.parse_args()
    verify(args.package, args.output_root)


if __name__ == "__main__":
    main()
