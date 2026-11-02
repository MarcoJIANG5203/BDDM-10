"""Independent output audit, without importing the experiment's metric code."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath

import numpy as np
import pandas as pd


def sha256(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def relative_path(value):
    path = PurePosixPath(str(value).replace('\\', '/'))
    if path.is_absolute() or '..' in path.parts or ':' in str(path):
        raise ValueError('Expected a relative manifest path: ' + str(value))
    return Path(*path.parts)


def resolve_input(project_root, configured, canonical, expected_sha):
    """Relocate old absolute input references only when exact bytes match."""
    project_root = Path(project_root)
    candidates = []
    if not Path(configured).is_absolute() and not PureWindowsPath(configured).is_absolute():
        candidates.append(project_root / relative_path(configured))
    candidates.append(project_root / relative_path(canonical))
    for candidate in candidates:
        if candidate.is_file() and sha256(candidate) == expected_sha:
            return candidate
    raise ValueError('Input missing or SHA256 mismatch; synchronize the registered bundle: ' + canonical)


def cohort_fallback(config):
    data_role = 'synthetic' if config.get('synthetic') else 'processed'
    extension = PureWindowsPath(config['data_path']).suffix.lower()
    if extension not in ['.csv', '.parquet']:
        raise ValueError('Unsupported cohort format: ' + extension)
    return f'data/{data_role}/cohort{extension}'


def verify(root, project_root=None):
    project_root = Path(project_root or Path(__file__).resolve().parents[1])
    root = Path(root)
    if not root.is_absolute():
        root = project_root / root
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    assert manifest['run_status'] == 'completed'
    for filename, expected in manifest['artifact_hashes'].items():
        assert sha256(root / relative_path(filename)) == expected, filename
    for filename, expected in manifest['source_hashes'].items():
        assert sha256(project_root / relative_path(filename)) == expected, 'Source changed since run: ' + filename
    import yaml
    config = yaml.safe_load((root / 'config.yaml').read_text(encoding='utf-8'))
    assert sha256(root / 'config.yaml') == manifest['config_sha256']
    data_role = 'synthetic' if config.get('synthetic') else 'processed'
    resolve_input(project_root, config['data_path'], cohort_fallback(config), manifest['data_sha256'])
    resolve_input(project_root, config['audit_path'], f'data/{data_role}/cohort_audit.json', manifest['audit_sha256'])
    for seed, expected in manifest['split_sha256'].items():
        canonical = f'data/synthetic/seed_{seed}.json' if config.get('synthetic') else f'splits/seed_{seed}.json'
        resolve_input(project_root, config['split_pattern'].format(seed=seed), canonical, expected)

    predictions = pd.read_csv(root / 'patient_predictions.csv')
    pm = pd.read_csv(root / 'p_m.csv')
    metrics = pd.read_csv(root / 'metrics.csv')
    context = ['split_seed', 'model', 'source_M', 'M', 'alpha', 'scenario',
               'imputation_batch', 'predictor']
    keys = context + ['method', 'target_acceptance', 'selection_mode']
    assert not predictions.duplicated(keys + ['patient_id']).any()
    assert not pm.duplicated(context + ['patient_id', 'draw']).any()
    assert (predictions.loc[predictions.scenario == 'S4', 'site'] == 'B').all()
    assert (predictions.loc[predictions.scenario != 'S4', 'site'] == 'A').all()

    # Compute all reported fractions afresh from the long patient table.
    computed = []
    for values, group in predictions.groupby(keys, dropna=False, sort=False):
        y = group.y_true.to_numpy()
        pred = group.y_pred.to_numpy()
        accept = group.accepted.to_numpy(bool)
        positives = y == 1
        negatives = accept & (pred == 0)
        errors = accept & (pred != y)
        singleton = group.set_0.to_numpy(int) + group.set_1.to_numpy(int) == 1
        assert not (accept & ~singleton).any()
        assert (pred[~singleton] == -1).all()
        ratio = lambda a, b: a / b if b else np.nan
        row = dict(zip(keys, values))
        row.update(n=len(group), positives=int(positives.sum()), accepted=int(accept.sum()),
                   accepted_errors=int(errors.sum()), accepted_negative=int(negatives.sum()),
                   accepted_false_negative=int((negatives & positives).sum()),
                   acceptance=float(accept.mean()),
                   selective_risk=ratio(errors.sum(), accept.sum()),
                   dangerous_miss=ratio((negatives & positives).sum(), positives.sum()),
                   negative_residual=ratio((negatives & positives).sum(), negatives.sum()),
                   coverage=np.where(y == 1, group.set_1, group.set_0).mean(),
                   pool_size=int(singleton.sum()))
        if row['selection_mode'] == 'batch' and row['method'] in ['B2', 'B3', 'B4', 'B5', 'B6']:
            assert row['accepted'] == min(int(np.floor(row['target_acceptance'] * len(group))),
                                          row['pool_size'])
        computed.append(row)
    comparison = metrics.merge(pd.DataFrame(computed), on=keys, validate='one_to_one',
                               suffixes=('_saved', '_independent'))
    assert len(comparison) == len(metrics) == len(computed)
    checked = ['n', 'positives', 'accepted', 'accepted_errors', 'accepted_negative',
               'accepted_false_negative', 'acceptance', 'selective_risk',
               'dangerous_miss', 'negative_residual', 'coverage', 'pool_size']
    for column in checked:
        assert np.allclose(comparison[column + '_saved'], comparison[column + '_independent'],
                           atol=1e-12, rtol=0, equal_nan=True), column

    shared = predictions[predictions.method.isin(['B2', 'B3', 'B4', 'B5', 'B6'])]
    by_patient = shared.groupby(context + ['patient_id'], dropna=False)
    for column in ['p_mean', 'p_std', 'set_0', 'set_1', 'missing_fraction', 'q']:
        assert (by_patient[column].nunique(dropna=False) == 1).all(), column
    by_capacity = shared[shared.selection_mode == 'batch'].groupby(
        context + ['target_acceptance', 'method'], dropna=False).accepted.sum()
    assert (by_capacity.groupby(level=list(range(len(context) + 1))).nunique() == 1).all()

    summary = pm.groupby(context + ['patient_id'], dropna=False).p_m.agg(['mean', 'std', 'size', 'min', 'max']).reset_index()
    summary['std'] = summary['std'].fillna(0)
    assert (summary['size'] == summary.M).all()
    joined = predictions.merge(summary, on=context + ['patient_id'], validate='many_to_one')
    assert len(joined) == len(predictions)
    assert np.allclose(joined.p_mean, joined['mean'], atol=1e-12, rtol=0)
    assert np.allclose(joined.p_std, joined['std'], atol=1e-12, rtol=0)
    assert np.array_equal(joined.flip, (joined['min'] < .5) & (joined['max'] >= .5))
    assert (predictions.loc[predictions.method == 'B0', 'M'] == 1).all()

    q_context = ['split_seed', 'model', 'source_M', 'M', 'alpha', 'scenario', 'method']
    assert (predictions.groupby(q_context, dropna=False).q.nunique() == 1).all()
    return dict(run=str(root), synthetic=manifest['synthetic'],
                run_status=manifest['run_status'], patient_method_rows=len(predictions),
                imputation_probability_rows=len(pm), independently_checked_metric_rows=len(metrics),
                artifact_hashes_checked=len(manifest['artifact_hashes']),
                source_hashes_checked=len(manifest['source_hashes']),
                split_hashes_checked=len(manifest['split_sha256']),
                checks=['all artifact hashes', 'current source/config/data/split hashes',
                        'unique output keys', 'hospital identity',
                        'singleton eligibility', 'independent counts and proportions',
                        'same batch K', 'shared MI predictions and sets',
                        'p_m mean and ddof=1 std and class flips', 'B0 M=1', 'q frozen across batches'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run')
    parser.add_argument('--output')
    args = parser.parse_args()
    result = verify(args.run)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text, encoding='utf-8')
    print(text)
