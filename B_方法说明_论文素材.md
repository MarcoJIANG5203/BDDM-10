# B岗位方法说明与论文素材

日期：2026-11-02。依据《T1_统一实验说明_v1.md》。本文件提供方法口径；运行和验收情况见《B_程序使用与交接.md》。A尚未交付正式数据，合成数据输出不得用于论文结果。

## 1. 研究对象与独立性

每位患者是一个分析单位。A负责冻结第12小时特征、之后至第24小时结局和患者划分；B接收后只读，不重建标签或调整纳排。训练、规则选择、校准和测试互斥，外院患者只用于冻结后的评价。

插补函数只读取输入特征，不接收结局。训练标签用于预测模型，规则选择标签用于超参数选择和B5/B6错误评分器，校准标签用于共形分位数。测试标签只在保存评价结果时合并。列白名单可以阻止已知非输入列进入模型，但不能证明A提供的聚合值没有使用未来信息；该项仍需A/C原始数据审计。

## 2. 多次插补与共享预测器

生理化验变量共有34项；Age、Gender分别使用训练中位数、众数填充。仅由训练数据决定删除哪些完全缺失的生理数值列，其缺失指示仍保留。原始36项输入均附加缺失指示，B3的缺失比例仅以34项生理化验变量为分母。

训练输入拟合BayesianRidge条件模型构成的随机链式方程插补器，运行10轮。每位患者生成M=10份补全；只裁剪缺失位置生成的值，界限取训练观测最小值和最大值，保留原始观测。抽样是实用的条件高斯抽样与裁剪，不称为真实缺失机制的正确后验。

M份训练副本共用一个分类器，每份权重1/M。标准化仅由训练副本拟合。逻辑回归C从0.1、1、10中按照规则选择集平均概率的AUPRC选择，平局选小C；B0另训练简单插补模型，但沿用同一个C。多次补全不会增加独立患者数。

固定分类器对每份补全给出阳性概率p_m。平均概率为p_mean；分歧D为p_m的样本标准差（ddof=1）。类别翻转指同一患者在0.5阈值两侧都出现预测。低D不意味着正确，高D也不预设必然错误。

## 3. 共形候选集合

候选标签y的非一致性分数为1-p_mean(y)。校准样本数n，取排序位置k=ceil((n+1)(1-alpha))；k>n时阈值q为正无穷。满足分数<=q的标签进入集合。主alpha=0.10。

空集合、双元素集合均拒识，只有单元素集合进入自动处理候选池。原始集合覆盖率分母是全部测试患者。后续筛选的接受者错误率、人工缺失偏移表现和外院表现均是经验指标，不自动享有标准共形的边际覆盖保证。

## 4. 容量公平与条件增量

B1接受全部单元素集合。B2—B6共用同一多次插补预测器、共形阈值和候选池。给定目标比例c，总患者数N，接受人数K=min(floor(cN),N_single)。候选池内分别按以下分数从低到高选K人，平局按固定患者ID哈希决定。

| 方法 | 排序分数 |
|---|---|
| B2 | 1-max(p_mean,1-p_mean) |
| B3 | 34项生理化验变量的缺失比例 |
| B4 | 多次插补概率样本标准差D |
| B5 | 由B2、B3分数拟合的错误风险 |
| B6 | 由B2、B3和D拟合的错误风险 |

B5/B6用规则选择集全部患者的基础分类错误作为目标，特征在该集标准化，L2逻辑回归C=1。该集错误或正确不足20例时，记录不可用原因；不以常数预测器假装完成增量评价。

主效应是同一c下B4风险减B2风险；B6减B5检验D的条件增量。候选池不足cN时，各策略都接受整个池，应报告实际接受比例和评分没有筛选空间。

批次评价允许查看当前批次输入分数排序。补充部署评价把规则选择集分数阈值冻结，应用到测试时不再调节容量；最终校准q用于界定单元素候选池，必须记录这项依赖。其接受比例可能因偏移或并列分数而变化。

## 5. 缺失压力与统计口径

