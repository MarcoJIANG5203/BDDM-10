# D-002 就绪清单与 A/B/C 待办

更新：2026-11-04。维护：D。用途：明确 D-002 何时可以开始，以及 A/B/C/E 各自还缺什么。**本文件不是验收记录，不改变任何状态。**

## 当前快照（2026-11-05）

| 项目 | 状态 |
|---|---|
| `main` 的 `data/processed/cohort.parquet`、`splits/seed_2026..2030.json` | ❌ 不存在；`data/processed/` 只有 README |
| A 分支 `a/resource-researching-and-pre-processing` | ✅ `68ce9d11`；PR **#3 open**；11-05 技术收尾完成；完整 full-r1 包 + 正式 data Release |
| A 正式数据 | ✅ `a-data-v1-20261104-r1.zip`（4,666,169 B，SHA256 `feb69777...`）已发布；A owner 确认、C-005 有条件技术接收；E 批准为 **user-attested**，不是 E 直接签名 |
| A PR #3 | ⚠️ open、mergeable；main 仍未合并，`data/processed/` 仍只有 README |
| A 精度门槛 | ❌ A 10,174 人/57 阳性；B 13,921 人/38 阳性；内部测试 1,525 人/8 阳性；门槛 200/200/50 未过；A 明确保留 v1 并限定结论 |
| B 正式 B-002 run | ✅ 主 run `20261105T055420_02d05b15`（5 seeds × S0–S4）+ 补充 `20261105T055445_54dd08de`；来自正式 A Release |
| B 完整 bundle | ✅ `b-clinical-v1-20261104-r1`，155,365,045 B，SHA256 `2328d266...`，已发布 pre-release；含两个 run 与完整逐患者/p_m/模型/mask |
| B PR #5 | ⚠️ open **draft**；B/E 正式交付与 coordination；main 不合并；**没有 C/E acceptance** |
| B 正式结果限制 | ❌ 阳性集合覆盖 0/8（内部）、0/38（外部）；B5/B6 因仅 6 个选择错误不可用；B4−B2 跨种子/场景方向不一致 |
| C 分支 | ✅ `b6d7c329`；PR **#4 open**；C-006 正式 run 独立复核已提交 |
| C-001 标签复核 | ✅ 20/20 例标签一致；C-005 对 A 原始 receipt 做条件接受（parquet/audit 层一致，未字节级重跑 40,336 .psv） |
| C-003 时间边界/候选指标 | ✅ 14 个边界断言 0 失败；900 行指标、30 个配对区间、p_m 抽样独立重算 0 失败 |
| C-006 正式 run 复核 | ✅ 对主 run `…02d05b15` 与补充 `…54dd08de` 独立重算：2,612,100/366,000 行、900/240 指标、30/48 区间、覆盖与 p_m **0 失败**；结论“有条件接受算术/协议保真” |
| C-004 引用核验 | ✅ R5 已补出（MICCAI 2026 Satellite/MLMI, LNCS 17272；预印 DOI 10.21203/rs.3.rs-10336064/v1）；R3 FDR 已由全文证实；R1 LOCF 仍未证实 |
| C-002 文献/投稿 | ✅ 7/7 元数据可引用；R1 “LOCF”不写；组内 11-20 通知证据仍待留存 |
| C/E acceptance | ✅ B 分支 `4de19ab6` 新增 `reviews/acceptance/20261105T055420_02d05b15.json` 与补充 run 的 acceptance：`accepted_with_limits`，C/E 均有记录；C 是转录既有 C-006 结论（`new_signature=false`），E 是用户授权统筹（非独立统计审稿人） |
| D-001 / D-001a | D-001 图表脚本/提纲/索引已提交；D-001a 增加“临床 run 必须有 C/E 签认”门槛 |
| D-002 准备 | ✅ `paper/references_checklist.md`（7/7）、`paper/references.bib`（7 条）、`paper/draft_v0.md`（结果全占位） |
| **D-002 正式 accepted run 图表** | ✅ `paper/runs/20261105T055420_02d05b15/`：Fig 1–6、Table 1–5、acceptance binding；provenance 状态 `ACCEPTED_CLINICAL` |
| D-002 bounded results | ✅ `paper/results_accepted_with_limits.md`；不是最终论文/PDF |

