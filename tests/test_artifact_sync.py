"""Team artifact transfer must preserve bytes and respect versioned paths."""
import importlib.util
import zipfile

import pytest


def sync_module():
    spec = importlib.util.find_spec('scripts.sync_artifacts')
    assert spec is not None, 'Versioned artifact synchronization is not implemented'
    return __import__('scripts.sync_artifacts', fromlist=['create_bundle'])


def test_bundle_roundtrip_and_hash_mismatch(tmp_path):
    sync = sync_module()
    source = tmp_path / 'source'
    (source / 'data/processed').mkdir(parents=True)
    payload = b'patient_id,value\r\nA1,3\r\n'
    (source / 'data/processed/cohort.csv').write_bytes(payload)
    archive = tmp_path / 'cohort.zip'
    metadata = sync.create_bundle(source, ['data/processed'], archive)
    assert metadata['files'] == 1
    target = tmp_path / 'target'
    with pytest.raises(ValueError, match='SHA256'):
        sync.extract_bundle(archive, target, metadata['roots'], '0' * 64)
    assert not target.exists()
    sync.extract_bundle(archive, target, metadata['roots'], metadata['sha256'])
    assert (target / 'data/processed/cohort.csv').read_bytes() == payload
    sync.extract_bundle(archive, target, metadata['roots'], metadata['sha256'])
    (target / 'data/processed/cohort.csv').write_bytes(b'local version')
    with pytest.raises(FileExistsError):
        sync.extract_bundle(archive, target, metadata['roots'], metadata['sha256'])
    sync.extract_bundle(archive, target, metadata['roots'], metadata['sha256'], replace=True)
    assert (target / 'data/processed/cohort.csv').read_bytes() == payload


@pytest.mark.parametrize('name', ['../outside.txt', 'data/processed/../../outside.txt',
                                  'C:/outside.txt', 'src/overwrite.py'])
def test_archive_rejects_escape_or_unlisted_roots_before_writing(tmp_path, name):
    sync = sync_module()
    archive = tmp_path / 'bad.zip'
    with zipfile.ZipFile(archive, 'w') as bundle:
        bundle.writestr('data/processed/valid.csv', 'valid')
        bundle.writestr(name, 'outside')
    target = tmp_path / 'target'
    with pytest.raises(ValueError):
        sync.extract_bundle(archive, target, ['data/processed'], sync.sha256(archive))
    assert not target.exists()


def test_pack_rejects_missing_or_external_input(tmp_path):
    sync = sync_module()
    with pytest.raises(ValueError):
        sync.create_bundle(tmp_path, ['../outside'], tmp_path / 'bad.zip')
    with pytest.raises(FileNotFoundError):
        sync.create_bundle(tmp_path, ['data/missing'], tmp_path / 'bad.zip')


def test_historical_windows_paths_resolve_in_a_new_clone(tmp_path):
    from reviews import verify_b_artifacts as audit
    assert hasattr(audit, 'resolve_input'), 'Historical absolute paths are not portable yet'
    path = tmp_path / 'data/synthetic/cohort.csv'
    path.parent.mkdir(parents=True)
    path.write_bytes(b'unchanged input bytes\r\n')
    digest = audit.sha256(path)
    assert audit.resolve_input(tmp_path, r'Z:\old-machine\EI\data\synthetic\cohort.csv',
                               'data/synthetic/cohort.csv', digest) == path
    assert audit.relative_path(r'models\seed2026.joblib').as_posix() == 'models/seed2026.joblib'
    path.write_bytes(b'wrong data')
    with pytest.raises(ValueError, match='SHA256'):
        audit.resolve_input(tmp_path, r'Z:\old-machine\cohort.csv', 'data/synthetic/cohort.csv', digest)


@pytest.mark.parametrize('second', ['data/processed/COHORT.csv', 'data/processed/cohort.csv.',
                                   'data/processed/cohort.csv '])
def test_windows_path_aliases_rejected_before_writing(tmp_path, second):
    sync = sync_module()
    archive = tmp_path / 'aliases.zip'
    with zipfile.ZipFile(archive, 'w') as bundle:
        bundle.writestr('data/processed/cohort.csv', 'FIRST')
        bundle.writestr(second, 'SECOND')
    target = tmp_path / 'target'
    with pytest.raises(ValueError):
        sync.extract_bundle(archive, target, ['data/processed'], sync.sha256(archive))
    assert not target.exists()


@pytest.mark.parametrize('linked_root', [True, False])
def test_existing_directory_link_cannot_redirect_a_delivery(tmp_path, linked_root):
    import os
    import subprocess
    sync = sync_module()
    root = tmp_path / 'project'
    destination = root / 'src'
    destination.mkdir(parents=True)
    link = root / 'data/processed' if linked_root else root / 'data/processed/nested'
    link.parent.mkdir(parents=True, exist_ok=True)
    if os.name == 'nt':
        subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(destination)],
                       capture_output=True, check=True)
    else:
        link.symlink_to(destination, target_is_directory=True)
    archive = tmp_path / 'link.zip'
    with zipfile.ZipFile(archive, 'w') as bundle:
        bundle.writestr('data/processed/valid.csv', 'GOOD')
        bundle.writestr('data/processed/escaped.csv' if linked_root else
                        'data/processed/nested/escaped.csv', 'BAD')
    with pytest.raises(ValueError):
        sync.extract_bundle(archive, root, ['data/processed'], sync.sha256(archive), replace=True)
    assert not (destination / 'escaped.csv').exists()
    assert not (root / 'data/processed/valid.csv').exists()


def test_clinical_csv_fallback_preserves_supported_format():
    from reviews import verify_b_artifacts as audit
    assert hasattr(audit, 'cohort_fallback'), 'Clinical CSV fallback is not implemented'
    assert audit.cohort_fallback({'synthetic': False, 'data_path': r'Z:\old\cohort.csv'}) == 'data/processed/cohort.csv'
    assert audit.cohort_fallback({'synthetic': False, 'data_path': r'Z:\old\cohort.parquet'}) == 'data/processed/cohort.parquet'
