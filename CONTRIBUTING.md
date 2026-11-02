# 团队提交与同步

开始前在无未提交改动时执行`git switch main`和`git pull --ff-only`，阅读README、STATUS、HANDOFFS和CHANGELOG。有自己的修改时先提交到自己的分支，不用覆盖文件的方式处理同步。

从最新main建立岗位分支，例如`a/cohort-v1`、`b/clinical-main`、`c/metric-audit`、`d/paper-draft`、`e/integration`。完成后push并发起Pull Request，由接收人检查再合并main。首次空仓库初始化直接写main，之后按此流程协作，不强制推送或覆盖他人提交。

## 每次交付一起提交

1. 实际文件或数据/产物版本索引。
2. `collaboration/STATUS.md`中本岗位状态、阻塞和下一步。
3. 要求变化时更新`collaboration/HANDOFFS.md`；协议、数据和接口变化写入`collaboration/CHANGELOG.md`。
4. 从`handoffs/TEMPLATE.md`复制日期/岗位命名的交付记录，写版本、路径、验证证据和接收人。
5. 大文件成功上传Release后提交`artifacts/registry.json`的published状态及真实SHA256；prepared不算已同步。

生产者记录“已提交待验收”，接收人记录“验收通过”。B代码复核不替代C的真实标签/指标核验。状态依据实际证据，不复制示例数字。

代码变更运行相关测试；影响完整流程时运行`python -m pytest -q`并记录输出。文档修改检查链接和口径。不提交凭证、虚拟环境、缓存、原始大数据或完整患者输出，后两者使用版本包。

已有固定合成验收ZIP是为弱网设置的Git备份，SHA256与Release一致；不据此把真实临床患者表和任意大输出放普通Git。

患者划分、标签、时间窗、指标分母、共形规则和主要比较变更须写原因、影响的旧结果、是否测试后变更，由E协调A/B/C确认版本。旧run不手改，修正后生成新run。共享说明使用仓库相对路径或Release版本，不用个人盘符作为唯一交付位置。
