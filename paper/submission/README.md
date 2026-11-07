# D-002 submission workspace — DRAFT

**Status: DRAFT / ACCEPTED_WITH_LIMITS / NOT SUBMITTED.** This is a review PDF, not the official submission. The C/E acceptance allows figures/tables and bounded descriptive writing, but explicitly **does not** accept a final manuscript, PDF, or submission.

## Files

| File | Purpose |
|---|---|
| `manuscript_draft.pdf` | DRAFT PDF generated 2026-11-07 from `paper/manuscript_draft.md` + formal figures/tables; 16 pages including figures and appendix tables. |
| `manuscript_draft.docx` | Editable Word version of the same DRAFT. |
| `manuscript_draft.html` | HTML source used to produce the PDF/DOCX. |
| `materials_manifest.csv` | SHA256/size of the PDF/DOCX/HTML/manuscript/S4 table/figures. |

## What is included

- Abstract, Introduction, Related Work, Methods, Experimental Setup, Results, Discussion, Conclusion, Statements, References.
- Formal Fig 1–6 and Tables 1, 2, 2b, 2c, 3b, 4, 5, S1–S3 as appendix tables.
- S4 source-tag fix from C PR #7: S4 point estimates cite S-005; S4 CI cites S-013 (`table2c_s4_primary_contrast.csv`).

## What is not done

1. **Official Word/LaTeX template and page limit**: this PDF uses a generic A4 layout, not the Workshop 3 template. The official template/page limit must be applied before submission.
2. **C/E final full-text consistency**: C has checked numbers/citations (0 numeric errors; S4 tag fixed), but the existing acceptance is `accepted_with_limits`, not final manuscript/PDF acceptance.
3. **A license**: PhysioNet CC BY 4.0 vs `LICENSE.txt` ODbL is unresolved; no new redistribution right is granted.
4. **Author/corresponding/AI disclosure**: to be confirmed by the group.
5. **Actual submission/receipt**: not performed; no claim of submission.

## Regenerate

```powershell
# HTML -> PDF/DOCX was generated with Microsoft Word COM.
# The authoritative source is paper/manuscript_draft.md;
# figures/tables are under paper/runs/20261105T055420_02d05b15/
# and paper/runs/20261105T055445_54dd08de/.
```

Do not submit this directory without the official template, C/E final consistency review, and A’s license decision.
