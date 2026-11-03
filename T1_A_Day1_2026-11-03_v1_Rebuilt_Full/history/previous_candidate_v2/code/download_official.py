"""Download public training files from the official PhysioNet Open S3 bucket.

The versioned PhysioNet landing page explicitly documents this bucket.
No credentials, patient uploads, third-party dataset mirrors, or package installs.
"""
import concurrent.futures as cf
import csv
import hashlib
import json
from pathlib import Path
import threading
import time
import xml.etree.ElementTree as ET
import zipfile
import requests

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://physionet-open.s3.amazonaws.com/'
PREFIX = 'challenge-2019/1.0.0/'
NS = {'s': 'http://s3.amazonaws.com/doc/2006-03-01/'}
LOCAL = threading.local()

def session():
    if not hasattr(LOCAL, 'session'):
        LOCAL.session = requests.Session()
    return LOCAL.session

def inventory(site):
    params = {'list-type': '2', 'prefix': PREFIX + f'training/training_set{site}/', 'max-keys': 1000}
    rows = []
    while True:
        r = session().get(BASE, params=params, timeout=(15, 90))
        r.raise_for_status()
        doc = ET.fromstring(r.content)
        for obj in doc.findall('s:Contents', NS):
            key = obj.findtext('s:Key', namespaces=NS)
            if key.endswith('.psv'):
                rows.append({'site': site, 'key': key,
                             'bytes': int(obj.findtext('s:Size', namespaces=NS)),
                             'etag': obj.findtext('s:ETag', namespaces=NS).strip('"')})
        if doc.findtext('s:IsTruncated', namespaces=NS) == 'false':
            return rows
        params['continuation-token'] = doc.findtext('s:NextContinuationToken', namespaces=NS)

def fetch(obj):
    r = session().get(BASE + obj['key'], timeout=(15, 90))
    r.raise_for_status()
    b = r.content
    md5 = hashlib.md5(b).hexdigest()
    if len(b) != obj['bytes'] or md5 != obj['etag']:
        raise ValueError('Size or single-part ETag/MD5 mismatch: ' + obj['key'])
    result = dict(obj, md5=md5, sha256=hashlib.sha256(b).hexdigest(),
                  url=BASE + obj['key'], etag_md5_verified=True)
    return result, b

def main():
    start = time.monotonic()
    inv = []
    with cf.ThreadPoolExecutor(max_workers=2) as pool:
        for rows in pool.map(inventory, ['A', 'B']):
            inv.extend(rows)
    inv.sort(key=lambda x: x['key'])
    expected = {'A': 20336, 'B': 20000}
    for site, n in expected.items():
        assert sum(x['site'] == site for x in inv) == n, site
    (ROOT / 'sources' / 's3_inventory.json').write_text(json.dumps(inv, indent=2), encoding='utf-8')
    print(f'Official inventory: {len(inv)} records', flush=True)
    manifests, failures = [], []
    for site in ['A', 'B']:
        archive = ROOT / 'raw' / f'training_set{site}.zip'
        with zipfile.ZipFile(archive, 'a', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            existing = set(z.namelist())
            pending = []
            for obj in [o for o in inv if o['site'] == site]:
                name = Path(obj['key']).name
                if name in existing:
                    b = z.read(name)
                    md5 = hashlib.md5(b).hexdigest()
                    assert len(b) == obj['bytes'] and md5 == obj['etag'], name
                    manifests.append(dict(obj, md5=md5, sha256=hashlib.sha256(b).hexdigest(),
                                          url=BASE+obj['key'], etag_md5_verified=True))
                else:
                    pending.append(obj)
            with cf.ThreadPoolExecutor(max_workers=32) as pool:
                tasks = {pool.submit(fetch, o): o for o in pending}
                for i, future in enumerate(cf.as_completed(tasks), 1):
                    try:
                        result, b = future.result()
                        z.writestr(Path(result['key']).name, b)
                        manifests.append(result)
                    except Exception as e:
                        failures.append({'key': tasks[future]['key'], 'error': str(e)})
                    if i % 1000 == 0 or i == len(tasks):
                        print(f'{site}: {i}/{len(tasks)} new files; failures={len(failures)}; elapsed={time.monotonic()-start:.0f}s', flush=True)
    manifests.sort(key=lambda x:x['key'])
    with (ROOT/'sources'/'raw_file_manifest.csv').open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(manifests[0])); w.writeheader(); w.writerows(manifests)
    (ROOT/'sources'/'download_status.json').write_text(json.dumps({
        'source':'Official PhysioNet Open S3, as linked by PhysioNet',
        'retrieval_date_hong_kong':'2026-11-03', 'expected_files':40336,
        'downloaded_verified_files':len(manifests), 'failures':failures,
        'elapsed_seconds':round(time.monotonic()-start,2)}, indent=2),encoding='utf-8')
    if failures:
        raise RuntimeError(f'{len(failures)} downloads failed; successful files preserved; no automatic retry.')
    print('COMPLETE: all 40,336 files match the official S3 sizes and single-part ETag MD5s.', flush=True)

if __name__ == '__main__':
    main()
