# 论文数字来源索引（D-001 模板）

更新：2026-11-04。维护：D。核对：C（数字/引用），E（全文一致性）。

**规则：** 摘要、正文、图表标题和结论中的每个数字都必须有本文件的一条 `S-xxx`。没有来源条目的数字不得写入论文。数字只从 `paper/runs/<run_id>/tables/` 或 `paper/validation/.../tables/` 的 CSV 读取；不得从聊天、截图、旧稿或合成 run 复制到临床稿。

**当前临床 run：** 无。以下条目的 `run_id` 与路径为占位；真实结果到位后由 D 更新、C 核对、E 签字。当前唯一可用的合成验证见本文件末尾 `V-001`，它不能替代任何 `S-xxx`。

## 索引表

| ID | 论文位置 / 用途 | 输出文件 | 过滤条件 | 列 / 计算 | 状态 |
|---|---|---|---|---|---|
| S-001 | 摘要/结果：每院样本量、阳性数、阳性率、纳排 | `tables/table1_cohort_summary.csv` | A-001 验收队列；按 `site`，Overall 行可选 | `n`, `positives`, `base_rate`, `included`, `excluded` | PENDING-A/C-001 |
| S-002 | 摘要/Table 2：B0–B6 的选择性风险、接受比例、危险漏放、阴性残余风险、覆盖 | `tables/table2_main_results.csv` | `split_seed=2026, model=LR, M=10, source_M=10, alpha=0.1, scenario=S0, imputation_batch=0, selection_mode=batch`；B0 `M=1,target`空；B1 `M=10,target`空；B2–B6 `target=0.6` | 对应列；B0/B1 的 target 为空；状态取 `method_status.csv` | PENDING-B/C |
| S-003 | 摘要/结果：主效应 B4−B2（c=0.60） | `tables/table2b_primary_contrasts.csv`；原始 `bootstrap_differences.csv` | 同 S-002；`comparison=B4-B2, target_acceptance=0.6, selection_mode=batch` | `risk_difference`, `ci_low`, `ci_high`, `valid`, `invalid` | PENDING-B/C |
| S-004 | 摘要/结果：条件增量 B6−B5（c=0.60） | 同上 | `comparison=B6-B5`，其余同 S-003 | 同上 | PENDING-B/C |
| S-005 | 结果：S0–S4 的 B4−B2、B6−B5 稳定性 | `tables/table3_scenario_per_seed.csv`、`table3_scenario_summary.csv` | `model=LR, M=10, source_M=10, alpha=0.1, imputation_batch=0, target_acceptance=0.6, selection_mode=batch`；全部种子 × S0–S4 | 每种子差值；汇总 `mean/min/max/seeds` | PENDING-B/C |
| S-006 | 结果/Table 4：原始集合覆盖（总体/类别/缺失分层） | `tables/table4_coverage_strata.csv`；原始 `coverage_strata.csv` | 主种子、S0、alpha=0.1、batch=0；MI `M=10`，median `M=1` | `n`, `covered`, `coverage`；空集计入分母 | PENDING-B/C |
| S-007 | 结果/Fig 5：分歧五分位错误率、每格 n、Wilson 区间 | `tables/fig5_disagreement_data.csv` | `patient_predictions.csv` 主条件；`method=B4, target=0.6, selection_mode=batch`；仅 singleton；`p_std` 五等分 | `n`, `errors`, `error_rate`, `ci_low`, `ci_high`, `p_std_min/max` | PENDING-B/C |
| S-008 | 结果/Table 5：跨测试插补批次的三状态不一致率 | `tables/table5_stability.csv` | `stability.csv` 主种子、S0、alpha=0.1；B0 `M=1,target`空；B1–B6 `target=0.6`；batch/frozen | `mean_disagreement`, `min`, `max`, `pairs` | PENDING-B/C |
| S-009 | 结果/Table 1b：特征缺失率（总体/分院） | `tables/table1_feature_missingness.csv` | A-001 队列；按协议 36 个特征；`site` 分组 | `overall_missing`, `missing_site_<site>`, `n` | PENDING-A/C-001 |
| S-010 | 补充表 S1–S3：RF、M=5/20、alpha=0.05 | 补充 run 的 `metrics.csv` / `bootstrap_differences.csv` | `model=RF, scenario=S0/S2`；或 `source_M=5/20, scenario=S0`；或 `alpha=0.05, model=LR, M=10` | 与主表同列；报告区间与分母 | PENDING-B/C |
| S-011 | 方法/结果：容量不足、实际接受比例、候选池大小 | `tables/table2_main_results.csv`；`metrics.csv` | 同 S-002 | `pool_size`, `capacity_shortfall`, `accepted`, `acceptance` | PENDING-B/C |
| S-012 | 方法/结果：AUROC/AUPRC、阳性基率、事件数 | `tables/table2_main_results.csv` | 同 S-002 | `auroc`, `auprc`, `base_rate`, `positives`, `n` | PENDING-B/C |

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

## 合成验证条目（不得用于论文）

| ID | 用途 | 位置 | 限制 |
|---|---|---|---|
| V-001 | 证明 `make_figures.py` 的过滤、哈希校验、制图和水印链路可运行 | `paper/validation/20261102T063118_fa76f8a8/` | 合成 run；120 人中仅 11 个单元素集合，c=0.4/0.6/0.8 全部容量不足；B2–B6 整池接受，排序无区分；**不得写入论文、摘要、投稿材料或对外汇报** |

## 待办

- [ ] D-002 启动前：A-001/C-001/B-002 验收完成，C-002 文献与会议规则锁定。
- [ ] 生成真实 run 后：更新 S-001–S-012 的 run_id、路径、哈希。
- [ ] C 独立核对 S-002/S-003/S-004 与摘要；E 核对摘要—正文—图表—结论一致。
- [ ] 补充 run 生成后：新增 S-010 对应表 S1–S3，不把补充结果升格为主结论。
