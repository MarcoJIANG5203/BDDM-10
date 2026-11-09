# Fig 5 source and filter

Fig 5 (`fig5_disagreement.{pdf,png}`) is a DRAFT diagnostic, not a paper result.

## Source

- Run: `20261105T055420_02d05b15`
- Bundle: `b-clinical-v1-20261104-r1` (155,365,045 B, SHA256 `2328d26682a39ccb895553d3cee3dc6dd11bd6506c41a5a0ac0f5d49890e8426`)
- Member: `results/clinical/20261105T055420_02d05b15/patient_predictions.csv`
- Uncompressed size: 599,215,288 B
- Full-file SHA256: `aa23c96131d0548208adc52bb0bf727700316e09dd981c9ebfec45dd1d5cf2b2` (matches the run manifest)

## Filter

The 599 MB member was decompressed in a stream and the following rows were retained:

```text
split_seed = 2026
model = LR
M = 10
source_M = 10
scenario = S0
alpha = 0.1
imputation_batch = 0
method = B4
target_acceptance = 0.6
selection_mode = batch
```

- Rows scanned: 2,612,100
- Filtered rows: 1,525
- Filtered file SHA256: `1fd235356954cc85d6d650496ae427efb24f6d5754978c18140e32bd86fd9732`
- The filtered patient-level file is **not committed** to Git (patient-level output); only the aggregated `fig5_disagreement_data.csv` is committed.

## What Fig 5 shows

- 1,388 singleton predictions; **4 errors** in total.
- Error rate by disagreement quintile: 1/278, 0/277, 1/278, 0/277, 2/278.
- The figure is annotated “Sparse errors; descriptive only”; it is not evidence of a stable disagreement advantage or clinical safety.

## Status

`DRAFT_CANDIDATE_NOT_ACCEPTED`. No C/E acceptance record exists. Do not cite or insert into the manuscript.
