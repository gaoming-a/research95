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

## 31. 2026-06-12 next candidate feasibility: scrapy_1

同步状态：

- 上一轮 `bugsinpy_fastapi_2` 与 `bugsinpy_sanic_1` 结果已提交并 push 到
  GitHub：`ea53435 docs: record fastapi2 sanic1 feasibility`。
- 当前 Git 状态：`main...origin/main`，工作区干净。

候选选择：

- 转向 broader pool 中的 `bugsinpy_scrapy_1`。
- 理由：
  - 非 FastAPI、非 Sanic；
  - metadata-level screening 中为 unittest 候选；
  - 目标测试聚焦 `tests/test_spidermiddleware_offsite.py`；
  - bug patch 只涉及 `scrapy/spidermiddlewares/offsite.py` 的
    `allowed_domains` URL/None 过滤逻辑。

元数据：

- project = `scrapy`；
- buggy commit = `c57512fa669e6f6b1b766a7639206a380f0d10ce`；
- fixed commit = `9d9dea0d69709ef0f7aef67ddba1bd7bda25d273`；
- F2P commands:
  - `python -m unittest -q tests.test_spidermiddleware_offsite.TestOffsiteMiddleware4._get_spiderargs`；
  - `python -m unittest -q tests.test_spidermiddleware_offsite.TestOffsiteMiddleware4.test_process_spider_output`。

本轮小目标：

1. 准备 `bugsinpy_scrapy_1` retained buggy/fixed checkout。
2. 尝试最小 F2P probe。
3. 如果缺依赖，只安装目标 F2P 所需的 declared dependency subset 到 ignored
   isolated venv，并记录 dependency audit。
4. 如果 F2P 清楚，再判断是否进入 project-level P2P-broad construction。

执行边界：

- 不安装全局依赖；
- 不全量安装 requirements，除非最小 probe 证明必须且依赖边界清晰；
- 不修改 Scrapy source/test fixture；
- 若遇到 native build、外部服务、网络、或 unclear compatibility shim 需求，先记录 blocker；
- unittest task 不能降级成单个 task-file P2P main evidence。

执行结果：

- buggy/fixed checkout 已成功创建到外部 retained workspace：
  `D:/mgao/code/research/data/real_bugs/bugsinpy_workspace/scrapy_1`。
- 初始 F2P probe 在 buggy/fixed 上均因缺少 `twisted` 失败：
  `ModuleNotFoundError: No module named 'twisted'`。
- 已创建 ignored isolated venv：
  `outputs/envs/scrapy1_p2p_py311`。
- 尝试只安装目标 F2P 所需的声明依赖子集时，
  `Twisted==20.3.0` 构建失败；失败点是 `twisted.test.raiser` C extension，
  当前环境缺少 Microsoft Visual C++ 14.0+ build tools。
- 这属于依赖/native build 阻塞。未替换 Twisted 版本，未 stub Twisted，
  未修改 Scrapy source/test fixture，也未降级到 task-file P2P。

最终状态：

- `bugsinpy_scrapy_1` 记录为 `blocked_dependency_native_build`。
- 新增结构化记录：
  `data/p2p_scopes/bugsinpy_scrapy_1_dependency_blocker.json`。
- 新增实验记录：
  `docs/experiments/scrapy1_feasibility.md`。
- `bugsinpy_scrapy_1` 不进入 `p2p_broad_main`。

下一步：

- 暂停 Scrapy 系列候选，避免重复撞到同一 Twisted 20.3.0 native build
  blocker。
- 转向 broader pool 中非 FastAPI、非 Sanic、非 Scrapy 的低摩擦候选。
  优先检查 `bugsinpy_youtube-dl_1` 这类 utility unittest 任务；
  开始前必须先同步本轮 GitHub 记录，并在计划中写明下一轮边界。

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

## 32. 2026-06-12 next candidate feasibility: youtube-dl_1

同步状态：

- `bugsinpy_scrapy_1` dependency/native build blocker 已提交并 push 到 GitHub：
  `90475d0 docs: record scrapy dependency blocker`。
- 当前 Git 状态：`main...origin/main`，工作区干净。

候选选择：

- 转向 broader pool 中的 `bugsinpy_youtube-dl_1`。
- 理由：
  - 非 FastAPI、非 Sanic、非 Scrapy；
  - metadata-level screening 中为 unittest 候选；
  - 目标测试为 utility 逻辑测试，低外部服务/网络风险；
  - bug patch 只涉及 `youtube_dl/utils.py` 中 `_match_one` 对布尔值的
    unary operator 语义。

元数据：

- project = `youtube-dl`；
- buggy commit = `99036a1298089068dcf80c0985bfcc3f8c24f281`；
- fixed commit = `1cc47c667419e0eadc0a6989256ab7b276852adf`；
- F2P command:
  - `python -m unittest -q test.test_utils.TestUtil.test_match_str`。

本轮小目标：

1. 准备 `bugsinpy_youtube-dl_1` retained buggy/fixed checkout。
2. 运行最小 F2P probe。
3. 如果 F2P 清楚，再尝试 project-level unittest P2P-broad construction。
4. 若 project-level scope 完成且 `p2p_broad_size >= 3`，再进入 reference
   patch 与 candidate label 验证；否则记录 blocker 或 insufficient scope。

执行边界：

- 不安装全局依赖；
- 不调用真实 API；
- 不修改 youtube-dl source/test fixture；
- 不使用网络测试或外部服务作为 P2P 主证据；
- 如果 dependency、Python 版本兼容、或 unittest discovery 边界不清楚，先记录
  blocker，不做 task-file P2P main downgrade。

验收条件：

- F2P probe 明确 buggy fail / fixed pass；
- project-level P2P-broad manifest 生成并记录 scope；
- `p2p_broad_size >= 3`；
- registry 中只在上述条件满足后才允许 `p2p_broad_main_included = true`。

并行执行策略更新：

- 用户要求加入并行操作后，本轮允许并行执行：
  - metadata-level candidate inspect；
  - 2-3 个候选的 checkout；
  - 2-3 个候选的最小 F2P probe。
- 仍必须串行执行：
  - 每次只允许 1 个候选进入 project-level P2P-broad construction；
  - registry / README / INDEX / experience / current plan 更新；
  - commit 和 push。
- 原因：F2P 和 checkout 的等待时间可以压缩，但 project-level P2P-broad 是主证据，
  并行运行会让 timeout、资源竞争和残留进程归因不干净。

当前 Inspect：

- `bugsinpy_tornado_1` buggy checkout 已在用户中断前创建到
  `D:/mgao/code/research/data/real_bugs/bugsinpy_workspace/tornado_1/buggy`。
- fixed checkout 尚未创建。
- buggy checkout 内部 Git dirty 状态来自 BugsInPy 注入测试/元数据文件，不属于
  research95 repo 修改。
- 候选池重筛已生成 ignored outputs：
  `outputs/candidate_pool_rescreen/parallel_latest.*`。
- 下一步：并行准备 Tornado fixed checkout 与 Tornado 后续候选元数据/F2P队列；
  但先同步本计划更新到 GitHub。

执行进展：

- `bugsinpy_tornado_1` fixed checkout 已创建成功。
- 直接运行 buggy F2P 时先失败在 Windows/Python 3.11 默认 Proactor event loop
  的 `add_reader` 未实现；这不是目标 bug oracle。
- 使用 Windows selector event loop policy 后，F2P oracle 明确：
  - buggy checkout: `WebSocketHandler.set_nodelay` 访问 `self.stream`，
    触发 `AssertionError`，测试最终得到 `None != "hello"`；
  - fixed checkout: 同一测试通过。
- 该兼容层属于 Windows 下 Tornado 本地测试服务器运行时 policy，不修改 Tornado
  source/test fixture，也不接入外部网络服务。
- 已将该 policy 加入 `scripts/build_pass_to_pass_scope.py` 的通用 compat shim，
  使后续 project-level unittest P2P-broad 与 F2P probe 使用同一运行边界。

下一步：

- 先验证并同步 compat shim 修改。
- 然后对 `bugsinpy_tornado_1` 启动单任务 project-level unittest
  P2P-broad construction。

Project-level P2P attempt：

- 已运行 `bugsinpy_tornado_1` project-level unittest P2P-broad construction：
  - discovery root = `tornado/test`；
  - pattern = `*_test.py`；
  - fail-to-pass oracle =
    `tornado.test.websocket_test.WebSocketTest.test_nodelay`；
  - runs = 3；
  - batch-first dynamic stability run。
- 该运行达到 40 分钟预算仍未完成，未生成
  `data/p2p_scopes/bugsinpy_tornado_1_p2p_broad.json`。
- 输出目录仅包含 `compat_shim`，说明未到达可用 manifest/test-record 阶段。
- 清理时观察到子进程停在
  `tornado.test.iostream_test.TestIOStreamSSLContext.test_future_interface`。
- 已终止本轮 Tornado P2P 构造残留进程，并确认无相关 Python 进程残留。

最终状态：

- `bugsinpy_tornado_1` 记录为
  `pending_blocked_project_level_unittest_scope_timeout`。
- 新增结构化 timeout 记录：
  `data/p2p_scopes/bugsinpy_tornado_1_project_level_timeout.json`。
- 新增实验记录：
  `docs/experiments/tornado1_feasibility.md`。
- `bugsinpy_tornado_1` 不进入 `p2p_broad_main`。

下一步：

- 继续并行筛选候选，但不再对 Tornado websocket/iostream-heavy 项目级 scope
  做长时间重复尝试。
- 优先选择已有 metadata 中更偏纯函数/短测试的候选，例如
  `bugsinpy_tornado_9` 的 `httputil.url_concat`。

## 34. 2026-06-12 next candidate feasibility: tornado_9

同步状态：

- `bugsinpy_tornado_1` project-level unittest scope timeout 已提交并 push 到
  GitHub：`bbfd234 docs: record tornado feasibility timeout`。
- 当前 Git 状态：`main...origin/main`，工作区干净。

候选选择：

- 转向 `bugsinpy_tornado_9`。
- 理由：
  - 非 websocket/iostream-heavy F2P；
  - F2P 目标为 `httputil.url_concat` 纯函数行为；
  - bug patch 只是在 `args is None` 时直接返回原 URL；
  - 相比 `tornado_1`，目标 oracle 对本地 socket/server 依赖更低。

元数据：

- project = `tornado`；
- buggy commit = `c9d2a3fa573987629ad576e991c2f3b65f4daab4`；
- fixed commit = `86cc31f52992fb9d11f92de6fd5496842fea2265`；
- F2P command:
  - `python -m unittest -q tornado.test.httputil_test.TestUrlConcat.test_url_concat_none_params`。

本轮小目标：

1. 并行准备 `bugsinpy_tornado_9` buggy/fixed checkout。
2. 运行最小 F2P probe。
3. 如果 F2P 清楚，优先尝试 project-level unittest P2P-broad construction。
4. 如果完整 Tornado project-level scope 再次停在 socket/SSL/iostream-heavy
   区域，记录共享 scope 风险，不降级成 task-file main evidence。

执行边界：

- 不安装全局依赖；
- 不执行 `setup.sh`；
- 不调用真实 API；
- 不修改 Tornado source/test fixture；
- 允许通用 Windows selector event loop policy；
- 允许 Tornado 本地 loop/server 测试，但不允许外部网络服务；
- project-level P2P 一次只跑 `tornado_9` 一个候选。

验收条件：

- F2P probe 明确 buggy fail / fixed pass；
- project-level P2P-broad manifest 生成；
- `p2p_broad_size >= 3`；
- registry 中只在上述条件满足后才允许 `p2p_broad_main_included = true`。

执行结果：

- 已串行启动 `bugsinpy_ansible_2` buggy checkout。
- checkout 运行超过 13 分钟仍未完成，且 retained checkout 中未写出
  `bugsinpy_run_test.sh` marker。
- 已终止 hanging checkout 进程，并删除本轮产生的不完整
  `D:/mgao/code/research/data/real_bugs/bugsinpy_workspace/ansible_2`
  retained workspace。
- 因 checkout 未完成，未执行 fixed checkout、F2P probe 或 project-level P2P。

最终状态：

- `bugsinpy_ansible_2` 记录为 `pending_blocked_checkout_timeout`。
- 新增结构化 timeout 记录：
  `data/p2p_scopes/bugsinpy_ansible_2_checkout_timeout.json`。
- 新增实验记录：
  `docs/experiments/ansible2_feasibility.md`。
- `bugsinpy_ansible_2` 不进入 `p2p_broad_main`。

下一步：

- 不继续优先尝试 Ansible 大仓库 checkout。
- 候选筛选转向更小项目或已知 checkout 成本低的项目；仍允许并行做 metadata
  inspect，但同一 task 的 buggy/fixed checkout 保持串行。

## 36. 2026-06-12 next candidate feasibility: matplotlib_1

同步状态：

- `bugsinpy_ansible_2` checkout timeout 已提交并 push 到 GitHub：
  `9505155 docs: record ansible checkout timeout`。
- 当前 Git 状态：`main...origin/main`，工作区干净。

候选选择：

- 转向 `bugsinpy_matplotlib_1`。
- 理由：
  - 当前 broader candidate pool 在排除 FastAPI/Sanic/Scrapy/youtube-dl/Tornado、
    Luigi 和 Ansible 后，剩余候选集中在 Matplotlib；
  - F2P 目标明确为 `lib/matplotlib/tests/test_bbox_tight.py::test_noop_tight_bbox`；
  - patch 涉及 tight-bbox renderer draw no-op 逻辑。

元数据：

- project = `matplotlib`；
- buggy commit = `c404d1f716e8aaefd4d7371ff49673e9c1f7f07c`；
- fixed commit = `5324adaec6a7fd3d78dea7b28451d5f6e95392a6`；
- F2P command:
  - `pytest lib/matplotlib/tests/test_bbox_tight.py::test_noop_tight_bbox`。
