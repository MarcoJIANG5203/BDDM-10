# -*- coding: utf-8 -*-
"""C 独立核验：时间边界（time-boundary）合成案例。

按协议 v1（T1_统一实验说明_v1.md 第 1 节、docs/A到B_数据交接说明.md 第 4 节）独立复述边界规则，
构造落在判定边界上的合成小时序列，验证规则在半开区间 (12,24] 上的正确性。

参考规则（独立复述，非照抄仓库实现）：
  1. 时间坐标 = ICULOS（ICU 小时，从 1 起）。
  2. 找第一个 SepsisLabel==1 的小时 t_first；官方标签比真实起病提前 6 小时，
     onset = t_first + 6。
  3. y = 1 当且仅当 12 < onset <= 24（即 13 <= onset <= 24）；否则 y = 0。
     无任何阳性标签者 onset=None，y = 0。
  4. 首观测即阳性（t_first==1）属于应排除范围，不能填精确起病时刻（这里标记 first_obs_positive）。

本脚本只使用标准库，不 import 仓库任何实验模块；只验证“规则本身在边界上是否正确”，
不替代对 A 原始 40,336 份 .psv 小时文件的逐例重算（那需要 A 的原始 receipt，不在 B 候选包内）。

用法：
    python reviews/verify_c_time_boundary.py [cohort_audit.json]
可选给出 cohort_audit.json 时，额外断言其时间窗声明与协议一致。
"""
import json
import sys


def derive_y(sepsis_hours):
    """sepsis_hours: list[int]，下标 i 对应 ICULOS=i+1（小时从 1 开始）。

    返回 (y, onset, t_first, first_obs_positive)。
    """
    n = len(sepsis_hours)
    assert n >= 1
    t_first = None
    for h, s in enumerate(sepsis_hours, start=1):
        if s == 1:
            t_first = h
            break
    first_obs_positive = sepsis_hours[0] == 1
    onset = (t_first + 6) if t_first is not None else None
    y = 1 if (onset is not None and 12 < onset <= 24) else 0
    return y, onset, t_first, first_obs_positive


def make_sequence(first_positive_hour, length=24):
    """构造长度 length 的小时序列：从 first_positive_hour 起全部为 1，此前为 0。

    first_positive_hour=None 表示全程无阳性标签。
    """
    return [1 if (first_positive_hour is not None and h >= first_positive_hour) else 0
            for h in range(1, length + 1)]


def main():
    # (描述, first_positive_hour, 期望 y, 期望 onset, 期望 first_obs_positive)
    cases = [
        ("首观测即阳性 t_first=1 -> onset=7（<=12，排除）", 1, 0, 7, True),
        ("t_first=5 -> onset=11（<=12，排除）", 5, 0, 11, False),
        ("边界 t_first=6 -> onset=12（12<12 为假，排除）", 6, 0, 12, False),
        ("边界 t_first=7 -> onset=13（首个纳入阳性）", 7, 1, 13, False),
        ("t_first=8 -> onset=14（纳入）", 8, 1, 14, False),
        ("t_first=17 -> onset=23（纳入）", 17, 1, 23, False),
        ("边界 t_first=18 -> onset=24（24<=24 为真，末个纳入阳性）", 18, 1, 24, False),
        ("边界 t_first=19 -> onset=25（24<25，排除）", 19, 0, 25, False),
        ("t_first=20 -> onset=26（排除）", 20, 0, 26, False),
        ("全程无阳性标签 -> onset=None（y=0）", None, 0, None, False),
    ]

    failures = 0
    print(f"{'描述':<46} {'y':>2} {'onset':>5} {'first+':>6}  结果")
    print("-" * 92)
    for desc, fph, exp_y, exp_onset, exp_fop in cases:
        seq = make_sequence(fph)
        y, onset, t_first, first_obs_positive = derive_y(seq)
        ok = (y == exp_y) and (onset == exp_onset) and (first_obs_positive == exp_fop)
        if not ok:
            failures += 1
        print(f"{desc:<46} {y:>2} {str(onset):>5} {str(first_obs_positive):>6}  "
              f"{'PASS' if ok else 'FAIL (期望 y=%d onset=%s first=%s)' % (exp_y, exp_onset, exp_fop)}")

    # 半开区间显式断言：onset 恰好 13 与 24 纳入，12 与 25 排除。
    boundary_expect = {
        12: 0, 13: 1, 24: 1, 25: 0,
    }
    print("\n半开区间 (12,24] 边界显式断言：")
    for onset, exp in sorted(boundary_expect.items()):
        t_first = onset - 6
        y, _, _, _ = derive_y(make_sequence(t_first))
        ok = (y == exp)
        failures += (not ok)
        print(f"  onset={onset:>2} (t_first={t_first:>2}) -> y={y} 期望 {exp}  {'PASS' if ok else 'FAIL'}")

    # 可选：校验 cohort_audit.json 的时间窗声明。
    audit_ok = True
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            audit = json.load(f)
        expected = {"feature_window_end": 12, "outcome_window": "(12,24]", "label_shift_hours": 6}
        print("\ncohort_audit.json 时间窗声明核验：")
        for k, v in expected.items():
            got = audit.get(k)
            ok = (got == v)
            audit_ok = audit_ok and ok
            print(f"  {k}: 声明 {got!r} 期望 {v!r}  {'PASS' if ok else 'FAIL'}")
        # 审计中 onset_at_or_before_12 与 first_observation_positive 排除数应为 0（协议要求最终队列不含早/左删失起病）。
        for k in ["onset_at_or_before_12", "first_observation_positive"]:
            got = audit.get("exclusion_counts", {}).get(k)
            print(f"  exclusion_counts.{k} = {got}（协议：此类在入组前已被排除，最终队列应为 0）")

    print("\n" + "=" * 60)
    print(f"时间边界合成案例：共 {len(cases) + len(boundary_expect)} 项断言，"
          f"失败 {failures} 项" + ("；审计声明 " + ("一致" if audit_ok else "不一致") if len(sys.argv) > 1 else ""))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
