"""Generate EXP-02 model diagnostics from a completed protocol-v1 run."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.metrics import average_precision_score, roc_auc_score

CONTEXT = ['split_seed', 'model', 'source_M', 'alpha', 'scenario', 'imputation_batch']
BINS = np.array([0, .005, .01, .025, .05, .1, .5, 1])
METRICS = ['prevalence', 'auroc', 'auprc', 'brier']


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def scores(y, p):
    positives = int(y.sum())
    return np.array([
        y.mean(),
        roc_auc_score(y, p) if 0 < positives < len(y) else np.nan,
        average_precision_score(y, p) if positives else np.nan,
        np.mean((y - p) ** 2),
    ])


def score_intervals(y, p, seed, repetitions):
    rng = np.random.default_rng(seed)
    draws = np.empty((repetitions, len(METRICS)))
    for i in range(repetitions):
        indices = rng.integers(0, len(y), len(y))
        draws[i] = scores(y[indices], p[indices])
    for metric, point, samples in zip(METRICS, scores(y, p), draws.T):
        valid = samples[np.isfinite(samples)]
        low, high = np.quantile(valid, [.025, .975]) if len(valid) else (np.nan, np.nan)
        yield dict(metric=metric, estimate=point, ci_low=low, ci_high=high,
                   bootstrap_valid=len(valid), bootstrap_invalid=repetitions - len(valid))


def wilson(positives, n):
    if not n:
        return np.nan, np.nan
    z = norm.ppf(.975)
    rate = positives / n
    denominator = 1 + z ** 2 / n
    midpoint = (rate + z ** 2 / (2 * n)) / denominator
    half_width = z * np.sqrt(rate * (1 - rate) / n + z ** 2 / (4 * n ** 2)) / denominator
    return max(0., midpoint - half_width), min(1., midpoint + half_width)


def summarize(run, output):
    manifest_file = run / 'manifest.json'
    manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
    if manifest['run_status'] != 'completed':
        raise ValueError('Run must have completed before analysis')
    predictions = run / 'patient_predictions.csv'
    if sha256(predictions) != manifest['artifact_hashes'][predictions.name]:
        raise ValueError('Patient predictions do not match the run manifest')

    columns = CONTEXT + ['patient_id', 'site', 'method', 'predictor', 'y_true', 'p_mean']
    data = pd.read_csv(predictions, usecols=columns)
    data = data.loc[(data.method == 'B1') & (data.predictor == 'MI')]
    if data.empty or data.duplicated(CONTEXT + ['patient_id']).any():
        raise ValueError('Expected exactly one MI prediction per evaluation patient and context')
    if not data.y_true.isin([0, 1]).all() or not data.p_mean.between(0, 1).all():
        raise ValueError('Invalid binary labels or probabilities')

    repetitions = 1000
    performance, calibration, distributions = [], [], []
    for values, group in data.groupby(CONTEXT):
        tags = dict(zip(CONTEXT, values))
        group = group.sort_values('patient_id')
        y = group.y_true.to_numpy()
        p = group.p_mean.to_numpy()
        site = 'B' if tags['scenario'] == 'S4' else 'A'
        if not group.site.eq(site).all():
            raise ValueError('Unexpected hospital in evaluation data')
        tags.update(site=site)
        seed = int(tags['split_seed'])
        performance.extend(dict(**tags, n=len(y), positives=int(y.sum()),
                                mean_probability=p.mean(), **score)
                           for score in score_intervals(y, p, seed, repetitions))
        bin_ids = np.searchsorted(BINS[1:-1], p, side='right')
        for index, (lower, upper) in enumerate(zip(BINS, BINS[1:])):
            in_bin = bin_ids == index
            n = int(in_bin.sum())
            positives = int(y[in_bin].sum())
            low, high = wilson(positives, n)
            calibration.append(dict(**tags, lower=lower, upper=upper, n=n, positives=positives,
                                    sparse=min(positives, n - positives) < 5,
                                    mean_probability=p[in_bin].mean() if n else np.nan,
                                    observed_rate=positives / n if n else np.nan,
                                    observed_ci_low=low, observed_ci_high=high))
        for label in (0, 1):
            probabilities = p[y == label]
            quantiles = np.quantile(probabilities, [0, .25, .5, .75, 1]) if len(probabilities) else [np.nan] * 5
            distributions.append(dict(**tags, label=label, n=len(probabilities),
                                      **dict(zip(['min', 'q25', 'median', 'q75', 'max'], quantiles))))

    output.mkdir(parents=True, exist_ok=False)
    outputs = {}
    for name, rows in [('model_diagnostics.csv', performance), ('calibration_bins.csv', calibration),
                       ('probability_by_class.csv', distributions)]:
        target = output / name
        pd.DataFrame(rows).to_csv(target, index=False, na_rep='NA', lineterminator='\n')
        outputs[name] = sha256(target)
    receipt = dict(run_id=manifest['run_id'], run_manifest_sha256=sha256(manifest_file),
                   patient_predictions_sha256=sha256(predictions),
                   diagnostic_source_sha256=sha256(Path(__file__)),
                   bootstrap_seed='split_seed, common sorted patient order within scenario',
                   bootstrap_repetitions=repetitions, output_sha256=outputs)
    (output / 'diagnostic_provenance.json').write_text(
        json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    summarize(args.run, args.output)
