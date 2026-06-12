# 当前计划：AI 生成补丁的可验证审查

最后更新：2026-06-08

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

历史执行清单和当前操作说明：

当前后续目标以 `docs/plans/final_paper_roadmap_zh.md` 为准。以下条目保留
早期 API pilot、质量门、artifact 和论文生成命令的执行上下文；其中已完成的
prompt-only、tool-augmented smoke/full run 不应被重新当作当前下一步。

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
23. 使用 `scripts/write_paper_tables.py` 重新生成 Markdown 与 LaTeX 表格。
24. 使用 `scripts/write_ieee_latex_draft.py` 重新生成当前 IEEEtran 投稿草稿
   `docs/paper/ieee_submission_draft.tex`；旧
   `docs/paper/ieee_preapi_draft.tex` 只保留为历史 pre-API 草稿。
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

## 6.3 2026-06-05 full run 失败分析后的修订计划

已完成：

- 已检查 `outputs/patch_verification_api_pilot_002/failure_examples.json`、
  `reviews.jsonl` 和关键 raw responses。
- 已新增
  `docs/experiments/deepseek_full_run_failure_analysis.md`，记录定性失败模式。

失败分析结论：

- `llm_only` 的 2 个 false accepts 都来自 `bugsinpy_httpie_1` 的 partial
  fixes：`candidate_0005` 和 `candidate_0006`。模型根据 patch 表面意图推断
  其正确，因此接受了缺失必要变更的 partial patch。
- `evidence_first` 未接受 2 个 correct reference patches：
  `candidate_0001` 被 escalate，`candidate_0023` 被 reject。
- 当前 evidence packet 对 evidence-first 来说证据不足：它主要包含 patch、
  task summary 和测试名，没有测试体、失败行为、oracle 输出或 claim-level trace。
- 因此当前结果只能支持“更保守、false accept 更少，但 recall 损失过大”的
  safety/utility tradeoff，不能支持“evidence-first 更好”的正向主张。

当时下一步最短路径：

1. 不继续用 `patch_verify_evidence_first_v1` 直接扩量。
2. 先设计一个小范围新条件，暂定
   `evidence_with_oracle_summary_v1` 或 `tool_augmented_evidence_v1`。
3. 新条件必须明确是否允许模型看到工具/测试执行摘要。如果允许，这就是
   tool-augmented verifier，不再是 prompt-only verifier。
4. 只在失败样本上做 redesign smoke：
   `candidate_0001`、`candidate_0005`、`candidate_0006`、
   `candidate_0023`、`candidate_0020`。
5. 继续门槛：新条件必须保持 false accept 不上升，并把两个 correct reference
   patches 至少从 reject/escalate 改善到 accept，或能给出可验证的升级理由。
6. 如果失败样本 smoke 仍不能修复 recall 损失，则停止正向 evidence-first 论文，
   转为负结果/方法论文：prompt-only merge gate 的局限与 executable evidence 的必要性。

本轮执行计划：

- 新条件命名为 `tool_augmented_evidence`，prompt version 为
  `patch_verify_tool_augmented_evidence_v1`。
- 该条件允许模型看到 patch apply 结果和 retained oracle 执行摘要；因此它不是
  prompt-only verifier，论文中必须单独报告。
- 输入构造脚本只选择 5 个 failure-case candidates：
  `candidate_0001`、`candidate_0005`、`candidate_0006`、
  `candidate_0020`、`candidate_0023`。
- 输出目录使用 `outputs/patch_verification_redesign_smoke_001`，不得覆盖
  `outputs/patch_verification_api_pilot_002`。
- 本轮 smoke 只运行新条件，不重新运行 `llm_only` 或旧 `evidence_first`。
- 验收指标：
  - 5 条真实非 mock review；
  - invalid output rate 为 0；
  - `candidate_0001` 和 `candidate_0023` 应被 accept，除非模型给出可由工具证据支持的升级理由；
  - `candidate_0005`、`candidate_0006`、`candidate_0020` 不应被 accept；
  - 如果这些条件不满足，不继续扩量，仍保持 negative/methods 方向。

执行链路问题与修复：

- 已发现 bug：`scripts/run_patch_verification_api_pilot.py` 的 argparse
  默认 `conditions=["llm_only", "evidence_first"]` 导致 config 中的
  `conditions=["tool_augmented_evidence"]` 无法覆盖默认值。
- 该问题会让 redesign dry-run 错跑旧两个条件，生成 10 条 prompt manifest；
  因此在修复前禁止真实 API 调用。
- 修复方式：将 parser 默认 conditions 改为 `None`，在 config 应用之后再用
  `apply_defaults()` 填充默认旧条件。这样显式 CLI 条件和 config 条件都能正确生效。
- 修复验收：重跑 redesign dry-run，必须只生成 5 条
  `tool_augmented_evidence` prompt records。

dry-run 修复验证结果：

- `outputs/patch_verification_redesign_smoke_001/dry_run/prompt_manifest.jsonl`
  已重新生成。
- prompt records = 5。
- condition counts = `{"tool_augmented_evidence": 5}`。
- prompt version counts =
  `{"patch_verify_tool_augmented_evidence_v1": 5}`。
- 实际渲染 prompt 边界扫描通过：未命中 evaluator labels、旧 evaluator patch id
  片段或本地路径。

当时下一步执行命令：

```powershell
python scripts\run_redesign_smoke_workflow.py `
  --config outputs\patch_verification_redesign_smoke_001\api_config.local.json `
  --execute `
  --summary-out outputs\redesign_smoke_workflow\executed.json
```

该命令只允许生成 5 条 `tool_augmented_evidence` 真实 review。若出现
`invalid_output`、错误 condition、缺失 raw response 或 smoke gate 未通过，
必须停止扩量并记录为 redesign smoke failure。

真实 redesign smoke 结果：

- 输出目录：`outputs/patch_verification_redesign_smoke_001`。
- 真实非 mock review records = 5。
- `run_completeness.json` 通过。
- invalid output count = 0。
- decisions：
  - `candidate_0001`: `accept`；
  - `candidate_0005`: `reject`；
  - `candidate_0006`: `reject`；
  - `candidate_0020`: `reject`；
  - `candidate_0023`: `accept`。
- `redesign_smoke_gate.json` passed = true。
- tracked 结果文档：
  `docs/experiments/tool_augmented_redesign_smoke_result.md`。

客观解释：

- 该结果支持一个窄诊断：旧 evidence-first 的失败很可能与证据不足有关；
  加入工具执行摘要后，已知失败样本上的 accept/reject 恢复到预期。
- 该结果不支持把原 prompt-only evidence-first 写成成功，也不能替代
  30-candidate full run。

当时下一步（已在后续章节完成）：

1. 构造 30-candidate 全量 `tool_augmented_evidence` input set。
2. 运行独立 full run，不覆盖旧 `patch_verification_api_pilot_002`。
3. 比较三组：旧 `llm_only`、旧 prompt-only `evidence_first`、新
   tool-augmented verifier。
4. 论文 claim 必须写成条件性工具增强收益，而不是 prompt-only 方法普遍更好。

## 6.4 2026-06-05 tool-augmented full run 前置修订

用户已确认路线：先把论文主张和实验设计改清楚，再跑 30-candidate
`tool_augmented_evidence` full run。

本轮已修订：

- `docs/paper/research_definition.md`：主假设改为 LLM-only 不可靠、
  prompt-only evidence-first 存在证据贫乏导致的 recall 损失、
  tool-augmented verifier 可能改善 safety/recall tradeoff。
- `docs/paper/patch_verification_outline.md`：贡献改为 prompt-only 负结果
  加 tool-augmented 修复路径。
- `docs/paper/patch_verification_draft.md`：加入 tool-augmented redesign smoke
  和后续 30-candidate full run 边界。
- `docs/experiments/evidence_first_protocol.md`：区分 prompt-only
  evidence-first 与 tool-augmented evidence verification。
- `docs/experiments/patch_verification_plan.md`：新增 revised
  tool-augmented stage。

执行边界：

- 30-candidate full run 必须写入新目录
  `outputs/patch_verification_tool_augmented_full_001`。
- 只运行 `tool_augmented_evidence`，不覆盖旧 full run。
- 结果只能作为 tool-assisted verifier 证据，不能说 prompt-only evidence-first
  成功。
- 如果 full run 没有通过 completeness、出现高 invalid output、或工具增强仍
  false accept/false reject 明显，则停止扩量并更新论文为负/条件性结果。

full run 前置验证：

- 已生成 `outputs/patch_verification_tool_augmented_full_001/inputs`。
- input candidates = 30，evidence packets = 30。
- validation summary：`all_validated=true`，oracle all-pass 7，oracle failed 23。
- check-only preflight 通过，且 `model_call_attempted=false`。
- dry-run prompt records = 30。
- condition counts = `{"tool_augmented_evidence": 30}`。
- prompt version counts =
  `{"patch_verify_tool_augmented_evidence_v1": 30}`。
- 实际渲染 prompt 边界扫描通过：未命中 evaluator labels、旧 evaluator patch id
  片段或本地路径。
- `outputs/patch_verification_tool_augmented_full_001/reviews.jsonl` 不存在，
  真实 run 不会覆盖旧结果。

执行命令：

```powershell
python scripts\run_redesign_smoke_workflow.py `
  --config outputs\patch_verification_tool_augmented_full_001\api_config.local.json `
  --gate-mode full `
  --execute `
  --summary-out outputs\tool_augmented_full_workflow\executed.json
