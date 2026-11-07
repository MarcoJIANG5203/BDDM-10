# 2026-11-07 · D · D-002_C_review_response

| 字段 | 本记录 |
|---|---|
| 生产者 / 接收人 | D / C、E |
| 状态 | 已修正 C PR #7 的唯一来源标注缺口；数值未变 |
| 输入 | C `handoffs/C/2026-11-07_稿件数字与引用核验.md`；main `87b4be4e`；正式 run `20261105T055420_02d05b15` |
| 文件 | `paper/manuscript_draft.md`、`paper/results_accepted_with_limits.md`、`paper/source_index.md`、`paper/figure_list.md`；新增 `paper/runs/20261105T055420_02d05b15/tables/table2c_s4_primary_contrast.csv`、`table2c_provenance.json` |
| 完成范围 | ① S4 点估计/接受错误改为引 S-005（`table3_scenario_per_seed.csv`）；② 新增 S-013 与 S4 对比表（含 bootstrap 区间）；③ 摘要、§5.2、results_accepted 同步改引 |
| 未完成 / 阻塞 | 最终模板/PDF、C/E 最终全文一致性 scope、A 许可；这些不由本修正解决 |
| 验证证据 | C 报告 0 数值错误/7 引用正确；S4 数字与 `metrics.csv`/`bootstrap_differences.csv` 一致；table2c 记录 source/acceptance hashes；输出 hash `33f7c62b...` |
| 接收人检查点 | C 确认 S4 标注已改为 `[S-005, S-013]`；E 复核来源索引；数值不得改 |
| 接收人结论 | 由 C/E 填 |
| 下一步 / 时间 | 官方模板排版、最终 PDF/材料；A 许可 |

## 1. C 的发现

C PR #7：

- 全部数字 0 错误；7/7 引用正确。
- 唯一问题：S4 数字被标为 `[S-002, S-003]`，但这两个源只含 S0 内部数据；S4 的 95% 区间没有 S-xxx 溯源。

## 2. D 的修正

- 摘要 S4 句：`[S-005, S-013]`。
- §5.2 S4 段：`[S-005, S-013]`。
- `results_accepted_with_limits.md` 同步。
- 新增 `table2c_s4_primary_contrast.csv`：
  - B2 8352 accepted / 24 errors / selective_risk 0.00287356；
  - B4 8352 / 21 / 0.00251437；
  - B4−B2 batch −0.0003591954，CI [−0.0010775862, 0.0003591954]；
  - frozen +0.0001749671，CI [−0.0001712176, 0.0005194703]。
- `table2c_provenance.json` 记录 metrics/bootstrap/acceptance 的 SHA256 与输出 hash。
- `source_index.md` 新增 S-013；`figure_list.md` 新增 Table 2c。
- 数值没有改动；只改来源标注并补可追溯表。

## 3. 未完成

- 官方 Word/LaTeX 模板、页数、作者信息。
- C/E 最终全文一致性（现有 acceptance 不含 final manuscript/PDF）。
- A 许可。
- 提交版 PDF/材料与回执。
