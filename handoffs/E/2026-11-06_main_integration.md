# 2026-11-06 · E · main 团队进度整合

用户授权将截至本次同步的各岗位交付汇入 `main`。成员可在工作区干净时执行 `git switch main` 和 `git pull --ff-only origin main`。查看[团队状态](../../collaboration/STATUS.md)、[正式图表](../../paper/runs/20261105T055420_02d05b15/)、[数字来源](../../paper/source_index.md)和[两周安排](2026-11-06_workshop3_two_week_plan.md)。

| 来源 | 已整合的交付 |
|---|---|
| A · `68ce9d1` | [数据交接](../A/2026-11-05_A_daily_closeout_EN.md)、队列构建脚本、测试、特征字典、聚合核验、冻结及[来源恢复说明](../../collaboration/A_SOURCE_REPLAY_2026-11-05.md)。A 当前快照相对于原 main 的 57 项新增文件均按原 Git blob 核对。早期 A 提交曾含原始数据及患者表，因此按当前文件快照导入；A 原分支保留原历史。 |
| B · `4de19ab` | 实验实现、配置、已发布数据及运行版本登记、两份正式运行摘要和[限定范围接受记录](../../collaboration/ACCEPTANCE_INDEX.md)。 |
| C · `b6d7c32` | [标签、文献、时间边界和正式运行复核交接](../C/)，以及独立核验脚本。 |
| D · `e5549e3` | 正式 Fig 1–6、主表和绘图脚本、来源索引及[结果段落](../../paper/results_accepted_with_limits.md)。原草稿、软件验证材料和正式产物各保留在原目录。[D 本次交付](../D/2026-11-06_D-002_formal_run.md) |
| E · `b8b6c9e` | [模拟审稿意见](2026-11-06_workshop3_reviewer_assessment.md)与[两周建议](2026-11-06_workshop3_two_week_plan.md)。新增配对人数属于描述性预查，供 C 独立核对。 |

**核验。** 整合环境运行 `python -m pytest -q`，73 项通过。核对 A 正式包和八项冻结身份、B 正式运行包、固定合成 ZIP 与 registry SHA256；两份正式运行的接受记录匹配各自原始 manifest。D 主运行 27 份图表文件及其对接受记录、绘图脚本的哈希引用均已核对。Windows 工作区旧接受文件曾有 CRLF 换行；按原 Git blob 检出后与 D 记录一致。版本库现为这两份 JSON 显式保留原字节。[数据与产物同步](../../collaboration/DATA_SYNC.md)

**下一步。** D 补充表 S1–S3、英文全文及最终 PDF；C 核数字和引用，E 核全文一致性，组内提交人留存实际投稿回执。此记录登记集成与可读性，科学接受仍以既有接收方记录为准。