```

真实 tool-augmented full run 结果：

- 输出目录：`outputs/patch_verification_tool_augmented_full_001`。
- 真实非 mock review records = 30。
- `run_completeness.json` 通过。
- `tool_augmented_full_gate.json` passed = true。
- invalid output count = 0。
- false accept rate = 0.0。
- correct-patch recall = 1.0。
- accepted precision = 1.0。
- false reject rate = 0.0。
- escalation rate = 0.0。
- tracked 结果文档：
  `docs/experiments/tool_augmented_full_run_result.md`。

三组结果解释：

- `llm_only`：召回高，但会接受 partial fixes。
- prompt-only `evidence_first`：false accept 降低，但 recall 损失超过 gate。
- `tool_augmented_evidence`：在该 30-candidate pilot 上同时保持 false accept
  为 0 和 correct recall 为 1。

论文边界：

- 这是 tool-assisted verification 的条件性收益，不是 prompt-only
  evidence-first 的成功。
- 结果依赖 retained oracle/tool execution summaries；写论文时必须讨论这些摘要
  是真实工程证据、工具工作流证据，还是较强的上界证据。

## 6.5 2026-06-05 审计口径修复与收敛状态

问题：

- 旧 `audit_paper_readiness.py`、`audit_ai_plan_progress.py` 和
  `audit_goal_completion.py` 只认识 prompt-only 60-record full run gate。
- 在新路线下，这会继续把 `stop_or_redesign` 报成未完成，或者诱导后续执行者
  把 tool-augmented 结果错误写成 prompt-only 成功。

已修复：

- `audit_paper_readiness.py` 保留
  `prompt_only_positive_claim_ready=false`，并新增
  `tool_augmented_claim_ready=true`。
- `audit_ai_plan_progress.py` 将 prompt-only `stop_or_redesign` 解释为已完成
  的负结果/重设计分流，并要求 tool-augmented full gate 通过。
- `audit_goal_completion.py` 同时要求：
  - prompt-only 正向 claim 保持为负；
  - 30-record tool-augmented full run 完整；
  - `tool_augmented_full_gate.json` 支持条件性 tool-assisted claim。
- `run_local_quality_gate.py` 摘要同时显示 prompt-only 与 tool-augmented
  readiness，避免单一“positive claim ready”误导。
- 匿名 artifact 打包说明和审计规则已加入 tool-augmented full run 命令与
  `tool_augmented_full_gate.json` 要求。

验证结果：

- `outputs/paper_readiness/latest.json`：
  - prompt-only positive claim ready = false；
  - tool-augmented claim ready = true；
  - tool-augmented blockers = none。
- `outputs/plan_progress/latest.json`：stage counts = `{"complete": 14}`。
- `outputs/goal_completion/latest.json`：complete = true。
- `outputs/local_quality_gate/latest.json`：passed = true。
- `artifacts/research95_anonymous_artifact_audit.json`：safe = true。

当前可写结论：

- 旧 prompt-only evidence-first full run 不支持正向 claim。
- 新的正向 claim 只限于：在当前 30-candidate pilot 中，带工具执行摘要的
  verifier 能在保留 recall 的同时消除观察到的 false accepts。
- 任何后续论文扩写必须继续保持该边界。

## 6.6 2026-06-05 IEEE 投稿草稿推进

本轮目标：

- 不新增 API 实验。
- 不改变上一轮审计结论。
- 将已经通过审计的三条件结果写入可重复生成的 IEEE LaTeX 投稿草稿。

边界：

- 旧 `docs/paper/ieee_preapi_draft.tex` 保留为历史 pre-API 草稿。
- 新投稿草稿输出到 `docs/paper/ieee_submission_draft.tex`。
- LaTeX 结果表必须来自已审计的指标值，而不是临时手写到最终文件。
- 论文表述必须继续区分：
  - prompt-only `evidence_first`：负/混合结果；
  - `tool_augmented_evidence`：条件性 tool-assisted verifier 结果。

验收条件：

- `scripts/write_ieee_latex_draft.py` 可重复生成投稿草稿。
- `docs/paper/ieee_submission_draft.tex` 存在，并包含 API pilot result、
  tool-augmented full run、threats、conclusion。
- `docs/INDEX.md`、README、经验文档和匿名 artifact 规则同步更新。
- 本地质量门通过后提交并同步 GitHub。

执行结果：

- 已更新 `scripts/write_ieee_latex_draft.py`，默认输出
  `docs/paper/ieee_submission_draft.tex`。
- 新草稿包含：
  - no-API baseline；
  - prompt-only `llm_only` vs `evidence_first` 真实 API mixed/negative result；
  - `tool_augmented_evidence` full-run 条件性正结果；
  - reproducibility、model-selection boundary、threats、conclusion。
- 结果表从以下审计证据读取：
  - `outputs/patch_verification_api_pilot_002/metrics.json`；
  - `outputs/patch_verification_tool_augmented_full_001/tool_augmented_full_gate.json`。
- 发现并修复一个生成脚本 bug：prompt-only metrics group key 实际为
  `evidence_first::evidence_first__deepseek-v4-pro`，不能按裸 key 读取。
- `pdflatex` 两遍编译通过，输出 4 页 PDF 到 ignored
  `outputs/latex_build/ieee_submission_draft.pdf`。
- `latexmk` 未使用：本机 MiKTeX 缺少 Perl 脚本引擎。

## 6.7 2026-06-06 论文配图生成

本轮目标：

- 为当前实验和 IEEE 投稿草稿生成多张 CCF-A 风格的论文配图。
- 只可视化已有审计证据，不新增 API 实验，不改变论文 claim。
- 图必须可复现生成，优先使用矢量 PDF/SVG，而不是不可复现的 AI 位图。

计划图集：

1. 整体 workflow/framework 图：从 candidate patch 到 prompt-only review、
   tool-augmented verification、accept/reject/escalate gate。
2. Evidence visibility 图：对比 LLM-only、prompt-only evidence-first、
   tool-augmented evidence 三种条件可见的信息边界。
3. Dataset composition 图：项目分布、candidate type 分布、oracle label
   validation 摘要。
4. Safety/recall tradeoff 结果图：false accept、accepted precision、
   correct recall、invalid output 等核心指标。
5. Finding boundary 图：prompt-only 负结果与 tool-assisted 条件性正结果的
   论文主张边界。

验收条件：

- 新增脚本 `scripts/generate_paper_figures.py`。
- 图输出到 `docs/figures/`，至少包含 SVG 与 PDF。
- `docs/paper/ieee_submission_draft.tex` 引用核心图。
- `docs/INDEX.md`、README、经验文档和匿名 artifact 规则同步更新。
- `pdflatex` 编译通过，本地质量门通过，提交并同步 GitHub。

执行结果：

- 已新增 `scripts/generate_paper_figures.py`。
- 已生成 5 张图，每张包含 PDF、SVG、PNG：
  - `fig1_framework`；
  - `fig2_evidence_visibility`；
  - `fig3_dataset_composition`；
  - `fig4_result_tradeoff`；
  - `fig5_claim_boundary`。
- 已新增 `docs/figures/README.md` 和 `docs/figures/figure_manifest.json`。
- 初次视觉 QA 发现 `fig1_framework` 有文字重叠，已修复后重新生成。
- `docs/paper/ieee_submission_draft.tex` 已引入 `graphicx` 并引用 5 张 PDF 图。
- `pdflatex` 两遍编译通过，输出 5 页 PDF 到 ignored
  `outputs/latex_build/ieee_submission_draft.pdf`。

## 6.8 2026-06-06 imagegen 位图候选图

本轮目标：

- 按用户要求使用 `$imagegen` 重新生成更适合论文/汇报视觉表达的配图候选。
- 只生成视觉候选，不改变实验结论，不新增 API 实验。
- 将 prompt、输出路径、用途边界写入仓库，避免后续执行把位图当成精确实验图。

执行结果：

- 已生成并纳入 `docs/figures/imagegen/`：
  - `imagegen_framework.png`；
  - `imagegen_evidence_boundary.png`；
  - `imagegen_tradeoff.png`；
  - `imagegen_claim_boundary.png`。
- 已新增 `docs/figures/imagegen/prompts.md`，记录 4 张图的完整生成
  prompt。
- 已新增 `docs/figures/imagegen/README.md`，明确这些图只适合 graphical
  abstract、汇报和视觉草稿。

边界：

- 这些 PNG 是不可完全复现的 AI 位图候选，不用于支撑精确实验数值。
- IEEE 正文中的数值和方法图仍以 `scripts/generate_paper_figures.py`
  生成的 PDF/SVG 为准。
- 若投稿系统需要 graphical abstract，可从 `docs/figures/imagegen/`
  选择候选并人工检查文字拼写、分辨率和版面。

## 6.9 2026-06-08 最终论文长期路线保存

本轮目标：

- 将用户提供并经评估后的 90+ 最终论文路线保存为后续计划。
- 不覆盖当前执行计划，不启动扩数据，不调用 API。
- 明确该路线是长期投稿/硕士论文增强路线，而不是当前 pilot 的最低完成要求。

执行结果：

- 新增 `docs/plans/final_paper_roadmap_zh.md`。
- 路线核心从“三组条件比较”升级为：
  evidence visibility 如何影响 LLM candidate patch verification 的 false
  accept、correct recall、escalation 和 merge-gate 决策。
- 文档包含：
  - 5 个 RQ；
  - BugsInPy/SWE-bench/构造型 patch 的数据扩展路线；
  - visible evidence 与 hidden evaluator 分离规则；
  - tool-only、accept-all、reject-all、test-only 等 baseline；
  - 指标体系、failure taxonomy、generated tests、多模型和 artifact 目标；
  - 双轨策略：当前 pilot/中期保底路线 + 长期最终论文路线。

边界：

- 当前不直接执行 80 bugs / 240 patches 的完整路线。
- 下一步仍应优先补中期报告材料、tool-only baseline 和 qualitative cases。
- 只有当前 pipeline 稳定后，才进入 15-20 bugs 小扩展，再考虑 30-50 bugs
  硕士论文稳健版。

## 6.10 2026-06-08 六步前置执行计划

本轮目标：

- 执行长期路线进入中期增强版前的六个前置步骤。
- 不调用真实模型 API。
- 不把扩展 task screening 误写成已经完成 patch candidate validation。

六步范围：

1. 补充统一 schema 文档，覆盖 TaskRecord、PatchRecord、EvidencePacket、
   ValidationOutcome 和 VerifierDecision。
2. 实现 tool-only baseline 脚本。
3. 在当前 30-candidate pilot 上运行 tool-only baseline 并生成指标。
4. 生成 qualitative case report，覆盖 LLM-only false accept、
   evidence-first false reject/escalate、tool-only 和 tool-augmented 对照。
5. 写 visible evidence / hidden evaluator leakage policy。
6. 对 retained BugsInPy workspace 做 15-20 bugs 扩展筛选，生成可跟进的
   candidate task registry；若缺少新 task 专用 oracle，只记录为 expansion
   screening，不声明为已完成扩展实验。

验收条件：

- 新脚本可 `--help` 或实际运行通过。
- 当前 30-candidate tool-only metrics 可由脚本复现。
- qualitative report 不包含本地绝对路径或 API key。
- leakage policy 明确 realistic setting 与 oracle-upper-bound setting。
- expansion registry 至少列出 15 个候选 BugsInPy task，且标明后续还需
  oracle migration/validation。
- 更新 README、docs/INDEX、经验文档后跑本地质量门并同步 GitHub。

执行结果：

- 已新增 `docs/experiments/patch_evidence_bench_schema.md`，覆盖
  TaskRecord、PatchRecord、EvidencePacket、ValidationOutcome 和
  VerifierDecision。
- 已新增 `scripts/run_tool_only_baseline.py`。
- 已在当前 30-candidate pilot 上运行 tool-only：
  - `tool_only_apply_only`：false accept rate 0.0，correct recall 0.0，
    escalation rate 1.0；
  - `tool_only_validation_summary`：false accept rate 0.0，correct recall
    1.0，accepted precision 1.0。
- 已新增 `docs/experiments/tool_only_baseline_result.md`，明确
  validation-summary 条件是当前 pilot 的 tool-summary/oracle-style baseline，
  不是最终 hidden-evaluator-free realistic baseline。
- 已新增 `scripts/build_qualitative_case_report.py` 和
  `docs/experiments/qualitative_case_report.md`，包含 4 个诊断案例。
- 已新增 `docs/experiments/leakage_policy.md`。
- 已新增 `scripts/screen_bugsinpy_expansion.py` 和
  `docs/experiments/bugsinpy_expansion_screening.md`；筛选 retained BugsInPy
  workspace 中 22 个 eligible tasks，并选择 15 个进入 expansion registry。

边界：

- 本轮没有调用真实模型 API。
- 第 6 步完成的是 15-task expansion screening，不是已经完成 15-task
  expanded candidate dataset。
- 新 registry 里的 task 必须先补 task-specific oracle、candidate
  materialization 和 `validate_patch_candidates.py` 验证，才能进入主实验。

## 6.11 2026-06-08 后续目标指定

本轮目标：

- 按用户要求，将 `docs/plans/final_paper_roadmap_zh.md` 指定为本项目后续目标。
- 不启动新的实验，不调用 API，不改变当前已有结果解释。

执行结果：

- `docs/plans/final_paper_roadmap_zh.md` 被标记为后续目标的规范入口。
- 后续研究主线明确为：evidence visibility 如何影响 LLM candidate patch
  verification 的 false accept、correct recall、escalation 和 merge-gate
  决策，以及 LLM 相比 tool-only baseline 的真实贡献。
- `docs/plans/current_plan_zh.md` 继续作为每轮执行记录；任何从最终路线拆出的
  具体任务，仍必须在执行前写入本文件的轮次计划。

边界：

- 指定后续目标不等于已经开始执行完整 90+ 路线。
- 下一步仍应从 `final_paper_roadmap_zh.md` 的 Stage A/B 开始，即继续完善当前
  pilot、oracle/schema/pipeline 和 15-task expansion registry。

## 6.12 2026-06-08 文档清理计划

本轮目标：

- 清理 README、docs/INDEX 和旧实验计划中的过期“下一步”描述。
- 继续指定 `docs/plans/final_paper_roadmap_zh.md` 为最终论文路线和后续目标。
- 不删除历史实验结果，不改变已有实验解释，不启动新实验，不调用模型 API。

计划：

1. 将 README 的执行入口从旧的 API/pre-API 命令清单改为当前目标入口：
   `final_paper_roadmap_zh.md` 是最终路线，`current_plan_zh.md` 是每轮执行日志。
2. 在 docs/INDEX 中明确计划文件层级，避免多个计划文件同时被理解为当前目标。
3. 将已完成的 prompt-only、tool-augmented smoke/full run 相关旧“下一步”改为历史状态。
4. 补齐 literature 文档索引。
5. 运行本地质量门，检查文档清理没有破坏索引和安全边界。
6. 提交并推送到 GitHub。

验收条件：

- 所有“当前下一步”都指向 `final_paper_roadmap_zh.md` 的 Stage A/B。
- `ieee_submission_draft.tex` 是当前 IEEE 投稿草稿；`ieee_preapi_draft.tex` 只保留为历史草稿。
- 旧执行计划保留为 historical/reference，不再作为最终目标。
- 本轮文档清理同步 README、docs/INDEX、计划文档和经验文档。

执行结果：

- README 已改为 `Current Execution Target`，明确最终路线是
  `docs/plans/final_paper_roadmap_zh.md`。
- docs/INDEX 已拆分 Active Plan 与 Historical Plan References，并补齐
  literature 文档索引。
- `pilot_dataset_construction.md` 和 `patch_verification_plan.md` 中已完成的
  API/tool-augmented “下一步”已改为历史状态。
- `current_plan.md` 与本文件已更新日期和当前目标说明。
- `docs/experience/engineering_notes.md` 已记录本次文档清理经验。

## 6.13 2026-06-08 Stage A/B 首批 httpie 扩展计划

本轮目标：

- 按用户确认，从 expansion screening 中选择 5 个 `httpie` 任务作为首批
  Stage A/B 小闭环。
- 完成 task-specific oracle/candidate/evidence pipeline 的最小闭环验证。
- 不直接启动 80 bugs / 240 patches 完整路线，不调用真实模型 API。

首批任务：

1. `bugsinpy_httpie_1`
2. `bugsinpy_httpie_2`
3. `bugsinpy_httpie_3`
4. `bugsinpy_httpie_4`
5. `bugsinpy_httpie_5`

计划：

1. 检查现有 `scripts/oracles/`、candidate builder、validation 和 leakage
   check 的可复用接口。
2. 若现有 oracle 已覆盖某些 httpie task，优先复用；若缺失，新增最小
   task-specific oracle wrapper。
3. 为首批任务生成 expanded candidate records，至少包含 reference/no-op/
   irrelevant/partial 或其他可验证 difficult negative。
4. 运行 candidate validation，确认每个 candidate 的 evaluator label 可由
   apply + oracle/tool evidence 复核。
5. 生成或更新 visible evidence / hidden evaluator 分离记录，确保 model-visible
   packet 不包含 reference provenance、hidden evaluator result 或最终标签。
6. 更新 README、docs/INDEX、实验记录和经验文档，运行本地质量门并同步 GitHub。

需要停下确认的情况：

- 某个 httpie task 缺少 retained checkout、reference diff 或可执行测试，且无法
  用现有数据客观修复。
- 需要改变首批任务范围、candidate 类型比例、是否允许人工构造 patch、是否调用
  真实模型 API。
- validation pipeline 只能通过泄漏 hidden evaluator summary 才能工作。

执行结果：

- 已为 `scripts/build_patch_verification_dataset.py` 增加 `--task-id` 和
  `--run-id`，默认旧 pilot 行为保持不变。
- 已生成独立 Stage A/B 输出目录 `outputs/httpie_stage_ab_001`。
- 数据集包含 5 个 `httpie` tasks、22 个 candidates：
  - `correct_reference`: 5；
  - `buggy_noop`: 5；
  - `irrelevant_patch`: 5；
  - `partial_fix`: 7。
- difficult negative ratio = 0.3182，满足当前最小 readiness 阈值。
- `validate_patch_candidates.py` 验证 22/22 candidates 通过；所有 patch
  apply 成功，oracle 全部运行，5 个 correct reference 通过 oracle，17 个负例按
  预期未通过 oracle。
- 已运行 no-API baseline metrics：
  - `accept_all` false accept rate = 1.0，accepted precision = 0.2273；
  - `reject_all` false accept rate = 0.0，correct recall = 0.0；
  - `oracle_upper_bound` false accept rate = 0.0，correct recall = 1.0。
- 已运行 tool-only baseline：
  - `tool_only_apply_only` 全部 escalate；
  - `tool_only_validation_summary` false accept rate = 0.0，correct recall = 1.0，
    但该条件仍是 retained executable validation summary，不是
    hidden-evaluator-free realistic merge gate。
- 已运行 prompt dry-run：`llm_only` 22 条、`evidence_first` 22 条，共 44 条；
  label-leakage check 全部 passed。
- 已新增 `docs/experiments/httpie_stage_ab_result.md` 记录本轮 tracked 结果。
- 本地质量门 `scripts/run_local_quality_gate.py` 已通过。

边界：

- 本轮没有调用真实模型 API。
- `httpie_stage_ab_001` 是 Stage A/B preparation evidence，不是最终研究假设的
  model-review evidence。
- 当前仍未生成真实 AI-generated patches；候选仍主要来自 reference/no-op/
  irrelevant/partial 构造。
- 下一步必须二选一并在执行前确认：继续迁移另一个 project group，或先设计并实现
  AI-generated candidate patch generation protocol。

## 6.14 2026-06-08 DeepSeek AI patch generation 计划

用户已确认：

- 允许调用 DeepSeek 官方 API；
- 使用 5 个已验证的 `httpie` tasks；
- 每个 task 生成 2 个 AI candidate patches；
- 本轮只生成 patch 并本地验证，不调用 verifier/reviewer API。

本轮目标：

- 建立真实 AI-generated patch generation protocol。
- 输出独立 run：`httpie_ai_patch_stage_ab_001`。
- 将生成 patch 接入现有 apply + oracle validation pipeline。

计划：

1. 新增独立 generator 脚本，复用现有 DeepSeek client 和 `.env` 加载方式。
2. generator 默认只 dry-run；真实 API 调用必须显式传入 `--execute`。
3. prompt 只能包含 buggy checkout 中的目标文件片段、issue summary、touched files
   和 visible test hint；禁止包含 reference diff、fixed checkout、hidden oracle
   路径、oracle 结果和 expected outcome。
4. 每个 task 生成 2 个 patch，输出 evaluator-facing candidates、generation
   metadata、raw response hash 和 prompt manifest。
5. 对生成 candidates 运行 `validate_patch_candidates.py`，按 oracle 结果把
   outcome 分类为 `correct` 或 `incorrect`；不能 apply 的标记为
   `environment_invalid`，不进入主实验 claims。
6. 生成 tracked 实验报告，更新 README、docs/INDEX、final roadmap、经验文档。
7. 运行本地质量门，提交并推送。

需要停下确认的情况：

- DeepSeek 返回非 diff patch 或大比例 patch 无法 apply，且需要决定是否调整 prompt
  或重试生成。
- 需要扩大 task 数、每 task patch 数、调用 verifier API，或改变模型。
- 为了让 patch 通过验证必须暴露 reference/fixed/hidden evaluator 信息。

执行中断：

- 首次真实生成在 `bugsinpy_httpie_5` 的第 1 个 patch 停止。
- DeepSeek response `finish_reason=length`，4096 completion tokens 全部消耗在
  reasoning tokens，final content 为空，因此无法解析为 JSON/diff。
- 前 8 个 raw responses 已保存，但旧 generator 只有全量成功后才写
  `candidates.pending.jsonl`，导致可解析 raw 尚未落成候选记录。

用户确认的修复策略：

- 允许修改 generator 为增量保存；
- 允许复用已保存 raw responses；
- 允许缩短 source context；
- 允许将 `max_tokens` 提高到 8192；
- 继续完成当前 5 个 httpie tasks x 2 patches，不扩大任务范围，不调用 verifier API。

执行结果：

- 已新增 `scripts/generate_ai_patch_candidates.py`。
- 已新增 `scripts/relabel_ai_patch_candidates.py`。
- 已完成 5 个 `httpie` tasks x 2 patches 的 DeepSeek 生成，共 10 个 AI patches。
- 首次生成在 `bugsinpy_httpie_5__ai_patch_01` 因空 final content 中断；修复后使用
  增量保存、raw 复用、独立 retry raw 和短 source context 完成生成。
- validation 结果：
  - generated candidates = 10；
  - patch applied = 4；
  - oracle ran = 4；
  - oracle passed = 3；
  - patch apply failed = 6。
- relabel 后 outcome：
  - `correct`: 3；
  - `incorrect`: 1；
  - `environment_invalid`: 6。
- 已新增 `docs/experiments/httpie_ai_patch_generation_attempt.md` 记录本轮
  generator-pipeline 诊断结果。

边界：

- 6/10 patch apply failed，比例过高，不能直接进入 verifier API 实验。
- 本轮证明 generator API、raw response 保存、candidate 转换和 validation 链路可运行；
  但没有得到干净的 AI-generated patch dataset slice。
- 下一步必须先确认 generation protocol 选择：更严格 diff-only prompt 重试、只保留
  4 个 applicable patches 作为诊断样本，或改用 coding-agent-style checkout editing
  workflow。

## 6.15 2026-06-08 coding-agent-style patch generation 计划

用户已确认选择：

- 不继续使用直接输出 unified diff 的 chat-style generation protocol；
- 改用 coding-agent-style workflow。

当前 Git 状态：

- 上一提交 `98823e4 Add AI patch generation diagnostics` 已在本地完成；
- GitHub push 多次失败，原因是连接 GitHub 443 reset/timeout；
- 本轮继续本地执行，最终再次尝试 push。

本轮目标：

- 让模型输出结构化 edit plan，而不是直接输出 unified diff。
- 脚本复制 buggy checkout 到 ignored workdir，在 copied checkout 中应用 edits。
- 由本地 `git diff` 生成 patch candidate，从而避免模型手写 diff 导致大比例
  `git apply` 失败。
- 仍使用 5 个 `httpie` tasks，每个 task 2 个 agent-style patches。
- 本轮只生成并验证 patches，不调用 verifier/reviewer API。

计划：

1. 新增 coding-agent-style generator 脚本。
2. prompt 只包含 buggy source、issue summary、visible test hint 和 touched files；
   禁止 reference patch、fixed checkout、hidden oracle path、oracle result 和 label。
3. 模型返回 JSON edit plan：目标文件、find snippet、replacement snippet、rationale。
4. 脚本在 copied buggy checkout 中执行 exact search/replace。
5. 用 `git diff -- <touched files>` 生成 patch_text，并写出 candidates/evidence。
6. 运行 apply + oracle validation；若 apply failure 仍高，停止并报告。
7. 更新 tracked 结果报告、README、INDEX、经验文档和本计划。

执行中断：

- DeepSeek agent-style workflow 已成功生成前 8 个 `httpie` patches。
- `bugsinpy_httpie_5__agent_patch_01` 两次失败，均为 `finish_reason=length`
  且 final content 为空；第二次已将 prompt 缩短到约 935 tokens，并将
  max tokens 提高到 8192，仍全部消耗在 reasoning tokens。

用户新确认：

- 使用 Qwen 试生成；`.env` 中已存在 `QWEN_API_KEY`。
- 本轮只替换 generator model/provider，不改变 task 范围，不调用 verifier API。

Qwen 执行计划：

1. 新增 Qwen official OpenAI-compatible client，读取 `QWEN_API_KEY`，base URL
   优先读取 `QWEN_BASE_URL`。
2. 默认模型使用 `qwen3-coder-plus`，用于 coding-agent-style edit-plan
   generation。
3. 先尝试补齐缺失的 `bugsinpy_httpie_5` agent patches。
4. 若 Qwen endpoint/model/base URL 不可用，停止并报告，不自动切换其他模型。

Qwen 初次结果：

- Qwen successfully returned JSON edit plan for `bugsinpy_httpie_5__agent_patch_01`；
- failure reason: exact `find` snippet not found in `httpie/cli.py`；
- 用户选择严格模式：不允许 fuzzy apply，不允许手动修补，只能让模型重新生成
  exact-match edit plan。

严格重试计划：

1. 强化 prompt，要求 `find` 必须逐字复制 buggy source 中连续存在的原文片段。
2. 若 exact find 仍然失败，则记录为 strict agent generation failure，不进入
   verifier 实验。
3. 不扩大任务范围，不调用 verifier API。

执行结果：

- 已新增 Qwen official OpenAI-compatible client，使用 `QWEN_API_KEY`，默认
  base URL 为 `https://dashscope.aliyuncs.com/compatible-mode/v1`。
