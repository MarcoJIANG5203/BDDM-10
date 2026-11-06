# B-002正式技术输入结果

## 2026-11-06 接受范围

[C-006原结论](../../handoffs/C/2026-11-05_正式run独立复核.md)已由[B接收](../../handoffs/B/2026-11-06_B_C006_receipt.md)及[E范围决定](../../handoffs/E/2026-11-06_E-001_C006_result_scope.md)登记。两份`reviews/acceptance/<run_id>.json`为`accepted_with_limits`，绑定原manifest；准许D从原run生成可追溯图表和有限事件数描述性稿件。C结论仅转录原有条件范围，非新增C签名。下文“生产者交付/验收分开”原则不变，实际接收以本轮独立记录为准。

输入版本`a-data-v1-20261104-r1`，协议v1。本目录保存正式输入上的两个新run的小型摘要与原字节表格；完整逐患者结果、p_m、模型、mask和抽样种子通过`b-clinical-v1-20261104-r1`版本包交付。生产者计算/核验与C/E独立验收分开记录，不将旧候选验收转移到新run。

[完整结果Release](https://github.com/MarcoJIANG5203/BDDM-10/releases/tag/b-clinical-v1-20261104-r1)已上传为待审pre-release，实际下载SHA256及空目录恢复复核通过，见[发布回执](../../reviews/B_formal_release_2026-11-04.json)。包SHA256 `2328d26682a39ccb895553d3cee3dc6dd11bd6506c41a5a0ac0f5d49890e8426`。

- [主模型五种子五场景](20261105T055420_02d05b15/SUMMARY.md)
- [RF/M/alpha补充](20261105T055445_54dd08de/SUMMARY.md)
- [队列计数](cohort_counts.csv)、[两院36输入缺失统计](cohort_missingness.csv)
- [B交接与接收方检查点](../../handoffs/B/2026-11-04_B-002_formal_v1.md)
- [正式输入接收](../../reviews/B_formal_A_receipt_2026-11-04.json)、[逐患者与区间重算证据](../../reviews/B_formal_verification_2026-11-04.json)

每份run摘要列出首批60%目标容量的全部预定场景；同目录原始小表保留全部容量、batch/frozen模式、分层覆盖、稳定性、模型状态和参数。不同seed复用同一队列，不合并为独立样本。总体覆盖不能替代阳性保护；事件数、B5/B6不可用、有限或零阳性覆盖均须如实报告。候选历史保留在`reports/candidate-trials/`。

恢复命令及资产API回退见[DATA_SYNC](../../collaboration/DATA_SYNC.md)。正式结果图稿须由C/E记录与manifest SHA256相绑定的新run接受范围；本目录和Release上传本身不构成该签认。
