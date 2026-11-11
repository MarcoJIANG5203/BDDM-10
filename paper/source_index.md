# 论文数字来源索引（D-001 模板）

## 2026-11-10 新增内容的写作入口

本轮新增 S-020–S-027，供[写作交接](WRITING_BRIEF_2026-11-10.md)限定的描述性初稿使用。S-013 留给 D 已交付的 S4 来源修正，本文不覆盖其编号。原 S-001–S-012 与两份 run 接受记录保持原范围。

本节源目录为 `paper/content-review/20261110-r1/`，文件 SHA256 和完整过滤条件见其中 `provenance.json`；[C 岗复算记录](../reviews/C_content_review_2026-11-10.json)绑定该 provenance，另见[本轮核验](../reviews/E/2026-11-10_drafting_readiness.json)。本节扩展下文早期允许取数目录，且只允许这一已核字节包。状态为**技术复算通过、E 已确定可写范围；新增派生包的 C 本人正式签认待记录，终稿待审**，不标为新增独立接受。

| ID | 用途 | 文件（相对上述目录） | 过滤条件 / 列 / 边界 |
|---|---|---|---|
| S-020 | 分院纳排和主划分事件数 | `cohort_flow.csv`、`split_event_counts.csv` | `site=A/B/Total` 按 `stage`；窗口事件使用 `target_transition_proxy`，同时列 `target_onset_beyond_released_hours`；划分 `seed=2026`、按 `role`；源 A `f0f0bfc`，全量原始重放沿用 C-010 |
| S-021 | 基础模型背景 | `base_model_context.csv` | `split_seed=2026, source_M=10, alpha=.1, imputation_batch=0`；LR S0/S4，RF S4；`estimate, ci_low, ci_high, n, positives`；点估计 C-010 已核，区间是 B 生产者计算，本轮核复制一致性 |
| S-022 | S0/S4 覆盖、接受和漏放主图 | `capacity_coverage_release.csv`、`fig_reliability.pdf` | 主 run `20261105T055420_02d05b15`；2026/LR/M=source_M=10/alpha=.1/batch=0/c=.6；B2/B4，`selection_mode=batch/frozen`；`accepted/n`、`accepted_false_negative/positives`、`covered/n`、`positive_covered/positives` |
| S-023 | 主比较及固定阈值的配对区间 | `risk_contrasts.csv` | 同 S-022；`comparison=B4-B2`；率差及上下限乘 100 写为百分点；各 1000 有效重采样，batch 重排选 K，frozen 保持冻结规则 |
| S-024 | 阳性患者双向处置变化 | `paired_positive_disposition.csv` | 同 S-022 的 batch 模式；`both_missed,b2_only_missed,b4_only_missed,both_rejected`；S0 1/0/1/6，S4 18/6/3/11；不要把净差当作全部处置变化 |
| S-025 | 原始集合到处置的分流 | `set_to_decision_counts.csv` | 主条件，固定 batch 模式；按 `scenario,method,set_type` 列阳性人数及接受/拒识计数；集合覆盖与后续动作分开解释；S4 所有 38 个阳性为阴性单元素 |
| S-026 | 外院固定阈值五种子稳定性 | `external_frozen_stability.csv` | `scenario=S4, selection_mode=frozen`；2026–2030，B2/B4；`accepted, acceptance, accepted_false_negative`；五种子同一外院队列，范围为划分敏感性 |
| S-027 | P1 随机排序探索性参照 | `random_reference.csv` | 固定主候选池、同 K、均匀无放回；期望和中央 95% 范围；事后补充，不能称患者抽样区间或显著性检验 |

## 既有正式运行来源 · 2026-11-06

更新：2026-11-06。维护：D。核对：C（数字/引用），E（全文一致性）。