- `setup.sh` 包含：
  - `pip install Cython`；
  - `python -mpip install -ve .`。

本轮小目标：

1. 串行准备 `bugsinpy_matplotlib_1` buggy/fixed checkout。
2. 尝试最小 F2P import/probe。
3. 如果需要依赖，只允许在 ignored isolated venv 中安装目标 F2P 所需的
   declared dependency subset。
4. 如果 editable install 或 import 明确需要 native build/toolchain，记录 blocker，
   不替换依赖、不改 source/test fixture。

执行边界：

- 不安装全局依赖；
- 不执行全局 `setup.sh`；
- 不调用真实 API；
- 不修改 Matplotlib source/test fixture；
- 不把 task-file P2P 降级成 main evidence；
- 不把本机已安装的 unrelated Matplotlib package 当作 checkout evidence；
- 若本地 native build、GUI/backend、font/data asset 或外部 toolchain 边界不清楚，
  先记录 blocker。

验收条件：

- F2P probe 明确 buggy fail / fixed pass；
- 或明确记录 dependency/native build/import blocker；
- 只有在 F2P 清楚后才考虑 project-level P2P-broad。

执行结果：

- `bugsinpy_matplotlib_1` buggy/fixed checkout 均完成到 BugsInPy marker 文件写出，
  但 checkout 成本较高。
- 使用 `PYTHONPATH=checkout/lib` 和 `MPLBACKEND=Agg` 做最小 F2P probe。
- buggy checkout 中未找到预期路径
  `lib/matplotlib/tests/test_bbox_tight.py`，因此 buggy oracle 未建立。
- fixed checkout 中目标测试文件存在，但导入 checkout 内 Matplotlib 时失败：
  `ImportError: cannot import name 'ft2font'`。
- 该失败说明目标测试需要 Matplotlib compiled extension；`setup.sh` 的
  editable install/Cython 路径属于本轮未批准的 native/build 边界。

最终状态：

- `bugsinpy_matplotlib_1` 记录为 `blocked_native_extension_import`。
- 新增结构化 blocker：
  `data/p2p_scopes/bugsinpy_matplotlib_1_import_blocker.json`。
- 新增实验记录：
  `docs/experiments/matplotlib1_feasibility.md`。
- 因 F2P 未建立，未尝试 project-level P2P-broad。

下一步：

- 当前 metadata pool 中剩余候选主要仍是 Matplotlib 系列；在未确认 native build
  / editable install 边界前，不继续重复 Matplotlib 候选。
- 需要重新扩大候选池或调整项目选择策略；若下一轮继续，应先 rerun broader
  screening 并明确跳过已确认项目级风险的项目。

## 37. 2026-06-12 candidate pool boundary after parallel sweep

同步状态：

- `bugsinpy_matplotlib_1` native/import blocker 已提交并 push 到 GitHub：
  `48413f7 docs: record matplotlib import blocker`。
- 当前 Git 状态：`main...origin/main`，工作区干净。

本轮 Inspect：

- 已检查 `outputs/candidate_pool_rescreen/parallel_latest.json`。
- 在排除已确认项目级风险或已处理项目后，`promising_candidates` 中没有新的项目：
  - FastAPI：official-root scope timeout；
  - Sanic：project-level scope timeout；
  - Scrapy：Twisted native build blocker；
  - youtube-dl：project-level unittest discovery timeout；
  - Tornado：shared project-level unittest scope timeout；
  - Luigi：shared large project-level suite blocker；
  - Ansible：checkout timeout；
  - Matplotlib：native extension import blocker；
  - httpie/tqdm/PySnooper/Black/Cookiecutter：已处理或已有明确 blocker/main status。
- `all_candidates` 中剩余可见项目主要为：
  - Keras：metadata blocker = `heavy_ml_dependency`；
  - Pandas：metadata blocker = `native_build_dependency`，部分还含
    `network_reference_in_metadata`。

当前边界问题：

- 如果继续，需要改变候选策略或实验边界：
  1. 放宽 metadata filter，尝试 Keras/Pandas 这类 heavy/native 候选；
  2. 允许 isolated native/editable build，用于 Matplotlib/Pandas 等项目；
  3. 停止继续补 BugsInPy 主任务，转向整理当前 7 个主任务与 blocked audit；
  4. 寻找 BugsInPy 之外的新 benchmark/source。
- 这些都不是当前计划内的“继续执行”细节，而是实验边界决策，不能由执行代理私自决定。

需要用户确认：

- 下一步采用哪一种候选/构建边界。

执行进展：

- 初次并行创建 `bugsinpy_tornado_9` buggy/fixed checkout 时，fixed checkout
  返回 `mv: cannot stat ...httputil_test.py`。
- 原因诊断：BugsInPy checkout 脚本会在 `projects/<project>/bugs/<id>/`
  下临时复制、移动并删除测试/补丁文件；同一 task 的 buggy/fixed checkout
  并行会争用同一临时资源。
- 已删除不完整的 fixed checkout，并串行重建 fixed checkout；重建后目标测试方法存在。
- 更新并行边界：不同 task 的 metadata / checkout 可并行；同一 task 的 buggy/fixed
  checkout 必须串行。
- 在通用 compat shim 下，F2P oracle 明确：
  - buggy checkout: `url_concat(..., None)` 抛出 `TypeError`；
  - fixed checkout: 同一测试通过。

下一步：

- 对 `bugsinpy_tornado_9` 启动单任务 project-level unittest P2P-broad
  construction。

Project-level P2P attempt：

- 已运行 `bugsinpy_tornado_9` project-level unittest P2P-broad construction：
  - discovery root = `tornado/test`；
  - pattern = `*_test.py`；
  - fail-to-pass oracle =
    `tornado.test.httputil_test.TestUrlConcat.test_url_concat_none_params`；
  - runs = 3；
  - per-test timeout = 8 秒；
  - 未启用 batch-first，避免 batch 子进程长时间遮蔽单测 timeout。
- 该运行在用户中断后仍在后台继续运行；后续观察确认父进程运行时间远超本轮预算，
  且未生成 `data/p2p_scopes/bugsinpy_tornado_9_p2p_broad.json`。
- 输出目录仅包含 `compat_shim`，说明未到达可用 manifest/test-record 阶段。
- 观察到 active tests 包括：
  - `tornado.test.gen_test.GenCoroutineTest.test_sync_return`；
  - `tornado.test.gen_test.GenEngineTest.test_moment`。
- 已终止本轮 Tornado_9 P2P 构造残留进程，并确认无相关 Python 进程残留。

最终状态：

- `bugsinpy_tornado_9` 记录为
  `pending_blocked_shared_project_level_unittest_scope_timeout`。
- 新增结构化 timeout 记录：
  `data/p2p_scopes/bugsinpy_tornado_9_project_level_timeout.json`。
- 新增实验记录：
  `docs/experiments/tornado9_feasibility.md`。
- `bugsinpy_tornado_9` 不进入 `p2p_broad_main`。

下一步：

- 不继续对 Tornado 项目级 unittest scope 做长时间重复尝试。
- 并行筛选应转向非 FastAPI、非 Sanic、非 Scrapy、非 youtube-dl、非 Tornado
  的候选项目，或只做 metadata/F2P 层面的短探针。

## 35. 2026-06-12 next candidate feasibility: ansible_2

同步状态：

- `bugsinpy_tornado_9` shared Tornado project-level scope timeout 已提交并
  push 到 GitHub：`c9516f0 docs: record tornado9 feasibility timeout`。
- 当前 Git 状态：`main...origin/main`，工作区干净。

候选选择：

- 转向 `bugsinpy_ansible_2`。
- 理由：
  - 非 FastAPI、非 Sanic、非 Scrapy、非 youtube-dl、非 Tornado；
  - F2P 目标为 `test/units/utils/test_version.py` 的版本比较 unit tests；
  - patch 只涉及 `lib/ansible/utils/version.py` 中 `_Alpha` 和 `_Numeric`
    的比较运算语义；
  - 相比 Ansible 其他候选，目标更偏纯函数/短测试。

元数据：

- project = `ansible`；
- buggy commit = `de59b17c7f69d5cfb72479b71776cc8b97e29a6b`；
- fixed commit = `5b9418c06ca6d51507468124250bb58046886be6`；
- BugsInPy pythonpath = `ansible/build/lib/`；
- F2P commands:
  - `pytest test/units/utils/test_version.py::test_alpha`；
  - `pytest test/units/utils/test_version.py::test_numeric`。

本轮小目标：

1. 串行准备 `bugsinpy_ansible_2` buggy/fixed checkout。不得并行同一 task 的
   buggy/fixed checkout。
2. 使用 checkout 声明的 `PYTHONPATH` 运行最小 F2P probe。
3. 如果缺依赖，只安装目标 F2P 所需的 declared dependency subset 到 ignored
   isolated venv，并记录 dependency audit。
4. 如果 F2P 清楚，再判断 project-level pytest P2P-broad construction 是否可行。

执行边界：

- 不安装全局依赖；
- 不执行 `setup.sh` 中的 `python setup.py install` 或全局 pip；
- 不调用真实 API；
- 不修改 Ansible source/test fixture；
- 不把 task-file P2P 降级成 main evidence；
- 如果 Ansible project-level scope 明显进入重依赖、外部服务或不可控长时测试，
  先记录 blocker。

验收条件：

- F2P probe 明确 buggy fail / fixed pass；
- project-level P2P-broad manifest 生成；
- `p2p_broad_size >= 3`；
- registry 中只在上述条件满足后才允许 `p2p_broad_main_included = true`。

执行结果：

- buggy/fixed checkout 已成功创建到外部 retained workspace：
  `D:/mgao/code/research/data/real_bugs/bugsinpy_workspace/youtube-dl_1`。
- F2P probe 明确：
  - buggy checkout:
    `test.test_utils.TestUtil.test_match_str` 失败，
    `match_str('is_live', {'is_live': False})` 返回 `True`；
  - fixed checkout: 同一测试通过。
- 已尝试 project-level unittest P2P-broad construction：
  - discovery root = `test/`；
  - pattern = `test_*.py`；
  - fail-to-pass oracle = `test.test_utils.TestUtil.test_match_str`；
  - 静态排除明显 network/external execution token；
  - batch-first dynamic stability run。
- 该运行达到 30 分钟预算仍未完成，未生成
  `data/p2p_scopes/bugsinpy_youtube-dl_1_p2p_broad.json`。
- 输出目录仅包含 `compat_shim`，说明未到达可用 manifest/test-record 阶段。
- 已确认无 `bugsinpy_youtube-dl_1` 相关残留 Python 进程。

最终状态：

- `bugsinpy_youtube-dl_1` 记录为
  `pending_blocked_project_level_unittest_discovery_timeout`。
- 新增结构化 timeout 记录：
  `data/p2p_scopes/bugsinpy_youtube-dl_1_project_level_timeout.json`。
- 新增实验记录：
  `docs/experiments/youtubedl1_feasibility.md`。
- `bugsinpy_youtube-dl_1` 不进入 `p2p_broad_main`。

下一步：

- 转向 broader pool 中下一个非 FastAPI、非 Sanic、非 Scrapy、非
  youtube-dl 的候选任务。
- 优先检查 `bugsinpy_tornado_1`，但其 websocket 测试可能涉及本地网络；
  开始前必须先 Inspect 其 patch、test 和 dependency 边界。

## 33. 2026-06-12 next candidate feasibility: tornado_1

同步状态：

- `bugsinpy_youtube-dl_1` project-level unittest discovery timeout 已提交并
  push 到 GitHub：`2e2b876 docs: record youtube-dl feasibility timeout`。
- 当前 Git 状态：`main...origin/main`，工作区干净。

候选选择：

- 转向 broader pool 中的 `bugsinpy_tornado_1`。
- 理由：
  - 非 FastAPI、非 Sanic、非 Scrapy、非 youtube-dl；
  - metadata-level screening 中为 unittest 候选；
  - F2P 目标明确为 Tornado websocket no-delay 行为；
  - bug patch 只涉及 `tornado/websocket.py` 中 no-delay 调用路径和协议抽象。

元数据：

- project = `tornado`；
- buggy commit = `6a5a0bfa370b6c0d3dbbf9589a560a98202d2baa`；
- fixed commit = `4677c54cc18bbfbdf0f4dadf11610fab6203fd63`；
- F2P command:
  - `python -m unittest -q tornado.test.websocket_test.WebSocketTest.test_nodelay`。

本轮小目标：

1. 准备 `bugsinpy_tornado_1` retained buggy/fixed checkout。
2. 运行最小 F2P probe。
3. 如果 F2P 清楚，再尝试 project-level unittest P2P-broad construction。
4. 若 project-level scope 完成且 `p2p_broad_size >= 3`，再进入 reference
   patch 与 candidate label 验证；否则记录 blocker 或 insufficient scope。

执行边界：

- 不安装全局依赖；
- 不执行 `setup.sh` 中的全局 pip 命令；
- 不调用真实 API；
- 不修改 Tornado source/test fixture；
- 允许 Tornado 测试框架内部启动本地 loop/server 进行 websocket/http 测试；
  不允许依赖外部网络服务；
- 如果 dependency、Python 版本兼容、或 unittest discovery 边界不清楚，先记录
  blocker，不做 task-file P2P main downgrade。

验收条件：

- F2P probe 明确 buggy fail / fixed pass；
- project-level P2P-broad manifest 生成并记录 scope；
- `p2p_broad_size >= 3`；
- registry 中只在上述条件满足后才允许 `p2p_broad_main_included = true`。

## 38. 2026-06-12 final roadmap advice extraction

同步状态：

- 当前 Git 状态为 `main...origin/main`，工作区在本轮修改前干净。
- 本轮只处理用户提供的研究路线建议，不运行真实 API，不新增实验数据，不修改
  candidate labels。

