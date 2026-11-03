"""Deterministic candidate day-one cohort; standard library only, no fitting.

All study choices are in protocol_candidate_v2.json. Clinical labels are read
only for outcomes; predictors use ICU hours 1--12 exclusively.
"""
import collections
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DYNAMIC = 'HR O2Sat Temp SBP MAP DBP Resp EtCO2 BaseExcess HCO3 FiO2 pH PaCO2 SaO2 AST BUN Alkalinephos Calcium Chloride Creatinine Bilirubin_direct Glucose Lactate Magnesium Phosphate Potassium Bilirubin_total TroponinI Hct Hgb PTT WBC Fibrinogen Platelets'.split()
STATIC = ['Age','Gender','HospAdmTime']
FEATURES = DYNAMIC + STATIC
HEADER = DYNAMIC + ['Age','Gender','Unit1','Unit2','HospAdmTime','ICULOS','SepsisLabel']
STAGES = ['invalid_schema_or_values','invalid_time_axis','invalid_label_sequence',
          'insufficient_history_12h','nonadult_or_age_unknown','left_censored_onset',
          'onset_at_or_before_12h','insufficient_followup_24h','included']
SEED = '20261103'

def write_csv(path, fields, rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def summarize_record(text, site, filename):
    ident=site+'_'+Path(filename).stem
    rows=list(csv.reader(io.StringIO(text),delimiter='|'))
    q={'record_id':ident,'site':site,'source_filename':filename,'n_hours':max(0,len(rows)-1),
       'first_observed_hour':'','last_observed_hour':'','history_rows_observed':'',
       'source_ever_positive':'','first_positive_hour':'','onset_proxy_hour':'',
       'first_label_positive':'','label_transition_observed':'','age_at_landmark':'',
       'eligibility_reason':'','outcome_12_24':'','split':'excluded'}
    vals=[]
    if not rows or rows[0]!=HEADER or any(len(r)!=41 for r in rows[1:]):
        q['eligibility_reason']=STAGES[0]; return q,None
    try:
        vals=[[float(v) for v in row] for row in rows[1:]]
        if any(math.isinf(v) for row in vals for v in row): raise ValueError('Infinite value')
    except ValueError:
        q['eligibility_reason']=STAGES[0]; return q,None
    n=len(vals)
    q['source_ever_positive']=int(any(row[40]==1 for row in vals))
    hours=[row[39] for row in vals]
    if not n or any(not math.isfinite(h) or h<1 or h!=int(h) for h in hours) or any(b!=a+1 for a,b in zip(hours,hours[1:])):
        q['eligibility_reason']=STAGES[1]; return q,None
    q.update(first_observed_hour=int(hours[0]),last_observed_hour=int(hours[-1]))
    labels=[row[40] for row in vals]
    if any(v not in (0,1) for v in labels) or any(a>b for a,b in zip(labels,labels[1:])):
        q['eligibility_reason']=STAGES[2];return q,None
    first_index=next((i for i,v in enumerate(labels) if v==1),None)
    first=int(hours[first_index]) if first_index is not None else None
    onset=first+6 if first_index is not None and first_index>0 else None
    q.update(source_ever_positive=int(first is not None),first_positive_hour=first or '',
             onset_proxy_hour=onset if onset is not None else '',
             first_label_positive=int(labels[0]==1),label_transition_observed=int(onset is not None))
    hist=[row for row in vals if 1<=row[39]<=12]
    q['history_rows_observed']=len(hist)
    last=[]; counts=[]
    for j in range(40):
        obs=[row[j] for row in hist if not math.isnan(row[j])]
        last.append(obs[-1] if obs else None);counts.append(len(obs))
    q['age_at_landmark']=last[34] if last[34] is not None else ''
    if hours[0]>12 or hours[-1]<12: reason=STAGES[3]
    elif last[34] is None or last[34]<18: reason=STAGES[4]
    elif labels[0]==1: reason=STAGES[5]
    elif onset is not None and onset<=12: reason=STAGES[6]
    elif hours[-1]<24: reason=STAGES[7]
    else: reason='included'
    q['eligibility_reason']=reason
    if reason!='included': return q,None
    q['outcome_12_24']=int(onset is not None and 12<onset<=24)
    idx=list(range(34))+[34,35,38]
    x={k:(last[j] if last[j] is not None else '') for k,j in zip(FEATURES,idx)}
    missing=sum(v=='' for v in x.values())
    q['feature_missing_fraction']=missing/37
    q['hourly_dynamic_missing_fraction']=sum(12-counts[j] for j in range(34))/(12*34)
    return q,{'x':x,'mask':{k:int(x[k]=='') for k in FEATURES},
              'counts':{k:counts[j] for j,k in enumerate(DYNAMIC)}}

def main():
    start=time.monotonic()
    config={
        'version':'candidate_v2','date_hong_kong':'2026-11-03',
        'approval_status':'PENDING_C_LABEL_REVIEW_AND_E_PROTOCOL_CONFIRMATION',
        'missing_group_files':['T1_Uniform_Experiment_Specification_v1','T1_Technical_Handover_Agreement'],
        'dataset_doi':'10.13026/v64v-d857','dataset_version':'1.0.0',
        'analysis_unit':'one released subject/ICU record file; cross-stay person linkage unavailable',
        'landmark_hour':12,'feature_hours_inclusive':[1,12],
        'outcome_window':'12 < dataset_label_derived_onset_proxy_hour <= 24',
        'onset_proxy':'first observed 0-to-1 label transition ICULOS + 6; first-row positive is left-censored',
        'followup_endpoint_for_both_classes':'last observed ICULOS >=24','minimum_age_years':18,
        'time_axis_required':'positive integer ICULOS with unit increments; first observed hour may exceed1',
        'landmark_coverage':'first observed ICULOS <=12 and last observed ICULOS >=12',
        'unrecorded_leading_hours':'count as missing; no invented rows/values; denominators remain12hours',
        'dynamic_aggregation':'last observed value in hours 1--12; missing if none',
        'static_aggregation':'last observed value in hours 1--12; no use of later values',
        'predictors':FEATURES,'never_predictors':['SepsisLabel','record_id','site','split',
            'outcome_12_24','first_positive_hour','onset_proxy_hour','n_hours','Unit1','Unit2','ICULOS'],
        'development_site':'A','external_site':'B',
        'split_ratios_by_outcome_class':{'train':0.6,'calibration':0.2,'internal_test':0.2},
        'split_seed':SEED,'split_algorithm':'Sort SHA256(seed|record_id) within A outcome class; first floor(0.6*n) train; next floor(0.2*n) calibration; remainder internal_test; all B external_test',
        'model_fitting_performed':False,'core_method_fitting_performed':False,
        'missing_values':'empty CSV cells; no imputation, scaling, clipping, normal-range replacement, or outcome balancing',
        'raw_preserved':True}
    (ROOT/'protocol_candidate_v2.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
    audit=[];payload={};rawcounts={}; rawstats={}; agg=collections.defaultdict(lambda:[0,0])
    for site in ['A','B']:
        with zipfile.ZipFile(ROOT/'raw'/f'training_set{site}.zip') as z:
            names=sorted(n for n in z.namelist() if n.endswith('.psv'))
            assert len(names)==(20336 if site=='A' else 20000)
            assert len(names)==len(set(names))
            for i,name in enumerate(names,1):
                q,p=summarize_record(z.read(name).decode('utf-8-sig'),site,name)
                audit.append(q)
                if p is not None: payload[q['record_id']]=p
                if i%5000==0:print(f'Parsed site {site}: {i}/{len(names)}',flush=True)
            rawcounts[site]=len(names)
    included=[q for q in audit if q['eligibility_reason']=='included']
    assert len({q['record_id'] for q in audit})==40336
    for y in [0,1]:
        sub=[q for q in included if q['site']=='A' and q['outcome_12_24']==y]
        sub.sort(key=lambda q:hashlib.sha256((SEED+'|'+q['record_id']).encode()).hexdigest())
        n=len(sub); a=math.floor(.6*n);b=a+math.floor(.2*n)
        for i,q in enumerate(sub):q['split']='train' if i<a else 'calibration' if i<b else 'internal_test'
    for q in included:
        if q['site']=='B':q['split']='external_test'
    fields=list(audit[0])
    for k in ['feature_missing_fraction','hourly_dynamic_missing_fraction']:
        if k not in fields:fields.append(k)
    write_csv(ROOT/'data'/'eligibility_audit_all_records.csv',fields,audit)
    write_csv(ROOT/'data'/'patients.csv',fields,included)
    write_csv(ROOT/'data'/'patient_split_manifest.csv', ['record_id','site','outcome_12_24','split'],
              [{k:q[k] for k in ['record_id','site','outcome_12_24','split']} for q in included])
    for name,key,cols in [('X_last12.csv','x',FEATURES),('missing_mask37.csv','mask',FEATURES),('observed_counts34.csv','counts',DYNAMIC)]:
        write_csv(ROOT/'data'/name,['record_id']+cols,
                  [dict(record_id=q['record_id'],**payload[q['record_id']][key]) for q in included])
    counts=[]
    for site in ['A','B']:
        for stage in STAGES:
            sub=[q for q in audit if q['site']==site and q['eligibility_reason']==stage]
            counts.append({'site':site,'stage':stage,'n_records':len(sub)})
    write_csv(ROOT/'reports'/'cohort_flow.csv',['site','stage','n_records'],counts)
    bysplit=[]; missrows=[]
    scopes=[('site_A',[q for q in included if q['site']=='A']),('site_B',[q for q in included if q['site']=='B'])]
    scopes += [(s,[q for q in included if q['split']==s]) for s in ['train','calibration','internal_test','external_test']]
    all_missing_train=[]
    for scope,sub in scopes:
        n=len(sub);pos=sum(q['outcome_12_24'] for q in sub)
        bysplit.append({'scope':scope,'n_records':n,'positive':pos,'negative':n-pos,
                        'positive_fraction':pos/n if n else '',
                        'mean_feature_missing_fraction':sum(q['feature_missing_fraction'] for q in sub)/n if n else '',
                        'mean_hourly_dynamic_missing_fraction':sum(q['hourly_dynamic_missing_fraction'] for q in sub)/n if n else ''})
        for k in FEATURES:
            missing=sum(payload[q['record_id']]['mask'][k] for q in sub)
            vals=[payload[q['record_id']]['x'][k] for q in sub if payload[q['record_id']]['x'][k]!='']
            row={'scope':scope,'feature':k,'n_records':n,'missing_records':missing,
                 'missing_fraction':missing/n if n else '', 'observed_min':min(vals) if vals else '',
                 'observed_max':max(vals) if vals else ''}
            missrows.append(row)
            if scope=='train' and missing==n: all_missing_train.append(k)
        for k in DYNAMIC:
            missing=sum(12-payload[q['record_id']]['counts'][k] for q in sub)
            agg[(scope,k)]=[missing,n*12]
    write_csv(ROOT/'reports'/'cohort_counts.csv',list(bysplit[0]),bysplit)
    feasibility=[]
    for site in ['A','B']:
        targets=[q for q in audit if q['site']==site and q['onset_proxy_hour']!='' and 12<q['onset_proxy_hour']<=24]
        feasibility.append({'site':site,'known_transition_onsets_12_24_before_other_filters':len(targets),
            'retained_positive':sum(q['eligibility_reason']=='included' for q in targets),
            'known_positive_excluded_for_followup_24h':sum(q['eligibility_reason']=='insufficient_followup_24h' for q in targets),
            'excluded_followup_with_proxy_after_last_observation':sum(q['eligibility_reason']=='insufficient_followup_24h' and q['onset_proxy_hour']>q['last_observed_hour'] for q in targets),
            'known_positive_excluded_for_other_reasons':sum(q['eligibility_reason'] not in ('included','insufficient_followup_24h') for q in targets)})
    write_csv(ROOT/'reports'/'endpoint_feasibility.csv',list(feasibility[0]),feasibility)
    write_csv(ROOT/'reports'/'feature_missingness37.csv',list(missrows[0]),missrows)
    hourly=[{'scope':s,'feature':k,'missing_cells':v[0],'total_cells':v[1],
             'missing_fraction':v[0]/v[1] if v[1] else ''} for (s,k),v in agg.items()]
    write_csv(ROOT/'reports'/'hourly_missingness34.csv',list(hourly[0]),hourly)
    allowed=[k for k in FEATURES if k not in all_missing_train]
    (ROOT/'data'/'model_feature_columns.json').write_text(json.dumps({
        'fit_scope':'train only','all_missing_training_columns':all_missing_train,
        'recommended_model_columns':allowed,'master_table_columns':FEATURES,
        'note':'No learned values were fit. Drop training-all-missing columns consistently before any imputation; keep master data unchanged.'},indent=2),encoding='utf-8')
    summary={'raw_counts':rawcounts,'source_ever_positive_counts':{s:sum(q['source_ever_positive']==1 for q in audit if q['site']==s) for s in ['A','B']},
             'time_axis_start_after_1_counts':{s:sum(q['first_observed_hour']!='' and q['first_observed_hour']>1 for q in audit if q['site']==s) for s in ['A','B']},
             'endpoint_feasibility':feasibility,
             'flow':counts,'cohorts':bysplit,'training_all_missing_features':all_missing_train,
             'elapsed_seconds':round(time.monotonic()-start,2),'candidate_status':config['approval_status']}
    (ROOT/'reports'/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    checks={
        'raw_file_count_40336':len(audit)==40336,
        'unique_record_ids':len({q['record_id'] for q in audit})==len(audit),
        'no_duplicate_model_rows':len(payload)==len(included),
        'flow_exhaustive':sum(r['n_records'] for r in counts)==40336,
        'all_included_observed_through_24h':all(q['last_observed_hour']>=24 and q['first_observed_hour']<=12 for q in included),
        'no_early_or_left_censored_onsets_in_cohort':all(q['first_label_positive']==0 and (q['onset_proxy_hour']=='' or q['onset_proxy_hour']>12) for q in included),
        'target_matches_label_hours_7_to_18':all(q['outcome_12_24']==int(q['first_positive_hour']!='' and 7<=q['first_positive_hour']<=18) for q in included),
        'site_B_entirely_external':all(q['split']=='external_test' for q in included if q['site']=='B'),
        'site_A_no_external':all(q['split']!='external_test' for q in included if q['site']=='A'),
        'features_exclude_future_and_label_metadata':not bool(set(FEATURES)&set(config['never_predictors'])),
        'mask_matches_predictors':all(p['mask'][k]==int(p['x'][k]=='') for p in payload.values() for k in FEATURES),
        'observations_within_12h':all(0<=v<=12 for p in payload.values() for v in p['counts'].values())}
    (ROOT/'reports'/'pipeline_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    assert all(checks.values()),checks
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted((ROOT/'data').glob('*')) if p.is_file()}
    (ROOT/'reports'/'derived_data_sha256.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2),flush=True)
    print('All cohort pipeline checks passed.',flush=True)

if __name__=='__main__':main()
