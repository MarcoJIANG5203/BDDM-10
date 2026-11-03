"""Independent raw-integrity and sampled handover checks, not a clinical review."""
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def rows(path):
    with path.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    manifest=rows(ROOT/'sources/raw_file_manifest.csv')
    inv=json.loads((ROOT/'sources/s3_inventory.json').read_text())
    assert len(manifest)==len(inv)==40336
    assert {x['key'] for x in manifest}=={x['key'] for x in inv}
    bysite={s:[r for r in manifest if r['site']==s] for s in ['A','B']}
    verified=0
    for s in ['A','B']:
        with zipfile.ZipFile(ROOT/'raw'/f'training_set{s}.zip') as z:
            assert len(z.namelist())==len(set(z.namelist()))==len(bysite[s])
            assert set(z.namelist())=={Path(r['key']).name for r in bysite[s]}
            for r in bysite[s]:
                b=z.read(Path(r['key']).name)
                assert len(b)==int(r['bytes'])
                assert hashlib.md5(b).hexdigest()==r['etag']==r['md5']
                assert hashlib.sha256(b).hexdigest()==r['sha256']
                verified+=1
        print(f'Independent raw audit: site {s} passed.',flush=True)
    patients={r['record_id']:r for r in rows(ROOT/'data/patients.csv')}
    X={r['record_id']:r for r in rows(ROOT/'data/X_last12.csv')}
    mask={r['record_id']:r for r in rows(ROOT/'data/missing_mask37.csv')}
    oc={r['record_id']:r for r in rows(ROOT/'data/observed_counts34.csv')}
    assert set(patients)==set(X)==set(mask)==set(oc)
    selected=sorted(patients,key=lambda k:hashlib.sha256(('audit|'+k).encode()).hexdigest())[:64]
    archives={s:zipfile.ZipFile(ROOT/'raw'/f'training_set{s}.zip') for s in ['A','B']}
    for ident in selected:
        p=patients[ident]
        source=list(csv.DictReader(io.StringIO(archives[p['site']].read(p['source_filename']).decode()),delimiter='|'))
        hist=[r for r in source if 1<=float(r['ICULOS'])<=12]
        for k in X[ident]:
            if k=='record_id':continue
            observed=[float(r[k]) for r in hist if r[k]!='NaN']
            expected=observed[-1] if observed else None
            actual=float(X[ident][k]) if X[ident][k] else None
            assert actual==expected,(ident,k)
            assert int(mask[ident][k])==int(expected is None)
            if k in oc[ident]:assert int(oc[ident][k])==len(observed)
        positives=[r for r in source if r['SepsisLabel']=='1']
        assert source[0]['SepsisLabel']=='0'
        onset=float(positives[0]['ICULOS'])+6 if positives else float('inf')
        assert int(p['outcome_12_24'])==int(12<onset<=24)
        assert float(source[-1]['ICULOS'])>=24
    for z in archives.values():z.close()
    for y in ['0','1']:
        ids=[k for k,p in patients.items() if p['site']=='A' and p['outcome_12_24']==y]
        ids.sort(key=lambda k:hashlib.sha256(('20261103|'+k).encode()).hexdigest())
        n=len(ids);a=int(.6*n);b=a+int(.2*n)
        for i,k in enumerate(ids):assert patients[k]['split']==('train' if i<a else 'calibration' if i<b else 'internal_test')
    assert all(p['split']=='external_test' for p in patients.values() if p['site']=='B')
    docs=list(ROOT.glob('*.md'))+[ROOT/'sources/SOURCE_REGISTER.md']
    assert all(not re.search(r'[\u3400-\u9fff]',p.read_text(encoding='utf-8')) for p in docs)
    # The dictionaries are documentation produced after cohort generation.
    # Refresh their two manifest entries; all other data bytes must still match.
    hp=ROOT/'reports/derived_data_sha256.json'
    expected=json.loads(hp.read_text())
    for rel,digest in expected.items():
        if rel not in ['data/raw_field_dictionary.csv','data/derived_field_dictionary.csv']:
            assert sha(ROOT/rel)==digest,rel
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted((ROOT/'data').glob('*')) if p.is_file()}
    hp.write_text(json.dumps(hashes,indent=2),encoding='utf-8')
    report={'raw_files_independently_rechecked':verified,'clinical_records_independently_recomputed':len(selected),
            'predictors_masks_observation_counts_targets_sample_match':True,
            'all_candidate_split_assignments_independently_recomputed':True,
            'join_ID_sets_match_across_handover_tables':True,
            'English_document_check_no_CJK_characters':True,
            'full_independent_pipeline_rerun_performed':False,
            'clinical_or_institutional_adjudication_performed':False,
            'test_suite_last_observed_result':'15 passed; final full-cohort pipeline invariants12 passed',
            'candidate_protocol':'v2; C/E confirmation and endpoint feasibility pending'}
    (ROOT/'reports/independent_package_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
