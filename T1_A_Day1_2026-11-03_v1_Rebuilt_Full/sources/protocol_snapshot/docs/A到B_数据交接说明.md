# A到B的数据交接说明

本说明对应2026-11-02统一实验v1。B不负责重新下载原始数据、构造标签或重划分患者。下列文件由A交付并经C核对，B程序再检查结构和基本一致性。

## 1. 患者表

默认路径为 `data/processed/cohort.parquet`，也接受CSV（CSV中的patient_id必须保留字符串）。每位患者恰好一行。

| 字段 | 要求 |
|---|---|
| patient_id | 全队列唯一字符串，建议带医院前缀，如A_p000001；不得跨医院重名 |
| site | A或B；含义写入审计文件 |
| y_true | 0或1，对应已核对的(12,24]结局 |
| 34项生理化验 | 前12小时最后观测值，未观测保留NaN；不得以未来值补齐 |
| Age | 数值，允许缺失 |
| Gender | 0或1，允许缺失 |

输入顺序固定为：

```text
HR, O2Sat, Temp, SBP, MAP, DBP, Resp, EtCO2,
BaseExcess, HCO3, FiO2, pH, PaCO2, SaO2, AST, BUN,
Alkalinephos, Calcium, Chloride, Creatinine, Bilirubin_direct,
Glucose, Lactate, Magnesium, Phosphate, Potassium,
Bilirubin_total, TroponinI, Hct, Hgb, PTT, WBC, Fibrinogen,
Platelets, Age, Gender
```

patient_id、site和y_true不属于模型输入。B程序自行生成36项缺失指示。列白名单之外的额外字段不会进入预测器；不能因此省略A对时间窗口的核对。

## 2. 固定患者划分

提交 `splits/seed_2026.json`，复核种子2027—2030分别同名。结构如下，示例ID仅说明格式：

```json
{
  "train": ["A_p000001", "A_p000002"],
  "selection": ["A_p000003", "A_p000004"],
  "calibration": ["A_p000005", "A_p000006"],
  "test": ["A_p000007", "A_p000008"],
  "external": ["B_p000001", "B_p000002"]
}
```

真实划分按医院A 60%/10%/15%/15%分层；B全部归external。五个角色必须非空、互斥，覆盖患者表全部ID且没有未知ID。train和selection都需包含两类标签。示例每组两人仅用于说明JSON格式，不是建议样本量。

B不能为了让程序运行而重新划分患者。若A已使用不同字段名，先明确对应关系、转为约定格式，再保留转换记录。

## 3. 审计文件

提交 `data/processed/cohort_audit.json`。以下是字段格式示例，数值由A填写真实统计；禁止直接把示例当成审计结论：

```json
{
  "protocol_version": "v1",
  "data_version": "A负责人确定的数据版本",
  "synthetic": false,
  "feature_window_end": 12,
  "outcome_window": "(12,24]",
  "label_shift_hours": 6,
  "site_meanings": {
    "A": "实际开发医院及原始数据来源",
    "B": "实际外部医院及原始数据来源"
  },
  "exclusion_counts": {
    "input": 0,
    "included": 0,
    "excluded": 0,
    "raw_patients": 0,
    "invalid_hourly_records": 0,
    "insufficient_followup": 0,
    "onset_at_or_before_12": 0
  }
}
```

示例的零是格式占位，正式交付必须替换为实际人数。程序要求input、included、excluded三个计数为非负整数，included等于患者表行数，input等于included+excluded。各排除原因可作为附加字段，需解释先后顺序，不能对重叠原因重复计数后强行相加。建议同时保存各医院阳性数、每列缺失率、数据文件哈希、异常患者清单、A/C人工核对记录和生成队列的代码版本。

若项目配置使用的protocol_version不是v1，审计必须与该配置逐字一致；不得仅改版本字符串掩盖算法或标签变更。

## 4. A/C仍需完成的实质核验

- 每位患者第1—24小时记录的完整性、起始时刻、重复小时和异常标签；按协议处理异常病例。
- 对观察到的0到1转换恢复起病时刻t_first+6，排除第12小时及以前已起病者；首次记录即为1者不能编造精确起始。
- 输入只来自ICULOS<=12，结局区间为12<t_onset<=24；不得把官方提前6小时标签直接当作起病时刻。
- 核查10例阳性、10例阴性和时间边界合成案例。
- 保存各院及内部测试阳性数量，确认预定精度门槛与队列选择限制。

B程序的通过信息只表示数据接口可用，不能替代上述核查。
