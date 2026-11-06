# 5 November 2026 · A · Daily technical delivery closeout

## Material Passport

- Artifact: A delivery-maintenance and source-verification record.
- Protocol/data: v1 / `a-data-v1-20261104-r1`; source clinical version `a-clinical-protocol-v1-20261103-full-r1`.
- Producer: A delivery automation on behalf of the previously confirmed owner Yicheng Jiang / MarcoJIANG5203; no new personal clinical-review declaration.
- Evidence scope: fresh release downloads and identity/count checks; fixed-commit observations of B/C/D/E records; official-source license recheck.
- Status: A daily technical supplement submitted for receiver review through the existing A branch/PR; recipient acceptance and external actions remain as listed below.

| Field | Record |
|---|---|
| Date/time basis | 5 November 2026, Asia/Hong_Kong (UTC+08:00); live checks completed at 2026-11-05T22:44:41.711836+08:00 |
| Receivers | B, C, D and E, within their existing review scopes |
| Formal A delivery | [Published version](https://github.com/MarcoJIANG5203/BDDM-10/releases/tag/a-data-v1-20261104-r1), SHA-256 `feb69777e7c03c51d580808182a4702a2b3991a0edd552ec4d0dcbf7b1a7129c` |
| Original full source | [Published source archive](https://github.com/MarcoJIANG5203/BDDM-10/releases/tag/a-v1-source-archive-20261104-r1), SHA-256 `a57d16dc5432b2e2518bc5f754b706c60de7b94d3fb496870687d4a564770cb1` |
| A branch / review | `a/resource-researching-and-pre-processing`; [existing PR #3](https://github.com/MarcoJIANG5203/BDDM-10/pull/3); main is not merged by this delivery |
| Evidence | [Fresh verification](../../reviews/A_daily_delivery_verification_2026-11-05.json), [recipient evidence index](../../reviews/A_recipient_receipt_index_2026-11-05.json) |
| Recipient conclusion | B/E existing technical receipts are cited below; conclusions on this new daily supplement are for the receiving members to record |

## Completed today

1. Downloaded the actual formal asset again: 4,666,169 bytes, exact registered SHA-256, 52 members. Checked the eight frozen CSV/Parquet/audit/split identities and the byte-identical embedded A freeze record. Recomputed 24,095 included records, A 10,174/57 positive and B 13,921/38 positive, plus five disjoint/complete site-correct splits with 1,525/8 internal test and 13,921/38 external records per seed.
2. Downloaded the complete original full source again: 50,674,324 bytes, exact original SHA-256 and valid archive CRC. Both raw ZIPs are present with 20,336/20,000 PSV members. The existing safe recovery command was also executed in a separate local cache and all 125 original package manifest entries matched. Added [current C source-replay instructions](../../collaboration/A_SOURCE_REPLAY_2026-11-05.md); the historical draft-channel description must not be used as the current download route. This is not a new raw-PSV onset rerun or C personal replay.
3. Indexed existing receiver records instead of creating new signatures: [B input receipt](https://github.com/MarcoJIANG5203/BDDM-10/blob/75ccea28e591376e163a2bc6199666c0b6e6acd4/reviews/B_formal_A_receipt_2026-11-04.json) reports eight identities/ten loader checks; [E](https://github.com/MarcoJIANG5203/BDDM-10/blob/75ccea28e591376e163a2bc6199666c0b6e6acd4/handoffs/E/2026-11-05_E-001_formal_v1_integration.md) explicitly receives A technical delivery and continuing-v1 scope, while disclosing its prior same-chat B involvement. The new E record is separately dated and does not rewrite the historical A approval provenance.
4. Captured the newer [C006](https://github.com/MarcoJIANG5203/BDDM-10/blob/b6d7c3293db1c2263bc6ae4a25ce3e178415aeb8/handoffs/C/2026-11-05_%E6%AD%A3%E5%BC%8Frun%E7%8B%AC%E7%AB%8B%E5%A4%8D%E6%A0%B8.md) submission: C reports independent arithmetic/protocol verification of both formal runs, 900+240 metric rows and 30+48 paired intervals with zero failures. This updates the older E/D snapshot saying C had not yet submitted. B/E reception of C006 and joint result acceptance remain separate. [D's Fig5](https://github.com/MarcoJIANG5203/BDDM-10/blob/33f85eac390dbaae8a1caa2f0a77a855dbbd101d/handoffs/D/2026-11-05_D-002_fig5.md) is still a draft.
5. Re-fetched the official dataset page, versioned license page, downloadable license, checksum and contact page. The CC BY 4.0 web versus ODbL file discrepancy persists. Prepared an updated [English clarification request](../../reviews/license/2026-11-05/clarification_request_EN.md) and a local unsent email file. The owner explicitly instructed not to send for now; status is **USER_DEFERRED_NOT_SENT**. No email was sent and no official reply was supplied.
6. Corrected obsolete current-state A documentation and recorded today's work in STATUS/CHANGELOG. Scientific data, algorithms, labels, five splits, the formal audit/freeze record, registry and existing Release assets remain unchanged.

## Remaining actions and responsibility

| Action | Owner / boundary |
|---|---|
| Preserve the prepared clarification request; do not send for now | User explicitly deferred sending. The license remains unresolved; sending is not a pending approval request in this task. Any future response must be genuine and retained with its provenance. |
| Receive C006 and record exact accepted run/manifest/scope | B/E, using C's actual new conclusion; A does not sign C/E result acceptance. |
| Decide whether C needs an additional raw-level independent replay | C/E; A has now supplied and verified the published source route, not C's credentials or own replay. |
| Produce final accepted figures/manuscript from the accepted runs | D after the scoped C/E acceptance record. At the checked B/C/D/main commits there are no `reviews/acceptance/` files. |

The unchanged precision limits remain 57/38 positives versus the protocol's 200/200 thresholds, and 8 internal positives versus 50. MI positive-set coverage of zero, B5/B6 unavailability and no stable disagreement advantage are reported by B/C, not recomputed by A in this maintenance task. Do not interpret input consistency as clinical safety or verified medical ground truth.

## Verification and preservation

The task-local evidence collection performed fresh binary downloads, frozen hash/count checks and official HTTPS captures. No model was trained; no full scientific pytest suite was rerun for this documentation-only change. Historical 56-test results remain historical. Byte-preservation and link checks for the final supplement are recorded separately in `reviews/A_daily_document_checks_2026-11-05.json`.

2026-11-05 | A | Reverified formal and full-source deliveries; indexed B/E receipts and new C006; corrected recovery instructions; refreshed official license evidence and prepared correspondence | This handoff, daily receipts and existing immutable Releases | Official license clarification and C/E result decision remain open | Receiver review can proceed immediately; no estimate is asserted for an external custodian reply. This entry was recorded after the routine 21:00 reporting target; it is not backdated as an on-time submission.