本轮小目标：

1. 对照附件建议、`docs/plans/final_paper_roadmap_zh.md`、当前 cohort 和论文草稿；
2. 只提取与现有最终路线不冲突、不重复的增量内容；
3. 同步最终路线图、当前计划、索引、README 和工程经验记录；
4. 审查 diff，确认没有引入新的实验 claim 或错误 cohort 口径；
5. 提交并 push 到 GitHub。

执行边界：

- 不重写既有 E0-E7 设计；
- 不重复添加已有 visible/hidden、tool-only baseline、Candidate Patches 标题和
  规模分档；
- 不把 “30-50 bugs / 100-180 patches” 写成无条件硬门槛；
- 不把当前 retained validation summary 写成 realistic hidden-evaluator-free
  主结果；
- 不继续 BugsInPy 扩量，除非先解决候选池/构建边界决策。

验收条件：

- `final_paper_roadmap_zh.md` 新增内容明确标注为增量修订；
- README 和 `docs/INDEX.md` 指向更新后的最终路线；
- `engineering_notes.md` 记录本轮避免冲突和重复的处理原则；
- Git diff 只包含本轮文档更新；
- 成功 commit 并同步远端。

执行结果：

- `docs/plans/final_paper_roadmap_zh.md` 新增第 18 节，只记录非重复增量：
  Evidence Visibility Curve、FACR/Evidence Gain、分阶段 evidence ablation、
  realistic tool-only 边界、扩量边界和旧论文/cohort 口径修正。
- README 已把项目入口标题和主研究方向同步为
  `Evidence Visibility for Candidate Patch Verification`，并弱化
  AI-generated correct patch 的硬目标地位。
- `docs/INDEX.md` 已索引第 18 节增量内容。
- `docs/experience/engineering_notes.md` 已记录本轮去重原则和未来避免
  oracle-style summary 误用的经验。
- `git diff --check` 通过；当前 diff 只包含上述 5 个文档文件。

## 39. 2026-06-12 EVP-7 protocol pilot freeze

用户决策：

- 现在选择 A：冻结当前 7 个主任务，停止继续盲扫 BugsInPy。
- 不批准 B 作为当前主路线；native/editable build 只能在 A 完成后作为小范围
  targeted probe。
- 不立刻进入 C；外部 benchmark/source 必须等 protocol schema、runner、
  hidden-evaluator 规范、metrics 和 LLM output schema 冻结后再接入。

本轮 Inspect：

- Git 状态：`main...origin/main`，工作区干净。
- 当前 `p2p_broad_main` 仍为 7 个任务 / 4 个项目：
  `httpie_5`、`cookiecutter_1`、`cookiecutter_2`、`cookiecutter_3`、
  `tqdm_9`、`PySnooper_1`、`PySnooper_3`。
- `docs/experiments/patch_evidence_bench_schema.md` 和
  `docs/experiments/leakage_policy.md` 已有长期 schema 与可见/隐藏边界。
- 当前 tracked `data/` 中稳定存在 cohort registry 和 P2P scope manifests；
  候选 patch JSONL 主要仍记录在 ignored `outputs/` 路径和实验报告中，不能直接
  当作最终 tracked EVP-7 candidate schema。

本轮小目标：

1. 正式命名当前冻结集合为 `EVP-7 Protocol Pilot`；
2. 新增可复现 builder，从 tracked registry/P2P manifests 生成：
   - `data/tasks/evp7_tasks.jsonl`；
   - `data/exclusions/blocked_bugsinpy_projects.jsonl`；
3. 新增 `docs/protocol/evidence_visibility_protocol.md`，固化 A 阶段执行边界、
   E0/E2/E4/E6 pilot 范围、G1-G5 gate 和后置扩量规则；
4. 新增 `docs/experiments/evp7_protocol_pilot.md`，记录本轮冻结结果和下一步
   candidate/evidence packet 前置缺口；
5. 更新 `docs/INDEX.md`、README、`engineering_notes.md`；
6. 运行最小验证，确认 manifest 与 registry 一致、JSONL 可解析、无敏感信息；
7. 提交并同步 GitHub。

执行边界：

- 不新增第 8 个 bug；
- 不运行真实 API；
- 不执行新的 checkout、F2P 或 P2P 构造；
- 不生成 E0/E2/E4/E6 packets，直到候选 patch 记录被提升为稳定 tracked
  `evp7_candidates.jsonl`；
- 不从 ignored workdirs 或本地 retained checkout 读取并固化绝对路径；
- 不把 blocked tasks 删除；必须进入 blocker registry。

验收条件：

- `evp7_tasks.jsonl` 中正好 7 条，全部来自 `p2p_broad_main`；
- `blocked_bugsinpy_projects.jsonl` 至少覆盖当前 registry 中所有
  `p2p_broad_main_included=false` 的 blocked/pending/insufficient 任务；
- builder 可重复运行且输出稳定；
- JSONL 解析通过；
- 文档明确：A 阶段是 protocol pilot，不是最终泛化结论。

执行结果：

- 新增 `scripts/build_evp7_protocol_manifests.py`，从 tracked
  `data/cohorts/task_cohort_registry.json` 和 P2P manifests 生成 EVP-7
  task/blocker manifests。
- 已生成：
  - `data/tasks/evp7_tasks.jsonl`：7 条；
  - `data/tasks/evp7_manifest_summary.json`：7 个主任务、4 个项目、registry
    已知 candidate 下界 36；`httpie_5` 缺少 registry candidate count 字段；
  - `data/exclusions/blocked_bugsinpy_projects.jsonl`：27 条 blocked/pending/
    insufficient/appendix-only records。
- 新增 `docs/protocol/evidence_visibility_protocol.md`，定义 Option A、
  E0/E2/E4/E6 pilot、visible/hidden 边界、merge-gate schema 和 G1-G5 gates。
- 新增 `docs/experiments/evp7_protocol_pilot.md`，记录本轮冻结 cohort、
  blocker registry 和 candidate-level schema 前置缺口。
- 已同步更新 README、`docs/INDEX.md`、`docs/plans/final_paper_roadmap_zh.md`
  和 `docs/experience/engineering_notes.md`。

验证结果：

- `python -m py_compile scripts\build_evp7_protocol_manifests.py` 通过。
- `python scripts\build_evp7_protocol_manifests.py --check` 通过。
- JSONL 解析复查通过：
  - `evp7_tasks.jsonl = 7`；
  - `blocked_bugsinpy_projects.jsonl = 27`；
  - summary `candidate_count_known_from_registry = 36`，且
    `candidate_count_missing_in_registry_tasks = [bugsinpy_httpie_5]`。
- 第一次内联 JSONL 解析命令因 PowerShell 换行转义写法报 `SyntaxError`；
  已用 here-string 方式重跑通过，不是数据或脚本问题。
- 当前 `data/tasks` 与 `data/exclusions` 受 ignore 规则影响；提交时必须只对
  本轮 3 个 manifest 文件使用显式 `git add -f`。

下一步：

- 不继续找第 8 个 bug。
- 转入 candidate-level schema：从已有 validated candidate outputs 和实验报告
  生成 tracked `data/patches/evp7_candidates.jsonl`，再判断 E0/E2/E4/E6 是否
  可构造。

## 40. 2026-06-12 EVP-7 candidate schema promotion

同步状态：

- 最新提交 `6d421a2 docs: freeze evp7 protocol pilot` 已 push。
- 当前 Git 状态为 `main...origin/main`，工作区干净。
- 已确认 7 个 EVP-7 任务对应的 candidate JSONL 和 P2P validation JSONL 存在于
  ignored `outputs/` 下：
  - `outputs/httpie5_stability_audit_001/candidates.jsonl`；
  - `outputs/cookiecutter1_candidate_validation_001/candidates.jsonl`；
  - `outputs/cookiecutter2_candidate_validation_001/candidates.jsonl`；
  - `outputs/cookiecutter3_candidate_validation_001/candidates.jsonl`；
  - `outputs/tqdm9_candidate_validation_001/candidates.jsonl`；
  - `outputs/pysnooper1_candidate_validation_001/candidates.jsonl`；
  - `outputs/pysnooper3_candidate_validation_001/candidates.jsonl`。

本轮小目标：

1. 新增可复现 builder，将已有 validated candidate outputs 提升为 tracked
   `data/patches/evp7_candidates.jsonl`；
2. 同步生成 `data/patches/evp7_candidate_summary.json`；
3. 生成只含可见性准备状态的 schema，不生成 E0/E2/E4/E6 evidence packets；
4. 验证 candidate 总数不低于 `evp7_manifest_summary.json` 的 registry 已知
   下界，并固定当前 EVP-7 promoted candidate count；
5. 更新 protocol/experiment/index/readme/engineering notes；
6. 提交并同步 GitHub。

执行边界：

- 不运行真实 API；
- 不重新执行 candidate validation；
- 不读取 raw workdirs 中的源文件；
- 不把本地绝对 workdir、venv command、stdout/stderr 细节写入 tracked
  candidate schema；
- `candidate_type`、`expected_outcome`、`label_with_p2p_broad`、
  `failure_type_label` 等仍属于 evaluator-only，不得进入后续 model-visible
  evidence packets；
- 为避免跨任务 `candidate_0001` 冲突，必须生成全局匿名
  `evp7_candidate_id`。

验收条件：

- `evp7_candidates.jsonl` 正好 42 条；
- 7 个 task 都有 candidate records；
- 每条 record 有全局唯一 `evp7_candidate_id`；
- 每条 record 能关联到 P2P validation label；
- JSONL 解析和 builder `--check` 通过。

执行结果：

- 新增 `scripts/build_evp7_candidate_manifest.py`，从 7 个已验证 candidate
  JSONL 和对应 P2P validation JSONL 生成 tracked candidate manifest。
- 已生成：
  - `data/patches/evp7_candidates.jsonl`：42 条；
  - `data/patches/evp7_candidate_summary.json`：7 个任务、4 个项目、42 个
    candidates。
- 候选分布：
  - `correct_reference = 7`；
  - `partial_fix = 21`；
  - `irrelevant_patch = 7`；
  - `buggy_noop = 7`。
- P2P-broad label 分布：
  - `correct_under_f2p_and_p2p_broad = 7`；
  - `incorrect_issue_not_fixed = 35`。

诊断与修复：

- 第一次运行 candidate builder `--check` 失败，原因是
  `evp7_manifest_summary.json` 原字段把 registry 已知 36 个 candidates
  当成最终候选总数。
- 定位后确认不是 candidate outputs 过宽，而是 `bugsinpy_httpie_5` 在
  `data/cohorts/task_cohort_registry.json` 中缺少
  `collection_summary.candidate_count` 和 label counts。
- 已修复 `scripts/build_evp7_protocol_manifests.py` 的 summary 语义：
  `candidate_count_known_from_registry = 36` 只作为下界，
  `candidate_count_missing_in_registry_tasks = [bugsinpy_httpie_5]` 明确记录
  缺口。
- candidate builder 的验收改为：candidate 总数必须不低于 registry 下界，且
  当前 EVP-7 promoted candidate count 固定为 42。
- 2026-06-12 后续 evidence packet builder 完成后，candidate summary 中的
  `evidence_packet_status` 不再写成 `not_generated`，而是改为
  `managed_by_separate_builder`，避免 candidate builder 越权描述 packet
  生成状态。

验证结果：

- `python -m py_compile scripts\build_evp7_protocol_manifests.py
  scripts\build_evp7_candidate_manifest.py` 通过。
- `python scripts\build_evp7_protocol_manifests.py --check` 通过，summary
  保留 `candidate_count_known_from_registry = 36` 和
  `candidate_count_missing_in_registry_tasks = [bugsinpy_httpie_5]`。
- `python scripts\build_evp7_candidate_manifest.py --check` 通过，summary
  为 42 candidates / 7 tasks / 4 projects。
- JSONL 解析复查通过：
  - `data/tasks/evp7_tasks.jsonl = 7`；
  - `data/exclusions/blocked_bugsinpy_projects.jsonl = 27`；
  - `data/patches/evp7_candidates.jsonl = 42`。
- `git diff --check` 通过；仅出现 Windows CRLF 工作区提示。
- 本轮 diff 的严格敏感信息扫描无命中；第一次宽松 `sk-` 扫描误命中
  `task-level`，已用 `sk-[0-9A-Za-z]{20,}` 规则复查。

下一步：

- 不继续找第 8 个 bug。
- 基于 `data/patches/evp7_candidates.jsonl` 生成 E0/E2/E4/E6 evidence
  packets，先做 E0/E4 completeness 和 leakage audit。
- 在 packet builder 通过泄漏审计前，不运行真实 LLM API。

## 41. 2026-06-12 EVP-7 evidence packet builder and leakage audit

同步状态：

- 上一轮提交 `97e5137 docs: promote evp7 candidate manifest` 已成功 push 到
  GitHub。
- 当前 Git 状态为 `main...origin/main`，工作区干净。
- 已存在 tracked candidate manifest：
  - `data/patches/evp7_candidates.jsonl`：42 条；
  - `data/patches/evp7_candidate_summary.json`：42 candidates / 7 tasks /
    4 projects。

本轮小目标：

1. 新增可复现 builder，从 `data/patches/evp7_candidates.jsonl` 生成
   E0/E2/E4/E6 evidence packet records；
2. 输出 `data/evidence/evp7_evidence_packets.jsonl` 和
   `data/evidence/evp7_evidence_packet_summary.json`；
3. 自动检查 packet 不包含 evaluator-only 字段、final labels、retained oracle
   status、hidden oracle、P2P-broad label 或 construction taxonomy；
4. E0/E2 可完成可见 packet；E4/E6 如果缺少独立可见 test/tool outcome source，
   必须显式标记 incomplete，不得用 hidden/evaluator validation 结果填充；
