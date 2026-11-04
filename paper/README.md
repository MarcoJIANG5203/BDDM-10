# D 岗位 · 论文与图表工作区

本目录由 **D（图表与论文负责人）** 维护。当前状态：**D-001 / D-001a 已提交待验收；D-002 准备（引用核实 + 英文稿骨架 + Table 1/Fig 1 DRAFT）已提交待验收**。D-002 的真实结果稿、提交版 PDF 与材料清单要等 A-001、C-001/C-002 与 B-002 真实结果验收后才能完成。**D-002 的前置条件与 A/B/C/E 待办见 [d002_readiness.md](d002_readiness.md)；引用范围见 [references_checklist.md](references_checklist.md)。**

## 目录约定

```text
paper/
  README.md              本说明
  outline.md             英文论文提纲、主张—证据台账、写作分工
  figure_list.md         图表清单、生成方式、来源与验收检查点
  source_index.md        正文每个数字的来源索引与核对规则
  references_checklist.md  引用核实清单（C-002 输入 → D 可引用范围）
  references.bib         只含已核实元数据的 7 条 BibTeX（含 C-004 补出的 R5）
  draft_v0.md            英文稿骨架；结果全部占位，不可提交
  d002_readiness.md      D-002 门槛、A/B/C/E 待办与当前数据状态
  acceptance_record_template.json  C/E 签认记录模板（模板本身不是验收）
  inputs/<data_version>/ A 正式数据生成的 Table 1 / Fig 1 DRAFT（仅数据描述，待接收）
  runs/<run_id>/figures/ 真实临床 run 生成的论文图（D-002；当前未生成）
  runs/<run_id>/tables/  真实临床 run 生成的论文表（D-002；当前未生成）
  validation/<run_id>/   仅合成 run 的软件验证输出，全部带“非临床证据”水印
```

`paper/runs/` 只能由已验收的真实临床 run 生成。`paper/inputs/` 的 Table 1/Fig 1 是 **DRAFT_PENDING_ACCEPTANCE**，在 A PR 合并、C/E 接收前不得作为最终论文表。`paper/validation/` 中的任何数字都不得写入论文、摘要、投稿材料或对外汇报。

## 生成命令

真实临床 run（D-002；需要 B/C/E 已验收该 run，且 `reviews/acceptance/<run_id>.json` 已签认）：

```powershell
python scripts/make_figures.py `
  --run-dir results/clinical/<run_id> `
  --cohort data/processed/cohort.parquet `
  --audit data/processed/cohort_audit.json
```

签认记录默认从 `reviews/acceptance/<run_id>.json` 读取；也可以显式指定：

```powershell
python scripts/make_figures.py `
  --run-dir results/clinical/<run_id> `
  --cohort data/processed/cohort.parquet `
  --audit data/processed/cohort_audit.json `
  --acceptance-file reviews/acceptance/<run_id>.json
```

签认记录必须匹配 run 的 `manifest_sha256`、`run_id`、协议与数据版本，并包含 C/E 的姓名、日期、决定和证据路径；模板见 `paper/acceptance_record_template.json`。

正式 A 数据 Release 的 Table 1 / Fig 1（D-002 数据描述；输出强制标 DRAFT，等 A PR 合并与 C/E 接收）：

```powershell
python scripts/make_cohort_tables.py `
  --release-zip dist/artifacts/a-data-v1-20261104-r1.zip `
  --expected-sha256 feb69777e7c03c51d580808182a4702a2b3991a0edd552ec4d0dcbf7b1a7129c
```

默认输出 `paper/inputs/a-data-v1-20261104-r1/`；脚本校验 release ZIP、audit、cohort、5 份 splits、site/阳性数、role 互斥完备，并在 `provenance.json` 写 `DRAFT_PENDING_ACCEPTANCE`。

仅合成 run 的软件验证（D-001；输出强制加水印）：

```powershell
python scripts/make_figures.py `
  --run-dir results/synthetic/20261102T063118_fa76f8a8 `
  --cohort data/synthetic/cohort.csv `
  --audit data/synthetic/cohort_audit.json `
  --validation-only
