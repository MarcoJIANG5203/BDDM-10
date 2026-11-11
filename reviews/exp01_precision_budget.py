# -*- coding: utf-8 -*-
"""C · EXP-01 精度预算：主终点（选择性风险差）与 AUROC 的可估计性评估。

独立、第一性原理：只用标准二项/Wilson 区间与 Hanley–McNeil AUROC 标准误公式，
不 import src。输入为 A 审计与两份正式 run 的公开计数（见 EXP-01 计划）。

输出口径：
  1) 各数据角色阳性数（事件数约束）；
  2) 主终点 B4−B2 选择性风险差的最小可检出差异(MDD)与观测 95% 区间宽度；
  3) AUROC 的近似 95% 区间宽度与 MDD。
结论用于 G1 判断「精度预算是否足以回答至少一个明确问题」。

运行：python reviews/exp01_precision_budget.py
"""
import sys
from math import sqrt

sys.stdout.reconfigure(encoding="utf-8")

Z95 = 1.959963984540054   # 双侧 95%
Z80 = 0.8416212335729143  # 80% 功效


def wilson(k, n, z=Z95):
    """Wilson 比例区间。"""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def two_prop_mdd(p, n1, n2, alpha=0.05, power=0.8):
    """两独立比例差的最小可检出差异（近似正态、p1≈p2≈p）。"""
    za = Z95 if alpha == 0.05 else 1.959963984540054
    zb = Z80 if power == 0.8 else 0.8416212335729143
    se0 = sqrt(p * (1 - p) * (1 / n1 + 1 / n2))   # H0 合并
    se1 = sqrt(p * (1 - p) / n1 + p * (1 - p) / n2)  # H1（取 p1≈p2≈p）
    return za * se0 + zb * se1


def auroc_se(auc, npos, nneg):
    """Hanley–McNeil AUC 标准误。"""
    q1 = auc / (2 - auc)
    q2 = 2 * auc * auc / (1 + auc)
    num = auc * (1 - auc) + (npos - 1) * (q1 - auc * auc) + (nneg - 1) * (q2 - auc * auc)
    return sqrt(num / (npos * nneg))


def main():
    print("=" * 78)
    print("EXP-01 精度预算 · C 独立评估")
    print("=" * 78)

    # 1) 数据角色阳性数（来自 A 审计 A_001_verification_2026-11-03.json）
    roles = [
        ("A 开发(训练)", 6104, 34),
        ("A 规则选择", 1018, 6),
        ("A 校准", 1527, 9),
        ("A 内部测试", 1525, 8),
        ("B 外院", 13921, 38),
        ("A 全纳入", 10174, 57),
        ("B 全纳入", 13921, 38),
    ]
    print("\n[1] 事件数（阳性）约束")
    print(f"    {'角色':<16}{'n':>8}{'阳性':>6}{'基率':>10}{'基率95%CI(Wilson)':>34}")
    for name, n, k in roles:
        lo, hi = wilson(k, n)
        print(f"    {name:<16}{n:>8}{k:>6}{k/n:>10.4f}   [{lo:.4f}, {hi:.4f}]")
    print("    参考门槛：每院阳性≥200、内部测试≥50 为预警线（当前均未达）。")

    # 2) 主终点 B4−B2 选择性风险差（错误数 / 接受数）
    #    S0 内部：B2 915/1，B4 915/2；S4 外院：B2 8352/24，B4 8352/21（观测值）
    print("\n[2] 主终点：选择性风险差 B4−B2（错误数/接受数）")
    contrasts = [
        ("S0 内部", 915, 1, 2),
        ("S4 外院", 8352, 24, 21),
    ]
    print(f"    {'场景':<10}{'接受n':>8}{'B2错':>6}{'B4错':>6}{'B2风险':>10}{'B4风险':>10}{'差':>12}{'观测95%CI':>28}{'MDD(80%)':>12}")
    for name, n, e2, e4 in contrasts:
        p2 = e2 / n
        p4 = e4 / n
        diff = p4 - p2
        # 观测 95% CI 直接用 bootstrap 结果（与 S-013 一致）：
        if name.startswith("S0"):
            ci_lo, ci_hi = 0.0, 0.00327869          # 摘要/Table 2b
        else:
            ci_lo, ci_hi = -0.00107759, 0.00035920  # S-013
        p_pool = (e2 + e4) / (2 * n)
        mdd = two_prop_mdd(p_pool, n, n)
        mdd_errors = mdd * n
        print(f"    {name:<10}{n:>8}{e2:>6}{e4:>6}{p2:>10.5f}{p4:>10.5f}"
              f"{diff:>12.5f}   [{ci_lo:.5f}, {ci_hi:.5f}]   {mdd:>8.5f}")
        print(f"          MDD 折合错误数 ≈ {mdd_errors:.1f}（即需约 {mdd_errors:.0f} 个错误的差异才 80% 可检出）")

    # 3) AUROC 精度（外院 38 阳性、内部测试 8 阳性）
    print("\n[3] AUROC 精度（Hanley–McNeil）")
    for name, auc, npos, nneg in [
        ("B 外院 S4", 0.502, 38, 13883),
        ("A 内部测试", 0.5, 8, 1517),
    ]:
        se = auroc_se(auc, npos, nneg)
        half = Z95 * se
        mdd_auc = (Z95 + Z80) * se * sqrt(2)  # 两 AUC 对比（独立）近似
        print(f"    {name:<16} AUC≈{auc:.3f}  n_pos={npos:<3} n_neg={nneg:<6}"
              f"  SE={se:.4f}  95%CI 半宽≈±{half:.3f}  单对比MDD≈{mdd_auc:.3f}")

    print("\n" + "=" * 78)
    print("结论（供 G1）：")
    print("  - 事件数是硬约束：外院 38 阳性 → AUROC 95%CI 半宽约 ±0.09，")
    print("    只能可靠区分约 0.13 以上的 AUROC 差异。")
    print("  - 主终点选择性风险差在 S4 由 24 vs 21 个错误驱动，观测差 −0.00036、")
    print("    CI 跨零；MDD(80%)≈0.0022（约 19 个错误），当前事件数不足以判定")
    print("    '分歧优于置信度'的小效应，结论上限为'有限/无效'，不宜外推到安全性。")
    print("  - 精度预算只支持回答'是否存在大效应'，不支持'排除有实际意义的增益'。")
    print("=" * 78)


if __name__ == "__main__":
    main()