5. 更新 protocol/experiment/index/readme/engineering notes；
6. 运行最小验证，提交并同步 GitHub。

执行边界：

- 不运行真实 API；
- 不重新执行 candidate validation、F2P、P2P 或 tool runners；
- 不读取 ignored retained checkout 中的源文件；
- 不把 `candidate_type`、`expected_outcome`、`failure_type_label`、
  `label_with_p2p_broad`、`label_retained_oracle`、`hidden_oracles`、
  `validation_summary.retained_oracle_passed` 写入 evidence packets；
- 不把 E4/E6 incomplete 误写成 G1/G5 已通过。

验收条件：

- 正好生成 42 * 4 = 168 条 evidence packet records；
- 每个 `evp7_candidate_id` 都有 E0/E2/E4/E6 四个 records；
- automated leakage audit 通过；
- summary 明确 G1 packet completeness 尚未通过，原因是 E4/E6 缺少独立可见
  outcome/tool evidence source；
- JSONL 解析和 builder `--check` 通过。

执行结果：

- 新增 `scripts/build_evp7_evidence_packets.py`。
- 已生成：
  - `data/evidence/evp7_evidence_packets.jsonl`：168 条；
  - `data/evidence/evp7_evidence_packet_summary.json`。
- evidence level 分布：
  - E0：42 条，complete 42；
  - E2：42 条，complete 42；
  - E4：42 条，complete 0；
  - E6：42 条，complete 0。
- G2 leakage audit 自动检查通过，`leakage_findings_count = 0`。
- G1 packet completeness 明确为 `not_passed`，blocker 是缺少独立可见 test
  outcomes 和 E6 realistic visible tool summaries。
- 发现并修正 candidate summary 的语义问题：`evidence_packet_status` 不能继续
  写 `not_generated`，因为 packet builder 已独立生成 evidence artifacts；已改为
  `managed_by_separate_builder` 并指向
  `data/evidence/evp7_evidence_packets.jsonl`。

验证结果：

- `python -m py_compile scripts\build_evp7_protocol_manifests.py
  scripts\build_evp7_candidate_manifest.py
  scripts\build_evp7_evidence_packets.py` 通过。
- `python scripts\build_evp7_protocol_manifests.py --check` 通过。
- `python scripts\build_evp7_candidate_manifest.py --check` 通过，candidate
  summary 现在记录 `evidence_packet_status = managed_by_separate_builder`。
- `python scripts\build_evp7_evidence_packets.py --check` 通过，summary 为
  168 packets，G2 passed，G1 not_passed。
- JSONL 解析复查通过：
  - `data/patches/evp7_candidates.jsonl = 42`；
  - `data/evidence/evp7_evidence_packets.jsonl = 168`；
  - E0/E2 complete counts = 42/42；
  - E4/E6 complete counts = 0/0。

下一步：

- 不运行真实 LLM API。
- 补齐独立可见 test outcome source 和 realistic visible tool summary source；
- 重新运行 `scripts/build_evp7_evidence_packets.py --check` 和 leakage audit；
- G1/G2 都通过后，再进入 tool-only baselines 和 merge-gate schema dry-run。

## 42. 2026-06-12 EVP-7 independent visible test outcome source

同步状态：

- 本地提交 `04eef23 data: build evp7 evidence packets` 已完成。
- `git push origin main` 因 GitHub HTTPS 443 不可达失败；当前本地
  `main...origin/main [ahead 1]`。
- 工作区在本轮开始时干净。

本轮小目标：

1. 先恢复 GitHub 同步；若网络仍失败，记录为外部同步阻塞但继续推进本地可验证
   artifact。
2. 新增 independent visible test outcome source，不复用 validation JSONL 中的
   retained oracle / hidden P2P outcome。
3. 新增 runner 从 `data/patches/evp7_candidates.jsonl` 读取每个 candidate 的
   `visible_tests`，在已有 candidate workdir 上重新执行这些预先标记为 visible
   的测试，只记录 visible test name、pass/fail/error/timeout 和相对来源。
4. 输出 tracked summary/manifest；如果 runner 只能完成部分任务，必须显式记录
   incomplete，不得把 G1 写成通过。
5. 重新生成 evidence packets，让 E4 使用新的 visible outcome source；E6 仍需
   realistic visible tool summary source，不能自动标 complete。

执行边界：

- 不运行真实 LLM API；
- 不使用 retained oracle outcome、`label_with_p2p_broad`、candidate
  construction taxonomy 或 hidden P2P results 填充 visible evidence；
- 不新增第 8 个 bug；
- 不重新构造 P2P-broad scope；
- 允许只在已有 ignored candidate workdirs 上执行预先声明的 `visible_tests`；
- 如果缺少 workdir、env 或测试命令边界不明，必须记录 incomplete 并停止该任务，
  不做临时兼容层。

验收条件：

- runner 有 dry-run/check 模式，能列出 42 个 candidate 的 visible-test 运行计划；
- 实际运行只产生 model-visible outcome source，不写入 evaluator-only label；
- evidence packet builder 的 leakage audit 仍通过；
- 文档明确 E4 是否达到 complete；E6 在 tool summary source 缺失前仍 incomplete。

执行结果：

- 新增 `scripts/run_evp7_visible_tests.py`。
- dry-run `python scripts\run_evp7_visible_tests.py --check` 通过：
  - 42 个 candidates；
  - 49 个 planned visible test entries；
  - blocked = 0。
- 实际运行 `python scripts\run_evp7_visible_tests.py --run --check --timeout 90`
  完成：
  - 42 个 outcome records；
  - completed = 30；
  - error = 12；
  - test outcomes: passed = 5，failed = 32，error = 12。
- 已生成：
  - `data/evidence/evp7_visible_test_outcomes.jsonl`；
  - `data/evidence/evp7_visible_test_outcome_summary.json`。
- 已更新 `scripts/build_evp7_evidence_packets.py`，使 E4 从 visible outcome
  source 读取 test outcomes。
- 重跑 `python scripts\build_evp7_evidence_packets.py --check` 后：
  - E0 complete = 42；
  - E2 complete = 42；
  - E4 complete = 30；
  - E6 complete = 0；
  - G2 leakage audit = passed；
  - G1 packet completeness = not_passed。

诊断与修复：

- 第一次 visible runner 把 pytest exit code 4 误归类为 `failed`。已修复：
  - exit code 0 -> `passed`；
  - exit code 1 -> `failed`；
  - 其他非零 exit code -> `error`。
- `bugsinpy_cookiecutter_3` 初始出现 pytest exit code 4，原因是
  `pytest_addopts_override` 是空字符串，语义为清空 addopts；runner 误把空字符串
  当作 false，导致项目默认 addopts 参与运行。已改为
  `addopts_override is not None`，cookiecutter_3 四个 candidates 恢复 completed。
- 剩余 12 个 error 不是 candidate patch 失败：
  - `bugsinpy_PySnooper_1` 6 个 candidates：visible pytest import 阶段触发
    Python 3.11 `collections.Mapping` import error；
  - `bugsinpy_httpie_5` 6 个 candidates：visible pytest import 阶段触发当前
    requests 版本缺少 `requests.compat.is_py26`。
- 按当前边界，不引入临时兼容层，不把这些 error 写成 visible test failed。

下一步：

- 先继续尝试同步 GitHub，因为本地已有未推送提交。
- 如继续推进本地实验，下一步不是 LLM API，而是决定如何处理 12 个 E4 runner
  error 与 E6 realistic visible tool summary source：
  - 若保持 no-compat-layer，则 E4 只能报告 30/42 complete，G1 不通过；
  - 若允许已有项目级 runtime compatibility shim 作为 visible runner 环境的一部分，
    需要先明确记录 scope policy，再重跑 PySnooper_1/httpie_5 visible tests；
  - E6 仍需单独生成 realistic visible tool summaries。

## 43. 2026-06-12 EVP-7 visible tool summary source

本轮小目标：

1. 新增 deterministic visible tool summary builder；
2. 输入只允许使用 `data/evidence/evp7_evidence_packets.jsonl` 和
   `data/evidence/evp7_visible_test_outcomes.jsonl` 中已经 model-visible 的
   patch apply/static/test runner evidence；
3. 输出 `data/evidence/evp7_visible_tool_summaries.jsonl` 和 summary；
4. 更新 evidence packet builder，让 E6 读取 tool summary source；
5. E6 对 E4 complete 且 tool summary 存在的 candidates 标 complete；对 12 个
   E4 error candidates 仍保持 incomplete；
6. leakage audit 必须继续通过。

执行边界：

- 不读取 evaluator-only label；
- 不读取 retained oracle / hidden P2P outcome；
- 不运行真实 LLM API；
- 不把 tool summary 写成结论标签；只能描述 visible evidence：patch apply、
  static not_run、visible test pass/fail/error/timeout。

验收条件：

- tool summary records = 42；
- E6 complete count 与 E4 complete count 一致，当前预期为 30；
- G1 仍 not_passed，直到 12 个 E4 error 被解决或明确排除；
- G2 leakage audit 继续 passed。

执行结果：

- 新增 `scripts/build_evp7_visible_tool_summaries.py`。
- 已生成：
  - `data/evidence/evp7_visible_tool_summaries.jsonl`；
  - `data/evidence/evp7_visible_tool_summary_summary.json`。
- `python scripts\build_evp7_visible_tool_summaries.py --check` 通过：
  - records = 42；
  - complete = 30；
  - incomplete = 12；
  - leakage audit = passed。
- 已更新 `scripts/build_evp7_evidence_packets.py` 读取 tool summary source。
- 重跑 `python scripts\build_evp7_evidence_packets.py --check` 后：
  - E0 complete = 42；
  - E2 complete = 42；
  - E4 complete = 30；
  - E6 complete = 30；
  - G2 leakage audit = passed；
  - G1 packet completeness = not_passed；
  - blocker 变为 12 个 E4/E6 visible-test runner environment/import errors。

验证结果：

- `python -m py_compile scripts\build_evp7_protocol_manifests.py
  scripts\build_evp7_candidate_manifest.py scripts\run_evp7_visible_tests.py
  scripts\build_evp7_visible_tool_summaries.py
  scripts\build_evp7_evidence_packets.py` 通过。
- `python scripts\build_evp7_protocol_manifests.py --check` 通过。
- `python scripts\build_evp7_candidate_manifest.py --check` 通过。
- `python scripts\build_evp7_visible_tool_summaries.py --check` 通过。
- `python scripts\build_evp7_evidence_packets.py --check` 通过。
- JSONL 解析复查通过：
  - `data/evidence/evp7_visible_test_outcomes.jsonl = 42`；
  - `data/evidence/evp7_visible_tool_summaries.jsonl = 42`；
  - `data/evidence/evp7_evidence_packets.jsonl = 168`。
- evidence summary 断言通过：
  - `complete_packet_counts_by_level = {E0: 42, E2: 42, E4: 30, E6: 30}`；
  - `g2_leakage_audit = passed`；
  - `g1_packet_completeness = not_passed`。
- `git diff --check` 通过；仅出现 Windows CRLF 工作区提示。
- 本轮 diff 严格敏感信息扫描无命中。

下一步：

- 不运行真实 LLM API。
- 不继续扩第 8 个 bug。
- 当前真正的决策点是如何处理 12 个 E4/E6 incomplete：
  - 保持 no-compat-layer：把 EVP-7 protocol pilot 写成 30/42 evidence-complete
    子集，并将 PySnooper_1/httpie_5 的 visible runner error 作为 Phase A
    blocker；
  - 或明确允许在 visible runner 中复用已记录的项目级 runtime compatibility
    shim，再重跑 PySnooper_1/httpie_5 visible tests。
- 在该边界明确前，不应启动 LLM merge-gate API。

## 44. 2026-06-13 EVP-7 visible runner environment consistency

本轮 Inspect：

- 当前 Git 状态：`main...origin/main`，工作区干净。
- 当前 EVP-7 evidence summary：
  - E0 complete = 42；
  - E2 complete = 42；
  - E4 complete = 30；
  - E6 complete = 30；
  - G2 leakage audit = passed；
  - G1 packet completeness = not_passed。
- 12 个 incomplete 来自 visible-test runner error：
  - `bugsinpy_PySnooper_1` 6 个 candidates；
  - `bugsinpy_httpie_5` 6 个 candidates。
- 检查 `data/p2p_scopes/bugsinpy_PySnooper_1_p2p_broad.json` 和
  `data/p2p_scopes/bugsinpy_httpie_5_p2p_broad.json` 后确认：两个 tracked
  project-level P2P manifest 都已有 `compat_shim.enabled = true` 和相对 shim
  路径。
- `scripts/validate_candidates_with_p2p.py` 已使用 scope manifest 的
  `compat_shim` 作为 P2P validation 环境的一部分。

本轮小目标：

1. 修复 `scripts/run_evp7_visible_tests.py` 的执行环境一致性：从 candidate
   manifest 中的 `source_files.p2p_manifest` 读取 tracked compat shim；
2. 仅当 P2P manifest 已声明 `compat_shim.enabled = true` 且路径存在时，将该
   shim 加入 visible-test runner 的 `PYTHONPATH`；
3. runner 不创建、不修改、不发明新的兼容层；
4. 重跑 visible tests、tool summaries、evidence packets；
5. 目标是把 PySnooper_1/httpie_5 的 runner import error 转化为真实 visible
   test outcome，而不是复用 hidden validation label。

执行边界：

- 不运行真实 LLM API；
- 不新增第 8 个 bug；
- 不读取 retained oracle / hidden P2P outcome 填充 visible evidence；
- 不创建新的 compat shim；
- 只复用 tracked P2P manifest 已审计的 compat shim；
- 若使用 compat shim 后仍有 runner error，必须保持 incomplete 并记录原因。

验收条件：

