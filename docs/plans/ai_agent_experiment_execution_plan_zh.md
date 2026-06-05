# AI 执行版实验计划：Evidence-First Patch Verification

最后更新：2026-06-05

本文档用于直接交给 AI agent 执行。它不是论文正文，也不是历史记录；它是当前研究的执行任务书。执行时以本文件为主，以 `docs/INDEX.md` 作为索引，以 `README.md` 作为项目状态入口。

## 0. AI 执行契约

接手本计划的 AI agent 必须把自己当作实验执行者，而不是论文包装者。所有动作按“先验证、再运行、再报告”的顺序推进。

每一轮执行必须遵守：

1. 先读取本计划和索引，再运行状态审计；不能直接从记忆或历史对话开始跑实验。
2. 每次修改代码、实验流程、prompt 或计划后，必须同步更新 `README.md`、`docs/INDEX.md`、相关计划文档和 `docs/experience/engineering_notes.md`。
3. 每次真实 API 调用前，必须先刷新计划状态和 pre-API handoff；真实 API 调用后，必须立刻做 postprocess、run completeness、paper readiness 和 local quality gate。
4. 每个阶段只接受本计划列出的产物作为证据。命令输出、口头描述、mock 结果、dry-run prompt 都不能替代缺失产物。
5. 如果一个阶段失败，只能修复该阶段的输入、代码或配置，然后重跑该阶段；不能跳过失败阶段继续后续实验。
6. 如果结果不支持假设，必须如实记录为负结果、条件性结果或停止结论；不能改样本、改阈值或改叙述来制造正向结果。

AI agent 的最终回复必须说明：

- 完成到哪个阶段；
- 运行了哪些命令；
- 新增或更新了哪些文件；
- 哪些 gate 通过、哪些仍 blocked；
- 是否存在真实 API model results；
- 是否可以写正向论文结论；
- 还需要用户提供什么输入。

## 1. 任务目标

本项目要验证的问题是：

> 对 AI coding agent 生成的 candidate patch，`evidence_first` verification 是否比 `llm_only` review 更少错误接受 incorrect/partial/overfitted patches，同时不明显牺牲 correct patch 的接受率？

必须保持研究边界：

- 研究对象是 patch 是否应被接受，不是普通代码审查是否能发现 bug。
- ground truth 来自可执行 oracle、patch construction metadata 和人工可追溯构造依据，不来自另一个 LLM 的意见。
- 当前只做 `llm_only` 与 `evidence_first` 两个条件；不要自行扩展 majority、agent-context、多轮讨论或新框架。
- 如果结果不支持假设，必须如实输出负结果或停止，不得包装成正向结论。

## 2. 执行前必须读取

AI agent 接手后，先按顺序读取：

1. `README.md`
2. `docs/INDEX.md`
3. `docs/plans/ai_agent_experiment_execution_plan_zh.md`
4. `docs/paper/research_definition.md`
5. `docs/experiments/patch_candidate_schema.md`
6. `docs/experiments/evidence_first_protocol.md`
7. `docs/experiments/patch_verification_metrics.md`
8. `docs/experience/engineering_notes.md`

如果文档和代码冲突，先修正冲突，再继续实验。不能一边带着冲突一边跑 API。

## 3. 禁止事项

执行过程中禁止：

- 把 `.env`、API key、`configs/*.local.json`、raw API outputs、benchmark checkouts、`data/` 或 `tmp/` 打包或提交。
- 把 dry-run、mock run、prompt 渲染结果写成模型实验结果。
- 在 validation、preflight 或 label-leakage gate 失败时继续调用 API。
- 因为样本让指标变差而删除样本。
- 修改 prompt 后不重新 dry-run、不重新记录 prompt change log。
- 使用 placeholder provider model id 调用 API。
- 在当前目录不是 Git 仓库时声称已同步 GitHub。

## 4. 当前已完成状态

当前本地 no-API 部分已完成：

- `outputs/patch_verification_pilot_001/`：原始 no-API pilot。
- `outputs/patch_verification_pilot_repro_001/`：一键复现实验输出。
- 30 个 candidate patches。
- 90 条 deterministic baseline verifier outputs。
- 30/30 executable validation passed。
- 60 条 prompt dry-run records。
- mock API smoke 只验证本地链路，不是实验结果。

当前未完成且不能跳过：

