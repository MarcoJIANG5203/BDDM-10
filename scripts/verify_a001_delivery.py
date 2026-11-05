"""Read-only A-001 audit of supplied A full package against a B branch snapshot.

No A extractor is imported. Only B's interface reader is called. No patient-level
output is written; original packages and all labels/splits remain unchanged.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone, timedelta
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import platform
import random
import sys
import zipfile

import numpy as np
import pandas as pd
import yaml

FEATURES = 'HR O2Sat Temp SBP MAP DBP Resp EtCO2 BaseExcess HCO3 FiO2 pH PaCO2 SaO2 AST BUN Alkalinephos Calcium Chloride Creatinine Bilirubin_direct Glucose Lactate Magnesium Phosphate Potassium Bilirubin_total TroponinI Hct Hgb PTT WBC Fibrinogen Platelets Age Gender'.split()
HEADER = FEATURES + ['Unit1', 'Unit2', 'HospAdmTime', 'ICULOS', 'SepsisLabel']
ROLES = ['train', 'selection', 'calibration', 'test', 'external']
REASONS = ['invalid_hourly_records', 'missing_initial_hours', 'insufficient_followup', 'first_observation_positive', 'onset_at_or_before_12', 'invalid_input_demographics', 'included']


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def check(ok, message):
    if not ok:
        raise ValueError(message)


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=True, allow_nan=False) + '\n', encoding='utf-8')


def assess(values):
    """Independent classification; keep left-censored onset unknown."""
    if values.ndim != 2 or values.shape[1] != 41 or len(values) == 0:
        return 'invalid_hourly_records', None, None
    hours, labels = values[:, 39], values[:, 40]
    valid = (not np.isinf(values).any() and np.isfinite(hours).all()
             and (hours >= 1).all() and (hours == np.floor(hours)).all()
             and (np.diff(hours) == 1).all() and np.isin(labels, [0, 1]).all()
             and (np.diff(labels) >= 0).all())
    if not valid:
        return 'invalid_hourly_records', None, None
    first = np.flatnonzero(labels == 1)
    onset = int(hours[first[0]] + 6) if len(first) and first[0] > 0 else None
    if hours[0] != 1:
        return 'missing_initial_hours', onset, None
    if not set(range(1, 25)).issubset(set(hours)):
        return 'insufficient_followup', onset, None
    if labels[0] == 1:
        return 'first_observation_positive', None, None
    if onset is not None and onset <= 12:
        return 'onset_at_or_before_12', onset, None
    past = values[hours <= 12, :36]
    last = np.full(36, np.nan)
    for col in range(36):
        observed = past[:, col][~np.isnan(past[:, col])]
        if len(observed):
            last[col] = observed[-1]
    if not np.isnan(last[35]) and last[35] not in (0, 1):
        return 'invalid_input_demographics', onset, None
    return 'included', onset, last


def audit(package, b_root, output):
    output.mkdir(parents=True, exist_ok=True)
    boundary_results = []
    for name, first, expected_reason, expected_label in [
        ('onset_12_excluded', 6, 'onset_at_or_before_12', None),
        ('onset_13_positive', 7, 'included', 1),
        ('onset_24_positive', 18, 'included', 1),
        ('onset_25_negative', 19, 'included', 0),
        ('never_positive', None, 'included', 0),
        ('left_censored_first_positive', 1, 'first_observation_positive', None),
    ]:
        values = np.full((24, 41), np.nan)
        values[:, 39] = np.arange(1, 25)
        values[:, 40] = 0 if first is None else (values[:, 39] >= first)
        values[:12, 0] = np.arange(1, 13)
        values[12:, 0] = 999
        reason, onset, last = assess(values)
        actual_label = int(onset is not None and 12 < onset <= 24) if reason == 'included' else None
        check(reason == expected_reason and actual_label == expected_label, f'Synthetic endpoint: {name}')
        if reason == 'included':
            check(last[0] == 12 and np.isnan(last[1:]).all(), 'Future leakage or missing-value filling')
        if first == 1:
            check(onset is None, 'Fabricated left-censored onset')
        boundary_results.append({'case': name, 'status': 'PASS', 'expected_reason': expected_reason, 'expected_label': expected_label})
    declared = json.loads((package / 'data/processed/cohort_audit.json').read_text(encoding='utf-8'))
    registered = {}
    for line in (package / 'PACKAGE_SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        digest, name = line.split('  ', 1)
        path = (package / name).resolve()
        check(path.is_relative_to(package.resolve()), 'Unsafe checksum path')
        check(name not in registered and sha(path) == digest, f'Package hash: {name}')
        registered[name] = digest
    for name, digest in declared['file_sha256'].items():
        check(sha(package / name) == digest, f'Current data hash: {name}')
    check(sha(package / 'scripts/build_a_cohort_v1.py') == declared['code_sha256'], 'Extractor hash')
    contracts = {}
    for name, digest in declared['source_contract_sha256'].items():
        a_bytes = (package / 'sources/protocol_snapshot' / name).read_bytes()
        b_bytes = (b_root / name).read_bytes()
        check(hashlib.sha256(a_bytes).hexdigest() == digest, f'A contract hash: {name}')
        check(a_bytes == b_bytes, f'A/B supplied contract bytes differ: {name}')
        contracts[name] = digest

    frame = pd.read_parquet(package / 'data/processed/cohort.parquet')
    text = pd.read_csv(package / 'data/processed/cohort.csv', dtype={'patient_id': str}, float_precision='round_trip')
    check(list(frame.columns) == ['patient_id', 'site', 'y_true'] + FEATURES, 'Feature order')
    pd.testing.assert_frame_equal(frame, text, check_dtype=False, check_exact=True)
    cohort = frame.set_index('patient_id', drop=False)
    check(cohort.index.is_unique, 'Cohort ID uniqueness')
    recorded = pd.read_csv(package / 'data/processed/record_audit.csv', dtype={'patient_id': str}).set_index('patient_id')
    check(recorded.index.is_unique, 'Audit ID uniqueness')
    with (package / 'sources/raw_file_manifest.csv').open(encoding='utf-8', newline='') as stream:
        items = list(csv.DictReader(stream))
    manifest = {(r['site'], r['key'].split('/')[-1]): r for r in items}
    check(len(manifest) == len(items), 'Raw manifest unique keys')
    stages, overlapping, onset_histogram = {}, {}, {}
    seen, included, reasons = set(), set(), Counter()
    numeric_cells = 0
    for site in ['A', 'B']:
        archive = package / f'raw/training_set{site}.zip'
        check(sha(archive) == declared['raw_archive_sha256'][archive.name], 'Raw ZIP SHA256')
        counts = {stage: Counter() for stage in ['raw', 'starts_at_1', 'full_hours_1_to_24', 'included']}
        flow = {reason: Counter() for reason in REASONS}
        overlaps, hist = Counter(), Counter()
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
            check(len(set(names)) == len(names), 'Duplicate ZIP entry')
            for number, name in enumerate(names, 1):
                pid = f'{site}_{Path(name).stem}'
                check(pid not in seen, 'Duplicate raw patient ID')
                seen.add(pid)
                content = z.read(name)
                item = manifest[(site, Path(name).name)]
                check(len(content) == int(item['bytes']), 'Raw byte size')
                check(hashlib.sha256(content).hexdigest() == item['sha256'], 'Raw SHA256')
                check(hashlib.md5(content).hexdigest() == item['md5'], 'Raw MD5')
                lines = list(csv.reader(io.StringIO(content.decode('utf-8-sig')), delimiter='|'))
                check(lines[0] == HEADER and all(len(r) == 41 for r in lines[1:]), 'Raw schema')
                values = np.asarray(lines[1:], dtype=float)
                reason, onset, last = assess(values)
                check(reason != 'invalid_hourly_records', 'Investigate invalid raw record')
                hours, labels = values[:, 39], values[:, 40]
                positive_label = int(bool((labels == 1).any()))
                target = int(onset is not None and 12 < onset <= 24)
                metrics = {'n': 1, 'any_observed_positive_label': positive_label, 'observed_onset_in_12_24': target}
                selected_stages = ['raw']
                if hours[0] == 1:
                    selected_stages.append('starts_at_1')
                    if set(range(1, 25)).issubset(set(hours)):
                        selected_stages.append('full_hours_1_to_24')
                if reason == 'included':
                    selected_stages.append('included')
                for stage in selected_stages:
                    counts[stage].update(metrics)
                flow[reason].update(metrics)
                overlaps['first_record_positive'] += int(labels[0] == 1)
                overlaps['observed_onset_at_or_before_12'] += int(onset is not None and onset <= 12)
                if reason == 'included':
                    category = 'no_observed_positive_label' if onset is None else ('at_or_before_12' if onset <= 12 else ('13_to_24' if onset <= 24 else 'after_24'))
                    hist[category] += 1
                row = recorded.loc[pid]
                check(row.site == site and row.reason == reason, 'Per-record exclusion reason')
                check(int(row.observed_rows) == len(values) and int(row.first_hour) == hours[0] and int(row.last_hour) == hours[-1], 'Hour metadata')
                check((pd.isna(row.onset_proxy) and onset is None) or row.onset_proxy == onset, 'Onset metadata')
                reasons[reason] += 1
                if reason == 'included':
                    included.add(pid)
                    patient = cohort.loc[pid]
                    check(patient.site == site and patient.y_true == target == row.y_true, 'Raw target')
                    np.testing.assert_allclose(patient[FEATURES].to_numpy(float), last, rtol=0, atol=0, equal_nan=True)
                    numeric_cells += 36
                if number % 10000 == 0:
                    print(f'{site}: {number} raw records checked', flush=True)
        stages[site] = {'stages': {k: dict(v) for k, v in counts.items()}, 'sequential_exclusions': {k: dict(v) for k, v in flow.items()}}
        overlapping[site] = dict(overlaps)
        onset_histogram[site] = dict(hist)
        check(counts['raw']['n'] == declared['site_counts'][site]['raw'], 'Raw site count')
        check(counts['included']['n'] == declared['site_counts'][site]['included'], 'Included site count')
        check(counts['included']['observed_onset_in_12_24'] == declared['site_counts'][site]['positive'], 'Site positives')
        print(f'{site}: all {len(names)} checked', flush=True)
    check(seen == set(recorded.index) == {f'{s}_{Path(n).stem}' for s, n in manifest}, 'Raw coverage')
    check(included == set(cohort.index), 'Cohort membership')
    for reason in REASONS:
        check(reasons[reason] == declared['exclusion_counts'].get(reason, len(cohort)), 'Sequential count')

    spec = importlib.util.spec_from_file_location('supplied_B_reader', b_root / 'src/data.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    check(module.FEATURES == FEATURES, 'B input whitelist')
    config = yaml.safe_load((b_root / 'configs/protocol_v1.yaml').read_text(encoding='utf-8'))
    config['audit_path'] = str(package / 'data/processed/cohort_audit.json')
    config['split_pattern'] = str(package / 'splits/seed_{seed}.json')
    split_summary = {}
    for seed in range(2026, 2031):
        splits = json.loads((package / f'splits/seed_{seed}.json').read_text(encoding='utf-8'))
        # Reproduce the declared seed algorithm only for equality checking; never write a new split.
        expected = {r: [] for r in ROLES}
        rng = random.Random(seed)
        for label in [0, 1]:
            ids = sorted(cohort.index[(cohort.site == 'A') & (cohort.y_true == label)])
            rng.shuffle(ids)
            quotas = [len(ids) * fraction for fraction in [0.60, 0.10, 0.15, 0.15]]
            n = [math.floor(v) for v in quotas]
            order = sorted(range(4), key=lambda i: (-(quotas[i] - n[i]), i))
            for i in order[:len(ids) - sum(n)]:
                n[i] += 1
            boundaries = np.cumsum([0] + n)
            for i, role in enumerate(ROLES[:4]):
                expected[role].extend(ids[boundaries[i]:boundaries[i+1]])
        expected['external'] = list(cohort.index[cohort.site == 'B'])
        expected = {role: sorted(ids) for role, ids in expected.items()}
        check(splits == expected, 'Declared fixed split algorithm differs')
        summary = {r: {'n': len(ids), 'positive': int(cohort.loc[ids].y_true.sum()), 'negative': int((cohort.loc[ids].y_true == 0).sum())} for r, ids in splits.items()}
        check(summary == declared['split_counts'][str(seed)], 'Declared split count')
        split_summary[str(seed)] = summary
        for extension in ['csv', 'parquet']:
            config['data_path'] = str(package / f'data/processed/cohort.{extension}')
            loaded, actual_splits, _ = module.load_cohort(config, seed)
            check(actual_splits == splits and len(loaded) == len(cohort), 'B loader')
    cases = pd.read_csv(package / 'data/processed/review_10_positive_10_negative.csv')
    check(len(cases) == 20 and cases.y_true.value_counts().to_dict() == {0: 10, 1: 10}, 'Review case balance')
    for row in cases.to_dict('records'):
        content = (package / row['raw_evidence']).read_bytes()
        with zipfile.ZipFile(package / f"raw/training_set{row['site']}.zip") as z:
            check(content == z.read(row['source_filename']), 'Review source byte equality')
        values = np.asarray(list(csv.reader(io.StringIO(content.decode('utf-8-sig')), delimiter='|'))[1:], dtype=float)
        reason, onset, last = assess(values)
        check(reason == 'included' and int(onset is not None and 12 < onset <= 24) == row['y_true'], 'Review target')
        np.testing.assert_allclose(cohort.loc[row['patient_id'], FEATURES].to_numpy(float), last, rtol=0, atol=0, equal_nan=True)

    b_manifest = json.loads((b_root / 'reports/candidate-trials/20261103T122334_93a9a266/manifest.json').read_text(encoding='utf-8'))
    check(b_manifest['data_version'] == declared['data_version'], 'B trial data version')
    check(b_manifest['data_sha256'] == sha(package / 'data/processed/cohort.parquet'), 'B trial input hash')
    check(b_manifest['audit_sha256'] == sha(package / 'data/processed/cohort_audit.json'), 'B trial audit hash')
    for seed, digest in b_manifest['split_sha256'].items():
        check(digest == sha(package / f'splits/seed_{seed}.json'), 'B trial split hash')
    for name, digest in b_manifest['source_hashes'].items():
        check(sha(b_root / name.replace('\\', '/')) == digest, 'B trial source hash')
    b_summary_files = 0
    for name, digest in b_manifest['artifact_hashes'].items():
        path = b_root / 'reports/candidate-trials/20261103T122334_93a9a266' / name.replace('\\', '/')
        if path.is_file():
            check(sha(path) == digest, 'B summary artifact hash')
            b_summary_files += 1
    b_received = json.loads((b_root / 'reviews/A_received_2026-11-03.json').read_text(encoding='utf-8'))
    check(b_received['split_counts'] == split_summary, 'B receipt split counts')
    check(b_received['all_raw_sha256_verified'] == len(seen), 'B receipt raw count')

    report = {'date_beijing': datetime.now(timezone(timedelta(hours=8))).isoformat(),
              'scope': 'A-001 automated technical verification; not independent human C review, clinical adjudication, or E freeze',
              'data_version': declared['data_version'], 'protocol_version': declared['protocol_version'],
              'verification_status': 'VERIFIED_WITHIN_DECLARED_TECHNICAL_SCOPE',
              'package_manifest_sha256': sha(package / 'PACKAGE_SHA256SUMS.txt'),
              'package_files_sha256_verified': len(registered), 'current_audit_files_verified': len(declared['file_sha256']),
              'all_raw_records_sha256_md5_and_rules_verified': len(seen), 'included_labels_verified': len(included),
              'included_feature_cells_exactly_checked': numeric_cells, 'parquet_csv_exact_equivalence': True,
              'B_loader_calls': 10, 'fixed_split_algorithms_exactly_matched': 5,
              'raw_review_cases_checked': 20, 'source_contracts_exact_A_B_bytes': contracts,
              'independent_endpoint_and_feature_boundary_checks': boundary_results,
              'B_trial_manifest_exact_A_input_hashes': True,
              'B_trial_scientific_source_files_matched': len(b_manifest['source_hashes']),
              'B_trial_available_summary_files_matched': b_summary_files,
              'sequential_counts': dict(reasons), 'site_flow': stages,
              'overlapping_exclusion_diagnostics_not_additive': overlapping,
              'included_onset_categories': onset_histogram, 'split_counts': split_summary,
              'precision_gates': declared['precision_gates'],
              'raw_source_integrity_scope': 'Compared with supplied acquisition manifest; no new live 40336-file re-download',
              'B_metrics_scope': 'B supplied reports inspected; original clinical run Release not supplied, no patient-level B metric replay in this audit',
              'A_personal_attestation': 'PENDING_USER_REVIEW', 'C_independent_review': 'PENDING',
              'E_precision_and_freeze_decision': 'PENDING', 'formal_data_release': 'NOT_PUBLISHED_BY_THIS_RUN',
              'source_archives_modified': False, 'labels_or_splits_modified': False, 'new_models_trained': False,
              'audit_script_sha256': sha(__file__), 'python': platform.python_version(),
              'packages': {'numpy': np.__version__, 'pandas': pd.__version__}}
    dump(output / 'A_001_verification_2026-11-03.json', report)
    flow_rows = []
    for site, data in stages.items():
        for stage, stats in data['stages'].items():
            flow_rows.append({'site': site, 'stage': stage, **stats})
    with (output / 'A_001_population_flow_2026-11-03.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['site', 'stage', 'n', 'any_observed_positive_label', 'observed_onset_in_12_24'])
        writer.writeheader()
        writer.writerows(flow_rows)
    print(json.dumps({k: report[k] for k in ['verification_status', 'all_raw_records_sha256_md5_and_rules_verified', 'included_labels_verified', 'included_feature_cells_exactly_checked', 'B_loader_calls', 'sequential_counts', 'included_onset_categories']}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--a-package', required=True, type=Path)
    parser.add_argument('--b-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    audit(args.a_package.resolve(), args.b_root.resolve(), args.output.resolve())