- visible runner `--run --check` 通过；
- `evp7_visible_test_outcome_summary.json` 中 error count 降低或明确保留；
- evidence packets 重新生成；
- G2 leakage audit 继续 passed；
- G1 只有在 E0/E2/E4/E6 全部 42 complete 时才允许 passed。

执行结果：

- 已更新 `scripts/run_evp7_visible_tests.py`，从 tracked P2P manifest 读取
  `compat_shim` 并加入 visible-test runner 的 `PYTHONPATH`。
- runner 不创建或修改 shim；只复用 manifest 已记录的
  `outputs/*/compat_shim`。
- 重跑 `python scripts\run_evp7_visible_tests.py --run --check --timeout 90` 后：
  - records = 42；
  - complete visible outcomes = 42；
  - run status: completed = 39，error = 3；
  - test outcomes: passed = 7，failed = 39，error = 3。
- httpie_5 的 6 个 import error 已通过 tracked compat shim 转化为真实 visible
  test outcomes。
- PySnooper_1 仍有 3 个 error，但手动复查显示这是 partial candidates 自身引入
  `pycompat.PY2` 引用却未修改 `pycompat.py` 导致的可见 import error，不是
  runner/environment error。
- 已更新 visible outcome complete 定义：`passed`、`failed`、`error`、`timeout`
  都是可见测试运行后的 outcome；它们都满足 E4 evidence completeness，但不会被
  混同为 pass/fail。
- 重跑 `python scripts\build_evp7_visible_tool_summaries.py --check` 后：
  - records = 42；
  - complete = 42；
  - leakage audit = passed。
- 重跑 `python scripts\build_evp7_evidence_packets.py --check` 后：
  - E0 complete = 42；
  - E2 complete = 42；
  - E4 complete = 42；
  - E6 complete = 42；
  - G1 packet completeness = passed；
  - G2 leakage audit = passed。

下一步：

- 不运行真实 LLM API。
- 进入 G3 baseline readiness：基于 E0/E2/E4/E6 packets 实现 tool-only
  baseline，输出 accept/reject/escalate schema 和 metrics。
- baseline 只能读取 model-visible evidence packets，不能读取 evaluator labels；
  metrics 计算时再 join evaluator-side candidate labels。

## 45. 2026-06-13 EVP-7 tool-only baseline readiness

本轮小目标：

1. 新增 EVP-7 专用 tool-only baseline runner；
2. 决策生成阶段只读取 `data/evidence/evp7_evidence_packets.jsonl`；
3. 评估阶段再 join `data/patches/evp7_candidates.jsonl` 的 evaluator labels
   计算 metrics；
4. 输出 deterministic baseline decisions 和 metrics；
5. baseline 输出遵守 accept/reject/escalate schema，不运行真实 LLM API。

执行边界：

- baseline decision records 不得包含 `label_with_p2p_broad`、
  `candidate_type`、`failure_type_label`、`expected_outcome`、`patch_id` 等
  evaluator-only 字段；
- metrics 可以使用 evaluator labels，但只输出聚合指标；
- 不启动 LLM API；
- 不新增 bug，不修改 candidate labels。

验收条件：

- 每个 condition 对 42 个 candidates 都生成一条 decision；
- 至少包含 apply-only、visible-tests、visible-tool-summary 三个 tool-only
  conditions；
- metrics 包含 accepted precision、false accept rate、correct recall、
  false reject rate、escalation rate、invalid output rate；
- G3 baseline readiness 可由 summary 证明。

执行结果：

- 新增 `scripts/run_evp7_tool_only_baselines.py`。
- 已生成：
  - `data/baselines/evp7_tool_only_decisions.jsonl`；
  - `data/baselines/evp7_tool_only_metrics.json`。
- `python scripts\run_evp7_tool_only_baselines.py --check` 通过：
  - decision_count = 126；
  - candidate_count = 42；
  - conditions = `tool_only_apply_only`、`tool_only_visible_tests`、
    `tool_only_visible_tool_summary`；
  - G3 baseline readiness = passed。
- metrics：
  - `tool_only_apply_only`：全部 escalate，false accept rate = 0.0，
    correct recall = 0.0，escalation rate = 1.0；
  - `tool_only_visible_tests`：accept = 6，reject = 36，accepted precision =
    1.0，false accept rate = 0.0，correct recall = 0.857143；
  - `tool_only_visible_tool_summary`：accept = 6，reject = 36，accepted
    precision = 1.0，false accept rate = 0.0，correct recall = 0.857143。
- visible-tests / visible-tool-summary baseline 都 reject 了 1 个 correct
  candidate，因此当前 tool-only 不是 oracle upper bound；它是 strong safety
  baseline。

验证结果：

- baseline decision records 的严格敏感/label marker 检查通过；
- decision records 不包含 `label_with_p2p_broad`、`candidate_type`、
  `failure_type_label`、`expected_outcome`、`hidden_oracles`、`patch_id`；
- metrics 的 label join 仅用于 aggregate summary。

下一步：

- 不运行真实 LLM API。
- 进入 G4 schema stability：生成 merge-gate schema dry-run inputs/outputs，
  确认 accept/reject/escalate JSON schema 可被稳定解析。

验证结果：

- `python -m py_compile scripts\build_evp7_protocol_manifests.py
  scripts\build_evp7_candidate_manifest.py scripts\run_evp7_visible_tests.py
  scripts\build_evp7_visible_tool_summaries.py
  scripts\build_evp7_evidence_packets.py` 通过。
- `python scripts\build_evp7_protocol_manifests.py --check` 通过。
- `python scripts\build_evp7_candidate_manifest.py --check` 通过。
- `python scripts\build_evp7_visible_tool_summaries.py --check` 通过。
- `python scripts\build_evp7_evidence_packets.py --check` 通过。
- evidence summary 断言通过：
  - `complete_packet_counts_by_level = {E0: 42, E2: 42, E4: 42, E6: 42}`；
  - `g1_packet_completeness = passed`；
  - `g2_leakage_audit = passed`。
- visible outcome summary 断言通过：
  - `complete_visible_outcome_count = 42`；
  - `run_status_counts = {completed: 39, error: 3}`。
- visible tool summary 断言通过：
  - `summary_status_counts = {complete: 42}`。

## 46. 2026-06-13 EVP-7 merge-gate schema stability dry-run

同步状态：

- 上一轮提交 `337c670 data: add evp7 tool-only baselines` 已成功 push 到
  GitHub。
- 当前 EVP-7 已满足：
  - G1 packet completeness = passed；
  - G2 leakage audit = passed；
  - G3 baseline readiness = passed。

本轮小目标：

1. 新增 EVP-7 merge-gate schema dry-run runner；
2. 输入只读取 `data/evidence/evp7_evidence_packets.jsonl`；
3. 为 42 个 candidates 的 E0/E2/E4/E6 packets 生成 deterministic
   schema-valid dry-run outputs；
4. 输出 `data/reviews/evp7_merge_gate_schema_dry_run.jsonl` 和 summary；
5. 验证 accept/reject/escalate JSON schema 可稳定解析，并记录 G4 status。

执行边界：

- 不运行真实 LLM API；
- 不把 dry-run 决策当作模型实验结果；
- 不读取 evaluator-only labels、candidate construction taxonomy、retained
  oracle、hidden P2P outcome 或 reference provenance；
- dry-run 输出不得包含 `label_with_p2p_broad`、`candidate_type`、
  `failure_type_label`、`expected_outcome`、`hidden_oracles`、`patch_id` 等
  evaluator-only 字段；
- 如果 schema 校验失败，先修 runner 或 schema，不进入真实 API。

验收条件：

- 生成 168 条 dry-run records；
- 每个 evidence level 42 条；
- 每条 record 的 parsed schema 都包含 `decision`、`confidence`、
  `primary_reason`、`evidence_used`、`risk_flags`、
  `suspected_failure_type`、`human_review_needed`；
- `decision` 只能是 `accept`、`reject`、`escalate`；
- `confidence` 在 `[0, 1]`；
- leakage audit 通过；
- summary 中 `g4_schema_stability = passed`。

执行结果：

- 新增 `scripts/run_evp7_merge_gate_schema_dry_run.py`。
- 已生成：
  - `data/reviews/evp7_merge_gate_schema_dry_run.jsonl`；
  - `data/reviews/evp7_merge_gate_schema_dry_run_summary.json`。
- `python scripts\run_evp7_merge_gate_schema_dry_run.py --check` 通过：
  - record_count = 168；
  - level_counts = `{E0: 42, E2: 42, E4: 42, E6: 42}`；
  - valid_parse_count = 168；
  - invalid_parse_count = 0；
  - leakage_findings_count = 0；
  - G4 schema stability = passed。
- dry-run policy 是 deterministic `schema_only_visible_rule`，只验证 parser
  和 fixed JSON schema，不是 LLM verifier 结果。

下一步：

- 不运行真实 LLM API。
- 进入 G5 signal existence 的 no-API 准备：基于 schema-stable
  E0/E2/E4/E6 records 先定义 metrics/utility/FACR 计算口径，确认是否能证明
  evidence level 改变 FAR、recall、escalation 或 utility。
- 如果 G5 口径需要真实 LLM 输出而不是 deterministic dry-run，应先写明 API
  输入、成本、模型和停止条件，再由用户确认后执行。

## 47. 2026-06-13 EVP-7 G5 metric scaffold without API

同步状态：

- 上一轮提交 `fc7ebf8 data: add evp7 schema dry run` 已成功 push 到
  GitHub。
- 当前 Git 状态为 `main...origin/main`，工作区干净。
- G1/G2/G3/G4 已通过；G5 仍未证明。

本轮小目标：

1. 新增 G5 metric scaffold 脚本；
2. 输入读取 `data/reviews/evp7_merge_gate_schema_dry_run.jsonl` 和
   `data/patches/evp7_candidates.jsonl`；
3. 按 E0/E2/E4/E6 计算 false accept rate、accepted precision、correct
   recall、false reject rate、escalation rate、invalid output rate；
4. 计算 FACR 和 Evidence Gain 的可复现口径；
5. 明确区分 deterministic dry-run signal preview 与真实 LLM verifier signal。

执行边界：

- 不运行真实 LLM API；
- 不把 dry-run metrics 写成模型效果结论；
- dry-run review records 不得追加 evaluator-only labels；
- evaluator labels 只能在 metrics 阶段 join，并且只输出聚合统计；
- 如果 metric scaffold 发现 schema 或 label join 不稳定，先修本地分析链路，
  不进入 API。

验收条件：

- 输出 tracked metrics summary；
- 每个 evidence level 都有 42 条 records；
- metric schema 覆盖主指标、FACR 和 Evidence Gain；
- summary 明确 `g5_signal_claim_status` 不是 passed，而是需要真实 LLM
  verifier 输出或用户确认 API 执行边界；
- 最小验证和泄漏检查通过。

执行结果：

- 新增 `scripts/analyze_evp7_schema_dry_run_metrics.py`。
- 已生成：
  - `data/reviews/evp7_schema_dry_run_metrics.json`；
  - `docs/experiments/evp7_g5_metric_scaffold.md`。
- `python scripts\analyze_evp7_schema_dry_run_metrics.py --check` 通过：
  - review_record_count = 168；
  - candidate_count = 42；
  - E0/E2/E4/E6 record_count = 42 each；
  - G5 metric scaffold = passed；
  - G5 signal claim status = `requires_real_llm_verifier_outputs`。
- dry-run preview metrics：
  - E0/E2：全部 escalate，correct recall = 0.0，escalation rate = 1.0；
  - E4/E6：accept = 6，reject = 36，false accept rate = 0.0，
    correct recall = 0.857143，escalation rate = 0.0；
  - Evidence Gain vs E0：E4/E6 = 15.5。

诊断：

- 这些变化来自 deterministic schema dry-run rule，只能证明 metrics path 对
  evidence level 敏感，不能证明 LLM signal existence。
- G5 不应标记为 passed；真实 G5 仍需要 genuine LLM verifier outputs，或用户
  明确确认 API/model/cost 边界后执行。

下一步：

- 在不调用 API 的前提下，可继续准备真实 LLM G5 的输入 manifest、成本上限、
  prompt/version 和停止条件。
- 如果要真正执行 G5，需要先得到用户对 API 调用的明确确认。

## 48. 2026-06-13 EVP-7 G5 LLM run readiness without API

同步状态：

- 上一轮提交 `5a01fdd data: add evp7 g5 metric scaffold` 已成功 push 到
  GitHub。
- 当前 Git 状态为 `main...origin/main`，工作区干净。
- G5 metric scaffold 已通过，但真实 G5 signal existence 仍未证明。

本轮小目标：

1. 新增 G5 LLM prompt-manifest builder；
2. 输入只读取 `data/evidence/evp7_evidence_packets.jsonl`；
3. 为 168 个 E0/E2/E4/E6 packet 生成 prompt hash/长度/版本 manifest；
4. 固定 G5 verifier prompt id 和输出 schema；
5. 生成真实 API 前的 readiness summary：运行范围、预计 prompt 规模、默认
   decoding、停止条件和必须由用户确认的项。

执行边界：

- 不运行真实 LLM API；
- 不创建 local API config，不读取 `.env`；
- prompt manifest 不保存完整 prompt text，只保存 hash、长度和边界检查结果；
- prompt 输入不得包含 evaluator-only labels、candidate construction
  taxonomy、retained oracle outcome、hidden P2P outcome 或 reference
  provenance；
- 通用 output schema 枚举可以包含 `partial_fix` 等风险类型名称，但不能包含任何
  candidate-specific evaluator label。

验收条件：

- 生成 168 条 prompt manifest records；
- 每个 evidence level 42 条；
- leakage/boundary check 通过；
- prompt 文档和 prompt change log 明确该 prompt 与旧
  `patch_verify_evidence_first_v1`、`patch_verify_tool_augmented_evidence_v1`
  不冲突、不替代；
