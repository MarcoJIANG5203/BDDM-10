# 2026-11-03 · B · B-002候选真实数据试跑

| 项目 | 记录 |
|---|---|
| 生产者 / 接收人 | B / C、D、E；A查阅数据适用性问题 |
| 状态 | 试跑及B计算核验完成，已提交待接收人独立审核；不是正式冻结或B-002全矩阵完成 |
| 授权 | 用户在A接口接收后明确要求跑A真实数据；本次使用候选状态执行 |
| 分支 / 协议 | b/core-methods-experiments / v1 |
| A提交 / 数据 | ec8fd750cc17038bb0a73c37e1537a1e7a4d780e / a-clinical-protocol-v1-20261103-full-r1 |
| run | results/candidate-clinical/20261103T122334_93a9a266，completed，351.71s |
| 范围 | 全部固定2026患者；LR/M10/10轮/alpha0.1/1000bootstrap；S0五批、S4一批；无其他场景/种子/敏感性 |
| 结果入口 | reports/candidate-trials/20261103T122334_93a9a266/SUMMARY.md；完整小表同目录 |
| 核验 | 120指标行、12配对区间、所有产物/源码/输入哈希独立通过；本地ZIP及实际远端API下载ZIP均在空目录恢复复核通过；B32测试、A15边界测试分别通过 |
| 包 | b-candidate-natural-20261103-r1已上传pre-release；28文件/21,522,751字节/SHA256 5d5879dd112d329a5b3079dbdc8d5588a7bdf82c4c1e596e4b15b98751fabd33，远端digest一致；科学未验收，网络下载实测另记reviews/A_candidate_download_2026-11-03.json |
| 真实不足 | B5/B6仅6错误不可用；主批次60%容量S0 B4 2错误对B2 1，S4 21对24且差异区间跨0；MI阳性覆盖0/8和0/38；未见稳定优势 |
| 未完成 | A负责人确认、C独立临床/指标审核、E精度/冻结决定、A正式data Release、B正式五种子五场景矩阵 |
| 下一步 | C独立复核并填写自己的结论；E与A/B/C讨论精度和阳性覆盖问题；D可调试图表，但不能把本候选试跑直接称为正式论文结论 |

只新增候选配置和复核工具/汇总，不修改src、规范配置、标签、患者划分或原始输入。原run及manifest保留原字节，完整临床文件仅放版本包。接收时先核registry SHA256并恢复，再执行独立核验；详细命令见collaboration/DATA_SYNC.md。