S0为内部自然缺失，S1/S2在测试患者原本观察到的34项生理化验聚合值上随机隐藏10%/30%，S3隐藏官方第9—34列的26项化验值，S4为医院B自然缺失。压力场景保持训练和校准不变；新掩码改变后重新生成缺失指示、补全和预测。所有策略共用同一场景掩码。

| 指标 | 分子 | 分母 |
|---|---|---|
| 接受比例 | 接受人数 | 全部测试人数 |
| 选择性风险 | 接受且错误人数 | 接受人数 |
| 危险漏放比例 | 真实阳性、接受且预测阴性人数 | 全部真实阳性人数 |
| 阴性接受残余风险 | 真实阳性、接受且预测阴性人数 | 接受且预测阴性人数 |
| 集合覆盖 | 真实标签在原始候选集合中的人数 | 全部测试人数 |

零分母记NA，并保留分子、分母。缺失分层使用[0,1/3]、(1/3,2/3]、(2/3,1]，另按真实类别报告覆盖和样本数。

主种子的风险差区间按患者配对bootstrap计算。每次共同重抽N个患者副本，对每种策略重新排序、重新计算K；重复患者占据独立抽样位置。该区间条件于已拟合模型和已冻结规则，不包含重新训练的全部不确定性。5次患者划分仅作全流程稳定性补充，不混为独立临床队列。

重复测试补全固定训练模型、最终q、辅助错误评分器和部署阈值，对5批输出比较阴性接受、阳性接受、拒识三状态。批次容量下的状态还会受到同批其他患者影响，需与冻结阈值结果分别解释。

## 6. English methods draft

We evaluate whether prediction variability induced by multiple imputation provides incremental information for selective classification beyond confidence and missingness burden. Each patient contributes one record, with the feature window, outcome definition, and patient partitions fixed before model evaluation. The training, rule-selection, calibration, and internal test partitions are disjoint; a second hospital is reserved for external evaluation.

A stochastic chained-equation imputer is fitted using training features only. Bayesian ridge conditional models are used for ten iterations, and ten completed versions are generated per patient. Age and sex are imputed using the training median and mode, respectively. Physiological variables entirely missing in training are removed from the numerical inputs while their missingness indicators are retained. Generated values at missing positions are clipped to the observed training ranges. This practical stochastic imputation procedure is not assumed to recover the true missing-data distribution.

A shared logistic regression classifier is trained on the completed training records with weight 1/M per replicate. The regularization parameter is chosen from 0.1, 1, and 10 using average precision on the rule-selection partition. For each patient, imputation predictions are aggregated by their mean, and disagreement is measured by the sample standard deviation of the positive-class probabilities. Replicates are never treated as independent patients in evaluation or resampling.

Split conformal prediction uses the score one minus the predicted probability of each candidate label. The calibration threshold is the ceil((n+1)(1-alpha))-th ordered calibration score, with an infinite threshold when the index exceeds n. Only singleton prediction sets are eligible for automatic acceptance. Set coverage is evaluated over all test patients, including those with empty sets.

At a prespecified acceptance target c, each ranking strategy accepts K=min(floor(cN),N_single) patients from the shared singleton pool. We compare rankings based on confidence uncertainty, missingness burden, imputation disagreement, and two error-risk models fitted on the rule-selection partition. The latter models use confidence uncertainty and missingness burden, with disagreement added to the second model. Ties are resolved by a fixed hash of patient identifiers. We additionally evaluate thresholds frozen on the rule-selection partition and report their realized test acceptance rates.

The primary contrast is selective risk under disagreement ranking minus selective risk under confidence ranking at c=0.60. We report false-negative automatic acceptance among all outcome-positive patients, residual outcome risk among accepted negative predictions, and original prediction-set coverage. Paired patient-level bootstrap resamples repeat the capacity allocation within each resample. External and missingness-shift evaluations are empirical stress tests; we do not extend the standard marginal conformal guarantee to the accepted subset or shifted populations.

以上为方法素材，不包含实验结果、效果方向或统计显著性；论文整合时须按最终代码审计与A交付情况核对。
