"""Summarize EXP-01 from the two registered A archives and the raw replay receipt."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
from statistics import NormalDist
from zipfile import ZipFile

import pandas as pd
from scipy.stats import beta

from verify_a_raw_psv_receipt import FEATURES, REASONS, require, sha


ROOT = Path(__file__).resolve().parents[1]
FORMAL = "a-data-v1-20261104-r1"
SOURCE = "a-v1-full-source-20261104-r1"
ROLES = ("train", "selection", "calibration", "test", "external")
MAIN_RUN = ROOT / "reports/clinical-v1/20261105T055420_02d05b15"
Z = NormalDist().inv_cdf(0.975)


def digest(value):
    return hashlib.sha256(value).hexdigest()


def write_csv(rows, destination):
    pd.DataFrame(rows).to_csv(destination, index=False, lineterminator="\n")


def describe(frame, prefix=""):
    result = {
        "n": len(frame),
        "any_observed_positive_label": int(frame.first_positive_hour.notna().sum()),
        "target_transition_proxy": int(frame.target_transition.sum()),
        "target_onset_within_released_hours": int(frame.target_observed.sum()),
        "target_onset_beyond_released_hours": int(
            (frame.target_transition & ~frame.target_observed).sum()
        ),
    }
    for field in ("observed_rows", "first_hour", "last_hour"):
        values = frame[field].dropna()
        for label, fraction in (("min", 0), ("q25", .25), ("median", .5),
                                ("q75", .75), ("max", 1)):
            result[f"{field}_{label}"] = float(values.quantile(fraction)) if len(values) else None
    return {prefix + key: value for key, value in result.items()}


def wilson_width(n, p):
    return 2 * Z * (p * (1 - p) / n + Z**2 / (4 * n**2))**.5 / (1 + Z**2 / n)


def minimum_events(p, width):
    n = 1
    while wilson_width(n, p) > width:
        n += 1
    return n


def exact_interval(k, n):
    return (
        float(beta.ppf(.025, k, n - k + 1)) if k else 0.0,
        float(beta.ppf(.975, k + 1, n - k)) if k < n else 1.0,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", required=True, type=Path)
    parser.add_argument("--formal-zip", required=True, type=Path)
    parser.add_argument("--replay-root", required=True, type=Path)
    parser.add_argument("--aggregate-dir", required=True, type=Path)
    parser.add_argument("--review-dir", required=True, type=Path)
    args = parser.parse_args()
    registry = json.loads((ROOT / "artifacts/registry.json").read_text(encoding="utf-8"))["bundles"]
    archives = {SOURCE: args.source_zip, FORMAL: args.formal_zip}
    for key, path in archives.items():
        require(sha(path) == registry[key]["sha256"], f"Registry archive hash mismatch: {key}")
    review_dir = args.review_dir.resolve()
    require(not review_dir.is_relative_to(ROOT) or review_dir.is_relative_to(ROOT / ".artifact-cache"),
            "Store patient-level review files outside Git or under .artifact-cache")
    require(review_dir != args.aggregate_dir.resolve(), "Use separate aggregate and private directories")
    args.aggregate_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)
    replay_path = args.replay_root / "private_receipt/raw_psv_receipt.csv"
    replay_summary = json.loads((args.replay_root / "reviews/A_raw_psv_receipt_2026-11-04.json")
                                .read_text(encoding="utf-8"))
    freeze_path = ROOT / registry[FORMAL]["freeze_record"]
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    frozen = {
        "data/processed/cohort.parquet": freeze["cohort_sha256"],
        "data/processed/cohort.csv": freeze["cohort_csv_sha256"],
        "data/processed/cohort_audit.json": freeze["delivery_audit_sha256"],
        **freeze["split_sha256"],
    }
    source_root = registry[SOURCE]["roots"][0]
    with ZipFile(args.formal_zip) as formal, ZipFile(args.source_zip) as source:
        for name, expected in frozen.items():
            require(digest(formal.read(name)) == expected, f"Freeze hash mismatch: {name}")
            if name != "data/processed/cohort_audit.json":
                require(digest(source.read(f"{source_root}/{name}")) == expected,
                        f"Source/frozen byte mismatch: {name}")
        source_manifest = source.read(f"{source_root}/PACKAGE_SHA256SUMS.txt")
        require(digest(source_manifest) == replay_summary["source_package_manifest_sha256"],
                "Replay package manifest differs from registered source")
        for filename, expected in replay_summary["source_archive_sha256"].items():
            require(digest(source.read(f"{source_root}/raw/{filename}")) == expected,
                    f"Replay raw archive differs: {filename}")
        require(sha(replay_path) == replay_summary["private_receipt"]["sha256"]
                == digest(formal.read("private_receipt/raw_psv_receipt.csv")),
                "Replay rows differ from the immutable formal receipt")
        cohort = pd.read_parquet(io.BytesIO(formal.read("data/processed/cohort.parquet")))
        split_by_seed = {
            seed: json.loads(formal.read(f"splits/seed_{seed}.json")) for seed in range(2026, 2031)
        }

    audit = pd.read_csv(replay_path)
    require(len(audit) == replay_summary["raw_records_checked"] == 40336
            and audit.patient_id.is_unique, "Unexpected raw patient population")
    require(audit.reason.isin(REASONS).all(), "Unknown exclusion reason")
    onset = audit.recovered_onset_hour
    audit["target_transition"] = onset.gt(12) & onset.le(24)
    require(audit.target_transition.equals(audit.observed_onset_in_12_24_diagnostic),
            "Target window count disagrees with the raw replay")
    audit["target_observed"] = audit.target_transition & onset.le(audit.last_hour)
    audit["hour12_present"] = audit.first_hour.le(12) & audit.last_hour.ge(12)
    audit["first_observed_label_positive"] = audit.first_observation_positive.eq(1)
    included = audit[audit.reason.eq("included")].set_index("patient_id")
    cohort = cohort.set_index("patient_id")
    require(cohort.index.is_unique and set(included.index) == set(cohort.index),
            "Frozen cohort membership differs")
    require(included.loc[cohort.index, "y_true"].eq(cohort.y_true).all()
            and included.loc[cohort.index, "site"].eq(cohort.site).all(),
            "Frozen labels or sites differ")
    negative = included[included.y_true.eq(0)]
    require(negative.complete_hours_1_to_24.all()
            and (negative.first_positive_hour.isna() | negative.recovered_onset_hour.gt(24)).all(),
            "A frozen negative lacks the declared v1 observation support")

    flow, reasons, followup, boundaries, missing, label_support = [], [], [], [], [], []
    for site in ("A", "B"):
        group = audit[audit.site.eq(site)]
        survivors = group
        flow.append({"site": site, "stage": "raw", **describe(group)})
        for reason in REASONS[:-1]:
            dropped = survivors[survivors.reason.eq(reason)]
            survivors = survivors[~survivors.reason.eq(reason)]
            flow.append({"site": site, "stage": "after_" + reason, **describe(survivors)})
            reasons.append({"site": site, "first_exclusion_reason": reason, **describe(dropped)})
        require(survivors.reason.eq("included").all(), "Stage flow did not resolve")
        reasons.append({"site": site, "first_exclusion_reason": "included", **describe(survivors)})
        for reason, part in group.groupby("reason"):
            pos = part[part.target_transition]
            followup.append({
                "site": site, "reason": reason,
                "target_transition_proxy": len(pos),
                "hour12_present": int(pos.hour12_present.sum()),
                "observed_through_hour18": int(pos.last_hour.ge(18).sum()),
                "observed_through_hour24": int(pos.last_hour.ge(24).sum()),
                "onset_within_released_hours": int(pos.target_observed.sum()),
                "onset_beyond_released_hours": int((~pos.target_observed).sum()),
                "first_observation_positive_all_labels": int(part.first_observed_label_positive.sum()),
            })
        for hour in (12, 13, 24, 25):
            boundary = group[group.recovered_onset_hour.eq(hour)]
            for reason in REASONS:
                part = boundary[boundary.reason.eq(reason)]
                boundaries.append({
                    "site": site, "recovered_onset_hour": hour, "first_exclusion_reason": reason,
                    "n": len(part), "recovered_hour_within_record": int(part.last_hour.ge(hour).sum()),
                    "included_target_positives": int(part.y_true.eq(1).sum()),
                    "included_target_negatives": int(part.y_true.eq(0).sum()),
                })
        for name, mask in (
            ("first_observation_positive", group.first_observed_label_positive),
            ("recovered_onset_at_or_before_12", onset.le(12).loc[group.index]),
            ("v1_negative_no_released_positive_label", group.y_true.eq(0) & group.first_positive_hour.isna()),
            ("v1_negative_recovered_onset_after_24", group.y_true.eq(0) & group.recovered_onset_hour.gt(24)),
        ):
            label_support.append({"site": site, "category": name, **describe(group[mask])})
        for feature in FEATURES:
            values = cohort.loc[cohort.site.eq(site), feature]
            missing.append({"site": site, "feature": feature, "n": len(values),
                            "n_missing": int(values.isna().sum()), "missing_fraction": float(values.isna().mean())})

    roles = []
    role_union = {role: set() for role in ROLES}
    for seed, split in split_by_seed.items():
        require(set(split) == set(ROLES), "Unexpected split roles")
        ids = [pid for values in split.values() for pid in values]
        require(len(ids) == len(set(ids)) and set(ids) == set(cohort.index),
                f"Split overlap or missing IDs for seed {seed}")
        for role in ROLES:
            part = cohort.loc[split[role]]
            require(set(part.site) == {"B" if role == "external" else "A"}, "Site/role mismatch")
            role_union[role].update(part.index)
            positives = int(part.y_true.sum())
            roles.append({"seed": seed, "role": role, "n_unique": len(part),
                          "positive": positives, "negative": len(part) - positives,
                          "prevalence": positives / len(part)})
    unions = [{"role": role, "n_unique_across_seeds": len(ids),
               "positive_unique_across_seeds": int(cohort.loc[sorted(ids), "y_true"].sum())}
              for role, ids in role_union.items()]

    budget = []
    for row in roles:
        if row["seed"] != 2026:
            continue
        for p in (.5, .9):
            budget.append({"role": row["role"], "n_positive": row["positive"],
                           "assumed_proportion": p,
                           "wilson95_full_width": wilson_width(row["positive"], p),
                           "fraction_per_positive_case": 1 / row["positive"],
                           "n_for_width_le_0_20": minimum_events(p, .20),
                           "n_for_width_le_0_10": minimum_events(p, .10)})
    coverage = pd.read_csv(MAIN_RUN / "positive_coverage.csv")
    coverage = coverage[(coverage.split_seed == 2026) & coverage.scenario.isin(["S0", "S4"])
                        & coverage.predictor.eq("MI") & coverage.stratum.eq("y=1")
                        & coverage.imputation_batch.eq(0) & coverage.alpha.eq(.1)]
    intervals = []
    for scene, role in (("S0", "test"), ("S4", "external")):
        records = coverage[coverage.scenario.eq(scene)]
        require(len(records) == 1, f"Ambiguous prior coverage row: {scene}")
        entry = records.iloc[0]
        n, k = int(entry.n), int(entry.covered)
        require(n == next(r["positive"] for r in roles if r["seed"] == 2026 and r["role"] == role),
                "Historical coverage denominator differs")
        lo, hi = exact_interval(k, n)
        intervals.append({"scene": scene, "role": role, "covered": k, "n_positive": n,
                          "clopper_pearson_lower": lo, "clopper_pearson_upper": hi})

    bootstrap_path = MAIN_RUN / "bootstrap_differences.csv"
    prior = pd.read_csv(bootstrap_path)
    prior = prior[(prior.split_seed == 2026) & prior.scenario.isin(["S0", "S4"])
                  & prior.model.eq("LR") & prior.source_M.eq(10) & prior.alpha.eq(.1)
                  & prior.imputation_batch.eq(0) & prior.comparison.eq("B4-B2")
                  & prior.target_acceptance.eq(.6) & prior.selection_mode.eq("batch")].copy()
    require(len(prior) == 2 and set(prior.scenario) == {"S0", "S4"},
            "Expected one historical comparison per scene")
    prior["historical_ci95_full_width"] = prior.ci_high - prior.ci_low
    prior["candidate_practical_difference_fraction"] = .01
    prior = prior[["scenario", "resample_size", "risk_difference", "ci_low", "ci_high",
                   "historical_ci95_full_width", "valid", "invalid",
                   "candidate_practical_difference_fraction"]]

    outputs = {
        "cohort_flow.csv": flow, "first_exclusion_reasons.csv": reasons,
        "target_event_observability.csv": followup, "boundary_hours.csv": boundaries,
        "label_observation_support.csv": label_support, "feature_missingness.csv": missing,
        "split_events.csv": roles, "unique_ids_across_seeds.csv": unions,
        "event_precision_budget.csv": budget, "historical_positive_coverage_intervals.csv": intervals,
        "historical_selective_risk_precision.csv": prior.to_dict("records"),
    }
    for name, rows in outputs.items():
        write_csv(rows, args.aggregate_dir / name)

    audit["review_all_lost_target_events"] = audit.target_transition & ~audit.reason.eq("included")
    audit["review_onset_boundary"] = onset.isin([12, 13, 24, 25])
    audit["review_sampled_included"] = False
    sample = audit[audit.reason.eq("included")].copy()
    sample["review_key"] = sample.patient_id.map(lambda pid: digest(("EXP01-r1|" + pid).encode()))
    sample = sample.sort_values("review_key")
    for mask, n in (
        (sample.y_true.eq(1), 5),
        (sample.y_true.eq(0) & sample.first_positive_hour.isna(), 3),
        (sample.y_true.eq(0) & sample.recovered_onset_hour.gt(24), 2),
    ):
        picked = sample[mask].groupby("site").head(n)
        require(len(picked) == 2 * n, "Insufficient representative review cases")
        audit.loc[picked.index, "review_sampled_included"] = True
    audit["review_left_censored"] = audit.first_observed_label_positive
    for role in ROLES:
        audit.loc[audit.patient_id.isin(split_by_seed[2026][role]), "seed_2026_role"] = role
    cases = review_dir / "case_review.csv"
    audit.sort_values(["site", "patient_id"]).to_csv(cases, index=False, lineterminator="\n")

    manifest = {
        "analysis_id": "exp01-a-20261110-r1",
        "scope": "A producer feasibility audit of v1 after historical A/B results were seen",
        "analysis_parameters": {
            "feature_landmark_icu_hour": 12,
            "target_window_icu_hours": "(12,24]",
            "label_shift_hours": 6,
            "main_seed": 2026,
            "precision_proportions": [.5, .9],
            "illustrative_practical_difference_positive_rate": .10,
            "illustrative_practical_difference_selective_risk": .01,
            "difference_thresholds_status": "ILLUSTRATIVE_PENDING_TEAM_DECISION",
        },
        "input_archives_sha256": {key: registry[key]["sha256"] for key in archives},
        "source_package_manifest_sha256": digest(source_manifest),
        "frozen_member_sha256": frozen,
        "freeze_record_sha256": sha(freeze_path),
        "raw_replay_receipt_sha256": sha(replay_path),
        "raw_replay_checker_sha256": replay_summary["verification_code_sha256"],
        "raw_replay_verified_records": replay_summary["raw_records_checked"],
        "raw_replay_verified_feature_cells": replay_summary["included_feature_cells_checked"],
        "analysis_script_sha256": sha(__file__),
        "historical_coverage_sha256": sha(MAIN_RUN / "positive_coverage.csv"),
        "historical_bootstrap_sha256": sha(bootstrap_path),
        "aggregate_sha256": {name: sha(args.aggregate_dir / name) for name in outputs},
        "private_case_review": {"filename": cases.name, "sha256": sha(cases), "rows": len(audit),
                                "lost_target_event_rows": int(audit.review_all_lost_target_events.sum())},
        "verification_status": "A_PRODUCER_REPLAY_VERIFIED_C_REVIEW_PENDING",
    }
    (args.aggregate_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Verified {len(audit)} raw records and {len(cohort)} frozen rows. "
          f"Audit contains {int(audit.review_all_lost_target_events.sum())} excluded target transitions.")


if __name__ == "__main__":
    main()
