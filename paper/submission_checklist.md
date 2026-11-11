# Submission checklist — D-002

**2026-11-10 更新。** E-1 英文稿已交付审阅，引用库为 21 条，其中新增 13 条待 C 核查。待完成 C 对新增派生包的正式签认、E-1 复核、作者声明和会议模板 PDF。以下清单保留 11 月 6 日的提交检查项。[E-1 英文稿](manuscript_draft.md) · [改稿交接](../handoffs/D/2026-11-10_manuscript_revision_E1.md)

更新：2026-11-06。状态：**ACCEPTED_WITH_LIMITS / NOT SUBMITTED**。acceptance 允许图表/表与 bounded descriptive writing，但明确不是最终 manuscript/PDF 或投稿验收。

## 当前已有

| 材料 | 路径 | 状态 |
|---|---|---|
| 正式图表 Fig 1–6 | `paper/runs/20261105T055420_02d05b15/figures/` | ACCEPTED_WITH_LIMITS |
| 正式表 Table 1–5 | `paper/runs/20261105T055420_02d05b15/tables/` | ACCEPTED_WITH_LIMITS |
| 补充表 S1–S3 | `paper/runs/20261105T055445_54dd08de/tables/` | ACCEPTED_WITH_LIMITS |
| 完整英文稿草稿 | `paper/manuscript_draft.md` | DRAFT，需 C/E 最终一致性 |
| 来源索引 | `paper/source_index.md` | S-001–S-012 已绑定 |
| 引用 | `paper/references.bib`（21 条） | 新增 13 条待 C 核查 |
| Provenance | `.../provenance.json`、`.../provenance_supplement.json` | 已记录 acceptance/哈希 |

## 提交前必须完成

1. **C/E 最终一致性**：C 核对 Table 2/2b、S1–S3 与摘要数字；E 检查摘要—正文—图表—结论一致。当前没有“final manuscript/PDF accepted”记录。
2. **A 许可**：解决 PhysioNet CC BY 4.0 vs LICENSE.txt ODbL，或明确不重新分发原始数据。当前 UNRESOLVED。
3. **官方模板/页数**：按 Workshop 3 的 Word/LaTeX 模板排版；C-002 已记录格式背景，但最终模板/页数需在投稿前按官方页面复核。
4. **作者信息**：标题、作者顺序、单位、通讯作者、贡献声明、利益冲突、AI 使用披露，由组内确认。
5. **摘要/正文/图表一致**：使用 `source_index.md` 的 S-xxx；不得写稳定优势、临床安全或条件覆盖保证。
6. **补充材料**：S1–S3、复现命令、数据/代码可用性声明。
7. **投稿通道**：用户已确认 11-20 前投稿；正式入口/回执由提交人记录。未提交前不得声称已投稿。

## 不得提交的内容

- `paper/draft-runs/` 的任何 DRAFT。
- `paper/validation/` 的任何合成数字。
- `paper/inputs/` 的旧 DRAFT Table 1/Fig 1（正式 run 已重新生成）。
- 未核实的引用（R1 的 LOCF 不写；R5 只能按 modality-level 写）。
- 任何“分歧有效/安全/优于”结论。

## 当前阻塞

- C/E 最终全文一致性未签。
- A 许可冲突未解决。
- 官方模板/页数/作者信息未最终确认。
- 因此 `manuscript_draft.md` 不能作为提交版 PDF；需先完成上述 1–4。
