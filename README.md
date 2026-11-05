A formal technical data: [a-data-v1-20261104-r1](https://github.com/MarcoJIANG5203/BDDM-10/releases/tag/a-data-v1-20261104-r1). See [A freeze handoff](handoffs/A/2026-11-04_formal_data_freeze_EN.md). E approval is user-reported; official licensing conflict remains unresolved. This is dataset content freeze, not clinical result acceptance.

# BDDM-10 · T1 团队协作仓库

研究：**缺失临床数据中基于多重插补预测分歧的共形拒识评估**。

This repository tracks protocol, scientific code and reviewable delivery evidence. A's formal technical data version is published and content-frozen; B/E technical receipts and the newer C006 submission are indexed in [the 5 November handoff](handoffs/A/2026-11-05_A_daily_closeout_EN.md). Use [current recovery instructions](collaboration/A_SOURCE_REPLAY_2026-11-05.md) and [current status](collaboration/STATUS.md). Source licensing remains unresolved; A content freeze does not grant joint C/E result acceptance.

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

本次A交付验证环境为Python 3.14.7，科学依赖保持锁定；历史B记录中的Python版本保留作溯源。macOS/Linux使用`source .venv/bin/activate`。仓库附有明确标记的合成输入，可直接运行demo。重新生成可运行`python scripts/create_demo_data.py --output data/synthetic`，它会重写本机demo配置路径，不要提交个人绝对路径。

本次A交付整合测试56项通过（原B32项、A提取15项、A原始回执9项），证据见reviews/A_closeout_tests_2026-11-04.json及对应日志；D分支的绘图测试不在此次范围内。

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
