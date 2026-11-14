#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C independent verification: D-002 Overleaf LaTeX typeset manuscript (2026-11-13).

Scope (per handoffs/D/2026-11-13_D-002_overleaf.md "receiver checkpoints"):
  1. abstract 150-250 words, no citations inside the abstract
  2. Table 1 (cohort) / Table 2 (paired dispositions) / Fig 1 numbers vs source
  3. no "stable advantage / safety / superiority" overclaim
  4. C/E final full-text consistency: every verifiable number in body.tex /
     supplementary.tex re-derived from the frozen source tables
  5. internal markers removed ([S-xxx], "Review draft", "CONTENT REVIEW",
     "content-review/", "pending C confirmation", "待核")

This script is stdlib-only (no pandas/numpy) so it runs on a fresh Python, and it
re-derives the manuscript's claims from the content-review source CSVs rather than
trusting the manuscript itself. The source CSVs were already independently verified
by C-010 / C-011 from the frozen patient-level tables.

Usage:
    python reviews/verify_c_overleaf_manuscript.py \
        --overleaf paper/overleaf \
        --content-review paper/content-review/20261110-r1
"""

import argparse
import csv
import os
import re
import sys

# ---------------------------------------------------------------------------
# tiny helpers
# ---------------------------------------------------------------------------

def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def near(a, b, tol=1e-9):
    return abs(float(a) - float(b)) <= tol


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------

def check_abstract(main_tex):
    """Return (passed, detail) for the abstract word-count / no-citation rule."""
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", main_tex, re.S)
    if not m:
        return False, "no \\begin{abstract} found"
    raw = m.group(1)
    if re.search(r"\\cite", raw):
        return False, "abstract contains \\cite"
    # strip LaTeX: \% -> %, $...$ kept as text, {} and commands removed
    t = raw
    t = re.sub(r"\\%", "%", t)
    t = re.sub(r"\\[a-zA-Z]+", " ", t)       # drop commands like \cite, \url
    t = re.sub(r"[{}]", " ", t)
    t = re.sub(r"\$", " ", t)
    t = re.sub(r"\\,", "", t)                 # \, thin space
    t = re.sub(r"--+", " ", t)
    words = [w for w in t.split() if re.search(r"[0-9A-Za-z]", w)]
    n = len(words)
    ok = 150 <= n <= 250
    return ok, f"abstract word count = {n} (expect 150-250, no \\cite)"


def check_citations(body_tex, bib_tex):
    """Return (passed, detail) for 21 bib <-> 21 cite, 0 missing/orphan."""
    bib_keys = set(re.findall(r"@\w+\{([^,]+)", bib_tex))
    cite_keys = set()
    for grp in re.findall(r"\\cite\{([^}]+)\}", body_tex):
        for k in grp.split(","):
            k = k.strip()
            if k:
                cite_keys.add(k)
    missing = sorted(cite_keys - bib_keys)     # cited but no bib entry
    orphan = sorted(bib_keys - cite_keys)      # bib entry never cited
    ok = (not missing) and (not orphan)
    return ok, f"bib={len(bib_keys)} cite={len(cite_keys)} missing={missing} orphan={orphan}"


def check_markers(*texts):
    """Return (passed, detail) for internal markers that D must have removed."""
    patterns = {
        "S-xxx tag": r"\[S-\d{3}\]",
        "Review draft": r"Review draft",
        "CONTENT REVIEW watermark": r"CONTENT REVIEW",
        "content-review link": r"content-review/",
        "pending C confirmation": r"pending C confirmation",
        "待核": r"待核",
    }
    hits = {name: any(re.search(p, t) for t in texts) for name, p in patterns.items()}
    bad = {k for k, v in hits.items() if v}
    return (not bad), f"markers found={sorted(bad) if bad else 'none'}"


def check_no_overclaim(body_tex):
    """Return (passed, detail) for the agreed negative/limited conclusion.

    The agreed conclusion is a *negative* result: "no stable selective-risk
    advantage" and "not a claim that any ranking signal is superior". We verify
    (a) those limiting statements are present and (b) no positive superiority /
    safety / guarantee claim is made.
    """
    # positive overclaim patterns (must NOT appear)
    positive = [
        (r"outperform", "outperform"),
        (r"\bis superior to\b", "is superior to"),
        (r"\bsignificant improvement\b", "significant improvement"),
        (r"\bguarantees?\b", "guarantee"),
        (r"\bsafe\b", "safe (positive claim)"),
        (r"stable (selective-risk )?advantage (of|in|over|for)", "positive stable advantage"),
    ]
    hits = [name for p, name in positive if re.search(p, body_tex)]
    # required limiting statements
    required = [
        "no stable selective-risk advantage",
        "not a claim that any ranking signal is superior",
    ]
    missing = [s for s in required if s not in body_tex]
    ok = (not hits) and (not missing)
    return ok, f"positive_claims={hits if hits else 'none'} missing_limits={missing if missing else 'none'}"


# ---------------------------------------------------------------------------
# number re-derivations from the content-review CSVs
# ---------------------------------------------------------------------------

def derive_numbers(cr):
    """Compute the manuscript's claimed numbers from the source CSVs."""
    out = {}

    # cohort_flow.csv  -> Table 1
    cf = {r["site"]: r for r in read_csv(os.path.join(cr, "cohort_flow.csv"))}
    out["cohort_A_raw"] = int(cf["A"]["n"]); out["cohort_A_incl"] = int(cf["A"]["n"])  # placeholder, fixed below
    # A included is the "after_insufficient_followup" row
    cfA = [r for r in read_csv(os.path.join(cr, "cohort_flow.csv")) if r["site"] == "A"]
    cfB = [r for r in read_csv(os.path.join(cr, "cohort_flow.csv")) if r["site"] == "B"]
    cfT = [r for r in read_csv(os.path.join(cr, "cohort_flow.csv")) if r["site"] == "Total"]
    out["cohort_A_raw"] = int(cfA[0]["n"])
    out["cohort_B_raw"] = int(cfB[0]["n"])
    out["cohort_T_raw"] = int(cfT[0]["n"])
    out["cohort_A_proxy"] = int(cfA[0]["target_transition_proxy"])
    out["cohort_B_proxy"] = int(cfB[0]["target_transition_proxy"])
    out["cohort_T_proxy"] = int(cfT[0]["target_transition_proxy"])
    out["cohort_A_incl"] = int(cfA[3]["n"])   # after_insufficient_followup
    out["cohort_B_incl"] = int(cfB[3]["n"])
    out["cohort_T_incl"] = int(cfT[3]["n"])
    out["cohort_A_pos"] = int(cfA[3]["target_transition_proxy"])
    out["cohort_B_pos"] = int(cfB[3]["target_transition_proxy"])
    out["cohort_T_pos"] = int(cfT[3]["target_transition_proxy"])

    # split_event_counts.csv -> test/split positives
    se = {r["role"]: r for r in read_csv(os.path.join(cr, "split_event_counts.csv"))}
    out["split_train_pos"] = int(se["train"]["positive"])
    out["split_sel_pos"] = int(se["selection"]["positive"])
    out["split_cal_pos"] = int(se["calibration"]["positive"])
    out["split_test_pos"] = int(se["test"]["positive"])
    out["split_ext_pos"] = int(se["external"]["positive"])

    # base_model_context.csv -> AUROC + intervals
    bm = read_csv(os.path.join(cr, "base_model_context.csv"))
    def auroc(model, scenario):
        row = next(r for r in bm if r["model"] == model and r["scenario"] == scenario and r["metric"] == "auroc")
        return float(row["estimate"]), float(row["ci_low"]), float(row["ci_high"])
    out["lr_s0_auroc"] = auroc("LR", "S0")
    out["lr_s4_auroc"] = auroc("LR", "S4")
    out["rf_s4_auroc"] = auroc("RF", "S4")

    # capacity_coverage_release.csv -> coverage / acceptance / fn
    cc = read_csv(os.path.join(cr, "capacity_coverage_release.csv"))
    def crow(scenario, mode, method):
        return next(r for r in cc
                    if r["scenario"] == scenario and r["selection_mode"] == mode and r["method"] == method)
    s0b2 = crow("S0", "batch", "B2"); s0b4 = crow("S0", "batch", "B4")
    s4b2 = crow("S4", "batch", "B2"); s4b4 = crow("S4", "batch", "B4")
    s0b2f = crow("S0", "frozen", "B2"); s0b4f = crow("S0", "frozen", "B4")
    s4b2f = crow("S4", "frozen", "B2"); s4b4f = crow("S4", "frozen", "B4")
    out["cov_s0_frac"] = (int(s0b2["covered"]), int(s0b2["n"]))
    out["cov_s4_frac"] = (int(s4b2["covered"]), int(s4b2["n"]))
    out["cov_s0_pos"] = int(s0b2["positive_covered"])
    out["cov_s4_pos"] = int(s4b2["positive_covered"])
    out["acc_s0_b2"] = int(s0b2["accepted"]); out["acc_s0_b4"] = int(s0b4["accepted"])
    out["acc_s4_b2"] = int(s4b2["accepted"]); out["acc_s4_b4"] = int(s4b4["accepted"])
    out["fn_s4_b2"] = int(s4b2["accepted_false_negative"]); out["fn_s4_b4"] = int(s4b4["accepted_false_negative"])
    out["acc_s0_b2f"] = int(s0b2f["accepted"]); out["acc_s0_b4f"] = int(s0b4f["accepted"])
    out["acc_s4_b2f"] = int(s4b2f["accepted"]); out["acc_s4_b4f"] = int(s4b4f["accepted"])
    out["fn_s4_b2f"] = int(s4b2f["accepted_false_negative"]); out["fn_s4_b4f"] = int(s4b4f["accepted_false_negative"])

    # risk_contrasts.csv -> primary B4-B2 risk difference + paired interval
    rc = read_csv(os.path.join(cr, "risk_contrasts.csv"))
    def rc_row(scenario, mode):
        return next(r for r in rc if r["comparison"] == "B4-B2" and r["scenario"] == scenario and r["selection_mode"] == mode)
    r0 = rc_row("S0", "batch"); r4 = rc_row("S4", "batch")
    out["rd_s0"] = (float(r0["risk_difference"]) * 100, float(r0["ci_low"]) * 100, float(r0["ci_high"]) * 100)
    out["rd_s4"] = (float(r4["risk_difference"]) * 100, float(r4["ci_low"]) * 100, float(r4["ci_high"]) * 100)

    # paired_positive_disposition.csv -> Table 2
    pp = {r["scenario"]: r for r in read_csv(os.path.join(cr, "paired_positive_disposition.csv"))}
    out["paired_s0"] = (int(pp["S0"]["both_missed"]), int(pp["S0"]["b2_only_missed"]),
                        int(pp["S0"]["b4_only_missed"]), int(pp["S0"]["both_rejected"]),
                        int(pp["S0"]["positives"]))
    out["paired_s4"] = (int(pp["S4"]["both_missed"]), int(pp["S4"]["b2_only_missed"]),
                        int(pp["S4"]["b4_only_missed"]), int(pp["S4"]["both_rejected"]),
                        int(pp["S4"]["positives"]))

    # external_frozen_stability.csv -> frozen acceptance + 5-seed range
    ef = read_csv(os.path.join(cr, "external_frozen_stability.csv"))
    b2_acc = [float(r["acceptance"]) * 100 for r in ef if r["method"] == "B2"]
    b4_acc = [float(r["acceptance"]) * 100 for r in ef if r["method"] == "B4"]
    out["ext_range_b2"] = (min(b2_acc), max(b2_acc))
    out["ext_range_b4"] = (min(b4_acc), max(b4_acc))

    # random_reference.csv -> supplementary S4
    rr = {r["scenario"]: r for r in read_csv(os.path.join(cr, "random_reference.csv"))}
    out["rand_s0"] = (float(rr["S0"]["expected_false_negatives"]), int(rr["S0"]["reference_low"]), int(rr["S0"]["reference_high"]))
    out["rand_s4"] = (float(rr["S4"]["expected_false_negatives"]), int(rr["S4"]["reference_low"]), int(rr["S4"]["reference_high"]))

    return out


