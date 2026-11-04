# 成员交付要求与验收矩阵

更新日期：2026-11-02。要求变化时改本页并写[CHANGELOG](CHANGELOG.md)，验收用[交付模板](../handoffs/TEMPLATE.md)。

统一交付仓库已切换为MarcoJIANG5203/BDDM-10。下列路径均相对此仓库，新的代码、数据版本、记录和PR不再提交到旧zsj-6/EI。

| ID / 生产者 → 接收者 | 必交内容 | 验收标准 | 时间点 |
|---|---|---|---|
| A-001 / A → B、C、E | data/processed/cohort.parquet、cohort_audit.json；splits/seed_2026.json到2030；生成代码、特征字典、标签核查；发布data版本包 | 每患者一行、36输入，划分互斥完备、医院正确；恢复提前6小时标签，特征<=12h，结局(12,24]；真实纳排/阳性数，C核病例和边界 | 11月3日数据门槛 |
| B-001 / B → A、C、D、E | src、configs、实验CLI、tests；方法/使用说明、合成包和验收报告 | B0—B6/S0—S4可运行；插补、共形、K公平、标签隔离、零分母、配对bootstrap可复核；模拟真实分开 | 程序与模拟已完成 |
| B-002 / B → C、D、E | 正式run完整目录：逐患者/p_m、指标/CI、覆盖/稳定性、mask/种子/阈值、环境/配置/manifest；clinical_results版本包 | 主效应B4-B2、增量B6-B5；共享模型/患者/mask/K；容量或风险器不足如实记；C独立核算，每个数字可追溯 | 11月6日跑通，10日核心，13日冻结 |
| C-001 / C → A、B、E | handoffs/C/标签和指标核查，独立核算代码 | 10阳性/10阴性和边界，手算一致；逐项写发现、处理和复核结论 | 11月3日标签，结果交付后核指标 |
| C-002 / C → D、E | 文献对照表、原文核对范围；投稿通道/截止/模板/页数/材料与通知证据 | 文献增量清楚；留存主席/老师11月20日前通知，不自行用公开冲突日期替代 | 11月3日前 |
| D-001 / D → 全组 | scripts/make_figures.py、paper/提纲、图表清单及来源索引 | 已验收结果生成图，禁止手改数字；可复跑且标注协议/数据/run | 并行推进，11月10日首图 |
| D-002 / D → C、E、全组 | paper/英文稿、图源、引用、最终PDF与材料清单 | 数字/引用可查；摘要正文图表一致；不用合成结果作临床结论或覆盖率代替安全性 | 11月16日全文，18日提交版 |
| E-001 / E → 全组 | 状态页、问题/变更、验收索引和整合版本 | 阻塞不遗漏，不替成员编造完成，main可供同步读取 | 持续维护 |
| E-002 / 统筹协助通讯作者 → 全组 | 最终PDF、稿号、回执、专场核对 | 通讯作者确认提交；专场正确；不承诺录用/检索 | 11月19日18:00内部目标，20日缓冲 |

每次记录生产者/接收人、日期、交付ID、协议/数据/commit、相对路径或bundle/run、完成/未完成、验证命令输出、问题和下一步。不要用截图或个人盘符作为唯一交付。

A新增原始队列提取脚本另建文件，衔接现有接口，不覆盖B已验证data.py/models.py。B不重划分患者。C独立核查而非复制汇总。D用已验收真实结果。E协调变更，不代替岗位实质验收。

## 2026-11-04 A retain-v1 review delivery

A owner explicitly confirmed using existing v1/full-r1 data and methods, with failed event-count limits. Current evidence is exposed in the A closeout; full40336-record raw PSV receipt is provided to C in the review bundle. Clinical data are removed from the current Git tree. Current registry entries remain prepared/draft; formal publication still requires the actual C/E decision and source-license clarification. See [A handoff](../handoffs/A/2026-11-04_A-001_closeout_EN.md) and [recovery instructions](A_DATA_REVIEW_2026-11-04.md). This updates delivery/evidence handling, not the v1 scientific algorithm, endpoint or split.
