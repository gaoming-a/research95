# 当前计划：AI 生成补丁的可验证审查

最后更新：2026-06-05

## 1. 研究转向

旧方向试图验证 LLM cross-review 或 agent-style context 是否能让代码审查更可靠。已有结果不支持这个强假设。真正可复用的发现是：

> LLM-only review 能提供一些有用信号，但 fixed/reference control 上持续存在 false positives，因此不能直接作为可靠 merge gate。

新方向研究一个更有实际价值的问题：

> AI coding agent 生成的 patch 是否可以被可靠验证，并判断是否应该合并？

## 2. 新核心主张

不要再声称 cross-review 普遍更好。目标主张应改为：

> 与 LLM-only review、majority review 或 agent-context review 相比，evidence-first patch verification 能降低错误 AI-generated patch 被接受的风险。

这个主张必须用 patch-level outcome 证明，不能只靠另一个 LLM opinion。

## 3. 实验单元

每个任务应包含：

- 一个真实 issue 或真实 bug；
- 一个 candidate patch；
- patch 周围源码上下文；
- 可用测试或 executable oracle；
- 可选 issue/test 描述；
- patch 的 ground-truth outcome。

Patch outcome labels：

- `correct`；
- `incorrect`；
- `partial`；
- `overfitted`；
- `test_passing_wrong`；
- `irrelevant_or_noop`；
- `environment_invalid`。

Verifier decision labels：

- `accept`；
- `reject`；
- `escalate`；
- `invalid_output`。

## 4. 主要指标

- False accept rate：错误 patch 被接受的比例。
- False reject rate：正确 patch 被拒绝的比例。
- Accepted precision：被接受 patch 中真正正确的比例。
- Correct-patch recall：正确 patch 被接受的比例。
- Escalation rate：交给 human/tool 进一步验证的比例。
- Cost 和 invalid-output rate。

旧项目中的 candidate-level bug detection metrics 只作为次级指标。

## 5. 可复用资产

保留并改造：

- `scripts/oracles/` 下的 BugsInPy executable oracles；
- paired buggy/fixed metadata 设计；
- claim-level evidence packet 工作流；
- OpenRouter API wrapper 和 JSON parsing utilities；
- false-positive taxonomy 与 tool-gated upper-bound analysis，作为新方向动机。

不要继承：

- generated-code benchmark 作为主贡献；
- 旧 IEEE real-bug draft 作为当前论文；
- prompt-only adjudication 作为 ground truth；
- majority review 作为已成立解决方案。

## 6. 立即执行顺序

已完成：

1. `scripts/build_patch_verification_dataset.py` 已能生成
   `patch_verification_pilot_001`。
2. `scripts/analyze_patch_verification.py` 已能计算 no-API 指标。
3. 当前 no-API pilot 包含 7 个 retained real-bug tasks、30 个
   candidates、90 条 deterministic verifier outputs。
4. 模型可见 evidence packet 使用匿名 candidate id，并已通过标签泄露检查。
5. 在提供外部 retained buggy/fixed checkout root 时，candidate patch text
   已能由真实 unified diff 生成。
6. `scripts/validate_patch_candidates.py` 已能逐个 apply candidate patch，并
   用 retained executable oracles 验证标签；当前 30/30 通过。
7. `docs/paper/patch_verification_draft.md` 已包含 pre-API 方法草稿、
   no-API validation 结果和明确的 API 待填部分。
8. `scripts/run_no_api_patch_pipeline.py` 已能一条命令复现完整本地
   no-API 链路。最新运行到 `outputs/patch_verification_pilot_repro_001`，
   生成 30 个 candidates、90 条 baseline outputs、30/30 executable
   validations、60 条 prompt dry-run records 和 pilot report。

下一步：

1. 若把任务交给新的 AI agent，优先使用
   `docs/plans/ai_agent_experiment_execution_plan_zh.md`。该文件是独立任务书，
   覆盖实验顺序、命令、阶段产物契约、实验记录模板、验收门槛、失败处理、
   论文更新和人工输入项。
