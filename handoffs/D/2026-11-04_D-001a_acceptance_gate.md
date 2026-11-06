# 2026-11-04 · D · D-001a

| 字段 | 本次记录 |
|---|---|
| 生产者 / 接收人 | D / 全组；C 核对数字与引用，E 检查全文一致性 |
| 状态 | 已提交待验收 |
| 协议 / 数据 / commit | 协议 v1；正式数据未交付；不改数据/标签/split/模型；分支 `d/figure-and-paper`，commit 见 PR #2 |
| 文件 / bundle / run | `scripts/make_figures.py`；`tests/test_make_figures.py`；`paper/acceptance_record_template.json`；`paper/d002_readiness.md`；`paper/README.md`、`paper/figure_list.md`、`paper/source_index.md`；`paper/validation/20261102T063118_fa76f8a8/`；`collaboration/STATUS.md`、`collaboration/CHANGELOG.md` |
| 完成范围 | D-001a：临床 run 必须通过 C/E 签认门槛；D-002 就绪清单与 A/B/C/E 待办；模板与文档同步；合成验证重新生成 |
| 未完成 / 阻塞 | D-002 真实结果图、英文全文、提交版 PDF：等待 A-001 签认/PR、C-001/C-002、E 冻结决定、B-002 正式 run。当前 B 的 `20261104T002604_e3a5a42b` 是候选预冻结，脚本会拒绝其生成论文图 |
| 验证证据 | 见下节 |
| 接收人检查点 | 1) 未签认的临床 run 必须被拒绝；2) 签认记录必须匹配 manifest SHA/run_id/协议/数据版本，并有 C/E 完整签认；3) 合成 run 仍只能走 `--validation-only`；4) `d002_readiness.md` 的 A/B/C 待办与实际分支状态一致；5) 没有真实/候选数字进入论文 |
| 接收人结论 | 由 C/E 填，附日期 |
| 下一步 / 时间 | A 完成本人签认并开 PR；C 完成 20 例人工复核与边界/指标审计；E 组织 v1/v2/暂停选择；之后 B 在正式 data Release 上跑 B-002，D 才能生成论文图 |

## 1. 为什么加这个门槛

B 的 PR #1 已产生真实候选矩阵 `20261104T002604_e3a5a42b`（`synthetic=false`），但它仍是预冻结候选：A 本人未签认、C 未完成逐患者/边界审计、E 已记录暂缓正式冻结。原脚本只拦截 synthetic run，真实但未验收的 run 仍可能被误用于生成无标记的论文图。D-001a 把“C/E 签认”变成硬门槛。

## 2. 实现

`scripts/make_figures.py` 新增 `load_acceptance()`：

- 临床 run 默认读取 `reviews/acceptance/<run_id>.json`，也可用 `--acceptance-file` 指定；
- 必须是 JSON 对象，`schema_version=1`、`synthetic=false`、`status` 为 `accepted` / `accepted_with_limits`；
- `run_id`、`manifest_sha256`、`protocol_version`、`data_version` 必须与 run 的 `manifest.json`/`config.yaml` 一致；
- `scope`、`accepted_at` 非空；
- `signoffs.C` 与 `signoffs.E` 均需 `name`、`date`、`decision`、`evidence`；
- 缺失/不匹配 → `ProvenanceError`，CLI 退出码 2，不读取结果文件、不生成任何图。
- `provenance.json` 新增 `acceptance` 段（记录路径、SHA256、status、scope、accepted_at、C/E 决定与日期）；
- 合成 run 仍走 `--validation-only`，不接受 `--acceptance-file`。

模板：`paper/acceptance_record_template.json`。模板本身 `status=template_not_accepted`，不会被脚本接受。

## 3. 验证

```powershell
python -m pytest tests/test_make_figures.py -q --basetemp <writable-temp>
```

本机（Python 3.14.5；pandas 3.0.3；matplotlib 3.11.2）：

```text
11 passed in 4.10s
```

新增测试覆盖：

- 临床 run 无签认记录 → 拒绝；
- 缺 E 签认 → 拒绝；
- `manifest_sha256` 不匹配 → 拒绝；
- 合法记录 → 返回并通过；
- synthetic run 传 `--acceptance-file` → 拒绝。

CLI 负向验证（伪造的临床 run，无结果文件）：

```text
ERROR: Clinical runs require a C/E-signed acceptance record before figures may be generated.
Expected ...\reviews\acceptance\fake-run.json. A candidate or unaccepted run must not be used
for paper figures; see paper/d002_readiness.md.
exit=2
```

合成 run 重新生成：15 个表/数据 CSV、6 图 × PDF/PNG；`provenance.json` 的 `acceptance` 为 `null`，脚本 SHA256 与当前文件一致。输出仍全部带 “SYNTHETIC SOFTWARE VALIDATION — NOT CLINICAL EVIDENCE” 水印。

## 4. D-002 就绪清单

`paper/d002_readiness.md` 已写明：

- 六个开始门槛：正式 data Release、B-002 正式 run、C/E 签认记录、E 冻结决定、C-002 文献/投稿、来源索引填数；
- A 待办：本人签认、开 PR 到 main、raw ZIP 出普通 Git、展开补件证据、许可澄清、精度门槛书面决定、发布正式 Release；
- B 待办：保持 PR #1 draft、给 C 可复核材料、在正式数据上重跑 B-002、补充实验按优先级、如实记录 0 阳性覆盖/B5-B6 不可用/方向不一致、v2 时重跑；
- C 待办：20 例人工复核签字、边界病例、逐患者指标/区间/稳定性、C-002 原文与投稿要求、给 D 可引用清单、C-003 复核；
- E 待办：组织 v1/v2/暂停选择、维护 STATUS、确认专场通知、最后签 acceptance。

## 5. 未完成 / 阻塞

| 项目 | 阻塞 | 解除条件 |
|---|---|---|
| 真实 Table/Fig | 无已验收临床 run | A 正式 Release + B-002 验收 + C/E 签认 |
| 论文全文/PDF | 无真实结果、C-002 未完成 | 上述 + C-002 引用/规则 + C 数字核对 + E 一致性 |
| 候选 run 图 | 脚本明确拒绝 | 不得绕过；候选 run 只作历史/预冻结证据 |
| A 数据合并 | A 分支无 PR、raw ZIP 在普通 Git | A 开 PR、处理打包、C/E 接受后合并 |

## 6. 接收人检查点（C/E）

1. 运行 `pytest`（11 项）并确认全部通过。
2. 用一个真实但未签认的 run（例如 B 候选 run）运行脚本，确认在读取结果前就因 acceptance 缺失而退出。
3. 检查 `paper/acceptance_record_template.json` 不能被当作签认记录。
4. 检查 `paper/d002_readiness.md` 的 A/B/C 待办是否与实际分支/PR/Release 状态一致。
5. 检查 `paper/validation/.../provenance.json` 的 `acceptance` 为 `null`，且合成数字没有进入 `outline.md`/`source_index.md` 的 `S-xxx`。

## 7. 下一步

1. A 完成本人签认、开 PR、处理 raw ZIP 入库与许可；C 完成 20 例人工复核与边界/指标审计。
2. E 召集 A/B/C/E 书面选择 v1 限定 / v2 重建 / 暂停；记录已查看旧结果。
3. 若保留 v1：A 发布正式 data Release，B 在正式数据上跑 B-002，C 独立复核后在 `reviews/acceptance/<run_id>.json` 与 E 共同签认。
4. D 用 `--acceptance-file` 生成 `paper/runs/<run_id>/`，更新 `source_index.md`，再进入 D-002 写作。
