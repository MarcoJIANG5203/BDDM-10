# D-002 就绪清单与 A/B/C 待办

更新：2026-11-04。维护：D。用途：明确 D-002 何时可以开始，以及 A/B/C/E 各自还缺什么。**本文件不是验收记录，不改变任何状态。**

## 当前快照（2026-11-04）

| 项目 | 状态 |
|---|---|
| `main` 的 `data/processed/cohort.parquet`、`splits/seed_2026..2030.json` | ❌ 不存在；`data/processed/` 只有 README |
| A 分支 `a/resource-researching-and-pre-processing` | ✅ `b717d1ae`；PR **#3 open**（57 files）；完整 full-r1 包 + 正式 data Release |
| A 正式数据 | ✅ `a-data-v1-20261104-r1.zip`（4,666,169 B，SHA256 `feb69777...`）已发布；A owner 确认、C-005 有条件技术接收；E 批准为 **user-attested**，不是 E 直接签名 |
| A PR #3 | ⚠️ open、mergeable；main 仍未合并，`data/processed/` 仍只有 README |
| A 精度门槛 | ❌ A 10,174 人/57 阳性；B 13,921 人/38 阳性；内部测试 1,525 人/8 阳性；门槛 200/200/50 未过；A 明确保留 v1 并限定结论 |
| B 候选 run | ✅ `20261104T002604_e3a5a42b`；PR #5 另加补充 run `20261104T132609_45c03e76`；**没有正式 B-002 run** |
| B PR #5 | ⚠️ open **draft**；候选补充与 coordination；完整临床 bundle 仍本地 prepared、未上传（许可冲突） |
| B 候选结果限制 | ❌ 阳性集合覆盖 0/8（内部）、0/38（外部）；B5/B6 因仅 6 个选择错误不可用；B4−B2 跨种子/场景方向不一致 |
| C 分支 | ✅ `f4d97366`；PR **#4 open**（9 files） |
| C-001 标签复核 | ✅ 20/20 例标签一致；C-005 对 A 原始 receipt 做条件接受（parquet/audit 层一致，未字节级重跑 40,336 .psv） |
| C-003 时间边界/候选指标 | ✅ 14 个边界断言 0 失败；900 行指标、30 个配对区间、p_m 抽样独立重算 0 失败 |
| C-004 引用核验 | ✅ R5 已补出（MICCAI 2026 Satellite/MLMI, LNCS 17272；预印 DOI 10.21203/rs.3.rs-10336064/v1）；R3 FDR 已由全文证实；R1 LOCF 仍未证实 |
| C-002 文献/投稿 | ✅ 7/7 元数据可引用；R1 “LOCF”不写；组内 11-20 通知证据仍待留存 |
| E precision/freeze | ⚠️ A PR #3 记录 E 批准但为 **user-attested**；没有 E 直接签名；**`reviews/acceptance` 在任何分支都不存在** |
| D-001 / D-001a | D-001 图表脚本/提纲/索引已提交；D-001a 增加“临床 run 必须有 C/E 签认”门槛 |
| D-002 准备 | ✅ `paper/references_checklist.md`（7/7）、`paper/references.bib`（7 条）、`paper/draft_v0.md`（结果全占位） |

## D 已完成的准备（不依赖真实结果）

- `paper/references_checklist.md`：把 C 的 7 条候选文献逐条核实；C-004 补出 R5 后 **7 条均可引用**；R3 FDR 已证实，R1 LOCF 仍不写。
- `paper/references.bib`：7 条已核实条目，含 `wong2026mc2`。
- `paper/draft_v0.md`：英文稿骨架（Abstract/Intro/Related Work/Methods/Results 占位/Discussion/Statements），所有结果处为 `[RESULT:S-xxx]`，没有临床数字。
- `paper/acceptance_record_template.json` + D-001a：临床 run 的 C/E 签认门槛。
- `scripts/make_cohort_tables.py` + `paper/inputs/a-data-v1-20261104-r1/`：从 A 正式 data Release 生成 **Table 1 / Fig 1 DRAFT**（`DRAFT_PENDING_ACCEPTANCE`）；校验 release SHA256、audit、cohort、5 splits、site/阳性数、role 互斥完备。可在 PR #3 合并/C/E 接收后转为最终表。
- 以上都只是 D 侧准备，不代表 A/B/C 验收或论文可以提交。

## D-002 开始门槛（全部满足才可生成论文图）

1. **正式数据**：A 发布正式 data Release（已发布 `a-data-v1-20261104-r1`），并在 **main** 的 `artifacts/registry.json` 登记 `published` + 真实 SHA256；A PR #3 尚未合并，C-005 是条件接收。
2. **正式临床 run**：B-002 在冻结数据上重跑并验收；当前 **没有** 正式 B-002 run，`results/clinical/` 不存在；B PR #5 的 run 是候选补充。
3. **签认记录**：`reviews/acceptance/<run_id>.json` 存在且通过脚本校验；当前 **A/B/C/D 任何分支都没有 `reviews/acceptance`**：
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

A 已完成：正式 data Release `a-data-v1-20261104-r1`（4,666,169 B，SHA256 `feb69777...`）、A owner confirmation、C-005 条件技术接收、PR #3 open。剩余：

