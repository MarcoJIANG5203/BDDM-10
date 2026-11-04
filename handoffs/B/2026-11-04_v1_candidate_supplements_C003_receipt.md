# 2026-11-04 · B · C-003接收与v1候选补充实验

| 字段 | 记录 |
|---|---|
| 生产者 / 接收人 | B / C、D、E；C-003由C独立提交，B只填写自身检查结论 |
| 协议 / 输入 | v1、`a-clinical-protocol-v1-20261103-full-r1`原字节、2026固定split；正式数据未发布 |
| run | `results/candidate-clinical/20261104T132609_45c03e76`；`configs/a_candidate_v1_supplements_20261104.yaml` |
| 小型摘要 / 包 | `reports/candidate-trials/20261104T132609_45c03e76/SUMMARY.md`；`b-candidate-v1-supplements-20261104-r1`本地prepared，SHA256 `808537f305e7acb47fa01ce0eb5012d950b1224b92ca9c86ece470a1ee2e5e7f` |
| 完成范围 | RF S0/S2、M5/20 S0、alpha=.05 S0/S2候选补充；不升格正式B-002 |
| B核验 | 完整run `run_status=completed`；独立核对240指标行、22产物/13源码/1split哈希、48配对bootstrap区间；26文件本地包SHA256与空目录恢复通过；LR M10 .1重合120指标行与旧候选矩阵一致；小型复核回执见`reviews/B_candidate_supplements_2026-11-04.json`，仓库32测试通过 |
| 远端状态 | 未上传；A源许可冲突未解决，暂不新增含临床输入/逐患者结果的公开或预发布附件。registry登记prepared，不能fetch或写published |
| 科学限制 | 内部测试仅8阳性；B5/B6选择集6错误未达20例门槛；阳性集合覆盖问题仍在，补充组合未显示稳定分歧优势 |
| 接收人结论 | 由C/E对本新run各自独立复核；B不代签 |

## B对C-003的接收

C分支`f4d9736`的`reviews/verify_c_candidate_metrics.py`不导入B实验模块。B检查其独立实现：患者并列键为`sha256(str(patient_id).encode())`；`np.lexsort((copy_key,tie_key,score))`将score设为主排序键，与B的`(score,tie_key,copy_key)`等价；frozen规则为在单元素池内`score<threshold`，或等于阈值且`tie_key<=tie_hash`，与B一致。B直接从C分支读取原脚本，对旧主矩阵重放：2,612,100逐患者方法行的标签和接受决策均0不一致、900指标行及30区间通过、1,436,655行p_m重算通过，0检查失败；小型回执见`reviews/B_candidate_supplements_2026-11-04.json`。**B接收C-003的候选指标及边界脚本核验范围；不把C-005写成C本人已从原始PSV逐份重跑，也不签正式run。**

后续：A完成许可澄清与正式data Release、E作正式冻结决定后，B从正式bundle字节启动新的不可变B-002主run，先2026/S0再完整主矩阵，并在主run验收后重新执行上述补充项目。旧候选run/manifest不重写。

2026-11-04｜B｜完成候选补充与C-003排序/阈值语义接收｜本记录、run、摘要、prepared bundle｜正式data/冻结/C新run复核待办｜条件满足后正式重跑，时间取决于上游交付。
