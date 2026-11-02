# 2026-11-02 · E · E-001仓库交付

已发布私有仓库https://github.com/zsj-6/EI ，默认main，首批代码提交3397dfa66462588b5340db53bd928c0f5f900308。配置代码/文档/状态随Git更新，大文件随本仓库Release版本包更新。

已发布tag artifacts-2026-11-02，资产b-synthetic-20261102.zip，79文件、29,717,166字节。SHA256为14909d30b2b7bfa1df6316e798e1a93e8482adda408e02dbe0a9a90f6e57c6f4，已与GitHub上传完成的远端digest比对一致。包仅含两个最终合成run及对应合成输入，非临床数据。

最终同步工具14项测试与原科学18项合计32项通过；新克隆32测试/38.28s和实际demo通过，工作区干净。独立复核的问题全部关闭。

Release上传及远端digest核验成功，但本机Release下载连接停滞，资产API重试120s超时；没有将其记录为成功。为该固定合成包提供同SHA Git备用ZIP（代码提交049cfc5）。新克隆实际从Git拉取ZIP，恢复前确认两最终run目录不存在；运行fetch后恢复成功，独立核算1440+576=2016指标行及全部产物/源码/输入/划分哈希。完整验收见reviews/repository_delivery.md，Git恢复不等于Release下载成功。

全组同步后阅读collaboration/STATUS.md、HANDOFFS.md、DATA_SYNC.md、CHANGELOG.md，交付时按handoffs/TEMPLATE.md记录并提交状态。A正式数据仍未交付，C/D实质任务未代为标记完成。成员接收和临床审计仍由相应负责人记录。
