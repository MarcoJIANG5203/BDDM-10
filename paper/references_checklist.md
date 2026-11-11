# 引用核实清单（C-002 → D-002）

## 2026-11-10 改稿 E-1 新增 R9–R21（已由 C 2026-11-11 逐条核实）

按 [E 审阅清单](../handoffs/E/2026-11-10_manuscript_consistency_and_submission_verdict.md)第 4 项补充，由本聊天（Claude）加入，均为领域经典文献，只用于背景和方法定位，不支持本文任何结果主张。引用库现为 21 条，稿内 `\cite` 键与 `references.bib` 一一对应（无多无少）。C 本人 2026-11-11 已逐条经 Crossref / arXiv 核对 DOI、卷期页与标题，全部属实，签认见 [C 本人签认](../handoffs/C/2026-11-11_本人签认_内容审阅包与引用核验.md)。

| 编号 / key | 文献 | 核实状态 | 稿中用途 |
|---|---|---|---|
| R9 `rubin1987multiple` | Rubin 1987，Wiley | ✅ 已核（C 11-11）DOI 10.1002/9780470316696 | 多重插补背景 |
| R10 `vanbuuren2011mice` | van Buuren & Groothuis-Oudshoorn 2011，JSS 45(3) | ✅ 已核（C 11-11）DOI 10.18637/jss.v045.i03 | 链式方程插补 |
| R11 `little2019statistical` | Little & Rubin 第 3 版，Wiley 2019 | ✅ 已核（C 11-11）DOI 10.1002/9781119482260（已补入 bib） | 缺失数据背景 |
| R12 `chow1970optimum` | Chow 1970，IEEE TIT 16(1):41–46 | ✅ 已核（C 11-11）DOI 10.1109/TIT.1970.1054406 | 拒识权衡起源 |
| R13 `geifman2017selective` | Geifman & El-Yaniv，NeurIPS 2017 | ✅ 已核（C 11-11）arXiv:1705.08500 | 选择性分类 |
| R14 `mozannar2020consistent` | Mozannar & Sontag，ICML 2020（PMLR 119） | ✅ 已核（C 11-11）arXiv:2006.01862 | 学习延迟 |
| R15 `vovk2005algorithmic` | Vovk、Gammerman、Shafer 2005，Springer | ✅ 已核（C 11-11）DOI 10.1007/b106715 | 共形预测、Mondrian |
| R16 `sadinle2019least` | Sadinle、Lei、Wasserman，JASA 114(525):223–234 | ✅ 已核（C 11-11）DOI 10.1080/01621459.2017.1395341（在线首发 2018，卷期 2019） | 类条件覆盖 |
| R17 `romano2020classification` | Romano、Sesia、Candès，NeurIPS 2020 | ✅ 已核（C 11-11）arXiv:2006.02544 | 自适应集合 |
| R18 `tibshirani2019covariate` | Tibshirani、Barber、Candès、Ramdas，NeurIPS 2019 | ✅ 已核（C 11-11）arXiv:1904.06019 | 协变量偏移 |
| R19 `barber2023beyond` | Barber 等，Ann. Stat. 51(2):816–845 | ✅ 已核（C 11-11）DOI 10.1214/23-AOS2276 | 非可交换 |
| R20 `goldberger2000physiobank` | Goldberger 等，Circulation 101(23):e215–e220 | ✅ 已核（C 11-11）DOI 10.1161/01.CIR.101.23.e215 | PhysioNet 平台署名（许可要求） |
| R21 `singer2016sepsis3` | Singer 等，JAMA 315(8):801–810 | ✅ 已核（C 11-11）DOI 10.1001/jama.2016.0287 | Sepsis-3 定义 |

C 已 2026-11-11 逐条核对 DOI/卷期页并签认；无条目被删除，无 `\cite` 需要撤回。

## 2026-11-10 写作前补齐

