"""Supplemental full-delivery diagnostics; does not change B's cohort or splits."""
import csv,json,math,io,zipfile,shutil
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def write(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
 audit=json.loads((ROOT/'data/processed/cohort_audit.json').read_text())
 frame=pd.read_parquet(ROOT/'data/processed/cohort.parquet');features=audit['feature_order']
 mask=frame[features].isna().astype(int);mask.insert(0,'patient_id',frame.patient_id)
 mask.to_csv(ROOT/'data/diagnostics/missing_mask36.csv',index=False)
 ids=set(frame.patient_id);obs=[]
 for site in ['A','B']:
  with zipfile.ZipFile(ROOT/'raw'/f'training_set{site}.zip') as z:
   for name in sorted(z.namelist()):
    ident=site+'_'+Path(name).stem
    if ident not in ids:continue
    rows=list(csv.DictReader(io.StringIO(z.read(name).decode()),delimiter='|'))[:12]
    assert [int(float(r['ICULOS'])) for r in rows]==list(range(1,13))
    counts={k:sum(not math.isnan(float(r[k])) for r in rows) for k in features[:34]}
    obs.append({'patient_id':ident,**counts})
 write(ROOT/'data/diagnostics/observed_counts34.csv',obs)
 obs_frame=pd.DataFrame(obs).set_index('patient_id')
 hourly=[]
 for site in ['A','B']:
  selected=frame.loc[frame.site==site,'patient_id'];n=len(selected)
  for feature in features[:34]:
   missing=int(n*12-obs_frame.loc[selected,feature].sum())
   hourly.append({'site':site,'feature':feature,'missing_hourly_cells':missing,'total_hourly_cells':n*12,'missing_fraction':missing/(n*12)})
 write(ROOT/'reports/hourly_missingness34.csv',hourly)
 shutil.copy2(ROOT/'data/processed/feature_missingness.csv',ROOT/'reports/feature_missingness36.csv')
 flows=[]
 for site,counts in audit['site_counts'].items():
  for reason,n in counts['exclusions'].items():flows.append({'site':site,'reason':reason,'n':n})
  flows.append({'site':site,'reason':'included','n':counts['included']})
 write(ROOT/'reports/cohort_flow.csv',flows)
 parts=[]
 for seed,roles in audit['split_counts'].items():
  for role,stats in roles.items():parts.append({'seed':seed,'role':role,**stats})
 write(ROOT/'reports/cohort_counts_by_seed.csv',parts)
 provenance={'data_version':audit['data_version'],'mask_definition':'1=missing;0=observed;36 columns in formal order',
   'observation_counts':'Number of observed cells in actual hours1--12 for34 physiological/laboratory variables',
   'scope':'Auxiliary diagnostics only. B consumes data/processed/cohort and generates its own indicators.',
   'no_data_or_split_modification':True}
 (ROOT/'data/diagnostics/README.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
 print('Full-current-version diagnostics generated; original data and splits unchanged.')

if __name__=='__main__':
 (ROOT/'data/diagnostics').mkdir(parents=True,exist_ok=True)
 main()
