# 2026-11-06 · D · D-002_supplement_tables

| 字段 | 本记录 |
|---|---|
| 生产者 / 接收人 | D / C、E |
| 状态 | **ACCEPTED_WITH_LIMITS**（不是最终论文/PDF 验收） |
| 协议 / 数据 / run | v1；A `a-data-v1-20261104-r1`；补充 run `20261105T055445_54dd08de`；acceptance `reviews/acceptance/20261105T055445_54dd08de.json` |
| 文件 | `paper/runs/20261105T055445_54dd08de/tables/table_s1_rf.csv`、`table_s2_m_sensitivity.csv`、`table_s3_alpha005.csv`；`provenance_supplement.json` |
| 完成范围 | 从 accepted supplement run 生成 S1（RF S0/S2）、S2（M=5/10/20 S0）、S3（alpha=.05 S0/S2）；含 methods 与 B4−B2 batch/frozen 对比 |
| 未完成 / 阻塞 | 完整英文稿、提交版 PDF/材料；C/E 最终全文一致性；A 许可 |
| 验证证据 | acceptance 状态 `accepted_with_limits`；run manifest/artifact hashes 由脚本核对；输出 3 tables；`provenance_supplement.json` 记录 acceptance/inputs/outputs |
| 接收人检查点 | C 核对 S1–S3 的分母/区间；E 检查与正文一致；不得写优势/安全结论 |
| 接收人结论 | C/E 已签 accepted_with_limits；最终全文一致性未签 |
| 下一步 | 整合完整英文稿；生成提交版 PDF/材料 |

## 1. 表的内容

- **S1 RF**：`model=RF`, M=10, alpha=.1, S0/S2, c=.6 batch；B0 (M=1) 与 B1–B4（B1 target 空，B2–B4 c=.6）；每个场景加 B4−B2 batch/frozen 对比。
- **S2 M sensitivity**：`model=LR`, alpha=.1, S0, c=.6 batch；source_M=5/10/20；B0 (M=1) 与 B1–B4；每个 M 加 B4−B2 对比。
- **S3 alpha=.05**：`model=LR`, M=10, alpha=.05, S0/S2, c=.6 batch；B0 (M=1) 与 B1–B4；每个场景加 B4−B2 对比。

## 2. 关键限制

- B5/B6 不可用，S1–S3 无 B6−B5。
- MI 阳性覆盖 0/8；不能写阳性安全或条件覆盖保证。
- 内部仅 8 阳性；有限事件数结论。
- acceptance 允许图表/表和 bounded writing，不是最终投稿验收。

## 3. 验证

- acceptance 文件与 run manifest 匹配（脚本 `make_supplement_tables.py` 校验）。
- 3 张表 + `provenance_supplement.json` 生成。
- 未新增代码测试；脚本在真实 supplement run 上跑通。

## 4. 下一步

1. 整合完整英文稿（引用只用已核实条目）。
2. C 核对 Table 2/2b、S1–S3 与摘要；E 检查全文一致性。
3. 生成提交版 PDF 与材料清单。
4. A 许可解决或明确不重新分发原始数据。
