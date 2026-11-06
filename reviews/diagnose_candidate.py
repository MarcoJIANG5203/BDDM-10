"""Post hoc descriptive diagnosis of an immutable candidate run; never fits models.

Replays only train/selection/calibration predictions from the saved model.
Test predictions are read from existing outputs; no threshold, label, split or
model is selected using this analysis. Outputs contain aggregate counts only.
"""
import argparse
from itertools import combinations
import json
import math
from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
import yaml

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from src.data import FEATURES, load_cohort
from reviews.verify_b_artifacts import relative_path, sha256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def probability_rows(role, predictor, probabilities, labels, deviations):
    rows = []
    for label in [0, 1]:
        take = labels == label
        values = probabilities[take]
        require(len(values) > 0, 'Diagnostic class group is empty')
        quantiles = np.quantile(values, [0, .25, .5, .75, 1])
        rows.append(dict(role=role, predictor=predictor, y_true=label, n=int(take.sum()),
                         p_min=quantiles[0], p_q25=quantiles[1], p_median=quantiles[2],
                         p_q75=quantiles[3], p_max=quantiles[4], p_mean=values.mean(),
                         mean_disagreement=deviations[take].mean(),
                         point_positive_at_half=int((values >= .5).sum())))
    return rows


def correlation(a, b):
    if np.unique(a).size < 2 or np.unique(b).size < 2:
        return None
    return float(spearmanr(a, b).statistic)


