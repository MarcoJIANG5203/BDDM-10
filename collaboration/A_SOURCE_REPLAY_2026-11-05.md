# A original-source recovery for C — 5 November 2026

## Current availability

The complete original source archive is **published**, not a draft. It is a historical source prerelease, distinct from the current formal technical data version. A downloaded the actual source asset again on 5 November, checked its complete SHA-256 and ZIP CRC, and confirmed that the two embedded raw archives contain 20,336 and 20,000 PSV members. This corrects the stale draft-download-channel statement in [C006](https://github.com/MarcoJIANG5203/BDDM-10/blob/b6d7c3293db1c2263bc6ae4a25ce3e178415aeb8/handoffs/C/2026-11-05_%E6%AD%A3%E5%BC%8Frun%E7%8B%AC%E7%AB%8B%E5%A4%8D%E6%A0%B8.md). It does not claim C has downloaded or replayed it.

| Purpose | Published asset | Bytes | SHA-256 |
|---|---|---:|---|
| Current frozen data, annotated audit, five splits and private raw receipt | [a-data-v1-20261104-r1](https://github.com/MarcoJIANG5203/BDDM-10/releases/tag/a-data-v1-20261104-r1) | 4,666,169 | `feb69777e7c03c51d580808182a4702a2b3991a0edd552ec4d0dcbf7b1a7129c` |
| Complete unchanged original package, including both raw ZIPs, original audit and checksum manifest | [T1_A_Day1_2026-11-03_v1_Rebuilt_Full.zip](https://github.com/MarcoJIANG5203/BDDM-10/releases/tag/a-v1-source-archive-20261104-r1) | 50,674,324 | `a57d16dc5432b2e2518bc5f754b706c60de7b94d3fb496870687d4a564770cb1` |

Source asset API ID: `709375176`. Formal data asset API ID: `709705860`. The repository is private; each receiver needs their own repository access. A successful owner-account check does not verify another member's credentials. No access token is distributed in the handoff.

## Recovery and raw replay

Use an authenticated GitHub CLI and A's current registry entry. For the source archive, this alternative works without switching scientific data in the worktree:

```powershell
New-Item -ItemType Directory -Force -Path '.artifact-cache/a-source-download' | Out-Null
gh release download a-v1-source-archive-20261104-r1 --repo MarcoJIANG5203/BDDM-10 --pattern T1_A_Day1_2026-11-03_v1_Rebuilt_Full.zip --dir .artifact-cache/a-source-download
$aSourceZip = '.artifact-cache/a-source-download/T1_A_Day1_2026-11-03_v1_Rebuilt_Full.zip'
$aSourceHash = (Get-FileHash -LiteralPath $aSourceZip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($aSourceHash -ne 'a57d16dc5432b2e2518bc5f754b706c60de7b94d3fb496870687d4a564770cb1') { throw 'Source archive SHA256 mismatch' }
```

From the A checkout containing `scripts/verify_a_raw_psv_receipt.py` and the locked dependencies, safely restore into a separate cache directory. The extractor validates the allowed root before writing and refuses conflicting existing bytes:

```powershell
@'
from pathlib import Path
from scripts.sync_artifacts import extract_bundle
archive = Path('.artifact-cache/a-source-download/T1_A_Day1_2026-11-03_v1_Rebuilt_Full.zip')
extract_bundle(archive, Path('.artifact-cache/a-source-replay'), ['T1_A_Day1_2026-11-03_v1_Rebuilt_Full'], 'a57d16dc5432b2e2518bc5f754b706c60de7b94d3fb496870687d4a564770cb1')
print('Verified original source restored into a separate review cache')
'@ | python -
python scripts/verify_a_raw_psv_receipt.py --package .artifact-cache/a-source-replay/T1_A_Day1_2026-11-03_v1_Rebuilt_Full --output-root .artifact-cache/c-raw-replay
```

Do not use PowerShell text redirection for binary asset API responses. A receiver who already uses the authenticated GitHub asset API for the B result bundle can use the source asset ID above with the same binary-safe method. Do not print credentials or commit a token. The CLI is an optional convenience, not evidence that C has used it.

The provided raw checker is **A's automated checker**. C may replay it as an additional consistency check, but calling it is not an independently implemented C onset audit. C must determine and describe its own independent review scope, including left-censoring, timing boundaries and raw-hour discrepancies. Keep per-record CSV output outside ordinary Git; publish aggregate findings and an explicit own-scope conclusion.

## Version boundary

The source package contains its original clinical audit version `a-clinical-protocol-v1-20261103-full-r1`; the formal delivery audit uses `a-data-v1-20261104-r1`. Use the source package for raw replay and the formal asset for B input identity. The cohort CSV/Parquet and all five splits have the same frozen scientific bytes. Do not substitute an old audit for the formal audit or overwrite a B run.

Verification evidence: [daily receipt](../reviews/A_daily_delivery_verification_2026-11-05.json). Scope: source availability and exact identities; not clinical adjudication, new C personal signoff or a resolution of the source-license discrepancy.
