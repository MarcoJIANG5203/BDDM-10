# A-001 independent recipient review requests

Prepared 2026-11-03. Blank fields below are requests, not completed decisions.

## C-001: independent label and case review

Use the preserved full A package's `data/processed/review_10_positive_10_negative.csv` and its 20 raw files under `data/processed/review_cases/`. The package contains 10 positive and 10 negative cases, balanced by site. Keep patient-level working notes in the data bundle or an ignored local review workspace; the Git handoff may summarize findings without copying the clinical table.

For each case, independently record: raw file/hash; actual ICU start/hour continuity/duplicate check; observed first-positive label or censoring; recovered onset only when identifiable; inclusion/exclusion; expected `(12,24]` label; feature timestamps <=12 and preserved missingness; discrepancy and resolution. Check onset 12/13/24/25, no observed positivity, and first-record positivity separately. Do not copy A/B automatic PASS as a personal conclusion.

Reviewer/name: PENDING. Date: PENDING. Independently read cases: PENDING. Findings: PENDING. Acceptance/required corrections: PENDING.

## C-003: B result and diagnosis review

Restore B's candidate Release using `collaboration/DATA_SYNC.md` and verify the registered SHA256. The supplied branch ZIP contains small summaries, not the complete clinical run. Independently check q/k, class-set coverage, accepted errors/leakage denominators, actual six selection errors, paired intervals, and batch stability. A's current audit confirms exact A input linkage but does not reproduce those full patient-level metrics.

Reviewer/name: PENDING. Date: PENDING. Source run/hash: PENDING. Findings and decision: PENDING.

## E with A/B/C: precision, task, and freeze decision

Facts for decision: A 10,174/57; B 13,921/38; test 1,525/8. Gates200/200/50 fail. B's viewed candidate reports zero MI positive coverage internally/externally, B5/B6 unavailable, and no stable incremental advantage. This describes a candidate and does not establish a clinical explanation.

Decision options to adjudicate, not auto-selected:

1. Retain v1 with explicit finite-event, cohort-selection, model-performance and conclusion limitations, and record whether continued formal experiments are scientifically useful.
2. Develop a new, substantively justified protocol with an incremented version and a new A/C verification cycle. Record all prior internal/external result exposure, preserve v1, and distinguish exploratory redevelopment from independent confirmation. Do not merely change a version string or search for favorable labels/splits.
3. Pause formal model experiments while resolving task feasibility and source metadata.

Chosen option/reason: PENDING. Participants and actual names: PENDING. Date: PENDING. Endpoint/eligibility/config changes: PENDING. Prior result exposure acknowledgment: PENDING. Data release/freeze authorized: PENDING. C review reference: PENDING. License metadata disposition: PENDING.

These options confer no freeze or publication authority by themselves. No deadline or acceptance is invented on behalf of another member.
