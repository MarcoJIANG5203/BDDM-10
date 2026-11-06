# B-002 formal-input main: 20261105T055420_02d05b15

Producer delivery complete; independent C/E result acceptance is pending.
Protocol v1; formal A data a-data-v1-20261104-r1. This is a new immutable run.
Elapsed: 1208.95s. Data synthetic=false.

Independent checks: 900 metric rows; 30 paired bootstrap intervals; 45 artifact / 13 source / 5 split hashes.

## Batch 0, 60% target capacity (all planned scenarios)

| Seed | Model | M | alpha | Scenario | B2 accepted/errors | B4 accepted/errors | B4-B2 risk difference [95% CI] |
|---:|---|---:|---:|---|---|---|---|
| 2026 | LR | 10 | 0.1 | S0 | 915/1 | 915/2 | 0.00109290 [0.00000000, 0.00327869] |
| 2026 | LR | 10 | 0.1 | S1 | 915/3 | 915/4 | 0.00109290 [0.00000000, 0.00327869] |
| 2026 | LR | 10 | 0.1 | S2 | 915/3 | 915/3 | 0.00000000 [0.00000000, 0.00000000] |
| 2026 | LR | 10 | 0.1 | S3 | 915/3 | 915/3 | 0.00000000 [-0.00327869, 0.00327869] |
| 2026 | LR | 10 | 0.1 | S4 | 8352/24 | 8352/21 | -0.00035920 [-0.00107759, 0.00035920] |
| 2027 | LR | 10 | 0.1 | S0 | 915/6 | 915/5 | -0.00109290 (other-seed stability only) |
| 2027 | LR | 10 | 0.1 | S1 | 915/5 | 915/6 | 0.00109290 (other-seed stability only) |
| 2027 | LR | 10 | 0.1 | S2 | 915/5 | 915/5 | 0.00000000 (other-seed stability only) |
| 2027 | LR | 10 | 0.1 | S3 | 915/2 | 915/2 | 0.00000000 (other-seed stability only) |
| 2027 | LR | 10 | 0.1 | S4 | 8352/21 | 8352/21 | 0.00000000 (other-seed stability only) |
| 2028 | LR | 10 | 0.1 | S0 | 915/6 | 915/5 | -0.00109290 (other-seed stability only) |
| 2028 | LR | 10 | 0.1 | S1 | 915/4 | 915/4 | 0.00000000 (other-seed stability only) |
| 2028 | LR | 10 | 0.1 | S2 | 915/3 | 915/3 | 0.00000000 (other-seed stability only) |
| 2028 | LR | 10 | 0.1 | S3 | 915/4 | 915/4 | 0.00000000 (other-seed stability only) |
| 2028 | LR | 10 | 0.1 | S4 | 8352/26 | 8352/26 | 0.00000000 (other-seed stability only) |
| 2029 | LR | 10 | 0.1 | S0 | 915/4 | 915/5 | 0.00109290 (other-seed stability only) |
| 2029 | LR | 10 | 0.1 | S1 | 915/4 | 915/4 | 0.00000000 (other-seed stability only) |
| 2029 | LR | 10 | 0.1 | S2 | 915/4 | 915/4 | 0.00000000 (other-seed stability only) |
| 2029 | LR | 10 | 0.1 | S3 | 915/3 | 915/4 | 0.00109290 (other-seed stability only) |
| 2029 | LR | 10 | 0.1 | S4 | 8352/22 | 8352/18 | -0.00047893 (other-seed stability only) |
| 2030 | LR | 10 | 0.1 | S0 | 915/3 | 915/4 | 0.00109290 (other-seed stability only) |
| 2030 | LR | 10 | 0.1 | S1 | 915/3 | 915/3 | 0.00000000 (other-seed stability only) |
| 2030 | LR | 10 | 0.1 | S2 | 915/1 | 915/1 | 0.00000000 (other-seed stability only) |
| 2030 | LR | 10 | 0.1 | S3 | 915/5 | 915/4 | -0.00109290 (other-seed stability only) |
| 2030 | LR | 10 | 0.1 | S4 | 8352/23 | 8352/24 | 0.00011973 (other-seed stability only) |

Risk differences use proportions, not percentage points. Negative favours B4.

## Limits and complete evidence

The two hospitals contain only 57 and 38 positives; internal test has 8 positives per seed. MI positive-class set coverage is zero in every planned setting here. B5/B6 are unavailable because the selection set has 6 errors and 1,012 correct cases (the protocol requires at least 20 of each); B6-B5 is unavailable, not zero. No stable disagreement advantage or clinical safety claim is supported. Other-seed results reuse the same cohort and are not independent cohorts.

All capacities, batch/frozen rules, coverage strata, stability and unavailable-method reasons are retained in the small CSV/JSON files alongside this summary; full patients, p_m, models, masks and draw seeds are in the registered B-002 Release bundle. The numerical metric/CI tables and model parameters reproduce the prior candidate, but prior candidate acceptance does not transfer to this run.

A source license metadata conflict and user-reported E approval provenance remain as recorded in A formal freeze; no new source clearance or recipient acceptance is asserted.

Recheck with:

```powershell
python reviews/verify_b_artifacts.py results/clinical/20261105T055420_02d05b15
python reviews/verify_candidate_bootstrap.py results/clinical/20261105T055420_02d05b15 --output .artifact-cache/20261105T055420_02d05b15-bootstrap.json
```