- `.env` 尚未确认存在。
- `configs/model_selection.local.json` 尚未确认存在。
- `configs/api_pilot.local.json` 尚未确认存在。
- 真实 DeepSeek official API run 尚未完成。
- 真实 API 结果的 failure analysis、gate report 和 paper readiness 尚未完成。
- 当前新目录尚未确认是 Git 仓库。

## 5. 总执行流程

严格按以下顺序执行：

```text
read docs
-> readiness audit
-> plan progress audit
-> no-API reproduction
-> reproducibility / validation check
-> model selection local config
-> API local config
-> API preflight
-> check-only guarded workflow
-> 2-candidate real API smoke
-> smoke postprocess and gate
-> 30-candidate real API full run
-> full postprocess and gate
-> failure analysis
-> paper readiness audit
-> update paper draft
-> anonymous artifact dry-run/package
-> goal completion audit
-> local quality gate
```

任何阶段失败，只能在本阶段修复；不能跳到后续阶段。

## 5.1 阶段产物契约

AI agent 应使用下表判断每个阶段是否真正完成。没有列出的证据文件时，不得口头标记完成。

| 阶段 | 目的 | 必须存在的证据 | 通过标准 |
| --- | --- | --- | --- |
| 0 状态审计 | 明确当前能否继续 | `outputs/readiness_audit/latest.json`, `outputs/plan_progress/latest.json`, `outputs/handoff/pre_api_handoff.md` | no-API ready；API/Git 阻塞原因被明确列出 |
| 1 no-API 复现 | 证明本地数据和脚本可复现 | `outputs/patch_verification_pilot_repro_001/`, `outputs/reproducibility/pilot_compare.json` | 30 candidates、90 baseline outputs、30/30 validation、60 dry-run prompts、deterministic matched |
| 2 标签边界 | 防止 label leakage 和无效样本 | `validation_summary.json`, `evidence_packets.jsonl`, `candidates.jsonl` | 30/30 validated；模型可见 evidence 不含 hidden labels 或 construction labels |
| 3 模型选择 | 防止 cherry-picking | `configs/model_selection.local.json`, `outputs/model_selection/latest.json` | slug 非 placeholder；来源、能力分档、局限性完整记录 |
| 4 API 配置 | 建立可运行但不泄密的本地配置 | `.env`, `configs/api_pilot.local.json`, `outputs/model_selection/api_config_check.json` | API config 和 model selection 的 model 完全一致；preflight ready |
| 5 check-only | 验证 guarded workflow 不会误调用模型 | `outputs/api_workflow_check/latest.json` | `model_call_attempted = false` 且 preflight passed |
| 6 smoke run | 用 2 个 candidate 检查真实 API 链路 | `outputs/patch_verification_api_pilot_001/reviews.jsonl`, `run_completeness.json`, `gate_report.md` | 4 条非 mock review；raw response 可追踪；JSON 解析无系统性错误 |
| 7 full run | 获得主实验结果 | `outputs/patch_verification_api_pilot_002/reviews.jsonl`, `metrics.json`, `run_summary.md` | 60 条非 mock review；不覆盖 smoke 输出；metadata 完整 |
| 8 postprocess | 生成结果解释材料 | `api_pilot_report.md`, `failure_examples.md`, `gate_report.md`, `run_completeness.md`, `paper_readiness.md` | completeness passed；gate verdict 不是 `not_evidence` |
| 9 结果判定 | 决定是否支持假设 | `gate_report.json`, `metrics.json`, `failure_examples.json` | 按阶段 9 规则判断，不能只看单个指标 |
| 10 failure analysis | 解释结果而非只报数 | `failure_examples.md` 和人工抽查记录 | 案例来自真实 API output；每个案例能追踪到 hidden oracle label |
| 11 论文更新 | 把实验状态同步到论文 | `docs/paper/*`, `outputs/paper_readiness/latest.md` | 正向 claim 只在 `positive_claim_ready = true` 时写入 |
| 12 artifact | 准备匿名补充材料 | `artifacts/research95_anonymous_artifact.zip`, `artifacts/research95_anonymous_artifact_audit.md` | 不含 credentials、local configs、raw outputs、data/tmp/checkouts |
| 13 本地质量门 | 防止交付物不一致 | `outputs/local_quality_gate/latest.md`, `outputs/goal_completion/latest.md` | local gate passed；goal completion 如实报告 complete/blockers |

## 5.2 实验记录格式

每次运行 smoke、full run 或 postprocess 后，AI agent 必须在最终回复或交接文档中记录以下字段：

