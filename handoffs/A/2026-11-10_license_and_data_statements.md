# 2026-11-10 · A · 许可冲突处置与论文数据声明

| 字段 | 记录 |
|---|---|
| 执行 / 授权 | 用户要求"完成 A 的内容"，由本聊天（Claude）在本地起草；A 本人确认待记录 |
| 状态 | 处置方案与声明草稿已交付，供作者组采纳 |
| 依据 | [11 月 5 日官方复核](../../reviews/license/2026-11-05/README.md)：PhysioNet 版本页显示 CC BY 4.0，下载的 `LICENSE.txt` 为 ODbL；冲突仍未解决，澄清邮件按用户指示未发送 |

## 处置决定（建议）

投稿**不依赖**许可冲突的解决。理由是两种许可都允许二次分析和发表结果，冲突只影响"是否可以重新分发原始数据或其派生数据库"。因此：

1. 论文、补充材料和对外代码包**不重新分发任何患者级记录**，包括原始 PSV、A 队列表、split 患者清单、逐患者预测表。
2. 对外只提供聚合表（Table 1–2、S1–S3、图源数据）和代码，读者从 PhysioNet 自行下载原始数据后复现。
3. 原始数据按两种许可中更严格的一方（ODbL 署名 + 相同方式共享）的要求处理：注明出处、不附加额外限制、不分发派生数据库。
4. 引用 Reyna 等 2020（R6）及 PhysioNet 平台标准引用（Goldberger 等 2000），这同时满足 CC BY 4.0 和 ODbL 的署名要求。

如果之后决定公开患者级派生文件，必须先发出[已备好的澄清请求](../../reviews/license/2026-11-05/clarification_request_EN.md)并保存官方回复。

## 论文可直接使用的声明草稿

**Data availability.** The PhysioNet/Computing in Cardiology Challenge 2019 data are publicly available from PhysioNet (https://physionet.org/content/challenge-2019/1.0.0/). We do not redistribute patient-level records or derived patient-level files. Aggregate result tables, figure source data and the analysis code needed to reproduce the cohort, partitions and results from the public source are available from the authors [or: in the supplementary material].

**Ethics.** This study is a retrospective secondary analysis of a publicly available, de-identified dataset released for research use. No patients were contacted and no new data were collected; therefore, additional ethical approval was not required. [Authors to confirm against their institution's policy.]

**Acknowledgment / citation to add.** Goldberger AL, et al. PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals. Circulation. 2000;101(23):e215–e220. — 加入前由 C/D 按 `references_checklist.md` 规则核对元数据。

## 未完成

- A 本人确认上述处置；作者组确认伦理措辞是否符合各自单位要求。
- 官方许可冲突本身仍未解决，本记录不声称已解决。