**规则：** 摘要、正文、图表标题和结论中的每个数字都必须有本文件的一条 `S-xxx`。没有来源条目的数字不得写入论文。数字只从 `paper/runs/<run_id>/tables/`、`paper/inputs/<data_version>/tables/` 或 `paper/validation/.../tables/` 的 CSV 读取；不得从聊天、截图、旧稿或合成 run 复制到临床稿。临床 run 必须同时有 `reviews/acceptance/<run_id>.json`；`provenance.json.acceptance` 记录该文件的路径、SHA256、C/E 签认状态。

**当前临床 run：** `20261105T055420_02d05b15`（主矩阵）+ `20261105T055445_54dd08de`（补充）。两份 acceptance 均为 `accepted_with_limits`：允许 D 从该 run 重新生成图表/表和**有限描述性写作**，但明确**不是最终论文/PDF 或投稿验收**；不得写安全/优势结论。来源见 `reviews/acceptance/20261105T055420_02d05b15.json`（B 分支）与 `provenance.json.acceptance`。

## 索引表

| ID | 论文位置 / 用途 | 输出文件 | 过滤条件 | 列 / 计算 | 状态 |
|---|---|---|---|---|---|
| S-001 | 摘要/结果：每院样本量、阳性数、阳性率、纳排 | `paper/runs/20261105T055420_02d05b15/tables/table1_cohort_summary.csv` | run `20261105T055420_02d05b15`；A data release `a-data-v1-20261104-r1`；按 `site` | `n`, `positives`, `base_rate`, `included`, `excluded` | ACCEPTED_WITH_LIMITS |
| S-002 | 摘要/Table 2：B0–B6 的选择性风险、接受比例、危险漏放、阴性残余风险、覆盖 | `paper/runs/20261105T055420_02d05b15/tables/table2_main_results.csv` | `split_seed=2026, model=LR, M=10, source_M=10, alpha=0.1, scenario=S0, imputation_batch=0, selection_mode=batch`；B0 `M=1,target`空；B1 `M=10,target`空；B2–B6 `target=0.6` | 对应列；B0/B1 target 为空；B5/B6 unavailable | ACCEPTED_WITH_LIMITS |
| S-003 | 摘要/结果：主效应 B4−B2（c=0.60） | `paper/runs/20261105T055420_02d05b15/tables/table2b_primary_contrasts.csv` | 同 S-002；`comparison=B4-B2, target_acceptance=0.6, selection_mode=batch` | `risk_difference`, `ci_low`, `ci_high`, `valid`, `invalid` | ACCEPTED_WITH_LIMITS |
| S-004 | 摘要/结果：条件增量 B6−B5（c=0.60） | 同上 | `comparison=B6-B5` | **NA：B5/B6 unavailable（6 errors/1,012 correct）** | ACCEPTED_WITH_LIMITS (NA) |
| S-005 | 结果：S0–S4 的 B4−B2 稳定性 | `paper/runs/20261105T055420_02d05b15/tables/table3_scenario_per_seed.csv`、`table3_scenario_summary.csv` | `model=LR, M=10, source_M=10, alpha=0.1, imputation_batch=0, target_acceptance=0.6, selection_mode=batch`；全部种子 × S0–S4 | 每种子差值；汇总 `mean/min/max/seeds` | ACCEPTED_WITH_LIMITS |
| S-006 | 结果/Table 4：原始集合覆盖（总体/类别/缺失分层） | `paper/runs/20261105T055420_02d05b15/tables/table4_coverage_strata.csv` | 主种子、S0、alpha=0.1、batch=0；MI `M=10`，median `M=1` | `n`, `covered`, `coverage`；空集计入分母；y=1 覆盖 0/8 | ACCEPTED_WITH_LIMITS |
| S-007 | 结果/Fig 5：分歧五分位错误率、每格 n、Wilson 区间 | `paper/runs/20261105T055420_02d05b15/tables/fig5_disagreement_data.csv` | `patient_predictions.csv` 主条件；`method=B4, target=0.6, selection_mode=batch`；仅 singleton；`p_std` 五等分 | `n`, `errors`, `error_rate`, `ci_low`, `ci_high`；1,388 单元素/4 错误 | ACCEPTED_WITH_LIMITS |
| S-008 | 结果/Table 5：跨测试插补批次的三状态不一致率 | `paper/runs/20261105T055420_02d05b15/tables/table5_stability.csv` | `stability.csv` 主种子、S0、alpha=0.1；B0 `M=1,target`空；B1–B6 `target=0.6`；batch/frozen | `mean_disagreement`, `min`, `max`, `pairs` | ACCEPTED_WITH_LIMITS |
| S-009 | 结果/Table 1b：特征缺失率（总体/分院） | `paper/runs/20261105T055420_02d05b15/tables/table1_feature_missingness.csv` | run `20261105T055420_02d05b15`；A data release；36 个特征；`site` 分组 | `overall_missing`, `missing_site_<site>`, `n` | ACCEPTED_WITH_LIMITS |
| S-010 | 补充表 S1–S3：RF、M=5/20、alpha=0.05 | `paper/runs/20261105T055445_54dd08de/tables/table_s1_rf.csv`、`table_s2_m_sensitivity.csv`、`table_s3_alpha005.csv` | 补充 run `20261105T055445_54dd08de`；RF S0/S2；M=5/10/20 S0；alpha=.05 S0/S2；c=.6 batch | 方法行 + B4−B2 batch/frozen 对比；报告区间与分母 | ACCEPTED_WITH_LIMITS |
| S-011 | 方法/结果：容量不足、实际接受比例、候选池大小 | `paper/runs/20261105T055420_02d05b15/tables/table2_main_results.csv`；`metrics.csv` | 同 S-002 | `pool_size`, `capacity_shortfall`, `accepted`, `acceptance` | ACCEPTED_WITH_LIMITS |
| S-012 | 方法/结果：AUROC/AUPRC、阳性基率、事件数 | `paper/runs/20261105T055420_02d05b15/tables/table2_main_results.csv` | 同 S-002 | `auroc`, `auprc`, `base_rate`, `positives`, `n` | ACCEPTED_WITH_LIMITS |

