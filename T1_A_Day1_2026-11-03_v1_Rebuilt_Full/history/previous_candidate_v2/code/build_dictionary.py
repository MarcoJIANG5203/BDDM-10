"""English schema documentation; source units are metadata, never conversions."""
from pathlib import Path
from prepare_day1 import DYNAMIC, FEATURES, HEADER, write_csv

ROOT=Path(__file__).resolve().parents[1]
DESCRIPTIONS=[
('Heart rate','beats/min'),('Pulse oximetry','%'),('Temperature','degrees C'),
('Systolic blood pressure','mm Hg'),('Mean arterial pressure','mm Hg'),('Diastolic blood pressure','mm Hg'),
('Respiration rate','breaths/min'),('End-tidal carbon dioxide','mm Hg'),
('Base excess','mmol/L'),('Bicarbonate','mmol/L'),('Fraction of inspired oxygen','%'),
('pH','unitless'),('Arterial carbon dioxide partial pressure','mm Hg'),('Arterial oxygen saturation','%'),
('Aspartate transaminase','IU/L'),('Blood urea nitrogen','mg/dL'),('Alkaline phosphatase','IU/L'),
('Calcium','mg/dL'),('Chloride','mmol/L'),('Creatinine','mg/dL'),('Direct bilirubin','mg/dL'),
('Glucose','mg/dL'),('Lactate','mg/dL'),('Magnesium','mmol/dL'),('Phosphate','mg/dL'),
('Potassium','mmol/L'),('Total bilirubin','mg/dL'),('Troponin I','ng/mL'),('Hematocrit','%'),
('Hemoglobin','g/dL'),('Partial thromboplastin time','seconds'),('White blood cell count','10^3/uL'),
('Fibrinogen','mg/dL'),('Platelet count','10^3/uL'),
('Age; source encodes patients aged 90 or above as 100','years'),
('Source Gender encoding: female=0; male=1','binary'),
('Administrative MICU indicator','binary'),('Administrative SICU indicator','binary'),
('Hospital-to-ICU admission offset as supplied','hours'),('Hourly ICU time since ICU admission','hours'),
('Shifted sepsis label; positive begins six hours before dataset-defined onset','binary')]

def main():
 rows=[]
 for i,(k,(desc,unit)) in enumerate(zip(HEADER,DESCRIPTIONS),1):
  role='dynamic_predictor' if k in DYNAMIC else ('static_predictor' if k in FEATURES else 'excluded_from_X')
  note='Documented source unit only; no unit conversion or clinical range validation performed.'
  if k in ['FiO2','Lactate','Magnesium']:note+=' Unit/scaling requires explicit review before clinical thresholds; retain raw numeric values.'
  if k=='Age':note+=' The >=90 encoding is not an exact age.'
  if k=='HospAdmTime':note+=' Usually negative for hospital admission before ICU; do not infer calendar dates.'
  rows.append({'source_column_index_1based':i,'field':k,'english_meaning':desc,
               'documented_source_unit_or_encoding':unit,'candidate_role':role,
               'missing_encoding':'NaN','notes':note,
               'source_url':'https://physionet.org/content/challenge-2019/1.0.0/'})
 assert len(rows)==41
 write_csv(ROOT/'data/raw_field_dictionary.csv',list(rows[0]),rows)
 defs={
 'record_id':('string','join_key_only','Site prefix plus original file stem; unique per released record, not verified cross-stay person identifier.'),
 'site':('A or B','metadata_only','A development hospital; B external hospital under candidate v2.'),
 'source_filename':('string','metadata_only','Original .psv name inside its site archive.'),
 'first_observed_hour':('integer','metadata_only','First actual ICULOS value in the raw file.'),
 'last_observed_hour':('integer','future_metadata_never_predictor','Last actual ICULOS value; determines observed horizon coverage.'),
 'history_rows_observed':('integer 0--12','audit_metadata','Number of actual recorded rows at ICULOS1--12; missing leading hours are not invented.'),
 'n_hours':('integer','future_metadata_never_predictor','Number of observed hourly rows in the full raw file; not the last elapsed ICU hour.'),
 'source_ever_positive':('0 or 1','future_metadata_never_predictor','Any positive official label anywhere in the full record; not the landmark target.'),
 'first_positive_hour':('integer or empty','future_metadata_never_predictor','First positive label ICULOS; empty when no label is positive.'),
 'onset_proxy_hour':('integer or empty','future_metadata_never_predictor','Observed zero-to-one transition hour +6; empty for all-zero or first-row-positive records.'),
 'first_label_positive':('0 or 1','metadata_only','One if label positive at first observed hour; onset is left-censored.'),
 'label_transition_observed':('0 or 1','metadata_only','One if first positive hour >1 after preceding zero; zero otherwise.'),
 'age_at_landmark':('numeric or empty','audit_metadata','Last observed Age at hours1--12; source >=90 encoding retained.'),
 'eligibility_reason':('category','metadata_only','First sequential exclusion reason or included; see protocol.'),
 'outcome_12_24':('0 or 1 or empty','target_only','One if onset proxy in (12,24]; zero for other eligible records; empty for excluded records.'),
 'split':('category','partition_only','train/calibration/internal_test/external_test for eligible records; excluded otherwise.'),
 'feature_missing_fraction':('fraction 0--1','missingness_metadata','Number of absent aggregate predictors divided by37; no extra imputation performed.'),
 'hourly_dynamic_missing_fraction':('fraction 0--1','missingness_metadata','Missing dynamic hourly cells divided by12*34 before aggregation.'),
 'X_last12.csv::<feature>':('numeric or empty','candidate_predictor','Last nonmissing source value at ICU hours1--12 for each of37 predictors; no later value is used.'),
 'missing_mask37.csv::<feature>':('0 or 1','missingness_mask','One means corresponding aggregate predictor is empty; zero means observed. Same37 names as X.'),
 'observed_counts34.csv::<feature>':('integer 0--12','audit_metadata','Number of nonmissing cells for each dynamic variable within12 hourly rows; not automatically a model input.'),
 'feature_missingness37.csv::missing_fraction':('fraction 0--1','summary','Records with absent aggregate feature divided by records in named scope.'),
 'hourly_missingness34.csv::missing_fraction':('fraction 0--1','summary','Missing hourly cells for named variable divided by12 times records in named scope.')}
 derived=[{'field_or_pattern':k,'type':v[0],'role':v[1],'meaning':v[2],'origin':'Derived by code/prepare_day1.py under protocol_candidate_v2.json'} for k,v in defs.items()]
 write_csv(ROOT/'data/derived_field_dictionary.csv',list(derived[0]),derived)
 print('41 raw fields and 23 derived field/pattern definitions documented.')

if __name__=='__main__':main()
