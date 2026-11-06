# BDDM-10 · T1 团队协作仓库

**2026-11-06最新：B/E已接收C-006，正式两run的1,140指标/78区间复跑零失败；已记录有条件算术/协议接受和限定数值结果冻结，D可按原门槛重新生成正式图文。** [本轮E决定](handoffs/E/2026-11-06_E-001_C006_result_scope.md)、[B接收](handoffs/B/2026-11-06_B_C006_receipt.md)、[验收索引](collaboration/ACCEPTANCE_INDEX.md)。D现有正式run草稿含Fig5/结果段落，正式稿/PDF与实际投稿未完成。下文上一轮“C新run结论待完成”等表述仅为历史快照。接受范围不包括临床安全、方法优势或全量原始标签独立核验；原v1限制及许可冲突保留。

研究：**缺失临床数据中基于多重插补预测分歧的共形拒识评估**。

## 上轮交付背景（2026-11-05历史快照）

这里统一维护代码、协议、成员交付要求、进度和数据/产物版本。**A正式技术数据 `a-data-v1-20261104-r1` 已发布并交付内容冻结记录；B已从正式字节完成B-002主矩阵和规定补充，1,140行指标/78个配对区间独立重算通过。E已完成技术交付与公平性范围接收，继续原v1有限事件数分析；C对两份新run的独立结论、联合结果签认及D正式图稿仍待完成。** 见[E本轮交接](handoffs/E/2026-11-05_E-001_formal_v1_integration.md)、[验收索引](collaboration/ACCEPTANCE_INDEX.md)及[正式结果索引](reports/clinical-v1/README.md)，完整包同步状态以[registry](artifacts/registry.json)为准。此前候选run完整保留。正式新run同样未显示稳定分歧优势，阳性覆盖为0，B5/B6不可用；不能解释为临床安全证据，合成结果也不能用于临床结论。

正式输入见[A交接](handoffs/A/2026-11-04_formal_data_freeze_EN.md)与[A内容冻结](reviews/freeze/A_formal_data_freeze_v1_2026-11-04.json)。A历史交接的E批准为转述，官方许可元数据冲突尚未澄清；E本轮授权决定另行记录，不追认历史签名或替代C科学验收。本聊天曾参与B，E复跑C代码不冒充C本人签认。投稿按用户确认的11月20日前安排，其他通知/入口/联系资料不再催补，见[排期](collaboration/SUBMISSION_PLAN.md)。此前[B原因诊断](reports/diagnostics/20261103T122334_93a9a266/DIAGNOSIS.md)仅解释候选数值机制。

## 每次同步后先读

| 入口 | 用途 |
|---|---|
| [当前状态](collaboration/STATUS.md) | A—E进展、阻塞和下一项交付 |
| [交付要求](collaboration/HANDOFFS.md) | 文件路径、接收人和验收标准 |
| [数据与产物同步](collaboration/DATA_SYNC.md) | 发布、下载、SHA256校验 |
| [变更记录](collaboration/CHANGELOG.md) | 协议、数据、接口和要求变更 |
| [接收与验收索引](collaboration/ACCEPTANCE_INDEX.md) | 每项交付的实际接收范围与剩余签认 |
| [任务与阶段安排](collaboration/ISSUES.md) | C/D后续任务与[投稿排期](collaboration/SUBMISSION_PLAN.md) |
| [协作规则](CONTRIBUTING.md) | 分支、提交和动态更新要求 |
| [版本索引](artifacts/registry.json) | Release标签、资产与发布状态 |

成员交付时一起更新这些文件并提交岗位分支；当前按用户要求不合并main，其他人同步相应分支或固定commit读取。状态依据真实文件与验收更新，不自动从聊天中推断。

## 开始使用

```powershell
git clone https://github.com/MarcoJIANG5203/BDDM-10.git
cd BDDM-10
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-lock.txt
python -m pytest -q
python scripts/run_experiments.py --config configs/demo.yaml
```

本地验证环境为Python 3.14.5。macOS/Linux使用`source .venv/bin/activate`。仓库附有明确标记的合成输入，可直接运行demo。重新生成可运行`python scripts/create_demo_data.py --output data/synthetic`，它会重写本机demo配置路径，不要提交个人绝对路径。

当前完整测试32项通过（原科学验证18项，同步及跨机器路径14项），证据见reviews/repository_tests.log；新克隆也执行完整测试。

这份固定合成验证包有随Git同步的备用ZIP，以下命令会先校验并使用本地副本，无需额外下载。对于只有Release的其他版本，先安装GitHub CLI并`gh auth login`。

```powershell
python scripts/sync_artifacts.py list
python scripts/sync_artifacts.py fetch b-synthetic-20261102
python reviews/verify_b_artifacts.py results/synthetic/20261102T063118_fa76f8a8
python reviews/verify_b_artifacts.py results/synthetic/20261102T063118_bdf6797a
```

Git同步代码/文档与本次固定合成包备用副本，Release管理完整数据/产物版本。私有仓库成员需要相应访问权限。

## 实验入口

- [统一实验v1](T1_统一实验说明_v1.md)、[团队执行计划](T1_组内执行计划.md)、[技术约定](T1_技术交接约定.md)。
- [B程序交接](B_程序使用与交接.md)、[B方法与英文素材](B_方法说明_论文素材.md)、[B最终验收](reviews/B_最终验收.md)。
- [A到B的数据格式](docs/A到B_数据交接说明.md)、[可阅读验证摘要](reports/validation/README.md)。

根目录保留原始选题、会议与参考资料供追溯；当前实施口径以统一协议和协作状态页为准。
