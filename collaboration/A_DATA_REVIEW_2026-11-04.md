> Superseded delivery status: A formal technical data version is now published at https://github.com/MarcoJIANG5203/BDDM-10/releases/tag/a-data-v1-20261104-r1. See `handoffs/A/2026-11-04_formal_data_freeze_EN.md`. Older draft-state paragraphs below are historical. E approval is user-reported; licensing clarification remains unresolved; B results are not frozen.

# A v1 review delivery and formal-release boundary

The owner has confirmed retaining existing protocol-v1 data, labels, splits and methods. The data's scientific version remains `a-clinical-protocol-v1-20261103-full-r1`. Delivery revision `a-v1-review-data-20261104-r1` annotates the audit with the explicitly confirmed owner record and links to the original audit hash. No clinical value or split has changed.

Two assets are prepared under draft Release tag `a-v1-review-delivery-20261104-r1`:

| Registry ID | Purpose |
|---|---|
| a-v1-review-data-20261104-r1 | Current cohort CSV/Parquet, annotated delivery audit, five original splits, source/license evidence,40,336-row raw receipt and C script logs |
| a-v1-full-source-20261104-r1 | Exact original full ZIP: raw archives, original audit, source materials, historical candidates and original checksum manifest |

Registry `status=prepared` and `publication_state=draft` mean uploaded review bytes are not a published formal data release. Standard `sync_artifacts.py fetch` refuses these entries intentionally. A remote transport receipt records actual draft/asset IDs and verified hashes; absent transport receipt means only local preparation. Draft assets require appropriate repository access and may not be visible to all readers.

## Download and restore for authorized review

Read the registry entry and the actual remote delivery receipt. With an appropriately authenticated GitHub CLI, save the registered asset API response as binary, verify SHA256, then restore using the existing safe extractor. A complete ready-to-run example after actual asset IDs are registered:

```powershell
@'
import hashlib, json, subprocess
from pathlib import Path
from scripts.sync_artifacts import extract_bundle
registry = json.loads(Path('artifacts/registry.json').read_text(encoding='utf-8'))
identifier = 'a-v1-review-data-20261104-r1'
entry = registry['bundles'][identifier]
assert entry['status'] == 'prepared' and entry['publication_state'] == 'draft'
assert entry.get('asset_api'), 'Draft has not been uploaded yet'
archive = Path('.artifact-cache') / entry['asset']
archive.parent.mkdir(parents=True, exist_ok=True)
with archive.open('wb') as stream:
    subprocess.run(['gh', 'api', entry['asset_api'], '-H', 'Accept: application/octet-stream'], stdout=stream, check=True, timeout=120)
assert hashlib.sha256(archive.read_bytes()).hexdigest() == entry['sha256']
extract_bundle(archive, Path('.artifact-cache/a-review'), entry['roots'], entry['sha256'])
print('Draft review bytes restored; no scientific freeze or formal publication asserted')
'@ | python -
```

For the complete original source, replace the ID with `a-v1-full-source-20261104-r1` and restore under `.artifact-cache/a-source`. The archive root is `T1_A_Day1_2026-11-03_v1_Rebuilt_Full`. Retain that original package; its original audit is not rewritten by the annotated current delivery audit. Use the full source plus A's raw checker for a complete raw-level replay.

## Required before formal publication

1. C reviews the newly supplied raw PSV receipt and records C's own acceptance/corrections; A's automated replay is not a new C human signature.
2. E with A/B/C records the retain-v1 decision and its finite-event conclusion limits, or another explicit decision. E's existing freeze deferral remains until E changes it.
3. PhysioNet clarifies the CC BY4.0 landing/view-license versus ODbL downloadable file discrepancy. Evidence and the not-sent English request are at `reviews/license/2026-11-04/`.
4. Actual release and metadata checks precede `published`; downstream B run and D C/E acceptance must name exact accepted data/audit/run hashes. No existing candidate run is silently renamed as formal.

The current Git tree carries code, aggregate evidence, source notices and this index. Original clinical files were removed from the current Git index and retained in ignored storage/versioned assets. Earlier commits still contain historical files; no force push or history rewrite was performed.

Actual draft URL: https://github.com/MarcoJIANG5203/BDDM-10/releases/tag/untagged-40b4eacb5c149f33ac90

Remote review-data asset709374298 (4,663,092bytes) and complete-source asset709375176 (50,674,324bytes) were both downloaded and restored with matching SHA256. See the transport receipt; this confirms bytes, not a published formal release.

A review PR: https://github.com/MarcoJIANG5203/BDDM-10/pull/3 (draft; recipient review pending).