- 已更新 `scripts/generate_agent_patch_candidates.py` 支持
  `--api-provider qwen_official`。
- Qwen strict dry-run 通过，2 条 `bugsinpy_httpie_5` prompt boundary checks
  passed。
- Qwen 真实调用成功返回 JSON edit plan，说明 key、endpoint 和模型路径可用。
- 但 strict exact apply 失败：`find snippet not found in httpie/cli.py`。
- 已新增 `docs/experiments/qwen_httpie5_strict_agent_attempt.md` 记录该结果。

边界：

- 本轮没有生成可进入 verifier 实验的 Qwen candidate。
- 按用户选择，不启用 fuzzy apply，不手动修补 patch。
- 当前最客观结论是：Qwen 比 DeepSeek 更稳定地给出结构化输出，但在严格
  exact edit-plan 模式下仍未通过本地应用门槛。

## 6.16 2026-06-09 Qwen 3.7 Plus strict retry for `httpie_5`

用户新要求：

- 使用最新 Qwen 3.7 Plus 再次尝试 `bugsinpy_httpie_5`。

模型确认：

- 阿里云百炼 OpenAI-compatible 文档中对应模型 ID 为 `qwen3.7-plus`。
- 本轮不使用旧的 `qwen3-coder-plus`，改用 `qwen3.7-plus`。

执行边界：

- 仍沿用 strict exact edit-plan protocol。
- 不启用 fuzzy apply。
- 不手动修补模型输出的 `find` snippet。
- 不调用 verifier/reviewer API。
- 若模型接口不可用或 strict exact apply 失败，记录失败原因后停止。

执行计划：

1. 使用 Qwen official client 与 `qwen3.7-plus` 运行 prompt dry-run。
2. 对 `bugsinpy_httpie_5` 生成 2 个 agent-style candidate patches。
3. 若候选 patch 成功生成，继续运行本地 apply/oracle validation。
4. 更新实验记录、索引、经验文档和本计划。

执行结果：

- dry-run 通过，2 条 prompt boundary checks 正常。
- `bugsinpy_httpie_5__agent_patch_01` 生成成功：
  - strict exact `find`/`replace` 应用成功；
  - 本地 `git diff` 成功 materialize patch；
  - patch apply 成功；
  - retained oracle 运行成功；
  - oracle 未通过；
  - relabel 后 outcome 为 `incorrect`。
- `bugsinpy_httpie_5__agent_patch_02` 未生成成功：
  - Qwen provider request 连续 3 次 read timeout；
  - 没有候选进入 pending/relabeled dataset。
- 已修正 `scripts/generate_agent_patch_candidates.py` 中 candidate `source`
  字段硬编码为 DeepSeek 的问题，改为记录实际 `api_provider`。
- 已新增 `docs/experiments/qwen37_httpie5_strict_agent_attempt.md`。

边界：

- 本轮得到 1 个可复现、可验证的 AI-generated negative patch。
- 本轮没有证明 `qwen3.7-plus` 能修复 `httpie_5`，只说明它能在 strict
  edit-plan protocol 下产出可应用 patch。
- `patch_02` timeout 应被记录为 provider/run instability，不应作为语义失败证据。

## 7. 继续/止损门槛

只有满足以下至少一项时继续：

- evidence-first verification 相比 LLM-only review 降低 false accepts；
- 数据集中能构造现实的 incorrect/partial/test-passing-wrong patches；
- claim-level evidence 能解释 LLM-only 决策为什么失败。

如果新数据集无法产生真实感的错误 patch，或者 verifier 只是通过拒绝几乎所有 patch 来降低 false accepts，就应停止。

## 8. 2026-06-09 DeepSeek agent-style 8-patch validation

用户要求继续完成四点：

1. 同步 GitHub；
2. 验证此前 DeepSeek agent-style workflow 已生成的 8 个 patches；
3. 根据验证结果判断是否扩大到更多 task；
4. 若结果质量差，则将 AI-generated patch 降级为扩展实验，而不是主线。

执行边界：

- 不调用新的模型 API。
- 不继续重试 `bugsinpy_httpie_5`。
- 只使用已有
  `outputs/httpie_agent_patch_stage_ab_001/candidates.pending.jsonl` 中的
  8 个候选。
- 使用本地 `validate_patch_candidates.py` 执行 patch apply + retained oracle
  validation。
- 使用 `relabel_ai_patch_candidates.py` 固化 outcome。

计划：

1. 先尝试 `git push`，若网络失败则记录为外部同步阻塞。
2. 验证 8 个 pending candidates。
3. relabel 并统计 correct / incorrect / environment_invalid。
4. 写 tracked 实验报告并更新 README、INDEX、经验文档和本计划。
5. 运行质量门，提交本地改动，最后再次尝试 push。

执行结果：

- `git push` 再次失败，错误为无法连接 `github.com:443`。同步属于外部网络
  阻塞，不是本地提交、认证或代码问题。
- 已验证
  `outputs/httpie_agent_patch_stage_ab_001/candidates.pending.jsonl` 中 8 个
  DeepSeek agent-style patches：
  - patch applied = 8/8；
  - oracle ran = 8/8；
  - oracle passed = 0/8；
  - validation status `validated` = 8/8。
- 已 relabel：
  - `incorrect` = 8；
  - `correct` = 0；
  - `environment_invalid` = 0。
- 已新增
  `docs/experiments/deepseek_agent_patch_validation_result.md`。

决策：

- agent-style workflow 的 patch materialization 可行：已有 8 个候选全部可应用、
  可验证。
- 但它当前没有产生正确修复，不能作为主实验的 balanced patch dataset source。
- AI-generated patches 暂时降级为扩展实验，主要用于 generated-negative /
  partial-fix verifier stress test。
- 主线仍应以真实 bug/reference patches 和可控 negative/partial variants 为核心；
  只有当未来生成协议能稳定产生 oracle-passing 与 oracle-failing 两类 patch 时，
  才能把 AI-generated patch 提升为主数据源。

## 9. 2026-06-09 final roadmap task-set reconstruction update

用户要求按新的判断修改最终计划：

- 研究主线不换，仍是 candidate patch verification under evidence
  visibility；
- 主实验任务集需要重构；
- `httpie_5` 不再承担“必须稳定产出正确 AI patch”的职责；
- `httpie_5` 若 validation 稳定，则保留为 hard-generation / stress /
  appendix case；
- AI-generated patch generation failure 应作为 generator success rate 和
  failure taxonomy 的一部分报告，而不是导致删除任务或更换课题。

本轮修改边界：

- 只修改计划和 schema 文档；
- 不调用新的模型 API；
- 不继续重试 `httpie_5`；
- 不改变论文主线；
- 不删除历史实验记录。

已执行修改：

- 更新 `docs/plans/final_paper_roadmap_zh.md`：
  - 明确 patch generation 不是主研究问题；
  - 新增 task inclusion / exclusion / hard-generation case 原则；
  - 修改 candidate patch 来源比例，不再要求每个 bug 都有 AI-generated correct
    patch；
  - 将 Stage D 改为 fixed-budget generation accounting；
  - 将 `httpie_5` 暂定为 hard-generation/stress case；
  - 将风险 2 改为 generator failure reporting 与 generated-negative extension。
- 更新 `docs/experiments/patch_candidate_schema.md`：
  - 新增 task-level generation accounting 字段；
  - 新增 `generation_status` 和 `task_role`；
  - 明确不能因为模型未修好任务而排除该任务。

后续执行规则：

- 下一步应先检查 `httpie_5` validation stability，而不是继续生成 patch。
- 若稳定，保留 `httpie_5`，但限制其候选数量：
  - 1 个 reference correct patch；
  - 2-3 个 AI-generated incorrect patches；
  - 1 个 constructed partial/control patch。
- 每出现 1 个 generator-unsolved hard case，应补充 1-2 个 validation-stable
  replacement tasks，保证主实验数据集层面正负样本平衡。
- non-applicable patches 主实验占比应控制在 10-15% 以内。

## 10. 2026-06-09 task stability and accounting execution

本轮目标：

- 执行最终 roadmap 的下一步：先检查 `httpie_5` validation stability，而不是继续
  生成 patch。
- 将 task-level generation accounting 从文档规则落成可复用脚本和 tracked
  报告。
- 根据结果决定 `httpie_5` 的角色：included hard-generation case / excluded
  unstable task。

执行边界：

- 不调用模型 API。
- 不继续重试 `httpie_5` patch generation。
- 不删除历史结果。
- 不把 generator failure 当作 task exclusion reason。

计划：

1. 基于现有 `httpie_stage_ab_001` candidates，单独抽取并重复验证
   `bugsinpy_httpie_5` candidates。
2. 检查 reference candidate 是否通过 oracle，negative/control candidates 是否
   按预期失败，所有候选是否 apply/oracle 可复现。
3. 新增 task accounting 脚本，汇总 validation stability、reference validity、
   generator attempts/applicable/correct/incorrect counts 和 task role。
4. 写 tracked 报告，明确 `httpie_5` 是否保留为 hard-generation/stress case。
5. 更新 README、INDEX、经验文档、本计划，运行质量门并同步 GitHub。

执行结果：

- 已生成 `outputs/httpie5_stability_audit_001` 单任务 dataset slice：
  - candidates = 6；
  - correct reference = 1；
  - buggy/no-op = 1；
  - irrelevant = 1；
  - partial fix = 3。
- 已运行两次 validation：
  - run1: 6/6 validated，patch applied 6/6，oracle ran 6/6，oracle passed 1/6；
  - run2: 6/6 validated，patch applied 6/6，oracle ran 6/6，oracle passed 1/6。
- 已新增 `scripts/build_task_generation_accounting.py`。
- 已生成 `outputs/task_generation_accounting/httpie5_task_accounting.jsonl`：
  - `task_role = hard_generation_case`；
  - `generation_status = unsolved`；
  - `main_experiment_included = true`；
  - `generator_attempts = 7`；
  - `num_ai_patches_generated = 3`；
  - `num_ai_patches_applicable = 1`；
  - `num_ai_patches_correct = 0`；
  - `num_ai_patches_incorrect = 1`；
  - `num_ai_patches_environment_invalid = 2`。
- 已新增 `docs/experiments/httpie5_task_stability_accounting.md`。

结论：

- `httpie_5` 在 retained-oracle candidate-label 层面稳定，可以保留在主实验中。
- 它不应作为 generator success case，而应作为 capped hard-generation/stress
  case。
- 目前不能声称它已完成完整 pass-to-pass regression stability audit，因为当前
  pipeline 没有单独定义 pass-to-pass check set。

阻塞/需确认：

- 若下一步要把 `httpie_5` 从 retained-oracle stability 提升为完整
  validation-stable task，需要定义 pass-to-pass regression suite 的来源和范围。

## 11. 2026-06-09 pass-to-pass scope design and httpie5 execution

用户已确认：

- 当前 `httpie_5` audit 报告保持第 3 种表述：只声称 retained-oracle
  candidate-label stability，不声称完整 regression stability。
- 最终主实验采用第 2 种：使用 entire runnable stable pass-to-pass subset。
- 该 subset 不是盲跑项目全部测试，而是满足以下条件的最大稳定可运行集合：
  1. 当前实验环境可收集；
  2. 不属于 fail-to-pass oracle；
  3. buggy baseline 上稳定通过；
  4. reference-fixed version 上稳定通过；
  5. 不依赖外部网络、缺失服务、随机环境或私有配置；
  6. 在 timeout 内稳定完成。
- 推荐双层设计：
  - `P2P-core`：相关非失败测试，用于快速 smoke audit；
  - `P2P-broad`：整个可运行且稳定通过的测试子集，用于最终主实验。

本轮目标：

1. 更新 roadmap、schema 和 `httpie5` 报告，使短期/长期结论一致。
2. 新增 `scripts/build_pass_to_pass_scope.py`，先定义 scope，再验证 candidates。
3. 对 `httpie_5` 尝试构建 P2P-broad stable subset。
4. 若测试收集或运行环境不稳定，记录阻塞点并停止确认。

执行边界：

- 不调用模型 API。
- 不把当前 retained-oracle audit 改写为 full regression stability。
- 不盲目保留所有测试；必须记录排除原因。
- 不因 pass-to-pass 未完成而删除 `httpie_5`。

执行结果：

- 首次直接运行 P2P scope 脚本超时。原因不是模型或数据问题，而是逐个 pytest
  启动开销高，且测试集中包含外部网络测试。
- 已新增 `scripts/build_pass_to_pass_scope.py`：
  - 自动生成 legacy compatibility shim，补齐旧测试依赖的
    `requests.compat.is_py26`；
  - 收集 buggy/reference-fixed 两边的测试；
  - 排除 fail-to-pass oracle；
  - 静态排除包含 `httpbin`、`http://`、`https://` 的外部网络测试；
  - 对剩余测试在 buggy baseline 和 reference-fixed 版本各运行两次；
  - 输出 P2P-core / P2P-broad scope 和排除原因。
- `httpie_5` P2P scope 结果：
  - collected tests = 17；
  - common collected tests = 17；
  - excluded fail-to-pass oracle = 1；
  - excluded static external dependency = 13；
  - P2P-broad tests = 3；
  - P2P-core tests = 3。
- P2P-broad 测试为：
  - `tests/tests.py::TestItemParsing::test_escape`；
  - `tests/tests.py::TestItemParsing::test_invalid_items`；
  - `tests/tests.py::TestItemParsing::test_valid_items`。
- 已新增 `scripts/validate_candidates_with_p2p.py`。
- 已对 6 个 `httpie_5` candidates 运行 retained oracle + P2P-broad validation：
  - `correct_under_f2p_and_p2p_broad` = 1；
  - `incorrect_issue_not_fixed` = 5；
  - `incorrect_regression` = 0。
- 已重新生成 task accounting：
  - `p2p_status = completed`；
  - `label_scope_current = f2p_plus_p2p_broad`；
  - `regression_scope_current = p2p_broad_stable_subset`；
  - `p2p_scope_size = 3`；
  - `p2p_core_size = 3`。
- 已新增 `docs/experiments/httpie5_pass_to_pass_scope.md`。

结论：

- `httpie_5` 现在不仅有 retained-oracle candidate-label stability，也有当前
  环境下的 P2P-broad stable subset。
- 它仍然是 hard-generation/stress case，不是 generator success case。
- P2P-broad 是当前环境下最大稳定可运行子集，不等于原项目完整测试套件；必须在
  论文中报告 collected/excluded/stable counts。

## 12. 2026-06-09 Luigi replacement task validation and P2P execution

本轮目标：

- 按最终 roadmap 的下一步，补充 1-2 个 validation-stable replacement tasks。
- 优先选择已有 task-specific oracle 的任务，降低环境风险：
  - `bugsinpy_luigi_3`；
  - `bugsinpy_luigi_4`。
- 对每个 task 执行与 `httpie_5` 相同的闭环：
  1. 生成 task-specific candidate slice；
  2. 重复运行 retained-oracle candidate validation；
  3. 构建 P2P-broad stable subset；
  4. 使用 retained oracle + P2P-broad 验证 candidates；
  5. 生成 task-level accounting；
  6. 写 tracked 报告并更新索引/经验/README/计划。

执行边界：

- 不调用模型 API。
- 不继续围绕 `httpie_5` 调参或生成 patch。
- P2P-broad 不盲跑全套后直接保留结果；必须记录 collected/excluded/stable
  counts 和排除原因。
