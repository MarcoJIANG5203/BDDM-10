# Overleaf LaTeX project — D-002

**Status: ready for Overleaf review; author/template confirmation still required.**

This folder is a self-contained Overleaf project built from the final E-1 manuscript
(`paper/manuscript_draft.md`, C-011 signed) and the accepted run
`20261105T055420_02d05b15`.

## Files

| File | Purpose |
|---|---|
| `main_ieee.tex` | IEEEtran conference wrapper (recommended if the venue uses IEEE Xplore/IEEEtran) |
| `main_acm.tex` | ACM `acmart` sigconf wrapper (alternative if the venue uses ACM ICPS) |
| `body.tex` | Shared body: Introduction to Conclusion and Statements |
| `references.bib` | 21 verified references (C-011) |
| `figures/fig_reliability.pdf` | Final three-panel reliability figure (S-022/S-023) |
| `supplementary.tex` | Supplementary Tables S1–S3 + post hoc random reference; compile separately |
| `README.md` | This file |

## Overleaf upload

1. In Overleaf: **New Project → Upload Project** and upload a zip of this folder,
   or create a blank project and copy the files preserving the `figures/` path.
2. Set the main document to `main_ieee.tex` (or `main_acm.tex`).
3. Compile with pdfLaTeX. Both wrappers share `body.tex`.
4. Compile `supplementary.tex` separately for the supplementary PDF.

If the official template is neither IEEEtran nor acmart, replace the wrapper's
`\documentclass` with the official class and keep `body.tex`/`references.bib`.

## Before submission

- **Author block**: `main_ieee.tex`/`main_acm.tex` contain placeholders. Fill in
  author names, affiliations, emails, corresponding author and contributions.
- **Official template/page limit**: the ICBDDM/Workshop 3 template and exact page
  limit must be confirmed by C/E or the chairs. The public site has been
  inconsistent; do not assume IEEEtran/acmart is the final template.
- **AI disclosure / ethics / data availability**: confirm the statements in
  `body.tex` with the group and institutional policy.
- **C/E final consistency**: C has signed the numbers/references and content
  review (C-011); the existing acceptance remains `accepted_with_limits`, not a
  final manuscript/PDF acceptance. A license conflict remains unresolved.
- **No internal markers**: `[S-xxx]`, `content-review/` links and "Review draft"
  wording have been removed from the LaTeX body. Do not re-insert them.

## Writing/norm notes used

- IEEE-style abstract 150–250 words, no citations; keywords after abstract.
- Define abbreviations at first use; use a zero before decimals; escape `%`;
  use `\cite{}` and a `.bib`; number equations/tables/figures consecutively.
- Two-column IEEEtran: wide Table 1/2 and Figure 1 use `table*`/`figure*`.
- Keep the result framing as a limited/negative reliability evaluation: no
  stable disagreement advantage, conditional increment not estimable, positive
  coverage 0/8 and 0/38, external acceptance drift.
