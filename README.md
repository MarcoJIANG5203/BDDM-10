# BDDM-10 · T1 团队协作仓库

研究：**缺失临床数据中基于多重插补预测分歧的共形拒识评估**。

这里统一维护代码、协议、成员交付要求、进度和数据/产物版本。**11月4日已按用户授权完成A的v1候选五种子五场景主模型矩阵；正式验收/冻结仍待A、C、E完成。** 见[五种子候选摘要](reports/candidate-trials/20261104T002604_e3a5a42b/SUMMARY.md)、[先前单种子试跑](reports/candidate-trials/20261103T122334_93a9a266/SUMMARY.md)及[B接收记录](reviews/A_received_2026-11-03.md)。当前结果未显示稳定分歧优势，阳性覆盖为0，不能解释为临床安全证据；合成结果也不能用于临床结论。

下一步及证据见[B原因诊断](reports/diagnostics/20261103T122334_93a9a266/DIAGNOSIS.md)：已复现阳性覆盖零的阈值机制和五批排序/稳定性；A确认数据、C独立审核、E协调冻结决定。

## 每次同步后先读

| 入口 | 用途 |
|---|---|
| [当前状态](collaboration/STATUS.md) | A—E进展、阻塞和下一项交付 |
| [交付要求](collaboration/HANDOFFS.md) | 文件路径、接收人和验收标准 |
| [数据与产物同步](collaboration/DATA_SYNC.md) | 发布、下载、SHA256校验 |
| [变更记录](collaboration/CHANGELOG.md) | 协议、数据、接口和要求变更 |
| [协作规则](CONTRIBUTING.md) | 分支、提交和动态更新要求 |
| [版本索引](artifacts/registry.json) | Release标签、资产与发布状态 |

成员交付时一起更新这些文件并合并main，其他人`git pull`后即可读取。状态依据真实文件与验收更新，不自动从聊天中推断。

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