1. **合并 PR #3**：PR #3 open、mergeable；main 的 `data/processed/` 与 `splits/` 仍只有 README。需要接收人评审后合并，D/C/B 才能在 main 上引用。
2. **确认 raw 不入普通 Git**：A PR #3 已修改 `.gitignore`/`.gitattributes`，声称不添加普通 Git 临床表/raw 归档；合并前核对 `raw/training_set*.zip` 不再进入 main。
3. **展开证据路径**：PR #3 已加入 `reviews/A_001_verification...`、`scripts/verify_a001_delivery.py`、`docs/A_001_source_provenance_correction_EN.md` 等普通文件；合并后确认 D/C 可直接读取。
4. **许可仍未解决**：PhysioNet 页面 CC BY 4.0 vs `LICENSE.txt` ODbL；A PR #3 保留了两份证据与澄清请求草稿，但没有保管人回复。正式投稿前必须记录结论或明确“不重新分发原始数据”。
5. **E 批准不是直接签名**：A PR #3 写 “E approved” 为 **USER-ATTESTED**，不是 E 的原始签认文件；`reviews/acceptance` 仍不存在。需要 E 的正式记录/签名，不能把 user-attested 当作 acceptance。
6. **精度门槛结论**：A 已选择保留 v1 并限定结论；需要 C/E 在统一记录中确认这一选择，不能只由 A PR body 表述。
7. **正式 data Release 已发布**：`a-data-v1-20261104-r1`；但 main 的 `artifacts/registry.json` 尚未合并 A 的 registry 更新（PR #3 里有）。合并后 D 才能按正式数据版本生成 Table 1/Fig 1。

## B 还需要做什么

1. **PR #1 已关闭，PR #5 仍是 draft**：PR #1 于 2026-11-04 02:28 关闭（未合并）；PR #5 open/draft 是候选补充与 coordination，不是正式 B-002。不要把候选 run `20261104T002604_e3a5a42b` 或补充 run `20261104T132609_45c03e76` 改称“已验收”。
2. **给 C 可独立复核的材料**：完整 run/Release、manifest、逐患者表、p_m、模型、mask、种子；提供与 `reviews/verify_b_artifacts.py`、bootstrap 复算脚本一致的命令；C 的结论由 C 自己填写。
3. **正式 B-002 重跑**：用 A 正式 data Release `a-data-v1-20261104-r1` 的字节重跑，产生新的不可变 run；当前没有正式 B-002 run，`results/clinical/` 不存在。
4. **上传完整临床 bundle**：B PR #5 自述完整临床 bundle 仍本地 `prepared`、未上传（许可冲突）；正式 B-002 需要可下载、可校验的 bundle。
5. **补充实验按优先级**：主 run 验收后再跑 RF（S0/S2）、M=5/20（S0）、alpha=0.05；作为敏感性分析，不升格为主结论。
6. **如实记录不利结果**：阳性覆盖 0/8 与 0/38、B5/B6 不可用（6 个选择错误）、B4−B2 跨种子方向不一致；不得换种子、换容量、改阈值或删场景来制造优势。
7. **v2 情况**：若团队选 v2，按新协议重新实现/运行，不能把 v1 结果当确认性证据；旧 run 保留作历史。
8. **更新记录**：正式 run 被接收后才更新 registry、STATUS、CHANGELOG、handoffs/B；候选 run 标记为历史/预冻结。

## C 还需要做什么

C 已完成：C-001 20/20 标签、C-003 时间边界 14 断言、候选 run 900 行指标/30 个配对区间/p_m 独立重算（0 失败）、C-004 引用核验、C-005 A receipt 条件复核。以下是把这些转成可接受交接的剩余工作：

1. **C PR #4 需要评审/合并**：PR #4 open（9 files）；main 仍停在 11-02。C 不能只把结果留在分支。
2. **完成 C-003 的接收闭环**：B 需确认 `tie_key=sha256(patient_id)`、排序键与 frozen 阈值语义；B/E 在 C-003 记录上填写接收结论，不能只由 C 自报“0 失败”。
3. **原始 `.psv` 逐例 onset**：C-005 已用 A receipt 的 parquet/audit 独立重算并条件接受；但 C 本人仍未字节级重跑 40,336 份 `.psv`。若需完整闭环，A/E 提供已认证下载通道；否则在记录中保留“C 未字节级重跑”的边界。
4. **C-002/C-004 剩余**：
   - R5 已由 C-004 补出（MICCAI 2026 Satellite/MLMI，LNCS 17272；预印 DOI 10.21203/rs.3.rs-10336064/v1），D 已写入 bib；**不再禁止引用**。
   - R3 的 FDR 已由 C-004 全文证实，D 可写；R1 的 LOCF 仍未证实，C/D 不写，除非逐字读全文并给页码。
   - 组内“11-20 前可投稿”通知证据仍需 C 记录核对日期，并由 E/通讯作者留存原件。
5. **给 D 的最终引用结论**：D 已建 `paper/references_checklist.md`（7 条可引用）；C-004 的结论已采用。C 只需确认 R1 是否补 LOCF 页码，否则保持不写。
6. **正式 run 后 C-003 复核**：E 冻结、B 在正式 data Release 上重跑后，C 需独立复算主表/区间并签 acceptance record。目前**没有任何 `reviews/acceptance` 记录**。
7. **许可/来源**：与 A/E 一起记录 PhysioNet CC BY 4.0 与 LICENSE.txt 的 ODbL 差异；A PR #3 已把两者证据保留，但未解决。

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
