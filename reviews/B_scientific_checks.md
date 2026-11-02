# B科学口径复核清单

2026-11-02；主代理独立于实施代码整理，完成状态依据最终运行证据更新。

1. 不能由列名验证第12小时窗口与恢复起病时刻：正式数据依赖A/C原始审计，不以程序schema校验冒称完成标签核验。
2. B0单列独立模型和共形池；B2—B6共用MI概率、q、掩码与K，B1作为全池参照。
3. 冻结阈值可以依赖最终q界定的selection单集合池；这一依赖需保存，不修改q，不使用测试标签或测试容量调参。
4. 只有缺失生成值被裁剪，外院已观测越界数值仍保留；裁剪统计应解释为条件链过程与最终补全位置的哪一种分母。
5. 默认sklearn随机transform对调用顺序与行序敏感，需要患者级稳定随机数或等价方法，并测试重排、分块和重复调用。
6. M训练副本权重总和须等于原患者数；bootstrap抽患者而不是副本，且每个重抽批次重新计算K。
7. selection不足20正确或20错误时B5/B6不可用；demo若人数太少只能测到不可用路径，因此另需可用路径的直接测试或足够大的合成选择集。
8. 共形q>0.5时可能单集合池不足容量；必须报告而不改变alpha。q为inf时所有集合双元素、接受率0、风险NA。
9. 外院、缺失压力和筛选后错误均不自动继承边际覆盖保证。
10. M敏感性与固定训练模型的重复测试补全含义不同，输出应能区分experiment_type或等效标记；重复batch保持q、风险器和部署阈值不变。

## 证据来源

- 本地协议：T1_统一实验说明_v1.md、T1_技术交接约定.md。
- PhysioNet官方特征表：https://physionet.org/content/challenge-2019/1.0.0/ （第1—8列生命体征，第9—34列26项化验）。
- 官方插补API：https://scikit-learn.org/stable/modules/generated/sklearn.impute.IterativeImputer.html （条件Gaussian后验，sample_posterior=True，max_iter=10，实验性API）。
- 官方LR API：https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html （sample_weight与训练样本逐一对应）。