## D 已完成的准备（不依赖真实结果）

- `paper/references_checklist.md`：把 C 的 7 条候选文献逐条核实；C-004 补出 R5 后 **7 条均可引用**；R3 FDR 已证实，R1 LOCF 仍不写。
- `paper/references.bib`：7 条已核实条目，含 `wong2026mc2`。
- `paper/draft_v0.md`：英文稿骨架（Abstract/Intro/Related Work/Methods/Results 占位/Discussion/Statements），所有结果处为 `[RESULT:S-xxx]`，没有临床数字。
- `paper/results_draft.md`：DRAFT 结果段落草稿，含正式 B-002 DRAFT 数字与 D-xxx 标签；**不得进论文**，只用于内部审阅与后续替换为 S-xxx。
- `paper/acceptance_record_template.json` + D-001a：临床 run 的 C/E 签认门槛。
- `scripts/make_cohort_tables.py` + `paper/inputs/a-data-v1-20261104-r1/`：从 A 正式 data Release 生成 **Table 1 / Fig 1 DRAFT**（`DRAFT_PENDING_ACCEPTANCE`）；校验 release SHA256、audit、cohort、5 splits、site/阳性数、role 互斥完备。
- `make_figures.py --draft-unaccepted --draft-reason ...`：在**不合并 main**的情况下，用 B 正式 B-002 小表（或候选 bundle）生成 `paper/draft-runs/<run_id>/` 的 DRAFT 模型图表；provenance 状态 `DRAFT_CANDIDATE_NOT_ACCEPTED`，图带 DRAFT 水印，表带 `draft=True`/`draft_reason`。正式 `paper/runs/` 仍只接受 C/E acceptance。
- 已生成候选 DRAFT：`paper/draft-runs/20261104T002604_e3a5a42b/` 的 Fig 2/3/4/6 与 Table 2/2b/3a/3b/4/5。
- 已生成**正式 B-002 DRAFT**：`paper/draft-runs/20261105T055420_02d05b15/` 的 Fig 2/3/4/5/6 与 Table 2/2b/3a/3b/4/5。Fig 5 从 bundle 流式解压 `patient_predictions.csv`（完整 SHA256 `aa23c961...` 与 manifest 一致），过滤后 1,525 行；患者级过滤文件不入库，聚合数据见 `fig5_disagreement_data.csv` 与 `FIG5_SOURCE.md`。
- 以上都只是 D 侧准备，不代表 A/B/C 验收或论文可以提交。

## D-002 开始门槛（全部满足才可生成论文图）

**不需要合并 main。** D 直接使用 A 的正式 Release、B 的 run bundle、C 的分支回执；以下门槛针对这些不可变产物，不要求 PR 合并。

1. **正式数据**：A 发布正式 data Release（已发布 `a-data-v1-20261104-r1`，SHA256 `feb69777...`）；D 直接按 Release 字节生成 Table 1/Fig 1，不依赖 main registry 合并。C-005 是条件接收。
2. **正式临床 run**：✅ 主 run `20261105T055420_02d05b15`、补充 `20261105T055445_54dd08de`；完整 bundle `b-clinical-v1-20261104-r1` 已发布。
3. **签认记录**：✅ B 分支 `4de19ab6` 有 `reviews/acceptance/20261105T055420_02d05b15.json` 与补充 run 的 acceptance，状态 `accepted_with_limits`，C/E 均有记录；D 通过 `--acceptance-file` 使用。
4. **结果接受与冻结**：✅ scoped v1 numerical result freeze（算术/协议保真）；**不是最终论文/PDF 或投稿验收**；临床安全未验证，原始 .psv 未逐例重放。
5. **文献与投稿**：C-002/C-004 引用已核对；R1 LOCF 不写；投稿材料仍需 D 的最终稿与 A 许可结论。
6. **来源索引**：✅ `paper/source_index.md` 的 `S-001`–`S-012` 已绑定 `paper/runs/20261105T055420_02d05b15/`；S-010 补充表待制。

任一项缺失，`scripts/make_figures.py` 会拒绝临床 run；不要用 `--validation-only` 绕过临床稿，也不要手改数字。

## DRAFT 模式边界（不合并 main）

