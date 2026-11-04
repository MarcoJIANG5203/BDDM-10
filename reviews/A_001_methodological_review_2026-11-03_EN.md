# Bounded A-001 methodological review — 2026-11-03 (UTC+08:00)

## Scope and provenance

This is an AI-assisted, same-family code/document review of the user-supplied A full-r1 package and downloaded B branch. It is not C's independent human review, A's personal signature, clinical adjudication, or E's freeze decision. The parent audit separately recomputes raw labels/features. This review read the B repository contract, unified protocol v1, handoff matrix, B diagnostic handoff, DIAGNOSIS.md, SUMMARY.md, A extraction code, and preserved source documentation. Source files were not changed and no model was trained.

## Protocol consistency

No concrete extraction defect was identified against the written v1 rules. The extractor checks finite integer consecutive ICULOS and monotone binary labels; requires actual hours 1–24; treats a first-record-positive as left censored without inventing its onset; restores observed 0-to-1 onset as the actual first-positive ICU hour plus six; excludes onset <=12; labels precisely 12 < onset <=24; takes the last nonmissing value from hours <=12 in the fixed 36-column order; and retains NaN. No adult-only restriction or undocumented clinical-value repair is added. A hospital alone receives the stratified 60/10/15/15 roles; all B records remain external. The five seeds are fixed rather than selected by trial performance. This consistency judgment is not proof of independent clinical ground truth or person-level deduplication.

## Event-count explanation

The following are descriptive re-tabulations of the supplied record_audit.csv, not a new raw replay:

| Site / sequential disposition | Records | Observed onset in (12,24] | Any positive label during released record |
|---|---:|---:|---:|
| A / included | 10174 | 57 | 730 |
| A / missing initial hours | 7497 | 93 | 574 |
| A / insufficient follow-up | 2665 | 184 | 486 |
| B / included | 13921 | 38 | 638 |
| B / missing initial hours | 1296 | 9 | 83 |
| B / insufficient follow-up | 4783 | 105 | 421 |

Of 1368 included records with any positive label, only 95 meet the target window; the remaining 1273 have observed onset after hour24. Included observed onsets range from hour21 to337 in both hospitals. There are 283 raw records with observable onset <=12 and 426 first-observation-positive records, but those records were already excluded by earlier initial-hour/follow-up steps. Therefore zero *sequential* early-onset/left-censor exclusion counts are not evidence that raw early/left-censored cases do not exist. Do not add overlapping reason counts to a mutually exclusive flow or interpret an unobserved/censored onset as known.

The strict cohort excludes records missing initial hours and those without the full follow-up. Its estimand is conditional on that selected cohort. It cannot be generalized to all ICU admissions. These counts explain arithmetic attrition, not the causal or clinical reasons for missingness, late onset, or model discrimination.

## B result boundaries

The supplied B documents explicitly restrict results to candidate 2026/S0/S4, acknowledge zero positive-class coverage, sparse events, B5/B6 unavailable due to six selection errors, and a paired external interval crossing zero. Their threshold algebra p >= 1-q is consistent with the stated score. No full five-seed/five-scenario result is established by this download. A should not relabel these descriptive results as a proven clinical mechanism, no-utility theorem, or safety guarantee. No independent recomputation of B's saved model or per-patient trial is claimed by this review.

## Concrete source-provenance correction needed

The stored PhysioNet landing page advertises Creative Commons Attribution 4.0, and sources/SOURCE_REGISTER.md row S5 repeats that claim, but the preserved sources/LICENSE.txt actually begins 'ODC Open Database License (ODbL)' and is named in the official root checksum file. This is an observed discrepancy between source artifacts, not an independent legal determination. Preserve the historical bytes and hashes; provide a dated provenance correction/discrepancy notice and ask the data custodian to resolve applicable redistribution terms before a formal publication assertion. Do not overwrite the original license or call this a verified CC-BY-only package. The dataset year2019 and final journal issue year2020 are correctly distinguished in the supplied references.

## A-owned next deliverable

1. Produce a dated A-001 technical verification record tied to the unchanged full-r1 package hash and raw/split hashes; identify automated work and leave the owner's personal review attestation explicitly pending unless the owner actually supplies it.
2. Give C the existing 10-positive/10-negative raw examples and boundary checks, with a blank acceptance record; never fill C's conclusions.
3. Give E the failed200/200/50 event gates and the B trial exposure disclosure. E with A/B/C must record whether to retain v1 with restricted conclusions or authorize a scientifically justified new version; a protocol change now is informed by viewed internal and external results.
4. Prepare immutable Release bytes and a truthful 'prepared, not published/not frozen' registry proposal. Do not automatically publish formal data before the stated reviews/decision, merge A clinical data into B, rewrite old manifests, or edit labels/splits to improve results.
5. Update the A status and a dated handoff without changing B/C/D/E acceptance states. Keep the original A package and B trial evidence immutable.
