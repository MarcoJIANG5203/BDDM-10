"""C independent replay of A's EXP-01 cohort audit (first-principles).

Re-derives every patient-level field straight from the raw .psv bytes in the
registered source ZIP, then compares the result against A's raw replay receipt
(inside the formal ZIP) and against the aggregate counts A published. It imports
nothing from `src` and does not read A's audit script, so the per-record
computation is an independent re-implementation of the written v1 protocol:

  feature landmark hour 12, target window (12,24], label shift +6 h,
  sequential exclusion order:
    invalid_hourly_records -> missing_initial_hours -> insufficient_followup
    -> first_observation_positive -> onset_at_or_before_12 -> included
    (invalid_input_demographics handled inside the included branch)

Usage:
  python reviews/verify_c_exp01.py \
      --source-zip .artifact-cache/exp01/inputs/T1_A_Day1_2026-11-03_v1_Rebuilt_Full.zip \
      --formal-zip .artifact-cache/exp01/inputs/a-data-v1-20261104-r1.zip \
      --output .artifact-cache/exp01/c_exp01_verification.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd


PHYSIO = ("HR O2Sat Temp SBP MAP DBP Resp EtCO2 BaseExcess HCO3 FiO2 pH PaCO2 SaO2 "
          "AST BUN Alkalinephos Calcium Chloride Creatinine Bilirubin_direct Glucose "
          "Lactate Magnesium Phosphate Potassium Bilirubin_total TroponinI Hct Hgb PTT "
          "WBC Fibrinogen Platelets").split()
FEATURES = PHYSIO + ["Age", "Gender"]
HEADER = FEATURES + ["Unit1", "Unit2", "HospAdmTime", "ICULOS", "SepsisLabel"]
REASONS = ["invalid_hourly_records", "missing_initial_hours", "insufficient_followup",
           "first_observation_positive", "onset_at_or_before_12",
           "invalid_input_demographics", "included"]

EXPECTED = {
    "source_zip": "a57d16dc5432b2e2518bc5f754b706c60de7b94d3fb496870687d4a564770cb1",
    "formal_zip": "feb69777e7c03c51d580808182a4702a2b3991a0edd552ec4d0dcbf7b1a7129c",
    "raw_records": 40336,
    "frozen_records": 24095,
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_one(content: bytes, filename: str) -> dict:
    """First-principles re-derivation of the v1 rules from raw .psv bytes."""
    row = {"source_filename": filename, "source_sha256": sha256_bytes(content),
           "source_bytes": len(content)}
    parsed = list(csv.reader(io.StringIO(content.decode("utf-8-sig")), delimiter="|"))
    if not parsed or parsed[0] != HEADER or not parsed[1:] or any(len(r) != 41 for r in parsed[1:]):
        row.update(reason="invalid_hourly_records", y_true=None)
        return row
    try:
        values = np.asarray(parsed[1:], dtype=float)
    except ValueError:
        row.update(reason="invalid_hourly_records", y_true=None)
        return row
    hours, labels = values[:, 39], values[:, 40]
    valid = (not np.isinf(values).any() and np.isfinite(hours).all()
             and (hours >= 1).all() and (hours == np.floor(hours)).all()
             and (np.diff(hours) == 1).all() and np.isin(labels, [0, 1]).all()
             and (np.diff(labels) >= 0).all())
    if not valid:
        row.update(reason="invalid_hourly_records", y_true=None)
        return row

    first = np.flatnonzero(labels == 1)
    first_index = int(first[0]) if first.size else None
    left_censored = labels[0] == 1
    onset = int(hours[first_index] + 6) if first_index is not None and not left_censored else None

    if hours[0] != 1:
        reason = "missing_initial_hours"
    elif hours[-1] < 24:
        reason = "insufficient_followup"
    elif left_censored:
        reason = "first_observation_positive"
    elif onset is not None and onset <= 12:
        reason = "onset_at_or_before_12"
    else:
        reason = "included"
    y_true = int(onset is not None and 12 < onset <= 24) if reason == "included" else None
    row.update(
        observed_rows=len(hours), first_hour=int(hours[0]), last_hour=int(hours[-1]),
        first_positive_hour=int(hours[first_index]) if first_index is not None else None,
        recovered_onset_hour=onset,
        first_observation_positive=int(left_censored),
        onset_after_last_record=bool(onset > hours[-1]) if onset is not None else None,
        complete_hours_1_to_24=bool(hours[0] == 1 and hours[-1] >= 24),
        onset_at_or_before_12_diagnostic=bool(onset is not None and onset <= 12),
        observed_onset_in_12_24_diagnostic=bool(onset is not None and 12 < onset <= 24),
        reason=reason, y_true=y_true,
    )
    return row


def equals_na(left, right):
    """Element-wise equality that treats missing (NaN/None) as equal."""
    l = pd.Series(left).reset_index(drop=True)
    r = pd.Series(right).reset_index(drop=True)
    return (l == r) | (l.isna() & r.isna())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-zip", required=True, type=Path)
    ap.add_argument("--formal-zip", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    checks = []
    def check(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    with open(args.source_zip, "rb") as f:
        src_bytes = f.read()
    with open(args.formal_zip, "rb") as f:
        fm_bytes = f.read()
    check("source_zip_sha256", sha256_bytes(src_bytes) == EXPECTED["source_zip"],
          sha256_bytes(src_bytes))
    check("formal_zip_sha256", sha256_bytes(fm_bytes) == EXPECTED["formal_zip"],
          sha256_bytes(fm_bytes))

    source_root = "T1_A_Day1_2026-11-03_v1_Rebuilt_Full"
    mine = []
    with ZipFile(io.BytesIO(src_bytes)) as src:
        names = [n for n in src.namelist()
                 if n.startswith(source_root + "/raw/") and n.endswith(".psv")]
        for name in names:
            filename = name.rsplit("/", 1)[-1]
            mine.append(parse_one(src.read(name), filename))
    mine = pd.DataFrame(mine)
    check("raw_record_count", len(mine) == EXPECTED["raw_records"], f"{len(mine)}")

    receipt = None
    with ZipFile(io.BytesIO(fm_bytes)) as fm:
        if "private_receipt/raw_psv_receipt.csv" in fm.namelist():
            receipt = pd.read_csv(fm.open("private_receipt/raw_psv_receipt.csv"))
    check("receipt_present", receipt is not None)

    result = {"checks": checks}

    if receipt is not None and len(mine) == EXPECTED["raw_records"]:
        # Derive site independently from the PhysioNet filename namespace:
        # setA (site A) files are p0xxxxx, setB (site B) files are p1xxxxx.
        stem = mine.source_filename.str[:-4]
        mine["site"] = np.where(stem.str[1] == "1", "B", "A")
        mine["patient_id"] = mine.site + "_" + stem

        check("source_filename_set_matches",
              set(mine.source_filename) == set(receipt.source_filename))
        joined = receipt.set_index("source_filename")
        # cross-check site: every filename's site in the receipt equals our derived site
        site_mismatch = int((joined.loc[mine.source_filename, "site"].to_numpy()
                             != mine.site.to_numpy()).sum())
        check("site_assignment_matches", site_mismatch == 0, f"{site_mismatch} mismatches")

        cols = ["patient_id", "site", "reason", "first_hour", "last_hour",
                "first_positive_hour", "recovered_onset_hour", "first_observation_positive",
                "onset_after_last_record", "complete_hours_1_to_24", "y_true",
                "observed_onset_in_12_24_diagnostic"]
        bad_cols = {}
        for c in cols:
            ref = joined.loc[mine.source_filename, c].reset_index(drop=True)
            n = int((~equals_na(ref, mine[c])).sum())
            if n:
                bad_cols[c] = n
        check("per_record_field_agreement", not bad_cols,
              f"{len(bad_cols)} columns disagree; "
              f"detail={bad_cols if bad_cols else 'all match'} over {len(mine)} records")

        # Independent per-site, per-rule flow recomputation.
        tgt = (mine.recovered_onset_hour > 12) & (mine.recovered_onset_hour <= 24)
        flow = []
        for site in ("A", "B"):
            g = mine[mine.site == site]
            survivors = g
            flow.append({"site": site, "stage": "raw", "n": len(g),
                         "target_transition_proxy": int(tgt.loc[g.index].sum())})
            for reason in REASONS[:-1]:
                survivors = survivors[survivors.reason != reason]
                flow.append({"site": site, "stage": "after_" + reason, "n": len(survivors),
                             "target_transition_proxy": int(tgt.loc[survivors.index].sum())})
        result["c_flow"] = flow

        lost = tgt & (mine.reason != "included")
        result["lost_target_transitions"] = int(lost.sum())
        check("lost_target_transitions_391", int(lost.sum()) == 391, int(lost.sum()))
        check("late_start_102",
              int((tgt & (mine.reason == "missing_initial_hours")).sum()) == 102,
              int((tgt & (mine.reason == "missing_initial_hours")).sum()))
        check("short_followup_289",
              int((tgt & (mine.reason == "insufficient_followup")).sum()) == 289,
              int((tgt & (mine.reason == "insufficient_followup")).sum()))
        result["lost_onset_after_last_record"] = int((lost & mine.onset_after_last_record).sum())
        result["frozen_positives"] = int((mine.y_true == 1).sum())
        result["frozen_negatives"] = int((mine.y_true == 0).sum())
        check("frozen_records_24095", int(mine.y_true.notna().sum()) == EXPECTED["frozen_records"],
              int(mine.y_true.notna().sum()))

        neg = mine[mine.y_true == 0]
        check("window_negative_support",
              bool(neg.complete_hours_1_to_24.all()
                   and (neg.first_positive_hour.isna() | (neg.recovered_onset_hour > 24)).all()),
              f"n_neg={len(neg)}, complete_1_to_24={bool(neg.complete_hours_1_to_24.all())}, "
              f"onset_after_24_or_none={bool((neg.first_positive_hour.isna() | (neg.recovered_onset_hour > 24)).all())}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8", newline="\n")
    passed = sum(1 for c in checks if c["pass"])
    print(f"C EXP-01 independent replay: {passed}/{len(checks)} checks passed.")
    for c in checks:
        print(f"  [{'PASS' if c['pass'] else 'FAIL'}] {c['check']} {c['detail']}")


if __name__ == "__main__":
    main()