2. 每次新一轮继续执行前，先运行
   `python scripts/audit_execution_readiness.py --out-json outputs/readiness_audit/latest.json --out-md outputs/readiness_audit/latest.md`
   检查 no-API、API 和 Git readiness。
3. 运行
   `python scripts/audit_ai_plan_progress.py --out-json outputs/plan_progress/latest.json --out-md outputs/plan_progress/latest.md`
   查看计划阶段 complete、partial、blocked、pending 状态。
4. 运行
   `python scripts/write_human_input_packet.py --out-json outputs/handoff/human_input_packet.json --out-md outputs/handoff/human_input_packet.md`
   生成真实 API 前所需的人工输入清单和安全命令顺序。
5. 运行
   `python scripts/write_git_sync_packet.py --out-json outputs/handoff/git_sync_packet.json --out-md outputs/handoff/git_sync_packet.md`
   记录 Git 状态和初始化/推送前必须由用户确认的 remote 决策。该报告还会输出
   remote 决策记录模板、允许暂存范围、ignore 验证命令、cached diff 检查命令和同步后验收标准；
   它不会执行 `git init`、`git add`、`git commit` 或 `git push`。
   随后运行
   `python scripts/audit_git_sync_packet.py --out-json outputs/git_sync_packet_audit/latest.json --out-md outputs/git_sync_packet_audit/latest.md`
   检查 Git 交接包是否保留人工决策门、禁止 `git add .`、在暂存前检查 ignored local files、
   并在暂存后检查 cached diff。
6. 运行
   `python scripts/write_pre_api_handoff.py --out-json outputs/handoff/pre_api_handoff.json --out-md outputs/handoff/pre_api_handoff.md`
   刷新所有本地 pre-API 交接报告，包括完整目标完成状态和 Git 交接安全审计；
   同时刷新 experiment run-record ledger；该命令不会调用模型 API。
7. 新环境或新 AI 接手时，先运行
   `python scripts/run_no_api_patch_pipeline.py --out-dir outputs/patch_verification_pilot_repro_001`
   验证 no-API pipeline，不调用模型 API。
8. 运行 `scripts/write_reproducibility_manifest.py`，比较
   `outputs/patch_verification_pilot_001` 与
   `outputs/patch_verification_pilot_repro_001` 的 deterministic outputs。
   当前 `outputs/reproducibility/pilot_compare.json` 显示 matched = true。
9. 编写并记录 `llm_only` 与 `evidence_first` 的 API pilot prompts。
10. 当前主执行模型路径已改为 DeepSeek 官方 API：
   `--api-provider deepseek_official --model deepseek-v4-pro`。OpenRouter
   shortlist/catalog 文档仅作为替代路径或历史选择依据保留，不是当前前置条件。
11. 如果未来重新切回 OpenRouter，才使用
   `scripts/audit_openrouter_model_catalog.py` 检查候选 slug 是否仍在
   OpenRouter 公开 catalog 中可见，并在生成 local config 时加
   `--require-openrouter-catalog`。
12. 实现或改造 API runner，确保每条输出记录 provider model id、prompt version、
   date、cost、raw response path 和 invalid-output status。
   状态：已在 `scripts/run_patch_verification_api_pilot.py` 中实现，支持
   DeepSeek official 和 OpenRouter；已完成 DeepSeek official 真实 smoke。
   runner 支持 `--config`、`--dry-run`，真实 run 后会写出 `metrics.json`。
   真实 API 调用必须通过 `scripts/run_api_pilot_workflow.py`；低层 runner
   只用于 dry-run、mock 检查或由 workflow 调用。直接真实调用会被拒绝，
   除非 guarded workflow 传入内部授权参数。
   若真实 API 中途失败，低层 runner 会写入脱敏的 `run_error.json`；
   completeness audit 会把包含该文件的 run 判为不完整，不能作为实验结果。
13. 先用 `--limit 2` 跑 API smoke pilot，再运行当前已验证的 30 个
   candidates。Dry-run 状态：60 个渲染 prompts 已通过 label-leakage check。
   Mock smoke 状态：`--mock-policy patch_surface` 已验证
   `reviews.jsonl -> metrics.json -> run_summary.md` 链路，但这不是实验结果。