- 若 Luigi 测试收集、依赖、运行时间或 P2P scope 定义不清楚，则停止向用户确认。

执行结果：

- 已生成 candidate slices：
  - `bugsinpy_luigi_3`: 5 candidates，1 reference + 4 negative/control；
  - `bugsinpy_luigi_4`: 3 candidates，1 reference + 2 negative/control。
- retained-oracle validation 各运行两次：
  - `luigi_3`: 两次均 5/5 validated，patch applied 5/5，oracle ran 5/5，
    oracle passed 1/5；
  - `luigi_4`: 两次均 3/3 validated，patch applied 3/3，oracle ran 3/3，
    oracle passed 1/3。
- P2P scope 构建中发现并处理的问题：
  - Luigi 旧测试需要 Python 3.11 compatibility shim；
  - `mock` 包缺失，已映射到标准库 `unittest.mock`；
  - `psutil` 缺失，但只影响 import-time compatibility，已加入轻量 shim；
  - per-test P2P 运行对 Luigi 3 过慢，已为
    `scripts/build_pass_to_pass_scope.py` 增加 batch-first；
  - 已为 `scripts/validate_candidates_with_p2p.py` 增加 chunked P2P
    validation，并跳过 retained oracle 已失败候选的 P2P 执行。
- P2P scope 结果：
  - `luigi_3`: collected 137，excluded fail-to-pass oracle 1，excluded static
    external dependency 1，P2P-broad 135；
  - `luigi_4`: collected 14，excluded fail-to-pass oracle 1，P2P-broad 13。
- retained oracle + P2P-broad labels：
  - `luigi_3`: `correct_under_f2p_and_p2p_broad` = 1，
    `incorrect_issue_not_fixed` = 4；
  - `luigi_4`: `correct_under_f2p_and_p2p_broad` = 1，
    `incorrect_issue_not_fixed` = 2。
- task accounting：
  - 两个任务均为 `task_role = main_balanced_task`；
  - 两个任务均为 `generation_status = not_attempted`；
  - 两个任务均为 `main_experiment_included = true`；
  - 两个任务均为 `label_scope_current = f2p_plus_p2p_broad`。
- 已新增 `docs/experiments/luigi_replacement_tasks_result.md`。

边界/需确认：

- 当前 Luigi P2P-broad 是 task-specific test file 内的最大稳定可运行子集：
  - `luigi_3`: `test/parameter_test.py`；
  - `luigi_4`: `test/contrib/redshift_test.py`。
- 这不是整个 Luigi 项目的 project-wide stable test subset。
- 若最终主实验严格要求 project-wide P2P-broad，则下一步需要重新定义并运行
  project-level test discovery；否则可以将当前规则明确为 per-task-file
  P2P-broad，并在论文中报告 scope 边界。

## 13. 2026-06-10 Project-level P2P-broad rebuild

本轮目标：

- 将最终主实验标准确认并落实为 `project_level_p2p_broad`：
  - 收集整个项目中当前环境可发现的测试；
  - 排除 fail-to-pass oracle；
  - 排除不可收集、外部依赖、超时、flaky 或在 buggy/reference 任一版本失败的测试；
  - 保留在 buggy baseline 与 reference-fixed version 上都稳定通过的最大可运行子集。
- 每个 task 输出 tracked-可引用的 manifest：
  - `data/p2p_scopes/{task_id}_p2p_broad.json`。
- 使用统一 label 规则：
  - patch 不可应用：`non_applicable`；
  - fail-to-pass oracle 失败：`incorrect_issue_not_fixed`；
  - P2P-broad 失败：`incorrect_regression`；
  - fail-to-pass 与 P2P-broad 均通过：`correct_under_f2p_and_p2p_broad`。

执行边界：

- 不调用模型 API。
- 不继续生成或调参 `httpie_5` patch。
- 不把 task-file P2P 结果当作最终主实验 project-level P2P 结果。
- 若 project-level 测试收集、运行耗时、环境依赖或 scope 定义出现无法自动判断的问题，停止并向用户确认。
- 稳定性运行次数优先采用 3 次；若项目级 scope 构造因成本或环境限制无法完成，记录阻塞原因后停止确认，而不是私自降级为 task-file scope。

计划步骤：

1. 扩展 `scripts/build_pass_to_pass_scope.py`，支持 project-level test collection 与 manifest 输出。
2. 先对 `bugsinpy_httpie_5` 构造 project-level P2P-broad scope，验证脚本兼容性。
3. 再对 `bugsinpy_luigi_3` 与 `bugsinpy_luigi_4` 构造 project-level P2P-broad scope。
4. 对已有 candidates 使用 project-level P2P-broad 重新验证。
5. 更新报告、索引、经验文档、README，并同步 GitHub。

执行结果：

- 已扩展 `scripts/build_pass_to_pass_scope.py`：
  - 支持 `project_level_p2p_broad` / `task_file_p2p_broad` scope type；
  - 支持 `--manifest-out` 输出 `data/p2p_scopes/{task_id}_p2p_broad.json`；
  - 支持 project-level 显式测试文件发现，覆盖 `test*.py`、`*_test.py`、
    `tests.py`；
  - 修正 buggy/reference checkout 产生不同路径前缀时的 nodeid 规范化；
  - 支持 Windows 下按 batch size 分块执行；
  - 支持按测试文件分组 batch-first 验证，减少失败测试对其他文件的影响。
- 已更新 `scripts/validate_candidates_with_p2p.py` 的最终正确标签：
  - `correct_under_f2p_and_p2p_broad`。
- `bugsinpy_httpie_5` project-level P2P-broad 已完成：
  - collected tests = 17；
  - common collected tests = 17；
  - excluded fail-to-pass oracle = 1；
  - excluded external dependency = 13；
  - included P2P-broad tests = 3；
  - stability runs = 3；
  - manifest: `data/p2p_scopes/bugsinpy_httpie_5_p2p_broad.json`。
- 已用 project-level P2P-broad 重新验证 `httpie_5` 的 6 个 candidates：
  - `correct_under_f2p_and_p2p_broad` = 1；
  - `incorrect_issue_not_fixed` = 5。
- `bugsinpy_luigi_3` project-level P2P-broad 当前阻塞：
  - project-level discovery 发现 113 个测试文件；
  - collect-only 诊断收集到 904 个 nodeids，但同时出现 44 个 collection
    errors，主要来自 contrib / 外部服务依赖类测试；
  - 两次 project-level scope construction 分别在 15 分钟和 20 分钟上限内
    未完成；
  - 第二次已加入按文件分组 batch-first，但仍卡在长时间 pytest batch /
    fallback 执行。
- 本轮本地质量门通过：
  - `python -m py_compile scripts\build_pass_to_pass_scope.py scripts\validate_candidates_with_p2p.py scripts\build_task_generation_accounting.py`；
  - `git diff --check`；
  - `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\project_level_p2p_latest.json --out-md outputs\local_quality_gate\project_level_p2p_latest.md`。

当前阻塞/需确认：

- 是否继续投入工程时间为 Luigi 构造严格 project-level P2P-broad，可能需要：
  - 先生成 collection-error 文件排除表；
  - 对通过 collection 的测试按文件建立稳定性缓存；
  - 对失败文件做 per-test fallback；
  - 允许单个 task 运行数小时。
- 或者将 Luigi 任务暂时标记为 `project_level_p2p_pending`，保留 task-file
  P2P 结果作为 appendix/smoke evidence，并优先换用更小、更容易构造
  project-level P2P-broad 的替代任务。

## 14. 2026-06-10 Luigi freeze and main-cohort filtering

本轮目标：

- 执行最终决策：不继续死磕 Luigi project-level P2P。
- 将 Luigi 标记为：
  - `project_level_p2p_status = pending_blocked`；
  - `p2p_broad_main_included = false`；
  - `appendix_smoke_included = true`；
  - task-file P2P 仅作为 appendix/smoke evidence。
- 建立主实验 cohort 过滤规则：
  - 只有 `project_level_p2p_status == completed` 且
    `p2p_broad_main_included == true` 的任务进入主指标。
- 确保 metrics 脚本默认不把 Luigi 的 incomplete project-level P2P 状态混入
  `p2p_broad_main`。

执行边界：

- 不再运行 Luigi project-level P2P。
- 不删除 Luigi；必须保留 blocked accounting，避免隐性 cherry-picking。
- 不把 task-file P2P 结果重命名成 project-level P2P 结果。
- 不调用模型 API。

计划步骤：

1. 新增 tracked task cohort registry。
2. 修改 metrics filter，默认只统计 `p2p_broad_main` cohort。
3. 更新报告、README、索引、经验文档和最终路线。
4. 运行本地检查后提交并推送。

追加执行：

- 按替代任务筛选原则，优先尝试已有 Stage A/B 验证闭环的
  `bugsinpy_httpie_1` 到 `bugsinpy_httpie_4`。
- 理由：
  - 同属已验证 `httpie_stage_ab_001`；
  - 已有 retained fail-to-pass oracle / candidates / validation records；
  - 项目测试规模相对 Luigi 小；
  - 有机会快速补足 3-5 个 `project_level_p2p_broad` 成功任务。
- 对每个任务执行：
  1. 构造 project-level P2P-broad manifest；
  2. 若 scope 完成且 P2P-broad size >= 3，则加入 cohort registry；
  3. 用对应 manifest 重新验证该 task 的 candidates；
  4. 若 scope 阻塞，则记录为 `pending_blocked`，不进入主指标。

执行结果：

- 已新增 `data/cohorts/task_cohort_registry.json`：
  - `bugsinpy_httpie_5` 进入 `p2p_broad_main`；
  - `bugsinpy_luigi_3` / `bugsinpy_luigi_4` 进入
    `blocked_or_pending` + `p2p_local_smoke`；
  - `bugsinpy_httpie_1` 到 `bugsinpy_httpie_4` 均记录为
    `pending_blocked`。
- 已修改 `scripts/analyze_patch_verification.py`：
  - 默认读取 `data/cohorts/task_cohort_registry.json`；
  - 默认只统计满足 `project_level_p2p_status == completed` 且
    `p2p_broad_main_included == true` 的任务；
  - `--no-cohort-filter` 仅用于 appendix/diagnostic。
- 已修改 `scripts/build_task_generation_accounting.py`：
  - 读取同一份 cohort registry；
  - blocked 任务覆盖为 `task_role = blocked_or_pending`；
  - blocked 任务不再进入 `main_experiment_included`。
- 已对 accounting 做本地验证：
  - `task_count = 3`；
  - `main_experiment_included_count = 1`；
  - `task_role_counts = {"main_balanced_task": 1, "blocked_or_pending": 2}`。
- 替代任务 sweep 结果：
  - `httpie_1`: 19 个测试文件全部 collection error，原因是缺少真实
    `pytest_httpbin` 测试依赖；
  - `httpie_2`: project-level scope 构造超过限定预算，被终止；
  - `httpie_3`: project-level scope 构造超过限定预算，被终止；
  - `httpie_4`: 初始缺旧版 `requests.compat.is_windows`；补兼容 shim 后仍超过
    限定预算，被终止。
- 已新增 `docs/experiments/p2p_feasibility_sweep_update.md`。

当前结论：

- 当前 `p2p_broad_main` cohort 仍只有 `bugsinpy_httpie_5`。
- 不应降低 project-level P2P 标准。
- 下一步应换项目进行 bounded feasibility sweep，优先选择没有重型 pytest
  fixture、没有外部服务依赖、collection 能在 5-8 分钟内完成的任务。

本轮检查：

- `python -m json.tool data\cohorts\task_cohort_registry.json` 通过；
- `python -m json.tool data\p2p_scopes\bugsinpy_httpie_5_p2p_broad.json` 通过；
- `python -m py_compile` 覆盖相关脚本通过；
- `git diff --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\cohort_gating_latest.json --out-md outputs\local_quality_gate\cohort_gating_latest.md` 通过。

## 15. 2026-06-10 `tqdm` replacement feasibility sweep

本轮目标：

- 执行用户确认的下一步：筛选 `bugsinpy_tqdm_1` 与 `bugsinpy_tqdm_2`。
- 目标不是降低标准凑样本，而是在 bounded feasibility 规则下寻找新的
  `p2p_broad_main` 任务。

执行边界：

- 不调用模型 API。
- 不生成新 candidate patch。
- 不继续运行 Luigi project-level P2P。
- 若 `tqdm` 任务无法在限定预算内完成 project-level P2P-broad，则记录为
  `pending_blocked`，不进入主指标。

计划步骤：

1. 对 `bugsinpy_tqdm_1` 构造 project-level P2P-broad scope。
2. 对 `bugsinpy_tqdm_2` 构造 project-level P2P-broad scope。
3. 若 scope 完成且 P2P-broad size >= 3，则写入 manifest 并更新 cohort
   registry。
4. 若 scope 阻塞，则更新 feasibility sweep report 和 cohort registry。
5. 运行检查、提交并同步 GitHub。

执行结果：

- `bugsinpy_tqdm_1` project-level P2P-broad scope 完成，但不达主实验门槛：
  - discovered test files = 10；
  - collected/common nodeids = 1；
  - collection error files = 9；
  - included P2P-broad tests = 1；
  - retained test = `tqdm/tests/tests_version.py::test_version`；
  - 主要阻塞原因：缺少 legacy `nose` 依赖。
- `bugsinpy_tqdm_2` project-level P2P-broad scope 完成，但不达主实验门槛：
  - discovered test files = 6；
  - collected/common nodeids = 1；
  - collection error files = 5；
  - included P2P-broad tests = 1；
  - retained test = `tqdm/tests/tests_version.py::test_version`；
  - 主要阻塞原因：缺少 legacy `nose` 依赖。
- 两个任务均已写入 cohort registry：
  - `project_level_p2p_status = completed_insufficient_p2p_broad`；
  - `p2p_broad_main_included = false`；
  - `appendix_smoke_included = true`。
- 已更新 `docs/experiments/p2p_feasibility_sweep_update.md`。

当前结论：

- `tqdm_1` / `tqdm_2` 不能进入 `p2p_broad_main`。
- 当前 `p2p_broad_main` cohort 仍只有 `bugsinpy_httpie_5`。
- 下一步若继续 `black_1` / `black_3`，需要注意它们 prior visible test
  使用 `unittest`，而当前 P2P scope builder 主要面向 pytest nodeid。

本轮检查：

- `python -m json.tool` 覆盖 cohort registry 与两个 `tqdm` P2P manifests；
- `python -m py_compile` 覆盖相关脚本；
- cohort filter 检查确认 `included_task_ids = ["bugsinpy_httpie_5"]`；
- `git diff --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\tqdm_sweep_latest.json --out-md outputs\local_quality_gate\tqdm_sweep_latest.md` 通过。

## 16. 2026-06-10 `unittest` adapter and `black` feasibility sweep

本轮目标：

- 执行用户确认的决策：扩展 project-level P2P scope builder，增加
  `unittest` adapter。
- 该扩展用于支持 `bugsinpy_black_1` / `bugsinpy_black_3` 等 unittest
  任务，但不改变 P2P-broad 定义，也不降低主实验门槛。

执行边界：

- 支持 `unittest` discovery / runner，用于 project-level P2P-broad scope
  construction。
- 不支持任意 custom test harness。
- 不支持 nose legacy runner。
- 不为 black 写硬编码路径；只允许通过 CLI 参数指定 unittest discovery
  配置。
- 不把 task-file unittest smoke 结果混进主指标。
- 只有当任务满足：
  - project-level P2P-broad construction completed；
  - `p2p_broad_size >= 3`；
  - stability runs = 3；
  - 后续 candidate revalidation under F2P + P2P-broad；
  才能进入 `p2p_broad_main`。

计划步骤：

1. 为 `scripts/build_pass_to_pass_scope.py` 增加 `--test-framework
   pytest|unittest`。
2. 实现 unittest discovery：`start_dir`、`pattern`、`top_level_dir` 可配置。
3. 实现 unittest 单测重复运行，输出与 pytest scope 一致的 manifest 字段。
4. 先运行 `bugsinpy_black_1` feasibility sweep。
5. 若 adapter 通用且未遇到结构性阻塞，再运行 `bugsinpy_black_3`。
6. 更新 cohort registry / feasibility report / README / index / experience
   notes，运行检查后提交并同步 GitHub。

执行结果：

- 已为 `scripts/build_pass_to_pass_scope.py` 增加 `unittest` adapter：
  - 新增 `--test-framework pytest|unittest`；
  - 新增 `--unittest-start-dir`、`--unittest-pattern`、
    `--unittest-top-level-dir`；
  - 支持 standard-library unittest discovery；
  - 支持 `python -m unittest <test_id>` 重复运行；
  - `_FailedTest` 不再被误当作 runnable test，而是记录为 collection
    error；
  - 若存在 collection errors，且使用 `--manifest-out`，则在
    `data/p2p_scopes/` 生成 tracked collection-error manifest。
- `bugsinpy_black_1` feasibility sweep：
  - test framework = `unittest`；
  - collected/common nodeids = 0；
  - collection errors = 1；
  - P2P-broad size = 0；
  - 阻塞原因：导入 `black` 时缺少真实依赖 `typed_ast`；
  - 状态：`pending_blocked`。
