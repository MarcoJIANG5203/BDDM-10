"""Repair individually recorded transport failures, retaining the failed receipt."""
import csv
import hashlib
import json
from pathlib import Path
import zipfile
import requests

ROOT=Path(__file__).resolve().parents[1]

def main():
    sp=ROOT/'sources/download_status.json'
    old=json.loads(sp.read_text())
    if not old['failures']:
        print('No missing downloads.');return
    original=ROOT/'sources/download_status_attempt1.json'
    if not original.exists():original.write_bytes(sp.read_bytes())
    inv={o['key']:o for o in json.loads((ROOT/'sources/s3_inventory.json').read_text())}
    mp=ROOT/'sources/raw_file_manifest.csv'
    with mp.open(newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;manifest=list(reader)
    remaining=[];fixed=[]
    for err in old['failures']:
        obj=inv[err['key']];url='https://physionet-open.s3.amazonaws.com/'+obj['key']
        try:
            with requests.Session() as session:
                r=session.get(url,timeout=(15,60));r.raise_for_status();b=r.content
            md5=hashlib.md5(b).hexdigest()
            assert len(b)==obj['bytes'] and md5==obj['etag'], obj['key']
            with zipfile.ZipFile(ROOT/'raw'/f"training_set{obj['site']}.zip",'a',compression=zipfile.ZIP_DEFLATED) as z:
                name=Path(obj['key']).name
                assert name not in z.namelist()
                z.writestr(name,b)
            manifest.append(dict(obj,md5=md5,sha256=hashlib.sha256(b).hexdigest(),url=url,etag_md5_verified=True))
            fixed.append({'key':obj['key'],'url':url,'status':200,'size_and_etag_md5_verified':True})
            print('Recovered '+name,flush=True)
        except Exception as e:remaining.append({'key':obj['key'],'error':str(e)})
    manifest.sort(key=lambda x:x['key'])
    with mp.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(manifest)
    (ROOT/'sources/download_recovery_receipt.json').write_text(json.dumps(fixed,indent=2),encoding='utf-8')
    old.update(downloaded_verified_files=len(manifest),failures=remaining,
               recovery_note='Individual fresh HTTPS sessions repaired transport failures; original failed receipt preserved separately.')
    sp.write_text(json.dumps(old,indent=2),encoding='utf-8')
    assert not remaining,remaining
    assert len(manifest)==40336
    print('COMPLETE: all 40,336 official files verified.',flush=True)

if __name__=='__main__':main()