```

脚本行为：

1. 读取 `manifest.json`，要求 `run_status=completed`，并逐个核对 `artifact_hashes`；任何文件缺失或被改动都会拒绝生成。
2. 合成 run 未加 `--validation-only` 时直接报错，不允许生成论文图；加了该参数后，所有输出带 “SYNTHETIC SOFTWARE VALIDATION — NOT CLINICAL EVIDENCE” 水印。
3. 真实临床 run 必须有 C/E 签认记录（默认 `reviews/acceptance/<run_id>.json`）；缺少、哈希不匹配、run_id/协议/数据版本不符或 C/E 未签，脚本都直接拒绝。候选 run 和未冻结 run 不能生成论文图。
4. 输出表格、图、**图背后的数据 CSV**、`provenance.json`（输入/输出 SHA256、run、过滤器、脚本哈希、acceptance 记录）。
5. 不覆盖已有输出，除非显式 `--overwrite`；历史 run 不被改写。

依赖：`matplotlib==3.11.2` 已加入 `requirements.txt` / `requirements-lock.txt`（D-001 新增）。

## 数字规则

- 论文中每个数字必须能在 `source_index.md` 找到一条 `S-xxx`，并指向 `paper/runs/<run_id>/tables/` 或 `paper/validation/.../tables/` 的具体文件、列和过滤条件。
- 禁止手改结果数字；需要新数字时，从新的不可变 run 重新运行脚本。
- 摘要、正文、图表必须使用同一 run、同一过滤条件；C 核对数字与引用，E 检查全文一致性。
- 合成结果只能用于软件与流程验证，不能支持临床结论、效果方向、覆盖率保证或安全声明。

## 当前交付（D-001 / D-001a / D-002 准备）

| 交付 | 路径 | 状态 |
|---|---|---|
| 图表/表格脚本 | `scripts/make_figures.py` | 已提交待验收 |
| A 数据 Table 1/Fig 1 脚本 | `scripts/make_cohort_tables.py` | 已提交待验收 |
| 正式 A 数据 Table 1/Fig 1 DRAFT | `paper/inputs/a-data-v1-20261104-r1/` | DRAFT，待 A PR 合并/C/E 接收 |
| 临床 run 签认门槛（D-001a） | `scripts/make_figures.py`、`paper/acceptance_record_template.json` | 已提交待验收 |
| 论文提纲 | `paper/outline.md` | 已提交待验收 |
| 图表清单 | `paper/figure_list.md` | 已提交待验收 |
| 来源索引 | `paper/source_index.md` | 已提交待验收 |
| 引用核实清单 | `paper/references_checklist.md` | 7/7 可引用；R5 由 C-004 补出；R1 LOCF 不写 |
| 已核实 BibTeX | `paper/references.bib` | 7 条，含 `wong2026mc2` |
| 英文稿骨架 v0 | `paper/draft_v0.md` | 结果全占位；不可提交 |
| D-002 就绪清单与 A/B/C 待办 | `paper/d002_readiness.md` | 已提交待验收 |
| 合成 run 验证输出 | `paper/validation/20261102T063118_fa76f8a8/` | 仅软件验证，非临床证据 |
| D-001 交付记录 | `handoffs/D/2026-11-04_D-001.md` | 已提交待验收 |
| D-001a 交付记录 | `handoffs/D/2026-11-04_D-001a_acceptance_gate.md` | 已提交待验收 |
| D-002 准备记录 | `handoffs/D/2026-11-04_D-002_prep.md` | 已提交待验收 |
| D-002 引用更新（C-004） | `handoffs/D/2026-11-04_D-002_prep_C004.md` | 已提交待验收 |
| D-002 Table 1/Fig 1 DRAFT | `handoffs/D/2026-11-04_D-002_cohort_tables.md` | 已提交待验收 |