- `bugsinpy_black_3` feasibility sweep：
  - test framework = `unittest`；
  - collected/common nodeids = 0；
  - collection errors = 1；
  - P2P-broad size = 0；
  - 阻塞原因：导入 `black` 时缺少真实依赖 `typed_ast`；
  - 状态：`pending_blocked`。
- 已更新：
  - `data/cohorts/task_cohort_registry.json`；
  - `docs/experiments/p2p_feasibility_sweep_update.md`；
  - README / INDEX / experience notes / final roadmap。

当前结论：

- `unittest` 框架支持已完成到 bounded feasibility 所需程度。
- `black_1` / `black_3` 没有进入 `p2p_broad_main`，原因不是框架不支持，
  而是当前环境缺少 `typed_ast`。
- 不应静默安装 `typed_ast`；是否允许安装/隔离依赖环境需要单独确认。

本轮检查：

- `python -m json.tool` 覆盖 cohort registry、black P2P manifests 和 black
  collection-error manifests；
- `python -m py_compile` 覆盖相关脚本；
- cohort filter 检查确认 `included_task_ids = ["bugsinpy_httpie_5"]`；
- `git diff --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\unittest_black_latest.json --out-md outputs\local_quality_gate\unittest_black_latest.md` 通过。

## 17. 2026-06-10 isolated `black` dependency environment

本轮目标：

- 执行用户确认的许可：为 `black` 任务建立隔离依赖环境，并尝试安装
  `typed-ast==1.4.0`。
- 目的：判断 `bugsinpy_black_1` / `bugsinpy_black_3` 的阻塞是否只是缺少
  declared dependency；若依赖补齐后可构造 project-level P2P-broad，则继续按
  原门槛筛选。

执行边界：

- 不安装到全局 Python。
- 不提交虚拟环境、pip cache 或运行 outputs。
- 不安装超出当前阻塞所需的依赖，除非新的 import error 明确显示仍是
  black declared dependency，且需要再次记录。
- 不降低主实验门槛：`p2p_broad_size >= 3`、stability runs = 3。
- 若 `typed-ast==1.4.0` 与当前 Python 版本不兼容，记录为环境阻塞后停止确认，
  不私自改装其他版本。

计划步骤：

1. 检查本机可用 Python 版本。
2. 在 ignored `outputs/envs/` 下创建 black 专用隔离环境。
3. 在隔离环境安装 `typed-ast==1.4.0`。
4. 使用隔离环境重跑 `black_1` / `black_3` unittest project-level P2P
   feasibility sweep。
5. 根据结果更新 cohort registry、feasibility report、README、index、经验和
   当前计划。

执行结果：

- 本机仅发现 Python 3.11：
  - `C:\Python311\python.exe`。
- 已在 ignored `outputs/envs/black_typed_ast_py311` 下创建隔离 venv，并尝试：
  - `pip install typed-ast==1.4.0`。
- 安装失败：
  - pip 下载源码包并尝试 build wheel；
  - 构建 `_ast27` 扩展时失败；
  - 明确错误为缺少 `Microsoft Visual C++ 14.0 or greater` build tools。
- 已删除失败的隔离 venv，避免留下无效环境。

当前阻塞：

- `typed-ast==1.4.0` 在当前机器的 Python 3.11 环境下没有直接可用 wheel，
  且需要本机 C++ build tools 编译。
- 按本轮边界，不私自：
  - 安装系统级 MSVC Build Tools；
  - 改装其他 `typed-ast` 版本；
  - 使用未确认的 Python 版本或替代依赖。
- 因此 `black_1` / `black_3` 仍保持 `pending_blocked`。

后续需要用户确认的选项：

1. 安装系统级 Microsoft C++ Build Tools 后重试 `typed-ast==1.4.0`；
2. 提供/安装 Python 3.8 或 3.9，再用更接近 BugsInPy 时代的解释器重建隔离环境；
3. 明确允许尝试较新 `typed-ast` 版本，但这会偏离 declared requirement，需要作为环境偏差记录；
4. 暂停 black，继续筛选其他不需要编译型 legacy dependency 的任务。

## 18. 2026-06-10 `cookiecutter` project-level P2P feasibility sweep

本轮目标：

- 在 `black` 被本机 C++ build tools / legacy `typed-ast` 阻塞后，执行最短路径的替代任务筛选。
- 对 `bugsinpy_cookiecutter_1` / `bugsinpy_cookiecutter_2` /
  `bugsinpy_cookiecutter_3` 尝试构造 project-level P2P-broad scope。
- 目标是判断这些任务是否可能补充 `p2p_broad_main`，不是迁移完整 oracle，也不是生成新的 candidate patch。

执行边界：

- 不调用模型 API。
- 不安装或升级依赖。
- 不使用 `tox` 作为隐式环境构造器；本轮只在当前 Python 环境下用已有
  `build_pass_to_pass_scope.py` 做 bounded feasibility。
- 不降低主实验门槛：只有 project-level P2P-broad construction completed、
  `p2p_broad_size >= 3`、stability runs = 3，且后续 candidate revalidation
  完成后，任务才可能进入 `p2p_broad_main`。
- 若 collection/import/runtime 因缺依赖、外部服务或超时失败，记录为 blocked/pending，
  不把 task-file/local smoke 证据混入主指标。

计划步骤：

1. 读取三个 `cookiecutter` retained checkout 中的 `bugsinpy_run_test.sh`，提取
   fail-to-pass nodeid 作为 P2P 排除项。
2. 分别运行 project-level P2P-broad scope builder，使用 3 次 stability runs 和 bounded timeout。
3. 将生成的 manifest 复制到 `data/p2p_scopes/`，并按结果更新 cohort registry。
4. 更新 feasibility sweep report、README、INDEX、经验文档和本计划。
5. 运行本地检查，提交并同步 GitHub。

执行结果：

- 已运行 `bugsinpy_cookiecutter_1` project-level P2P-broad scope builder：
  - discovered test files = 45；
  - collected/common nodeids = 0；
  - collection error files = 45；
  - included P2P-broad tests = 0；
  - blocker = retained checkout `setup.cfg` 注入 `--cov-report` 与
    `--cov=cookiecutter`，当前环境缺少 pytest-cov 或明确的 addopts override。
- 已生成 tracked manifests：
  - `data/p2p_scopes/bugsinpy_cookiecutter_1_p2p_broad.json`；
  - `data/p2p_scopes/bugsinpy_cookiecutter_1_p2p_broad_collection_errors.json`。
- `bugsinpy_cookiecutter_2` / `bugsinpy_cookiecutter_3` 未继续重复运行；它们在
  cohort registry 中记录为 shared cookiecutter pytest-cov addopts blocker。
- 已更新 cohort registry、feasibility report、README、INDEX 和经验文档。

当前阻塞/需确认：

- 若继续 `cookiecutter`，需要明确选择：
  1. 在隔离环境中安装 pytest-cov，并把它作为 declared test dependency 记录；
  2. 或允许 `build_pass_to_pass_scope.py` 增加受审计的 pytest `-o addopts=`
     override，用于移除 coverage-only addopts。
- 在确认前，`cookiecutter_1` / `cookiecutter_2` / `cookiecutter_3` 均不能进入
  `p2p_broad_main`。

## 19. 2026-06-10 audited coverage-only pytest addopts override

用户确认的决策：

- 针对 `cookiecutter` 的 P2P scope 构造，允许在
  `scripts/build_pass_to_pass_scope.py` 中加入受审计的 pytest addopts override。
- override 只移除 coverage-only 的 pytest-cov 参数，例如 `--cov`、
  `--cov=...`、`--cov-report`、`--cov-report=...`、`--cov-config`、
  `--cov-append`、`--cov-branch`、`--cov-context`、`--cov-fail-under`、
  `--cov-reset`。
- 不优先安装 pytest-cov；安装 pytest-cov 只保留为后续 fallback。
- 不能无条件清空所有 addopts；必须读取原始 addopts、只移除 coverage 相关 token、
  保留非 coverage token，并把原始/移除/保留/sanitized 内容写入 audit manifest。

执行计划：

1. 扩展 `build_pass_to_pass_scope.py`，新增显式开关
   `--sanitize-coverage-addopts`，默认不开启。
2. 读取 `setup.cfg` / `pytest.ini` / `tox.ini` 中的 pytest `addopts`。
3. 当且仅当 sanitizer 可安全移除 coverage-only token 时，用
   `pytest -o addopts="<sanitized_addopts>"` 执行 collection 和 P2P 稳定性运行。
4. 将 audit 信息写入 scope manifest，并在 `data/p2p_scopes/` 写 sibling
   `*_addopts_override_audit.json`。
5. 用 `bugsinpy_cookiecutter_1` 重跑 project-level P2P feasibility；根据结果更新
   registry、报告、README、INDEX、经验文档和本计划。
6. 运行检查、提交；GitHub push 若仍受网络阻塞，保留 ahead 状态并记录。

执行结果：

- 已为 `build_pass_to_pass_scope.py` 增加显式
  `--sanitize-coverage-addopts` 开关，默认不开启。
- sanitizer 已接入 pytest collection、单测重复运行和 batch P2P 稳定性运行。
- `bugsinpy_cookiecutter_1` retry 中记录的 audit：
  - original addopts = `-vvv --cov-report term-missing --cov=cookiecutter`；
  - removed tokens = `--cov-report`, `term-missing`, `--cov=cookiecutter`；
  - retained tokens = `-vvv`；
  - sanitized addopts = `-vvv`。
- retry 结果：
  - coverage-only blocker 已移除；
  - discovered test files = 45；
  - collected/common nodeids = 0；
  - collection error files = 20；
  - missing modules = `poyo`、`binaryornot`、`freezegun`。
- 已写入 tracked audit：
  - `data/p2p_scopes/bugsinpy_cookiecutter_1_p2p_broad_addopts_override_audit.json`。

当前阻塞/需确认：

- `cookiecutter` 当前已不是 coverage-only blocker，而是缺少 declared runtime/test
  dependencies 的环境问题。
- 按安全规则，不继续自动安装依赖、不继续运行 `cookiecutter_2` /
  `cookiecutter_3`，直到用户确认是否建立隔离 Cookiecutter dependency environment。

本轮检查：

- `python -m json.tool` 覆盖 cohort registry、`cookiecutter_1` P2P manifest、
  collection-error manifest 和 addopts override audit；
- `python -m py_compile` 覆盖 P2P scope builder 与相关分析脚本；
- cohort filter 检查确认 `included_task_ids = ["bugsinpy_httpie_5"]`；
- `git diff --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json
  outputs\local_quality_gate\cookiecutter_addopts_override_latest.json --out-md
  outputs\local_quality_gate\cookiecutter_addopts_override_latest.md` 通过。

## 20. 2026-06-10 isolated `cookiecutter` dependency environment

用户确认：

- 允许为 `cookiecutter` 建立隔离依赖环境，安装 declared runtime/test dependencies，
  然后继续 P2P feasibility sweep。

执行边界：

- 只在 ignored `outputs/envs/` 下创建 venv，不污染全局 Python。
- 不安装 `pytest-cov` 作为优先修复；继续使用第 19 节实现的 coverage-only
  addopts sanitizer。
- 依赖来源以 retained checkout 的 `setup.py` runtime requirements 与
  `test_requirements.txt` 为准；`bugsinpy_requirements.txt` 中的 editable Git
  checkout 和 `pkg-resources==0.0.0` 不直接作为 Windows 当前环境安装输入。
- 若出现需要编译型依赖、Python 版本不兼容、或新的非声明依赖，记录后停止确认。
- 若 `cookiecutter_1` 在隔离环境下完成 project-level P2P-broad，则再判断是否继续
  `cookiecutter_2` / `cookiecutter_3`；不提前把它们加入主实验。

计划步骤：

1. 创建 `outputs/envs/cookiecutter_p2p_py311`。
2. 安装 `setup.py` 中声明的 runtime deps 与 `test_requirements.txt` 中的 test deps，
   但不依赖 pytest-cov 来解决 coverage addopts。
3. 使用该 venv Python、`--sanitize-coverage-addopts` 重跑 `bugsinpy_cookiecutter_1`
   project-level P2P feasibility。
4. 根据结果更新 cohort registry、P2P manifest、实验报告、README、INDEX、经验文档和本计划。
5. 运行检查、提交；若 GitHub 仍因网络失败，记录本地 ahead 状态。

执行结果：

- 已创建 ignored venv：`outputs/envs/cookiecutter_p2p_py311`。
- 已安装 Cookiecutter runtime/test dependencies 所需包；未安装 pytest-cov，继续使用
  audited coverage-only addopts sanitizer。
- 首次使用相对 venv Python 路径的动态 P2P run 超过 15 分钟并留下混合
  system/venv Python 子进程；已仅终止该 P2P run 相关进程，保留 app server 进程。
- 诊断发现 retained `-vvv` addopts 会让 pytest 9 的 `--collect-only` 输出变成树形结构；
  已修复 `build_pass_to_pass_scope.py`：
  - 支持解析 pytest collect tree；
  - 参数化 nodeid 可映射回非参数化源码片段；
  - 当 error_count 归零时刷新 sibling collection-error manifest，避免 stale evidence。
- 使用绝对 venv Python 同时作为脚本 runner 和 `--python` test interpreter 后，
  `bugsinpy_cookiecutter_1` project-level P2P-broad 构造完成：
  - discovered test files = 45；
  - collected/common nodeids = 296；
  - excluded fail-to-pass oracle = 1；
  - excluded failed on buggy baseline = 5；
  - included P2P-broad tests = 290；
  - stability runs = 3 per version。
- 已新增依赖环境审计：
  - `data/p2p_scopes/bugsinpy_cookiecutter_1_dependency_environment_audit.json`。
- 已刷新：
  - `data/p2p_scopes/bugsinpy_cookiecutter_1_p2p_broad.json`；
  - `data/p2p_scopes/bugsinpy_cookiecutter_1_p2p_broad_collection_errors.json`
    现在 `error_count = 0`；
  - `data/cohorts/task_cohort_registry.json`。

当前结论：

- `bugsinpy_cookiecutter_1` 是 P2P scope ready，但仍不能进入 `p2p_broad_main`。
- 原因：还没有 Cookiecutter fail-to-pass oracle 和 candidate validation under F2P +
  P2P-broad。
- 下一步应迁移 `cookiecutter_1` 的 fail-to-pass oracle，并构造/reference/no-op/partial
  candidate 后再进行 validation；不要仅凭 P2P scope ready 就加入主指标。

本轮检查：

- `python -m json.tool` 覆盖 cohort registry、`cookiecutter_1` P2P manifest、
  collection-error manifest、addopts override audit 和 dependency environment audit；
- `python -m py_compile` 覆盖 P2P scope builder 与相关分析脚本；
- cohort filter 检查确认 `included_task_ids = ["bugsinpy_httpie_5"]`；
- `git diff --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json
  outputs\local_quality_gate\cookiecutter_scope_ready_latest.json --out-md
  outputs\local_quality_gate\cookiecutter_scope_ready_latest.md` 通过。

## 21. 2026-06-10 `cookiecutter_1` oracle and candidate validation

本轮目标：

- 继续执行 `cookiecutter_1` 的下一步：迁移 fail-to-pass oracle，并构造可验证
  candidates。
- 将 `cookiecutter_1` 从 P2P scope ready 推进到 candidate validation ready。
- 仍不把它加入 `p2p_broad_main`，除非 reference/no-op/partial candidates 已完成
  F2P + P2P-broad validation。

已确认事实：

- BugsInPy 原始测试命令：`tox tests/test_generate_context.py::test_generate_context_decodes_non_ascii_chars`。
- bug 修复点：`cookiecutter/generate.py` 中 `open(context_file)` 改为
  `open(context_file, encoding='utf-8')`。

执行边界：

- 使用已有 isolated venv `outputs/envs/cookiecutter_p2p_py311` 运行 oracle 和 P2P；
  不安装新的依赖，除非出现新的 declared dependency blocker 并先记录。
- 新 oracle 只验证 UTF-8 JSON context decoding，不扩大为全项目测试。
- candidate 构造先走最小集：reference correct、buggy no-op、partial/negative control。
- 所有主标签仍必须通过 F2P oracle + project-level P2P-broad；P2P scope ready 本身不等于
  main inclusion。

计划步骤：

1. 新增 `scripts/oracles/cookiecutter_1_utf8_context.py`。
2. 在 buggy/fixed retained checkout 上分别运行 oracle，确认 buggy fail / fixed pass。
3. 构造 `cookiecutter_1` candidate slice，至少包含 reference、no-op、partial/negative。
4. 用 `validate_patch_candidates.py` 或必要扩展执行 apply + oracle validation。
5. 用 `validate_candidates_with_p2p.py` 合并 F2P + P2P-broad label。
6. 更新 cohort registry、实验报告、README、INDEX、经验文档和本计划，运行检查并提交。

执行中新增约束：

- `cookiecutter_1` checkout 中存在 Windows reparse point/junction 形式的
  `docs/*.md` 条目，`shutil.copytree` 不能按普通文件复制它们。它们不属于当前
  `cookiecutter/generate.py` oracle、candidate patch 或 P2P scope 的语义输入；
  因此本轮只允许在 candidate validation 的 checkout 复制阶段跳过 reparse point，
  并必须在经验文档中记录该环境兼容问题。
