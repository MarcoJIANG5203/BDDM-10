# 2026-11-13 · 终稿格式硬伤修正与 Fig. 1 重绘

| 项目 | 记录 |
|---|---|
| 执行 / 授权 | 用户对照参会通知审阅《初版.pdf》《论文初稿.pdf》后，要求“先改格式硬伤”并“把图美化到接近顶刊”；由本聊天（Claude）在本地完成。D 本人复核待记录 |
| 结果数字 | **没有新增或改动任何结果**；新增句子只引用 C 已签认的 `random_reference.csv`（S-027）与补充 run `20261105T055445_54dd08de` 的 S1–S3 表（S-010） |
| 不变 | `paper/content-review/20261110-r1/` 签认包及其生成脚本 `scripts/build_content_review.py` 均未改动 |

## Fig. 1 重绘

- 新脚本 `scripts/make_reliability_figure.py`，输出 `paper/camera-ready/fig1_reliability.{pdf,png,svg}` 和 `fig1_reliability.provenance.json`。
- 只读签认包里的 `capacity_coverage_release.csv`、`random_reference.csv`；出图前核对其 SHA-256 与签认包 `provenance.json` 一致，不一致即中止。
- 原图 `fig_reliability.pdf` 内嵌 DejaVuSans **Type 3** 字体，可能过不了 IEEE PDF eXpress。新图用 Liberation Serif（与 Times 等宽，同 IEEE 正文）按 TrueType（Type 42）嵌入，`pdffonts` 中已无 Type 3 字体。
- 风格（用户选定）：SciencePlots `science + ieee + no-latex`，即衬线字体、封闭坐标框、刻度朝内。配色保留 Okabe–Ito 蓝/橙，不用 ieee 默认的纯红/纯蓝。ieee 样式会轮换线型，脚本已把所有线固定为实线。
- 版式：IEEE 通栏 7.16 in × 2.2 in，7 pt；Cleveland 点图；标出名义 90%、目标 60% 两条参考线，阳性覆盖的精确 95% 区间，以及随机排序参照带；去掉 “CONTENT REVIEW” 标记和图内大标题。
- `--theme clean` 仍可输出无衬线备选版（`*_clean.*`），默认是 `ieee`。
- 依赖：`requirements.txt` 新增 `SciencePlots`；不需要安装 LaTeX。`requirements-lock.txt` 未更新，因为本机 Python 3.10 无法复现锁定环境（pandas 3.0.3 需要 Python ≥ 3.11）。
- 生成环境：本机 Python 3.10 的临时 venv（matplotlib 3.10.9、pandas 2.3.3、SciencePlots 2.2.2）。本脚本只读 CSV 出图，结果不受这些版本差异影响。

```bash
python -m scripts.make_reliability_figure --out-dir paper/camera-ready
```

## 正文 `paper/manuscript_draft.md`

| 问题 | 处理 |
|---|---|
| 策略表 B0–B6 无表题、无编号 | 加 **Table 1. Acceptance strategies**；原 Table 1/2 顺延为 Table 2/3，正文引用同步修改 |
| 讨论提到 “random reference”，结果中没有 | §5.3 补一句随机参照（期望 2.64 / 23.38，中央 95% 范围 1–4 / 17–29）；两种排序在两院都落在范围内 |
| 引用 “Supplementary Tables S1–S3”（会议集通常不收补充材料） | 改为正文一句，给出 RF、M、alpha 检查的差值；所有区间都触及 0 |
| “ddof=1” 代码用语 | 改为 “sample standard deviation … (denominator M − 1)” |
| AI 使用声明空白 | 起草一版，标注“作者确认” |
| Fig. 1 图注 | 按新图重写，并把风险差及其区间写进图注 |

## IEEE 模板排版（同日追加）

- 新增 `paper/latex/main.tex`（IEEEtran conference 模板，双栏 Times），内容取自上述 `manuscript_draft.md`。已删除 `[S-0xx]` 标签和 “Review draft” 抬头；摘要按 IEEE 要求合并为一段，正文措辞做了压缩，结果数字未改。
- 编译：`sh paper/latex/build.sh`，生成 `paper/camera-ready/BDDM2026_manuscript.pdf`，编译过程不在仓库里留 aux 文件。需要的 apt 包：`texlive-latex-recommended texlive-latex-extra texlive-publishers texlive-fonts-recommended`。
- 结果：**5 页**（第 5 页只有半栏参考文献），不产生超页费；0 个未定义引用；21 条 `\cite` 与 `references.bib` 一一对应；PDF 中没有 Type 3 字体。
- 数字核对：PDF 第 1–4 页的 110 个数值都能在 `manuscript_draft.md` 中找到；未找到的只有图中坐标刻度（25/40/50/75/80/100）。
- `references.bib` 只给 6 个标题加了花括号来保护大写（SafeImpute、SQUIREDL、PhysioNet/Computing in Cardiology Challenge、R、PhysioBank/PhysioToolkit/PhysioNet、Sepsis-3），书目信息没有改。
- PDF 未收录 Author contributions：IEEE 会议论文不要求这一节，且现稿只有 A–E 代号。AI 使用声明放在 Acknowledgment。

## 方法流程主图（同日追加）

- 新增 `scripts/make_pipeline_figure.py`，输出 `paper/camera-ready/fig_pipeline.{pdf,png,svg}` 和 provenance。图中分五步：队列与特征 → 多重插补与共享 LR（$\bar p_i$、$D_i$）→ 分裂共形集合 → B2/B3/B4 排序、等容量或冻结阈值接受 → 内外院评价。
- 这是示意图，不读结果文件。图中数字（10,174 / 57、13,921 / 38、1,525 / 8、60/10/15/15%、M=10、α=0.10）全部取自 `manuscript_draft.md` 的 Table 2 和 Methods。
- LaTeX 中作为 Fig. 1 放在 Methods 开头，原可靠性图顺延为 Fig. 2（`fig1_reliability.*` 的文件名未改）。重新编译后仍为 **5 页**，没有 Type 3 字体。

## 仍待（不在本次范围）

- PDF 中的红色方括号需作者组填写或删除：作者、单位、Email、代码公开方式、伦理说明是否符合机构政策、AI 声明的范围。
- D 本人复核排版稿；C/E 确认措辞压缩后主张范围不变。
- 会务的页数要求（以往记录为“至少 8 页”，本通知只说第 6 页起收超页费）仍需向会务确认。