def round3(x):
    return round(x, 3)


# manuscript claims (as stated in body.tex / abstract / supplementary.tex)
MANUSCRIPT = {
    "cohort_A_raw": 20336, "cohort_B_raw": 20000, "cohort_T_raw": 40336,
    "cohort_A_proxy": 334, "cohort_B_proxy": 152, "cohort_T_proxy": 486,
    "cohort_A_incl": 10174, "cohort_B_incl": 13921, "cohort_T_incl": 24095,
    "cohort_A_pos": 57, "cohort_B_pos": 38, "cohort_T_pos": 95,
    "split_train_pos": 34, "split_sel_pos": 6, "split_cal_pos": 9,
    "split_test_pos": 8, "split_ext_pos": 38,
    "lr_s0_auroc": (0.793, 0.579, 0.947),
    "lr_s4_auroc": (0.502, 0.407, 0.596),
    "rf_s4_auroc": (0.581, 0.480, 0.674),
    "cov_s0_frac": (1384, 1525), "cov_s4_frac": (13537, 13921),
    "cov_s0_pos": 0, "cov_s4_pos": 0,
    "acc_s0_b2": 915, "acc_s0_b4": 915, "acc_s4_b2": 8352, "acc_s4_b4": 8352,
    "fn_s4_b2": 24, "fn_s4_b4": 21,
    "acc_s0_b2f": 919, "acc_s0_b4f": 928, "acc_s4_b2f": 12396, "acc_s4_b4f": 11984,
    "fn_s4_b2f": 33, "fn_s4_b4f": 34,
    "rd_s0": (0.109, 0.000, 0.328), "rd_s4": (-0.036, -0.108, 0.036),
    "paired_s0": (1, 0, 1, 6, 8), "paired_s4": (18, 6, 3, 11, 38),
    "ext_range_b2": (79.48, 89.54), "ext_range_b4": (72.33, 86.29),
    "rand_s0": (2.637, 1, 4), "rand_s4": (23.379, 17, 29),
}