- `cookiecutter_1` P2P scope construction 使用了 audited coverage-only
  addopts sanitizer；candidate-level P2P validation 必须复用 scope manifest 中的
  `pytest_addopts_override.sanitized_addopts`，否则未安装 `pytest-cov` 的隔离 venv
  会把 reference candidate 误标为 pytest invocation failure。

执行结果：

- 已新增 `scripts/oracles/cookiecutter_1_utf8_context.py`。
- oracle 直接检查结果：buggy checkout fail，fixed checkout pass。
- 已将 `bugsinpy_cookiecutter_1` 加入 candidate builder，并为单行 UTF-8 bug 新增
  `task_specific_wrong_encoding_diff` 负例。
- retained-oracle validation：
  - candidates = 4；
  - patch_applied = 4；
  - oracle_ran = 4；
  - oracle_all_passed = 1；
  - validation_status_counts = `validated: 4`。
- F2P + P2P-broad validation：
  - p2p_broad_test_count = 290；
  - `correct_under_f2p_and_p2p_broad: 1`；
  - `incorrect_issue_not_fixed: 3`。
- 已更新 `data/cohorts/task_cohort_registry.json`：
  - `bugsinpy_cookiecutter_1.project_level_p2p_status = completed`；
  - `bugsinpy_cookiecutter_1.p2p_broad_main_included = true`；
  - `bugsinpy_cookiecutter_1.cohorts = ["p2p_broad_main"]`。

当前结论：

- `bugsinpy_cookiecutter_1` 已从 P2P scope ready 推进到 project-level
  `p2p_broad_main` 任务。
- 这是第二个完成 project-level P2P-broad 主任务；但该任务只有 4 个候选，不能被表述为
  最终论文规模已经足够。

## 22. 2026-06-10 `cookiecutter_2` project-level P2P and candidate validation attempt

本轮目标：

- 在不改变最终研究主线的前提下，争取补齐第三个 project-level P2P 主任务。
- 优先尝试 `bugsinpy_cookiecutter_2`，因为 `cookiecutter_1` 已证明同项目的隔离
  dependency venv、coverage-only addopts sanitizer、compat shim 和 candidate-level
  P2P runner 路径可行。
- 若 `cookiecutter_2` 的原始 oracle、reference patch 或 P2P scope 不能稳定定义，
  立即记录 blocker，不把它硬纳入主指标。

执行边界：

- 继续使用已有 isolated venv `outputs/envs/cookiecutter_p2p_py311`；不安装新依赖，
  除非出现明确的 declared dependency blocker 并先记录。
- 继续使用 project-level P2P-broad 标准；不能降级为 task-file P2P 来凑主指标。
- candidate 最小集仍为 reference correct、buggy no-op、irrelevant/comment-only、以及
  与 bug 语义相关的 constructed negative。若 constructed negative 无法从 bug 语义
  合理生成，则只记录 reference/no-op/irrelevant，不伪造困难负例。
- 所有最终标签仍必须来自 F2P oracle + P2P-broad。

计划步骤：

1. 检查 `cookiecutter_2` 的 BugsInPy metadata、原始测试命令、buggy/fixed diff。
2. 构造或迁移最小 fail-to-pass oracle，并在 buggy/fixed checkout 上验证
   buggy fail / fixed pass。
3. 构造 project-level P2P-broad scope；若 scope 已因同项目条件可复用，只能复用
   方法和环境，不能直接复用 `cookiecutter_1` 的 manifest。
4. 将 `cookiecutter_2` 加入 candidate builder，构造候选切片并运行 retained-oracle
   validation。
5. 运行 F2P + P2P-broad candidate validation。
6. 根据结果更新 cohort registry、实验报告、README、INDEX、经验文档和本计划，运行检查，
   提交并 push。

执行结果：

- `cookiecutter_2` retained workspace 缺少 `bugsinpy_bug.info` 与
  `bugsinpy_run_test.sh`，因此本轮从 buggy/fixed diff 和测试文件推断行为边界。
- source diff 集中在 `cookiecutter/hooks.py`：`find_hook` 由返回单个脚本改为返回
  所有匹配脚本列表，`run_hook` 逐个执行。
- 已确认 F2P 节点：
  `tests/test_hooks.py::TestExternalHooks::test_run_hook`：
  - buggy fail；
  - fixed pass。
- 已构造 project-level P2P-broad scope：
  - common nodeids = 286；
  - excluded fail-to-pass oracle = 1；
  - excluded failed on buggy baseline = 7；
  - included P2P-broad tests = 278；
  - stability runs = 3 per version。
- 已新增 `scripts/oracles/cookiecutter_2_multiple_hooks.py`：
  - direct oracle check: buggy fail / fixed pass。
- 已将 `bugsinpy_cookiecutter_2` 加入 candidate builder。
- candidate slice：
  - candidates = 11；
  - correct_reference = 1；
  - buggy_noop = 1；
  - irrelevant_patch = 1；
  - partial_fix = 8。
- retained-oracle validation：
  - patch_applied = 11；
  - oracle_ran = 11；
  - oracle_all_passed = 1；
  - validation_status_counts = `validated: 11`。
- F2P + P2P-broad validation：
  - p2p_broad_test_count = 278；
  - `correct_under_f2p_and_p2p_broad: 1`；
  - `incorrect_issue_not_fixed: 10`。
- 已更新 `data/cohorts/task_cohort_registry.json`：
  - `bugsinpy_cookiecutter_2.project_level_p2p_status = completed`；
  - `bugsinpy_cookiecutter_2.p2p_broad_main_included = true`；
  - `bugsinpy_cookiecutter_2.cohorts = ["p2p_broad_main"]`。

当前结论：

- `bugsinpy_cookiecutter_2` 已成为第三个 project-level `p2p_broad_main` 任务。
- 当前主 cohort 任务数从 2 增至 3，但距离中期增强版 15-20 bugs 仍明显不足。
- 已本地提交：`420030c Admit cookiecutter 2 P2P validation`。
- GitHub push 失败，错误为 HTTPS `Recv failure: Connection was reset`；后续提交后需要重试
  push，不能认为远端已经同步。

## 23. 2026-06-11 `cookiecutter_3` project-level P2P and candidate validation attempt

本轮目标：

- 继续按最短路径扩展第四个 project-level P2P 主任务。
- 优先尝试 `bugsinpy_cookiecutter_3`，因为 Cookiecutter 的隔离依赖环境、
  coverage-only addopts sanitizer、Windows reparse point 处理、candidate-level P2P
  runner 已经在 `cookiecutter_1/2` 中打通。
- 若 `cookiecutter_3` 缺少可稳定定义的 F2P oracle、reference patch 或 P2P-broad
  scope，记录 blocker 并停止该任务，不用降级标准凑数量。

执行边界：

- 使用已有 `outputs/envs/cookiecutter_p2p_py311`，不安装新依赖，除非出现新的明确
  blocker 并先记录。
- 仍采用 project-level P2P-broad，不能复用 `cookiecutter_1/2` 的 manifest。
- 先从 buggy/fixed diff、测试文件和可运行节点确认 bug 行为；如果没有
  BugsInPy metadata，需要明确写成 inference。
- candidate 最小集为 reference、no-op、irrelevant/comment-only、以及能从 bug 语义
  合理生成的 partial/negative；不能伪造难负例。

计划步骤：

1. 检查 `cookiecutter_3` checkout、metadata、buggy/fixed diff 和相关测试。
2. 确认可稳定运行的 F2P 节点或构造 standalone oracle，并验证 buggy fail / fixed pass。
3. 构造 `cookiecutter_3` project-level P2P-broad scope。
4. 注册 candidate builder，构造候选并运行 retained-oracle validation。
5. 运行 F2P + P2P-broad candidate validation。
6. 更新 registry、实验报告、README、INDEX、经验文档和本计划，运行检查，提交并重试 push。

执行中新增约束：

- `cookiecutter_3` 的 `setup.py` 声明 `future>=0.15.2`，但当前
  `outputs/envs/cookiecutter_p2p_py311` 中缺失该包，导致
  `ModuleNotFoundError: No module named 'past'`。这是 declared dependency
  blocker。本轮允许仅在 ignored isolated venv 中安装 pinned `future==0.18.3`，
  并必须生成/更新 dependency environment audit；不得安装全局依赖。
- 首次 project-level P2P scope 构造后仍有 18 个 collection-error files，原因是
  缺少 `whichcraft`；`cookiecutter_3` 的 `setup.py` 声明 `whichcraft>=0.4.0`。
  本轮允许仅在同一 ignored isolated venv 中安装 pinned `whichcraft==0.6.1`，然后
  重建 `cookiecutter_3` scope；不得把含缺失声明依赖的 18 个 collection errors
  当作最终主实验 scope。

执行结果：

- metadata 存在，原始 F2P 命令为：
  `tox tests/test_read_user_choice.py::test_click_invocation`。
- source diff 集中在 `cookiecutter/prompt.py`：
  `click.prompt(..., default=default)` 改为
  `click.prompt(..., default=default, show_choices=False)`。
- 已安装 declared dependencies 到 ignored isolated venv：
  - `future==0.18.3`；
  - `whichcraft==0.6.1`。
- 已生成 dependency environment audit：
  `data/p2p_scopes/bugsinpy_cookiecutter_3_dependency_environment_audit.json`。
- 已确认 F2P 参数化节点：
  - `tests/test_read_user_choice.py::test_click_invocation[1-hello]`；
  - `tests/test_read_user_choice.py::test_click_invocation[2-world]`；
  - `tests/test_read_user_choice.py::test_click_invocation[3-foo]`；
  - `tests/test_read_user_choice.py::test_click_invocation[4-bar]`。
- 已构造 project-level P2P-broad scope：
  - common nodeids = 262；
  - excluded fail-to-pass oracle = 4；
  - excluded failed on buggy baseline = 3；
  - collection errors = 0；
  - included P2P-broad tests = 255；
  - stability runs = 3 per version。
- 已新增 `scripts/oracles/cookiecutter_3_prompt_show_choices.py`：
  - direct oracle check: buggy fail / fixed pass。
- 已将 `bugsinpy_cookiecutter_3` 加入 candidate builder，并新增
  `task_specific_wrong_prompt_visibility_diff` 负例。
- candidate slice：
  - candidates = 4；
  - correct_reference = 1；
  - buggy_noop = 1；
  - irrelevant_patch = 1；
  - partial_fix = 1。
- retained-oracle validation：
  - patch_applied = 4；
  - oracle_ran = 4；
  - oracle_all_passed = 1；
  - validation_status_counts = `validated: 4`。
- F2P + P2P-broad validation：
  - p2p_broad_test_count = 255；
  - `correct_under_f2p_and_p2p_broad: 1`；
  - `incorrect_issue_not_fixed: 3`。
- 已更新 `data/cohorts/task_cohort_registry.json`：
  - `bugsinpy_cookiecutter_3.project_level_p2p_status = completed`；
  - `bugsinpy_cookiecutter_3.p2p_broad_main_included = true`；
  - `bugsinpy_cookiecutter_3.cohorts = ["p2p_broad_main"]`。

当前结论：

- `bugsinpy_cookiecutter_3` 已成为第四个 project-level `p2p_broad_main` 任务。
- 当前主 cohort 任务数从 3 增至 4；仍未达到中期增强版 15-20 bugs 的目标规模。
- 已本地提交：`b2c1532 Admit cookiecutter 3 P2P validation`。
- GitHub push 两次失败：
  - 默认 HTTPS：`Recv failure: Connection was reset`；
  - HTTP/1.1 retry：无法连接 `github.com:443`。
- 当前远端同步未完成；后续继续大规模实验前应优先重试 push，避免本地 ahead
  积累过多。

## 24. 2026-06-11 fifth project-level P2P task selection

本轮目标：

- 先恢复远端同步，再继续扩展第 5 个 project-level `p2p_broad_main` 任务。
- 当前 `p2p_broad_main` 已有 4 个任务：
  - `bugsinpy_httpie_5`；
  - `bugsinpy_cookiecutter_1`；
  - `bugsinpy_cookiecutter_2`；
  - `bugsinpy_cookiecutter_3`。
- 本轮选择策略：优先从已有 BugsInPy workspace 中寻找依赖可控、F2P oracle 清楚、
  project-level P2P-broad 可构造的任务；不降低 project-level P2P 标准。

已完成前置同步：

- `Test-NetConnection github.com -Port 443` 恢复为 `TcpTestSucceeded: True`。
- `git push origin main` 成功，将本地 3 个提交同步到远端：
  - `420030c Admit cookiecutter 2 P2P validation`；
  - `b2c1532 Admit cookiecutter 3 P2P validation`；
  - `155ceea Record GitHub push blocker`。

执行边界：

- 先检查候选任务 metadata、buggy/fixed diff、F2P 节点和依赖；遇到新的依赖 blocker
  必须记录后再处理。
- 不复用其他任务的 P2P manifest；每个任务必须独立构造 project-level P2P-broad。
- 若某候选任务无法稳定证明 buggy fail / fixed pass 或 reference patch under P2P，
  记录为 blocked，不硬纳入主 cohort。

候选筛选结果：

- `bugsinpy_black_2` 暂不优先：没有已迁移 visible test，且 black 同系列已经暴露
  `typed_ast` project-level collection blocker。
- `bugsinpy_tqdm_3` 到 `bugsinpy_tqdm_8` 暂不优先：测试体系仍显著依赖
  `nose`，与 `tqdm_1/2` 的 blocker 同类；安装或模拟 `nose` 属于新的环境
  决策，不在本轮静默执行。
- `bugsinpy_tqdm_9` 作为第 5 个候选任务：
  - changed file: `tqdm/_tqdm.py`；
  - retained F2P nodes:
    - `tqdm/tests/tests_tqdm.py::test_si_format`；
    - `tqdm/tests/tests_tqdm.py::test_update`；
  - buggy checkout: 两个 F2P 节点失败；
  - fixed checkout: `tqdm/tests/tests_tqdm.py` 共 14 个测试全部通过；
  - 当前未触发 `nose` collection blocker。

下一步执行：

1. 新增 `scripts/oracles/tqdm_9_si_len.py`，直接覆盖 SI rounding 与
   `len(tqdm(total=2))` 两个行为。
2. 将 `bugsinpy_tqdm_9` 注册进 candidate builder。
3. 构造 `bugsinpy_tqdm_9` 的 project-level P2P-broad scope，排除两个 F2P
   oracle 节点。
4. 生成并验证 candidate patches。
5. 更新 cohort registry、实验报告、README、INDEX、经验文档，提交并 push。

执行结果：

- 已新增 oracle：`scripts/oracles/tqdm_9_si_len.py`。
- direct oracle check：
  - buggy checkout: fail；
  - fixed checkout: pass。
- 已构造 project-level P2P-broad scope：
  - collected/common nodeids = 14；
  - excluded fail-to-pass oracle = 2；
  - collection error files = 0；
  - included P2P-broad tests = 12；
  - stability runs = 3 per version。
- 初始 candidate generation 产生 13 个候选，但 6 个 generic partial negatives
  仍通过 retained oracle。原因是 reference diff 混入 style-only changes 或
  不影响两个目标行为的 threshold-line variants；这些不能作为负例。
- 已在 candidate builder 中为 `bugsinpy_tqdm_9` 增加任务级 partial allowlist，
  最终 candidate slice 为 7 个：
  - correct_reference = 1；
  - buggy_noop = 1；
  - irrelevant_patch = 1；
  - partial_fix = 4。
- retained-oracle validation：
  - patch_applied = 7；
  - oracle_ran = 7；
  - validation_status_counts = `validated: 7`。
- F2P + P2P-broad validation：
  - `correct_under_f2p_and_p2p_broad: 1`；
  - `incorrect_issue_not_fixed: 6`。
- 已更新 `data/cohorts/task_cohort_registry.json`：
  - `bugsinpy_tqdm_9.project_level_p2p_status = completed`；
  - `bugsinpy_tqdm_9.p2p_broad_main_included = true`；
  - `bugsinpy_tqdm_9.cohorts = ["p2p_broad_main"]`。

当前结论：

- `bugsinpy_tqdm_9` 已成为第五个 project-level `p2p_broad_main` 任务。
- 当前主 cohort 任务数从 4 增至 5；仍未达到中期增强版 15-20 bugs 的目标规模。

## 25. 2026-06-11 sixth project-level P2P task screening boundary

本轮目标：

- 在 `bugsinpy_tqdm_9` 成为第五个主任务后，继续从 retained BugsInPy
  workspace 中寻找第 6 个不需要新环境决策的 project-level P2P 任务。

筛选对象：

- `bugsinpy_black_2`；
- `bugsinpy_tqdm_3`；
- `bugsinpy_tqdm_4`；
- `bugsinpy_tqdm_5`；
- `bugsinpy_tqdm_6`；
- `bugsinpy_tqdm_7`；
- `bugsinpy_tqdm_8`。

筛选结果：

- `bugsinpy_black_2`：
  - bug diff 指向 `black.py` 的 `fmt: on/off` 处理，并新增
    `tests/data/fmtonoff4.py`；
  - `tests/test_black.py` 中存在 `test_fmtonoff4`；
  - 但当前环境中 `import black` 直接失败：
    `ModuleNotFoundError: No module named 'typed_ast'`；
  - 这与 `black_1/3` 的 blocker 同类，不能静默安装或模拟 `typed_ast`。
