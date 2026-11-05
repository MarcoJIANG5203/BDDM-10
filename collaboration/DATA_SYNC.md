# 数据和完整产物同步

Git维护代码、协议、状态、小样本和版本索引；较大数据和完整run放**同一仓库GitHub Release**，无需另建网盘。

当前发布目标为MarcoJIANG5203/BDDM-10，脚本读取artifacts/registry.json中的repository。历史报告里的zsj-6/EI仅用于溯源，新数据与产物交付均使用新仓库。

## 当前正式A输入（2026-11-04）

`a-data-v1-20261104-r1`已正式发布，SHA256 `feb69777e7c03c51d580808182a4702a2b3991a0edd552ec4d0dcbf7b1a7129c`，4,666,169字节。B分支已同步A registry与原字节冻结记录；B实际资产API下载、8项冻结身份和五种子×两格式loader检查通过，见[接收证据](../reviews/B_formal_A_receipt_2026-11-04.json)。`fetch a-data-v1-20261104-r1`恢复cohort/audit/五split及来源/私有receipt，后两目录也已加入Git忽略。若已有不同版本audit，先在别处保留再恢复，默认不覆盖。A历史source/review两个包保留为pre-release，正式包另有独立ID。

A许可元数据冲突与E批准仅用户转述的限制随冻结记录保留；published仅表示实际字节已发布，A内容冻结不代表C/E已验收B结果。以下草稿/候选段落为历史记录，其当时的未发布状态已由本段取代。

## B-002正式输入结果包（2026-11-04）

`b-clinical-v1-20261104-r1`已打包prepared、尚待上传；112文件、155,365,045字节、SHA256 `2328d26682a39ccb895553d3cee3dc6dd11bd6506c41a5a0ac0f5d49890e8426`。含`results/clinical/20261105T055420_02d05b15`主矩阵及`20261105T055445_54dd08de`补充、正式最小输入/五split、源码/锁文件和来源/冻结证据。见[B交接](../handoffs/B/2026-11-04_B-002_formal_v1.md)。正式输入新run计算核验完成不表示C/E结果接受或D正式图稿可用。

11月4日A后续草稿交付：A分支`6b2650e`把原始临床树从当前Git索引移除，保留不可变历史。草稿Release的review-data ZIP为4,663,092字节、SHA256 `3a84a2432d6d2332c68b7e49199da597df2b5c3d724ea208b490f2c609dd1527`；原始full-source ZIP为50,674,324字节、SHA256 `a57d16dc5432b2e2518bc5f754b706c60de7b94d3fb496870687d4a564770cb1`。A回执记载两个资产均实际下载、校验和空目录恢复；A分支registry保持`prepared`、`draft=true`，标准`fetch`不得当作正式数据。来源许可证冲突尚待数据保管方澄清，见[E协调记录](../handoffs/E/2026-11-04_A_C_D_B_coordination.md)。

B候选补充包`b-candidate-v1-supplements-20261104-r1`已本地pack并空目录恢复核对：26文件、32,655,716字节、SHA256 `808537f305e7acb47fa01ce0eb5012d950b1224b92ca9c86ece470a1ee2e5e7f`。registry状态`prepared`且**未上传**，含临床逐患者结果与最小输入，许可澄清前不改标published；本地运行摘要随Git同步。

11月3日已收到A分支的`a-clinical-protocol-v1-20261103-full-r1`候选，固定源提交`ec8fd750cc17038bb0a73c37e1537a1e7a4d780e`。B已在忽略缓存中按源字节核验；正式data Release仍未发布，不能用`fetch`合成包来代替真实队列。A早期提交曾把临床文件直接放入Git；后续A分支`6b2650e`已从当前索引移除临床树，保留历史源提交。B不合并该数据树、不重写A历史。临时复核固定提交的方法见[接收报告](../reviews/A_received_2026-11-03.md)。

用户随后授权的B真实候选试跑使用版本包`b-candidate-natural-20261103-r1`交付。该包包含完整S0/S4 run、原字节最小输入（Parquet、audit、五split）和来源/许可，恢复到run记录的相对路径；不包含A全部原始ZIP。包的`kind=clinical_results`表示使用真实输入，`scientific_status=candidate_pre_freeze_not_accepted`表示仍未科学验收；Release标记pre-release。published只说明候选字节已上传，不是A正式data发布或C/E签收。

当前交付在B分支；同步该分支后可在registry状态为published时获取并复核：

11月4日另有五种子五场景主模型候选包`b-candidate-v1-matrix-20261104-r1`，完整run及最小原字节输入按同一规则交付，registry已标published/pre-release。同步本分支后执行`python scripts/sync_artifacts.py fetch b-candidate-v1-matrix-20261104-r1`，再执行`python reviews/verify_b_artifacts.py results/candidate-clinical/20261104T002604_e3a5a42b`及`python reviews/verify_candidate_bootstrap.py results/candidate-clinical/20261104T002604_e3a5a42b --output .artifact-cache/candidate-full-bootstrap-recheck.json`。常规Release下载失败时可按下文的资产API方案替换bundle ID使用，并始终核对registry SHA256；本轮实际资产API下载123,342,522字节、SHA及空目录恢复已通过，证据见`reviews/B_candidate_v1_matrix_release_2026-11-04.json`。它仍是候选预冻结包，不是A正式data发布或C/E科学验收。

