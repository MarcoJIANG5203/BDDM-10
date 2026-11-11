"""Stdlib-only recomputation of manuscript_draft.md numbers from the formal main run."""
import csv, sys, json
from collections import defaultdict

RUN = sys.argv[1]
out = {}

# ---- metrics.csv
M = list(csv.DictReader(open(f"{RUN}/metrics.csv")))
def m(**kw):
    r = [x for x in M if all(x[k] == v for k, v in kw.items())]
    return r
base = dict(model="LR", M="10", alpha="0.1", imputation_batch="0", predictor="MI")
for sc in ("S0", "S4"):
    for meth in ("B2", "B4"):
        for mode in ("batch", "frozen"):
            r = m(split_seed="2026", scenario=sc, method=meth, target_acceptance="0.6", selection_mode=mode, **base)
            assert len(r) == 1, (sc, meth, mode, len(r))
            r = r[0]
            out[f"{sc}_{meth}_{mode}"] = dict(n=r["n"], pos=r["positives"], acc=r["accepted"], err=r["accepted_errors"],
                                              fn=r["accepted_false_negative"], acc_rate=r["acceptance"],
                                              risk=r["selective_risk"], auroc=r["auroc"], cov=r["coverage"], pool=r["pool_size"])
# seed ranges
rng = defaultdict(list)
for seed in ("2026", "2027", "2028", "2029", "2030"):
    for meth in ("B2", "B4"):
        r = m(split_seed=seed, scenario="S4", method=meth, target_acceptance="0.6", selection_mode="frozen", **base)
        rng[f"S4_frozen_acc_{meth}"].append(float(r[0]["acceptance"]))
out["seed_ranges_frozen_external"] = {k: (min(v), max(v)) for k, v in rng.items()}

# ---- bootstrap
Bd = list(csv.DictReader(open(f"{RUN}/bootstrap_differences.csv")))
def bd(seed, sc, mode="batch", comp="B4-B2", c="0.6"):
    r = [x for x in Bd if x["split_seed"] == seed and x["scenario"] == sc and x["selection_mode"] == mode
         and x["comparison"] == comp and x["target_acceptance"] == c and x["model"] == "LR" and x["M"] == "10"
         and x["alpha"] == "0.1" and x["imputation_batch"] == "0"]
    return r
for sc in ("S0", "S4"):
    r = bd("2026", sc)[0]
    out[f"boot_{sc}"] = [round(float(r[k]) * 100, 3) for k in ("risk_difference", "ci_low", "ci_high")] + [r["valid"], r["invalid"]]
seedd = defaultdict(list)
for seed in ("2026", "2027", "2028", "2029", "2030"):
    for sc in ("S0", "S1", "S2", "S3", "S4"):
        r = bd(seed, sc)
        if r:
            seedd[sc].append(round(float(r[0]["risk_difference"]) * 100, 3))
out["seed_batch_diff_pp"] = dict(seedd)
comps = sorted({x["comparison"] for x in Bd})
out["comparisons_present"] = comps

# ---- per-patient pairing, stream big file
keep = defaultdict(dict)  # (sc,mode) -> meth -> {pid: (y, accepted, ypred, set0,set1)}
cov = defaultdict(lambda: [0, 0, 0, 0])  # sc -> n, covered, pos, pos_covered (from B2 rows; set is shared)
setflow = defaultdict(lambda: defaultdict(int))
with open(f"{RUN}/patient_predictions.csv", newline="") as f:
    rd = csv.reader(f)
    h = next(rd); ix = {k: i for i, k in enumerate(h)}
    for row in rd:
        if row[ix["split_seed"]] != "2026" or row[ix["model"]] != "LR" or row[ix["M"]] != "10":
            continue
        if row[ix["alpha"]] != "0.1" or row[ix["imputation_batch"]] != "0" or row[ix["predictor"]] != "MI":
            continue
        sc = row[ix["scenario"]]
        if sc not in ("S0", "S4"):
            continue
        meth = row[ix["method"]]
        if meth not in ("B2", "B4") or row[ix["target_acceptance"]] != "0.6":
            continue
        mode = row[ix["selection_mode"]]
        y = int(row[ix["y_true"]]); s0 = row[ix["set_0"]] == "True"; s1 = row[ix["set_1"]] == "True"
        acc = row[ix["accepted"]] == "True"; yp = row[ix["y_pred"]]
        keep[(sc, mode)].setdefault(meth, {})[row[ix["patient_id"]]] = (y, acc, yp, s0, s1)
        if meth == "B2" and mode == "batch":
            c = cov[sc]; c[0] += 1; covd = s1 if y else s0; c[1] += covd
            if y:
                c[2] += 1; c[3] += covd
                setflow[sc][("empty" if not (s0 or s1) else "both" if (s0 and s1) else "neg" if s0 else "pos")] += 1
out["coverage"] = {k: v for k, v in cov.items()}
out["positive_setflow"] = {k: dict(v) for k, v in setflow.items()}
for (sc, mode), d in keep.items():
    b2, b4 = d["B2"], d["B4"]
    assert b2.keys() == b4.keys()
    tab = defaultdict(int)
    for pid, (y, a2, p2, *_ ) in b2.items():
        if not y:
            continue
        _, a4, p4, *_ = b4[pid]
        miss2 = a2 and p2 == "0"; miss4 = a4 and p4 == "0"
        tab[("both" if miss2 and miss4 else "conf_only" if miss2 else "dis_only" if miss4 else "both_defer")] += 1
    out[f"pairs_{sc}_{mode}"] = dict(tab)
    out[f"acc_{sc}_{mode}"] = (sum(v[1] for v in b2.values()), sum(v[1] for v in b4.values()), len(b2))
print(json.dumps(out, indent=1, default=str))