```text
run_id:
run_dir:
run_type: no_api_repro | smoke_api | full_api | postprocess | quality_gate
date:
model_slug:
conditions:
candidate_count:
review_record_count:
mock_review_count:
command:
key_outputs:
gate_verdict:
paper_claim_allowed: yes | no
notes:
```

如果 `model_slug`、`review_record_count` 或 `mock_review_count` 无法填写，说明该 run 不能作为真实实验结果。

执行者应使用以下命令刷新当前 run ledger：

```powershell
python scripts\write_experiment_run_records.py `
  --out-json outputs\experiment_run_records\latest.json `
  --out-md outputs\experiment_run_records\latest.md
```

验收：

- no-API 记录必须明确 `paper_claim_allowed = no`。
- smoke API 记录只能作为链路检查，不能作为 full paper result。
- full API 记录只有在 60 条非 mock review、completeness passed 且 gate verdict
  为 `continue` 时才能标记 `paper_claim_allowed = yes`。
- local quality gate 记录只能报告 readiness，不是模型实验结果。

## 5.3 失败处理规则

失败时按以下规则处理：

- readiness 或 preflight 失败：只修配置、路径、缺失文件或 credential boundary；不能调用 API。
- validation 失败：只修 dataset builder、candidate patch、oracle 或标签依据；不能删除让结果变差的样本。
- label leakage 失败：只修 evidence packet/prompt 边界；修完后重新 dry-run 和 validation。
- model selection 失败：重新让用户确认 provider model id 和选择依据；AI 不能自行替换模型。
- smoke run 失败：分析 raw response、parser、prompt schema、API 错误和 run completeness；不能直接 full run。
- full run 部分失败：先检查 `run_error.json` 和 completeness audit；如果存在 `run_error.json`、review 数不足或 raw response 缺失，该 run 不能进入论文结果。
- gate 不支持正向结论：写负结果或停止建议；不能通过改写研究问题来声称方法有效。
- local quality gate 失败：先修复本地质量问题；不能打包 artifact 或声称完成。

## 5.4 最小人工输入

真实实验前，人类必须明确给出：

```text
DEEPSEEK_API_KEY 已放入未追踪 .env: yes/no
provider model id:
api provider:
provider:
model selection source:
model selection source URL:
capability source:
capability band:
short rationale:
是否允许真实 API smoke run:
是否允许真实 API full run:
是否初始化并同步 Git 仓库:
GitHub remote URL:
```

缺少任一项时，AI agent 只能继续 no-API、dry-run、文档、artifact dry-run 或本地质量审计。

## 6. 阶段 0：状态审计

执行：

```powershell
python scripts\audit_execution_readiness.py `
  --out-json outputs\readiness_audit\latest.json `
  --out-md outputs\readiness_audit\latest.md
```

验收：

- no-API readiness 应为 ready。
- API readiness 可以暂时不 ready，但原因必须是缺少 `.env`、model selection 或 local API config。
- 如果 no-API readiness 不通过，先修复 no-API pipeline。

输出：

- `outputs/readiness_audit/latest.json`
- `outputs/readiness_audit/latest.md`
- `outputs/plan_progress/latest.json`
- `outputs/plan_progress/latest.md`

阶段进度审计：

```powershell
python scripts\audit_ai_plan_progress.py `
  --out-json outputs\plan_progress\latest.json `
  --out-md outputs\plan_progress\latest.md
```

当前最新阶段状态：

- complete：阶段 0、1、2、13。
- partial：阶段 11、12。
- blocked：真实 API 相关阶段，因为缺少 `.env`、模型选择 local config 和 API local config。

真实 API 前还应生成人工输入包：

```powershell
python scripts\write_human_input_packet.py `
  --out-json outputs\handoff\human_input_packet.json `
  --out-md outputs\handoff\human_input_packet.md
```

当前缺失的 required inputs：

- `provider_api_key`
- `provider_model_id`
- `model_selection_rationale`
- `api_local_config`

如果只需要刷新当前本地交接状态，使用一键 pre-API handoff：

```powershell
python scripts\write_pre_api_handoff.py `
  --out-json outputs\handoff\pre_api_handoff.json `
  --out-md outputs\handoff\pre_api_handoff.md
```

该命令只执行本地审计与报告生成，不调用模型 API。
它会刷新 experiment run records，并把
`outputs/experiment_run_records/latest.md` 列为交接报告之一。