- readiness summary 明确真实 API 仍需用户确认。

执行结果：

- 新增 `scripts/build_evp7_g5_llm_prompt_manifest.py`。
- 已生成：
  - `data/reviews/evp7_g5_llm_prompt_manifest.jsonl`；
  - `data/reviews/evp7_g5_llm_run_readiness.json`；
  - `docs/experiments/evp7_g5_llm_run_readiness.md`。
- `python scripts\build_evp7_g5_llm_prompt_manifest.py --check` 通过：
  - prompt_record_count = 168；
  - level_counts = `{E0: 42, E2: 42, E4: 42, E6: 42}`；
  - label_leakage_failed_count = 0；
  - prompt_char_min = 1880；
  - prompt_char_max = 4938；
  - estimated_prompt_tokens_char_div_4 = 121619；
  - G5 LLM run readiness = `passed_without_api`；
  - api_call_attempted = false。
- 新 prompt id：
  `patch_verify_evidence_visibility_merge_gate_v1`。
- 已更新 `docs/prompts/api_pilot_prompts.md` 和
  `docs/prompts/prompt_change_log.md`：
  - 不替代旧 `patch_verify_evidence_first_v1`；
  - 不复用 `patch_verify_tool_augmented_evidence_v1` 的 retained-oracle/tool
    summary 边界；
  - 通用 schema enum 不等于 candidate-specific label 泄漏。

下一步：

- 真实 G5 API 执行仍需用户确认 provider、model、最大总成本、smoke scope 和
  full-run permission。
- 在确认前，不运行真实 API。

## 49. 2026-06-13 EVP-7 G5 API config and preflight without API

同步状态：

- 上一轮提交 `2bac37f data: prepare evp7 g5 llm readiness` 已成功 push 到
  GitHub。
- 当前 Git 状态为 `main...origin/main`，工作区干净。
- G5 LLM prompt readiness 已通过 no-API 检查，但真实 G5 API 执行仍未获用户
  确认。

本轮小目标：

1. 新增 tracked G5 API example config；
2. 新增 G5 preflight/check-only 脚本；
3. preflight 验证 prompt manifest、readiness summary、evidence packet 和
   metric scaffold 的结构一致性；
4. 在用户确认项未填写时，允许 structural readiness 通过，但 strict API
   readiness 必须保持 false；
5. 不读取 `.env`，不调用真实 API。

执行边界：

- 不运行真实 LLM API；
- 不创建或修改 `configs/*.local.json`；
- 不读取 `.env` 或任何 credential；
- example config 只能包含 placeholder，不包含真实 provider/model/cost 决策；
- preflight 不得把 pending user confirmation 误判为 API-ready。

验收条件：

- example config 可由 preflight 解析；
- structural readiness = passed；
- api_ready = false，原因是 provider/model/cost/smoke/full-run permission
  仍需用户确认；
- prompt manifest 仍为 168 条，四层各 42 条；
- 最小验证和敏感信息扫描通过。

执行结果：

- 新增 `configs/evp7_g5_llm.example.json`。
- 新增 `scripts/preflight_evp7_g5_llm_run.py`。
- 已生成：
  - `data/reviews/evp7_g5_llm_preflight_example.json`；
  - `data/reviews/evp7_g5_llm_preflight_strict_example.json`。
- `python scripts\preflight_evp7_g5_llm_run.py --out
  data\reviews\evp7_g5_llm_preflight_example.json` 通过：
  - structural_ready = true；
  - api_ready = false；
  - api_call_attempted = false。
- strict 检查按预期失败并被 wrapper 验证：
  - `python scripts\preflight_evp7_g5_llm_run.py --strict-api-ready --out
    data\reviews\evp7_g5_llm_preflight_strict_example.json`；
  - 失败原因是 provider/model/cost/smoke/full-run permission 仍未由用户确认。

诊断：

- 当前本地结构已经足以让未来 local config 做真实 G5 前检查；
- example config 仍然不能执行真实 API，这符合边界；
- 没有读取 `.env`，没有创建 local config，没有调用 API。

下一步：

- 真实 G5 执行仍需要用户明确提供或确认：
  - API provider；
  - model；
  - max_total_cost_usd；
  - smoke_scope；
  - full_run_permission。

## 50. 2026-06-13 EVP-7 G5 guarded workflow without API

同步状态：

- 上一轮提交 `1f8f936 chore: add evp7 g5 preflight` 已成功 push 到 GitHub。
- 当前 Git 状态为 `main...origin/main`，工作区干净。
- G5 example config 的 structural readiness 已通过；strict API readiness
  仍因用户确认项缺失而失败。

本轮小目标：

1. 新增 G5 guarded workflow；
2. 支持 `--check-only`：只运行 preflight，不调用 API；
3. 支持 `--mock-policy`：用本地 mock response 验证 output schema、
   review JSONL 和 metrics pipeline；
4. 支持未来 `--execute` 路径，但必须要求 strict API preflight 通过且显式
   `--execute`；
5. 生成 tracked check-only/mock summary，证明 workflow guard 能阻止未确认的
   example config 真实执行。

执行边界：

- 不运行真实 LLM API；
- 不读取 `.env`；
- 不创建 local config；
- mock 输出只能作为 pipeline validation，不能作为 LLM 结果或 G5 signal；
- 真实 execute 路径不得在 example config 上通过。

验收条件：

- check-only summary 显示 `model_call_attempted = false`；
- mock run summary 显示 `mock_run = true`、`api_call_attempted = false`；
- mock review records 能被 G5 metrics scaffold 解析；
- strict execute guard 对 example config 保持 blocked；
- 文档明确真实 G5 仍需用户确认。

执行结果：

- 新增 `scripts/run_evp7_g5_llm_workflow.py`。
- 已生成：
  - `data/reviews/evp7_g5_workflow_check_only_example.json`；
  - `data/reviews/evp7_g5_workflow_mock_reviews.jsonl`；
  - `data/reviews/evp7_g5_workflow_mock_metrics.json`；
  - `data/reviews/evp7_g5_workflow_mock_summary.json`。
- `python scripts\run_evp7_g5_llm_workflow.py --check-only --summary-out
  data\reviews\evp7_g5_workflow_check_only_example.json` 通过：
  - mode = check_only；
  - structural_ready = true；
  - api_ready = false；
  - model_call_attempted = false；
  - api_call_attempted = false。
- `python scripts\run_evp7_g5_llm_workflow.py --mock-policy
  schema_visible_rule ...` 通过：
  - mock_run = true；
  - review_count = 168；
  - model_call_attempted = false；
  - api_call_attempted = false；
  - G5 metric scaffold = passed；
  - G5 signal claim status = `requires_real_llm_verifier_outputs`。
- `python scripts\run_evp7_g5_llm_workflow.py --execute ...` 在 example config
  上按预期失败，且在 API 调用前停止，原因是 strict API readiness 仍为 false。

诊断与修复：

- 初次 mock workflow 失败，因为 workflow 把相对 `reviews_out` 传给
  metrics scaffold，而 metrics scaffold 对相对路径调用
  `relative_to(REPO_ROOT)`。已在 workflow 中统一转为绝对路径。
- 单独调用 metrics scaffold 并传相对 `--reviews-in` 时也会失败；已修复
  `scripts/analyze_evp7_schema_dry_run_metrics.py`，在读取和 leakage audit 前
  统一解析相对路径。

下一步：

- 真实 G5 执行仍需要用户明确确认 provider、model、max_total_cost_usd、
  smoke_scope 和 full_run_permission。
- 若用户确认后，必须先用 ignored local config 跑 strict preflight 和
  check-only workflow，再执行 smoke；不能直接 full run。

## 51. 2026-06-13 EVP-7 G5 local config helper without API

同步状态：

- 上一轮提交 `e4b02ee chore: add evp7 g5 guarded workflow` 已成功 push 到
  GitHub。
- 当前 Git 状态为 `main...origin/main`，工作区干净。
- G5 guarded workflow 已可 check-only/mock；真实执行仍等待用户确认。

本轮小目标：

1. 新增 G5 local config 生成器；
2. 支持 `--dry-run`，只打印/写入 tracked dry-run plan，不创建 local config；
3. 支持未来写入 ignored `configs/evp7_g5_llm.local.json`，但必须要求显式
   provider/model/cost/smoke/full-run 参数；
4. 生成 G5 execution confirmation packet，列出用户必须确认的值和安全命令顺序；
5. 不读取 `.env`，不调用真实 API。

执行边界：

- 不私自选择 provider、model、cost 或 smoke scope；
- 不创建真实 local config，除非未来命令显式提供全部参数且不使用 `--dry-run`；
- 不读取 credential；
- helper 输出不得包含密钥或本机绝对路径；
- tracked dry-run artifacts 必须保持“待用户确认”状态。

验收条件：

- dry-run helper 通过；
- dry-run 不创建 `configs/evp7_g5_llm.local.json`；
- execution packet 明确真实 API 前的命令顺序：
  local config -> strict preflight -> check-only workflow -> smoke execute ->
  post-smoke decision -> full run；
- 最小验证和敏感信息扫描通过。

执行结果：

- 新增 `scripts/create_evp7_g5_llm_local_config.py`。
- 已生成：
  - `data/reviews/evp7_g5_local_config_dry_run.json`；
  - `docs/experiments/evp7_g5_execution_confirmation_packet.md`。
- `python scripts\create_evp7_g5_llm_local_config.py --dry-run ...` 通过：
  - local_config_write_attempted = false；
  - api_call_attempted = false；
  - ready_to_write_local_config = false；
  - missing_or_unconfirmed = provider/model/cost/smoke/full-run permission。
- 验证 `configs/evp7_g5_llm.local.json` 未被创建。
- 非 dry-run 空参数写入检查按预期失败，且仍未创建 local config。

下一步：

- 真实 G5 执行仍需要用户提供 provider、model、max_total_cost_usd、
  smoke_scope 和 full_run_permission。
- 用户确认后，必须先用 helper 写入 ignored local config，再跑 strict preflight
  和 check-only workflow；smoke 通过后才允许考虑 full run。

## 52. 2026-06-13 EVP-7 G5 sync audit and confirmation gate

同步状态：

- 本地提交 `37e1b7f chore: add evp7 g5 local config helper` 已成功 push 到
  GitHub `origin/main`。
- 当前 Git 状态为 `main...origin/main`，工作区干净。
- `docs/experiments/evp7_g5_execution_confirmation_packet.md` 是当前真实
  G5 执行前的确认入口。

本轮审计结论：

- EVP-7 G5 的 no-API 前置链路已经补到 local config helper、strict
  preflight、check-only workflow 和 mock parser/metrics validation。
- 这些产物只能证明执行链路和指标链路可运行，不能作为 LLM verifier signal。
- 旧计划中的模型选择记录不能替代当前 EVP-7 G5 execution packet，因为当前
  仍缺少完整的 provider、model、max_total_cost_usd、smoke_scope 和
  full_run_permission 确认。

当前门禁：

- 不得继续运行真实 API；
- 不得自行写入 `configs/evp7_g5_llm.local.json`；
- 不得把 dry-run/mock outputs 写成论文级 G5 signal；
- 必须等待用户明确给出全部 5 个真实执行参数。

## 53. 2026-06-13 EVP-7 G5 DeepSeek V4 smoke execution plan

用户确认：

- 用户指令：使用 `deepseekv4`，其余不作限制。
- 本项目已有一致模型记录为 DeepSeek official API 的 `deepseek-v4-pro`，因此
  本轮将 `deepseekv4` 落地为：
  - `api_provider = deepseek_official`；
  - `model = deepseek-v4-pro`。
- “其余不作限制”解释为：
  - 不再额外限制 smoke 后 full run permission；
  - `max_total_cost_usd` 使用高额安全上限，仅作为脚本所需的异常保护；
  - 仍必须按既定协议先跑 smoke，不直接 full run。

本轮小目标：

1. 写入 ignored `configs/evp7_g5_llm.local.json`；
2. 运行 strict preflight；
3. 运行 check-only workflow；
4. 先执行 4-packet smoke，覆盖同一 candidate 的 E0/E2/E4/E6 四层；
5. 审计 smoke 的 parse status、invalid-output rate、成本和 summary；
6. 只有 smoke 通过后，才考虑 full run。

执行边界：

- 可以读取 `.env` 中的 `DEEPSEEK_API_KEY`，但不得输出或提交 key；
- 不提交 ignored local config 或 `outputs/` 原始结果；
- smoke/mock/dry-run 结论必须和 real full-run 结论分开记录；
- 若 DeepSeek API、模型 id、JSON parse、成本或 prompt boundary 出错，先诊断并记录，
  不得直接继续 full run。

初次 smoke 结果：

- 命令：`python scripts\run_evp7_g5_llm_workflow.py --config
  configs\evp7_g5_llm.local.json --execute --limit 4 ...`。
- 真实 API 已调用，生成 4 条 non-mock review。
- E0/E2 parse valid，均为 `escalate`。
- E4/E6 parse invalid，`raw_response_text` 为空，invalid reason 为
  `invalid_json:No JSON object found in model response`。
- smoke invalid-output rate = 2/4，不能进入 full run。

诊断：

- 失败类型：执行链路输出格式问题，不是论文结论问题。
- 当前 G5 config 使用 `max_tokens = 1024`。
- 项目已有 DeepSeek V4 经验表明过低 `max_tokens` 会导致 reasoning 消耗完
  completion budget，final `content` 为空。

修复计划：

1. 将 G5 example/local config 的 `max_tokens` 提升到 4096；
2. 重新生成 ignored local config；
3. 重新运行 strict preflight 和 check-only；
4. 重新执行同一 4-packet smoke；
5. 若 invalid-output rate 仍不为 0，继续诊断，不进入 full run。

修复后 smoke 结果：