- `bugsinpy_tqdm_3` 到 `bugsinpy_tqdm_8`：
  - 在不安装新依赖的情况下逐文件 pytest collect；
  - 每个任务只收集到 `tqdm/tests/tests_version.py::test_version`；
  - 行为相关测试文件仍通过 legacy `nose` 路径 collection error；
  - 低于主实验 P2P-broad 标准，不能作为第 6 个主任务。

已更新：

- `data/cohorts/task_cohort_registry.json` 中新增/更新上述任务为
  `blocked_or_pending`；
- `project_level_p2p_status = pending_blocked`；
- `p2p_broad_main_included = false`。

当前阻碍：

- retained selected subset 中，除已完成的 5 个 main tasks 外，剩余候选都需要
  新的环境决策：
  - 是否建立 controlled legacy `nose` environment；
  - 是否处理 Black 的 `typed_ast`/MSVC blocker；
  - 或者是否引入更多 BugsInPy 项目作为新候选池。

## 26. 2026-06-11 expand BugsInPy candidate pool decision

用户确认：

- 选择第 3 个方向。
- 不再优先修复 legacy `nose` blocker，也不优先处理 Black 的
  `typed_ast`/MSVC native dependency blocker。
- 下一阶段直接引入更多 BugsInPy 项目作为新候选池，目标是扩大真实任务规模。

决策文本：

```text
Decision:
Do not spend the next phase repairing legacy dependency blockers.
Expand the BugsInPy candidate pool and prioritize tasks that can complete
project-level P2P-broad construction under the existing audited pipeline.
```

执行边界：

- `tqdm_3-8` 保留为 `pending_blocked` / legacy dependency cases。
- `black_1/2/3` 保留为 `pending_blocked` / native dependency cases。
- 不降低主实验纳入标准：
  - `project_level_p2p_status = completed`；
  - `p2p_broad_main_included = true`；
  - `p2p_broad_size >= 3`；
  - `stability_runs = 3`；
  - reference patch 必须通过 F2P 和 P2P-broad；
  - candidate labels 必须能在 F2P + P2P-broad 下重新验证。
- 新候选优先级：
  - pytest 或标准 unittest；
  - 不依赖 `nose`；
  - 不依赖本地编译型 legacy package；
  - 不依赖外部网络、数据库、浏览器、服务端；
  - collection 能在限定时间内完成；
  - F2P oracle 清楚；
  - reference patch 稳定；
  - project-level P2P-broad size >= 3。

下一步：

1. 定位本地 BugsInPy 源仓库或项目元数据。
2. 生成新的 candidate-pool feasibility sweep 输入。
3. 先做 lightweight screening，不直接进入完整 candidate validation。
4. 对所有失败任务记录 blocker，不静默删除。

执行进展：

- 本地 BugsInPy 源仓库已定位：
  `D:/mgao/code/research/tmp/bugsinpy_archive/BugsInPy-master`。
- 已新增 metadata-level screening 脚本：
  `scripts/screen_bugsinpy_candidate_pool.py`。
- 首次筛选结果：
  - total BugsInPy tasks = 501；
  - new candidate tasks = 479；
  - promising metadata-level candidates = 195；
  - top candidates = `bugsinpy_PySnooper_1/2/3`、`fastapi_1/2` 等。
- 已生成 tracked report：
  `docs/experiments/bugsinpy_candidate_pool_screening.md`。

`bugsinpy_PySnooper_1` probe：

- buggy/fixed checkout 已成功创建到外部 retained workspace：
  `D:/mgao/code/research/data/real_bugs/bugsinpy_workspace/PySnooper_1`。
- 直接使用系统 Python 3.11 运行 F2P 时，buggy/fixed 均先遇到
  `ImportError: cannot import name 'Mapping' from 'collections'`。
  这是 Python 3.11 兼容 shim 范围，和现有 P2P builder 的
  `collections.abc` shim 一致。
- 加入兼容 shim 后，buggy/fixed 均遇到
  `ModuleNotFoundError: No module named 'python_toolbox'`。
- `python-toolbox` 是 `setup.py` 的 `extras_require['tests']` 中声明的测试
  依赖。本轮允许仅在 ignored isolated venv 中安装 declared test
  dependencies，并生成 dependency environment audit；不得安装全局依赖。

执行结果：

- 已建立 ignored isolated venv：
  `outputs/envs/pysnooper_p2p_py311`。
- 已跟踪依赖环境审计：
  `data/p2p_scopes/bugsinpy_PySnooper_1_dependency_environment_audit.json`。
- 已新增 retained oracle：
  `scripts/oracles/pysnooper_1_utf8_log.py`。
- direct oracle check：
  - buggy checkout：读取 UTF-8 log 时触发 `UnicodeDecodeError`；
  - fixed checkout：`oracle_passed`。
- 已构造 project-level P2P-broad scope：
  - collected/common nodeids = 29；
  - excluded fail-to-pass oracle = 1；
  - excluded failed on buggy baseline = 4；
  - included P2P-broad tests = 24；
  - collection error files = 0；
  - stability runs = 3 per version。
- 已修复候选构造脚本两个问题：
  - reference diff 支持多 touched files；
  - label-leakage guard 改为完整 token 匹配，避免 `noop` 误命中
    `PySnooper`。
- 已生成并验证 6 个 candidate patches：
  - correct_reference = 1；
  - buggy_noop = 1；
  - irrelevant_patch = 1；
  - partial_fix = 3。
- `missing_change_1` 在 Python 3.11 retained oracle 下实际通过，因为它保留
  UTF-8 解码和 UTF-8 写日志，只省略 Python 2 compatibility hunk；因此已从
  PySnooper partial negative allowlist 中排除。
- retained oracle validation：
  - record_count = 6；
  - patch_applied_count = 6；
  - oracle_ran_count = 6；
  - oracle_all_passed_count = 1；
  - validation_status_counts.validated = 6。
- F2P + P2P-broad validation：
  - record_count = 6；
  - p2p_broad_test_count = 24；
  - patch_applied_count = 6；
  - retained_oracle_passed_count = 1；
  - `correct_under_f2p_and_p2p_broad` = 1；
  - `incorrect_issue_not_fixed` = 5。
- 已新增实验报告：
  `docs/experiments/pysnooper1_candidate_validation.md`。
- 已将 `bugsinpy_PySnooper_1` 加入 `p2p_broad_main` cohort。

当前结论：

- `p2p_broad_main` 从 5 个任务扩展到 6 个任务。
- `bugsinpy_PySnooper_1` 满足当前主实验纳入标准：
  - `project_level_p2p_status = completed`；
  - `p2p_broad_main_included = true`；
  - `p2p_broad_size = 24 >= 3`；
  - `stability_runs = 3`；
  - reference patch 通过 F2P + P2P-broad；
  - candidate labels 可在 F2P + P2P-broad 下重新验证。

下一步：

1. 最终一致性检查已通过：
   - Python 编译通过；
   - JSON 解析通过；
   - cohort 主任务计数 = 6；
   - `git diff --check` 无空白错误，仅有 Windows 换行提示。
2. 下一步提交并 push 本轮更新。
3. 随后继续从 broader BugsInPy pool 中筛选下一个低摩擦 candidate task，
   优先 `PySnooper_2/3`、`fastapi_1/2` 或同等 pytest/unittest 任务。

## 27. 2026-06-12 seventh project-level P2P candidate

同步恢复：

- 上轮 `bugsinpy_PySnooper_1` 提交 `8e5613d` 一直未能通过直连 GitHub
  push，因为 `github.com:443` 直连失败。
- 本轮发现本机 `127.0.0.1:7890` 代理可用，使用临时 Git 代理配置完成 push：
  `git -c http.proxy=http://127.0.0.1:7890 -c https.proxy=http://127.0.0.1:7890 push origin main`。
- 注意：没有写入永久 Git config，只是本次命令级代理。

第 7 个候选任务选择：

- 优先尝试 `bugsinpy_PySnooper_2`。
- 理由：
  - broader BugsInPy screening 中 `PySnooper_1/2/3` 排名靠前；
  - `PySnooper_1` 已证明该项目可以在当前 Python 3.11 + compatibility shim +
    declared test dependency venv 下完成 project-level P2P-broad；
  - 同项目后续任务更可能复用已审计环境边界，能更快扩大主 cohort。

执行边界：

- 不因为同项目复用就跳过 validation-stability gate。
- `bugsinpy_PySnooper_2` 必须独立完成：
  - buggy/fixed checkout；
  - F2P oracle：buggy fail、fixed pass；
  - project-level P2P-broad，`p2p_broad_size >= 3`；
  - 3 runs stability；
  - reference patch 通过 F2P + P2P-broad；
  - candidate labels 可重新验证。
- 如果 F2P 行为、oracle 构造或 task role 不清楚，停止并向用户确认。

初步审计结果：

- buggy/fixed checkout 已成功创建到：
  `D:/mgao/code/research/data/real_bugs/bugsinpy_workspace/PySnooper_2`。
- `bugs/2/run_test.sh` 指定：
  `pytest -q -s tests/test_pysnooper.py::test_custom_repr_single`。
- 元数据存在不一致：
  - `bugs/2/run_test.sh` 指向 `test_custom_repr_single`；
  - `PySnooper-pass.txt` 中 bug 2 行指向
    `test_snooping_on_class_does_not_cause_base_class_to_be_snooped`；
  - 但 `bug_patch.txt` 的核心 source patch 明确是 `custom_repr` 支持，因此当前
    以 `run_test.sh` 和实际 F2P probe 为准。
- F2P probe 未能进入目标断言：
  - buggy checkout：`tests/test_pysnooper.py` collection 失败，因为 copied test
    imports `.mini_toolbox`，但 checkout 的 `tests/` 目录中没有
    `mini_toolbox.py`；
  - fixed checkout：import `pysnooper` 时失败，因为 fixed `tracer.py` 引用
    `pycompat.PY2`，但 fixed `pycompat.py` 没有定义 `PY2`。
- 这两个问题都不是 `custom_repr` 目标行为本身：
  - `mini_toolbox.py` 是 test fixture/helper 缺失；
  - `pycompat.PY2` 是 reference checkout import-compatibility 缺口。

当前不能私自继续：

- 若直接给 source tree 补 `pycompat.PY2` 或补 `tests/mini_toolbox.py`，会改变
  retained checkout 的可执行环境边界；
- 若完全绕开原始 test 写 standalone oracle，也仍需要决定是否允许
  `pycompat.PY2` compatibility shim，否则 reference patch 无法 import；
- 因此 `bugsinpy_PySnooper_2` 暂停在 user-confirmation gate。

需要用户确认的下一步：

1. 将 `bugsinpy_PySnooper_2` 标记为 blocked feasibility case，然后尝试
   `bugsinpy_PySnooper_3` 或 `fastapi_1`；
2. 或者允许为 `bugsinpy_PySnooper_2` 使用明确记录的 compatibility/test-fixture
   shim：
   - external shim 定义 `pycompat.PY2 = not pycompat.PY3`；
   - 从可信来源补齐缺失的 `tests/mini_toolbox.py`，或绕过原始 pytest fixture
     使用 standalone oracle；
   - 所有 shim 必须记录到 dependency/environment audit，且不得混入 patch
     candidate 本身。

最终决策：

- `bugsinpy_PySnooper_2` 标记为 `blocked_feasibility_case`。
- `main_experiment_included = false`。
- `p2p_broad_main_included = false`。
- `blocked_reason = unclear_experimental_boundary`。
- `shim_allowed_now = false`。

决策理由：

- `bugsinpy_PySnooper_2` 的问题不是单纯缺依赖或 coverage 参数阻塞，而是实验
  边界不清楚；
- 当前阶段不允许为了让该任务进入主实验而做 compatibility/test-fixture shim；
- test-fixture shim 可能改变测试前置条件、fixture 行为、输出捕获或环境语义，
  比 `pytest -o addopts` coverage-only override 更敏感；
- 为保持主 cohort 标签可信度，`bugsinpy_PySnooper_2` 只保留在 blocked task
  accounting 中。

下一步执行：

1. 冻结 `bugsinpy_PySnooper_2`，不做 shim。
2. 尝试 `bugsinpy_PySnooper_3`。
3. `bugsinpy_PySnooper_3` 只能使用现有受审计 pipeline，不允许为 PySnooper
   家族新增 compatibility/test-fixture shim 先例。
4. 如果 `bugsinpy_PySnooper_3` 也出现同类 boundary/shim 需求，立即 block。
5. 随后转向 `bugsinpy_fastapi_1`。

`bugsinpy_PySnooper_3` probe 启动：

- 目标：在不新增 compatibility/test-fixture shim 的前提下判断是否能进入
  project-level P2P-broad 主实验候选。
- 允许复用：
  - 现有 PySnooper ignored venv；
  - 已审计的 Python 3.11 `collections.abc` compatibility shim；
  - 现有 `build_pass_to_pass_scope.py` / validation scripts。
- 不允许：
  - 补 `tests/mini_toolbox.py`；
  - 给 source tree 注入 `pycompat.PY2`；
  - 修改原始 test fixture 或测试语义；
  - 为 PySnooper 家族新增 task-specific shim。

初步 F2P probe：

- buggy/fixed checkout 已成功创建到：
  `D:/mgao/code/research/data/real_bugs/bugsinpy_workspace/PySnooper_3`。
- `bugs/3/run_test.sh` 指定：
  `pytest -q -s tests/test_pysnooper.py::test_file_output`。
- 直接使用 `PySnooper_1` venv 运行时，buggy/fixed 均在 collection 阶段失败：
  `ModuleNotFoundError: No module named 'future'`。
- `future>=0.17.1` 是 `PySnooper_3` retained checkout 的
  `requirements.txt` 中声明的依赖，不属于 compatibility/test-fixture shim。

执行决定：

- 不污染 `PySnooper_1` 的审计 venv；
- 为 `bugsinpy_PySnooper_3` 建立独立 ignored venv：
  `outputs/envs/pysnooper3_p2p_py311`；
- 只安装项目声明依赖和 pytest runner；
- 后续若仍出现 test-fixture/compatibility shim 需求，则立即 block。

执行结果：

- 已安装 declared runtime/test dependencies 到 ignored isolated venv：
  `decorator`、`future`、`six`、`python_toolbox`、`pytest`。
- 已新增 dependency environment audit：
  `data/p2p_scopes/bugsinpy_PySnooper_3_dependency_environment_audit.json`。
- F2P probe：
  - buggy checkout：`test_file_output` 因 `NameError: output_path is not defined`
    失败；
  - fixed checkout：`test_file_output` 通过。
- 已构造 project-level P2P-broad scope：
  - collected/common nodeids = 5；
  - excluded fail-to-pass oracle = 1；
  - excluded failed on buggy baseline = 0；
  - included P2P-broad tests = 4；
  - collection error files = 0；
  - stability runs = 3 per version。
- 已新增 retained oracle：
  `scripts/oracles/pysnooper_3_file_output.py`。
- direct oracle check：
  - buggy checkout：`NameError: output_path is not defined`；
  - fixed checkout：`oracle_passed`。
- 已将 `bugsinpy_PySnooper_3` 加入候选构造脚本。
- reference patch 是单行修复，默认 generic candidates 只有 3 个且没有
  difficult negative；已新增 task-specific negative：
  `wrong_mode_keeps_undefined_path`，它触及相关 `open(...)` 调用但仍保留
  未定义的 `output_path`。
- candidate validation：
  - candidate_count = 4；
  - correct_reference = 1；
  - buggy_noop = 1；
  - irrelevant_patch = 1；
  - partial_fix = 1；
  - retained oracle validation 全部通过标签校验。
- F2P + P2P-broad validation：
  - record_count = 4；
  - p2p_broad_test_count = 4；
  - patch_applied_count = 4；
  - retained_oracle_passed_count = 1；
  - `correct_under_f2p_and_p2p_broad` = 1；
  - `incorrect_issue_not_fixed` = 3。
- 已新增实验报告：
  `docs/experiments/pysnooper3_candidate_validation.md`。

当前结论：

- `bugsinpy_PySnooper_3` 满足当前主实验纳入标准：
  - `project_level_p2p_status = completed`；
  - `p2p_broad_main_included = true`；
  - `p2p_broad_size = 4 >= 3`；
  - `stability_runs = 3`；
  - reference patch 通过 F2P + P2P-broad；
  - candidate labels 可在 F2P + P2P-broad 下重新验证。
- `p2p_broad_main` 从 6 个任务扩展到 7 个任务。
- 下一候选任务转向 broader pool 中的 `bugsinpy_fastapi_1`。

一致性检查：

- Python 编译通过；
- JSON 解析通过；
- cohort 主任务计数 = 7；
- `bugsinpy_PySnooper_2` registry 状态确认为
  `blocked_feasibility_case` / `p2p_broad_main_included = false` /
  `shim_allowed_now = false`；
- `git diff --check` 无空白错误，仅有 Windows 换行提示。

## 30. 2026-06-12 next candidate feasibility: fastapi_2 first

本轮 Inspect：

- Git 状态：`main...origin/main`，工作区干净。
- `bugsinpy_fastapi_1` 已按 official-test-root timeout 记录，不进入
  `p2p_broad_main`。