Git 同步必须先生成决策包，不能擅自初始化或推送：

```powershell
python scripts\write_git_sync_packet.py `
  --out-json outputs\handoff\git_sync_packet.json `
  --out-md outputs\handoff\git_sync_packet.md
```

当前状态：`research95` 不是 Git 仓库；旧仓库 remote 是
`https://github.com/gaoming-a/review.git`；是否复用或新建 remote 需要用户确认。
决策包会输出 remote 决策记录模板、允许暂存范围、ignore 验证命令、
cached diff 检查命令和同步后验收标准。AI agent 只能在用户明确确认
`initialize_clean_workspace`、`github_remote_url` 和
`reuse_old_review_remote` 后执行其中的 Git 命令模板；确认前不能运行
`git init`、`git add`、`git commit` 或 `git push`。

Git 交接安全审计：

```powershell
python scripts\audit_git_sync_packet.py `
  --out-json outputs\git_sync_packet_audit\latest.json `
  --out-md outputs\git_sync_packet_audit\latest.md
```

验收：

- 保留人工决策门。
- 命令模板不包含 `git add .`。
- ignored local files 在暂存前被检查。
- cached diff 在暂存后被检查。
- `git push` 只能作为最后一步模板出现。

API 失败处理审计：

```powershell
python scripts\audit_api_failure_handling.py `
  --out-json outputs\api_failure_handling\latest.json `
  --out-md outputs\api_failure_handling\latest.md
```

验收：

- 使用本地拒连地址，不访问 OpenRouter 或任何模型 API。
- 真实 API 失败路径会写入脱敏 `run_error.json`。
- stdout、stderr 和 `run_error.json` 不泄露 dummy secret 或 provider key。
- completeness audit 会拒绝包含 `run_error.json` 的 run。

## 7. 阶段 1：复现 no-API pipeline

执行：

```powershell
python scripts\run_no_api_patch_pipeline.py `
  --out-dir outputs\patch_verification_pilot_repro_001
```

验收：

- `candidate_count = 30`
- `verifier_output_count = 90`
- `validation_summary.json` 中 `all_validated = true`
- prompt dry-run records = 60
- 不调用任何模型 API

如果输出数量不一致，停止并检查 dataset builder、candidate schema、oracles 和 prompt dry-run。

随后生成可复现性 manifest，并与原始 pilot 对比：

```powershell
python scripts\write_reproducibility_manifest.py `
  --run-dir outputs\patch_verification_pilot_001 `
  --out outputs\reproducibility\pilot_001_manifest.json
python scripts\write_reproducibility_manifest.py `
  --run-dir outputs\patch_verification_pilot_repro_001 `
  --out outputs\reproducibility\pilot_repro_001_manifest.json `
  --compare-to outputs\reproducibility\pilot_001_manifest.json `
  --compare-out outputs\reproducibility\pilot_compare.json `
  --compare-md outputs\reproducibility\pilot_compare.md
```

可复现性验收：

- `outputs/reproducibility/pilot_compare.json` 中 `matched = true`。
- 对比范围只包括 deterministic no-API 输出。
- raw API responses、运行 workdirs、外部 checkout 和环境相关文件不能作为 deterministic evidence。

当前最新对比结果：

- 原始 run：`outputs/patch_verification_pilot_001`
- 复现 run：`outputs/patch_verification_pilot_repro_001`
- checked deterministic files：7
- matched：true

## 8. 阶段 2：标签边界和数据有效性

检查目标：

- 模型可见 `evidence_packets.jsonl` 不能包含 hidden oracle、expected outcome、candidate type、patch id 或构造标签。
- evaluator-facing `candidates.jsonl` 可以包含标签，但不能传给模型。
- 所有 patch 必须能 apply，并且 oracle label 与 candidate outcome 一致。

执行：

```powershell
python scripts\validate_patch_candidates.py `
  --candidates outputs\patch_verification_pilot_001\candidates.jsonl `
  --out outputs\patch_verification_pilot_001\validation.jsonl `
  --summary-out outputs\patch_verification_pilot_001\validation_summary.json
