# 图表清单与来源索引（D-001）

更新：2026-11-04。负责人：D。验收：C 核对数字/引用，E 检查全文一致性。

**当前状态：** 只有合成 run 的软件验证输出，位于 `paper/validation/20261102T063118_fa76f8a8/`。这些图不是临床结果，不得进入论文。真实临床图表要等 A-001、C-001 和 B-002 验收后，用 `scripts/make_figures.py` 从 `results/clinical/<run_id>` 生成到 `paper/runs/<run_id>/figures/` 与 `paper/runs/<run_id>/tables/`。

## 状态图例

| 标记 | 含义 |
|---|---|
| `READY-QA` | 脚本已生成并通过合成 run 验证；仅软件证据 |
| `PENDING-A` | 依赖 A-001 正式队列/审计 |
| `PENDING-B` | 依赖 B-002 已验收临床 run |
| `PENDING-C` | 依赖 C-001/C-002 独立核验/文献 |
| `ACCEPTED` | 接收人已签字；数字可用于论文 |

## 主图

| ID | 英文图题（工作版） | 回答的问题 | 数据来源与过滤 | 脚本输出 | 状态 |
|---|---|---|---|---|---|
| Fig 1 | Feature missingness in the delivered cohort | 哪些输入缺失最多？两院是否不同？ | A-001 `cohort` + `cohort_audit.json`；按 `site` 分组；特征列取协议 36 项 | `figures/fig1_missingness.{pdf,png}`；`tables/fig1_missingness_data.csv` | PENDING-A |
| Fig 2 | Risk vs realized acceptance; B4 − B2 risk difference | 在相同目标容量下，分歧排序是否比置信度排序错误更少？ | `metrics.csv`：`split_seed=2026, model=LR, M=10, source_M=10, alpha=0.1, scenario=S0, imputation_batch=0, selection_mode=batch`；B0 用 `M=1` 且 `target_acceptance` 为空；B2/B3/B4 取 c=0.4/0.6/0.8；B4−B2 区间取 `bootstrap_differences.csv` 同条件 `comparison=B4-B2` | `figures/fig2_risk_acceptance.{pdf,png}`；`tables/fig2_risk_acceptance_data.csv`；`tables/fig2_contrast_data.csv` | READY-QA / PENDING-B |
| Fig 3 | Scenario robustness (mean, min–max) | B4−B2、B6−B5 在自然缺失、额外缺失、化验缺失、外院是否同向？ | `metrics.csv`：`model=LR, M=10, source_M=10, alpha=0.1, imputation_batch=0, target_acceptance=0.6, selection_mode=batch`，全部 5 个种子 × S0–S4 | `figures/fig3_scenarios.{pdf,png}`；`tables/fig3_scenario_data.csv` | READY-QA / PENDING-B |
| Fig 4 | Coverage by stratum (S0, primary seed) | 原始共形集合的边际覆盖如何？按类别/缺失分层呢？ | `coverage_strata.csv`：主种子、S0、alpha=0.1、batch=0；MI 取 `M=10`，median 取 `M=1`；分层顺序见脚本 `STRATA_ORDER` | `figures/fig4_coverage.{pdf,png}`；`tables/fig4_coverage_data.csv` | READY-QA / PENDING-B |
| Fig 5 | Error by disagreement quintile; singleton predictions | 分歧高的患者是否更容易错？这是描述性证据，不是规则 | `patient_predictions.csv`：主种子、S0、alpha=0.1、batch=0、`method=B4`、`target_acceptance=0.6`、`selection_mode=batch`；仅 singleton（`set_0 xor set_1`）；按 `p_std` 五等分；误差=singleton 预测≠真实标签 | `figures/fig5_disagreement.{pdf,png}`；`tables/fig5_disagreement_data.csv` | READY-QA / PENDING-B |
| Fig 6 | Test-time stability (S0, c=0.60) | 同一患者跨 5 批测试插补的三状态决策是否稳定？ | `stability.csv`：主种子、S0、alpha=0.1；B0 取 `M=1,target_acceptance` 空；B1–B6 取 `target_acceptance=0.6`；分别汇总 batch/frozen | `figures/fig6_stability.{pdf,png}`；`tables/fig6_stability_data.csv` | READY-QA / PENDING-B |

## 主表

