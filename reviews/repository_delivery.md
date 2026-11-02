# 团队仓库发布与同步验收

日期：2026-11-02，北京时间。用户授权将现有项目上传zsj-6/EI，并在仓库持续维护数据同步及成员交付要求。

## 发布结果

- 私有仓库：https://github.com/zsj-6/EI ，默认分支main；本地origin/upstream已设置。
- 首批代码/文档提交3397dfa，发布索引提交4318131，Git备用传输代码提交049cfc5。后续文档验收提交另计，科学协议仍v1。
- 当前状态、交付矩阵、数据同步、变更日志和交付模板均已入库；AGENTS/CONTRIBUTING要求每次任务交付一起更新状态，成员pull后读取。
- 原始研究资料保留，内部聊天规划/环境快照/缓存/开发旧run不上传。普通Git保留代码、文档、小表、合成输入，以及本次固定合成ZIP备用副本。

## 完整产物

Release：https://github.com/zsj-6/EI/releases/tag/artifacts-2026-11-02 。资产b-synthetic-20261102.zip，79文件、29,717,166字节，SHA256：

```text
14909d30b2b7bfa1df6316e798e1a93e8482adda408e02dbe0a9a90f6e57c6f4
```

已读取GitHub远端响应，确认isDraft=false、asset state=uploaded，大小/digest与registry一致（repository_release.json）。索引状态为published。

本机Release客户端下载0字节停滞，核实自有进程后停止；资产API另一次重试120s超时。此路径未验收成功。故为固定合成包增加Git备用副本artifacts/packages/b-synthetic-20261102.zip，其字节与Release完全一致，fetch优先使用该副本；真实大数据仍按Release版本管理。

## 独立目录实际验收

从远端克隆到另一个临时目录，经git pull取得备用ZIP；没有从原工作区手工复制结果。恢复前确认两个最终run目录不存在，再执行：

```powershell
python scripts/sync_artifacts.py fetch b-synthetic-20261102
python reviews/verify_b_artifacts.py results/synthetic/20261102T063118_fa76f8a8
python reviews/verify_b_artifacts.py results/synthetic/20261102T063118_bdf6797a
python -m pytest -q
python scripts/run_experiments.py --config configs/demo.yaml
```

结果：Git副本恢复成功；两个完整run均通过全部文件哈希及独立CSV指标核算，分别1440与576行，共2016行。核对45/25项产物哈希、每run12份科学源码、输入/audit和5/1份split哈希，候选池/K、概率/std/翻转、零分母和指标分母均一致。Windows历史路径在新目录正确定位同字节输入，不依赖原电脑盘符。

本机最终完整测试**32 passed in 21.02s**；远端克隆最终测试**32 passed in 38.28s**。包含原科学18项和新增同步/路径14项。新克隆实际demo成功，git status为空。独立复核发现的路径大小写/尾点空格、本地链接重定向及CSV格式问题均已测试修复并关闭；备用路径也经独立复核通过。

证据：repository_tests.log、repository_clone_tests.log、repository_clone_demo.log、repository_clone_fetch.log、repository_clone_matrix_audit.json、repository_clone_supplements_audit.json、repository_review.md。此报告的Git恢复通过不能解读为Release下载通过。

## 后续共同维护

成员同步main后先读collaboration/STATUS.md、HANDOFFS.md、CHANGELOG.md和DATA_SYNC.md。交付时一起提交真实状态、版本索引与handoffs记录，接收人再记验收。A正式队列尚未交付，C真实标签/指标核查及D真实结果稿件仍待推进，不据本次模拟软件验收标记完成。