```

验收：

- 30/30 candidates validated。
- `environment_invalid = 0`，除非有明确记录并停止 API run。
- difficult negatives 比例不能低于当前数据集水平；如果后续修改数据，必须重新计算并记录。

## 9. 阶段 3：模型选择

目的：避免模型选择被质疑为 cherry-picking。

执行者必须先由用户或项目负责人提供真实 provider model id 和选择依据。当前主路径已由用户确认改为 DeepSeek 官方 API，模型为 `deepseek-v4-pro`。AI agent 不能自行凭空替换模型。

决策辅助文档：

```text
docs/experiments/model_selection_shortlist.md
```

该文档给出可选 OpenRouter slug 和论文表述边界，但当前只作为替代路径/历史参考，不能替代用户确认。

仅当切回 OpenRouter 时，确认模型前可运行公开 catalog 可用性检查：

```powershell
python scripts\audit_openrouter_model_catalog.py `
  --model <openrouter-model-slug> `
  --out-json outputs\model_selection\selected_model_catalog_audit.json `
  --out-md outputs\model_selection\selected_model_catalog_audit.md
```

生成 local model selection：

```powershell
python scripts\create_model_selection_local.py `
  --model deepseek-v4-pro `
  --api-provider deepseek_official `
  --provider DeepSeek `
  --selection-source "DeepSeek official API docs and user-confirmed primary model" `
  --selection-source-url https://api-docs.deepseek.com `
  --capability-source "DeepSeek official V4 model family" `
  --capability-band "single documented primary pilot model" `
  --reason "Use DeepSeek V4 Pro through the official DeepSeek API for a within-model llm_only versus evidence_first comparison, controlling base-model capability."
```

如果用户已经一次性给出 provider model id、来源、能力分档和选择理由，也可以先用
`scripts\bootstrap_api_prereqs.py --dry-run --allow-missing-credentials` 检查将要写入的两份 local
config。确认无误后去掉 `--dry-run`，该脚本会生成
`configs\model_selection.local.json` 和 `configs\api_pilot.local.json`，
校验二者 model 一致，并运行 preflight。正式写入模式要求 `.env` 已包含
当前 provider 的 key；DeepSeek official 路径要求 `DEEPSEEK_API_KEY`，否则不会写入 local config。该脚本不会创建 `.env`，
也不会替用户选择模型。

验证：

```powershell
python scripts\validate_model_selection.py `
  --selection configs\model_selection.local.json `
  --out outputs\model_selection\latest.json
```

验收：

- `configs/model_selection.local.json` 存在。
- provider model id 不是 placeholder。
- selection source、capability source、capability band、limitation 均有记录。
- 如果只跑单模型 pilot，论文只能表述为 pilot evidence，不能泛化为所有模型。

## 10. 阶段 4：API local config 与 preflight

生成 local API config：

```powershell
python scripts\create_api_pilot_local_config.py `
  --model deepseek-v4-pro `
  --api-provider deepseek_official `
  --out configs\api_pilot.local.json `
  --smoke-limit 2
```

交叉验证：

```powershell
python scripts\validate_model_selection.py `
  --selection configs\model_selection.local.json `
  --api-config configs\api_pilot.local.json `
  --out outputs\model_selection\api_config_check.json
```

preflight：

```powershell
python scripts\preflight_api_pilot.py `
  --config configs\api_pilot.local.json
```

验收：

- `.env` 中存在当前 provider 的 key；DeepSeek official 路径要求 `DEEPSEEK_API_KEY`。
- `.env` 可选配置 `DEEPSEEK_BASE_URL`；默认使用 `https://api.deepseek.com`。
- OpenRouter 替代路径仍支持 `OPENROUTER_TIMEOUT_SECONDS`、`OPENROUTER_MAX_RETRIES`、
  `OPENROUTER_RETRY_BACKOFF_SECONDS`。
- model selection 与 API config 中 model 完全一致。
- candidate、evidence packet、validation summary 均存在。
- API preflight 返回 ready。

## 11. 阶段 5：guarded workflow check-only

在任何真实 API 调用前，先运行不调用模型的 guarded workflow：

```powershell
python scripts\run_api_pilot_workflow.py `
  --config configs\api_pilot.local.json `
  --check-only `
  --summary-out outputs\api_workflow_check\latest.json
```

验收：

- `model_call_attempted = false`
- model selection validation passed
- preflight passed
- 如果 check-only 失败，不能加 `--execute`

## 12. 阶段 6：真实 API smoke run

只跑 2 个 candidates，两个条件：

- `llm_only`
- `evidence_first`

执行：

```powershell
python scripts\run_api_pilot_workflow.py `
  --config configs\api_pilot.local.json `
  --execute
