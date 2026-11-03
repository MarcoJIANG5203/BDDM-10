# -*- coding: utf-8 -*-
"""C 独立标签核验：从 A 数据包的原始 .psv 小时文件逐例重算脓毒症结局标签。

用法：
    python reviews/verify_c_labels.py <A包根目录>

A 包根目录即 T1_A_Day1_2026-11-03_v1_Rebuilt_Full，需包含
data/processed/review_10_positive_10_negative.csv 与 data/processed/review_cases/{A,B}/*.psv。

核验规则（协议 v1）：
1. 找第一个 SepsisLabel==1 的小时 t_first；onset = t_first + 6（官方标签提前 6 小时）。
2. y=1 当且仅当 12 < onset <= 24；否则 y=0。无阳性标签者 y=0。
3. 结构检查：ICULOS 从 1 连续、观察满 24 小时、首小时非阳性（first-observation-positive）。

本脚本只读原始文件，不 import 仓库任何实验模块，独立于 A/B 的实现。
"""
import csv
import os
import sys


def verify_case(psv_path):
    with open(psv_path, encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    header = lines[0].split("|")
    i_iculos = header.index("ICULOS")
    i_sepsis = header.index("SepsisLabel")

    iculos, sepsis = [], []
    for ln in lines[1:]:
        c = ln.split("|")
        iculos.append(int(float(c[i_iculos])))
        sepsis.append(int(float(c[i_sepsis])))

    n = len(iculos)
    issues = []
    if iculos != list(range(1, n + 1)):
        issues.append("ICULOS不连续")
    if iculos[0] != 1:
        issues.append("首小时非1")
    if iculos[-1] < 24:
        issues.append("观察不足24小时")
    if sepsis[0] == 1:
        issues.append("首观测即阳性")

    ones = [h for h, s in zip(iculos, sepsis) if s == 1]
    t_first = min(ones) if ones else None
    onset = (t_first + 6) if t_first is not None else None
    y = 1 if (onset is not None and 12 < onset <= 24) else 0
    return y, onset, t_first, issues


def main(pkg_root):
    review_csv = os.path.join(pkg_root, "data", "processed", "review_10_positive_10_negative.csv")
    cases_dir = os.path.join(pkg_root, "data", "processed", "review_cases")

    with open(review_csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = []
    for r in rows:
        psv = os.path.join(cases_dir, r["site"], r["source_filename"])
        y_ind, onset, t_first, issues = verify_case(psv)
        y_A = int(r["y_true"])
        ok = (y_ind == y_A) and not issues
        results.append((r["patient_id"], r["site"], y_A, y_ind, onset, ok, issues))

    print(f"{'patient_id':<12} {'site':<2} {'y_A':>3} {'y_ind':>5} {'onset':>5}  match  问题")
    for pid, site, y_A, y_ind, onset, ok, issues in results:
        print(f"{pid:<12} {site:<2} {y_A:>3} {y_ind:>5} {str(onset):>5}  {str(ok):>5}  {', '.join(issues)}")

    n = len(results)
    n_ok = sum(1 for x in results if x[5])
    print(f"\n共 {n} 例；标签一致且无结构异常 {n_ok} 例；不一致 {n - n_ok} 例")
    return 0 if n_ok == n else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python reviews/verify_c_labels.py <A包根目录>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
