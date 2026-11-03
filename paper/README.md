# D 岗位 · 论文与图表工作区

本目录由 **D（图表与论文负责人）** 维护。当前状态：**D-001 已提交待验收**；D-002（真实结果稿、提交版 PDF 与材料清单）要等 A-001、C-001/C-002 与 B-002 真实结果验收后才能完成。

## 目录约定

```text
paper/
  README.md              本说明
  outline.md             英文论文提纲、主张—证据台账、写作分工
  figure_list.md         图表清单、生成方式、来源与验收检查点
  source_index.md        正文每个数字的来源索引与核对规则
  runs/<run_id>/figures/ 真实临床 run 生成的论文图（D-002；当前未生成）
  runs/<run_id>/tables/  真实临床 run 生成的论文表（D-002；当前未生成）
  validation/<run_id>/   仅合成 run 的软件验证输出，全部带“非临床证据”水印
```

`paper/runs/` 只能由已验收的真实临床 run 生成。`paper/validation/` 中的任何数字都不得写入论文、摘要、投稿材料或对外汇报。

## 生成命令

真实临床 run（D-002；需要 B/C/E 已验收该 run）：

```powershell
python scripts/make_figures.py `
  --run-dir results/clinical/<run_id> `
  --cohort data/processed/cohort.parquet `
  --audit data/processed/cohort_audit.json
```

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
3. 输出表格、图、**图背后的数据 CSV**、`provenance.json`（输入/输出 SHA256、run、过滤器、脚本哈希）。
4. 不覆盖已有输出，除非显式 `--overwrite`；历史 run 不被改写。

依赖：`matplotlib==3.11.2` 已加入 `requirements.txt` / `requirements-lock.txt`（D-001 新增）。

## 数字规则

- 论文中每个数字必须能在 `source_index.md` 找到一条 `S-xxx`，并指向 `paper/runs/<run_id>/tables/` 或 `paper/validation/.../tables/` 的具体文件、列和过滤条件。
- 禁止手改结果数字；需要新数字时，从新的不可变 run 重新运行脚本。
- 摘要、正文、图表必须使用同一 run、同一过滤条件；C 核对数字与引用，E 检查全文一致性。
- 合成结果只能用于软件与流程验证，不能支持临床结论、效果方向、覆盖率保证或安全声明。

## 当前交付（D-001）

| 交付 | 路径 | 状态 |
|---|---|---|
| 图表/表格脚本 | `scripts/make_figures.py` | 已提交待验收 |
| 论文提纲 | `paper/outline.md` | 已提交待验收 |
| 图表清单 | `paper/figure_list.md` | 已提交待验收 |
| 来源索引 | `paper/source_index.md` | 已提交待验收 |
| 合成 run 验证输出 | `paper/validation/20261102T063118_fa76f8a8/` | 仅软件验证，非临床证据 |
| 交付记录 | `handoffs/D/2026-11-04_D-001.md` | 已提交待验收 |