当前引用库共 8 条。新增 R8 使用 arXiv v2；元数据和 §§3.1–3.3 的固定模型、目标标签角色与动作定义本轮重新核对，5.1 的配对评价范围沿用[C 岗原文核引](../handoffs/C/2026-11-10_content_review_recheck.md)。未据预印本模板页眉推断正式出版状态。

| 编号 / BibTeX key | 条目与来源 | 可引用范围 |
|---|---|---|
| R8 / `li2026deployment` | Li 等，*A Deployment Audit of Release-Side Risk in Conformal Triage under Prevalence Shift*，arXiv:2605.20956v2，2026-08-04；[元数据](https://arxiv.org/abs/2605.20956v2) · [方法](https://arxiv.org/html/2605.20956v2#S3) | 源模型冻结，目标队列分为事件率校正、共形校准和评价；已有同患者漏放/覆盖/复核比较；阳性警报也计入人工复核。当前稿应具体比较共同单元素池中同容量的置信度/插补分歧排序及源院阈值外院表现。 |

R1/R2/R3 的方法级表述采用上述 C 岗交接的边界：R1 已有固定接受率比较；R2 以回归为主但附录含分类，不能写成只研究回归；R3 已用图扰动离散度评分，不能声称首次将插补不确定性用于筛选。当前研究的分歧定义为同一患者风险预测在多次插补之间的标准差。此更新取代下文“只有 7 条”和相关尚未核原文的旧状态；未覆盖的旧限制继续有效。

## 既有清单 · 2026-11-04

更新：2026-11-04。维护：D。输入：C 的[文献与投稿要求](https://github.com/MarcoJIANG5203/BDDM-10/blob/c/Literature-Review-and-Independent-Test/handoffs/C/2026-11-03_文献与投稿要求.md)与 [C-004 引用核验](https://github.com/MarcoJIANG5203/BDDM-10/blob/c/Literature-Review-and-Independent-Test/handoffs/C/2026-11-04_引用核验_D002.md)（C 分支，未合并到 main）。D 只把**已核实元数据**的条目写入 `paper/references.bib`。

**重要：** C 的对照表自己注明“未逐条读原文”。D 本轮核对了 DOI/出版社页面/摘要等**元数据**；C-004 补了 R5 出处并确认 R3 的 FDR。引用时仍只写能被标题/摘要/已核实原文支持的内容；R1 的“LOCF”仍未证实，不能写。

## 核实结果

| C 编号 | 候选文献 | 核实状态 | DOI / 稳定链接 | 已核实范围 | 仍待确认 / 处理 |
|---|---|---|---|---|---|
| R1 | Kwon & Kim 2026, *Conformal selective prediction with cost aware deferral for safe clinical triage under distribution shift*, Scientific Reports | ✅ 元数据 + 摘要已核实 | [10.1038/s41598-026-40637-w](https://doi.org/10.1038/s41598-026-40637-w) | 标题、作者、期刊、2026；摘要确认：split conformal、Mondrian 分组覆盖、importance-weighted 变体、成本感知 deferral、早期脓毒症分诊、80% coverage 结果 | C 表中“LOCF”未在摘要出现，**不要写 LOCF**，除非读到全文；只写“cost-aware deferral + conformal sets under distribution shift” |
| R2 | Zaffran, Dieuleveut, Josse & Romano 2023, *Conformal Prediction with Missing Values*, ICML (PMLR 202) | ✅ 元数据已核实 | [PMLR v202/zaffran23a](https://proceedings.mlr.press/v202/zaffran23a.html) | 标题、四位作者、ICML、PMLR 202 | 全文级“掩码条件有效性”表述需读原文；D 只写“conformal prediction with missing values” |
| R3 | He, Ai, Wang, Cook & He 2026, *SafeImpute: Reliable Clinical Data Imputation via Conformal Selection*, KDD 2026 | ✅ 元数据 + C-004 全文核验 | [10.1145/3770855.3817967](https://doi.org/10.1145/3770855.3817967)；[arXiv:2607.05613](https://arxiv.org/abs/2607.05613) | 标题、五位作者、KDD 2026；C-004 确认全文用 conformal p-value + Benjamini–Hochberg 控制 FDR | 可写“conformal selection + FDR control”，不扩展为“优于”结论 |
| R4 | Vavaroutas, Dang, Rocheteau & Mascolo 2025, *SQUIREDL: Sparse Sequence-to-Sequence Uncertainty Estimation in Evidential Deep Learning*, ACM Transactions on Computing for Healthcare | ✅ 元数据 + 摘要已核实 | [10.1145/3723049](https://doi.org/10.1145/3723049) | 标题、四位作者、期刊、2025；摘要确认：evidential regression、Akima spline imputation、对插补点/观测点加权、稀疏医疗时序 | 可引用；不要扩展为“优于所有时序模型” |
| R5 | Wong & Ajit 2026, *Guarantees That Survive a Missing Scan: Modality-Conditional Conformal Prediction for Multimodal Medical Diagnosis*, MICCAI 2026 Satellite Events (MLMI), LNCS 17272 | ✅ C-004 补出处；预印 DOI 可核 | [官方页](https://papers.miccai.org/miccai-2026-sat/MLMI_024.html)；[OpenReview](https://openreview.net/forum?id=asy0zD9Urd)；[10.21203/rs.3.rs-10336064/v1](https://doi.org/10.21203/rs.3.rs-10336064/v1) | 标题、作者、会议/workshop、卷号；C-004 确认方法名 MC² = Modality-Conditional Conformal，按模态可用性分层校准 | 可引用；只写“modality-level missingness + Mondrian calibration”，与本研究的 variable-level missingness/MI disagreement 区分，不写成同一层级 |
| R6 | Reyna et al. 2020, *Early Prediction of Sepsis From Clinical Data: The PhysioNet/Computing in Cardiology Challenge 2019*, Critical Care Medicine 48(2):210–217 | ✅ 元数据 + 摘要已核实 | [10.1097/CCM.0000000000004145](https://doi.org/10.1097/CCM.0000000000004145) | 标题、八位作者、卷期页、2020；摘要确认 PhysioNet/CinC 2019 挑战与早期脓毒症预测 | 数据来源引用；不把挑战论文当成本研究临床结论 |
| R7 | Angelopoulos & Bates 2023, *Conformal Prediction: A Gentle Introduction*, Foundations and Trends in Machine Learning | ✅ 元数据 + arXiv 标题已核实 | [10.1561/2200000101](https://doi.org/10.1561/2200000101)；[arXiv:2107.07511](https://arxiv.org/abs/2107.07511) | 标题、作者、期刊/年份；arXiv 标题确认 | 方法背景引用；不要写成“我们的新保证” |

## 处理规则

1. **只有** `paper/references.bib` 里的 7 条可进入论文；R5 已由 C-004 补出，写入 bib。
2. R1 的“LOCF”仍未证实，不能写；R3 的“FDR”已由 C-004 证实，可以写；R5 只写 modality-level missingness + Mondrian calibration，不能与 variable-level MI disagreement 混为一谈。
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
| R5 | `wong2026mc2` | `paper/references.bib` |
| R6 | `reyna2020early` | `paper/references.bib` |
| R7 | `angelopoulos2023conformal` | `paper/references.bib` |

## C-004 后的状态

- R5 已由 C-004 补出，写入 bib；不再需要 C 补。
- R3 的 FDR 已由 C-004 用全文确认，D 可以写。
- R1 的“LOCF”仍未证实；除非 C/D 逐字读全文并给页码，否则不写。
- C-002 的“11-20 前可投稿”通知证据仍由组内留存；D 不据此写论文。
- C-004 本身状态为“已提交待验收”；D 在本清单中记录为“已采用”，接收结论由 C/D 在 PR 评审中确认。
