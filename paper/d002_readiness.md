# D-002 就绪清单与 A/B/C 待办

更新：2026-11-04。维护：D。用途：明确 D-002 何时可以开始，以及 A/B/C/E 各自还缺什么。**本文件不是验收记录，不改变任何状态。**

## 当前快照（2026-11-04）

| 项目 | 状态 |
|---|---|
| `main` 的 `data/processed/cohort.parquet`、`splits/seed_2026..2030.json` | ❌ 不存在；`data/processed/` 只有 README |
| A 分支 `a/resource-researching-and-pre-processing` | ✅ 有完整 full-r1 包（cohort、audit、5 splits、raw、20 review cases），4 commits ahead；**没有 PR 到 main** |
| A 正式验收 | ❌ `human_review` 三项均 PENDING；`release_status=LOCAL_PREPARED_NOT_PUBLISHED_NOT_ACCEPTED` |
| A 精度门槛 | ❌ A 10,174 人/57 阳性；B 13,921 人/38 阳性；内部测试 1,525 人/8 阳性；门槛 200/200/50 未过 |
| B 候选 run | ✅ `20261104T002604_e3a5a42b`，`synthetic=false`，5 seeds × 5 scenarios；pre-release 123,342,522 B |
| B PR #1 | ⚠️ 已于 2026-11-04 02:28 关闭（未合并）；B 自述“候选预冻结”，不是正式 B-002 |
| B 候选结果限制 | ❌ 阳性集合覆盖 0/8（内部）、0/38（外部）；B5/B6 因仅 6 个选择错误不可用；B4−B2 跨种子/场景方向不一致 |
| C 分支 | ✅ `f2eb560a`，ahead 3 vs main；**没有 PR 到 main** |
| C-001 标签复核 | ✅ 20/20 例标签一致（`handoffs/C/2026-11-03_标签核验.md`）；状态仍“已提交待验收” |
| C-003 时间边界/候选指标 | ✅ 14 个边界断言 0 失败；900 行指标、30 个配对区间、p_m 抽样独立重算 0 失败；原始 `.psv` 逐例 onset 闭环仍待 A receipt |
| C-002 文献/投稿 | ⚠️ 对照表已提交；D 核实 6/7 条元数据，**R5 “MC²”未找到出处，禁止引用**；R1/R3 的 LOCF/FDR 细节待全文核对；组内通知证据仍待留存 |
| E precision/freeze | ⏸️ 已记录**暂缓**正式冻结和启动 B-002；要求 A/B/C/E 书面选择路径 |
| D-001 / D-001a | D-001 图表脚本/提纲/索引已提交；D-001a 增加“临床 run 必须有 C/E 签认”门槛 |
| D-002 准备 | ✅ `paper/references_checklist.md`、`paper/references.bib`（6 条已核实）、`paper/draft_v0.md`（英文骨架，结果全占位） |

## D 已完成的准备（不依赖真实结果）

- `paper/references_checklist.md`：把 C 的 7 条候选文献逐条核实；6 条可引用，**R5 “MC²”未找到出处，禁止引用**。
- `paper/references.bib`：只含 6 条已核实元数据的条目。
- `paper/draft_v0.md`：英文稿骨架（Abstract/Intro/Related Work/Methods/Results 占位/Discussion/Statements），所有结果处为 `[RESULT:S-xxx]`，没有临床数字。
- `paper/acceptance_record_template.json` + D-001a：临床 run 的 C/E 签认门槛。
- 以上都只是 D 侧准备，不代表 A/B/C 验收或论文可以提交。

## D-002 开始门槛（全部满足才可生成论文图）

1. **正式数据**：A 发布正式 data Release，并在 `artifacts/registry.json` 登记 `published` + 真实 SHA256；C-001 通过。
2. **正式临床 run**：B-002 在冻结数据上重跑并验收；`manifest.json` 为 `run_status=completed`、`synthetic=false`，完整 artifact hashes 可核。
3. **签认记录**：`reviews/acceptance/<run_id>.json` 存在且通过脚本校验：
   - `run_id` 与 run 目录一致；
   - `manifest_sha256` 与 `manifest.json` 一致；
   - `status` 为 `accepted` / `accepted_with_limits`；
   - C 与 E 均有 `name`、`date`、`decision`、`evidence`。
   - 模板：`paper/acceptance_record_template.json`。