- D 可以**不合并 main**，直接用 A 的正式 Release、B 的候选 bundle、C 的分支回执工作。
- 但未验收的 B 正式 B-002 run 或候选 run 只能走 `--draft-unaccepted --draft-reason ...`，输出到 `paper/draft-runs/<run_id>/`，provenance 为 `DRAFT_CANDIDATE_NOT_ACCEPTED`，图表带 DRAFT 水印，表格带 `draft=True`/`draft_reason`。
- DRAFT 产物**不能**进入 `paper/runs/`、不能写入论文结果、不能作为投稿材料。
- 正式 `paper/runs/<run_id>/` 仍必须有 C/E acceptance record；这一条不因“不合并 main”而改变。

## A 还需要做什么

A 已完成：正式 data Release `a-data-v1-20261104-r1`（4,666,169 B，SHA256 `feb69777...`）、A owner confirmation、C-005 条件技术接收、`68ce9d11` 11-05 技术收尾（125 项恢复/完整性检查）、PR #3 open。许可冲突仍未解决。剩余：

1. **PR #3 可保持 open**：用户明确不需要合并 main；D 直接使用正式 Release `a-data-v1-20261104-r1` 的字节。A 只需保证 Release 字节与 PR #3 的 cohort/splits/audit 一致，且不替换既有 Release 资产。
2. **确认 raw 不入普通 Git**：A PR #3 已修改 `.gitignore`/`.gitattributes`，声称不添加普通 Git 临床表/raw 归档；即使不合并，也建议保持这一边界。
3. **证据路径可读**：PR #3 已加入 `reviews/A_001_verification...`、`scripts/verify_a001_delivery.py`、`docs/A_001_source_provenance_correction_EN.md` 等普通文件；D/C 可直接从 PR #3 分支读取，不需要合并。
4. **许可仍未解决**：PhysioNet 页面 CC BY 4.0 vs `LICENSE.txt` ODbL；A PR #3 保留了两份证据与澄清请求草稿，但没有保管人回复。正式投稿前必须记录结论或明确“不重新分发原始数据”。
5. **E 批准不是直接签名**：A PR #3 写 “E approved” 为 **USER-ATTESTED**，不是 E 的原始签认文件；`reviews/acceptance` 仍不存在。需要 E 的正式记录/签名，不能把 user-attested 当作 acceptance。
6. **精度门槛结论**：A 已选择保留 v1 并限定结论；需要 C/E 在统一记录中确认这一选择，不能只由 A PR body 表述。
7. **正式 data Release 已发布**：`a-data-v1-20261104-r1`；D 已按 Release 字节生成 Table 1/Fig 1 DRAFT，不依赖 main registry 合并。

## B 还需要做什么

1. **B 生产任务已完成，PR #5 仍 draft**：B-002 主 run `20261105T055420_02d05b15`、补充 `20261105T055445_54dd08de` 已跑完；完整 bundle `b-clinical-v1-20261104-r1` 已发布 pre-release。PR #5 保持 draft 供接收人检查，main 不合并。
2. **给 C 可独立复核的材料已齐**：完整 run/Release、manifest、逐患者表、p_m、模型、mask、种子、复算脚本都在 bundle/分支；C 的个人结论仍待。
3. **正式 B-002 已重跑**：来自正式 A Release 字节，`run_status=completed`，`synthetic=false`；C 对两个新 run 的独立结论未提交。
4. **完整 bundle 已上传**：155,365,045 B，SHA256 `2328d266...`；不再是本地 prepared。
5. **补充实验已完成**：RF（S0/S2）、M=5/20（S0）、alpha=.05（S0/S2）；C 需按混合上下文独立核验，不能把主矩阵 900/30 结果冒充补充的 240/48。
6. **B 已如实记录不利结果**：阳性覆盖 0/8 与 0/38、B5/B6 不可用（6 个选择错误）、B4−B2 跨种子方向不一致。
7. **v2 情况**：若团队选 v2，按新协议重新实现/运行；v1 结果只作历史。
8. **更新记录**：C/E 接受后才可把 B-002 标为已验收/冻结；当前仍是生产者交付完成、接收待审。

## C 还需要做什么

