# 团队当前状态

更新日期：2026-11-04（北京时间）。A—E由组内对应到姓名；本页只记录已交付事实，详见[交付要求](HANDOFFS.md)。

当前统一仓库为[MarcoJIANG5203/BDDM-10](https://github.com/MarcoJIANG5203/BDDM-10)。代码、完整合成包及Release已迁移，新克隆32测试、完整产物恢复及2016指标行复核通过。成员改用新地址同步，原zsj-6/EI记录保留作历史证据。岗位实质进展不因迁移改变。

| 岗位 | 当前状态 | 证据 | 下一项交付 / 接收人 |
|---|---|---|---|
| A 数据与基础实验 | 待正式数据交付 | 已有[接口说明](../docs/A到B_数据交接说明.md)，暂无真实队列 | A-001：队列、五split、audit和时间标签核对；B接通，C核验，E定版本 |
| B 核心方法与实验 | 程序和合成验证完成；临床实验待A | [交付记录](../handoffs/B/2026-11-02.md)、[原算法验收](../reviews/B_最终验收.md) | B-002：先主种子S0再正式矩阵；C核算、D制图、E核公平性 |
| C 文献与独立核验 | 待成员提交文献及验收记录 | B代码已有独立复核，不替代C真实标签/指标核验 | C-001标签、C-002文献/投稿要求、C-003真实指标；交A/B/D/E |
| D 图表与论文 | D-001/D-001a/D-002准备已提交待验收：提纲、图表脚本、C/E签认门槛、引用核实（7条可引用，C-004已补R5）、英文稿骨架（结果全占位）、A数据Table 1/Fig 1 DRAFT、B候选DRAFT模型图 | [D-002准备记录](../handoffs/D/2026-11-04_D-002_prep.md)、[D-001a门槛记录](../handoffs/D/2026-11-04_D-001a_acceptance_gate.md)、[D-002就绪清单](../paper/d002_readiness.md)、[引用清单](../paper/references_checklist.md)、[BibTeX](../paper/references.bib)、[英文稿骨架](../paper/draft_v0.md)、[Table1/Fig1 DRAFT](../paper/inputs/a-data-v1-20261104-r1/provenance.json)、[B候选DRAFT](../paper/draft-runs/20261104T002604_e3a5a42b/provenance.json)、[合成验证provenance](../paper/validation/20261102T063118_fa76f8a8/provenance.json) | D-002正式结果仍需B-002正式run、C/E acceptance记录；不需要合并main；C核对数字/引用，E检查一致性 |
| E 统筹与整合 | 新仓库迁移及同步验证完成；持续统筹 | [新仓库交付记录](../handoffs/E/2026-11-02_repository_migration.md)；新Release已published；新克隆32测试和完整恢复核算通过 | E-001在BDDM-10维护状态/要求/版本，跟进11月3日数据门槛；全组检查各自范围 |

正式数据版本：**未发布**。可下载包仅为B合成验证，版本索引见[registry](../artifacts/registry.json)。当前临床实验前置项是A-001及C的标签核查；B收到有效队列后才能产真实主表，D再写结果。

每人随提交更新本岗位行，接收人验收后填结论，E处理跨岗位阻塞。每日21:00前记录“日期｜岗位｜完成事项｜仓库路径/版本｜问题｜下一步及预计时间”。