- broader candidate pool 中下一高分候选为 `bugsinpy_fastapi_2`，其元数据为：
  - project = `fastapi`；
  - buggy commit = `210af1fd3dc0f612a08fa02a0cb3f5adb81e5bfb`；
  - fixed commit = `02441ff0313d5b471b662293244c53e712f1243f`；
  - F2P test = `tests/test_ws_router.py::test_router_ws_depends_with_override`。

本轮小目标：

1. 准备 `bugsinpy_fastapi_2` retained buggy/fixed checkout。
2. 在现有 FastAPI isolated venv 或同等 declared-dependency venv 下运行 F2P probe。
3. 如果 F2P oracle 不清楚、需要 test-fixture shim、或明显继承 FastAPI official-root
   scope timeout 风险，则记录 blocker 并转向下一个候选。

执行边界：

- 本轮先做 checkout 和 F2P feasibility，不做 45-60 分钟 P2P construction。
- 不安装全局依赖；如需新增依赖，只能进入 ignored isolated venv 并记录依赖审计。
- 不改 FastAPI source/test fixture。
- 不降级到 task-file-level P2P 作为 main evidence。
- 如果 FastAPI 同项目 official-root scope 风险仍不可控，优先转向 `bugsinpy_sanic_1`
  或其他低摩擦 pytest/unittest 项目，而不是继续多个 FastAPI 任务重复超时。

验收条件：

- checkout 成功；
- F2P probe 明确 buggy fail / fixed pass；
- 或者明确记录 blocker 与下一候选。

`bugsinpy_fastapi_2` 执行结果：

- buggy/fixed checkout 已成功创建到外部 retained workspace：
  `D:/mgao/code/research/data/real_bugs/bugsinpy_workspace/fastapi_2`。
- 使用现有 FastAPI isolated venv
  `outputs/envs/fastapi1_p2p_py311` 运行目标 F2P：
  - buggy checkout：
    `tests/test_ws_router.py::test_router_ws_depends_with_override` 失败，
    断言 `"Socket Dependency" == "Override"`；
  - fixed checkout：同一测试通过。
- 因此 `bugsinpy_fastapi_2` 的 F2P oracle 清楚。

本轮决策：

- 不继续对 `bugsinpy_fastapi_2` 执行 official-root P2P construction。
- 原因：`bugsinpy_fastapi_1` 已证明 FastAPI 项目级 official-root `tests/` scope
  在当前 pipeline 下超过 60 分钟仍无法生成 manifest；`fastapi_2` 共享同一项目测试根目录和
  scope 风险。
- `bugsinpy_fastapi_2` 应记录为 shared FastAPI official-root scope risk case，
  不进入 `p2p_broad_main`。

下一候选：

- 转向 `bugsinpy_sanic_1`。
- F2P metadata：
  - project = `sanic`；
  - buggy commit = `e7001b00747b659f7042b0534802b936ee8a53e0`；
  - fixed commit = `44973125c15304b4262c51c78b5a86bd1daafa86`；
  - F2P test = `tests/test_blueprints.py::test_bp_middleware_order`；
  - patch changes response middleware insertion from `append` to `appendleft`。
- Sanic requirements 较重，且包含不适合当前 Windows 环境的依赖；本轮不得全量安装
  requirements，只允许按 F2P probe 的最小缺失依赖进入 ignored isolated venv 并记录。

`bugsinpy_sanic_1` 执行结果：

- buggy/fixed checkout 已成功创建到外部 retained workspace：
  `D:/mgao/code/research/data/real_bugs/bugsinpy_workspace/sanic_1`。
- 初始 F2P probe 在 buggy/fixed 上均因缺少 `aiofiles` 失败。
- 已创建 ignored isolated venv：
  `outputs/envs/sanic1_p2p_py311`。
- 只安装目标 F2P/P2P probe 所需的声明 runtime/test 依赖子集；未安装全量
  requirements。
- `multidict==4.7.6` 初次安装因 MSVC C extension 构建失败；使用
  `MULTIDICT_NO_EXTENSIONS=1` 安装纯 Python fallback 成功。
- Python 3.11 下还需要外部 runtime compatibility shim：
  - 恢复 `asyncio.coroutine = types.coroutine`；
  - 对 legacy asyncio primitives 忽略已移除的 `loop=` keyword。
- 该 shim 已同步到 `scripts/build_pass_to_pass_scope.py` 的通用 compat shim；
  不修改 Sanic source/test fixture。

F2P probe：

- buggy checkout：
  `tests/test_blueprints.py::test_bp_middleware_order` 失败，middleware order 为
  `[1, 2, 3, 6, 5, 4]`，预期 `[1, 2, 3, 4, 5, 6]`。
- fixed checkout：同一测试通过。
- 因此 `bugsinpy_sanic_1` 的 F2P oracle 清楚。

Project-level P2P attempt：

- 已尝试运行
  `scripts/build_pass_to_pass_scope.py --task-id bugsinpy_sanic_1 --project sanic --test-path . --scope-type project_level_p2p_broad ...`。
- 该运行达到 60 分钟预算仍未完成，未生成
  `data/p2p_scopes/bugsinpy_sanic_1_p2p_broad.json`。
- 观察到残留进程停在 `tests/test_response_timeout.py` 相关 batch；已终止本轮 Sanic
  scope 构造进程。

最终状态：

- `bugsinpy_fastapi_2` 记录为 `pending_blocked_shared_scope_risk`。
- `bugsinpy_sanic_1` 记录为
  `pending_blocked_project_level_scope_timeout`。
- 新增依赖环境审计：
  `data/p2p_scopes/bugsinpy_sanic_1_dependency_environment_audit.json`。
- 新增 Sanic timeout 记录：
  `data/p2p_scopes/bugsinpy_sanic_1_project_level_timeout.json`。
- 新增实验记录：
  `docs/experiments/fastapi2_sanic1_feasibility.md`。
- 两个任务均不进入 `p2p_broad_main`。

下一步：

- 转向 broader pool 中非 FastAPI、非 Sanic 的下一个低摩擦候选。
- 优先考虑 `bugsinpy_scrapy_1` 等 unittest 候选，但开始前必须先 Inspect
  其 dependencies 是否含外部服务、native build 或网络边界。

本轮最小验证：

- `python -m py_compile scripts\build_pass_to_pass_scope.py` 通过。
- `data/cohorts/task_cohort_registry.json` JSON 解析通过。
- `data/p2p_scopes/bugsinpy_sanic_1_dependency_environment_audit.json` JSON 解析通过。
- `data/p2p_scopes/bugsinpy_sanic_1_project_level_timeout.json` JSON 解析通过。
- registry 中 `bugsinpy_fastapi_2` 唯一，状态为
  `pending_blocked_shared_scope_risk`，`p2p_broad_main_included = false`。
- registry 中 `bugsinpy_sanic_1` 唯一，状态为
  `pending_blocked_project_level_scope_timeout`，`p2p_broad_main_included = false`。
- 已确认无 `bugsinpy_sanic_1` / `bugsinpy_fastapi_2` 相关残留 Python 进程。
- `git diff --check` 无空白错误，仅有 Windows 换行提示。

`bugsinpy_fastapi_1` probe 启动：

- 目标：从 broader BugsInPy pool 中继续扩展第 8 个 project-level
  P2P-broad 主实验候选。
- 元数据：
  - `buggy_commit_id = 766157bfb4e7dfccba09ab398e8ec444d14e947c`；
  - `fixed_commit_id = 3397d4d69a9c2d64c1219fcbf291ea5697a4abb8`；
  - `test_file = tests/test_jsonable_encoder.py`；
  - `run_test.sh = pytest tests/test_jsonable_encoder.py::test_encode_model_with_default`。
- 执行边界：
  - 只允许安装 `requirements.txt` 或项目声明的依赖到 ignored isolated venv；
  - 不修改 FastAPI source/test fixture；
  - 不为单个 task 增加 compatibility/test-fixture shim；
  - 若 F2P 行为、dependency boundary 或 project-level P2P scope 需要不清楚的
    shim，则停止并记录 blocked。

`bugsinpy_fastapi_1` 当前 probe 状态：

- 已通过 BugsInPy checkout 准备 buggy/fixed workspace。
- 已创建 ignored isolated venv：
  `outputs/envs/fastapi1_p2p_py311`。
- 已安装最小项目声明 runtime/test dependencies：
  `pytest`、`starlette==0.13.2`、`pydantic>=1.5.1,<2.0.0`、`requests`。
- F2P probe 结果：
  - buggy checkout：
    `tests/test_jsonable_encoder.py::test_encode_model_with_default`
    因 `TypeError: jsonable_encoder() got an unexpected keyword argument
    'exclude_defaults'` 失败；
  - fixed checkout：同一 oracle 通过。
- 第一次 project-level P2P-broad scope construction 使用完整 repo test discovery
  运行超时，未生成 manifest；已终止残留 Python/pytest 进程。
- 超时后的局部排查显示，最后观察到的 `tests/test_dependency_contextmanager.py`
  单文件收集可快速完成；当前风险更像是 FastAPI 项目可发现测试文件数量较大
  导致的执行时间问题，而不是单个测试文件卡死。

下一步：

- 在不改变实验边界、不引入 task-specific shim、不降级为 task-file scope 的前提下，
  先用更长执行窗口重试同一 project-level P2P-broad construction。
- 若长时重试仍无法完成，再记录为 project-level scope construction feasibility
  风险，并判断是否需要向用户确认 FastAPI 的 project-level test-suite scope 是否应
  限定为项目主测试目录 `tests/`。

`bugsinpy_fastapi_1` 长时 P2P-broad 重试结果：

- 在保持同一边界的情况下再次执行完整 repo test discovery / project-level
  P2P-broad construction。
- 第二次执行窗口扩大到约 30 分钟，仍未完成并未生成
  `data/p2p_scopes/bugsinpy_fastapi_1_p2p_broad.json`。
- 输出目录仅留下 `compat_shim` 辅助目录，没有可用于主实验的 P2P manifest。
- 因此，`bugsinpy_fastapi_1` 目前不能被标记为 `p2p_broad_main_included = true`。

当前需要确认的边界问题：

- FastAPI 项目存在大量可发现 Python 测试/示例测试文件；完整 repo discovery
  在当前 pipeline 下两次超时。
- 若把 project-level P2P-broad scope 定义为 FastAPI 主测试目录 `tests/`，可以继续
  尝试构造 `bugsinpy_fastapi_1` 的主实验范围，但这需要明确写入 scope policy，
  防止被理解为事后缩小测试范围。
- 若不允许该 scope policy，则应将 `bugsinpy_fastapi_1` 标记为
  `blocked_feasibility_case` 或 `project_level_scope_timeout`，并转向下一个候选任务。

## 28. 2026-06-12 current-turn progress sync

本轮 Inspect：

- Git 状态：`main...origin/main`，仅
  `docs/plans/current_plan_zh.md` 存在未提交进度记录。
- 已读取当前计划、README、`docs/INDEX.md`、工程经验文档和最近 outputs。
- 已确认当前计划的下一步停在 `bugsinpy_fastapi_1` scope policy 确认门。

本轮无 API 审计：

- 已运行
  `python scripts/audit_execution_readiness.py --out-json outputs/readiness_audit/latest.json --out-md outputs/readiness_audit/latest.md`。
- 结果：no-API ready = yes；local API config/model selection ready = yes；
  overall_ready_for_real_api = yes。
- 已运行
  `python scripts/audit_ai_plan_progress.py --out-json outputs/plan_progress/latest.json --out-md outputs/plan_progress/latest.md`。
- 结果：14 个历史执行阶段均为 complete；prompt-only positive claim 仍为 no；
  tool-augmented paper claim 为 yes。

当前阻塞：

- `bugsinpy_fastapi_1` 的 F2P oracle 清楚，但 full-repo project-level
  P2P-broad construction 两次超时，未生成 manifest。
- 是否允许将 FastAPI 的 project-level P2P scope 定义为项目主测试目录 `tests/`
  是实验边界决策，不能由执行代理私自决定。

需要用户确认：

1. 允许为 FastAPI 写入明确 scope policy：project-level P2P-broad 仅限定到
   FastAPI 主测试目录 `tests/`，然后继续尝试 `bugsinpy_fastapi_1`；
2. 或将 `bugsinpy_fastapi_1` 记录为 `project_level_scope_timeout` /
   `blocked_feasibility_case`，并转向下一个候选任务。

## 29. 2026-06-12 official-test-root scope policy decision

用户确认：

- 选择第 1 个方向。
- 允许 `bugsinpy_fastapi_1` 继续使用 official-test-root project-level
  P2P-broad scope。
- 对 FastAPI，scope root 为项目主测试目录 `tests/`。

通用 policy：

- 这不是 FastAPI 特判，也不是因为 FastAPI 太慢而随意缩小测试范围。
- 当 full-repo discovery 因仓库根目录范围过大连续超时，且项目存在明确的官方测试根目录时，
  允许将 project-level P2P-broad scope 定义为该项目的官方测试根目录集合。
- 对 Python 项目，官方测试根目录通常是项目主 `tests/` 目录，或项目配置中声明的测试根目录。
- 该 policy 不能降级为 task-file-level P2P；不能只选择当前 bug 相关测试文件。

FastAPI 决策：

- `bugsinpy_fastapi_1` 的 full-repo discovery 已两次超时，且未生成 manifest。
- 允许继续从 `tests/` 构造 official-test-root project-level P2P-broad。
- manifest 必须记录：
  - `p2p_scope_type = project_level_official_test_root`；
  - `p2p_scope_roots = ["tests/"]`；
  - full-repo discovery attempted = true；
  - full-repo attempts = 2；
  - full-repo status = timeout；
  - policy reason = `full_repo_project_level_discovery_timeout`；
  - `is_task_file_level = false`；
  - `is_project_official_test_root = true`。

本轮执行边界：

- 不允许 test-fixture shim；
- 不允许 task-file-level 降级；
- 不改 FastAPI source 或 tests；
- official test-root collection budget 为 10-15 分钟量级；
- scope construction 总预算为 45-60 分钟量级；
- 稳定性运行次数仍为 3；
- main cohort 门槛仍为 `p2p_broad_size >= 3`。

验收条件：

- `data/p2p_scopes/bugsinpy_fastapi_1_p2p_broad.json` 生成；
- manifest 记录 official-test-root policy；
- `p2p_broad_size >= 3`；
- reference patch 通过 F2P 和 P2P-broad；
- candidate labels 能在 F2P + P2P-broad 下重新验证；
- cohort registry 中标注 `p2p_scope_type = project_level_official_test_root`。

失败处理：

- 如果 `tests/` scope 仍 collection timeout，记录
  `pending_blocked_official_test_root_timeout`。
- 如果 scope 完成但 `p2p_broad_size < 3`，记录
  `completed_insufficient_p2p_broad`。
- 如果 reference patch 不能通过 P2P-broad，记录对应 validation failure。
- 任何失败都不继续无限重试，转向下一个候选任务。

执行结果：

- 已新增通用 policy 文档：
  `docs/experiments/p2p_scope_policy.md`。
- 已扩展 `scripts/build_pass_to_pass_scope.py`：
  - `--scope-type` 支持 `project_level_official_test_root`；
  - manifest 支持记录 `p2p_scope_roots`、`full_repo_discovery`、
    `scope_policy` 和 `main_experiment_eligibility`。
- 第一次 official-root 构造暴露执行链路 bug：
  `static_source_segments` 在 `--test-path tests` 时仍尝试读取目录本身，
  触发 `PermissionError`。
- 已修复该执行链路 bug：当 `test_path` 是目录时，按已收集 nodeid 的测试文件读取源码片段。
- 修复后重跑 FastAPI `tests/` official-root scope 构造；该运行达到 60 分钟预算仍未完成，
  未生成 `data/p2p_scopes/bugsinpy_fastapi_1_p2p_broad.json`。
- 已终止本轮 FastAPI scope 构造残留进程；未触碰其他项目进程。

最终状态：

- `bugsinpy_fastapi_1` 记录为
  `pending_blocked_official_test_root_timeout`。
- 新增结构化 timeout 记录：
  `data/p2p_scopes/bugsinpy_fastapi_1_official_test_root_timeout.json`。
- 新增实验记录：
  `docs/experiments/fastapi1_scope_probe.md`。
- `bugsinpy_fastapi_1` 不进入 `p2p_broad_main`。
- 原因：official-test-root scope 未生成 manifest，无法证明
  `p2p_broad_size >= 3`，也无法做 F2P + P2P-broad candidate revalidation。

下一步：

- 转向下一个 broader BugsInPy 候选任务。
- 优先选择 metadata-level screening 中的低摩擦 pytest/unittest 任务，例如
  `bugsinpy_fastapi_2` 或 `bugsinpy_sanic_*`，但开始前仍需先执行 Inspect 和记录本轮边界。

本轮最小验证：

- `python -m py_compile scripts\build_pass_to_pass_scope.py` 通过。
- `data/cohorts/task_cohort_registry.json` JSON 解析通过。
- `data/p2p_scopes/bugsinpy_fastapi_1_official_test_root_timeout.json` JSON 解析通过。
- registry 中 `bugsinpy_fastapi_1` 唯一，状态为
  `pending_blocked_official_test_root_timeout`，`p2p_broad_main_included = false`。
- `git diff --check` 无空白错误，仅有 Windows 换行提示。