4. **冻结决定**：E 记录 v1 限定/v2 重建/暂停的最终选择；协议、数据版本、CHANGELOG 已更新。
5. **文献与投稿**：C-002 给出已核对引用清单、页数/模板/截止/披露要求。
6. **来源索引**：`paper/source_index.md` 的 `S-xxx` 已填入该 run 的路径、过滤条件、哈希。

任一项缺失，`scripts/make_figures.py` 会拒绝临床 run；不要用 `--validation-only` 绕过临床稿，也不要手改数字。

## A 还需要做什么

1. **本人签认 A-001**：在 `handoffs/A/` 与 `cohort_audit.json` 的 `human_review.A_owner_review` 填入姓名/日期/结论；当前是 PENDING。
2. **开 PR 到 main**：A 分支已有 4 个 commit，但没有 PR；把数据包与交接记录提交 PR，按 CONTRIBUTING 由接收人验收后再合并。
3. **处理 raw ZIP 入库问题**：A 分支把 `raw/training_setA.zip`（21.7 MB）与 `training_setB.zip`（19.8 MB）放进了普通 Git，与 `collaboration/DATA_SYNC.md` 的“原始/大文件走 Release”不一致。合并前改为 Release/LFS 或从 Git 排除，保留 SHA256 与来源清单。
4. **展开被引用证据**：A 报告引用的 `reviews/A_001_verification_2026-11-03.json`、`scripts/verify_a001_delivery.py`、`docs/A_001_source_provenance_correction_EN.md` 目前只在补件 ZIP 的 `git_overlay/` 内；请放到可直接读取的路径，并保留原 ZIP 字节。
5. **澄清许可**：PhysioNet 页面标 CC BY 4.0，但 `LICENSE.txt` 是 ODbL 文本；与数据保管人确认后在正式 Release 元数据中记录，不能自行选一个。
6. **精度门槛书面决定**：A/B/C/E 明确选择：
   - 保留 v1，限定研究问题与结论；或
   - 另立 v2（例如 `(12,36]` 预测窗），说明理由、重建数据、披露已查看旧结果；或
   - 暂停正式实验，先解决可行性。
   不能静默改标签、时间窗或 split 来追阳性数。
7. **发布正式 data Release**：仅在 C-001/E 决定后；更新 registry、STATUS、CHANGELOG、handoffs/A，并保持 `cohort.parquet`、`cohort_audit.json`、5 splits 同版本。

## B 还需要做什么

1. **候选 PR 已关闭，不要重开成正式 PR**：B 的 PR #1 已于 2026-11-04 02:28 关闭（未合并）；候选矩阵不是正式 B-002。在 A 正式数据、C 完整复核、E 冻结前不要合并或改称“已验收”。
2. **给 C 可独立复核的材料**：完整 run/Release、manifest、逐患者表、p_m、模型、mask、种子；提供与 `reviews/verify_b_artifacts.py`、bootstrap 复算脚本一致的命令；C 的结论由 C 自己填写。
3. **正式 B-002 重跑**：E 冻结后用正式 data Release 的字节重跑，产生新的不可变 run；不要直接把 `20261104T002604_e3a5a42b` 当正式 B-002。
4. **补充实验按优先级**：主 run 验收后再跑 RF（S0/S2）、M=5/20（S0）、alpha=0.05；作为敏感性分析，不升格为主结论。
5. **如实记录不利结果**：阳性覆盖 0/8 与 0/38、B5/B6 不可用（6 个选择错误）、B4−B2 跨种子方向不一致；不得换种子、换容量、改阈值或删场景来制造优势。
6. **v2 情况**：若团队选 v2，按新协议重新实现/运行，不能把 v1 结果当确认性证据；旧 run 保留作历史。
7. **更新记录**：正式 run 被接收后才更新 registry、STATUS、CHANGELOG、handoffs/B；候选 run 标记为历史/预冻结。

