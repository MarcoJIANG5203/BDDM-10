# v1预冻结补充实验候选摘要

run：`20261104T132609_45c03e76`；原v1数据`a-clinical-protocol-v1-20261103-full-r1`；固定2026 split；配置`configs/a_candidate_v1_supplements_20261104.yaml`。**候选、未冻结、未科学验收。**完整run保留在`results/candidate-clinical/`，本地包在registry登记为`prepared`，未上传。

在主种子内部测试S0/S2运行RF(300树，S0/S2)、LR的M=5/20(S0)和alpha=.05(S0/S2)；同run中LR/M10/alpha=.1为原主矩阵的重合复跑。10轮插补、1000次患者级配对bootstrap、原始标签和split均未改。240指标行、48配对区间、366,000逐患者方法行、208,925插补概率行；B独立复核22产物/13源码/1 split哈希及全部240指标行，48区间独立重算；本地包26文件空目录恢复通过。重合LR/M10/alpha=.1/S0/S2的120指标行与原主矩阵逐项相同。

主种子内部测试每场景均为1,525人、8阳性。下表只列首批、60%批次容量下的接受错误数；B2/B4都接受915人，不能把差异外推为可靠阳性安全结论。

| 模型 / M / alpha | 场景 | B2错误 | B4错误 | B4−B2配对风险差95%区间 |
|---|---:|---:|---:|---:|
| LR / 10 / .1 | S0 | 1 | 2 | [0, .003279] |
| LR / 10 / .1 | S2 | 3 | 3 | [0, 0] |
| RF / 10 / .1 | S0 | 4 | 6 | [-.002186, .006557] |
| RF / 10 / .1 | S2 | 4 | 6 | [0, .005464] |
| LR / 5 / .1 | S0 | 1 | 2 | [0, .003279] |
| LR / 20 / .1 | S0 | 1 | 1 | [0, 0] |
| LR / 10 / .05 | S0 | 1 | 3 | [0, .005464] |
| LR / 10 / .05 | S2 | 3 | 3 | [0, 0] |

B5/B6在所有组合都因规则选择集仅6错误/1,012正确而不可用，不能报告B6−B5增量。全部接受错误在上述首批中均为接受阳性并判阴性；这与零阳性集合覆盖风险同向，不能称为安全。区间`[0,0]`反映该设置下重抽样比较持平，不代表零临床风险。完整分层覆盖、全部容量、冻结阈值和五批稳定性见原CSV；不按有利组合筛选主结论。

验证命令：`python reviews/verify_b_artifacts.py results/candidate-clinical/20261104T132609_45c03e76`；`python reviews/verify_candidate_bootstrap.py results/candidate-clinical/20261104T132609_45c03e76 --output .artifact-cache/b-supplement-bootstrap.json`。候选描述不替代正式data Release、B-002新run、C独立复核和E冻结。