## 计算口径（防止分母错误）

| 指标 | 分子 | 分母 | 备注 |
|---|---|---|---|
| 接受比例 | 接受人数 | 全部测试患者 N | 不是候选池人数 |
| 选择性风险 | 接受且预测错误人数 | 接受人数 | 零分母 NA |
| 危险漏放 | 真实阳性、接受且预测阴性人数 | 全部真实阳性人数 | 不是接受人数 |
| 阴性接受残余风险 | 真实阳性、接受且预测阴性人数 | 接受且预测阴性人数 | 零分母 NA |
| 集合覆盖 | 真实标签在原始共形集合中的人数 | 全部测试患者 | 含空集；筛选后的安全不等于此覆盖 |
| 主效应 B4−B2 | B4 选择性风险 | — | 同一 c、同一候选池、同一 K；B4−B2<0 表示 B4 风险更低 |
| 条件增量 B6−B5 | B6 选择性风险 | — | 同规则选择集训练；事件不足时报告不可用 |

## 版本与 provenance

每条 `S-xxx` 在填数时必须同时记录：

- `run_id`、`manifest_sha256`、`data_version`、`protocol_version`；
- 生成命令与 `paper/.../provenance.json` 路径；
- 输出文件 SHA256（脚本已写入 `provenance.json.outputs`）；
- 核对人（C）与核对日期；E 的一致性签字。

脚本生成的 `provenance.json` 是来源链的一部分；论文附录/补充材料可以引用它，但不要把哈希写进正文。

## DRAFT formal B-002 条目（不得用于论文）

以下条目来自 **正式 B-002 run**，但**没有 C/E acceptance**，只用于 D-002 草稿排版与流程检查，**不是**论文数字来源。正式 `S-xxx` 仍等 C/E acceptance。

