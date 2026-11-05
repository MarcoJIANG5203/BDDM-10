# 2026-11-05 · D · D-002_formal_draft

| 字段 | 本次记录 |
|---|---|
| 生产者 / 接收人 | D / C、E；B 确认 formal run 身份 |
| 状态 | 已提交待验收（**DRAFT_CANDIDATE_NOT_ACCEPTED**，不是正式论文图） |
| 协议 / 数据 / run | v1；A `a-data-v1-20261104-r1`；B 正式主 run `20261105T055420_02d05b15`；完整 bundle `b-clinical-v1-20261104-r1`（155,365,045 B，SHA256 `2328d266...`） |
| 文件 / bundle / run | `paper/draft-runs/20261105T055420_02d05b15/`；`paper/d002_readiness.md` 等状态修正 |
| 完成范围 | 从 B 正式 B-002 的 Git 小表（manifest/config/metrics/coverage/bootstrap/stability/method_status）生成 DRAFT Fig 2/3/4/6 与 Table 2/2b/3a/3b/4/5；修正 D 文档中的过期 B 状态与 R5 残留 |
| 未完成 / 阻塞 | Fig 5 跳过（本次只用 Git 小表，未取 bundle 内 599 MB patient_predictions）；**没有 C 对正式 run 的独立结论，也没有 C/E acceptance**；正式 `paper/runs/` 与论文/PDF 未生成 |
| 验证证据 | `tests/test_make_figures.py` 14 passed；DRAFT run 输出 11 tables / 8 figures；`provenance.status=DRAFT_CANDIDATE_NOT_ACCEPTED`；`skipped` 记录 Fig5；Table 2 标 B5/B6 unavailable（6 errors/1012 correct）；Fig4 标 y=1 0/8 |
| 接收人检查点 | C 确认正式 run 的独立指标/区间结论；C/E 是否签 acceptance；D 的 DRAFT 不得进论文 |
| 接收人结论 | 由 C/E 填；DRAFT 不是 sign-off |
| 下一步 / 时间 | C 先完成两个正式 run 的独立结论；C/E 签 acceptance；D 再生成正式 `paper/runs/`、补 Fig5、填 `S-xxx`、出全文/PDF |

## 1. 本次使用的正式 run

- 主 run：`20261105T055420_02d05b15`，`synthetic=false`，1208.95 秒，5 seeds × S0–S4。
- 补充 run：`20261105T055445_54dd08de`（RF、M5/20、alpha=.05），本次 DRAFT 图未使用补充 run。
- Bundle：`b-clinical-v1-20261104-r1`，112 文件，155,365,045 B，SHA256 `2328d26682a39ccb895553d3cee3dc6dd11bd6506c41a5a0ac0f5d49890e8426`，pre-release。
- C/E acceptance：**不存在**；E 只记录技术接收/范围，C 对正式 run 的独立结论仍待。

## 2. DRAFT 输出

`paper/draft-runs/20261105T055420_02d05b15/`：

- Fig 2/3/4/6（PDF/PNG），均带 DRAFT 水印。
- Table 2 / 2b / 3a / 3b / 4 / 5 及图背后的数据 CSV。
- `provenance.json`：状态 `DRAFT_CANDIDATE_NOT_ACCEPTED`，`skipped` 记录 Fig5，`inputs_missing` 记录未取的 models/masks/patient_predictions。
- **Fig 5 未生成**：需要 bundle 内的 `patient_predictions.csv`；本次只用 Git 小表。

## 3. 关键限制（保留）

- B5/B6 在正式 run 仍因选择集 6 errors/1,012 correct（<20）不可用；B6−B5 是 NA。
- MI 阳性集合覆盖 0/8（内部）；Fig4 已明确标出。
- B4−B2 方向与幅度很小，跨种子/场景不稳定；不能写成稳定优势。
- A/B 57/38、内部 8 阳性，低于 200/200/50 精度门槛；只能写有限事件数下的探索性/负结果。
- 所有 DRAFT 不得进论文、摘要、投稿材料。

## 4. 状态修正

- `paper/d002_readiness.md`：B 从“无正式 B-002/完整包未上传”更新为正式 run + 155 MB bundle；D-002 准备加入正式 DRAFT；R5 残留“禁止引用”改为 C-004 已补出。
- `paper/figure_list.md`、`paper/source_index.md`、`paper/draft_v0.md`、`collaboration/STATUS.md` 同步正式 B-002 DRAFT。
- 未改 main；PR #2 只在 D 分支更新。

## 5. 下一步

1. C 对主 run `20261105T055420_02d05b15` 与补充 `20261105T055445_54dd08de` 独立复核并记录本人结论；补充需处理 RF/M5/M20/alpha.05 的混合上下文。
2. C/E 签 `reviews/acceptance/<run_id>.json`。
3. D 用正式 run + acceptance 生成 `paper/runs/<run_id>/`；补 Fig5；更新 `source_index.md` 的 `S-xxx`；再出全文与提交版 PDF。
