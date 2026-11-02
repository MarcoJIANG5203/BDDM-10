import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from src.data import FEATURES,load_cohort
from src.models import predict_draws
from src.selection import frozen_accept
from src.conformal import prediction_sets,singleton_predictions
r=Path('results/synthetic/20261102T062332_98484fc5')
a=joblib.load(r/'models/seed2026_LR_M10_alpha0.1.joblib')
f,s,audit=load_cohort(a['config'],2026)
x=f.loc[s['test'],FEATURES]
z,_,_=a['imputer'].transform(x,s['test'],M=10,role='test',batch=0)
p=predict_draws(a['model'],z)
expected=pd.read_csv(r/'patient_predictions.csv')
expected=expected[(expected.method=='B1')&(expected.scenario=='S0')&(expected.imputation_batch==0)]
assert np.array_equal(p['p_mean'],expected.p_mean.to_numpy()) or np.allclose(p['p_mean'],expected.p_mean,atol=1e-15)
pool,_=singleton_predictions(prediction_sets(p['p_mean'],a['q']))
actual=frozen_accept(s['test'],pool,p['p_std'],a['thresholds']['B4',.6])
expected=pd.read_csv(r/'patient_predictions.csv')
expected=expected[(expected.method=='B4')&(expected.target_acceptance==.6)&(expected.selection_mode=='frozen')&(expected.scenario=='S0')&(expected.imputation_batch==0)]
assert np.array_equal(actual,expected.accepted)
print('PASS: trusted local joblib reload reproduced S0 MI probabilities and frozen B4 decisions.')
