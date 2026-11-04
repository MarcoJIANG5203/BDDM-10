# 团队当前状态

更新日期：2026-11-04（北京时间）。A—E由组内对应到姓名；本页只记录已交付事实，详见[交付要求](HANDOFFS.md)。

当前统一仓库为[MarcoJIANG5203/BDDM-10](https://github.com/MarcoJIANG5203/BDDM-10)。代码、完整合成包及Release已迁移，新克隆32测试、完整产物恢复及2016指标行复核通过。成员改用新地址同步，原zsj-6/EI记录保留作历史证据。岗位实质进展不因迁移改变。

| 岗位 | 当前状态 | 证据 | 下一项交付 / 接收人 |
|---|---|---|---|
| A 数据与基础实验 | Owner confirmed retain-v1 technical handoff; full raw PSV receipt and exposed evidence completed; review delivery prepared, formal freeze pending | [A closeout](../handoffs/A/2026-11-04_A-001_closeout_EN.md), [owner record](../reviews/A_owner_confirmation_2026-11-04.json), [raw receipt](../reviews/A_raw_psv_receipt_2026-11-04.json) | C reviews raw receipt; E coordinates retain-v1 limited conclusions; official license clarification and formal data publication pending |
| B 核心方法与实验 | B reports completed pre-freeze five-seed/five-scenario candidate; PR1 closed unmerged; no formal B-002 acceptance | [Pinned B handoff](https://github.com/MarcoJIANG5203/BDDM-10/blob/f15fbc8d72f4a11a365d1e0eb4fd1e9749f19925/handoffs/B/2026-11-04_v1_candidate_full_matrix.md) | Preserve candidate evidence; formal rerun follows actual data freeze and recipient review |
| C 文献与独立核验 | C submitted20-case labels,14 boundary assertions and900-metric/30-interval candidate checks; new A raw receipt supplied for review | [Pinned C handoff](https://github.com/MarcoJIANG5203/BDDM-10/blob/f2eb560a29423f05af6a06b08ef777c975f4e92f/handoffs/C/2026-11-04_时间边界与候选指标核验.md) | C reviews raw receipt and records own conclusion; B/E receive C-003; citation/venue evidence remains C/E responsibility |
| D 图表与论文 | D PR2 open with figure/acceptance gate and English skeleton; no accepted clinical figures/results | [D PR2](https://github.com/MarcoJIANG5203/BDDM-10/pull/2), [A methods input](../paper/inputs/A_data_and_preprocessing_v1_EN.md) | D-002 waits for formal data/run and C/E acceptance; A does not bypass the figure gate |
| E 统筹与整合 | E recorded deferral of formal freeze; A now explicitly chooses existing v1 with finite-event limitations | [Pinned E decision](https://github.com/MarcoJIANG5203/BDDM-10/blob/f15fbc8d72f4a11a365d1e0eb4fd1e9749f19925/handoffs/E/2026-11-04_precision_freeze_review.md) | E with A/B/C records joint continuation/freeze scope; source license and submission evidence still need actual resolution |

Formal data: **not published or frozen**. Existing v1 full-r1 is retained by explicit owner instruction; the review delivery annotates audit metadata only. A57/B38/internal-test8 remain below200/200/50. Current Git clinical files move to versioned draft review assets; formal publication awaits C/E and official license clarification. See [review delivery](A_DATA_REVIEW_2026-11-04.md).

每人随提交更新本岗位行，接收人验收后填结论，E处理跨岗位阻塞。每日21:00前记录“日期｜岗位｜完成事项｜仓库路径/版本｜问题｜下一步及预计时间”。

Current A delivery note (2026-11-04): owner confirmation is recorded; no endpoint/label/split/method changes. Metadata is prepared for a draft Release, not published formal data. Other-role statements above are pinned source observations, not A granting their acceptance.