14. 任何真实 API 调用前，先把 `configs/api_pilot.example.json` 复制为未追踪
   local config，或用 `scripts/create_api_pilot_local_config.py` 生成；
   同时基于 `configs/model_selection.example.json` 写入
   `configs/model_selection.local.json`，用
   `scripts/validate_model_selection.py` 校验；建议用
   `scripts/create_model_selection_local.py` 生成该文件；填入 provider model id，
   加入 `.env`，并运行 `scripts/preflight_api_pilot.py`。
   当前配置应使用 `DEEPSEEK_API_KEY`、`deepseek-v4-pro`、
   `deepseek_official`。如果 model id、来源、能力区间和选择理由已经由人明确确认，也可以用
   `scripts/bootstrap_api_prereqs.py` 一次性生成两个 ignored local config，
   校验模型一致性并运行 preflight；交给其他 AI agent 前应先用
   `--dry-run --allow-missing-credentials` 检查。正式写入模式要求 `.env`
   已包含当前 provider 的 key；DeepSeek official 路径要求
   `DEEPSEEK_API_KEY`，否则不会写入 local config。
15. 每次 validation 或 dry-run 更新后，用
   `scripts/summarize_patch_verification_pilot.py` 重新生成
   `outputs/patch_verification_pilot_001/pilot_report.md`，并同步生成 tracked
   摘要 `docs/experiments/patch_verification_pilot_report.md`。
16. 真实 API smoke/full run 优先使用 `scripts/run_api_pilot_workflow.py`。
   它会先严格 preflight，并且只有显式传入 `--execute` 才会调用模型 API。
   smoke run 使用 local config 默认的 `smoke_limit=2`；full run 在 smoke 通过后使用
   `--run-dir outputs/patch_verification_api_pilot_002 --limit 0 --execute`，
   避免覆盖 smoke 输出并强制 30 个 candidates 全量运行。
17. 每次 smoke 或完整 API run 后，优先对 run directory 运行
   `scripts/postprocess_api_pilot_run.py`，一次性生成 API report、failure
   examples、gate report、run completeness、paper readiness 和 postprocess summary。
   smoke run 使用 `--expected-candidates 2`；full run 使用
   `--expected-candidates 30`。该 wrapper 已在 mock smoke run 上验证，
   并正确返回 `not_evidence`。
18. 如果需要分步排错，再用
   `scripts/summarize_api_pilot_results.py` 从 `reviews.jsonl` 和
   `metrics.json` 生成 run-specific Markdown 报告。如果使用
   `--mock-policy`，报告只能保留在 ignored `outputs/` 下，不能作为模型证据。
19. 真实 full API run 后，运行 `scripts/extract_api_failure_examples.py`，
   抽取 false accepts、正确 patch 未被接受、evidence-first reject/escalate
   等定性分析样本。mock extraction 只能验证本地抽取链路。
20. full API run 后运行 `scripts/evaluate_api_pilot_gate.py`，生成
   stop/continue gate report。如果 verdict 是 `stop_or_redesign`、
   `indeterminate` 或 `not_evidence`，不能写成正向论文结论。
21. 论文从 pre-API 方法草稿进入正式结果写作前，先运行
   `scripts/audit_paper_readiness.py`。
22. 在声称整个计划完成前，必须运行 `scripts/audit_goal_completion.py`。
   该审计要求真实 API 结果、postprocess 报告、论文 gate readiness、
   artifact safety、本地质量门和 Git 仓库证据全部成立。本地质量门现在包含
   no-API 的 API failure-handling audit 和 experiment run-record ledger 生成。
23. 使用 `scripts/write_paper_tables.py` 重新生成 pre-API Markdown 与
   LaTeX 表格；这些表格只记录数据集、验证、no-API baseline 和可复现性，
   不包含真实模型审查结果。