def diagnose(root, output):
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    cfg = yaml.safe_load((root / 'config.yaml').read_text(encoding='utf-8'))
    require(manifest['run_status'] == 'completed' and not manifest['synthetic'], 'Expected completed real candidate')
    require(cfg['seeds'] == [2026] and cfg['scenarios'] == ['S0', 'S4'], 'This diagnostic is scoped to the recorded trial')
    require(not output.resolve().is_relative_to(root.resolve()), 'Diagnostics must be outside the immutable run')
    frozen = {root / relative_path(name): digest for name, digest in manifest['artifact_hashes'].items()}
    frozen.update({PROJECT / relative_path(name): digest for name, digest in manifest['source_hashes'].items()})
    frozen[root / 'config.yaml'] = manifest['config_sha256']
    frozen[PROJECT / cfg['data_path']] = manifest['data_sha256']
    frozen[PROJECT / cfg['audit_path']] = manifest['audit_sha256']
    for seed, digest in manifest['split_sha256'].items():
        frozen[PROJECT / cfg['split_pattern'].format(seed=seed)] = digest
    manifest_hash = sha256(root / 'manifest.json')
    for path, digest in frozen.items():
        require(sha256(path) == digest, f'Frozen bytes differ: {path.name}')
    local_cfg = dict(cfg, data_path=str(PROJECT / cfg['data_path']),
                     audit_path=str(PROJECT / cfg['audit_path']),
                     split_pattern=str(PROJECT / cfg['split_pattern']))
    frame, splits, _ = load_cohort(local_cfg, 2026)
    saved = joblib.load(root / 'models/seed2026_LR_M10_alpha0.1.joblib')
    probability, calibration, role_counts = [], [], []
    for role in ['train', 'selection', 'calibration']:
        part = frame.loc[splits[role]]
        labels = part.y_true.to_numpy(int)
        role_counts.append(dict(role=role, n=len(part), positive=int(labels.sum()), base_rate=float(labels.mean())))
        for predictor, m, posterior, model, threshold in [
                ('MI', cfg['M'], True, saved['model'], saved['q']),
                ('median', 1, False, saved['median_model'], saved['q0'])]:
            # Uses a saved fitted imputer and classifier; no .fit call is made.
            draws, _, _ = saved['imputer'].transform(part[FEATURES], splits[role], M=m,
                                                  role=role, batch=0, posterior=posterior)
            probabilities = model.predict_proba(draws.reshape(-1, draws.shape[-1]))[:, 1].reshape(m, len(part))
            mean = probabilities.mean(axis=0)
            std = probabilities.std(axis=0, ddof=1) if m > 1 else np.zeros(len(part))
            probability.extend(probability_rows(role, predictor, mean, labels, std))
            if role == 'selection' and predictor == 'MI':
                selection_errors = int(((mean >= .5) != labels).sum())
                params = json.loads((root / 'model_parameters.json').read_text(encoding='utf-8'))[0]
                require(selection_errors == params['selection_errors'], 'Selection error replay')
            if role == 'calibration':
                scores = np.where(labels == 1, 1 - mean, mean)
                k = math.ceil((len(labels) + 1) * (1 - cfg['alpha']))
                q = float(np.sort(scores)[k - 1])
                require(np.isclose(q, threshold, rtol=0, atol=1e-12), 'Calibration threshold replay')
                calibration.append(dict(predictor=predictor, n=len(labels), positive=int(labels.sum()),
                                        k=k, q_saved=threshold, q_independent=q,
                                        q_replay_absolute_difference=abs(q-threshold),
                                        positive_set_requires_p_at_least=1-threshold,
                                        positive_score_min=float(scores[labels == 1].min()),
                                        positive_score_max=float(scores[labels == 1].max()),
                                        covered_positive=int((scores[labels == 1] <= threshold).sum()),
                                        covered_negative=int((scores[labels == 0] <= threshold).sum()),
                                        covered_total=int((scores <= threshold).sum())))
        print(f'Replayed saved {role} predictions without fitting', flush=True)

    pred = pd.read_csv(root / 'patient_predictions.csv', float_precision='round_trip')
    unique = pred[(pred.method == 'B1') & (pred.predictor == 'MI')].copy()
    set_rows, score_rows = [], []
    for (scene, batch), group in unique.groupby(['scenario', 'imputation_batch'], sort=True):
        p = group.p_mean.to_numpy()
        q = group.q.to_numpy()
        require(np.all(q == saved['q']), 'MI threshold is not frozen')
        zero, one = p <= q, 1-p <= q
        require(np.array_equal(zero, group.set_0) and np.array_equal(one, group.set_1), 'Saved sets differ from defining inequalities')
        y = group.y_true.to_numpy(int)
        if batch == 0:
            probability.extend(probability_rows(scene, 'MI', p, y, group.p_std.to_numpy()))
            role_counts.append(dict(role=scene, n=len(y), positive=int(y.sum()), base_rate=float(y.mean())))
        for label in [0, 1]:
            take = y == label
            set_rows.append(dict(scenario=scene, batch=int(batch), y_true=label, n=int(take.sum()),
                                 empty=int((take & ~zero & ~one).sum()),
                                 negative_singleton=int((take & zero & ~one).sum()),
                                 positive_singleton=int((take & ~zero & one).sum()),
                                 doubleton=int((take & zero & one).sum()),
                                 true_label_covered=int((take & (one if label else zero)).sum()),
                                 p_max=float(p[take].max()), point_positive_at_half=int((p[take] >= .5).sum())))
        errors = (p >= .5) != y
        d = group.p_std.to_numpy()
        u = np.minimum(p, 1-p)
        score_rows.append(dict(scenario=scene, batch=int(batch), n=len(y), errors=int(errors.sum()),
                               D_vs_confidence_spearman=correlation(d, u),
                               D_vs_missing_spearman=correlation(d, group.missing_fraction.to_numpy()),
                               D_error_detection_auroc=float(roc_auc_score(errors, d)),
                               confidence_error_detection_auroc=float(roc_auc_score(errors, u)),
                               interpretation='post_hoc_descriptive_not_model_selection'))

    comparisons = []
    subset = pred[pred.method.isin(['B2', 'B4'])]
    for (scene, batch, capacity, mode), g in subset.groupby(['scenario', 'imputation_batch', 'target_acceptance', 'selection_mode']):
        a = g[g.method == 'B2'].set_index('patient_id')
        b = g[g.method == 'B4'].set_index('patient_id').loc[a.index]
        require(np.array_equal(a.y_pred, b.y_pred) and np.array_equal(a.y_true, b.y_true), 'Shared predictor differs')
        aa, bb = a.accepted.to_numpy(bool), b.accepted.to_numpy(bool)
        y = a.y_true.to_numpy(int)
        err = a.y_pred.to_numpy() != y
        if mode == 'batch':
            require(aa.sum() == bb.sum(), 'Paired capacity mismatch')
        comparisons.append(dict(scenario=scene, batch=int(batch), capacity=capacity, mode=mode,
                                B2_accepted=int(aa.sum()), B4_accepted=int(bb.sum()),
                                accepted_by_both=int((aa & bb).sum()),
                                B2_only=int((aa & ~bb).sum()), B4_only=int((bb & ~aa).sum()),
                                positive_both=int((aa & bb & (y == 1)).sum()),
                                positive_B2_only=int((aa & ~bb & (y == 1)).sum()),
                                positive_B4_only=int((bb & ~aa & (y == 1)).sum()),
                                B2_errors=int((aa & err).sum()), B4_errors=int((bb & err).sum()),
                                risk_difference=float(err[bb].mean()-err[aa].mean()) if aa.any() and bb.any() else np.nan))

    stability = []
    recorded = pd.read_csv(root / 'stability.csv', float_precision='round_trip')
    for (method, capacity, mode), g in pred[(pred.scenario == 'S0') & pred.method.isin(['B2', 'B3', 'B4'])].groupby(['method', 'target_acceptance', 'selection_mode']):
        g = g.copy()
        g['state'] = np.where(g.accepted, g.y_pred, -1)
        pivot = g.pivot(index='patient_id', columns='imputation_batch', values='state')
        require(pivot.shape == (len(splits['test']), 5) and not pivot.isna().any().any(), 'Five-batch alignment')
        values = pivot.to_numpy()
        disagreements = [float((values[:, i] != values[:, j]).mean()) for i, j in combinations(range(5), 2)]
        old = recorded[(recorded.method == method) & (recorded.target_acceptance == capacity) & (recorded.selection_mode == mode)]
        require(len(old) == 10 and np.allclose(np.sort(disagreements), np.sort(old.disagreement), rtol=0, atol=1e-12), 'Saved stability replay')
        positive = frame.loc[pivot.index].y_true.to_numpy() == 1
        switched = np.any(values != values[:, [0]], axis=1)
        stability.append(dict(method=method, capacity=capacity, mode=mode, patients=len(values),
                              mean_pair_disagreement=float(np.mean(disagreements)),
                              max_pair_disagreement=float(np.max(disagreements)),
                              any_batch_state_switch=int(switched.sum()),
                              positive_patients=int(positive.sum()),
                              positive_any_batch_state_switch=int((switched & positive).sum())))

    clips = []
    for entry in json.loads((root / 'clipping.json').read_text(encoding='utf-8')):
        if entry['M'] != cfg['M']:
            continue
        for feature, counts in entry['columns'].items():
            clips.append(dict(role=entry['role'], feature=feature,
                              missing_fills=counts['missing_fills'], clipped=counts['clipped']))
    clips = pd.DataFrame(clips).groupby(['role', 'feature'], as_index=False)[['missing_fills', 'clipped']].sum()
    clips['clip_fraction'] = clips.clipped.div(clips.missing_fills.where(clips.missing_fills > 0))

    # Ensure replay/analysis has not mutated any original evidence.
    for path, digest in frozen.items():
        require(sha256(path) == digest, f'Original bytes changed during diagnosis: {path.name}')
    require(sha256(root / 'manifest.json') == manifest_hash, 'Original manifest changed')
    output.mkdir(parents=True, exist_ok=True)
    for name, rows in [('probabilities_by_role_class', probability), ('role_counts', role_counts),
                       ('set_allocation', set_rows), ('error_score_diagnostics', score_rows),
                       ('paired_acceptance', comparisons), ('five_batch_stability', stability)]:
        pd.DataFrame(rows).to_csv(output / f'{name}.csv', index=False)
    clips.to_csv(output / 'clipping_by_role.csv', index=False)
    summary = dict(run=root.relative_to(PROJECT).as_posix(), source_manifest_sha256=manifest_hash,
                   diagnostic_script_sha256=sha256(Path(__file__)), scope='post_hoc_descriptive_frozen_model_replay',
                   model_refit=False, labels_splits_or_protocol_changed=False, scientific_acceptance=False,
                   frozen_file_checks_before_and_after=len(frozen), calibration=calibration,
                   selection_errors=selection_errors, selection_correct=len(splits['selection'])-selection_errors,
                   risk_model_minimum_errors=20, S0_batches=5, test_prediction_replay='existing_test_outputs_only',
                   hypothesis_limit='Numerical mechanism verified; underlying clinical validity and causes of poor discrimination require A/C/E review.')
    (output / 'diagnostics.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=Path('results/candidate-clinical/20261103T122334_93a9a266'))
    parser.add_argument('--output', type=Path, default=Path('reports/diagnostics/20261103T122334_93a9a266'))
    args = parser.parse_args()
    diagnose((PROJECT / args.run).resolve(), (PROJECT / args.output).resolve())