```powershell
git fetch origin
git switch b/core-methods-experiments
git pull --ff-only
python scripts/sync_artifacts.py fetch b-candidate-natural-20261103-r1
python reviews/verify_b_artifacts.py results/candidate-clinical/20261103T122334_93a9a266
python reviews/verify_candidate_bootstrap.py results/candidate-clinical/20261103T122334_93a9a266 --output .artifact-cache/candidate-bootstrap-recheck.json
```

本机实测上述标准下载报`release not found`，但Release元数据可读；资产API下载成功，SHA256匹配，下载包在空目录恢复后120指标行和全部哈希复核通过。若遇同样问题，使用registry登记的资产API下载并校验恢复（PowerShell；用二进制文件流保存，避免文本重定向损坏ZIP）：

```powershell
@'
import json, subprocess
from pathlib import Path
from scripts.sync_artifacts import extract_bundle
registry = json.loads(Path('artifacts/registry.json').read_text(encoding='utf-8'))
entry = registry['bundles']['b-candidate-natural-20261103-r1']
assert entry['status'] == 'published'
archive = Path('.artifact-cache') / entry['asset']
archive.parent.mkdir(parents=True, exist_ok=True)
with archive.open('wb') as stream:
    subprocess.run(['gh', 'api', entry['asset_api'], '-H', 'Accept: application/octet-stream'], stdout=stream, check=True, timeout=60)
extract_bundle(archive, Path.cwd(), entry['roots'], entry['sha256'])
print('Downloaded, SHA256 verified, and restored candidate trial')
'@ | python -
```

随后执行上面的两条独立核验命令即可；现有同字节文件跳过，不同内容默认拒绝覆盖。临床候选包不添加普通Git备用ZIP；需要相应私有仓库访问权限。小型摘要在[候选结果目录](../reports/candidate-trials/20261103T122334_93a9a266/SUMMARY.md)，原始manifest及输入字节保留。

本次固定合成验收包另有`artifacts/packages/b-synthetic-20261102.zip`备用副本（约30MB）。它与已发布Release的SHA256完全相同。弱网下fetch优先校验Git副本再恢复，不再等待Release下载；不改变版本与内容。真实大型数据仍使用Release。

## 接收者

```powershell
git pull --ff-only
python scripts/sync_artifacts.py list
python scripts/sync_artifacts.py fetch b-synthetic-20261102
```

fetch先看registry是否登记并提供了Git备用ZIP，否则用gh下载Release（该方式需先`gh auth login`）；两条路径都核对同一SHA256，再恢复声明目录。相同本地文件跳过，不同内容默认报错；确定切换新版本时先保留自己的工作，再显式加`--replace`。不改哈希绕过失败。

为保持Windows/macOS/Linux间的文件对应关系，包内不使用仅大小写不同的重名、尾点/尾空格路径，也不通过本机符号链接或目录联接重定向交付目录。工具在写入前检查整包路径；`--replace`只允许替换明确的普通文件，不放宽目录边界。

git pull不会自动下载Release大文件，先读STATUS和registry再获取所需bundle。published代表已上传，prepared仅代表本地打包。私有仓库成员需要相应访问权限。

## 生产者

A完成且C核查后发布新版本（以下为通用格式；当前实际正式输入使用上文A版本）：

```powershell
python scripts/sync_artifacts.py pack data-v1 --paths data/processed splits --tag data-v1 --kind data
python scripts/sync_artifacts.py publish data-v1
```

pack生成dist/artifacts/data-v1.zip，登记路径、大小、文件数与SHA256为prepared；publish用已登录gh上传，成功后改published，失败不伪造完成。再次发布用data-v2等新ID/tag，不覆盖旧版本。

随后把registry、STATUS、CHANGELOG和handoffs/A/记录一起提交并合并main。cohort、audit和五split必须同版；生产脚本和C核查放Git，audit声明不替代原始小时核对。接口见[数据说明](../docs/A到B_数据交接说明.md)。

B发布真实结果时：

```powershell
python scripts/sync_artifacts.py pack clinical-main-v1 --paths results/clinical/实际run_id --tag clinical-main-v1 --kind clinical_results
python scripts/sync_artifacts.py publish clinical-main-v1
```

换成实际已验收run路径，保留原manifest不手改；可阅读小表放reports/，D的每个数字指向对应版本/run。

## 当前边界

- b-synthetic-20261102仅含两份最终合成run及对应合成输入；可重建全部验证产物。
- A正式技术版本已发布并内容冻结，B已核对输入；许可冲突、E批准来源限制和C/E新run结果验收仍分别记录，不因published自动消失。
- 原始大文件、正式患者表、split和完整results默认不入普通Git，使用版本包；Git保留目录说明和元数据。

历史manifest中的本机绝对路径保留作溯源；复核脚本在当前项目定位同字节输入，只有SHA256匹配才接受，不依赖原电脑盘符。.gitattributes保留合成输入字节，避免换行转换破坏校验。