## C 还需要做什么

C 已完成：C-001 20/20 标签核对、C-003 时间边界 14 断言、候选 run 900 行指标/30 个配对区间/p_m 独立重算（0 失败）。以下是把这些转成可接受交接的剩余工作：

1. **开 PR 到 main**：C 分支 `f2eb560a` 已 ahead 3，但没有 PR；main 仍停在 11-02。
2. **完成 C-003 的接收闭环**：B 需确认 `tie_key=sha256(patient_id)`、排序键与 frozen 阈值语义；B/E 在 C-003 记录上填写接收结论，不能只由 C 自报“0 失败”。
3. **原始 `.psv` 逐例 onset**：C 目前用 A receipt 的 parquet/audit 交叉核对；完整逐例重算需要 A 的原始小时 receipt。要么等 A 提供，要么在记录中明确标为 A 的独立回执范围。
4. **C-002 引用补齐**：
   - **R5 “MC² (MICCAI 2026)” 未找到 DOI/URL，D 已禁止引用**；请 C 提供准确标题/作者/会议/DOI，补不上就从 Related Work 删除。
   - R1 的“LOCF”和 R3 的“FDR”未在摘要/元数据中确认；若原文确有，请给页码/章节，D 再写入。
   - 组内“11-20 前可投稿”通知证据仍需 C 记录核对日期，并由 E/通讯作者留存原件。
5. **给 D 的引用结论**：D 已建 `paper/references_checklist.md`（6 条可引用、R5 禁止）；C 只需确认/修正 claim 范围，不要再把未读原文的条目写成“已核实”。
6. **正式 run 后 C-003 复核**：E 冻结、B 在正式 data Release 上重跑后，C 需独立复算主表/区间并签 acceptance record。
7. **许可/来源**：与 A/E 一起记录 PhysioNet CC BY 4.0 与 LICENSE.txt 的 ODbL 差异；不要把未核实来源写成结论。

## E 需要做什么（与 A/B/C 联动）

1. 召集 A/B/C/E 书面选择 v1 限定、v2 重建或暂停；记录理由、已查看旧结果的事实、版本号与日期。
2. 维护 `collaboration/STATUS.md`：主分支当前仍停在 11-02，A/B 的最新状态在分支/PR 上；合并后统一更新。
3. 与通讯作者确认专场入口、北京时间截止、页数/模板；公开日历不能替代通知原件。
4. 在 A 正式签认、C-001 完成、正式 data Release 与 B-002 验收后，才填写 E 的 acceptance signoff。

## D 在门槛满足后会做什么

1. 用正式 run 运行：
   ```powershell
   python scripts/make_figures.py `
     --run-dir results/clinical/<accepted_run_id> `
     --cohort data/processed/cohort.parquet `
     --audit data/processed/cohort_audit.json
   ```
   默认输出 `paper/runs/<run_id>/{figures,tables}/`，并校验 `reviews/acceptance/<run_id>.json`。
2. 更新 `paper/source_index.md` 的 `S-001`–`S-012`，把 `[RESULT:S-xxx]` 替换为真实数字。
3. 按 `paper/outline.md` 整合英文稿；以 `paper/draft_v0.md` 为骨架，引用只用 `paper/references.bib` 中已核实条目（R5 禁止引用），不补未核对文献。
4. C 核对表 2/2b 与摘要；E 检查摘要—正文—图表—结论一致；然后生成提交版 PDF 与材料清单。

## 明确禁止

- 不用 B 的候选 run `20261104T002604_e3a5a42b` 生成论文图或写结果。
- 不用 `paper/validation/` 的合成数字写摘要、正文、图表或汇报。
- 不手改 CSV/图表数字；不从聊天/截图复制数字。
- 不在精度门槛失败时静默改标签、时间窗、split、容量或阈值来制造有利结果。
