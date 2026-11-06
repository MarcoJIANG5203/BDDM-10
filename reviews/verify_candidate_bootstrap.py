"""Recompute saved candidate paired-bootstrap intervals without src.metrics.

Vectorized sorting uses the same documented score, ID-hash and sampled-copy
ordering. Both batch re-ranking and frozen acceptance are checked for every
saved comparison; clinical/scientific acceptance is outside this audit.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def verify(root):
    predictions = pd.read_csv(root / 'patient_predictions.csv', float_precision='round_trip')
    intervals = pd.read_csv(root / 'bootstrap_differences.csv', float_precision='round_trip')
    import yaml
    config = yaml.safe_load((root / 'config.yaml').read_text(encoding='utf-8'))
    checked = []
    for row in intervals.itertuples(index=False):
        a, b = row.comparison.split('-')
        mask = ((predictions.split_seed == row.split_seed)
                & (predictions.model == row.model) & (predictions.M == row.M)
                & (predictions.scenario == row.scenario) & (predictions.alpha == row.alpha)
                & (predictions.imputation_batch == row.imputation_batch)
                & (predictions.target_acceptance == row.target_acceptance)
                & (predictions.selection_mode == row.selection_mode))
        first = predictions.loc[mask & (predictions.method == a)].reset_index(drop=True)
        second = predictions.loc[mask & (predictions.method == b)].set_index('patient_id').loc[first.patient_id]
        assert len(first) == len(second) > 0
        assert np.array_equal(first.y_true, second.y_true)
        assert np.array_equal(first.y_pred, second.y_pred)
        assert np.array_equal(first.set_0, second.set_0) and np.array_equal(first.set_1, second.set_1)
        n = len(first)
        hashes = np.array([hashlib.sha256(str(pid).encode()).hexdigest() for pid in first.patient_id])
        tie_ranks = np.empty(n, dtype=int)
        tie_ranks[np.argsort(hashes)] = np.arange(n)
        pool = first.set_0.to_numpy(int) + first.set_1.to_numpy(int) == 1
        errors = first.y_pred.to_numpy() != first.y_true.to_numpy()
        score_a, score_b = first.score.to_numpy(), second.score.to_numpy()
        accepted_a, accepted_b = first.accepted.to_numpy(bool), second.accepted.to_numpy(bool)
        parts = (int(row.split_seed), row.scenario, a, b, float(row.target_acceptance), row.selection_mode)
        seed = int.from_bytes(hashlib.sha256(json.dumps(parts, ensure_ascii=False).encode()).digest()[:4], 'big')
        rng = np.random.default_rng(seed)
        differences = []
        for _ in range(config['bootstrap']):
            sample = rng.integers(0, n, n)
            if row.selection_mode == 'batch':
                eligible = np.flatnonzero(pool[sample])
                k = min(int(np.floor(row.target_acceptance * n)), len(eligible))
                ranked_a = np.lexsort((eligible, tie_ranks[sample][eligible], score_a[sample][eligible]))
                ranked_b = np.lexsort((eligible, tie_ranks[sample][eligible], score_b[sample][eligible]))
                take_a, take_b = eligible[ranked_a[:k]], eligible[ranked_b[:k]]
            else:
                take_a, take_b = np.flatnonzero(accepted_a[sample]), np.flatnonzero(accepted_b[sample])
            if len(take_a) and len(take_b):
                differences.append(errors[sample[take_a]].mean() - errors[sample[take_b]].mean())
        actual = errors[accepted_a].mean() - errors[accepted_b].mean() if accepted_a.any() and accepted_b.any() else np.nan
        low, high = np.quantile(differences, [.025, .975]) if differences else (np.nan, np.nan)
        assert len(differences) == row.valid
        assert config['bootstrap'] - len(differences) == row.invalid
        assert np.allclose([actual, low, high], [row.risk_difference, row.ci_low, row.ci_high],
                           atol=1e-12, rtol=0, equal_nan=True)
        checked.append(dict(scenario=row.scenario, comparison=row.comparison,
                            capacity=row.target_acceptance, mode=row.selection_mode,
                            n=n, valid=len(differences), invalid=config['bootstrap']-len(differences),
                            risk_difference=actual, ci_low=low, ci_high=high))
    assert len(checked) == len(intervals) > 0
    return dict(run=root.as_posix(), independent_bootstrap='PASS',
                interval_rows_checked=len(checked), checks=checked,
                scientific_acceptance=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = verify(args.run)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'Independent paired-bootstrap checks passed: {result["interval_rows_checked"]}')
