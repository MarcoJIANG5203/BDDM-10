# Challenge 2019 v1.0.0: licensing evidence and clarification status

## Material Passport

- Origin skill: academic-research-suite
- Bounded workflow: source verification for A's 2026-11-04 closeout
- Task date and timezone: 2026-11-04, Asia/Hong_Kong (UTC+08:00)
- Verification scope: public repository licensing statements, downloaded license integrity, and public contact channel
- Evidence finding: OFFICIAL_SOURCE_CONFLICT_REPRODUCED
- Case status: **PENDING_NO_CUSTODIAN_RESPONSE**
- External request status: **DRAFT_ONLY_NOT_SENT**
- Clinical or institutional approval: not sought or asserted by this verification

## Findings

The current official versioned landing page identifies the license as CC BY 4.0. Its version-specific license display also serves CC BY 4.0 text. The downloadable `LICENSE.txt` in the same versioned project instead begins with **ODC Open Database License (ODbL)**. The downloadable file matches the official checksum and the immutable A source copy exactly. This verifies the discrepancy; it does not establish which license governs the dataset or any derived file.

| Evidence | Public source | Live retrieval | Observation |
|---|---|---|---|
| Landing-page Access/License field | [Version 1.0.0 landing page](https://physionet.org/content/challenge-2019/1.0.0/) | 2026-11-04 19:54:58–19:55:01 +08:00; HTTP 200 | Displays CC BY 4.0 and links to the version-specific license display. |
| License display reached through that field | [Version-specific license display](https://physionet.org/content/challenge-2019/view-license/1.0.0/) | 2026-11-04 19:55:38–19:55:39 +08:00; HTTP 200 | Heading and license body are CC BY 4.0. |
| Project file | [Official LICENSE.txt](https://physionet.org/files/challenge-2019/1.0.0/LICENSE.txt) | 2026-11-04 19:54:58–19:55:06 +08:00; HTTP 302 then 200 | 25,815 bytes; ODbL text; official redirect goes to the PhysioNet public S3 object. |
| Integrity reference | [Official SHA256SUMS.txt](https://physionet.org/files/challenge-2019/1.0.0/SHA256SUMS.txt) | 2026-11-04 19:54:58–19:55:00 +08:00; HTTP 200 | Lists the same SHA-256 hash for `LICENSE.txt` as computed from the downloaded bytes. |
| Current public contact route | [PhysioNet About / Contact us](https://physionet.org/about/#contact-us) | 2026-11-04 19:54:58–19:55:00 +08:00; HTTP 200 | Publishes `contact@physionet.org` as the route to the PhysioNet team. Mailbox delivery and response availability were not tested. |

The final license-object URL recorded in the HTTPS receipt is:

`https://physionet-open.s3.amazonaws.com/challenge-2019/1.0.0/LICENSE.txt`

The corresponding author contact on the dataset landing page is login-gated. No login was attempted. The landing page also retains `challenge@physionet.org` in historical 2019 competition instructions. Its current activity was not established; the current general contact route above is the proposed recipient. The old community-forum link redirected to a generic Google Groups page in the web reader, so a functioning dataset-specific request form or forum was not verified.

## Source integrity and original A comparison

The current license SHA-256, the value listed for it in the official checksum file, and the immutable A source license SHA-256 all equal:

`bcdfcd4f31c790e30fb645dc36414907172405897adff329ad379eed85d12017`

The current checksum file SHA-256 equals the immutable A checksum copy:

`ba025b2702297c202592a01d4eb31532938a2f6b3aab3afe125e75a52bd281a5`

The original A landing-page snapshot hash differs from the newly retrieved live HTML. A live HTML page may contain changing metadata or presentation; this hash difference is not evidence of a license change. Both the current live license statements and the preserved file evidence are recorded independently. No historical relicensing event, effective date, or custodian intent is inferred.

The server's license-object `Last-Modified` header was 2024-03-04, while the checksum response reported 2019-08-05. These are transport metadata, not evidence of a license-grant date. The dataset remains version 1.0.0, published 2019-08-05; its version DOI is [10.13026/v64v-d857](https://doi.org/10.13026/v64v-d857). The retrieval date is 2026-11-04 and must not be substituted for the dataset's publication year.

## Disposition

**PENDING_NO_CUSTODIAN_RESPONSE.** No external message, email, form, or forum post was sent. No custodian answer exists within this task. The clarification request is saved separately for an authorized person to send. It asks the repository to identify the applicable license and provide a version-specific correction or explanation, including applicability to derived feature tables.

No license has been selected, overwritten, or synthesized. This report grants no permission to redistribute data and does not change the current v1 protocol, freeze status, or any A/C/E signoff. Source verification can be completed while the licensing resolution remains pending.

## Receipts and local evidence

- `source_receipts.json`: requested and final URLs, UTC and Hong Kong retrieval timestamps, HTTP statuses and redirect chain, response metadata, byte counts, SHA-256 hashes, and read-only original-copy comparisons.
- `official_landing_page.html`: live versioned dataset landing page.
- `official_view_license.html`: live version-specific license display.
- `official_LICENSE.txt`: exact live downloaded license bytes.
- `official_SHA256SUMS.txt`: exact live official checksum bytes.
- `official_about_contact.html`: public contact-channel evidence.
- `clarification_request_draft.md`: ready-to-send English request; no attachments or send action.
- `capture_license_evidence.py`: reproducible public-source capture script; no clinical-data upload or messaging functions.

The immutable A files read for comparison are `sources/LICENSE.txt`, `sources/official_SHA256SUMS.txt`, and `sources/physionet_dataset_page.html` under `outputs/T1_A_Day1_2026-11-03_v1_Rebuilt_Full/`. They were not modified.

## Verification limits

All five substantive evidence sources are first-party repository records. The clinical-study evidence hierarchy is inapplicable to repository licensing metadata; no clinical evidence grade or journal-quality verdict is implied. The records are not independent legal determinations. This task identified a source conflict and verified file integrity, not the legal priority of the conflicting statements, model-data license effects, institution-owned decisions, or the custodian's intentions.

The web reader could not retrieve the license after its S3 redirect. A separate authenticated-by-HTTPS, anonymous direct GET successfully retrieved the bytes; its receipt records that separate transport outcome. No authentication credentials, patient records, manuscript text, or unpublished research files were sent to an external service.