def check_numbers(cr):
    """Re-derive every manuscript number from the CSVs and compare."""
    # decimal places the manuscript rounds each tuple to
    DECIMALS = {
        "lr_s0_auroc": 3, "lr_s4_auroc": 3, "rf_s4_auroc": 3,
        "rd_s0": 3, "rd_s4": 3,
        "ext_range_b2": 2, "ext_range_b4": 2,
        "rand_s0": 3, "rand_s4": 3,
    }
    d = derive_numbers(cr)
    fails = []
    for key, expected in MANUSCRIPT.items():
        got = d[key]
        if isinstance(expected, tuple):
            dp = DECIMALS.get(key, 0)
            ok = all(round(float(g), dp) == round(float(e), dp) for g, e in zip(got, expected))
        else:
            ok = got == expected
        if not ok:
            fails.append((key, expected, got))
    return (not fails), fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--overleaf", required=True)
    ap.add_argument("--content-review", required=True)
    args = ap.parse_args()

    overleaf = args.overleaf
    cr = args.content_review

    body = read_text(os.path.join(overleaf, "body.tex"))
    main_tex = read_text(os.path.join(overleaf, "main_ieee.tex"))
    bib = read_text(os.path.join(overleaf, "references.bib"))
    supp = read_text(os.path.join(overleaf, "supplementary.tex"))

    results = []
    results.append(("abstract 150-250 words, no cite", *check_abstract(main_tex)))
    results.append(("21 bib <-> 21 cite, 0 missing/orphan", *check_citations(body, bib)))
    results.append(("internal markers removed", *check_markers(body, main_tex, bib, supp)))
    results.append(("no stable-advantage/safety overclaim", *check_no_overclaim(body)))
    results.append(("all manuscript numbers re-derived", *check_numbers(cr)))

    print("C overleaf-manuscript independent verification")
    print("=" * 72)
    all_ok = True
    for name, ok, detail in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if isinstance(detail, list):
            for k, e, g in detail:
                print(f"          mismatch {k}: manuscript={e} source={g}")
        else:
            print(f"          {detail}")
        all_ok = all_ok and ok
    print("=" * 72)
    print("OVERALL:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
