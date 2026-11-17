# 2026-11-16 · Workshop3 新版稿：LaTeX 源重建与投稿前修改（r1）

| 项目 | 记录 |
|---|---|
| 执行 / 授权 | 用户审阅两版稿件后选定「Workshop3 新版」（`BDDM2026_Workshop3_Pipeline_English_Manuscript.pdf`，tectonic 编译）为投稿底稿并要求修改；由本聊天（Claude）在本地完成。D/C/E 本人复核待记录 |
| 状态 | **已提交待复核**，不是验收，也没有投稿 |
| 源文件来历 | 新版 PDF 的 LaTeX 源不在本机、共享目录或 `origin` 任何分支上，因此 **`paper/latex-workshop3/main.tex` 是按该 PDF 重建的**，不是原作者的源文件。若原始源之后找到，按下文「改动清单」移植即可 |
| 结果数字 | 没有重跑任何实验。新写入正文的数字全部取自已接受的正式主运行 `20261105T055420_02d05b15` 和 C 已核的 `base_model_context.csv`，见「新写入的数字」 |
| 未改动 | `paper/latex/`（11-15 旧版）、`paper/references.bib`、`paper/manuscript_draft.md`、签认包 |

## 产物

- `paper/latex-workshop3/main.tex`：单文件、自包含。四张图用 TikZ/pgfplots 直接画，参考文献为手写 `thebibliography`，不需要 BibTeX 和外部图片，可直接放 Overleaf/MiKTeX。
- `paper/latex-workshop3/build.sh`：`sh paper/latex-workshop3/build.sh`，在临时目录编译，不留 aux 文件。
- `paper/camera-ready/BDDM2026_Workshop3_manuscript_r1.pdf`：**5 页**，Letter，无 Type 3 字体，0 个未定义引用，0 个 Overfull。

## 与原 PDF 的一致性核对

对两份 PDF 的 `pdftotext` 输出做 5 词滑窗比对（忽略版面顺序）。正文里不一致的片段只有下表列出的有意改动，以及图表重画、小节标题大小写、DOI 断行这三类排版差异。

## 改动清单

| # | 位置 | 原稿 | r1 |
|---|---|---|---|
| 1 | 引言末段 | 无贡献说明 | 新增一段：点明可靠性评估定位，列三条贡献，并说明主结论为阴性 |
| 2 | 方法 D | AUROC/AP 无区间说明 | 补一句：AUROC 给 1,000 次 bootstrap 的 95% 区间 |
| 3 | 结果 B | AUROC 0.793 / 0.502 无区间 | 补 [0.579, 0.947] 与 [0.407, 0.596] |
| 4 | 结果 B | B0 在方法中定义、结果中未报告 | 补一句 B0 的单例池规模与阳性去向 |
| 5 | 结果 C | 引用 “Supplementary Fig. S1” | 删除引用，改为正文给出 40%/80% 目标下的漏诊人数 |
| 6 | 结果 D | 引用 “Supplementary Tables S1–S3” | 删除括号引用，句子保留 |
| 7 | 讨论首段 | 未解释外院 AUROC≈0.5 的含义 | 补一句（取自 11-15 旧版的表述） |
| 8 | 数据与代码声明 | “The manuscript package identifies…” | 改为不重新分发患者级数据、材料可向通讯作者索取；仓库地址留红色待确认 |
| 9 | 致谢（AI 披露） | 仅 OpenAI Codex | 改为 OpenAI Codex 与 Anthropic Claude，范围留红色待作者确认 |
| 10 | 文献 [8][9] | “Candés” | “Candès” |
| 11 | 文献 [10][13] | 带 “[Online]. Available” 链接 | 已有卷号页码，删链接以省版面 |
| 12 | Fig. 2 | 图例 “Site A / Site B” | “Hospital A / Hospital B”，与正文一致 |
| 13 | Fig. 3B | “1/278” 标签压在 y 轴刻度上 | 重画后不再重叠；Wilson 区间重新计算，与原图一致 |
| 14 | 小节标题 | 句首大写 | IEEE 惯用的首字母大写 |
| 15 | 作者栏 | 黑色占位符 | 红色占位符，避免漏填 |

## 新写入的数字（请 C 复核）

| 句子 | 数字 | 来源 |
|---|---|---|
| AUROC 区间 | 0.793 [0.579, 0.947]；0.502 [0.407, 0.596] | `paper/content-review/20261110-r1/base_model_context.csv`（C-010 已复算点估计，区间为 B 诊断输出） |
| B0 单例池 | 内院 1,380（90.49%），含 4/8 阳性；外院 13,143（94.41%），含 37/38 阳性；全部为阴性预测 | `reports/clinical-v1/20261105T055420_02d05b15/metrics.csv`，seed 2026、LR、B0、S0/S4 |
| 40%/80% 目标 | B4 对 B2 的漏诊人数：内院 1 对 1、2 对 3；外院 18 对 15、30 对 29 | 同上，B2/B4、batch、target 0.4/0.8 |
| Fig. 4A | 五个种子的 B4−B2 均值与范围 | 同上，逐种子复算后与原图一致 |
| Fig. 3B | 1/278、0/277、2/278 的 Wilson 95% 区间 | 由原图标注的计数直接计算 |

## 同日追加：作者组决定（用户转述）

- 作者四人：Yicheng Jiang\*、Shijie Zhang\*、Sirui Huang、Xufeng Yin；前两位共同一作（脚注），蒋奕程排第一。单位均为北京交通大学。不单列通讯作者，不写邮箱。
- 数据与代码：写公开仓库 `https://github.com/MarcoJIANG5203/BDDM-10`。**该仓库 2026-11-16 未登录访问返回 404（仍为私有），投稿前须公开或换成新建的公开仓库地址。**
- AI 披露：作者确认属实，已去掉红色标记。无基金；不需要额外伦理说明；致谢不写第五位组员。
- 稿面已无红色标记，重新编译仍为 5 页。下列第 1–3 项已由此关闭。

## 仍需作者组处理

1. 填写作者、单位、通讯作者邮箱（填完后重新确认仍为 5 页；第 5 页右栏目前约余 8 行）。
2. 确认数据与代码的提供方式（公开仓库地址，或保留 “on request”）。
3. 确认 AI 披露中的工具与范围属实。
4. 文献 [18]：MICCAI 页面的作者元数据只有 Ajit，而 `paper/references.bib` 写的是 Wong 与 Ajit，请打开论文 PDF 确认。
5. 文献 [12]、[15] 的卷号与页码未能在线核实（[13] 已核实为 PMLR 329:793–812）。
6. C-002 要求引用 chair Lei Zhang 的不完备医疗数据工作，本稿仍未引用。
7. 向会务确认投稿入口、注册截止日和查重要求。
