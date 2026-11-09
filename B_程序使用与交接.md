# B岗位程序使用与交接

2026-11-04更新：A正式技术数据`a-data-v1-20261104-r1`已发布并交付内容冻结。当前B-002新run、小型摘要、完整版本包和独立验收待办见[正式交接](handoffs/B/2026-11-04_B-002_formal_v1.md)及[结果索引](reports/clinical-v1/README.md)。本轮主线与规定补充并行计算、一起交C/E核验；这不改变接收人独立签认要求。以下原程序/合成验证说明保留，原18项算法测试为历史范围，当前仓库完整基线32项通过。

## 1. 从这里运行

在PowerShell中进入项目目录：

```powershell
cd BDDM-10
python -m pip install -r requirements-lock.txt
python -m pytest -q
python scripts/create_demo_data.py --output data/synthetic
python scripts/run_experiments.py --config configs/demo.yaml
```

合成数据生成器构造模拟特征和标签，不下载或模拟还原PhysioNet原始患者。默认demo仍采用M=10、10轮补全、alpha=0.10和40%/60%/80%容量；仅使用主种子并将bootstrap降为100次，以验证程序。

正式数据接入后运行：

```powershell
python scripts/run_experiments.py --config configs/protocol_v1.yaml
```

正式配置为5个固定划分种子、S0—S4及主种子1000次配对bootstrap。先按《docs/A到B_数据交接说明.md》核查输入，不能直接把synthetic配置的标识改成clinical使用。

补充实验独立开关：

```powershell
python scripts/run_experiments.py --config configs/demo.yaml --rf --m-sensitivity --alpha-sensitivity
```

正式运行把上面配置改为protocol_v1.yaml。随机森林只运行S0/S2；M=5/20只在主种子LR的S0运行；alpha=0.05只在主种子LR、M=10运行。M变化会重建相应预测与校准流程；5批测试补全固定已训练模型、q和筛选规则，用来评价另一种稳定性。

目前所有命令都从项目根目录运行，配置中的相对路径也以该工作目录解释。正式运行可能耗时较长；各次运行均新建目录，避免覆盖先前结果。

## 2. 程序入口和责任

| 路径 | 内容 |
|---|---|
| configs/protocol_v1.yaml | 正式主线参数与A输入路径 |
| configs/demo.yaml | 合成演示参数 |
| src/data.py | 读取A交付及schema/split/审计声明检查 |
| src/imputation.py | 训练集拟合、患者稳定随机种子、随机补全和裁剪诊断 |
| src/models.py | 共享分类器、1/M权重、selection AUPRC选C、预测汇总 |
| src/conformal.py | 有限样本分位数、候选集合 |
| src/selection.py | 同容量排序、冻结阈值、B5/B6错误评分器 |
| src/scenarios.py | S0—S4掩码 |
| src/metrics.py | 指标、分层覆盖和配对bootstrap |
| src/experiment.py | 执行、模型存储、逐患者输出和运行记录 |
| scripts/create_demo_data.py | 独立生成合成演示输入 |
| scripts/run_experiments.py | 主命令入口 |
| tests/ | 算法边界、接口、独立手算与端到端验证 |

代码中的data.py/models.py是B本轮为接通实验提供的共享接口实现。A后续衔接时保留已验证的算法和权重口径，不以同名文件直接覆盖。

## 3. B交给C/D的结果

每次运行保存在 `results/synthetic/<run_id>/` 或 `results/clinical/<run_id>/`。先检查manifest.json的synthetic和run_status；failed运行的残留文件不能当作完整实验。

| 文件 | 用途 |
|---|---|
| patient_predictions.csv | 每种方法、容量、模式、患者的概率、集合、接受状态、真实标签 |
| p_m.csv | 每位患者的各次补全概率，用于复核mean/std/翻转 |
| metrics.csv | 指标、分子分母相关计数、实际接受率、候选池不足情况 |
| bootstrap_differences.csv | B4-B2、B6-B5风险差、95%区间、有效/无效重抽次数 |
| coverage_strata.csv | 原始集合的总体、类别与缺失分层覆盖 |
| thresholds.csv | selection冻结的分数阈值、平局规则和q依赖 |
| stability.csv | 5批测试补全之间三态两两不一致率 |
| method_status.csv | B0—B6可用性；B5/B6样本不足时的原因 |
| model_parameters.json | C选择依据、删除列、风险器状态及抽样解释 |
| imputation_seeds.csv | 患者、角色、批次和draw的可重建种子 |
| clipping.json / masks.json / timing.json | 裁剪、掩码统计和预测时间 |
| masks/ | 每位患者被额外隐藏的生理化验位置 |
| models/ | 已拟合模型、插补器、q与冻结规则的本地joblib文件 |
| config.yaml / manifest.json | 配置快照、源代码/数据/划分哈希、版本、起止时间和运行状态 |
| warnings.log / error.log | 运行警告；出错时另存完整异常 |

患者输出是长表，同一患者会因方法、容量、批次和场景重复出现。统计人数时必须先固定实验条件，不能把这些行当成独立患者相加。跨种子同一患者也不构成新的临床病例。

MI方法B1—B6共享p_m、平均概率、分歧、原始集合和同一场景缺失比例；B0有独立简单插补预测器与q。p_m的predictor字段区分二者。B0实际M=1；source_M标记它所属的MI任务（10或补充5/20），防止不同任务的简单基线混淆。连接预测和p_m时保留source_M、predictor及其他实验条件；B1—B6的predictor均对应MI。配对比较使用同一运行、split_seed、model、source_M、M、alpha、scenario、imputation_batch、selection_mode、target_acceptance下的方法结果。非单元素集合的y_pred=-1，不能当作二分类结论；B0的p_std固定记0表示确定性填充，它不是用单个样本计算的标准差。MI分歧仍严格采用ddof=1。

batch表示每批重新分配K人的容量评价；frozen表示应用selection冻结阈值，其实际接受率允许变化。B0/B1接受全部单元素池，不应当作目标容量相同的B4增量对照。对未达到目标容量的结果，必须同时报告pool_size和actual_acceptance。

所有比例的零分母按NA处理，CSV中通常为空值；不要用0填充后作图或计算均值。C仍需用独立实现复核临床主表。方法口径及可供D整合的英文段落见《B_方法说明_论文素材.md》。

## 4. A交付后怎样推进

1. A交正式患者表、5份划分、特征/标签说明和审计；C核对时序和边界案例，E记录版本。
2. B检查schema、ID互斥、医院分配、种子、配置和文件哈希，先完成主种子LR S0小规模全流程。
3. 复核逐患者记录和指标，再运行正式5种子5场景。所有对照共用输入、掩码和规则，不根据测试效果改标签或调容量。
4. 运行协议限定的补充开关；可与主线并行计算，保留独立run。主线与补充完成B计算核验后交C/E分别验收，D依据已签认run生成图表和论文数字。

## 5. 验证记录

最终验收命令、结果目录、通过数量和剩余限制记录在 `reviews/B_最终验收.md`。18项测试通过；已实际跑通合成数据的五种子五场景主线及全部补充，并独立核算2,016行指标。该记录是本轮完成范围的依据，不代表真实临床研究已完成。