24. 使用 `scripts/write_ieee_latex_draft.py` 重新生成 IEEEtran pre-API
   LaTeX 草稿；该草稿必须保留真实 API 结果待填边界，不能作为最终投稿版。
25. 使用 `scripts/prepare_anonymous_artifact.py` 生成匿名 supplemental
   package。当前 package 只包含源码、文档、示例和配置模板；排除 outputs、
   data、credentials 和本地 checkouts。
26. 分析 evidence-first 是否降低 false accepts，同时不通过全部 reject 或
   escalate 换取表面提升。
27. 每次变更同步更新 README、索引、计划和实验记录。

## 6.1 2026-06-05 DeepSeek API smoke 执行计划

本轮只执行真实 API smoke，不直接进入 full run。执行前置条件：

- `configs/model_selection.local.json` 与 `configs/api_pilot.local.json` 已指向
  `api_provider=deepseek_official`、`model=deepseek-v4-pro`。
- `.env` 中存在 `DEEPSEEK_API_KEY`，但 key 不得写入任何 tracked 文件或报告。
- `python scripts\preflight_api_pilot.py --config configs\api_pilot.local.json`
  必须通过。
- `outputs/patch_verification_api_pilot_001/reviews.jsonl` 不存在，避免覆盖已有真实 API 结果。

执行命令：

```powershell
python scripts\run_api_pilot_workflow.py `
  --config configs\api_pilot.local.json `
  --execute `
  --summary-out outputs\api_workflow_smoke\latest.json
```

smoke 验收条件：

- workflow summary 中 `mode=executed`，`model_call_attempted=true`。
- `outputs/patch_verification_api_pilot_001/run_completeness.json` 通过，且
  expected candidates 为 2、review records 为 4、mock review count 为 0。
- postprocess 生成 `api_pilot_report.md`、`failure_examples.json`、
  `gate_report.json`、`paper_readiness.json` 和 `postprocess_summary.json`。
- 如果出现 `run_error.json`、API 认证/模型不存在/解析失败/records 不足，
  该 smoke 只能作为失败诊断，不能进入 full run。

smoke 后决策规则：

- 如果 API 调用链路、JSON 解析、postprocess 和 completeness 全部通过，
  可以继续 full run，但仍必须在 full run 前刷新计划与 handoff。
- 如果 smoke 通过但 gate 为 `not_evidence`，这不阻止 full run；smoke 样本太小，
  只用于验证执行链路。
- 如果 smoke 的模型输出大量 invalid 或 schema 不稳定，先修 prompt/schema，
  不继续 full run。

第一次 smoke 结果：

- 真实调用成功，生成 4 条非 mock review，`run_completeness.json` 通过。
- 但 candidate_0001 两个条件均为 `invalid_output`，原因为模型 response
  `finish_reason=length` 且最终 `content` 为空；completion token 全部消耗在
  `reasoning_content`。
- gate 为 `indeterminate`，不能进入 full run。

修复动作：

- 将 API pilot `max_tokens` 从 1200 提高到 4096。
- 修复 `scripts/run_patch_verification_api_pilot.py` 的配置加载逻辑，确保
  config 中的 `temperature` 和 `max_tokens` 能覆盖 runner 默认值。
- 第二次 schema-stability smoke 必须写入新目录
  `outputs/patch_verification_api_pilot_001_tokens4096`，不能覆盖第一次 smoke。
- 第二次 smoke 已完成：4 条非 mock review，`run_completeness.json` 通过，
  invalid output rate 为 0。
- 第二次 smoke 的 gate 仍为 `indeterminate`，原因是样本太小且 evidence-first
  对 correct reference 选择 escalate，不能作为论文正向证据。
- 结论：执行链路可以继续到 full run；研究结论不能继续写，必须等待
  30-candidate full run 的 `gate_report.json` 和 failure analysis。

full run 前计划修订：

- full run 必须继续使用 `max_tokens=4096`。
- Stage 6 smoke 验收不再只看 review 数量，还必须看 completeness 通过、
  mock count 为 0、invalid output rate 不超过 0.2。
- `outputs/patch_verification_api_pilot_001` 保留为 1200-token 失败诊断；
  有效 smoke 以 `outputs/patch_verification_api_pilot_001_tokens4096` 为准。
- full run 命令仍使用独立目录：

```powershell
python scripts\run_api_pilot_workflow.py `
  --config configs\api_pilot.local.json `
  --run-dir outputs\patch_verification_api_pilot_002 `
  --limit 0 `
  --execute `
  --summary-out outputs\api_workflow_full\latest.json
```

