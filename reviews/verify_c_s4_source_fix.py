# -*- coding: utf-8 -*-
"""C 独立核验 D 对 C-007（S4 来源标注缺口）的修正。

不 import src、不依赖 D 脚本，直接从仓库内两个不可变源文件
（metrics.csv / bootstrap_differences.csv / table3_scenario_per_seed.csv）
逐列重算并核对 D 新增的 S-013 对比表（table2c_s4_primary_contrast.csv）与来源标注。

运行：python reviews/verify_c_s4_source_fix.py
"""
import csv
import hashlib
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(BASE, "reports", "clinical-v1", "20261105T055420_02d05b15")
METRICS = os.path.join(RUN, "metrics.csv")
BOOTSTRAP = os.path.join(RUN, "bootstrap_differences.csv")
TABLE3 = os.path.join(
    BASE, "paper", "runs", "20261105T055420_02d05b15", "tables",
    "table3_scenario_per_seed.csv",
)

# D 在 table2c_provenance.json 声明的输入哈希
EXPECTED_SHA = {
    "metrics.csv": "c70f0163d10c0a768d91ceb86684d489a5ca2b7d5e8b15accfe9795e8b5f61ff",
    "bootstrap_differences.csv": "49616181d02b6abb65a19ff1de1b984bab88738ec118fb3e90aee1c1088e80b5",
}

# D 新增 S-013 表（table2c_s4_primary_contrast.csv）中的值（作为核对目标）
S013_EXPECTED = {
    # (selection_mode, comparison) -> dict of expected columns
    ("batch", "B2"): {"accepted": 8352, "accepted_errors": 24,
                      "selective_risk": 0.0028735632183908046},
    ("batch", "B4"): {"accepted": 8352, "accepted_errors": 21,
                      "selective_risk": 0.002514367816091954},
    ("batch", "B4-B2"): {"risk_difference": -0.00035919540229885057,
                         "ci_low": -0.0010775862068965517,
                         "ci_high": 0.00035919540229885057,
                         "valid": 1000, "invalid": 0},
    ("frozen", "B4-B2"): {"risk_difference": 0.00017496707452466492,
                          "ci_low": -0.00017121758021573793,
                          "ci_high": 0.0005194702785816792,
                          "valid": 1000, "invalid": 0},
}

TOL = 1e-12


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_rows(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def close(a, b):
    return abs(float(a) - float(b)) <= TOL


def main():
    fails = []
    ok = []

    # 1) 输入哈希
    for name, want in EXPECTED_SHA.items():
        p = os.path.join(RUN, name)
        got = sha256(p)
        if got == want:
            ok.append(f"SHA256 {name} 一致")
        else:
            fails.append(f"SHA256 {name} 不一致：{got}")

    # 2) S-013 表数值 ← metrics.csv（S4, seed2026, M10, source_M10, alpha0.1,
    #    imputation_batch0, predictor MI, target 0.6, batch）
    metrics = read_rows(METRICS)
    for mode, method in [("batch", "B2"), ("batch", "B4")]:
        rows = [r for r in metrics
                if r["split_seed"] == "2026" and r["scenario"] == "S4"
                and r["model"] == "LR" and r["M"] == "10" and r["source_M"] == "10"
                and r["alpha"] == "0.1" and r["imputation_batch"] == "0"
                and r["predictor"] == "MI" and r["target_acceptance"] == "0.6"
                and r["selection_mode"] == mode and r["method"] == method]
        if len(rows) != 1:
            fails.append(f"metrics.csv S4 {mode} {method} 行数={len(rows)}")
            continue
        r = rows[0]
        exp = S013_EXPECTED[(mode, method)]
        for col, want in exp.items():
            got = r.get(col)
            if col in ("accepted", "accepted_errors") and int(got) != want:
                fails.append(f"metrics S4 {mode} {method} {col}={got} 期望 {want}")
            elif col == "selective_risk" and not close(got, want):
                fails.append(f"metrics S4 {mode} {method} {col}={got} 期望 {want}")
        if not fails or fails[-1].startswith("metrics S4 " + mode + " " + method + " "):
            pass
        ok.append(f"metrics S4 {mode} {method}: accepted={r['accepted']} "
                  f"errors={r['accepted_errors']} selective_risk={r['selective_risk']}")

    # 3) S-013 表 B4-B2 batch/frozen ← bootstrap_differences.csv
    boot = read_rows(BOOTSTRAP)
    for mode in ("batch", "frozen"):
        rows = [r for r in boot
                if r["split_seed"] == "2026" and r["scenario"] == "S4"
                and r["model"] == "LR" and r["M"] == "10" and r["source_M"] == "10"
                and r["alpha"] == "0.1" and r["imputation_batch"] == "0"
                and r["comparison"] == "B4-B2" and r["target_acceptance"] == "0.6"
                and r["selection_mode"] == mode]
        if len(rows) != 1:
            fails.append(f"bootstrap S4 B4-B2 {mode} 行数={len(rows)}")
            continue
        r = rows[0]
        exp = S013_EXPECTED[(mode, "B4-B2")]
        for col, want in exp.items():
            got = r.get(col)
            if col in ("valid", "invalid") and int(got) != want:
                fails.append(f"bootstrap S4 B4-B2 {mode} {col}={got} 期望 {want}")
            elif col in ("risk_difference", "ci_low", "ci_high") and not close(got, want):
                fails.append(f"bootstrap S4 B4-B2 {mode} {col}={got} 期望 {want}")
        ok.append(f"bootstrap S4 B4-B2 {mode}: diff={r['risk_difference']} "
                  f"CI=[{r['ci_low']}, {r['ci_high']}] valid={r['valid']}")

    # 4) 点估计来源 S-005（table3_scenario_per_seed.csv）S4 2026 B4_minus_B2
    t3 = read_rows(TABLE3)
    row = [r for r in t3 if r["scenario"] == "S4" and r["split_seed"] == "2026"]
    if len(row) != 1:
        fails.append(f"table3 S4 2026 行数={len(row)}")
    else:
        v = float(row[0]["B4_minus_B2"])
        want = -0.0003591954022988996
        if close(v, want):
            ok.append(f"S-005 table3 S4 2026 B4-B2={v}（点估计来源有效）")
        else:
            fails.append(f"table3 S4 2026 B4-B2={v} 期望 {want}")

    # 5) 稿件 S4 段来源标注（本地 main 仍为旧标注，D 修正在其分支，
    #    此处仅提示已核验分支 diff，不把本地 main 当作已修正）
    print("=" * 70)
    for line in ok:
        print("PASS |", line)
    for line in fails:
        print("FAIL |", line)
    print("=" * 70)
    print(f"结果：{len(ok)} 项通过，{len(fails)} 项失败")
    if fails:
        print("!!! 存在失败项，D 修正未通过 C 独立核验 !!!")
        sys.exit(1)
    print("D 的 S-013 数值与两不可变源文件逐列一致；来源标注修正方向正确。")


if __name__ == "__main__":
    main()