- 已将 `configs/evp7_g5_llm.example.json` 的 `max_tokens` 提升到 4096，并重新
  生成 ignored local config。
- strict preflight 通过：`api_ready = true`。
- check-only workflow 通过：`model_call_attempted = false`，
  `api_call_attempted = false`。
- 第二次 4-packet smoke 通过：
  - review_count = 4；
  - parse valid = 4/4；
  - invalid-output rate = 0；
  - E0/E2/E6 = `escalate`；
  - E4 = `accept`。
- smoke metrics scaffold 仍为 `not_passed`，原因是 smoke 只有 4 条记录，不是
  168 条完整 G5 结果；这不阻止进入 full run，但不能写成论文级结论。

full run 决策：

- 用户已给出“其余不作限制”，local config 中
  `full_run_permission = true`。
- smoke parse gate 已通过。
- 下一步执行 168-packet full run，输出仅写入 ignored `outputs/`，完成后再生成
  tracked summary 和文档结论。

## 54. 2026-06-13 EVP-7 G5 bounded parallel execution acceleration

用户确认：

- 用户明确允许将 G5 full run 改为并行加速执行。

本轮小目标：

1. 给 `scripts/run_evp7_g5_llm_workflow.py` 增加显式 `--concurrency` 参数；
2. 默认保持 `--concurrency 1`，不改变既有 smoke/check-only/mock 行为；
3. 并发执行只在 `--execute` 路径生效；
4. 并发时先完成 prompt-boundary 检查，再发起 bounded model calls；
5. 所有结果按原 packet 顺序一次性写入 JSONL，避免多线程竞争写文件。

执行边界：

- 本轮只改执行器和文档，不启动真实 full run；
- 不提交 ignored local config 或 `outputs/` 原始结果；
- 如果后续使用并行 full run，建议从 `--concurrency 4` 或 `--concurrency 6`
  开始；遇到 rate limit 或 invalid output 上升必须暂停诊断。

验收条件：

- `python -m py_compile scripts\run_evp7_g5_llm_workflow.py` 通过；
- `--check-only` 仍不调用模型；
- mock workflow 在 `--concurrency` 参数存在时仍可运行并保持 no-API；
- staged diff 不含 credentials 或 raw outputs。

## 55. 2026-06-13 EVP-7 G5 parallel full run result

执行结果：

- 旧的 sequential full run 被中断后仍在后台运行；为节省时间，已确认其命令未带
  `--concurrency`，并停止该旧进程，避免重复 API 消耗。
- 使用 bounded parallel path 执行：
  `python scripts\run_evp7_g5_llm_workflow.py --config
  configs\evp7_g5_llm.local.json --execute --limit 0 --concurrency 4 ...`。
- full run 完成：
  - review_count = 168；
  - evidence level counts = E0/E2/E4/E6 各 42；
  - review ids 唯一数 = 168；
  - 输出顺序与 evidence packet 顺序一致；
  - parse valid = 167；
  - invalid = 1。

质量审计：

- 唯一 invalid 记录为 `evp7_candidate_0012__E0`，原因是
  `missing_keys:primary_reason`；模型返回了 `reason` 字段但未返回
  protocol 要求的 `primary_reason`。
- invalid-output rate = 1/168 = 0.005952。
- DeepSeek response 未在已保存 usage 字段中暴露可直接计费的 cost；runner
  `total_cost_usd = 0.0` 不能当作账单估计。
- 原始模型响应仍只保留在 ignored `outputs/`，tracked summary 不复制 raw
  responses。

指标结论：

- `g5_metric_scaffold = passed`；
- `run_kind = real_llm`；
- `g5_signal_claim_status =
  real_llm_verifier_signal_observed_on_evp7`；
- E0：escalate 23、reject 18、invalid 1，false accept rate = 0；
- E2：escalate 24、reject 18，false accept rate = 0；
- E4：accept 1、escalate 5、reject 36，accepted precision = 1.0，
  correct recall = 0.142857，Evidence Gain vs E0 = 4.5；
- E6：accept 2、escalate 7、reject 33，accepted precision = 1.0，
  correct recall = 0.285714，Evidence Gain vs E0 = 5.0。

下一步：

- 不重跑 full run；保留 1 条 invalid 作为真实模型输出质量边界。
- 进入 15-20 bugs controlled expansion 的准备：优先补可复用的 summary、
  analysis 和 expansion planning，避免在无关阻塞点上串行等待。

## 56. 2026-06-13 EVP-7 expansion readiness without new checkout

本轮小目标：

- 在不启动新 checkout、不运行新 API 的情况下，整理 EVP-7 后 controlled
  expansion 的输入边界；
- 复用现有 `outputs/candidate_pool_rescreen/parallel_latest.json` 和
  `data/cohorts/task_cohort_registry.json`；
- 生成 tracked readiness summary，避免后续重复人工翻阅大文件。

执行结果：

- 新增 `scripts/summarize_evp7_expansion_readiness.py`。
- 生成：
  - `data/tasks/evp7_expansion_readiness.json`；
  - `docs/experiments/evp7_expansion_readiness.md`。
- 当前 EVP-7 main task count = 7；
- 当前 main projects = PySnooper 2、cookiecutter 3、httpie 1、tqdm 1；
- registry blocked/pending tasks = 27；
- broader BugsInPy pool：
  - total tasks = 501；
  - already registered = 30；
  - new candidate tasks = 471；
  - metadata-promising candidates = 187。

效率边界：

- 下一步不应批量启动 187 个候选或盲扫 BugsInPy；
- 应按 project-diverse lane 做 bounded probe；
- 每个高风险项目一次最多推进一个 task；
- buggy/fixed checkout for same task 不并行；
- 只有 F2P、project-level P2P-broad、candidate construction 和 candidate
  revalidation 全部通过后，才允许进入 `p2p_broad_main`。

## 57. 2026-06-13 controlled expansion probe: fastapi_4 F2P only

选择理由：

- `evp7_expansion_readiness` 显示 fresh-project promising candidates = 0；
  后续扩展只能在 already-risky 或 already-main project 中做 bounded probe。
- `bugsinpy_fastapi_4` 是 metadata score = 8 的 pytest 候选，run command 为
  `pytest tests/test_param_in_path_and_dependency.py::test_reused_param`。
- FastAPI 项目已有 `fastapi_1/2` 的 project-level P2P timeout 风险，因此本轮
  只做 F2P feasibility，不启动长 project-level P2P construction。

执行边界：

- buggy/fixed checkout 串行执行，不并行同一 task；
- 不修改 checkout 源码、测试或 fixture；
- 不安装新依赖，除非后续有明确依赖审计；
- 若 checkout、collection、F2P 行为或 run command 边界不清，记录 blocker；
- 本轮结果只能作为 expansion probe，不得作为 main cohort admission。

执行结果：

- buggy checkout 完成；
- fixed checkout 完成；
- buggy 与 fixed 均在 pytest collection 阶段失败，未到达目标断言；
- 失败原因是当前环境的 Pydantic v2 与该 legacy FastAPI checkout 的
  OpenAPI model import 不兼容；
- 未安装依赖、未修改 checkout 源码、测试或 fixture。

产物：

- 新增 `data/tasks/evp7_controlled_probe_results.json`；
- 新增 `docs/experiments/evp7_fastapi4_f2p_probe.md`；
- `scripts/summarize_evp7_expansion_readiness.py` 现在会读取 tracked
  controlled probe status；
- `docs/experiments/evp7_expansion_readiness.md` 与
  `data/tasks/evp7_expansion_readiness.json` 已显示
  `bugsinpy_fastapi_4 = f2p_blocked_dependency_environment`。

判定：

- `bugsinpy_fastapi_4` 不进入 `p2p_broad_main`；
- 它只保留为 dependency-environment blocker；
- 不在本轮修 FastAPI 依赖隔离，避免把扩展任务变成环境工程任务。

## 58. 2026-06-13 controlled expansion probe: sanic_2 F2P only

本轮小目标：

- 继续 controlled expansion，但切换到独立项目 lane；
- 只验证 `bugsinpy_sanic_2` 的 F2P feasibility；
- 不启动 project-level P2P-broad construction。

选择理由：

- `bugsinpy_sanic_2` 是 readiness top lane 中另一个 metadata score = 8
  的 pytest 候选；
- run command 为
  `pytest tests/test_app.py::test_asyncio_server_start_serving`；
- Sanic 已有 `sanic_1` 的 project-level P2P timeout 记录，因此本轮同样只做
  F2P feasibility，避免先进入长 P2P。

执行边界：

- buggy/fixed checkout 串行执行，不并行同一 task；
- 不修改 checkout 源码、测试或 fixture；
- 不安装新依赖，除非后续有明确依赖审计；
- 若 checkout、collection、F2P 行为或 run command 边界不清，记录 blocker；
- 本轮结果只能作为 expansion probe，不得作为 main cohort admission。

执行结果：

- buggy checkout 完成；
- fixed checkout 完成；
- buggy 与 fixed 均在 `tests/conftest.py` import 阶段失败，未到达目标测试；
- 失败原因是当前环境缺少 Sanic runtime dependency `aiofiles`；
- 未安装依赖、未修改 checkout 源码、测试或 fixture。

产物：

- `data/tasks/evp7_controlled_probe_results.json` 追加
  `bugsinpy_sanic_2 = f2p_blocked_dependency_environment`；
- 新增 `docs/experiments/evp7_sanic2_f2p_probe.md`；
- `docs/experiments/evp7_expansion_readiness.md` 与
  `data/tasks/evp7_expansion_readiness.json` 已重新生成以反映 probe status。

判定：

- `bugsinpy_sanic_2` 不进入 `p2p_broad_main`；
- 它只保留为 dependency-environment blocker；
- 不在本轮安装 `aiofiles`，避免把 F2P triage 变成依赖隔离任务。

## 59. 2026-06-13 parallel controlled F2P-only triage

本轮小目标：

- 为节省时间，按 readiness 边界并行推进多个独立 project lane 的
  F2P-only triage；
- 每个 task 内部仍保持 buggy/fixed checkout 串行；
- 不启动任何 project-level P2P-broad construction。

候选 lane：

- `bugsinpy_scrapy_2`：unittest，已知 Scrapy 项目有 native build 风险；
- `bugsinpy_tornado_1`：unittest，已知 Tornado project-level P2P timeout
  风险；
- `bugsinpy_youtube-dl_2`：unittest，已知 youtube-dl project-level discovery
  timeout 风险。

执行边界：

- 只做 checkout + original F2P command；
- 不安装依赖，不编辑 checkout；
- 若某个 lane checkout 或 F2P 环境失败，记录 blocker 后继续其他独立 lane；
- 即使某个 lane F2P 成立，也只记录可行性，不自动启动 P2P-broad。

执行结果：

- `bugsinpy_scrapy_2`：
  - buggy/fixed checkout 均完成；
  - buggy/fixed 均在 import Scrapy 时因缺少 `twisted` 失败；
  - 判定为 `f2p_blocked_dependency_environment`。
- `bugsinpy_tornado_1`：
  - 复用已有 buggy/fixed checkout；
  - 直接 unittest 在 Windows Proactor event loop 下失败；
  - 使用已记录的 Windows selector event loop policy 后，buggy fail、fixed
    pass；
  - 但该任务已有 project-level P2P-broad timeout blocker，仍不进入主样本。
- `bugsinpy_youtube-dl_2`：
  - buggy/fixed checkout 均完成；
  - target unittest 结果为 buggy fail、fixed pass；
  - 判定为 `f2p_established_p2p_not_attempted`。

产物：

- `data/tasks/evp7_controlled_probe_results.json` 追加
  `scrapy_2`、`tornado_1`、`youtube-dl_2`；
- 新增 `docs/experiments/evp7_parallel_f2p_triage_20260613.md`；
- `youtube-dl_2` 是当前 batch 中唯一新的 clean F2P signal。

判定：

- 不自动启动 `youtube-dl_2` project-level P2P-broad，因为第 59 节边界是
  F2P-only triage；
- 下一步可以继续并行 F2P-only triage 剩余 readiness lanes，或者显式转入
  `youtube-dl_2` 的 bounded project-level P2P-broad construction。

## 60. 2026-06-13 remaining readiness lanes F2P-only triage

本轮小目标：

- 在不触发 P2P-broad、不安装依赖的前提下，补完 readiness top lanes 中剩余
  metadata 候选的 F2P-only triage；
- 如果 checkout 或 import 阶段失败，记录 blocker 后停止该 lane；
- 若发现新的 clean F2P signal，只记录为 P2P 候选，不直接 admission。

候选 lane：

- `bugsinpy_ansible_1`：pytest，已知历史风险为 checkout timeout；
- `bugsinpy_luigi_1`：pytest，已知 Luigi 项目有 collection/large-suite/P2P
  timeout 风险；
- `bugsinpy_matplotlib_1`：pytest，已知 Matplotlib 有 native extension import
  blocker。

执行边界：

- 每个 task 内 buggy/fixed checkout 串行；
- 独立 project lane 可以并行推进；
- checkout 使用 bounded timeout；
- 不安装依赖，不编辑 checkout；
- 不启动任何 project-level P2P-broad construction。

执行结果：

- `bugsinpy_ansible_1`：
  - buggy/fixed checkout 均完成；
  - 首次运行缺 `PYTHONPATH=lib`，修正路径后进入 Windows `fcntl` import
    blocker；
  - 判定为 `f2p_blocked_windows_posix_import`。
- `bugsinpy_luigi_1`：
  - buggy/fixed checkout 均完成；
  - 复用已有 Luigi `inspect.ArgSpec/getargspec` runtime compatibility 后，
    两端均因缺少 `tornado` 失败；
  - 判定为 `f2p_blocked_dependency_environment`。
