# 既有研究谱系隔离与未来研究 Gate v0.1

日期：2026-07-18
状态：PASSED_ARMED_NO_NEW_STUDY

## 结论

历史数据和结果没有被删除或搬移；它们被限制为 provenance、失败复盘、污染审计和
排除用途。旧 V2-P2 cursor、order63、continuous authorization、pilot standing
authorization、归档 v0.2 及 v0.3 execution authorization 均已撤销，并在旧研究
执行入口 fail closed。当前未来研究
manifest 为空，因此训练、验证、确认性测试、模型 API 和论文效果结论均未获授权。

## 隔离投影

- 硬排除任务：501 个。
- 默认阻断项目：17 个；若未来需要项目复用，必须在接触新数据前另行预注册并版本化本规则。
- 硬排除旧元数据内容标识 SHA-256：3420 个；其中精确 patch payload SHA-256 为 522 个。
- cutoff HEAD tracked 内容：1515 个路径、1509 个唯一 blob。
- cutoff 工作树内容指纹：273918 个文件，57172 个唯一 SHA-256，4415259787 bytes，reparse/nonregular=0；只哈希、不解析内容。
- 全部 Git refs 可达历史 blob 指纹：3232 个 blob、3232 个 raw SHA-256。
- 冻结旧研究谱系：7 条。
- fail-closed 全部旧研究 Python 入口：280 个。
- 历史原路径与字节：保留。

## 允许与禁止用途

允许用途只有 provenance、失败分析、污染审计、任务/项目/payload 去重排除，以及明确
标注为 development-only 的假设动机。禁止进入训练/SFT/RL/reward、开发或验证集、
prompt/model/超参数选择、采样与停止规则调整、样本量规划、确认性测试、效果量合并、
论文数字/表/图/claim，以及任何读取旧 raw response 或 rationale 的未来流水线。
复制或重命名不能改变内容指纹；未来命名空间中的 hardlink、symlink、junction 与其他
reparse 链均被拒绝。哈希冻结读取了范围内文件字节，但没有解释或输出凭证值、raw
response、rationale、prompt 或 patch 文本。

## 原 P1 Gate 的诊断

原 P1 按当前脚本集合重算为 `failed`，发现 9 条命名空间冲突。
其历史 `status=passed` 不再被信任；本 Gate 不给旧 pilot 添加例外，而是把整条 pilot
谱系封存。

## Gate

- `registry_active_fail_closed`: PASS
- `projection_source_hashes_exact`: PASS
- `blocked_task_projection_exact`: PASS
- `blocked_project_projection_exact`: PASS
- `blocked_payload_projection_exact`: PASS
- `blocked_content_fingerprint_registry_exact`: PASS
- `blocked_payload_exclusion_registry_exact`: PASS
- `cutoff_source_commits_identical`: PASS
- `revoked_authorization_records_exact`: PASS
- `old_cursor_frozen_before_order63`: PASS
- `old_pilot_complete_development_only`: PASS
- `old_execution_entrypoints_fail_closed`: PASS
- `future_manifest_empty_and_unauthorized`: PASS
- `adversarial_manifest_self_tests_pass`: PASS

当前状态是 `ARMED / NO NEW STUDY`，不是新研究数据有效性的空集证明。未来研究必须
先在 `data/future_studies/<study_id>/` 建立独立输入、非空 manifest 和作者签核，
研究代码只能放在 `future_studies/<study_id>/`，科学输入必须经 `src/cross_review/future_study_loader.py` 读取。
再把预使用清单写入唯一规范路径 `data/protocols/future_research_input_manifest_v0_1.json`，
并运行 `python scripts/audit_research_lineage_isolation.py --validate-manifest data/protocols/future_research_input_manifest_v0_1.json`。签核是可审计的作者声明，不是密码学身份认证或可信时间戳。
仓库 Gate 约束受认可的研究流水线；同一操作系统用户仍可绕过代码直接读取文件。若要阻止这种读取，
需要另行采用操作系统账户/ACL 隔离，本次未擅自改变文件权限。
