# 引用核实清单（C-002 → D-002）

更新：2026-11-04。维护：D。输入：C 的[文献与投稿要求](https://github.com/MarcoJIANG5203/BDDM-10/blob/c/Literature-Review-and-Independent-Test/handoffs/C/2026-11-03_文献与投稿要求.md)（C 分支，未合并到 main）。D 只把**已核实元数据**的条目写入 `paper/references.bib`；未核实条目不进论文。

**重要：** C 的对照表自己注明“未逐条读原文”。D 本轮核对了 DOI/出版社页面/摘要等**元数据**，不等于已核对全文结论。引用时只写能被标题或摘要支持的内容；全文级 claim 仍需 C 或 D 逐条读原文后确认。

## 核实结果

| C 编号 | 候选文献 | 核实状态 | DOI / 稳定链接 | 已核实范围 | 仍待确认 / 处理 |
|---|---|---|---|---|---|
| R1 | Kwon & Kim 2026, *Conformal selective prediction with cost aware deferral for safe clinical triage under distribution shift*, Scientific Reports | ✅ 元数据 + 摘要已核实 | [10.1038/s41598-026-40637-w](https://doi.org/10.1038/s41598-026-40637-w) | 标题、作者、期刊、2026；摘要确认：split conformal、Mondrian 分组覆盖、importance-weighted 变体、成本感知 deferral、早期脓毒症分诊、80% coverage 结果 | C 表中“LOCF”未在摘要出现，**不要写 LOCF**，除非读到全文；只写“cost-aware deferral + conformal sets under distribution shift” |
| R2 | Zaffran, Dieuleveut, Josse & Romano 2023, *Conformal Prediction with Missing Values*, ICML (PMLR 202) | ✅ 元数据已核实 | [PMLR v202/zaffran23a](https://proceedings.mlr.press/v202/zaffran23a.html) | 标题、四位作者、ICML、PMLR 202 | 全文级“掩码条件有效性”表述需读原文；D 只写“conformal prediction with missing values” |
| R3 | He, Ai, Wang, Cook & He 2026, *SafeImpute: Reliable Clinical Data Imputation via Conformal Selection*, KDD 2026 | ⚠️ 元数据已核实；claim 未核实 | [10.1145/3770855.3817967](https://doi.org/10.1145/3770855.3817967) | 标题、五位作者、KDD 2026 proceedings | C 表“FDR 控制”未从摘要/元数据确认；D 只写“conformal selection for imputation”，不写 FDR，直到读到全文 |
| R4 | Vavaroutas, Dang, Rocheteau & Mascolo 2025, *SQUIREDL: Sparse Sequence-to-Sequence Uncertainty Estimation in Evidential Deep Learning*, ACM Transactions on Computing for Healthcare | ✅ 元数据 + 摘要已核实 | [10.1145/3723049](https://doi.org/10.1145/3723049) | 标题、四位作者、期刊、2025；摘要确认：evidential regression、Akima spline imputation、对插补点/观测点加权、稀疏医疗时序 | 可引用；不要扩展为“优于所有时序模型” |
| R5 | C 表所称 “MC² (MICCAI 2026 workshop), 模态级缺失的 Mondrian CP” | ❌ **未找到出处** | — | Crossref / Semantic Scholar / DOI 检索均未命中；C 未给出 DOI、作者或 URL | **禁止引用**。请 C 提供准确标题、作者、会议/workshop、DOI 或官方页面；在补上前从 Related Work 删除该条 |
| R6 | Reyna et al. 2020, *Early Prediction of Sepsis From Clinical Data: The PhysioNet/Computing in Cardiology Challenge 2019*, Critical Care Medicine 48(2):210–217 | ✅ 元数据 + 摘要已核实 | [10.1097/CCM.0000000000004145](https://doi.org/10.1097/CCM.0000000000004145) | 标题、八位作者、卷期页、2020；摘要确认 PhysioNet/CinC 2019 挑战与早期脓毒症预测 | 数据来源引用；不把挑战论文当成本研究临床结论 |
| R7 | Angelopoulos & Bates 2023, *Conformal Prediction: A Gentle Introduction*, Foundations and Trends in Machine Learning | ✅ 元数据 + arXiv 标题已核实 | [10.1561/2200000101](https://doi.org/10.1561/2200000101)；[arXiv:2107.07511](https://arxiv.org/abs/2107.07511) | 标题、作者、期刊/年份；arXiv 标题确认 | 方法背景引用；不要写成“我们的新保证” |

## 处理规则

1. **只有** `paper/references.bib` 里的 6 条可进入论文；R5 不写入 bib。
2. R1/R3 的 claim 级描述必须保守：只写标题/摘要支持的内容，不写 C 表中的未核实细节（LOCF、FDR）。
3. 引用格式、作者顺序、页码/卷期在投稿前再由 D 按官方模板核对一次；C 负责判断“是否可作为相关工作”。
4. 任何新增引用先在本文件加一行，写 DOI/URL 与核实范围，再进 `references.bib`。
5. 论文中每个 `\cite{...}` 必须能在本清单找到对应行；找不到的引用一律删除。

## BibTeX 键映射

| C 编号 | BibTeX key | 文件 |
|---|---|---|
| R1 | `kwon2026conformal` | `paper/references.bib` |
| R2 | `zaffran2023conformal` | `paper/references.bib` |
| R3 | `he2026safeimpute` | `paper/references.bib` |
| R4 | `vavaroutas2025squiredl` | `paper/references.bib` |
| R5 | —（不引用） | — |
| R6 | `reyna2020early` | `paper/references.bib` |
| R7 | `angelopoulos2023conformal` | `paper/references.bib` |

## 需要 C 补的

- R5 的准确出处（标题/作者/会议/DOI/URL）；补不上就从 Related Work 删除。
- R1 的“LOCF”与 R3 的“FDR”是否真在原文；若在，给页码/章节，D 再写入。
- C-002 的“11-20 前可投稿”通知证据仍由组内留存；D 不据此写论文。
