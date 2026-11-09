# 2026-11-04 · D · D-002_cohort_tables

| 字段 | 本次记录 |
|---|---|
| 生产者 / 接收人 | D / A、C、E；A 核对数据版本，C 核对数字/边界，D 负责图表 |
| 状态 | 已提交待验收（DRAFT_PENDING_ACCEPTANCE，不是最终论文表） |
| 协议 / 数据 / commit | 协议 v1；A data Release `a-data-v1-20261104-r1`（4,666,169 B，SHA256 `feb69777e7c03c51d580808182a4702a2b3991a0edd552ec4d0dcbf7b1a7129c`）；分支 `d/figure-and-paper`，commit 见 PR #2 |
| 文件 / bundle / run | `scripts/make_cohort_tables.py`；`tests/test_cohort_tables.py`；`paper/inputs/a-data-v1-20261104-r1/`（Table 1a/1b、Fig 1、split_counts、provenance、README） |
| 完成范围 | 从 A 正式 data Release 生成 Table 1 / Fig 1 DRAFT；校验 release SHA256、audit、cohort、5 份 splits、site/阳性数、role 互斥完备、外部医院=B；不读取任何模型结果 |
| 未完成 / 阻塞 | 最终论文 Table 1/Fig 1 需 A PR #3 合并、C-005 完整接收/C/E 签认；B-002 正式 run 仍缺失，因此 D-002 模型图表/全文/PDF 未开始 |
| 验证证据 | release SHA256 与 A 声明一致；cohort 24,095 行、patient_id 唯一、95 阳性、36 特征；5 seeds × 5 roles 与 audit `split_counts` 完全一致；外部角色=医院 B；audit `file_sha256` 全部匹配；`pytest tests/test_cohort_tables.py` 2 passed；输出 `provenance.json` 标记 `DRAFT_PENDING_ACCEPTANCE` |
| 接收人检查点 | A 确认 release ZIP/数据版本；C 核对 Table 1 的 n/阳性/纳排与 Table 1b 缺失率；E/接收人确认后 D 才去掉 DRAFT 标记 |
| 接收人结论 | 由 A/C/E 填，附日期 |
| 下一步 / 时间 | 合并 A PR #3；B 用同一 Release 跑正式 B-002；C/E 签 acceptance；D 再生成模型图表并出全文 |

## 1. 数据与校验

| 项 | 值 |
|---|---|
| Release | `a-data-v1-20261104-r1` |
| ZIP SHA256 | `feb69777e7c03c51d580808182a4702a2b3991a0edd552ec4d0dcbf7b1a7129c` |
| Data version | `a-data-v1-20261104-r1` |
| 总行数 | 24,095 |
| A / B | 10,174 / 13,921 |
| 阳性 | 95（A 57 / B 38） |
| 特征 | 36（audit `feature_order`） |
| 排除 | 16,241（missing_initial 8,793 + insufficient_followup 7,448） |
| Splits | seed 2026–2030，train/selection/calibration/test/external；互斥完备；external=B |
| License | `UNRESOLVED_OFFICIAL_METADATA_CONFLICT`（未解决，不在本表处理） |
| 状态 | `DRAFT_PENDING_ACCEPTANCE` |

## 2. 输出

`paper/inputs/a-data-v1-20261104-r1/`：

- `tables/table1_cohort_summary.csv`：Overall/A/B 的 n、阳性、阳性率、raw/included/excluded、缺失初始小时/随访不足、数据版本、release/license 状态。
- `tables/table1_feature_missingness.csv`：36 项总体/分院缺失率。
- `tables/split_counts.csv`：5 seeds × 5 roles 的 n/positive/negative/sites。
- `tables/fig1_missingness_data.csv`：Fig 1 的数据。
- `figures/fig1_missingness.{pdf,png}`：带 `DRAFT — formal A data release; pending PR merge and C/E acceptance; not for submission` 水印。
- `provenance.json`：release ZIP SHA256、audit/cohort/splits 哈希、脚本 SHA256、validation、outputs SHA256。
- `README.txt`：DRAFT 范围与 license 状态。

## 3. 重新生成

```powershell
python scripts/make_cohort_tables.py `
  --release-zip dist/artifacts/a-data-v1-20261104-r1.zip `
  --expected-sha256 feb69777e7c03c51d580808182a4702a2b3991a0edd552ec4d0dcbf7b1a7129c `
  --overwrite
```

## 4. 没有做什么

- 没有用 B 的候选 run、没有生成任何模型结果图、没有写临床效果或安全结论。
- 没有把 Table 1/Fig 1 当作最终论文表；输出全部标 DRAFT。
- 没有解决 PhysioNet 许可冲突；`license_status` 原样记录。
- 没有替 A/C/E 签收。

## 5. 下一步

1. A 合并 PR #3；C 完成 C-005 接收/C/E 签认。
2. B 用同一 A Release 跑正式 B-002，上传完整 bundle。
3. C/E 签 `reviews/acceptance/<run_id>.json`。
4. D 去掉 Table 1/Fig 1 的 DRAFT 标记，生成模型图表，填 `[RESULT:S-xxx]`，出全文与 PDF。
