"""B-reader integration and independent raw evidence checks. No model fitting."""
import argparse,csv,hashlib,io,json,math,os,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import yaml
from src.data import FEATURES,ROLES,load_cohort

def filehash(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def verify(project):
 os.chdir(project);folder=project/'data/processed'
 audit=json.loads((folder/'cohort_audit.json').read_text())
 config=yaml.safe_load((project/'configs/protocol_v1.yaml').read_text())
 assert config['protocol_version']==audit['protocol_version']=='v1'
 counts={};data=pd.read_csv(folder/'cohort.csv',dtype={'patient_id':str})
 assert list(data)==['patient_id','site','y_true']+FEATURES
 parquet=pd.read_parquet(folder/'cohort.parquet')
 pd.testing.assert_frame_equal(data,parquet,check_dtype=False)
 for seed in range(2026,2031):
  counts[str(seed)]={}
  for ext in ['parquet','csv']:
   config['data_path']=f'data/processed/cohort.{ext}'
   frame,splits,_=load_cohort(config,seed)
   for role in ROLES:
    part=frame.loc[splits[role]]
    counts[str(seed)][role]={'n':len(part),'positive':int(part.y_true.sum()),'negative':int((part.y_true==0).sum())}
  assert counts[str(seed)]==audit['split_counts'][str(seed)]
 for rel,digest in audit['file_sha256'].items():assert filehash(project/rel)==digest,rel
 review=pd.read_csv(folder/'review_10_positive_10_negative.csv',dtype={'patient_id':str})
 assert len(review)==20 and review.y_true.value_counts().to_dict()=={0:10,1:10}
 indexed=data.set_index('patient_id');checks=[]
 for row in review.to_dict('records'):
  path=project/row['raw_evidence'];assert filehash(path)==row['raw_sha256']
  original=list(csv.DictReader(io.StringIO(path.read_text()),delimiter='|'))
  axis=[int(float(r['ICULOS'])) for r in original]
  assert axis[:24]==list(range(1,25))
  labels=[int(r['SepsisLabel']) for r in original];assert labels[0]==0 and labels==sorted(labels)
  first=next((i for i,y in enumerate(labels) if y==1),None)
  onset=axis[first]+6 if first is not None else math.inf
  target=int(12<onset<=24);assert target==row['y_true']
  patient=indexed.loc[row['patient_id']]
  for feature in FEATURES:
   observed=[float(r[feature]) for r in original if int(float(r['ICULOS']))<=12 and r[feature]!='NaN']
   expected=observed[-1] if observed else math.nan;actual=patient[feature]
   assert (math.isnan(expected) and pd.isna(actual)) or expected==actual,(row['patient_id'],feature)
  checks.append({'patient_id':row['patient_id'],'site':row['site'],'y_true':target,
                 'raw_hour_label_feature_check':'PASS','human_C_review':'PENDING'})
 result={'interface':'PASS','B_loader_invocations':10,'parquet_csv_equivalence':'PASS',
   'five_seed_counts':counts,'hashes':'PASS','20_actual_raw_cases':checks,
   'full_input_hour_audit':'data/processed/record_audit.csv',
   'precision_gates':audit['precision_gates'],
   'C_independent_human_review':'PENDING','E_freeze_decision':'PENDING',
   'clinical_experiments_run':False,'conclusion':'Interface usable; not accepted by C/E; precision gates not met.'}
 path=project/'reviews/A_interface_validation.json';path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in result.items() if k not in ['five_seed_counts','20_actual_raw_cases']},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path(__file__).resolve().parents[1]);args=p.parse_args();verify(args.project_root.resolve())
