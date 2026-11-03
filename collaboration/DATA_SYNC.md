# 数据和完整产物同步

Git维护代码、协议、状态、小样本和版本索引；较大数据和完整run放**同一仓库GitHub Release**，无需另建网盘。

当前发布目标为MarcoJIANG5203/BDDM-10，脚本读取artifacts/registry.json中的repository。历史报告里的zsj-6/EI仅用于溯源，新数据与产物交付均使用新仓库。

11月3日已收到A分支的`a-clinical-protocol-v1-20261103-full-r1`候选，固定源提交`ec8fd750cc17038bb0a73c37e1537a1e7a4d780e`。B已在忽略缓存中按源字节核验；正式data Release和registry条目仍未发布，不能用`fetch`合成包来代替真实队列。当前A分支把临床文件直接放入Git，与本页约定不符；B不合并该数据树、不重写A历史，待A/C/E审核后由A/E发布版本包。临时复核固定提交的方法见[接收报告](../reviews/A_received_2026-11-03.md)。

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

A完成且C核查后发布新版本（当前正式数据未就绪，以下为将来交付格式）：

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
- A候选已提交并经B接口核对；负责人确认、C独立复核、E精度/冻结决定及正式Release尚待完成，审核后发布登记。
- 原始大文件、正式患者表、split和完整results默认不入普通Git，使用版本包；Git保留目录说明和元数据。

历史manifest中的本机绝对路径保留作溯源；复核脚本在当前项目定位同字节输入，只有SHA256匹配才接受，不依赖原电脑盘符。.gitattributes保留合成输入字节，避免换行转换破坏校验。
