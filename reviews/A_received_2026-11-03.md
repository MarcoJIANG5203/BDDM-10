# B接收A候选数据 · 2026-11-03

接收结论：**B接口及全量原始规则核验通过；仅接受接通，正式科学验收、冻结和发布仍待完成。** 本轮没有训练模型或生成临床效果指标。

生产者A，接收核验B；协议v1。源为[a/resource-researching-and-pre-processing](https://github.com/MarcoJIANG5203/BDDM-10/tree/a/resource-researching-and-pre-processing)，固定提交`ec8fd750cc17038bb0a73c37e1537a1e7a4d780e`，包目录`T1_A_Day1_2026-11-03_v1_Rebuilt_Full/`，数据版本`a-clinical-protocol-v1-20261103-full-r1`。只读取该包当前根目录；`history/previous_candidate_v2/`不能作为v1输入。

## 接收证据

[只读核验脚本](verify_a_received.py)不调用A的提取/核验函数，使用B当前src/data.py，并从原始小时文件独立计算规则。[聚合报告](A_received_2026-11-03.json)记录源提交、哈希、人数、划分及审核状态，没有患者明细。

- 原包125项SHA256清单、audit中31份当前数据/split文件、两原始ZIP与40,336份原始患者文件SHA256均通过；原始文件字节数/MD5也一致。规范快照5份与B Git blob逐字节一致。
- B当前load_cohort五种子×CSV/Parquet共10次通过，两格式内容一致；五角色互斥完备、站点及两类检查通过，没有重划分。
- 从全部原始小时重新核对连续ICULOS、标签单调、完整1—24小时、首次阳性/提前6小时恢复、(12,24]结局，以及<=12小时最后观测的36输入；24,095名纳入患者的标签及特征逐项相等，含NaN。
- 纳入24,095、排除16,241；顺序排除初始小时缺失8,793、随访不足7,448，其余顺序原因0。原始人群另有283例可观察早发起病、426例首次记录阳性，已在更早纳排步骤排除；不能把后续顺序原因0解释为原始人群没有这些情况。
- 当前B全套`python -m pytest -q`：**32 passed in 31.83s**。在独立缓存包目录执行A提供的`python -m pytest -q tests/test_a_cohort_v1.py`：**15 passed in 0.09s**。测试结果分开记录，不冒称原仓库全套47项已运行。

| 人群 / 主种子角色 | 人数 | 阳性 |
|---|---:|---:|
| 医院A | 10,174 | 57 |
| 医院B | 13,921 | 38 |
| A train | 6,104 | 34 |
| A selection | 1,018 | 6 |
| A calibration | 1,527 | 9 |
| A test | 1,525 | 8 |

五种子的角色人数/阳性数一致，具体患者不同。两院200阳性、内部测试50阳性的精度门槛均未达到；事件数很少，接口可用不能证明统计精度足够。规则选择集的6阳性也不能代替对B5/B6实际错误样本数门槛的检查。

## 复核固定提交

以下在B分支仓库根目录运行，临床表保留在忽略缓存。先读取A包代码与说明再运行其测试。不要覆盖data/processed或已冻结run。

```powershell
git fetch origin a/resource-researching-and-pre-processing
New-Item -ItemType Directory -Force .artifact-cache/a-receipt/ec8fd750cc17038bb0a73c37e1537a1e7a4d780e
git archive --format=tar --output=.artifact-cache/a-receipt/ec8fd750cc17038bb0a73c37e1537a1e7a4d780e/source.tar ec8fd750cc17038bb0a73c37e1537a1e7a4d780e T1_A_Day1_2026-11-03_v1_Rebuilt_Full
tar -xf .artifact-cache/a-receipt/ec8fd750cc17038bb0a73c37e1537a1e7a4d780e/source.tar -C .artifact-cache/a-receipt/ec8fd750cc17038bb0a73c37e1537a1e7a4d780e
python reviews/verify_a_received.py --package .artifact-cache/a-receipt/ec8fd750cc17038bb0a73c37e1537a1e7a4d780e/T1_A_Day1_2026-11-03_v1_Rebuilt_Full --output .artifact-cache/a-receipt/recheck.json
```

此方法用于核验已提交候选，不是正式大数据同步方案。Windows本地部分规范文本有CRLF，脚本先要求A快照和B Git blob的原SHA精确相等，再核本地文本只存在换行差别，并另存其真实工作字节SHA。所有源包、数据、split和原始文件仍逐字节校验；不修改原manifest来通过校验。

## 未完成的接收条件

- A负责人确认；C独立检查10阳性/10阴性与边界并自行签收；B的全量自动核对不替代这些记录。
- E与A/B/C讨论精度不足并形成冻结决定；时间窗/纳排如需变更，必须新版本重建重核，不能根据模型结果改标签或选择划分。
- A当前把临床表/原始ZIP直接提交至Git，尚无data Release/registry条目。B未合并该数据树，也未代A重写历史。审核后A/E按DATA_SYNC发布可校验的不可变版本。
- 冻结及正式交付完成后，B先运行2026/S0，再运行协议矩阵；本轮仅接收核验，不产生正式主表。C、D的任务状态保持待本人交付/验收。

后续记录：用户在本接收核验后另行授权跑真实候选，已完成2026/S0/S4；详见[候选试跑结果](../reports/candidate-trials/20261103T122334_93a9a266/SUMMARY.md)。本接收JSON保留当时未运行模型的历史状态，不覆盖为后续结果。
