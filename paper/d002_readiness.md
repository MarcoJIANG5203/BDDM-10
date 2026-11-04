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
| B PR #1 | ⚠️ 仍是 **draft**；B 自述“候选预冻结”，不是正式 B-002 |
| B 候选结果限制 | ❌ 阳性集合覆盖 0/8（内部）、0/38（外部）；B5/B6 因仅 6 个选择错误不可用；B4−B2 跨种子/场景方向不一致 |
| C 标签复核 | ⚠️ C 脚本对 20 例 20/20 匹配；C 本人签署、边界病例、逐患者指标/区间的完整复核仍待完成 |
| C-002 文献/投稿 | ⚠️ 有提交；官网日期与组内通知冲突，需核对并记录日期；引用未逐条核原文 |
| E precision/freeze | ⏸️ 已记录**暂缓**正式冻结和启动 B-002；要求 A/B/C/E 书面选择路径 |
| D-001 / D-001a | D-001 图表脚本/提纲/索引已提交；D-001a 增加“临床 run 必须有 C/E 签认”门槛 |

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

1. **保持 PR #1 为 draft**：候选矩阵不是正式 B-002；在 A 正式数据、C 完整复核、E 冻结前不要合并或改称“已验收”。
2. **给 C 可独立复核的材料**：完整 run/Release、manifest、逐患者表、p_m、模型、mask、种子；提供与 `reviews/verify_b_artifacts.py`、bootstrap 复算脚本一致的命令；C 的结论由 C 自己填写。
3. **正式 B-002 重跑**：E 冻结后用正式 data Release 的字节重跑，产生新的不可变 run；不要直接把 `20261104T002604_e3a5a42b` 当正式 B-002。
4. **补充实验按优先级**：主 run 验收后再跑 RF（S0/S2）、M=5/20（S0）、alpha=0.05；作为敏感性分析，不升格为主结论。
5. **如实记录不利结果**：阳性覆盖 0/8 与 0/38、B5/B6 不可用（6 个选择错误）、B4−B2 跨种子方向不一致；不得换种子、换容量、改阈值或删场景来制造优势。
6. **v2 情况**：若团队选 v2，按新协议重新实现/运行，不能把 v1 结果当确认性证据；旧 run 保留作历史。
7. **更新记录**：正式 run 被接收后才更新 registry、STATUS、CHANGELOG、handoffs/B；候选 run 标记为历史/预冻结。

## C 还需要做什么

1. **完成 C-001 人工复核**：现在 `03_C_E_REVIEW_AND_DAILY_UPDATE.md` 的 20 行仍是空白 PENDING；C 需逐例读原始小时文件，填 findings、姓名/日期、结论。自动化脚本 20/20 匹配不能替代本人签字。
2. **独立边界病例**：至少覆盖 onset=12/13/24/25、首观测即阳性、36 输入顺序/缺失指示、t≤12 截断与未来值泄漏；记录 A 的六个边界例是否可复现，不能只引用 A 的自报。
3. **独立审计 B 的 run**：逐患者集合、阳性漏放、阴性残余风险、配对 bootstrap 区间、5 批稳定性；核对零阳性覆盖和 B5/B6 门槛，不只核对聚合算术。
4. **完成 C-002**：逐条读原文核对引用；核实 Workshop 3 的入口、页数、模板、截止、AI 披露要求；官网日期与组内通知冲突时以主席/老师通知为准并记录核对日期。
5. **给 D 可引用清单**：只给已核对原文的文献；把“优于现有方法”等表述改为待检验假设；标明哪些结论不能写。
6. **C-003 真实指标复核**：正式 run 后独立复算主表与关键区间；在 `handoffs/C/`、STATUS 中填结论。
7. **许可/来源**：与 A/E 一起记录 PhysioNet 许可差异；不要把未核实来源写成结论。

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
3. 按 `paper/outline.md` 整合英文稿；引用只用 C-002 已核对清单。
4. C 核对表 2/2b 与摘要；E 检查摘要—正文—图表—结论一致；然后生成提交版 PDF 与材料清单。

## 明确禁止

- 不用 B 的候选 run `20261104T002604_e3a5a42b` 生成论文图或写结果。
- 不用 `paper/validation/` 的合成数字写摘要、正文、图表或汇报。
- 不手改 CSV/图表数字；不从聊天/截图复制数字。
- 不在精度门槛失败时静默改标签、时间窗、split、容量或阈值来制造有利结果。
