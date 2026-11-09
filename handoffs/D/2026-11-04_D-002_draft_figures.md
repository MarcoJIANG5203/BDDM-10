# 2026-11-04 · D · D-002_draft_figures

| 字段 | 本次记录 |
|---|---|
| 生产者 / 接收人 | D / C、E；B 确认候选 run 身份与限制 |
| 状态 | 已提交待验收（**DRAFT_CANDIDATE_NOT_ACCEPTED**，不是最终论文图） |
| 协议 / 数据 / run | v1；A 数据版本 `a-clinical-protocol-v1-20261103-full-r1`；B 候选 run `20261104T002604_e3a5a42b`（bundle `b-candidate-v1-matrix-20261104-r1`，123,342,522 B，SHA256 `b701d0ee...`）；**没有 C/E acceptance** |
| 文件 / bundle / run | `paper/draft-runs/20261104T002604_e3a5a42b/`；`scripts/make_figures.py` 的 `--draft-unaccepted` 模式；`tests/test_make_figures.py` |
| 完成范围 | 在**不合并 main**的情况下，从 B 候选 bundle 取小表并用 Range 取部分大文件，生成 DRAFT Fig 2/3/4/6 与 Table 2/2b/3a/3b/4/5；provenance 标记 `DRAFT_CANDIDATE_NOT_ACCEPTED`；图带 DRAFT 水印，表带 `draft=True`/`draft_reason` |
| 未完成 / 阻塞 | Fig 5 跳过：`patient_predictions.csv` 599,227,488 B，本次 Range 只取到部分字节，未通过 hash；需完整 bundle 才能补。正式 `paper/runs/` 仍缺 C/E acceptance |
| 验证证据 | `tests/test_make_figures.py`：**14 passed**；DRAFT run 输出 11 tables、8 figures；`provenance.status=DRAFT_CANDIDATE_NOT_ACCEPTED`、`acceptance=null`、`skipped` 记录 Fig5；Table 2 的 B5/B6 标 unavailable（6 errors/1012 correct，门槛 20）；Fig4 明确标 0/8 阳性覆盖 |
| 接收人检查点 | C/E 确认这些 DRAFT 数字没有被写入 `draft_v0.md`/`source_index.md` 的 `S-xxx`；B 确认 run id 与候选状态；D 不在投稿稿中使用 DRAFT |
| 接收人结论 | 由 C/E 填，附日期；不把 DRAFT 当作 acceptance |
| 下一步 / 时间 | B 在 A 正式 Release 上跑正式 B-002；C/E 签 acceptance；D 再用正式 `paper/runs/` 和完整 patient-level 数据补 Fig 5 |

## 1. 生成了什么

`paper/draft-runs/20261104T002604_e3a5a42b/`：

- `figures/fig2_risk_acceptance.{pdf,png}`：风险—接受比例 + B4−B2 区间。
- `figures/fig3_scenarios.{pdf,png}`：S0–S4 的 B4−B2；B6−B5 不可用已在图上标注。
- `figures/fig4_coverage.{pdf,png}`：MI/median 覆盖；y=1 的 0/8 已明确标出。
- `figures/fig6_stability.{pdf,png}`：5 批三状态不一致率。
- `tables/table2_main_results.csv`、`table2b_primary_contrasts.csv`、`table3_scenario_per_seed.csv`、`table3_scenario_summary.csv`、`table4_coverage_strata.csv`、`table5_stability.csv`。
- `tables/fig2_*_data.csv`、`fig3_scenario_data.csv`、`fig4_coverage_data.csv`、`fig6_stability_data.csv`。
- `provenance.json`、`README.txt`。

**没有** `fig5_disagreement`：`patient_predictions.csv` 599 MB，未完整取回；provenance `skipped` 已记录。

## 2. 关键限制（必须保留）

- 这是 B 的**候选预冻结** run；`config.yaml` 写 `scientific_acceptance: PENDING_A_C_E_NOT_FORMAL_FROZEN_RESULTS`。
- B5/B6 在五个种子都因选择集仅 6 个错误（<20 门槛）不可用；Table 2 标 `unavailable`，Fig3 标注 B6−B5 不可用。
- MI 阳性集合覆盖为 **0/8**（内部）；Fig4 已明确标 0/8，不能把总体覆盖当阳性安全。
- B4−B2 的方向与幅度很小且跨种子不稳定；不得写成稳定优势。
- 所有输出带 DRAFT，**不能进入论文、摘要、投稿材料或对外汇报**。

## 3. 验证

```powershell
python -m pytest tests/test_make_figures.py -q -p no:cacheprovider
# 14 passed
```

DRAFT 运行：

```text
status=DRAFT_CANDIDATE_NOT_ACCEPTED
draft=true
tables=11
figures=8
acceptance=null
skipped=fig5_disagreement: patient_predictions.csv not available in the draft fetch
inputs_missing=39（models/masks/p_m 等未取，DRAFT 允许）
```

## 4. 为什么没有合并 main

用户明确不需要合并 main。D 的 PR #2 只在 `d/figure-and-paper` 分支上；本记录与 DRAFT 输出也只在分支。main 保持不变。

## 5. 下一步

1. B 在 A 正式 data Release `a-data-v1-20261104-r1` 上跑正式 B-002，上传完整 bundle（含 patient_predictions）。
2. C 独立复核；C/E 签 `reviews/acceptance/<run_id>.json`。
3. D 去掉 DRAFT，改用 `paper/runs/<run_id>/`；补 Fig 5；更新 `source_index.md` 的 `S-xxx`；再把 `draft_v0.md` 的占位替换为正式数字。