- `bugsinpy_matplotlib_1`：
  - 历史 workspace 存在，但 buggy checkout 缺目标测试文件；
  - 该任务已有 native extension import blocker；
  - 本轮不重建 checkout，不进入 F2P。

产物：

- `data/tasks/evp7_controlled_probe_results.json` 追加
  `ansible_1`、`luigi_1`、`matplotlib_1`；
- 新增 `docs/experiments/evp7_remaining_f2p_triage_20260613.md`。

当前结论：

- readiness top 8 lanes 已全部完成 metadata-to-F2P triage；
- 唯一新的 clean F2P signal 是 `bugsinpy_youtube-dl_2`；
- 其余 lane 均为 dependency、Windows runtime、known timeout 或 historical
  incomplete/native blocker；
- 下一步的实质决策点是：是否对 `youtube-dl_2` 启动 bounded project-level
  P2P-broad construction，尽管 `youtube-dl_1` 已有 project-level discovery
  timeout 风险。

## 61. 2026-06-13 youtube-dl family F2P-only continuation

本轮小目标：

- 不启动 `youtube-dl_2` 的 project-level P2P-broad construction；
- 继续做不依赖该决策的 F2P-only triage；
- 优先选择同项目中短命令、无新增依赖安装需求的 `youtube-dl` 候选。

候选 lane：

- `bugsinpy_youtube-dl_3`：
  `python -m unittest -q test.test_utils.TestUtil.test_unescape_html`；
- `bugsinpy_youtube-dl_4`：
  `python -m unittest -q test.test_jsinterp.TestJSInterpreter.test_call`；
- `bugsinpy_youtube-dl_5`：
  `python -m unittest -q test.test_utils.TestUtil.test_unified_timestamps`。

选择理由：

- `youtube-dl_2` 已在 no-install/no-edit 边界下建立 clean F2P；
- `youtube-dl` 候选多为纯 unittest，环境风险低于 FastAPI/Sanic/Scrapy/
  Ansible/Luigi/Matplotlib；
- 这一步只增加 F2P 可行性证据，不改变 main cohort，也不绕过 P2P-broad
  admission gate。

执行边界：

- 每个 task 内 buggy/fixed checkout 串行；
- 独立 task lane 可以并行推进；
- 不安装依赖，不编辑 checkout；
- 不启动任何 project-level P2P-broad construction；
- 若 F2P 成立，只记录为 P2P 候选，不直接 admission。

执行结果：

- `bugsinpy_youtube-dl_3`：
  - buggy/fixed checkout 均完成；
  - target unittest 结果为 buggy fail、fixed pass；
  - 判定为 `f2p_established_p2p_not_attempted`。
- `bugsinpy_youtube-dl_4`：
  - buggy/fixed checkout 均完成；
  - target unittest 结果为 buggy error、fixed pass；
  - 判定为 `f2p_established_p2p_not_attempted`。
- `bugsinpy_youtube-dl_5`：
  - buggy/fixed checkout 均完成；
  - target unittest 结果为 buggy error、fixed pass；
  - 判定为 `f2p_established_p2p_not_attempted`。

产物：

- `data/tasks/evp7_controlled_probe_results.json` 追加
  `youtube-dl_3`、`youtube-dl_4`、`youtube-dl_5`；
- 新增 `docs/experiments/evp7_youtubedl_f2p_continuation_20260613.md`；
- `scripts/summarize_evp7_expansion_readiness.py` 增加 controlled probe
  status counts 与 F2P-established P2P candidate list。

当前结论：

- 当前新增 clean F2P 候选为 `youtube-dl_2/3/4/5`；
- 这些仍不是 main cohort tasks；
- 下一步若要进入 admission 路径，必须先决定是否对 youtube-dl family
  启动 bounded project-level P2P-broad construction。

## 62. 2026-06-13 youtube-dl pure-utils F2P-only continuation

本轮小目标：

- 继续做不依赖 P2P 决策的 F2P-only triage；
- 优先选择 `youtube-dl` 中更轻的 pure-utils unittest；
- 不启动 project-level P2P-broad construction。

候选 lane：

- `bugsinpy_youtube-dl_6`：
  `python -m unittest -q test.test_utils.TestUtil.test_parse_dfxp_time_expr`；
- `bugsinpy_youtube-dl_7`：
  `python -m unittest -q test.test_utils.TestUtil.test_js_to_json_realworld`；
- `bugsinpy_youtube-dl_11`：
  `python -m unittest -q test.test_utils.TestUtil.test_str_to_int`。

执行边界：

- 每个 task 内 buggy/fixed checkout 串行；
- 独立 task lane 可以并行推进；
- 不安装依赖，不编辑 checkout；
- 若 F2P 成立，只记录为 P2P 候选，不直接 admission；
- 若 F2P 不成立或两端行为相同，记录为 non-admitted probe result。

执行结果：

- `bugsinpy_youtube-dl_6`：
  - buggy/fixed checkout 均完成；
  - target unittest 结果为 buggy fail、fixed pass；
  - 判定为 `f2p_established_p2p_not_attempted`。
- `bugsinpy_youtube-dl_7`：
  - buggy/fixed checkout 均完成；
  - target unittest 结果为 buggy fail、fixed pass；
  - 判定为 `f2p_established_p2p_not_attempted`。
- `bugsinpy_youtube-dl_11`：
  - buggy/fixed checkout 均完成；
  - target unittest 结果为 buggy error、fixed pass；
  - 判定为 `f2p_established_p2p_not_attempted`。

产物：

- `data/tasks/evp7_controlled_probe_results.json` 追加
  `youtube-dl_6`、`youtube-dl_7`、`youtube-dl_11`；
- 新增 `docs/experiments/evp7_youtubedl_pure_utils_f2p_20260613.md`。

当前结论：

- 当前新增 clean F2P 候选为
  `youtube-dl_2/3/4/5/6/7/11`；
- 它们仍不是 main cohort tasks；
- 下一步必须在 youtube-dl family P2P-broad 预算与 timeout 风险之间做显式
  决策，不能把 F2P 数量直接当作论文主样本扩容。

## 63. 2026-06-13 youtube-dl family P2P-broad decision packet

本轮小目标：

- 不继续盲目补第 8 个 F2P；
- 将 `youtube-dl` family 是否进入 bounded project-level P2P-broad 的决策
  背景、候选集、预算和 gate 单独成文；
- 在用户确认前不启动真实 P2P-broad construction。

背景：

- controlled expansion 目前已有 7 个 clean F2P `youtube-dl` 候选：
  `youtube-dl_2/3/4/5/6/7/11`；
- `bugsinpy_youtube-dl_1` 已有 clean F2P，但 project-level unittest
  discovery/P2P-broad construction 曾达到 bounded runtime 且未生成 manifest；
- 因此当前风险不是 F2P 数量不足，而是尚未证明 `youtube-dl` family 能在最终
  project-level P2P-broad 协议下形成可入主样本证据。

执行边界：

- 只整理决策包，不执行 P2P；
- 不安装依赖、不编辑 checkout、不修改实验标签；
- 若后续用户确认 P2P，先只对一个代表性 `youtube-dl` task 运行 bounded
  project-level P2P-broad，不并行启动多个长 P2P。

产物：

- 新增 `docs/experiments/evp7_youtubedl_p2p_decision_packet_20260613.md`。

当前结论：

- 推荐首个代表任务已根据第 66 节静态 sweep 从 `bugsinpy_youtube-dl_6`
  修订为 `bugsinpy_youtube-dl_7`；
- 这是执行效率最高的下一步决策：若该代表任务仍重复 `youtube-dl_1` timeout
  pattern，应停止 youtube-dl P2P 扩展，而不是继续批量补 F2P；
- 在获得明确确认前，真实 P2P-broad 仍保持未执行状态。

## 64. 2026-06-13 youtube-dl_6 no-run static P2P preflight

本轮小目标：

- 在不执行 P2P、不创建 manifest 的前提下，评估 `youtube-dl_6` 代表性 P2P
  尝试的静态规模；
- 检查 buggy/fixed 两端 `test/` 下 unittest 方法集合是否一致；
- 为后续是否批准 bounded P2P 提供效率证据。

执行边界：

- 只读取现有 checkout 文件；
- 不执行 unittest、pytest 或 P2P；
- 不安装依赖、不编辑 checkout、不修改实验标签。

静态预检结果：

- buggy/fixed 两端均有 20 个 `test*.py` 文件；
- buggy/fixed 两端均有 154 个静态 unittest test methods；
- 使用当前决策包中的静态排除 token 后，两端均排除 43 个方法；
- 两端剩余方法数均为 111，且剩余集合完全一致；
- `test/test_utils.py` 两端均剩余 46 个方法。

当前结论：

- `youtube-dl_6` 的 project-level P2P 代表尝试不是无边界全仓库扫描，但动态
  范围仍有 111 个候选方法，存在重复 `youtube-dl_1` timeout 的风险；
- 该证据支持“若确认 P2P，则只先跑一个代表任务”的边界；
- 该预检不等于 P2P 结果，不允许据此 admission。

## 65. 2026-06-13 reusable static unittest P2P preflight

本轮小目标：

- 将第 64 节的一次性 inline 静态预检固化为可复用脚本；
- 后续遇到 unittest 项目时，可先用 no-run AST 统计估算 P2P 动态规模；
- 继续不执行真实 P2P、不创建 P2P manifest。

执行边界：

- 新增脚本只读取 buggy/fixed checkout 源文件；
- 只统计 `test*.py` 中类方法名以 `test` 开头的 unittest methods；
- 只做静态 token 排除和 buggy/fixed 剩余集合比较；
- 不执行测试、不安装依赖、不修改 checkout、不改变实验标签。

产物：

- 新增 `scripts/static_unittest_p2p_preflight.py`。

验收条件：

- `python -m py_compile scripts\static_unittest_p2p_preflight.py` 通过；
- 使用该脚本复现 `youtube-dl_6` 的静态结果：
  - buggy/fixed 各 154 个静态 unittest methods；
  - 静态排除后各剩余 111 个；
  - buggy/fixed 剩余集合差异为 0；
- README、INDEX 和经验文档补充脚本入口。

执行结果：

- 已新增 `scripts/static_unittest_p2p_preflight.py`；
- 已用该脚本复现 `youtube-dl_6` 静态预检结果；
- 已补充 README、INDEX 和经验文档入口。

## 66. 2026-06-13 youtube-dl family static preflight sweep

本轮小目标：

- 使用可复用静态预检脚本检查全部 7 个 clean-F2P `youtube-dl` 候选；
- 找出如果后续批准 P2P，哪个代表任务静态成本最低；
- 不执行 P2P、不创建 P2P manifest、不修改实验标签。

执行结果：

| Task | Static methods per side | Remaining methods per side | Buggy/fixed remaining diff |
| --- | ---: | ---: | ---: |
| `bugsinpy_youtube-dl_2` | 212 | 151 | 0 |
| `bugsinpy_youtube-dl_3` | 211 | 151 | 0 |
| `bugsinpy_youtube-dl_4` | 196 | 141 | 0 |
| `bugsinpy_youtube-dl_5` | 191 | 137 | 0 |
| `bugsinpy_youtube-dl_6` | 154 | 111 | 0 |
| `bugsinpy_youtube-dl_7` | 149 | 108 | 0 |
| `bugsinpy_youtube-dl_11` | 232 | 167 | 0 |

当前结论：

- 全部 7 个候选的 buggy/fixed 静态剩余集合差异均为 0；
- `bugsinpy_youtube-dl_7` 静态剩余方法数最少，为 108；
- 因此将 P2P 决策包中的推荐代表任务从 `youtube-dl_6` 修订为
  `youtube-dl_7`；
- 这仍只是静态效率证据，不允许据此 admission。

## 67. 2026-06-13 Git readiness upstream visibility repair

本轮小目标：

- 修复 `scripts/audit_execution_readiness.py` 只读取 `git status --short` 的
  可见性缺口；
- 让 readiness audit 能区分 working tree clean、local ahead、upstream
  behind 和 fully synced；
- 不执行 P2P，不改变实验标签。

背景：

- 当前本地 `main` 因 GitHub 连接重置曾出现 `ahead 1`；
- 旧 audit 的 `git.status_short` 在工作区干净时为空，无法提示“本地提交未推送”；
- 这会降低无人值守执行时的同步可见性。

执行边界：

- 只修改 readiness 审计脚本和对应文档；
- 不把 Git sync 状态混入模型/API readiness 结论；
- 若 push 因网络失败，记录为网络问题而不是仓库状态问题。

执行结果：

- `scripts/audit_execution_readiness.py` 改为读取
  `git status --short --branch`；
- audit JSON/Markdown 现在记录：
  - `branch_header`；
  - `upstream`；
  - `ahead` / `behind`；
  - `clean`；
  - `synced_with_upstream`；
  - 非 branch header 的 `status_short` entries；
- 当前 dirty 状态验证中，audit 正确报告 `ahead = 1`、
  `clean = false`、`synced_with_upstream = false`。

## 68. 2026-06-13 youtube-dl P2P decision consistency audit

本轮小目标：

- 将 `youtube-dl` P2P 决策包的一致性检查自动化；
- 审计 controlled probe 中的 clean-F2P `youtube-dl` 候选、静态最低成本代表、
  决策包推荐任务和命令模板是否一致；
- 不执行 P2P、不创建 P2P manifest、不修改实验标签。

执行边界：

- 只读取 `data/tasks/evp7_controlled_probe_results.json`、决策包和现有
  buggy/fixed checkout 源文件；
- 复用 `scripts/static_unittest_p2p_preflight.py` 的静态 AST 逻辑；
- 若推荐任务不是最低静态成本候选，或命令模板 task-id 与推荐不一致，则审计失败。

产物：

- 新增 `scripts/audit_youtubedl_p2p_decision.py`；
- 默认输出到 ignored `outputs/youtubedl_p2p_decision_audit/latest.json/md`。
