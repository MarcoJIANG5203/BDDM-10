"""Read-only B receipt audit; never fits models, writes data, or grants C/E approval.

Run with the immutable package exported from A's recorded Git commit. Only a
small aggregate report is written; no patient-level output is added to Git.
"""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import numpy as np
import pandas as pd
import yaml

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from src.data import FEATURES, ROLES, load_cohort

A_COMMIT = 'ec8fd750cc17038bb0a73c37e1537a1e7a4d780e'
A_FOLDER = 'T1_A_Day1_2026-11-03_v1_Rebuilt_Full'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(package):
    audit = json.loads((package / 'data/processed/cohort_audit.json').read_text(encoding='utf-8'))
    package_hashes = {}
    for line in (package / 'PACKAGE_SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        digest, relative = line.split('  ', 1)
        path = (package / relative).resolve()
        require(path.is_relative_to(package.resolve()), 'Checksum path escapes package')
        require(relative not in package_hashes, 'Duplicate checksum path')
        require(sha(path) == digest, f'Original package SHA256 mismatch: {relative}')
        package_hashes[relative] = digest
    for relative, digest in audit['file_sha256'].items():
        require(sha(package / relative) == digest, f'Audit SHA256 mismatch: {relative}')
    require(sha(package / 'scripts/build_a_cohort_v1.py') == audit['code_sha256'], 'A extractor hash')
    working_contract = {}
    for relative, digest in audit['source_contract_sha256'].items():
        require(sha(package / 'sources/protocol_snapshot' / relative) == digest, 'A contract snapshot hash')
        blob = subprocess.check_output(['git', '-C', str(PROJECT), 'show', f'HEAD:{relative}'])
        require(hashlib.sha256(blob).hexdigest() == digest, f'B Git contract differs: {relative}')
        working = (PROJECT / relative).read_bytes()
        # Windows working text may have CRLF. Check the immutable Git blob exactly,
        # then allow only that text conversion in the working contract. Clinical
        # files and package bytes above are always checked without conversion.
        require(working.replace(b'\r\n', b'\n') == blob.replace(b'\r\n', b'\n'),
                f'Working B contract changed beyond line endings: {relative}')
        working_contract[relative] = {'sha256': hashlib.sha256(working).hexdigest(),
                                      'exact_git_bytes': working == blob,
                                      'text_matches_git': True}

    # Use B's current loader, not the preserved loader inside A's package.
    base = yaml.safe_load((PROJECT / 'configs/protocol_v1.yaml').read_text(encoding='utf-8'))
    base['audit_path'] = str(package / 'data/processed/cohort_audit.json')
    base['split_pattern'] = str(package / 'splits/seed_{seed}.json')
    counts, loaded = {}, {}
    for seed in range(2026, 2031):
        for extension in ['parquet', 'csv']:
            base['data_path'] = str(package / f'data/processed/cohort.{extension}')
            frame, splits, _ = load_cohort(base, seed)
            require(list(frame.columns) == ['patient_id', 'site', 'y_true'] + FEATURES, 'Column order')
            loaded[extension] = frame
            summary = {role: {'n': len(ids), 'positive': int(frame.loc[ids].y_true.sum()),
                             'negative': int((frame.loc[ids].y_true == 0).sum())}
                       for role, ids in splits.items()}
            require(summary == audit['split_counts'][str(seed)], 'Split count declarations')
            counts[str(seed)] = summary
        pd.testing.assert_frame_equal(loaded['parquet'], loaded['csv'], check_dtype=False)
    cohort = loaded['parquet']
    record_audit = pd.read_csv(package / 'data/processed/record_audit.csv').set_index('patient_id')
    require(record_audit.index.is_unique, 'Duplicate raw audit IDs')
    raw_manifest = pd.read_csv(package / 'sources/raw_file_manifest.csv')
    raw_manifest['filename'] = raw_manifest.key.map(lambda x: x.rsplit('/', 1)[-1])
    require(not raw_manifest.duplicated(['site', 'filename']).any(), 'Duplicate source manifest records')
    manifest = raw_manifest.set_index(['site', 'filename']).to_dict('index')
    header = FEATURES + ['Unit1', 'Unit2', 'HospAdmTime', 'ICULOS', 'SepsisLabel']
    reasons, sites, seen, included = Counter(), {}, set(), set()
    early_or_first_positive = Counter()
    for site in ['A', 'B']:
        archive = package / f'raw/training_set{site}.zip'
        require(sha(archive) == audit['raw_archive_sha256'][archive.name], 'Raw archive SHA256')
        site_counts = Counter()
        with zipfile.ZipFile(archive) as bundle:
            names = bundle.namelist()
            require(len(names) == len(set(names)), 'Duplicate archive members')
            for name in names:
                patient_id = f'{site}_{Path(name).stem}'
                require(patient_id not in seen, 'Duplicate source patient ID')
                seen.add(patient_id)
                content = bundle.read(name)
                registered = manifest[(site, name)]
                require(len(content) == int(registered['bytes']), 'Source byte count')
                require(hashlib.sha256(content).hexdigest() == registered['sha256'], 'Source SHA256')
                require(hashlib.md5(content).hexdigest() == registered['md5'], 'Source MD5')
                rows = list(csv.reader(io.StringIO(content.decode('utf-8-sig')), delimiter='|'))
                require(rows[0] == header, 'Raw column order')
                values = np.asarray(rows[1:], dtype=float)
                hours, labels = values[:, 39], values[:, 40]
                valid = (values.shape[1] == 41 and not np.isinf(values).any()
                         and np.isfinite(hours).all() and (hours >= 1).all()
                         and (hours == np.floor(hours)).all() and (np.diff(hours) == 1).all()
                         and np.isin(labels, [0, 1]).all() and (np.diff(labels) >= 0).all())
                require(valid, 'Unexpected invalid raw file: investigate instead of repairing')
                positives = np.flatnonzero(labels == 1)
                onset = hours[positives[0]] + 6 if len(positives) and positives[0] > 0 else None
                if labels[0] == 1:
                    early_or_first_positive['first_observation_positive_any_eligibility'] += 1
                if onset is not None and onset <= 12:
                    early_or_first_positive['onset_at_or_before_12_any_eligibility'] += 1
                prior = values[hours <= 12, :36]
                feature_values = np.array([col[~np.isnan(col)][-1] if (~np.isnan(col)).any() else np.nan
                                           for col in prior.T])
                if hours[0] != 1:
                    reason = 'missing_initial_hours'
                elif hours[-1] < 24:
                    reason = 'insufficient_followup'
                elif labels[0] == 1:
                    reason = 'first_observation_positive'
                elif onset is not None and onset <= 12:
                    reason = 'onset_at_or_before_12'
                elif not np.isnan(feature_values[35]) and feature_values[35] not in (0, 1):
                    reason = 'invalid_input_demographics'
                else:
                    reason = 'included'
                declared = record_audit.loc[patient_id]
                require(reason == declared.reason, 'Sequential exclusion differs')
                require(declared.site == site and int(declared.observed_rows) == len(hours), 'Raw audit metadata')
                require(int(declared.first_hour) == hours[0] and int(declared.last_hour) == hours[-1], 'Hour metadata')
                require((pd.isna(declared.onset_proxy) and onset is None) or declared.onset_proxy == onset, 'Onset metadata')
                site_counts['raw'] += 1
                reasons[reason] += 1
                if reason == 'included':
                    included.add(patient_id)
                    patient = cohort.loc[patient_id]
                    target = int(onset is not None and 12 < onset <= 24)
                    require(patient.site == site and patient.y_true == target == declared.y_true, 'Recomputed target')
                    np.testing.assert_allclose(patient[FEATURES].to_numpy(float), feature_values,
                                               rtol=0, atol=0, equal_nan=True)
                    site_counts['included'] += 1
                    site_counts['positive'] += target
            sites[site] = dict(site_counts)
        print(f'B independent raw audit complete: site {site}', flush=True)
    require(seen == set(record_audit.index), 'Raw audit coverage')
    require(seen == {f'{s}_{Path(n).stem}' for s, n in manifest}, 'Source manifest coverage')
    require(included == set(cohort.index), 'Recomputed cohort membership')
    require(len(seen) == audit['exclusion_counts']['input'], 'Raw population')
    for reason in audit['exclusion_order']:
        require(reasons[reason] == audit['exclusion_counts'].get(reason, len(cohort)), 'Exclusion totals')
    for site, summary in sites.items():
        require(all(audit['site_counts'][site][k] == v for k, v in summary.items()), 'Site totals')
    precision = {'site_positive_minimum': 200, 'internal_test_positive_minimum': 50,
                 'site_pass': {s: c['positive'] >= 200 for s, c in sites.items()},
                 'internal_test_pass': {s: c['test']['positive'] >= 50 for s, c in counts.items()}}
    require(all(precision[k] == audit['precision_gates'][k] for k in precision), 'Precision declarations')
    return {'source_repository': 'MarcoJIANG5203/BDDM-10', 'source_commit': A_COMMIT,
            'source_package': A_FOLDER, 'data_version': audit['data_version'], 'protocol': 'v1',
            'verification_scope': 'B receiving audit; no A-owned extractor/validator called',
            'package_files_sha256_verified': len(package_hashes),
            'audit_files_sha256_verified': len(audit['file_sha256']),
            'source_contract_sha256': audit['source_contract_sha256'],
            'B_working_contract': working_contract,
            'current_B_loader_invocations': 10, 'parquet_csv_equivalence': 'PASS',
            'all_raw_sha256_verified': len(seen), 'all_raw_rule_checks': 'PASS',
            'all_included_labels_and_36_features': len(cohort),
            'sequential_exclusion_counts': dict(reasons),
            'overlapping_early_onset_diagnostics': dict(early_or_first_positive),
            'site_counts': sites, 'split_counts': counts, 'precision_gates': precision,
            'A_declared_human_review': audit['human_review'],
            'B_interface_receipt': 'ACCEPTED_FOR_INTEGRATION_ONLY',
            'C_independent_review': 'PENDING', 'E_freeze_decision': 'PENDING',
            'clinical_release': 'NOT_PUBLISHED', 'clinical_experiments_run': False,
            'formal_scientific_acceptance': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, type=Path)
    parser.add_argument('--output', type=Path, default=PROJECT / 'reviews/A_received_2026-11-03.json')
    args = parser.parse_args()
    # Git export should be pinned; directory supplied by caller must be that exact package.
    manifest_blob = subprocess.check_output(['git', '-C', str(PROJECT), 'show',
                                            f'{A_COMMIT}:{A_FOLDER}/PACKAGE_SHA256SUMS.txt'])
    require((args.package / 'PACKAGE_SHA256SUMS.txt').read_bytes() == manifest_blob,
            'Package checksum manifest differs from pinned A commit')
    result = verify(args.package.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'B receipt verified; precision/C/E gates remain open. Report: {args.output}')