C 已完成：C-001 20/20 标签、C-003 时间边界 14 断言、候选 run 900/30 独立重算（0 失败）、C-004 引用核验、C-005 A receipt 条件复核、**C-006 两个正式 run 独立复核（900/240 指标、30/48 区间、0 失败，结论为有条件接受算术/协议保真）**。以下是把这些转成可接受交接的剩余工作：

1. **C PR #4 可保持 open**：用户明确不需要合并 main；D 直接从 C 分支读取 C-004/C-005 回执。C 只需保证分支 commit 不被改写，并把接受结论写在可见记录里。
2. **完成 C-003 的接收闭环**：B 需确认 `tie_key=sha256(patient_id)`、排序键与 frozen 阈值语义；B/E 在 C-003 记录上填写接收结论，不能只由 C 自报“0 失败”。
3. **原始 `.psv` 逐例 onset**：C-005 已用 A receipt 的 parquet/audit 独立重算并条件接受；但 C 本人仍未字节级重跑 40,336 份 `.psv`。若需完整闭环，A/E 提供已认证下载通道；否则在记录中保留“C 未字节级重跑”的边界。
4. **C-002/C-004 剩余**：
   - R5 已由 C-004 补出（MICCAI 2026 Satellite/MLMI，LNCS 17272；预印 DOI 10.21203/rs.3.rs-10336064/v1），D 已写入 bib；**不再禁止引用**。
   - R3 的 FDR 已由 C-004 全文证实，D 可写；R1 的 LOCF 仍未证实，C/D 不写，除非逐字读全文并给页码。
   - 组内“11-20 前可投稿”通知证据仍需 C 记录核对日期，并由 E/通讯作者留存原件。
5. **给 D 的最终引用结论**：D 已建 `paper/references_checklist.md`（7 条可引用）；C-004 的结论已采用。C 只需确认 R1 是否补 LOCF 页码，否则保持不写。
6. **C-006 的接收与签认**：C 已完成两个正式 run 的独立复核并写“有条件接受算术/协议保真”；还需要 B/E 回填接收意见，并在 `reviews/acceptance/<run_id>.json` 记录 C/E 的正式签认。目前**没有任何 acceptance 记录**；C 的交接本身不是 acceptance 文件。
7. **许可/来源**：与 A/E 一起记录 PhysioNet CC BY 4.0 与 LICENSE.txt 的 ODbL 差异；A PR #3 已把两者证据保留，但未解决。

## E 需要做什么（与 A/B/C 联动）

1. 召集 A/B/C/E 书面选择 v1 限定、v2 重建或暂停；记录理由、已查看旧结果的事实、版本号与日期。
2. 维护 `collaboration/STATUS.md`：主分支当前仍停在 11-02，A/B 的最新状态在分支/PR 上；合并后统一更新。
3. 与通讯作者确认专场入口、北京时间截止、页数/模板；公开日历不能替代通知原件。
4. 在 A 正式签认、C-001 完成、正式 data Release 与 B-002 验收后，才填写 E 的 acceptance signoff。

## D 在门槛满足后会做什么

D 已完成：

1. 用正式 run + acceptance 生成 `paper/runs/20261105T055420_02d05b15/`（Fig 1–6、Table 1–5），provenance 状态 `ACCEPTED_CLINICAL`。
2. `paper/source_index.md` 的 `S-001`–`S-012` 已绑定正式 run；S-010 补充表待制。
3. `paper/results_accepted_with_limits.md` 已写 bounded results。

仍待 D 完成：

4. 生成补充 run `20261105T055445_54dd08de` 的 Table S1–S3（RF、M=5/20、alpha=.05）。
5. 按 `paper/outline.md` 整合完整英文稿；引用只用 `paper/references.bib` 中已核实条目。
6. C 核对 Table 2/2b 与摘要；E 检查摘要—正文—图表—结论一致；生成提交版 PDF 与材料清单。
7. A 许可冲突解决或明确不重新分发原始数据后，才可做正式投稿材料。

## 明确禁止

- 不用 B 的候选 run `20261104T002604_e3a5a42b` 生成论文图或写结果。
- 不用 `paper/validation/` 的合成数字写摘要、正文、图表或汇报。
- 不手改 CSV/图表数字；不从聊天/截图复制数字。
- 不在精度门槛失败时静默改标签、时间窗、split、容量或阈值来制造有利结果。
