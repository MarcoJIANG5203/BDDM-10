# 2026-11-02 · E · 仓库迁移交付

用户指定新统一仓库：https://github.com/MarcoJIANG5203/BDDM-10 ，私有、main，当前账号具备WRITE权限。

新仓库原有初始提交a07b0272d25184a4b8791317de9dd4ea5aa3b99f（仅README）。通过合并保留双方历史，README采用BDDM-10标题及完整项目入口，不强推覆盖已有历史。

本地origin指向新仓库，legacy-origin保留旧zsj-6/EI。共享克隆指令、数据发布目标和交接入口改到新仓库；旧历史报告、run和manifest不重写。

固定合成包字节和SHA256保持不变，Git备用随迁移上传。新仓库Release artifacts-2026-11-02已发布，远端资产大小29,717,166字节及SHA256与registry一致，见reviews/migration_release.json。

迁移验证完成：从新仓库独立克隆，32测试通过（30.65s，reviews/migration_clone_tests.log）；实际fetch从新仓库Git副本恢复完整包（migration_clone_fetch.log）。两run分别1440/576指标行、45/25产物哈希、每run12科学源码及输入/audit/5或1份split哈希均通过。证据为migration_matrix_audit.json及migration_supplements_audit.json。原始a07b027与旧项目d9e8cf4均为新main祖先，双方历史保留。

后续成员从新仓库同步main，按STATUS/HANDOFFS/DATA_SYNC/CHANGELOG交付并维护版本。A/C/D临床实质任务不据本次迁移标记完成；旧验收报告内旧仓库地址保留作历史证据，不是当前发布目标。
