# 仓库同步独立复核

日期：2026-11-02。依据requesting-code-review流程，只读检查scripts/sync_artifacts.py、tests/test_artifact_sync.py、reviews/verify_b_artifacts.py、Git属性/忽略规则及协作文档。未执行远端操作，未修改实施代码，未重复原18项科学测试。

## 结论

补丁复核通过，可以继续首次提交、推送和Release发布。原2项Important及1项Minor均已修复关闭，当前无未关闭实质问题。未发现科学协议改变。当前prepared是明确的中间状态，不作为发布失败，也不声称Release已发布。

## 初审Important（均已关闭；行号为修复前）

1. scripts/sync_artifacts.py:75—77、87—90：重复路径检测使用区分大小写的PurePosixPath，实际Windows目标路径却不区分大小写。ZIP含data/processed/cohort.csv和data/processed/COHORT.csv时，预检查认为是两条不存在的新路径；默认replace=False仍会顺序覆盖同一文件，且最后返回成功。已在临时目录实测：第一项FIRST、第二项SECOND，解压后仅1个文件，内容SECOND。此ZIP可以在大小写敏感机器上由正常打包产生，因此影响跨平台数据完整性。建议按最终目标文件系统规范化的绝对路径检测重复，并拒绝Windows尾点/尾空格等路径别名；增加大小写冲突在写入前拒绝且目标目录仍为空的测试。

2. scripts/sync_artifacts.py:65—72：allowed_roots校验只看字面路径，而target.resolve()只检查项目根。若本地data/processed或其子目录是指向同仓库其他目录的符号链接/目录联接，合法字面路径仍可写入声明根之外，例如data/processed -> src后写入src下文件。ZIP自身的symlink检查无法检测本地已有链接。建议拒绝解压目标及其祖先中的符号链接/目录联接，或对解析后的目标仍严格校验实际声明根边界并排除根本身重定向。应在任何写入前验证，--replace不应放宽目录范围。此项由控制流确认，未创建系统链接进行演示。

## 初审Minor（已关闭；行号为修复前）

reviews/verify_b_artifacts.py:49—50：正式数据跨机器重定位回退名固定cohort.parquet，正式入口也支持CSV。历史配置为另一台机器的绝对cohort.csv时，即使当前data/processed/cohort.csv存在且SHA完全正确，也会只尝试parquet并失败。建议根据历史configured路径后缀选择规范回退文件，或尝试两个受支持名称且必须精确SHA匹配。当前合成包不受影响。

## 已核实的正向证据

- 两份最终科学run manifest所列12个原src/scripts文件哈希仍与当前文件一致；原算法及原科学CLI未修改。
- 本地prepared包实际SHA256等于registry所记14909d30b2b7bfa1df6316e798e1a93e8482adda408e02dbe0a9a90f6e57c6f4。
- 下载先检查整包SHA再提取；普通路径穿越/盘符/未声明根被拒绝；常规已有同字节文件跳过、不同内容默认拒绝；publish只有gh上传返回成功后才设置published，失败不会伪造状态。
- 初审7项新增测试GREEN日志已查阅，涵盖正常往返、SHA失败、常见路径逃逸和历史Windows路径重定位；修复后扩展至13项，新增路径别名、本地链接及CSV回退验证，见下文。
- configs/demo.yaml使用相对输入路径；合成输入在.gitattributes中禁用换行转换；Git忽略正式数据/完整run/缓存，Release保存完整包，README区分git pull与fetch。
- 状态/交付/变更记录清楚区分生产者提交、接收人验收及真实数据尚未交付；准备、发布两个状态含义明确。后续初次push、Release上传、published状态提交及干净clone验证仍应按计划完成，不能以本次只读检查替代。

## 修复后复核

- 路径别名：relative_name拒绝各段尾点/尾空格；打包及解压均使用casefold键检测同名冲突。解压完整预检查通过后才进入写入循环，大小写冲突不会先落盘。对应3个大小写/尾点/尾空格测试检查拒绝且目标目录未创建。Important 1关闭。
- 本地链接：reject_local_links从项目根开始逐段检查is_symlink/is_junction，解压在写入前对每个目标调用，pack也拒绝输入链接/联接。replace不绕过这一步。新增测试实际在Windows通过mklink /J构造声明根及嵌套目录两种联接，并以replace=True验证仍拒绝、声明根内的先行正常条目也未落盘。Important 2关闭。
- CSV回退：cohort_fallback读取配置路径后缀，并仅接受.csv/.parquet；verify已实际调用此函数，仍由resolve_input要求SHA完全一致，不改变原始manifest或降低校验。新增测试覆盖历史Windows绝对CSV及parquet。Minor关闭。
- 已核阅reviews/repository_review_RED.log：3种路径别名及2种本地联接在旧实现均未抛错，5项失败；修复后reviews/repository_review_GREEN.log显示13 passed in 0.79s。本复核者只读审阅补丁与测试期望，未重复原科学测试。

发布就绪结论仅指本轮代码及文档复核。Release是否已经可下载、registry是否已记录published、干净clone是否完整复现，仍以随后的实际发布验证为准。
