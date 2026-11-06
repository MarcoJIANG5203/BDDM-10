# 2026-11-04 · B · A-001补件及C-001接收复核

| 字段 | 记录 |
|---|---|
| 生产者 / 接收人 | A、C / B（本记录）；A/C/E各自验收仍由本人记录 |
| 状态 | A技术补件与C标签脚本在下述范围内接收；正式A数据、C完整指标核查和B-002矩阵未验收 |
| 协议 / 数据 / run | v1 / `a-clinical-protocol-v1-20261103-full-r1` / `20261103T122334_93a9a266` |
| 固定提交 | A `845f799`（补件；源数据仍为`ec8fd750`）；C `f15505e`；B复核基线`54f8342` |
| 交付位置 | A分支`artifacts/packages/T1_A_001_Review_2026-11-03.zip`、`reports/A_001_validation_2026-11-03_EN.md`；C分支`reviews/verify_c_labels.py`与`handoffs/C/2026-11-03_标签核验.md` |
| 验证输出 | A补件ZIP 34,626字节、SHA256 `32731ef13079d626a1da6f4451d2510a228c95347f21634ae2260cfb8c8921f7`，ZIP CRC无错、内部17项SHA256全匹配；C脚本按固定A包运行20/20；B候选`verify_b_artifacts.py`独立复算120指标行、18产物/13源码/1划分哈希通过；手算测试2 passed |
| B接收结论 | A补件可作为技术审核证据，C的20例标签一致结论在所查病例范围成立；不把自动核验扩写为临床真值、A本人确认或C完整科学验收 |
| 待补核 | A本人核签及正式data Release/来源许可说明；C独立边界病例、候选run的逐患者集合/漏放/配对区间和五批稳定性；E与A/B/C的精度/冻结决定 |

复跑命令（C脚本从C提交的只读输出流执行，A原字节包在忽略缓存；逐例输出含患者ID，不纳入Git记录）：

```powershell
git show origin/c/Literature-Review-and-Independent-Test:reviews/verify_c_labels.py | python - .artifact-cache/a-receipt/ec8fd750cc17038bb0a73c37e1537a1e7a4d780e/T1_A_Day1_2026-11-03_v1_Rebuilt_Full
python reviews/verify_b_artifacts.py results/candidate-clinical/20261103T122334_93a9a266
python -m pytest -q tests/test_independent_audit.py
```

审核范围：C脚本逐例读取20份原始小时文件并复算标签，检查首小时、连续小时、满24小时与首观测阳性；当前20例均匹配。脚本没有单独执行`onset=12/13/24/25`、首观测即阳性等人工构造边界，也未检查36项输入/时间截断。A补件自己报告六个边界例通过，不能代替C的独立边界结论。C的交接仅按`metrics.csv`/`stability.csv`核对聚合算术，未声明完整逐患者重算与12个配对区间。B本轮独立复核原候选run的120指标行，但不能代替C的接收。

A报告引用的`reviews/A_001_verification_2026-11-03.json`、`scripts/verify_a001_delivery.py`和`docs/A_001_source_provenance_correction_EN.md`位于补件ZIP的`git_overlay/`，尚未在A分支展开为普通文件；后续A交付时应让引用路径可直接读取，并保留原ZIP与数据源字节。A报告明确注明负责人签名仍待本人，正式数据Release未发布。补件为小型审核文件，不是正式数据版本包。

本轮未改标签、划分、阈值、模型、历史manifest或run；B-002正式矩阵等E联合冻结结论和可校验正式data版本。

每日记录：2026-11-04｜B｜核验A补件SHA及C 20例，复核原候选120指标行｜本记录、`845f799`、`f15505e`、候选run｜边界/完整C复核及正式冻结待办｜待A/C/E交齐后执行B-002，预计时间由联合决定确定。