| ID | 用途 | 文件 | run / 状态 | 限制 |
|---|---|---|---|---|
| D-101 | Table 2 主结果草稿 | `paper/draft-runs/20261105T055420_02d05b15/tables/table2_main_results.csv` | `20261105T055420_02d05b15` / `DRAFT_CANDIDATE_NOT_ACCEPTED` | B5/B6 unavailable；不得进论文 |
| D-102 | Table 2b 主对比草稿 | `.../tables/table2b_primary_contrasts.csv` | 同上 | 仅 B4-B2；无 B6-B5 |
| D-103 | Table 3 scenario 草稿 | `.../tables/table3_scenario_per_seed.csv`、`table3_scenario_summary.csv` | 同上 | 方向不稳定；不得写成效果结论 |
| D-104 | Table 4 coverage 草稿 | `.../tables/table4_coverage_strata.csv` | 同上 | 阳性覆盖 0/8；不能替代安全声明 |
| D-105 | Table 5 stability 草稿 | `.../tables/table5_stability.csv` | 同上 | 无 C/E acceptance |
| D-106 | Fig 2/3/4/5/6 草稿 | `.../figures/fig2_*`、`fig3_*`、`fig4_*`、`fig5_*`、`fig6_*` | 同上 | 带 DRAFT 水印；Fig 5 为稀疏诊断（1,388 单元素预测/4 错误） |
| D-107 | Fig 5 聚合数据 | `.../tables/fig5_disagreement_data.csv` | 同上 | 仅描述性；患者级过滤文件未入库，见 `FIG5_SOURCE.md` |

## DRAFT candidate 条目（历史，不得用于论文）

以下候选条目保留作历史；当前最近产物是上面的正式 B-002 DRAFT。

| ID | 用途 | 文件 | run / 状态 | 限制 |
|---|---|---|---|---|
| D-001 | Table 2 主结果草稿（候选） | `paper/draft-runs/20261104T002604_e3a5a42b/tables/table2_main_results.csv` | `20261104T002604_e3a5a42b` / `DRAFT_CANDIDATE_NOT_ACCEPTED` | 候选预冻结；不得进论文 |
| D-002 | Table 2b 主对比草稿（候选） | `.../tables/table2b_primary_contrasts.csv` | 同上 | 仅 B4-B2；无 B6-B5 |
| D-003 | Table 3 scenario 草稿（候选） | `.../tables/table3_scenario_per_seed.csv`、`table3_scenario_summary.csv` | 同上 | 方向不稳定 |
| D-004 | Table 4 coverage 草稿（候选） | `.../tables/table4_coverage_strata.csv` | 同上 | 阳性覆盖 0/8 |
| D-005 | Table 5 stability 草稿（候选） | `.../tables/table5_stability.csv` | 同上 | 候选预冻结 |
| D-006 | Fig 2/3/4/6 草稿（候选） | `.../figures/fig2_*`、`fig3_*`、`fig4_*`、`fig6_*` | 同上 | 带 DRAFT 水印；Fig 5 跳过 |

## 合成验证条目（不得用于论文）

| ID | 用途 | 位置 | 限制 |
|---|---|---|---|
| V-001 | 证明 `make_figures.py` 的过滤、哈希校验、制图和水印链路可运行 | `paper/validation/20261102T063118_fa76f8a8/` | 合成 run；120 人中仅 11 个单元素集合，c=0.4/0.6/0.8 全部容量不足；B2–B6 整池接受，排序无区分；**不得写入论文、摘要、投稿材料或对外汇报** |

## 待办

- [ ] D-002 启动前：A-001/C-001/B-002 验收完成，C-002 文献与会议规则锁定。
- [ ] 生成真实 run 后：更新 S-001–S-012 的 run_id、路径、哈希。
- [ ] C 独立核对 S-002/S-003/S-004 与摘要；E 核对摘要—正文—图表—结论一致。
- [ ] 补充 run 生成后：新增 S-010 对应表 S1–S3，不把补充结果升格为主结论。