```

期望输出目录由 config 或 runner 决定，通常为：

```text
outputs/patch_verification_api_pilot_001/
```

验收：

- `reviews.jsonl` 存在。
- `metrics.json` 存在。
- `run_summary.md` 存在。
- `run_error.json` 不存在。
- reviewer record 数量 = 2 candidates x 2 conditions = 4。
- `mock records = 0`。
- invalid output rate 不高到无法解释。
- 至少人工抽查 2 条 raw response，确认 JSON parsing 没有系统性误读。

smoke 后处理：

```powershell
python scripts\postprocess_api_pilot_run.py `
  --run-dir outputs\patch_verification_api_pilot_001 `
  --expected-candidates 2
```

如果 smoke gate 显示 prompt、parser 或输出格式有问题，先修复并重跑 smoke，不允许直接 full run。

## 13. 阶段 7：真实 API full run

前置条件：

- smoke run 通过。
- 不修改 candidates。
- 不修改 prompts。
- 不修改 model。
- 如果修改任一项，回到 dry-run、preflight 和 smoke。

不要覆盖 smoke 输出。推荐不修改 local config，直接用 workflow 覆盖输出目录和 candidate limit：

```text
outputs/patch_verification_api_pilot_002/
```

执行：

```powershell
python scripts\run_api_pilot_workflow.py `
  --config configs\api_pilot.local.json `
  --run-dir outputs\patch_verification_api_pilot_002 `
  --limit 0 `
  --execute
```

验收：

- reviewer record 数量 = 30 candidates x 2 conditions = 60。
- `mock records = 0`。
- `metrics.json` 能计算 false accept、accepted precision、correct-patch recall、escalation、invalid output。
- `run_completeness.json` 中 `passed = true`，`expected_records = 60`，
  `mock_review_count = 0`。
- `run_error.json` 不存在；如果存在，说明该 run 中途失败，不能进入结果分析。
- raw responses 可追踪。
- run metadata 包含 provider model id、api provider、date、prompt version、temperature、max tokens、cost 或 token usage。
- DeepSeek official 路径当前必须使用 `max_tokens=4096`；1200-token smoke
  已出现 reasoning 阶段耗尽导致最终 JSON 为空的问题。

## 14. 阶段 8：full run 后处理

执行：

```powershell
python scripts\postprocess_api_pilot_run.py `
  --run-dir outputs\patch_verification_api_pilot_002 `
  --expected-candidates 30
```

必须生成：

- `api_pilot_report.md`
- `failure_examples.json`
- `failure_examples.md`
- `gate_report.json`
- `gate_report.md`
- `run_completeness.json`
- `run_completeness.md`
- `paper_readiness.json`
- `paper_readiness.md`
- `postprocess_summary.json`

验收：

- gate verdict 不能是 `not_evidence`。
- 如果 verdict 是 `stop_or_redesign` 或 `indeterminate`，不能写正向结论。
- failure examples 必须来自真实 API output，不是 mock output。

## 15. 阶段 9：结果判定规则

必须客观回答四个问题：

1. `evidence_first` 的 false accept rate 是否低于 `llm_only`？
2. `evidence_first` 的 accepted precision 是否高于 `llm_only`？
3. `evidence_first` 的 correct-patch recall 是否没有明显崩溃？
4. 改善是否不是靠 reject/escalate 几乎所有样本换来的？

判定：

- 如果 1 和 2 成立，且 3、4 没有明显问题，可以进入正向 pilot claim。
- 如果 1 或 2 不成立，不能写成方法有效；只能写负结果、条件性结果或回到实验设计。
- 如果 3 明显恶化，主张必须改为“更保守但成本高”，不能说总体更好。
- 如果 4 不成立，说明方法只是过度拒绝，不是有效 verification。

## 16. 阶段 10：failure analysis

从 `failure_examples.md` 和 raw responses 中整理：

- LLM-only false accepts：至少 3 个，若不足则写明不足。
- evidence-first 成功拒绝或升级错误 patch：至少 3 个，若不足则写明不足。
- evidence-first 错拒 correct patch：如存在，至少 3 个。
- invalid outputs：如存在，分析是否由 prompt/schema/parser 导致。

每个案例记录：

- task id
- candidate id
- patch outcome
- reviewer condition
- model decision
- model rationale
- visible evidence
- hidden oracle label
- 为什么这是 false accept、false reject 或合理 escalation

## 17. 阶段 11：论文更新

先运行：

```powershell
python scripts\audit_paper_readiness.py `
  --full-run-dir outputs\patch_verification_api_pilot_002 `
  --out-json outputs\paper_readiness\latest.json `
  --out-md outputs\paper_readiness\latest.md
```

