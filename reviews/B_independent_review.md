# B独立全流程复核

日期：2026-11-02。只读审查实现；未修改src、scripts、configs或tests。依据B_implementation_brief、T1_统一实验说明_v1、T1_技术交接约定逐项核对。非Git工作区，open-code-review技能明确排除此情形，未运行OCR或向外部LLM发送源码。

## 结论

- Spec compliance：本轮“程序实现＋合成验证”通过，唯一Minor已修复并独立复核关闭；最终全配置合成运行已完成，当前源码hash核对通过。正式临床实验尚未完成，也不能由本审查确认原始标签及时间窗。
- Code quality：通过。当前未关闭的Critical、Important、Minor均为0。单文件编排较紧凑，后续扩展宜拆分，但不以风格偏好阻断验收。
- 当前全量Python源码已逐个阅读；不只依赖通过测试或实施者自查。初审16项测试日志及修复后18项测试日志已查阅，未重复同码整套测试。

## 发现

Critical：无。Important：无。Minor：原1项已关闭。

已关闭Minor — 原src/imputation.py:30在训练全部34项生理列为空时直接抛错。修复后的src/imputation.py:30—40初始化空边界数组和chain_=None，仅active_非空时拟合；transform的posterior分支检查chain_非空后才迭代。空(n,0)生理数组与两个人口学输入及36个原始缺失指示正常拼接，得到38列；即使测试期出现原训练全空列的观测值，数值仍删除，其缺失指示保留真实状态。非空active_路径的拟合和采样逻辑保持不变，median路径也不访问空chain_。

复核证据：tests/test_protocol.py新增手算边界测试验证shape=(3,2,38)、Age中位数30、Gender众数1、全36指示、所有数据角色、测试HR观测不重引入数值列以及dropped/填充/裁剪计数。reviews/B_RED_all_missing.log明确记录原抛错位置导致失败；reviews/B_GREEN_all_missing.log为18 passed in 18.96s。该修复逻辑及测试期望经过只读检查，Minor关闭；未重复完整测试。

## 独立检查内容

- 共形分位数实现使用ceil((n+1)*(1-alpha))，超出样本数为inf；空/双集合拒识，单集合预测有效，覆盖分母为所有患者。
- B2—B6共享p、集合、pool及batch K；排序只看预定分数和患者哈希，不使用测试标签。B0独立中位数模型及q，M字段为1，source_M区别所属任务。
- 风险器只在selection全部患者上学习基础分类错误；20正确/20错误门槛及不可用状态真实存在。冻结阈值来源selection，使用最终q的依赖已记录；测试不调整阈值。
- bootstrap共同患者索引重抽，重复副本独立占位，重新计算K和排序；frozen明确复用固定接受状态；有效/无效次数均保存。危险漏放、残余风险和选择风险分母正确，零分母为NA。
- 插补fit无y输入；34生理列训练全空逐列删除、指示保留；Age/Gender采用训练中位数/众数；观测值原样保留；后验链10轮BayesianRidge、缺失位置最终裁剪且计数可解释。输出ddof=1标准差，副本权重1/M。标准化仅训练副本；C在selection平均概率AUPRC选定，并给B0共享。
- 随机流按split/role/ID/batch/draw稳定哈希建立，变换时排序并还原位置；不依赖方法调用顺序。S1/S2只隐藏原观察生理值；S3官方9—34列，共26列；掩码文件和统计保存。
- 白名单特征、全局ID唯一、拆分互斥完备、医院身份、train/selection两类、审计基本时间声明及纳排计数均检查。额外列不会进入模型，但loader不可能证明原始小时标签正确。
- patient_predictions字段满足技术交接最小schema，附加run/alpha/selection_mode/synthetic等；p_m、种子、耗时、裁剪、缺失、阈值、模型、CI、稳定性均有保存路径。
- 正式默认五种子、五场景、M10、10轮、1000 bootstrap；RF/M/alpha补充不是空壳。预测长表及种子表流式写出，文件hash按1MiB分块，避免随整个实验累计患者长表占用内存。训练draws仍为O(M*N_train*P)，模型拟合有数组副本；本次未声称已做正式规模RSS/耗时测量，A交付后应先单种子测量资源。

## 当前源码与运行证据

初审时，初始快照reviews/B_review_package.txt之后变化的Python文件为src/data.py、src/experiment.py、tests/test_protocol.py；本报告已审阅新增审计计数检查、流式输出、失败保留证据等代码。第二轮又独立审阅src/imputation.py及对应测试的唯一Minor修复。旧run 20261102T061906_ff1f98c8仅作历史证据，不能替代最终源码验证。

初审时独立逐项比较以下两个manifest的source_hashes与当时src/scripts文件SHA256：均无差异，状态均completed。它们早于上述Minor修复，现作为历史运行证据；最终新run的hash复核待主代理提供运行ID。

- results/synthetic/20261102T062332_98484fc5：主线。
- results/synthetic/20261102T062332_a3f5dbb9：全部补充开关开启。

实际读取补充metrics分组确认：LR M10 alpha.1含S0—S4、S0批次0—4；LR M10 alpha.05含S0—S4；LR M5和M20仅S0；RF M10仅S0/S2。稳定性每组恰10个批次对。

额外独立重载主线joblib，使用保存config定位合成数据，重新变换S0测试患者并预测，与B1/batch0已保存p_mean最大绝对误差5.551115123125783e-17（CSV浮点往返精度）。这验证了当前可信本地模型产物可重载复算。未安装或改动实施依赖。

后续若再次修改源码，应重新对照最终运行hash并做针对性验证；上述结论不覆盖尚未交付的A真实数据及其原始时间标签审计。

## 最终验收证据（Minor修复后）

最终主线：results/synthetic/20261102T063118_fa76f8a8。覆盖5个split种子×5场景，主种子1000次bootstrap及S0五批。manifest为completed；本复核者重新计算当前12个src/scripts文件SHA256，与该manifest全部相符，无差异。manifest包含5份split哈希及45份产物哈希。

最终补充：results/synthetic/20261102T063118_bdf6797a。manifest为completed；本复核者重新计算当前12个src/scripts文件SHA256，与该manifest全部相符，无差异。manifest包含1份split哈希及25份产物哈希。

已核阅主代理独立产物审计摘要reviews/B_acceptance_matrix.json及reviews/B_acceptance_supplements.json：主线172800患者方法行、59400条p_m、1440汇总行；补充69120患者方法行、24360条p_m、576汇总行。摘要记录产物、当前源代码/配置/数据/split哈希、唯一输出键、医院身份、单集合资格、独立计数与比例、同批K、共享MI预测与集合、p_m均值/ddof=1标准差/翻转、B0 M=1以及跨批q冻结均通过。本轮只核对摘要和源码hash，没有冒称重新执行全部产物审计。

最终测试日志reviews/B_final_tests.log显示18 passed in 21.80s。本复核者未重复同码测试或模型运行。最终判定保持：协议符合性通过，代码质量通过，未关闭Critical/Important/Minor均为0；验收范围严格为程序与合成数据验证。
