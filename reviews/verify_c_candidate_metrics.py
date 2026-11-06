# -*- coding: utf-8 -*-
"""C 独立指标核验：对 B 候选主矩阵 run 逐患者/逐区间独立重算。

独立于 B 的 reviews/verify_b_artifacts.py 与 reviews/verify_candidate_bootstrap.py：
不 import 仓库任何实验模块，只用 numpy/pandas/sklearn 从第一性原理重算——

  1. y_true 逐患者与 A cohort.parquet 交叉核对（防标签被替换）。
  2. score 重推：B2=min(p_mean,1-p_mean)、B3=missing_fraction、B4=p_std。
  3. 候选池 pool=(set_0+set_1==1)；B0/B1 accepted==pool。
  4. accepted 重推：B2/B3/B4 的 batch 用容量受限排序选 K（并列按 patient_id sha256 破同），
     frozen 用 thresholds.csv 的阈值+tie_hash 复现。
  5. 全部 900 行指标独立重算并与 metrics.csv 逐行比对。
  6. 30 个配对 bootstrap 区间（种子 2026，B4-B2，5场景×3容量×2模式）独立重算并比对。
  7. p_m 抽样的 p_mean/p_std(ddof=1)/类别翻转 独立重算。

用法：
    python reviews/verify_c_candidate_metrics.py <run目录> <cohort.parquet> [--skip-pm]
run 目录含 patient_predictions.csv / metrics.csv / bootstrap_differences.csv / thresholds.csv / p_m.csv。
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

TOL = 1e-9


# ---- 独立复述的协议原语（不 import src）----
def tie_bytes(patient_id):
    """sha256(patient_id) 的 32 字节大端表示，等价于原 hex 字符串的字典序比较。"""
    return int(hashlib.sha256(str(patient_id).encode()).hexdigest(), 16).to_bytes(32, 'big')


def stable_seed(*parts):
    return int.from_bytes(hashlib.sha256(json.dumps(parts, ensure_ascii=False).encode()).digest()[:4], 'big')


def batch_accept(pool, score, capacity, tie, copy_keys=None):
    """tie 为与 pool 等长的 32 字节并列键（sha256(patient_id) 大端字节）。"""
    pool = np.asarray(pool, bool)
    score = np.asarray(score, float)
    tie = np.asarray(tie)
    k = min(math.floor(capacity * len(pool)), int(pool.sum()))
    copy_keys = np.arange(len(pool)) if copy_keys is None else np.asarray(copy_keys)
    idx = np.flatnonzero(pool)
    if idx.size == 0:
        return np.zeros(len(pool), bool)
    # np.lexsort 末键为主键：按 (score, tie, copy_key) 优先级稳定排序。
    order = idx[np.lexsort((copy_keys[idx], tie[idx], score[idx]))]
    accepted = np.zeros(len(pool), bool)
    accepted[order[:k]] = True
    return accepted


def frozen_accept(pool, score, threshold, tie_hash_bytes, tie):
    score = np.asarray(score, float)
    tie = np.asarray(tie)
    return (np.asarray(pool, bool)
            & ((score < threshold)
               | ((score == threshold) & (tie <= tie_hash_bytes))))


def paired_bootstrap(y, pred, pool, score_a, score_b, capacity, repetitions, seed, tie,
                     fixed_a=None, fixed_b=None):
    y = np.asarray(y); pred = np.asarray(pred); pool = np.asarray(pool)
    score_a = np.asarray(score_a); score_b = np.asarray(score_b); tie = np.asarray(tie)
    rng = np.random.default_rng(seed)
    diff = []
    n = len(y)
    for _ in range(repetitions):
        ix = rng.integers(0, n, n)
        if fixed_a is None:
            a = batch_accept(pool[ix], score_a[ix], capacity, tie[ix], copy_keys=np.arange(n))
            b = batch_accept(pool[ix], score_b[ix], capacity, tie[ix], copy_keys=np.arange(n))
        else:
            a = np.asarray(fixed_a)[ix]; b = np.asarray(fixed_b)[ix]
        if not a.any() or not b.any():
            continue
        err = pred[ix] != y[ix]
        diff.append(float(err[a].mean() - err[b].mean()))
    return dict(
        ci_low=float(np.quantile(diff, 0.025)) if diff else float('nan'),
        ci_high=float(np.quantile(diff, 0.975)) if diff else float('nan'),
        valid=len(diff), invalid=repetitions - len(diff))


def ratio(a, b):
    return float(a / b) if b else float('nan')


def main():
    # 防止 Windows GBK 控制台遇到非 GBK 字符崩溃；正常 UTF-8 终端不受影响。
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('cohort_parquet')
    ap.add_argument('--skip-pm', action='store_true', help='跳过 p_m 抽样一致性核验')
    ap.add_argument('--output', help='写 JSON 结果摘要到该路径')
    args = ap.parse_args()
    root = Path(args.run)
    cohort_path = Path(args.cohort_parquet)

    cohort = pd.read_parquet(cohort_path)
    cohort['patient_id'] = cohort.patient_id.astype(str)
    print(f"[cohort] 行数 {len(cohort)}，阳性 {int(cohort.y_true.sum())}，"
          f"A 阳性 {int(cohort[cohort.site == 'A'].y_true.sum())}，"
          f"B 阳性 {int(cohort[cohort.site == 'B'].y_true.sum())}")

    dtypes = {
        'protocol_version': 'category', 'model': 'category', 'scenario': 'category',
        'predictor': 'category', 'method': 'category', 'selection_mode': 'category',
        'site': 'category', 'patient_id': 'category',
    }
    print("[load] patient_predictions.csv ...")
    pred = pd.read_csv(root / 'patient_predictions.csv', dtype=dtypes)
    pred['patient_id'] = pred.patient_id.astype(str)
    print(f"[load] patient_predictions 行数 {len(pred)}")

    metrics = pd.read_csv(root / 'metrics.csv')
    bootstrap = pd.read_csv(root / 'bootstrap_differences.csv')
    thresholds = pd.read_csv(root / 'thresholds.csv')

    failures = []

    def check(name, ok, detail=''):
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ''))
        if not ok:
            failures.append(name)

    # ---- 1. y_true 交叉核对 ----
    merged = pred.merge(cohort[['patient_id', 'y_true']].rename(columns={'y_true': 'cohort_y'}),
                        on='patient_id', how='left', validate='many_to_one')
    y_mismatch = (merged.y_true != merged.cohort_y).sum()
    n_na = merged.cohort_y.isna().sum()
    check('y_true 逐患者 == cohort.parquet',
          y_mismatch == 0 and n_na == 0,
          f'不一致 {y_mismatch} 行，缺失映射 {n_na} 行')

    # ---- 2. score 重推 ----
    score_ref = pd.Series(np.nan, index=pred.index)
    m = pred.method
    score_ref[m == 'B2'] = np.minimum(pred.loc[m == 'B2', 'p_mean'], 1 - pred.loc[m == 'B2', 'p_mean'])
    score_ref[m == 'B3'] = pred.loc[m == 'B3', 'missing_fraction']
    score_ref[m == 'B4'] = pred.loc[m == 'B4', 'p_std']
    has_score = pred.method.isin(['B2', 'B3', 'B4'])
    score_ok = np.allclose(pred.loc[has_score, 'score'], score_ref[has_score], rtol=0, atol=TOL, equal_nan=False)
    b01_score_na = pred.loc[~has_score, 'score'].isna().all()
    check('score 重推（B2/B3/B4）且 B0/B1 为 NaN',
          score_ok and b01_score_na,
          f'B2/B3/B4 匹配={score_ok}，B0/B1 NaN={b01_score_na}')

    # ---- 3. pool 重推 + B0/B1 accepted==pool ----
    pool = (pred.set_0.fillna(False).astype(int) + pred.set_1.fillna(False).astype(int)) == 1
    accept_in_pool = (~pred.accepted | pool).all()
    b01 = pred.method.isin(['B0', 'B1'])
    b01_accept_eq_pool = (pred.loc[b01, 'accepted'] == pool[b01]).all()
    check('候选池 pool=(set_0+set_1==1)，accepted subset of pool，B0/B1 accepted==pool',
          accept_in_pool and b01_accept_eq_pool,
          f'accept_in_pool={accept_in_pool}，B0/B1==pool={b01_accept_eq_pool}')

    # ---- 4. accepted 重推 ----
    pred = pred.assign(_pool=pool.to_numpy())
    accepted_ref = pd.Series(False, index=pred.index)
    # 阈值查表：(split_seed, method, target_acceptance) -> (threshold, tie_hash_bytes)
    thr_lookup = {}
    for _, t in thresholds.iterrows():
        thr_lookup[(int(t.split_seed), t.method, float(t.target_acceptance))] = \
            (float(t['threshold']), int(t['tie_hash'], 16).to_bytes(32, 'big'))
    patient_set_keys = ['split_seed', 'scenario', 'imputation_batch', 'target_acceptance', 'selection_mode']
    for method in ['B2', 'B3', 'B4']:
        sub = pred[pred.method == method]
        for vals, g in sub.groupby(patient_set_keys, sort=False, dropna=False):
            seed, scenario, batch, cap, mode = vals
            cap = float(cap)
            tie = np.array([tie_bytes(p) for p in g.patient_id], dtype='S32')
            if mode == 'batch':
                acc = batch_accept(g._pool.to_numpy(), g.score.to_numpy(), cap, tie)
            else:
                threshold, tie_hash_bytes = thr_lookup[(int(seed), method, cap)]
                acc = frozen_accept(g._pool.to_numpy(), g.score.to_numpy(), threshold, tie_hash_bytes, tie)
            accepted_ref.loc[g.index] = acc
    # B0/B1
    accepted_ref.loc[b01] = pool[b01].to_numpy()
    accept_mismatch = (pred.accepted != accepted_ref).sum()
    check('accepted 重推（batch 排序选 K / frozen 阈值 / B0B1=pool）与列一致',
          accept_mismatch == 0, f'不一致 {accept_mismatch} 行')

    # ---- 5. 900 行指标独立重算 ----
    pred = pred.assign(_accept=accepted_ref.to_numpy(),
                       _pool=pool.to_numpy())
    keys = ['split_seed', 'model', 'source_M', 'M', 'alpha', 'scenario',
            'imputation_batch', 'predictor', 'method', 'target_acceptance', 'selection_mode']
    computed = []
    for vals, g in pred.groupby(keys, dropna=False, sort=False):
        y = g.y_true.to_numpy()
        pred_cls = g.y_pred.to_numpy()
        accept = g._accept.to_numpy(bool)
        positives = y == 1
        negatives = accept & (pred_cls == 0)
        errors = accept & (pred_cls != y)
        hit = np.where(y == 1, g.set_1.to_numpy(bool), g.set_0.to_numpy(bool))
        p_mean = g.p_mean.to_numpy()
        row = dict(zip(keys, vals))
        row.update(
            n=len(g), positives=int(positives.sum()),
            accepted=int(accept.sum()), accepted_errors=int(errors.sum()),
            accepted_negative=int(negatives.sum()),
            accepted_false_negative=int((negatives & positives).sum()),
            acceptance=float(accept.mean()),
            selective_risk=ratio(errors.sum(), accept.sum()),
            dangerous_miss=ratio((negatives & positives).sum(), positives.sum()),
            negative_residual=ratio((negatives & positives).sum(), negatives.sum()),
            coverage=float(hit.mean()),
            auroc=float(roc_auc_score(y, p_mean)) if len(np.unique(y)) == 2 else float('nan'),
            auprc=float(average_precision_score(y, p_mean)) if positives.any() else float('nan'),
            pool_size=int(g._pool.sum()),
        )
        computed.append(row)
    comp = pd.DataFrame(computed)
    cmp = metrics.merge(comp, on=keys, validate='one_to_one', suffixes=('_saved', '_ind'))
    if len(cmp) != len(metrics):
        check('900 行指标：行数对齐', False, f'metrics {len(metrics)} vs 重算 {len(comp)}')
    else:
        check('900 行指标：行数对齐', True, f'{len(metrics)} 行')
        for col in ['n', 'positives', 'accepted', 'accepted_errors', 'accepted_negative',
                    'accepted_false_negative', 'acceptance', 'selective_risk',
                    'dangerous_miss', 'negative_residual', 'coverage', 'pool_size',
                    'auroc', 'auprc']:
            ok = np.allclose(cmp[col + '_saved'], cmp[col + '_ind'], rtol=0, atol=TOL, equal_nan=True)
            check(f'指标列 {col}', ok)

    # ---- 6. 30 个配对 bootstrap 区间 ----
    boot = bootstrap[bootstrap.comparison == 'B4-B2']
    print(f"[bootstrap] B4-B2 区间行数 {len(boot)}")
    n_boot_ok = 0
    n_boot_total = 0
    for _, br in boot.iterrows():
        scenario = br.scenario
        capacity = float(br.target_acceptance)
        mode = br.selection_mode
        # 保持 CSV 原始顺序（= split 文件顺序），与 B 实验的 ids 顺序一致，bootstrap 的按位抽样才能复现。
        sub = pred[(pred.split_seed == 2026) & (pred.scenario == scenario)
                   & (pred.imputation_batch == 0) & (pred.target_acceptance == capacity)
                   & (pred.method.isin(['B2', 'B4'])) & (pred.selection_mode == mode)]
        b2 = sub[sub.method == 'B2']
        b4 = sub[sub.method == 'B4']
        assert list(b2.patient_id) == list(b4.patient_id)
        ids = b2.patient_id.to_numpy()
        y = b2.y_true.to_numpy()
        pred_cls = b2.y_pred.to_numpy()
        pool_arr = b2._pool.to_numpy()
        score_a = b4.score.to_numpy()   # a = B4
        score_b = b2.score.to_numpy()   # b = B2
        tie = np.array([tie_bytes(i) for i in ids], dtype='S32')
        extra = {}
        if mode == 'frozen':
            extra = dict(fixed_a=b4._accept.to_numpy(), fixed_b=b2._accept.to_numpy())
        ci = paired_bootstrap(y, pred_cls, pool_arr, score_a, score_b, capacity,
                              int(br.valid) + int(br.invalid), stable_seed(2026, scenario, 'B4', 'B2', capacity, mode),
                              tie, **extra)
        aa = b4._accept.to_numpy(bool)
        bb = b2._accept.to_numpy(bool)
        rd = float((pred_cls[aa] != y[aa]).mean() - (pred_cls[bb] != y[bb]).mean()) if aa.any() and bb.any() else float('nan')
        ok_rd = np.allclose(rd, br.risk_difference, rtol=0, atol=TOL, equal_nan=True)
        ok_ci = (np.allclose(ci['ci_low'], br.ci_low, rtol=0, atol=TOL, equal_nan=True)
                 and np.allclose(ci['ci_high'], br.ci_high, rtol=0, atol=TOL, equal_nan=True)
                 and ci['valid'] == br.valid and ci['invalid'] == br.invalid)
        n_boot_total += 1
        if ok_rd and ok_ci:
            n_boot_ok += 1
        else:
            check(f'bootstrap {scenario}/{capacity}/{mode}', False,
                  f'rd 重算 {rd!r} vs {br.risk_difference!r}；ci {ci["ci_low"]!r},{ci["ci_high"]!r} vs {br.ci_low!r},{br.ci_high!r}')
    check(f'配对 bootstrap 区间（{n_boot_total} 个）独立重算', n_boot_ok == n_boot_total,
          f'{n_boot_ok}/{n_boot_total} 一致')

    # ---- 7. p_m 抽样一致性（可选）----
    if not args.skip_pm:
        print("[load] p_m.csv ...")
        pm = pd.read_csv(root / 'p_m.csv')
        pm['patient_id'] = pm.patient_id.astype(str)
        print(f"[load] p_m 行数 {len(pm)}")
        pm_sum = pm.groupby(['split_seed', 'model', 'source_M', 'M', 'alpha', 'scenario',
                             'imputation_batch', 'predictor', 'patient_id'],
                            sort=False).p_m.agg(['mean', 'std', 'size', 'min', 'max']).reset_index()
        pm_sum['std'] = pm_sum['std'].fillna(0.0)
        for (model,), g in pm_sum.groupby(['model']):
            pass
        joined = pred.merge(pm_sum, on=['split_seed', 'model', 'source_M', 'M', 'alpha', 'scenario',
                                        'imputation_batch', 'predictor', 'patient_id'],
                            how='left', validate='many_to_one')
        ok_mean = np.allclose(joined.p_mean, joined['mean'], rtol=0, atol=TOL, equal_nan=True)
        ok_std = np.allclose(joined.p_std, joined['std'], rtol=0, atol=TOL, equal_nan=True)
        ok_size = (joined['size'] == joined.M).all()
        ok_flip = np.array_equal(joined.flip.to_numpy(), ((joined['min'] < 0.5) & (joined['max'] >= 0.5)).to_numpy())
        check('p_m 抽样 p_mean/p_std(ddof=1)/size/flip 一致',
              ok_mean and ok_std and ok_size and ok_flip,
              f'mean={ok_mean} std={ok_std} size={ok_size} flip={ok_flip}')

    print("\n" + "=" * 60)
    print(f"独立指标核验完成：{len(failures)} 项检查失败")
    if failures:
        for f in failures:
            print("  -", f)
    if args.output:
        Path(args.output).write_text(
            json.dumps({'failed_checks': failures,
                        'patient_method_rows': int(len(pred)),
                        'y_true_mismatch': int(y_mismatch),
                        'acceptance_mismatch': int(accept_mismatch),
                        'bootstrap_ok': f'{n_boot_ok}/{n_boot_total}'},
                       ensure_ascii=False, indent=2),
            encoding='utf-8')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
