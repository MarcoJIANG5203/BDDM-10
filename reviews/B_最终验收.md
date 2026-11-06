# B岗位最终验收

日期：2026年11月2日，北京时间。验收范围：B核心方法程序、合成数据验证、参数与逐患者产物、交接和方法素材。**以下为当时的历史验收，真实临床实验尚未运行、A正式数据仍待交付均指截至该日期。** 2026-11-04的正式输入B-002交付见[新记录](../handoffs/B/2026-11-04_B-002_formal_v1.md)，不回写本历史验收，也不将合成验收作为临床验收。

## 1. 验收结论

本轮授权的程序与验证任务已完成。B0—B6、S0—S4、主线五种子、M10/10轮、容量40%/60%/80%、批次与冻结阈值评价、患者配对bootstrap和5批测试补全稳定性均有可运行实现。RF、M5/20、alpha.05补充入口已实际运行。

独立代码审查未发现Critical或Important。发现的唯一Minor（训练34项生理列全空）已用先失败的测试复现并修复，退化为Age/Gender+36个缺失指示共38列，未关闭问题为0。报告：`reviews/B_independent_review.md`。

## 2. 最终测试证据

```powershell
python -m pytest -q
```

主代理最终执行：**18 passed in 21.80s，退出码0**，日志 `reviews/B_final_tests.log`。测试涵盖共形有限样本边界、空/单/双集合、相同容量与平局、零分母、手算指标、患者配对重抽、插补观测值不变/可复现、全缺失列、M权重、掩码、数据划分/标签隔离、Parquet读取、失败保留产物及端到端运行。

测试驱动证据保存在 `reviews/B_RED*.log`。独立手算夹具为 `reviews/B_hand_calculations.json`，对应 `tests/test_independent_audit.py`，不从实施代码反推期望值。

## 3. 最终运行目录（以此处为准）

| 项目 | 完整主线模拟验收 | 全部补充模拟验收 |
|---|---|---|
| run_id | 20261102T063118_fa76f8a8 | 20261102T063118_bdf6797a |
| 目录 | results/synthetic/20261102T063118_fa76f8a8 | results/synthetic/20261102T063118_bdf6797a |
| 状态 | completed / synthetic=true | completed / synthetic=true |
| 配置 | reviews/B_full_matrix.yaml | configs/demo.yaml加全部补充开关 |
| 范围 | 5种子×5场景，主种子1000次配对bootstrap，S0固定模型5批 | RF S0/S2、M5/20 S0、alpha.05五场景，含主线 |
| 患者方法输出行 | 172,800 | 69,120 |
| p_m概率行 | 59,400 | 24,360 |
| 独立核算指标行 | 1,440 | 576 |
| bootstrap条目 | 60 | 168 |
| 有效/无效重抽总数 | 60,000 / 0 | 16,800 / 0 |
| 两两稳定性条目 | 1,600 | 320 |
| 完成时间 | 2026-11-02 14:32:07，北京时间 | 2026-11-02 14:31:43，北京时间 |

这些是输出记录数量，不能理解为真实临床样本数。合成输入为医院A 800人、医院B 120人；同一人会在方法、容量、批次和种子中重复出现。两次运行的warnings.log均为空。运行耗时只代表该模拟规模，不推算正式队列性能。

命令与日志：

```powershell
python scripts/run_experiments.py --config reviews/B_full_matrix.yaml
python scripts/run_experiments.py --config configs/demo.yaml --rf --m-sensitivity --alpha-sensitivity
```

日志为 `reviews/B_full_matrix.log`、`reviews/B_final_supplements.log`。旧run全部保留作开发记录；源码最后修复后的验收以本表两个run为准。

## 4. 独立产物核算

`reviews/verify_b_artifacts.py`不导入实验的metrics实现，直接读取逐患者CSV重算接受人数、错误人数、危险漏放、阴性残余风险和覆盖。还检查：

- B2—B6共享概率、分歧、集合与缺失比例，同容量的K完全一致。
- 非单元素集合不能接受，y_pred=-1；B0实际M=1。
- p_m条数与M一致，mean、ddof=1标准差和类别翻转均能重建。
- q在不同测试插补批次间固定，输出键唯一，外院分配正确。
- 最终运行与当前12份src/scripts源文件哈希一致，配置、数据、审计、split和每项产物哈希匹配。

两个报告均通过：`reviews/B_acceptance_matrix.json`、`reviews/B_acceptance_supplements.json`。分别核查45/25项产物哈希及5/1份split哈希。主代理共独立核算2,016行汇总指标。

可复核命令：

```powershell
python reviews/verify_b_artifacts.py results/synthetic/20261102T063118_fa76f8a8
python reviews/verify_b_artifacts.py results/synthetic/20261102T063118_bdf6797a
```

Parquet接口已通过真实文件读写测试；本地可信模型重载复现也已通过，证据见 `reviews/B_reload.log` 及独立代码审查报告。环境直接依赖及必要传递依赖共18项锁在requirements-lock.txt，每次manifest另存Python和运行依赖版本。

## 5. 交付入口

- `B_程序使用与交接.md`：运行方法、模块、结果字典、B交C/D的规则。
- `B_方法说明_论文素材.md`：中文方法口径、指标分母和英文方法段落。
- `docs/A到B_数据交接说明.md`：正式队列、五份划分、审计字段与A/C仍需完成的核验。
- `reviews/B_implementation_report.md`：实现API、抽样种子、裁剪分母和详细RED/GREEN记录。

## 6. 尚待A交付的真实研究工作

正式队列、五份固定患者划分及cohort_audit.json尚未交付。当前正式入口因缺少cohort.parquet退出并保存failed manifest，未用合成队列冒充临床实验。

A/C必须核对原始小时记录、提前6小时标签恢复、第12/24小时边界、队列纳排、医院映射和阳性数量。B的schema/审计声明检查不证明这些实质条件成立。

正式数据到位后，先验收主种子S0小规模运行及资源占用，再开展临床主实验，交C独立核算、D制图写结果。B5/B6可能因事件不足不可用、共形候选池也可能不足目标容量，均按实际记录。合成结果不能支持临床优势、安全性、覆盖保证或分歧增量结论。