| ID | 表题（工作版） | 内容 | 数据来源与过滤 | 脚本输出 | 状态 |
|---|---|---|---|---|---|
| Table 1a | Cohort summary | 每院/总体的 n、阳性数、阳性率、纳排计数、数据版本 | A-001 `cohort.parquet`/`cohort.csv` + `cohort_audit.json`；`y_true` 求和；`exclusion_counts` 来自审计 | `tables/table1_cohort_summary.csv` | PENDING-A |
| Table 1b | Feature missingness | 36 项输入总体及分院缺失率 | 同上；按 `features` 列 | `tables/table1_feature_missingness.csv` | PENDING-A |
| Table 2 | Main selective-risk results | B0–B6 的接受人数/比例、选择性风险、危险漏放、阴性残余风险、覆盖、AUROC/AUPRC、候选池大小、容量不足标记 | `metrics.csv` 主条件（见 Fig 2）；B0 `M=1,target_acceptance` 空；B1 `M=10,target_acceptance` 空；B2–B6 `M=10,target_acceptance=0.6`；状态取 `method_status.csv` | `tables/table2_main_results.csv` | READY-QA / PENDING-B |
| Table 2b | Primary contrasts | B4−B2、B6−B5 的风险差、95% CI、有效/无效重抽 | `bootstrap_differences.csv` 主条件 c=0.6；batch 与 frozen 各一行 | `tables/table2b_primary_contrasts.csv` | READY-QA / PENDING-B |
| Table 3a | Scenario per-seed | 每种子 × S0–S4 的 B2/B4/B5/B6 风险及差值 | `metrics.csv` c=0.6 batch，5 seeds × 5 scenarios | `tables/table3_scenario_per_seed.csv` | READY-QA / PENDING-B |
| Table 3b | Scenario summary | 每个场景的 B4−B2、B6−B5 均值、最小、最大、种子数 | 由 Table 3a 聚合 | `tables/table3_scenario_summary.csv` | READY-QA / PENDING-B |
| Table 4 | Coverage strata | MI 与 median 的总体/类别/缺失分层覆盖、n、covered | `coverage_strata.csv` 主种子 S0；MI `M=10`，median `M=1` | `tables/table4_coverage_strata.csv` | READY-QA / PENDING-B |
| Table 5 | Stability | B0–B6 在 batch/frozen 下的三状态不一致率均值、最小、最大、对数 | `stability.csv` 主种子 S0；B0 `M=1,target_acceptance` 空；B1–B6 c=0.6 | `tables/table5_stability.csv` | READY-QA / PENDING-B |
| Table S1 | RF robustness (S0/S2) | 随机森林复核的方向与区间 | 补充 run 的 `metrics.csv`/`bootstrap_differences.csv`；过滤 `model=RF` | 待扩展脚本（同一过滤原则） | PENDING-B |
| Table S2 | M sensitivity (M=5/20, S0) | 插补次数变化下的主效应 | 补充 run；`source_M=5/20` | 待扩展脚本 | PENDING-B |
| Table S3 | Alpha sensitivity (0.05) | 更严格共形阈值下的主效应 | 补充 run；`alpha=0.05` | 待扩展脚本 | PENDING-B |

## 来源索引规则

1. `paper/source_index.md` 为每个正文/摘要数字分配 `S-xxx`；表和图数据文件是唯一读数位置。
2. 生成器同时写出 `provenance.json`：run_id、manifest SHA256、输入/输出 SHA256、过滤器、脚本 SHA256。缺少 provenance 的图表不得进入论文。
3. 脚本核对 `manifest.json` 的全部 `artifact_hashes`；任何文件被改动、缺失或 run 未完成都会报错。
4. 合成 run 必须带 `--validation-only`，所有输出带 “SYNTHETIC SOFTWARE VALIDATION — NOT CLINICAL EVIDENCE” 水印；未加参数会被拒绝。
5. 数字只允许从 CSV 读入排版；不得从聊天、截图或旧稿复制。C 独立核对表 2/2b 与摘要数字；E 核对摘要—正文—图表—结论一致。
6. 零分母写 NA 并保留分子/分母；图不把 NA 画成 0。脚本对 n=0 的分层标注 `n=0`。

## 当前合成验证输出（READY-QA）

`paper/validation/20261102T063118_fa76f8a8/` 由以下命令生成（证据见同目录 `provenance.json`）：

```powershell
python scripts/make_figures.py `
  --run-dir results/synthetic/20261102T063118_fa76f8a8 `
  --cohort data/synthetic/cohort.csv `
  --audit data/synthetic/cohort_audit.json `
  --validation-only
```

该合成 run 的重要限制（必须写进交付记录，不得写进论文结果）：

- 120 名内部测试患者中只有 11 个单元素共形集合，目标 c=0.4/0.6/0.8 都超过候选池；
- 因此 B2–B6 都接受整个候选池，排序策略没有区分空间，B4−B2 与 B6−B5 的合成为 0（见 `table2b_primary_contrasts.csv`）；
- 图 2 已自动标注 capacity shortfall；该 run 只能证明脚本、哈希校验、过滤、制图与水印链路可运行，不能支持任何效果方向或临床结论。

## D-002 替换流程（真实结果到位后）

1. 只接受 B-002 已验收、C 独立核算、E 记录的临床 run；先检查 `manifest.run_status=completed`、`synthetic=false`、artifact hashes 全匹配。
2. 运行：
   ```powershell
   python scripts/make_figures.py `
     --run-dir results/clinical/<accepted_run_id> `
     --cohort data/processed/cohort.parquet `
     --audit data/processed/cohort_audit.json
   ```
   输出默认到 `paper/runs/<accepted_run_id>/`，不会覆盖其他 run。
3. 更新 `paper/source_index.md` 的 run_id、文件路径和 SHA256；删除/归档旧的验证引用，但 `paper/validation/` 保留作软件证据。
4. C 核对 Table 2/2b 与摘要数字；E 检查全文一致性；D 才可把图放进投稿稿。

## 审稿检查点（C/E）

- [ ] 图的每个数字能在 `tables/*_data.csv` 找到，且过滤条件与图注一致。
- [ ] Table 2 的 B0 使用 M=1 且 target 为空；B1 使用 M=10 且 target 为空；B2–B6 使用同一候选池、同一 K。
- [ ] 容量不足时报告 `actual_acceptance` 与 `pool_size`，不把整池接受解释为排序差异。
- [ ] 覆盖分母包含全部测试患者（含空集）；零分母为 NA，不填 0。
- [ ] 没有合成数字进入摘要、正文、图表或投稿材料。
- [ ] 引用只来自 C-002 已核对清单；D 不自行补引用。