如果 `positive_claim_ready = false`：

- 不能写正向结果。
- 可以更新 methods、dataset、negative/conditional findings、threats。

如果 `positive_claim_ready = true`：

更新：

- `docs/paper/patch_verification_outline.md`
- `docs/paper/patch_verification_draft.md`
- `docs/experiments/patch_verification_pilot_report.md`
- 必要时新增 results summary 文档。

更新 no-API 或 pre-API 输出后，重新生成论文表格：

```powershell
python scripts\write_paper_tables.py `
  --out-md docs\paper\generated_tables.md `
  --out-tex docs\paper\generated_tables.tex
```

重新生成 IEEE LaTeX pre-API 草稿：

```powershell
python scripts\write_ieee_latex_draft.py `
  --tables-tex docs\paper\generated_tables.tex `
  --out docs\paper\ieee_preapi_draft.tex
```

论文必须区分：

- no-API deterministic baselines
- prompt dry-run boundary checks
- mock pipeline checks
- real API model results

## 18. 阶段 12：匿名 artifact

生成 dry-run 或正式 package：

```powershell
python scripts\prepare_anonymous_artifact.py `
  --out artifacts\research95_anonymous_artifact.zip `
  --manifest-out artifacts\research95_anonymous_artifact_manifest.json
python scripts\audit_anonymous_artifact.py `
  --artifact artifacts\research95_anonymous_artifact.zip `
  --out-json artifacts\research95_anonymous_artifact_audit.json `
  --out-md artifacts\research95_anonymous_artifact_audit.md
```

验收：

- 不包含 `.env`。
- 不包含 `configs/*.local.json`。
- 不包含 raw `outputs/`。
- 不包含 `data/`、`tmp/` 或 benchmark checkouts。
- 不包含 API key、绝对用户路径或 provider secrets。
- ZIP audit 必须通过，且 embedded manifest 与文件列表一致。

## 19. 阶段 13：本地质量门

每轮代码、计划、prompt 或实验流程变更后执行：

```powershell
python scripts\audit_goal_completion.py `
  --out-json outputs\goal_completion\latest.json `
  --out-md outputs\goal_completion\latest.md
python scripts\run_local_quality_gate.py `
  --out-json outputs\local_quality_gate\latest.json `
  --out-md outputs\local_quality_gate\latest.md
```

验收：

- compile passed。
- sensitive scan passed。
- credential boundary audit passed。
- bootstrap safety audit passed。
- workflow guard audit passed。
- API failure handling audit passed。
- command template audit passed。
- experiment run records refreshed。
- Git sync packet audit passed。
- artifact dry-run passed。
- `__pycache__` 已清理。
- goal completion audit 必须被刷新；如果真实 API、postprocess、论文 gate、
  artifact、experiment run records、质量门或 Git 证据缺失，`complete`
  必须保持 false。
- API readiness 和 Git readiness 只作为状态报告；如果不 ready，最终汇报必须明确说明。

## 20. 最终交付物

当所有阶段完成后，AI agent 应给出：

1. 实验执行摘要：运行了哪些命令，输出目录在哪里。
2. 数据摘要：candidate 数量、correct/incorrect/partial 分布、validation 结果。
3. 模型摘要：provider model id、api provider、provider、选择依据、运行日期、prompt version。
4. 指标摘要：false accept、accepted precision、correct-patch recall、escalation、invalid output。
5. gate 结论：continue、stop_or_redesign、indeterminate 或 not_evidence。
6. failure analysis 摘要。
7. paper readiness 状态。
8. artifact package 状态。
9. goal completion audit 状态。
10. 明确说明是否可以写正向论文结论。

## 21. 人类需要提供的输入

AI agent 不能自行假定以下内容：

- 当前 provider API key 是否可用；DeepSeek official 路径要求 `DEEPSEEK_API_KEY`。
- 真实 provider model id；当前为 `deepseek-v4-pro`。
- 模型选择来源与能力分档依据。
- 是否允许真实 API 调用。
- 是否要把 `research95` 初始化为 Git 仓库并同步到哪个 GitHub repo。

没有这些输入时，AI agent 只能完成 no-API、dry-run、文档、artifact dry-run 和 local quality gate，不能继续真实模型实验。