## 6.2 2026-06-05 DeepSeek API full run 执行计划

本轮执行 30-candidate full run。执行前检查结果：

- Git 工作区干净，remote 为 `https://github.com/gaoming-a/research95.git`。
- `configs/api_pilot.local.json` 使用 `api_provider=deepseek_official`、
  `model=deepseek-v4-pro`、`max_tokens=4096`。
- 有效 smoke 目录为 `outputs/patch_verification_api_pilot_001_tokens4096`：
  4 条非 mock review，`run_completeness.json` 通过，invalid output rate 为 0。
- `outputs/patch_verification_api_pilot_002` 不存在，full run 不会覆盖已有结果。
- `python scripts\preflight_api_pilot.py --config configs\api_pilot.local.json`
  已通过。

执行命令：

```powershell
python scripts\run_api_pilot_workflow.py `
  --config configs\api_pilot.local.json `
  --run-dir outputs\patch_verification_api_pilot_002 `
  --limit 0 `
  --execute `
  --summary-out outputs\api_workflow_full\latest.json
```

full run 验收条件：

- `reviews.jsonl` 为 60 条，两个条件各 30 条。
- `run_completeness.json` 通过，`mock_review_count=0`，无 `run_error.json`。
- postprocess 生成 `api_pilot_report.md`、`failure_examples.json/md`、
  `gate_report.json/md`、`paper_readiness.json/md` 和 `postprocess_summary.json`。
- 只有当 full-run `gate_report.json` verdict 为 `continue` 且 failure analysis
  支持解释时，才允许写正向论文结论。
- 如果 verdict 为 `indeterminate`、`stop_or_redesign` 或 `not_evidence`，
  只能写负结果/方法边界，不能声称 evidence-first 已被支持。

full run 执行结果：

- `outputs/patch_verification_api_pilot_002` 已生成。
- 60 条非 mock review，两个条件各 30 条。
- `run_completeness.json` 通过，raw responses 60/60 存在且 hash 匹配，
  无 `run_error.json`。
- `gate_report.json` verdict 为 `stop_or_redesign`。
- `paper_readiness.json` 显示 `negative_or_methods_draft_ready=true`，
  `positive_claim_ready=false`。

核心指标：

| condition | false accept rate | accepted precision | correct recall | escalation rate | invalid output rate |
|---|---:|---:|---:|---:|---:|
| `llm_only` | 0.0909 | 0.7143 | 1.0000 | 0.0667 | 0.1000 |
| `evidence_first` | 0.0000 | 1.0000 | 0.7143 | 0.1333 | 0.0333 |

客观结论：

- evidence-first 降低 false accepts，并提高 accepted precision。
- 但 correct-patch recall 下降 0.2857，超过预设 `max_recall_drop=0.25`。
- 当前不能写正向论文结论；只能写 mixed/negative result，并说明安全性提升伴随
  过度拒绝/升级正确 patch 的代价。
- 下一步应人工检查 `failure_examples.md`，判断是否要重新设计 evidence-first
  prompt/evidence packet，或将论文主旨改为“LLM merge gate 的安全/效用权衡”。

## 7. 继续/止损门槛

只有满足以下至少一项时继续：

- evidence-first verification 相比 LLM-only review 降低 false accepts；
- 数据集中能构造现实的 incorrect/partial/test-passing-wrong patches；
- claim-level evidence 能解释 LLM-only 决策为什么失败。

如果新数据集无法产生真实感的错误 patch，或者 verifier 只是通过拒绝几乎所有 patch 来降低 false accepts，就应停止。
