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
- 若推荐任务不是最低静态成本候选、命令模板 task-id 与推荐不一致，或命令模板
  `--fail-to-pass-nodeid` 与 controlled probe 中已建立的 F2P unittest 目标不一致，
  则审计失败。

产物：

- 新增 `scripts/audit_youtubedl_p2p_decision.py`；
- 默认输出到 ignored `outputs/youtubedl_p2p_decision_audit/latest.json/md`。

修订：

- 审计增加 `command_fail_to_pass_matches_probe` 检查，防止 P2P 命令模板使用
  与 retained F2P probe 不一致的 oracle nodeid。

## 69. 2026-06-13 youtube-dl P2P command packet no-run audit

本轮小目标：

- 在不执行 P2P 的前提下，把获批后要运行的 `youtube-dl_7` P2P 命令固化到
  决策审计输出；
- 检查推荐任务的 buggy/fixed checkout 是否存在；
- 检查输出 manifest 尚未存在；
- 明确记录该命令包仍需用户批准后才能执行。

执行边界：

- 只修改 `scripts/audit_youtubedl_p2p_decision.py` 和文档；
- 不执行 `scripts/build_pass_to_pass_scope.py`；
- 不创建 `data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json`；
- 不修改实验标签或 main cohort。

验收条件：

- 决策审计通过；
- 审计 JSON/Markdown 中包含 `command_packet.approval_required = true`；
- 审计 checks 包含并通过：
  - `recommended_buggy_checkout_exists`；
  - `recommended_fixed_checkout_exists`；
  - `command_packet_requires_approval`。

## 70. 2026-06-13 youtube-dl P2P command full-flag audit

本轮小目标：

- 增强 `scripts/audit_youtubedl_p2p_decision.py`，解析决策包中的 PowerShell
  command template；
- 将文档命令参数与 generated approval-gated command packet 的 expected flags
  完整比对；
- 不执行 P2P、不创建 P2P manifest。

新增检查：

- `decision_packet_command_flags_match_expected`；
- 覆盖 `task-id`、project、framework、unittest discovery 参数、F2P nodeid、
  scope type、runs、timeouts、batch size、`--batch-first`、static exclude
  tokens、out-dir 和 manifest-out。

## 71. 2026-06-13 P2P scope builder dry-run mode

本轮小目标：

- 为 `scripts/build_pass_to_pass_scope.py` 增加 `--dry-run`；
- 获批前可验证 `youtube-dl_7` command packet 的参数、checkout、scope type、
  test paths 和 manifest 目标；
- dry-run 不执行 collection、不运行测试、不创建 compat shim、不写 manifest。

执行边界：

- `--dry-run` 只能打印 JSON plan；
- 不创建 `outputs/p2p_scope_builds/...`；
- 不创建 `data/p2p_scopes/...`；
- 不改变实验标签或 cohort。

验收条件：

- `python -m py_compile scripts\build_pass_to_pass_scope.py` 通过；
- 对 `bugsinpy_youtube-dl_7` 运行 command packet 加 `--dry-run`，输出
  `will_execute_tests=false`、`will_write_manifest=false`、
  `manifest_out_exists=false`。

## 72. 2026-06-13 youtube-dl decision audit invokes builder dry-run

本轮小目标：

- 将 `scripts/build_pass_to_pass_scope.py --dry-run` 纳入
  `scripts/audit_youtubedl_p2p_decision.py`；
- 使一个 no-run decision audit 同时验证：
  - 决策包推荐与命令模板一致；
  - generated approval-gated command packet 一致；
  - 实际 P2P builder 接受该命令的 dry-run 参数；
  - dry-run 不执行测试、不写 manifest、不创建 output dir。

新增检查：

- `builder_dry_run_completed`；
- `builder_dry_run_no_test_execution`；
- `builder_dry_run_no_manifest_write`；
- `builder_dry_run_no_output_dir_creation`；
- `builder_dry_run_manifest_absent`；
- `builder_dry_run_scope_matches_expected`。

## 73. 2026-06-13 API pilot preflight report output

本轮小目标：

- 执行 readiness audit 建议的 strict local API preflight；
- 确认 `configs/api_pilot.local.json` 在 DeepSeek official /
  `deepseek-v4-pro` 下结构就绪；
- 为 `scripts/preflight_api_pilot.py` 增加可审计输出，避免只有终端结果。

执行边界：

- 不调用真实 API；
- 不执行新的 LLM run；
- 不修改 ignored local config 或 `.env`；
- 输出写入 ignored `outputs/api_pilot_preflight/latest.json/md`。

执行结果：

- strict preflight 通过：
  - `api_ready = true`；
  - `dry_run_ready = true`；
  - provider = `deepseek_official`；
  - model = `deepseek-v4-pro`；
  - candidates/evidence packets = 30/30；
  - conditions = `llm_only`、`evidence_first`。
- `scripts/preflight_api_pilot.py` 新增 `--out-json` 和 `--out-md`。
- `scripts/audit_execution_readiness.py` 现在读取
  `outputs/api_pilot_preflight/latest.json`，如果该报告对应当前
  `configs/api_pilot.local.json` 且 `api_ready/dry_run_ready` 均为 true，则不再
  反复提示运行 preflight。

## 74. 2026-06-13 goal completion audit covers youtube-dl P2P decision

本轮小目标：

- 修复 `scripts/audit_goal_completion.py` 对当前 controlled expansion 状态的
  覆盖缺口；
- 防止旧 API/paper/artifact 主流程已 complete 时，将仍待确认的
  `youtube-dl_7` P2P admission 决策误判为完成；
- 不执行 P2P、不创建 P2P manifest。

执行结果：

- `scripts/audit_goal_completion.py` 新增 required check：
  `youtube_dl_p2p_decision_resolved`；
- 该 check 要求：
  - youtube-dl decision audit passed；
  - `command_packet.approval_required = false`；
  - `data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json` 存在；
- 当前 audit 正确报告：
  - `complete = false`；
  - `missing_required = ["youtube_dl_p2p_decision_resolved"]`。

## 75. 2026-06-13 human input packet covers youtube-dl P2P decision

本轮小目标：

- 将 `scripts/write_human_input_packet.py` 与 goal completion frontier 对齐；
- 在交接包中显式暴露当前唯一未解决的人类决策：
  `youtube_dl_p2p_decision`；
- 不执行 P2P、不创建 P2P manifest、不调用真实 API。

执行边界：

- 只读取 ignored 决策审计输出
  `outputs/youtubedl_p2p_decision_audit/latest.json`；
- 交接包只记录 recommended task、approval gate、builder dry-run checks 和
  approval-gated command packet；
- 如果用户批准，只允许按决策包执行一次 bounded project-level P2P-broad
  attempt for `bugsinpy_youtube-dl_7`；
- 如果用户拒绝或要求停止，需要在计划中记录 stop/reject 决策，并停止
  youtube-dl expansion path。

验收条件：

- `outputs/handoff/human_input_packet.json/md` 的 missing required inputs 包含
  `youtube_dl_p2p_decision`；
- forbidden actions 明确禁止未批准时运行 `youtube-dl_7` P2P；
- 后续 readiness/goal completion audit 继续报告当前目标未完成，直到该决策被
  明确批准并完成 manifest，或被明确拒绝并修订计划。

## 76. 2026-06-13 readiness Markdown next-action consistency

本轮小目标：

- 修复 `outputs/readiness_audit/latest.md` 中 next actions 与 JSON
  `next_actions` 不一致的问题；
- 不执行真实 API、不执行 `youtube-dl_7` P2P、不创建新的 P2P manifest；
- 只修本地审计报告表达，避免后续快速交接时误以为仍需要重新跑 API smoke。

执行边界：

- `scripts/audit_execution_readiness.py` 的 JSON 逻辑已经能正确返回空
  `next_actions`；
- 本轮只修 Markdown fallback：当无 next action 时报告 `None.`；
- 验证后刷新 readiness/goal completion/handoff 报告，确认唯一硬缺口仍是
  `youtube_dl_p2p_decision_resolved`。

## 77. 2026-06-13 run-record ledger covers tool-augmented full run

本轮小目标：

- 将已有 `outputs/patch_verification_tool_augmented_full_001` 纳入
  experiment run-record ledger；
- 让 `scripts/audit_goal_completion.py` 要求 ledger 覆盖
  `tool_augmented_full_api`；
- 保持 prompt-only evidence-first 的负结论不变，只把
  `tool_augmented_evidence` 记录为条件性 tool-assisted claim 的证据。

执行边界：

- 不调用真实 API；
- 不重跑 full run；
- 只读取已有 `reviews.jsonl`、`metrics.json`、`run_completeness.json` 和
  `tool_augmented_full_gate.json`；
- ledger summary 需要区分 prompt-only positive claim 与 tool-augmented
  conditional claim。

## 78. 2026-06-13 handoff summary separates prompt-only and tool-augmented claims

本轮小目标：

- 修复 `outputs/handoff/pre_api_handoff.md` 的摘要歧义；
- 保持原 JSON 字段 `positive_paper_claim_ready` 作为 prompt-only 历史兼容字段；
- 新增并显示：
  - `prompt_only_positive_paper_claim_ready`；
  - `tool_augmented_claim_ready`。

执行边界：

- 不调用真实 API；
- 不运行 P2P；
- 不改变论文 claim，只让 handoff 摘要与 paper readiness、local quality gate
  的 claim 边界一致。

## 79. 2026-06-13 human input packet separates claim readiness

本轮小目标：

- 修复 `outputs/handoff/human_input_packet.md` 的摘要歧义；
- 保留 `positive_paper_claim_ready` 字段作为旧兼容字段，但其语义必须是
  prompt-only positive claim；
- 新增并显示：
  - `prompt_only_positive_paper_claim_ready`；
  - `tool_augmented_paper_claim_ready`。

执行边界：

- 不调用真实 API；
- 不运行 P2P；
- 不改变论文 claim；
- 只让 human-input packet 与 pre-API handoff、paper readiness、local quality
  gate 的 claim 边界一致。

## 80. 2026-06-13 approved youtube-dl_7 bounded P2P execution

本轮小目标：

- 根据用户明确回复 `1、批准 2、暂时不用管`，执行一次
  `bugsinpy_youtube-dl_7` bounded project-level P2P-broad；
- GitHub 同步暂时不作为本轮阻塞项；
- 将批准和执行记录写入
  `docs/experiments/evp7_youtubedl_p2p_execution_attempt_20260613.md`，避免只
  依赖聊天上下文。

执行边界：

- 只执行 `bugsinpy_youtube-dl_7`；
- 只使用已审计过的 command packet 参数；
- 不批量执行其他 youtube-dl P2P；
- 不调用模型 API；
- 若 P2P 失败，先诊断为执行链路、环境、数据/证据或实验设计问题，不继续扩量。

验收条件：

- 生成 `data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json`；
- 该 manifest 的 task、scope type、fail-to-pass nodeid、P2P broad tests 和
  buggy/fixed/reference run 状态可被本地审计验证；
- `audit_goal_completion.py` 不再依赖 pre-run no-run 审计里的
  `approval_required=true` 字段判断该决策未解决，而应读取批准记录和执行结果。

执行结果：

- 已执行一次批准命令；
- 工具层 40 分钟超时，未生成
  `data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json`；
- 只创建了 ignored 输出目录
  `outputs/p2p_scope_builds/bugsinpy_youtube-dl_7` 中的 compat shim；
- 超时后发现遗留进程：
  - builder 进程：`scripts/build_pass_to_pass_scope.py ... youtube-dl_7 ...`；
  - unittest 子进程正在运行动态生成的
    `test.test_download.TestDownload.*` 下载测试；
- 已终止这两个遗留进程；
- 诊断：当前 static source-token filter 不会排除动态生成的
  `TestDownload` nodeid，因为它们不对应 AST 中的静态 `test_` 方法。

当前 gate：

- 这次批准已被执行一次，但 P2P manifest 未生成；
- 继续执行需要新的 scope-policy 决策：是否允许为 youtube-dl 动态下载测试加入
  nodeid-level exclusion，例如排除 `test.test_download.TestDownload` 后重跑；
- 在该策略未确认前，不继续真实 P2P。

## 81. 2026-06-13 youtube-dl_7 dynamic-download nodeid exclusion rerun

本轮小目标：

- 根据用户最新确认，将明确的执行链路修复视为已批准：只为
  `bugsinpy_youtube-dl_7` 增加可审计的 nodeid-level exclusion；
- 先验证 `scripts/build_pass_to_pass_scope.py --dry-run` 是否记录该排除策略且
  不创建 manifest；
- dry-run 通过后，按同一 scope policy 重跑一次 bounded project-level P2P-broad。

执行边界：

- 只排除动态生成的 `test.test_download.TestDownload` 前缀；
- 不新增静态 token 规则来伪装该动态排除；
- 修复 unittest 静态源码扫描时，只允许把 dotted unittest nodeid 映射回同一
  测试文件，并展开同文件本地 helper；不做跨文件依赖分析；
- 不运行其他 youtube-dl task 的 P2P；
- 不调用模型 API；
- GitHub 同步仍按用户上一轮指示暂时不作为阻塞项；
- 若 rerun 再次超时或出现新的非明确 scope 分歧，停止并诊断，不继续改
  scope。

验收条件：

- builder dry-run 输出包含 `exclude_nodeid_prefixes`，且
  `will_execute_tests=false`、`will_write_manifest=false`；
- 若真实 P2P 完成，`data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json`
  存在，并且 manifest 记录：
  - `scope_policy.policy_name = youtube_dl_dynamic_download_nodeid_exclusion_v1`；
  - `exclude_nodeid_prefixes = ["test.test_download.TestDownload"]`；
  - `counts.exclusion_reason_counts.excluded_nodeid_prefix > 0`；
  - `p2p_broad_tests` 不包含该动态下载前缀。

中间诊断：

- 首次 nodeid-prefix rerun 再次工具层超时，未生成 manifest；
- 遗留进程显示卡在
  `test.test_age_restriction.TestAgeRestriction.test_youtube`；
- 该测试通过同文件 helper 调用 `YoutubeDL(...).download(...)`，但旧静态扫描
  对 unittest dotted nodeid 没有映射源码文件，也没有展开本地 helper；
- 已将该问题定位为执行链路 bug，而不是新的研究 scope 决策。

执行结果：

- builder dry-run 通过，确认不会执行测试、不会写 manifest，且记录
  `exclude_nodeid_prefixes = ["test.test_download.TestDownload"]`；
- 修复 unittest dotted nodeid 静态源码映射和同文件 helper 展开后，真实 P2P
  rerun 完成；
- 已生成
  `data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json`；
- manifest 统计：
  - collected/common tests = 1472；
  - `excluded_nodeid_prefix` = 1297；
  - `excluded_static_external_dependency` = 64；
  - `excluded_fail_to_pass_oracle` = 1；
  - included `p2p_broad_tests` = 108；
  - `p2p_broad_tests` 不包含 `test.test_download.TestDownload` 前缀。

验证：

- `python -m py_compile scripts\build_pass_to_pass_scope.py` 通过；
- 静态源码验证确认
  `test.test_age_restriction.TestAgeRestriction.test_youtube` 被
  `excluded_static_external_dependency` 捕获；
- `audit_goal_completion.py` 输出 `complete=true`；
- `write_human_input_packet.py` 输出 `missing=[]`；
- `run_local_quality_gate.py` 输出 `passed=true`。

当前 gate：

- `youtube-dl_7` 的 project-level P2P-broad admission blocker 已解决；
- 该结果是带 `youtube_dl_dynamic_download_nodeid_exclusion_v1` scope policy 的
  P2P manifest，不等于无排除的 full test-suite claim；
- GitHub 同步按用户指示暂时不作为阻塞项，本地分支仍需后续同步。

## 82. 2026-06-13 handoff packet reflects resolved youtube-dl manifest

本轮小目标：

- 修复 `youtube-dl_7` manifest 已存在后，人类输入包仍展示旧 approval-gated
  P2P command 的交接歧义；
- 修复 goal completion audit 中仍使用“等待 manifest 或停止”的旧 boundary 文案；
- 不重新运行 P2P，不修改 scope policy，不调用 API。

执行边界：

- manifest 存在时，`write_human_input_packet.py` 将
  `approval_required=false`，并不再输出旧重跑命令；
- `audit_goal_completion.py` 在 evidence 中展示 manifest scope policy 和
  P2P-broad 数量；
- 这只是报告同步，不改变 `data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json`。

验收条件：

- human-input packet 仍为 `missing=[]`；
- packet 中 youtube-dl decision 显示 approval required = no；
- packet 不再包含未带 nodeid exclusion 的旧 approval command；
- goal completion 仍为 `complete=true`。

## 83. 2026-06-13 youtube-dl_7 formal admission and candidate validation

本轮小目标：

- 将已完成 project-level P2P-broad manifest 的 `bugsinpy_youtube-dl_7` 走完
  formal admission 链路；
- 先补 retained oracle 和最小候选集，再做 retained-oracle + P2P-broad
  validation；
- 只有 candidate validation 通过后，才更新 cohort registry、EVP-7 task
  manifest、candidate manifest 和 evidence artifacts。

当前事实：

- `data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json` 已存在；
- manifest 保留 108 个 P2P-broad tests；
- 当前 `data/cohorts/task_cohort_registry.json` 的 `p2p_broad_main` 仍是 7
  个 task，尚不包含 `bugsinpy_youtube-dl_7`；
- 因此当前正式主样本 bug 数仍是 7，不是 8。

执行边界：

- 不再重跑 P2P scope construction；
- 不新增别的 youtube-dl task；
- 不调用模型 API；
- 候选集先采用最小 admission slice：reference correct、empty/no-op negative、
  partial/incorrect negative、irrelevant negative；
- 如果 reference patch 或 oracle 无法稳定验证，停止诊断，不更新 cohort。

验收条件：

- 新增 `scripts/oracles/youtubedl_7_js_to_json.py`，能在 buggy checkout 失败、
  fixed checkout 通过；
- 生成 `outputs/youtubedl7_candidate_validation_001/candidates.jsonl`；
- retained-oracle validation 全部符合预期；
- P2P-broad validation 输出存在且 correct reference 通过 108 个 P2P-broad
  tests，negative candidates 不被误标为 correct；
- 通过后再把 `bugsinpy_youtube-dl_7` 纳入 registry，并重建 EVP-7 task、
  candidate、evidence artifacts，使主 cohort 从 7 提升到 8。

中间诊断：

- retained-oracle validation 已通过：4 个候选全部 apply，reference 通过
  oracle，3 个 negative 未通过 oracle；
- 首次 P2P validation 将 reference 标为 `incorrect_regression`，原因不是
  patch 回归，而是 `validate_candidates_with_p2p.py` 对 unittest scope 仍调用
  pytest，pytest 无法识别 `test.test_utils.TestUtil...` dotted nodeid；
- 已将该问题定位为执行链路 bug：candidate-level P2P validator 必须根据
  manifest 的 `test_framework` 使用 `python -m unittest -q` 执行 unittest
  scope。

执行结果：

- 新增 retained oracle：
  `scripts/oracles/youtubedl_7_js_to_json.py`；
- 新增 admission candidate builder：
  `scripts/build_youtubedl7_candidates.py`；
- retained-oracle validation 通过：
  - record_count = 4；
  - patch_applied_count = 4；
  - oracle_all_passed_count = 1；
  - validation_status_counts = `{"validated": 4}`；
- 已修复 `scripts/validate_candidates_with_p2p.py` 的 unittest P2P dispatch；
- 已同步修复 `scripts/run_evp7_visible_tests.py` 的 unittest visible-test
  dispatch，避免 admission 后 E4 复现链路继续误用 pytest；
- P2P-broad validation 通过：
  - record_count = 4；
  - retained_oracle_passed_count = 1；
  - p2p_broad_test_count = 108；
  - label_with_p2p_broad_counts =
    `{"correct_under_f2p_and_p2p_broad": 1, "incorrect_issue_not_fixed": 3}`；
- 已将 `bugsinpy_youtube-dl_7` 纳入
  `data/cohorts/task_cohort_registry.json` 的 `p2p_broad_main`；
- 已重建 EVP-7 task/candidate/evidence/tool-baseline/schema-dry-run/prompt
  manifest artifacts；
- 当前正式主 cohort 已从 7 提升到 8：
  - main_task_count = 8；
  - main_projects = 5；
  - promoted candidates = 46；
  - correct references = 8；
  - issue-not-fixed negatives = 38；
  - E0/E2/E4/E6 packets = 184；
  - G5 prompt manifest records = 184。

当前边界：

- 本节结束时的边界曾是：旧 DeepSeek official G5 full run 只覆盖
  admission 前 168 packets，当前 8-task / 184-packet cohort 只完成
  structural/no-API readiness；
- 第 84 节已经补跑 fresh 184-packet DeepSeek V4 full run，因此当前
  8-task cohort 已有 real LLM result；旧 168-run 只保留为历史记录。

下一步：

1. 先完成文档、索引、经验记录和质量门同步；
2. 如果质量门通过，提交本轮 admission 变更；
3. 第 84 节 fresh run 完成后，下一步转向质量审计与 15-20 bugs controlled
   expansion 决策。

## 84. 2026-06-13 fresh 184-packet DeepSeek V4 G5 run

本轮小目标：

- 在 `bugsinpy_youtube-dl_7` admission 后，对当前 8-task / 46-candidate /
  184-packet EVP-7 cohort 执行 fresh real LLM G5 run；
- 先做 strict preflight，再做 4-packet smoke；
- smoke 通过后才执行 full 184-packet run；
- 原始模型响应只写入 ignored `outputs/evp7_g5_llm_002/`，不覆盖旧
  `outputs/evp7_g5_llm_001/`。

当前事实：

- `configs/evp7_g5_llm.local.json` 已存在且被 `.gitignore` 忽略；
- local config 已确认：
  - provider = `deepseek_official`；
  - model = `deepseek-v4-pro`；
  - full_run_permission = true；
  - evidence packets = `data/evidence/evp7_evidence_packets.jsonl`；
  - prompt manifest = `data/reviews/evp7_g5_llm_prompt_manifest.jsonl`；
- `.env` 中存在 DeepSeek API 相关变量名；
- 当前 no-API artifacts 已通过：
  - candidate_count = 46；
  - prompt_record_count = 184；
  - level_counts = E0/E2/E4/E6 各 46；
  - leakage failed count = 0。

执行边界：

- 不修改 prompt id；
- 不改变 evidence packet 内容；
- 不把 raw model responses 写入 tracked data；
- smoke 不通过时不得继续 full run；
- full run 后只生成 raw-output-free tracked summary 与必要的 plan/doc
  更新。

验收条件：

- strict preflight `api_ready=true`；
- smoke run 写入 `outputs/evp7_g5_llm_002/smoke_reviews.jsonl`、
  `smoke_metrics.json`、`smoke_summary.json`；
- smoke parse invalid rate 不超过 0.2；
- full run 写入 `outputs/evp7_g5_llm_002/reviews.jsonl`、`metrics.json`、
  `workflow_summary.json`；
- full run 后运行 summary/postprocess 生成 tracked raw-output-free summary；
- 同步 README/INDEX/plan/experience/prompt log 中 184-run 的真实结果边界；
- 运行 local quality gate 和 goal completion audit；
- 提交本轮 tracked 结果，GitHub push 仍按用户之前指示暂时不处理。

中间结果：

- strict preflight 已通过：
  - config = `configs/evp7_g5_llm.local.json`；
  - structural_ready = true；
  - api_ready = true；
  - prompt_manifest_record_count = 184；
  - candidate_count = 46；
- 4-packet smoke 已完成：
  - output dir = `outputs/evp7_g5_llm_002/`；
  - review_count = 4；
  - parse_status = `{"valid": 4}`；
  - invalid_rate = 0.0；
  - decisions = `{"escalate": 4}`；
  - stop condition 未触发，可以进入 full 184-packet run。

执行结果：

- full 184-packet run 已完成：
  - command = `scripts/run_evp7_g5_llm_workflow.py --execute --concurrency 6`；
  - reviews = `outputs/evp7_g5_llm_002/reviews.jsonl`；
  - metrics = `outputs/evp7_g5_llm_002/metrics.json`；
  - workflow summary = `outputs/evp7_g5_llm_002/workflow_summary.json`；
  - review_count = 184；
  - unique_review_ids = 184；
  - parse_status = `{"valid": 183, "invalid": 1}`；
  - invalid_output_rate = 0.005435；
  - invalid record = `evp7_candidate_0004__E2`，原因是空响应导致
    `invalid_json:No JSON object found in model response`；
  - decision_counts =
    `{"accept": 6, "escalate": 64, "invalid_output": 1, "reject": 113}`；
  - G5 signal claim status =
    `real_llm_verifier_signal_observed_on_evp7`。

核心指标：

- E0：FAR = 0.0，correct recall = 0.0，escalation rate = 0.565217；
- E2：FAR = 0.0，correct recall = 0.0，escalation rate = 0.608696，
  invalid_output_rate = 0.021739；
- E4：FAR = 0.0，accepted precision = 1.0，correct recall = 0.375，
  escalation rate = 0.086957，Evidence Gain vs E0 = 7.5；
- E6：FAR = 0.0，accepted precision = 1.0，correct recall = 0.375，
  escalation rate = 0.130435，Evidence Gain vs E0 = 7.0。

已生成 tracked raw-output-free summary：

- `data/reviews/evp7_g5_llm_full_run_summary.json`；
- `docs/experiments/evp7_g5_llm_full_run_result.md`。

当前下一步：

1. 同步 README、INDEX、protocol、roadmap、prompt log、experience；
2. 运行 local quality gate 和 goal completion audit；
3. 提交 tracked summary/doc updates；
4. 然后进入 15-20 bugs controlled expansion 的下一项决策，不再重复跑同一
   184-packet full run。

验证结果：

- `python -m py_compile` 覆盖 G5 preflight、workflow、summary 脚本，通过；
- strict preflight after full run 通过：
  - structural_ready = true；
  - api_ready = true；
- `scripts/summarize_evp7_g5_llm_full_run.py` 默认输入已改为
  `outputs/evp7_g5_llm_002/`，无参运行确认仍生成 184-run summary；
- local quality gate 通过；
- goal completion audit 通过。

## 85. 2026-06-13 184-run quality audit and claim boundary

本轮小目标：

- 对当前 184-packet DeepSeek V4 G5 full run 做 tracked、可复现的质量审计；
- 明确哪些 claim 可以写、哪些 claim 不能写；
- 不重新调用 API，不读取或复制 raw model responses；
- 不新增 bug，不进入 controlled expansion 实验执行。

当前事实：

- tracked summary 已存在：
  `data/reviews/evp7_g5_llm_full_run_summary.json`；
- full run 覆盖当前 8-task / 46-candidate / 184-packet cohort；
- invalid output 为 1 条空响应；
- E4/E6 false accept rate = 0.0，accepted precision = 1.0，
  correct recall = 0.375；
- G5 signal claim status =
  `real_llm_verifier_signal_observed_on_evp7`。

审计边界：

- 审计只读取 raw-output-free tracked summary；
- 审计不把 raw response text 写入 tracked files；
- 审计结论只能支持 EVP-7 pilot-level signal claim；
- 不能写成 scale-generalized paper claim；
- 不能写成 LLM 超过 tool-only baseline，因为 tool-only visible-tests 当前
  correct recall = 0.875，高于 DeepSeek E4/E6 的 0.375。

验收条件：

- 新增或更新质量审计脚本，输出 JSON + Markdown；
- 审计检查：
  - review_count = 184；
  - unique_review_ids = 184；
  - raw_outputs_tracked = false；
  - invalid_output_count = 1；
  - invalid_output_rate = 0.005435；
  - E4/E6 false_accept_rate = 0.0；
  - E4/E6 accepted_precision = 1.0；
  - E4/E6 correct_recall = 0.375；
  - G5 signal observed；
- 同步 README、INDEX、protocol/experiment docs、experience notes；
- 运行最小验证、local quality gate、goal completion audit；
- 提交 tracked 结果，仍不 push。

执行结果：

- 新增质量审计脚本：
  `scripts/audit_evp7_g5_full_run_quality.py`；
- 生成 tracked audit：
  - `data/reviews/evp7_g5_full_run_quality_audit.json`；
  - `docs/experiments/evp7_g5_full_run_quality_audit.md`；
- 审计结果：
  - quality_status = `passed_with_limitations`；
  - review_count = 184；
  - unique_review_ids = 184；
  - raw_outputs_read = false；
  - raw_outputs_tracked = false；
  - invalid_output_count = 1；
  - invalid_output_rate = 0.005435；
  - E4/E6 false_accept_rate = 0.0；
  - E4/E6 accepted_precision = 1.0；
  - E4/E6 correct_recall = 0.375；
  - E4/E6 Evidence Gain vs E0 = 7.5 / 7.0；
  - G5 signal observed。

当前 claim 边界：

- 支持：
  - 当时 EVP-7 8-task/46-candidate/184-packet run 观察到真实 DeepSeek verifier
    outputs 中的 evidence-visibility signal；
  - E4/E6 在零 observed false accepts 下接受 3/8 correct patches；
  - E4/E6 相对 E0 提高 correct recall 并产生正 Evidence Gain；
- 不支持：
  - scale-generalized paper claim；
  - LLM 超过 deterministic visible-test tool-only baseline；
  - E6 严格优于 E4；
  - DeepSeek 真实计费成本已知。

下一步：

- 进入 15-20 bugs controlled expansion 的执行决策；
- 继续沿用 admission gate：F2P、project-level P2P-broad、candidate
  construction、candidate revalidation 全部通过后才能入主 cohort；
- 不重复跑当前 184-packet G5 full run。

## 86. 2026-06-13 ninth bug admission: youtube-dl_6

本轮小目标：

- 完成第 9 个正式主 cohort bug admission；
- 只在已 clean-F2P 的 `youtube-dl` 候选中选最低成本目标推进；
- 目标选择为 `bugsinpy_youtube-dl_6`，因为既有 no-run static sweep 中它是
  除已 admitted `youtube-dl_7` 外的最低静态 P2P 成本：
  - `youtube-dl_6`: 154 common static unittest methods，111 remaining；
  - `youtube-dl_5`: 191 common static unittest methods，137 remaining；
  - `youtube-dl_4`: 196 common static unittest methods，141 remaining；
  - `youtube-dl_2/3/11` 更大。

执行边界：

- 不调用模型 API；
- 不重复跑当前 184-packet G5 full run；
- 不做 dependency install、compat shim 或 task-file downgrade；
- 先用 `build_pass_to_pass_scope.py --dry-run` 验证 command；
- 真实 P2P 若发现动态下载/网络测试进入 scope，先诊断并采用可审计的
  nodeid exclusion policy，不能静默扩大 scope policy；
- P2P manifest 通过后，才能构造 candidate slice 和做 retained-oracle +
  P2P-broad validation；
- validation 通过后，才更新 registry 和 EVP-7 artifacts，使主 cohort 从
  8 提升到 9。

验收条件：

- `bugsinpy_youtube-dl_6` retained F2P oracle 明确；
- 生成 tracked P2P manifest；
- 构造最小 admission candidate slice：reference、noop、partial/incorrect、
  irrelevant；
- retained-oracle validation 全部符合预期；
- P2P-broad validation 中 reference 通过、negative 不被误标为 correct；
- `data/cohorts/task_cohort_registry.json` 纳入第 9 个主任务；
- EVP-7 task/candidate/evidence/baseline/schema/prompt artifacts 重建并通过
  no-API gates；
- README/INDEX/plan/experience/experiment record 同步；
- local quality gate 和 goal completion audit 通过；
- 提交本轮 tracked 结果，仍不 push。

本轮执行更新：

- `bugsinpy_youtube-dl_6` static no-run preflight 通过：
  - static unittest methods = 154；
  - remaining after static exclusions = 111；
  - common remaining = 111；
  - buggy-only/fixed-only = 0。
- `build_pass_to_pass_scope.py --dry-run` 通过，未写 manifest。
- 第一次真实 P2P 构建在工具级 40 分钟超时，未生成 manifest。
- 超时诊断：
  - 残留 builder 子进程正在执行
    `test.test_download.TestDownload.*` 动态下载测试；
  - 这与 `youtube-dl_7` 已记录问题相同，属于动态生成下载用例进入
    project-level scope 的执行链路问题；
  - 不是 `youtube-dl_6` admission 语义失败。
- 修订后的 rerun policy：
  - policy name: `youtube_dl_dynamic_download_nodeid_exclusion_v1`；
  - excluded nodeid prefix: `test.test_download.TestDownload`；
  - retained F2P oracle 仍为
    `test.test_utils.TestUtil.test_parse_dfxp_time_expr`；
  - 先 dry-run，再真实 rerun；
  - 不扩大到其他未审计 exclusion。

完成结果：

- 真实 P2P rerun 完成，生成
  `data/p2p_scopes/bugsinpy_youtube-dl_6_p2p_broad.json`：
  - common collected unittest nodeids = 1525；
  - excluded dynamic download nodeids = 1345；
  - excluded static external-dependency tests = 67；
  - excluded retained F2P oracle = 1；
  - retained P2P-broad tests = 110；
  - retained tests 中没有 `test.test_download.TestDownload` 前缀。
- 新增 retained oracle：
  `scripts/oracles/youtubedl_6_dfxp_time.py`；
  - buggy checkout fail；
  - fixed checkout pass。
- 新增 candidate builder：
  `scripts/build_youtubedl6_candidates.py`；
  - admission slice = 4 candidates；
  - reference / noop / partial / irrelevant。
- retained-oracle validation 通过：
  - record_count = 4；
  - patch_applied_count = 4；
  - oracle_ran_count = 4；
  - oracle_all_passed_count = 1；
  - all_validated = true。
- P2P-broad validation 通过：
  - record_count = 4；
  - retained_oracle_passed_count = 1；
  - p2p_broad_test_count = 110；
  - label counts =
    `correct_under_f2p_and_p2p_broad: 1`,
    `incorrect_issue_not_fixed: 3`。
- 已将 `bugsinpy_youtube-dl_6` 纳入
  `data/cohorts/task_cohort_registry.json` 的 `p2p_broad_main`。
- 已重建 EVP-7 no-API artifacts：
  - main tasks = 9；
  - projects = 5；
  - promoted candidates = 50；
  - correct reference candidates = 9；
  - issue-not-fixed candidates = 41；
  - evidence packets = 200；
  - E0/E2/E4/E6 各 50；
  - G1 packet completeness = passed；
  - G2 leakage audit = passed；
  - G3 tool-only baseline readiness = passed；
  - G4 schema stability = passed；
  - G5 prompt manifest = 200 records，passed_without_api；
  - example preflight structural_ready = true，api_ready = false。
- 新增实验记录：
  `docs/experiments/youtubedl6_candidate_validation.md`。
- README、docs/INDEX、engineering notes 已同步。

当前边界：

- 第 9 个 bug 已完成 admission，主 cohort 数量已经提升；
- 旧 DeepSeek V4 真实 G5 full run 仍只覆盖
  8-task / 46-candidate / 184-packet cohort；
- 新的 9-task / 50-candidate / 200-packet cohort 只完成 no-API structural
  gates，尚未执行 fresh real LLM verifier run；
- 因此不能把旧 184-run 的模型结果 claim 直接外推到第 9 个样本。

## 87. 2026-06-13 fresh 200-packet DeepSeek V4 G5 run

本轮小目标：

- 对当前 9-task / 50-candidate / 200-packet EVP-7 cohort 执行 fresh
  DeepSeek V4 G5 verifier run；
- 先验证 strict preflight 和 check-only workflow；
- 先跑 smoke，再根据 stop condition 决定是否进入 full 200-packet run；
- 只写 raw responses 到 ignored `outputs/evp7_g5_llm_003/`，tracked
  artifacts 只保留 raw-output-free summary、metrics 和 quality audit。

执行边界：

- 使用已存在 ignored local config：
  `configs/evp7_g5_llm.local.json`；
- 当前 local config 指向 `deepseek_official` / `deepseek-v4-pro`；
- 不修改 prompt；
- 不修改 candidate labels；
- 不把 raw model outputs 加入 Git；
- 如果 strict preflight、check-only、smoke parse、invalid-output rate 或
  cost/认证检查失败，停止 full run，先诊断；
- 旧 184-packet run 继续保留为 historical 8-task evidence，不覆盖其 claim
  边界。

验收条件：

- strict preflight 对 200-packet artifacts 返回 `api_ready=true`；
- check-only workflow 不调用 API；
- smoke run 通过 schema / parse / stop-condition 检查；
- full 200-packet run 完成后生成 raw-output-free tracked summary；
- metric scaffold 和 quality audit 覆盖 200 records；
- README/INDEX/plan/experience/experiment docs 同步；
- 提交本轮 tracked 结果，除非 GitHub sync 被重新启用，否则仍不 push。

执行更新：

- strict preflight 已通过：
  - config = `configs/evp7_g5_llm.local.json`；
  - api_provider = `deepseek_official`；
  - model = `deepseek-v4-pro`；
  - prompt manifest records = 200；
  - evidence packets = 200；
  - api_ready = true；
  - api_call_attempted = false。
- check-only workflow 已通过：
  - structural_ready = true；
  - api_ready = true；
  - model_call_attempted = false。
- smoke run 已完成：
  - command output dir = `outputs/evp7_g5_llm_003/`；
  - reviews = `smoke_reviews.jsonl`；
  - review_count = 4；
  - parse valid = 4/4；
  - invalid output count = 0；
  - decisions = 3 escalate, 1 accept；
  - stop condition 未触发，可以进入 full 200-packet run。
- full 200-packet run 已完成：
  - reviews = `outputs/evp7_g5_llm_003/reviews.jsonl`；
  - metrics = `outputs/evp7_g5_llm_003/metrics.json`；
  - workflow summary = `outputs/evp7_g5_llm_003/workflow_summary.json`；
  - review_count = 200；
  - unique_review_ids = 200；
  - parse valid = 199/200；
  - invalid output = 1，位于 `evp7_candidate_0021__E4`，
    原因为 `invalid_suspected_failure_type:test_overfitting`；
  - E0/E2/E4/E6 各 50 条；
  - G5 signal status = `real_llm_verifier_signal_observed_on_evp7`。
- full-run summary 和 quality audit 已生成 tracked artifacts：
  - `data/reviews/evp7_g5_llm_full_run_summary.json`；
  - `docs/experiments/evp7_g5_llm_full_run_result.md`；
  - `data/reviews/evp7_g5_full_run_quality_audit.json`；
  - `docs/experiments/evp7_g5_full_run_quality_audit.md`。
- quality audit 结果为 `passed_with_limitations`：
  - E4 false_accept_rate = 0.0；
  - E4 accepted_precision = 1.0；
  - E4 correct_recall = 0.111111；
  - E4 evidence_gain_vs_e0 = 5.0；
  - E6 false_accept_rate = 0.0；
  - E6 accepted_precision = 1.0；
  - E6 correct_recall = 0.222222；
  - E6 evidence_gain_vs_e0 = 4.75。

当前边界：

- 可以支持 9-task / 50-candidate / 200-packet EVP-7 pilot 中的
  evidence-visibility signal；
- 不能 claim scale-generalized result；
- 不能 claim DeepSeek verifier 优于 deterministic visible-test tool-only
  baseline；
- DeepSeek 官方响应 usage 未给出可计费价格，cost claim 仍保持 unknown；
- raw model outputs 只保留在 ignored `outputs/evp7_g5_llm_003/`。

## 88. 2026-06-13 tenth bug admission attempt: youtube-dl_5

本轮小目标：

- 在完成 200-packet G5 run 后，继续 controlled expansion；
- 目标选择 `bugsinpy_youtube-dl_5`，因为它是剩余 clean-F2P
  `youtube-dl` 候选中静态 P2P 成本最低的任务：
  - `youtube-dl_5`: 191 common static unittest methods，137 remaining；
  - `youtube-dl_4`: 196 common static unittest methods，141 remaining；
  - `youtube-dl_2/3/11` 更大；
- 先做 no-run static preflight 和 builder dry-run；
- 只有 dry-run 通过后，才执行 bounded project-level unittest P2P-broad；
- P2P manifest 合格后，才进入 candidate construction 和 retained-oracle +
  P2P-broad revalidation。

执行边界：

- 复用已获准的 `youtube_dl_dynamic_download_nodeid_exclusion_v1` scope
  policy；
- 排除动态生成下载测试 nodeid 前缀
  `test.test_download.TestDownload`；
- 保留 `youtube-dl_5` 的 F2P oracle
  `test.test_utils.TestUtil.test_unified_timestamps`，不得把 oracle 纳入
  P2P-broad；
- 不修改 prompt、不调用真实 LLM API、不修改 candidate labels；
- 不引入 dependency shim、fixture shim 或 task-file P2P 降级；
- 若 static preflight、builder dry-run、P2P construction 或 manifest quality
  失败，先诊断，不进入 candidate validation。

验收条件：

- static preflight 输出与既有成本预期一致或更低；
- builder dry-run 不创建 manifest；
- real P2P manifest 包含 project-level unittest P2P-broad scope；
- manifest 排除 F2P oracle 和动态下载 nodeids；
- retained P2P-broad tests 数量 >= 3；
- 通过后同步 plan、experience、INDEX/README 和实验记录。

执行更新：

- 第一次 static preflight 使用了不完整 token set，得到 191 total /
  182 remaining，与既有 137 remaining 预期不一致；已诊断为命令复现问题，
  未进入真实 P2P。
- 使用 canonical static tokens 后，static preflight 复现预期：
  - total static methods = 191；
  - excluded by static tokens = 54；
  - remaining after static exclusions = 137；
  - buggy/fixed remaining set diff = 0。
- builder dry-run 通过：
  - fail-to-pass oracle =
    `test.test_utils.TestUtil.test_unified_timestamps`；
  - scope type = `project_level_p2p_broad`；
  - test framework = `unittest`；
  - exclude nodeid prefix = `test.test_download.TestDownload`；
  - manifest write = false。
- real P2P-broad construction 已完成：
  - manifest = `data/p2p_scopes/bugsinpy_youtube-dl_5_p2p_broad.json`；
  - collected tests = 1890；
  - excluded dynamic download nodeids = 1673；
  - excluded static external-dependency tests = 80；
  - excluded fail-to-pass oracle = 1；
  - excluded buggy-baseline failures = 8；
  - retained P2P-broad tests = 128；
  - retained dynamic download nodeids = 0。
- 新增 oracle 和 candidate builder：
  - `scripts/oracles/youtubedl_5_unified_timestamps.py`；
  - `scripts/build_youtubedl5_candidates.py`。
- retained-oracle validation 已通过 admission gate：
  - candidates = 4；
  - patch_applied = 4/4；
  - oracle_ran = 4/4；
  - oracle_all_passed = 1。
- candidate-level P2P validation 已通过：
  - P2P-broad test count = 128；
  - labels = 1 `correct_under_f2p_and_p2p_broad`,
    3 `incorrect_issue_not_fixed`。
- 已将 `bugsinpy_youtube-dl_5` 纳入
  `data/cohorts/task_cohort_registry.json` 的 `p2p_broad_main`。
- 已重建 EVP-7 no-API artifacts：
  - main tasks = 10；
  - projects = 5；
  - promoted candidates = 54；
  - correct reference candidates = 10；
  - issue-not-fixed candidates = 44；
  - evidence packets = 216；
  - E0/E2/E4/E6 各 54；
  - visible outcomes = 54，51 completed / 3 error；
  - visible tool summaries = 54 complete；
  - G1 packet completeness = passed；
  - G2 leakage audit = passed；
  - G3 tool-only baseline readiness = passed；
  - G4 schema stability = passed；
  - G5 prompt manifest = 216 records，passed_without_api；
  - example preflight structural_ready = true，api_ready = false。
- 新增实验记录：
  `docs/experiments/youtubedl5_candidate_validation.md`。

当前边界：

- 第 10 个 bug 已完成 admission，主 structural cohort 数量已经提升；
- 最新真实 DeepSeek V4 G5 full run 仍只覆盖上一轮
  9-task / 50-candidate / 200-packet cohort；
- 当前 10-task / 54-candidate / 216-packet cohort 已完成 no-API gates，
  但尚未执行 fresh real LLM verifier run；
- 因此不能把旧 200-run 的模型结果 claim 直接外推到第 10 个样本。

## 89. 2026-06-13 fresh 216-packet DeepSeek V4 G5 run

背景：

- 第 88 节已经完成 `bugsinpy_youtube-dl_5` admission；
- 当前 structural cohort 已提升到 10 tasks / 54 candidates / 216 packets；
- `configs/evp7_g5_llm.local.json` 仍指向
  `deepseek_official` / `deepseek-v4-pro`，且 full-run permission 已为 true；
- 为避免覆盖旧 run，本轮 raw outputs 只写入 ignored
  `outputs/evp7_g5_llm_004/`。

本轮小目标：

1. 对 216-packet cohort 运行 local strict preflight；
2. 执行 4-packet smoke，确认 API、JSON parse 和 schema 仍稳定；
3. smoke 通过后执行 216-packet full run；
4. 只把 tracked summary、quality audit 和文档更新纳入 Git；
5. raw model responses 保持在 ignored `outputs/evp7_g5_llm_004/`。

边界：

- 不修改 prompt、candidate labels、evidence packets 或 P2P manifests；
- 不读取或提交 raw model response 正文；
- 若 strict preflight、smoke、JSON parse、API auth 或 full-run summary 失败，
  立即停止并诊断；
- 旧 200-run 结果继续保留为历史，不再作为当前 216-packet cohort 的最新模型证据。

验收条件：

- local strict preflight: structural_ready=true, api_ready=true；
- smoke: model_call_attempted=true, invalid_json 不超过既有 stop 条件；
- full run: 216 review records，E0/E2/E4/E6 各 54；
- tracked summary 明确记录 provider/model、run size、invalid-output rate、主要指标；
- README、INDEX、experiment report、current plan 和 engineering notes 同步更新。

执行更新：

- local strict preflight 已通过：
  - config = `configs/evp7_g5_llm.local.json`；
  - provider/model = `deepseek_official` / `deepseek-v4-pro`；
  - structural_ready = true；
  - api_ready = true；
  - prompt records = 216；
  - candidates = 54；
  - E0/E2/E4/E6 各 54。
- 4-packet smoke 已完成：
  - output dir = `outputs/evp7_g5_llm_004/`；
  - model_call_attempted = true；
  - review_count = 4；
  - parse_status = 4 valid / 0 invalid；
  - stop condition 未触发。
- full 216-packet run 已完成：
  - command output = `outputs/evp7_g5_llm_004/reviews.jsonl`,
    `metrics.json`, `workflow_summary.json`；
  - concurrency = 6；
  - review_count = 216；
  - E0/E2/E4/E6 各 54；
  - parse-valid = 215；
  - invalid = 1，位置为 `evp7_candidate_0034__E4`，
    reason = `invalid_json:No JSON object found in model response`；
  - raw responses 仍只在 ignored `outputs/`。
- tracked summary 已刷新：
  - `data/reviews/evp7_g5_llm_full_run_summary.json`；
  - `docs/experiments/evp7_g5_llm_full_run_result.md`。
- 当前主要指标：
  - E0: accept=1, escalate=32, reject=21, FAR=0.0, correct_recall=0.1；
  - E2: escalate=26, reject=28, FAR=0.0, correct_recall=0.0；
  - E4: accept=1, escalate=9, reject=43, invalid=1, FAR=0.0,
    correct_recall=0.1, Evidence Gain vs E0 = 4.75；
  - E6: accept=2, escalate=8, reject=44, FAR=0.0,
    correct_recall=0.2, Evidence Gain vs E0 = 6.0。
- `scripts/audit_evp7_g5_full_run_quality.py` 原先硬编码
  200 records / 50 candidates / 9-task wording，导致 216-run 审计失败；
  已修为从 summary 动态读取 review count、level count 和 invalid rate。
- 质量审计已通过：
  - `data/reviews/evp7_g5_full_run_quality_audit.json`；
  - `docs/experiments/evp7_g5_full_run_quality_audit.md`；
  - quality_status = `passed_with_limitations`；
  - raw_outputs_read = false；
  - raw_outputs_tracked = false。

当前边界：

- 最新真实 DeepSeek V4 G5 full run 已覆盖当前
  10-task / 54-candidate / 216-packet cohort；
- 该 run 支持 bounded pilot observations：证据层级带来 metric variation，
  E4/E6 保持 zero false accepts 和 accepted precision 1.0；
- 仍不能 claim：
  - scale-generalized paper result；
  - LLM 优于 deterministic visible-test tool-only baseline；
  - E6 严格优于 E4；
  - DeepSeek 真实计费成本已知。

## 90. 2026-06-13 controlled expansion attempt: youtube-dl_2

背景：

- 216-packet DeepSeek V4 G5 run 已完成并通过 raw-output-free quality audit；
- controlled expansion readiness 已刷新到当前 10-task registry；
- metadata-promising pool 没有新的低风险 fresh-project lane；
- `bugsinpy_youtube-dl_2` 已在 controlled probe 中建立 F2P：
  - buggy fails；
  - fixed passes；
  - target = `test.test_InfoExtractor.TestInfoExtractor.test_parse_mpd_formats`；
  - P2P-broad 尚未尝试。
- 该任务属于已经验证过的 youtube-dl unittest family，可复用
  `youtube_dl_dynamic_download_nodeid_exclusion_v1`，但仍必须重新经过
  static preflight、builder dry-run、real P2P 和 manifest quality gate。

本轮小目标：

1. 用 canonical youtube-dl static tokens 运行 static P2P preflight；
2. 运行 `build_pass_to_pass_scope.py --dry-run`，确认 F2P oracle、nodeid
   exclusion 和 static exclusion 边界正确；
3. 只有 dry-run 通过后，才构造真实 project-level P2P-broad manifest；
4. 若 manifest retained P2P-broad tests >= 3 且排除了 F2P oracle 与
   `test.test_download.TestDownload`，再进入 candidate/oracle construction。

边界：

- 不调用模型 API；
- 不修改 prompt、已有候选标签或既有 P2P manifests；
- 不引入 compatibility shim、dependency install、fixture shim 或 task-file
  P2P 降级；
- 若 static preflight、dry-run、P2P construction 或 manifest quality 失败，
  立即停止并诊断，不进入 candidate validation。

验收条件：

- static preflight 的 buggy/fixed remaining set 无 diff；
- dry-run 不写 manifest；
- real P2P manifest 为 `project_level_p2p_broad` / `unittest`；
- manifest 排除 F2P oracle 和动态下载 nodeids；
- retained P2P-broad tests >= 3；
- 完成后同步 current plan、engineering notes、INDEX/README 和 GitHub。

执行更新：

- controlled expansion readiness 已刷新到当前 registry：
  - main tasks = 10 before this attempt；
  - youtube-dl main tasks = 3 before this attempt。
- static preflight 已通过：
  - total static unittest methods = 212；
  - excluded by canonical static tokens = 61；
  - remaining after static exclusions = 151；
  - buggy/fixed remaining set diff = 0。
- builder dry-run 已通过：
  - fail-to-pass oracle =
    `test.test_InfoExtractor.TestInfoExtractor.test_parse_mpd_formats`；
  - scope type = `project_level_p2p_broad`；
  - test framework = `unittest`；
  - exclude nodeid prefix = `test.test_download.TestDownload`；
  - manifest write = false。
- real P2P-broad construction 已完成：
  - manifest = `data/p2p_scopes/bugsinpy_youtube-dl_2_p2p_broad.json`；
  - collected tests = 2235；
  - excluded dynamic download nodeids = 1997；
  - excluded static external-dependency tests = 86；
  - excluded fail-to-pass oracle = 1；
  - excluded buggy-baseline failures = 4；
  - retained P2P-broad tests = 147；
  - retained dynamic download nodeids = 0。
- 新增 oracle 和 candidate builder：
  - `scripts/oracles/youtubedl_2_parse_mpd_formats.py`；
  - `scripts/build_youtubedl2_candidates.py`。
- retained-oracle validation 已通过 admission gate：
  - candidates = 4；
  - patch_applied = 4/4；
  - oracle_ran = 4/4；
  - oracle_all_passed = 1。
- candidate-level P2P validation 已通过：
  - P2P-broad test count = 147；
  - labels = 1 `correct_under_f2p_and_p2p_broad`,
    3 `incorrect_issue_not_fixed`。
- 已将 `bugsinpy_youtube-dl_2` 纳入
  `data/cohorts/task_cohort_registry.json` 的 `p2p_broad_main`，并将
  `data/tasks/evp7_controlled_probe_results.json` 更新为 admitted。
- 已重建 EVP-7 no-API artifacts：
  - main tasks = 11；
  - projects = 5；
  - promoted candidates = 58；
  - correct reference candidates = 11；
  - issue-not-fixed candidates = 47；
  - evidence packets = 232；
  - E0/E2/E4/E6 各 58；
  - visible outcomes = 58，55 completed / 3 error；
  - visible tool summaries = 58 complete；
  - G1 packet completeness = passed；
  - G2 leakage audit = passed；
  - G3 tool-only baseline readiness = passed；
  - G4 schema stability = passed；
  - G5 prompt manifest = 232 records，passed_without_api；
  - example preflight structural_ready = true，api_ready = false；
  - local preflight structural_ready = true，api_ready = true。
- 新增实验记录：
  `docs/experiments/youtubedl2_candidate_validation.md`。

诊断记录：

- 第一次并行运行 `build_evp7_visible_tool_summaries.py --check` 和
  `build_evp7_evidence_packets.py --check` 时，tool summary 读取了旧的
  54-candidate evidence packets，导致 E6 complete 只有 54；
- 这是依赖顺序问题：tool summary 依赖最新 evidence packets，不能和
  evidence builder 并行；
- 按顺序重跑 tool summary，再重跑 evidence packets 后，G1/G2 通过。

当前边界：

- 第 11 个 bug 已完成 admission，主 structural/no-API cohort 已提升到
  11-task / 58-candidate / 232-packet；
- 最新真实 DeepSeek V4 G5 full run 仍只覆盖上一轮
  10-task / 54-candidate / 216-packet cohort；
- 当前 232-packet cohort 已完成 no-API gates，但尚未执行 fresh real LLM run；
- 因此不能把旧 216-run 的模型结果 claim 直接外推到第 11 个样本。

## 91. 2026-06-13 fresh DeepSeek V4 G5 run on 232-packet cohort

背景：

- `bugsinpy_youtube-dl_2` 已纳入 EVP-7 main cohort；
- no-API gates 已重建并通过：
  - candidates = 58；
  - evidence packets = 232；
  - G1 packet completeness = passed；
  - G2 leakage audit = passed；
  - G3 tool-only baseline readiness = passed；
  - G4 schema stability = passed；
  - G5 prompt manifest = passed_without_api；
  - local preflight api_ready = true。
- 旧真实 DeepSeek V4 G5 run 只覆盖 216 packets，不能作为当前
  232-packet cohort 的模型结果。

本轮小目标：

1. 用 `configs/evp7_g5_llm.local.json` 重新运行 strict local preflight；
2. 先执行 4-packet smoke run，覆盖同一 candidate 的 E0/E2/E4/E6；
3. smoke 若满足 record_count=4、parse_status 全 valid、metrics scaffold 可构建，
   再执行 full 232-packet run；
4. full run 完成后运行 metrics/audit，总结 232-run 是否形成论文级信号；
5. 同步更新 G5 run 文档、current plan、engineering notes、README/INDEX，
   然后提交并同步 GitHub。

边界：

- 使用用户已确认的 DeepSeek V4 provider/model：
  `deepseek_official` / `deepseek-v4-pro`；
- 不修改 prompt、label、candidate、P2P scope 或 evidence-packet 内容；
- 不把 smoke 结果当作 full-run 论文结论；
- 若 strict preflight、prompt-boundary、schema parse、metrics scaffold 或 API
  任一失败，立即停止真实 full run 并先诊断。

验收条件：

- smoke run：
  - review_count = 4；
  - parse_status 全 valid；
  - no `run_error.json`；
  - metrics scaffold 能读取 58-candidate labels。
- full run：
  - review_count = 232；
  - E0/E2/E4/E6 各 58；
  - invalid_parse_count 可解释且不超过协议 stop condition；
  - raw outputs 只保存在 ignored `outputs/`，tracked data/docs 不保存真实
    raw_response_text；
  - 完成后 GitHub 同步。

执行更新：

- strict local preflight 已通过：
  - structural_ready = true；
  - api_ready = true；
  - prompt manifest records = 232；
  - E0/E2/E4/E6 各 58。
- 4-packet smoke run 已完成：
  - review_count = 4；
  - parse_status = 4 valid；
  - E0/E2/E4/E6 各 1；
  - decision = 4 escalate；
  - 无 `run_error.json`。
- full 232-packet run 已完成：
  - review_count = 232；
  - E0/E2/E4/E6 各 58；
  - parse_status = 230 valid / 2 invalid；
  - invalid reason = `invalid_json:No JSON object found in model response`；
  - invalid records =
    `evp7_candidate_0055__E4`,
    `evp7_candidate_0057__E0`；
  - raw response chars = 0 for both invalid records；
  - output dir = ignored `outputs/evp7_g5_llm_232_full`。

诊断：

- 2 条 invalid 是 API/model 空响应导致的 parse failure，不是 prompt-boundary、
  evidence-packet 或 label leakage 问题；
- invalid rate = 2/232 = 0.0086，低于协议 stop condition，但会削弱
  quality audit；
- `scripts/analyze_evp7_schema_dry_run_metrics.py` 的 `_scaffold_passed`
  仍硬编码 200 records / each level 50 records，这是 10-task/50-candidate
  旧队列假设；当前 58-candidate/232-record 队列会被误判为 incomplete。

修复边界：

- 对两个空响应 packet 使用同一 config、同一 prompt、同一 model 重试；
- 生成 repaired ignored output，不覆盖原始 full run；
- 修复 metrics scaffold 为动态校验：record_count 必须等于
  `candidate_count * len(EVIDENCE_LEVELS)`，且每个 evidence level 必须等于
  `candidate_count`；
- 不修改 prompt、labels、candidate 内容或 evidence packets。

修复结果：

- 已重试两个空响应 packet：
  - `evp7_candidate_0055__E4`；
  - `evp7_candidate_0057__E0`。
- repaired output =
  `outputs/evp7_g5_llm_232_full_repaired/reviews.jsonl`；
- repaired parse_status = 232 valid / 0 invalid；
- 已修复 `scripts/analyze_evp7_schema_dry_run_metrics.py` 的 G5 scaffold
  动态规模校验；
- schema dry-run metrics 已重新生成并通过：
  - review records = 232；
  - E0/E2/E4/E6 各 58；
  - G5 metric scaffold = passed。
- repaired real-run metrics 已重新生成并通过：
  - review records = 232；
  - E0/E2/E4/E6 各 58；
  - G5 metric scaffold = passed；
  - G5 signal claim status =
    `real_llm_verifier_signal_observed_on_evp7`；
  - E4/E6 false accept rate = 0.0；
  - E4/E6 accepted precision = 1.0；
  - E4 correct recall = 0.272727；
  - E6 correct recall = 0.090909；
  - E4/E6 Evidence Gain vs E0 = 10.0 / 7.25。
- 已用默认 summarizer 生成 raw-output-free tracked summary：
  - `data/reviews/evp7_g5_llm_full_run_summary.json`；
  - `docs/experiments/evp7_g5_llm_full_run_result.md`。
- 已运行 raw-output-free quality audit：
  - `quality_status = passed_with_limitations`；
  - raw outputs read = false；
  - raw outputs tracked = false；
  - unsupported claims 仍包括 scale-generalized result、LLM outperforming
    tool-only baseline、E6 strictly improves over E4、known DeepSeek billing
    cost。

## 92. 2026-06-13 controlled expansion readiness ledger repair

背景：

- 232-run 已完成并同步 GitHub；
- 回到 controlled expansion 后，`data/tasks/evp7_expansion_readiness.json`
  仍把 `bugsinpy_youtube-dl_5` 和 `bugsinpy_youtube-dl_6` 列为
  `f2p_established_p2p_not_attempted`；
- 但这两个任务已经有 tracked P2P-broad manifests、candidate validation
  reports，并已纳入 `data/cohorts/task_cohort_registry.json` 的
  `p2p_broad_main`；
- 该不一致会污染下一步 P2P candidate 选择。

本轮小目标：

1. 修正 `data/tasks/evp7_controlled_probe_results.json` 中 ydl5/ydl6 的
   probe status；
2. 重新生成 `data/tasks/evp7_expansion_readiness.json` 和
   `docs/experiments/evp7_expansion_readiness.md`；
3. 验证 readiness 的 P2P candidate list 只剩尚未 admission 的
   `youtube-dl_3`、`youtube-dl_4`、`youtube-dl_11`；
4. 根据已有 static preflight sweep，选择下一轮最低静态成本候选。

边界：

- 不新跑 P2P；
- 不改 cohort registry；
- 不改 candidate labels、prompt 或 evidence packets；
- 只修 ledger/status 与 readiness 派生文档。

验收条件：

- ydl5/ydl6 probe status = `admitted_p2p_broad_main`；
- readiness `p2p_candidate_tasks` 不再包含 ydl5/ydl6；
- 下一步候选选择必须基于已记录 static preflight，而不是盲目扩量。

执行结果：

- 已将 `bugsinpy_youtube-dl_5` 和 `bugsinpy_youtube-dl_6` 的
  controlled-probe ledger 修正为：
  - decision = `admitted_to_p2p_broad_main`；
  - probe_status = `admitted_p2p_broad_main`；
  - 补充对应 P2P manifest 和 candidate validation report 路径。
- 已重新生成 expansion readiness：
  - admitted_p2p_broad_main = 4；
  - f2p_established_p2p_not_attempted = 3；
  - P2P candidate tasks =
    `bugsinpy_youtube-dl_11`,
    `bugsinpy_youtube-dl_3`,
    `bugsinpy_youtube-dl_4`。
- 根据 section 66 的 static preflight sweep：
  - ydl3 remaining methods = 151；
  - ydl4 remaining methods = 141；
  - ydl11 remaining methods = 167；
  - 下一轮最低静态成本候选是 `bugsinpy_youtube-dl_4`。

下一步边界：

- 同步 ledger 修复后，若继续 controlled expansion，优先对
  `bugsinpy_youtube-dl_4` 执行 static preflight refresh、builder dry-run 和
  bounded real P2P；
- 不并行运行多个 youtube-dl P2P；
- 不修改 task-file P2P、dependency 或 fixture policy。

## 93. 2026-06-13 controlled expansion P2P attempt: youtube-dl_4

背景：

- readiness ledger 已修正，未 admission 的 clean-F2P youtube-dl P2P candidates
  只剩 ydl3、ydl4、ydl11；
- 已有 section 66 static preflight sweep 显示 ydl4 的 remaining methods = 141，
  低于 ydl3 的 151 和 ydl11 的 167；
- ydl4 retained F2P target =
  `test.test_jsinterp.TestJSInterpreter.test_call`；
- 该任务属于已验证的 youtube-dl unittest family，可复用
  `youtube_dl_dynamic_download_nodeid_exclusion_v1`，但仍必须重新经过
  static preflight、builder dry-run、real P2P 和 manifest quality gate。

本轮小目标：

1. 刷新 ydl4 static P2P preflight；
2. 运行 `build_pass_to_pass_scope.py --dry-run` 验证命令边界；
3. dry-run 通过后构造真实 project-level P2P-broad manifest；
4. 若 manifest retained P2P-broad tests >= 3 且排除 F2P oracle 与
   `test.test_download.TestDownload`，再进入 candidate/oracle construction。

边界：

- 不调用模型 API；
- 不并行运行其他 youtube-dl P2P；
- 不修改 prompt、已有候选标签或既有 P2P manifests；
- 不引入 compatibility shim、dependency install、fixture shim 或 task-file
  P2P 降级；
- 若 static preflight、dry-run、P2P construction 或 manifest quality 失败，
  立即停止并诊断，不进入 candidate validation。

验收条件：

- static preflight 的 buggy/fixed remaining set 无 diff；
- dry-run 不写 manifest；
- real P2P manifest 为 `project_level_p2p_broad` / `unittest`；
- manifest 排除 F2P oracle 和动态下载 nodeids；
- retained P2P-broad tests >= 3；
- 完成后同步 current plan、engineering notes、INDEX/README 和 GitHub。

执行结果：

- static preflight 已通过：
  - total static unittest methods = 196；
  - excluded by canonical static tokens = 55；
  - remaining after static exclusions = 141；
  - buggy/fixed remaining set diff = 0。
- builder dry-run 已通过：
  - fail-to-pass oracle =
    `test.test_jsinterp.TestJSInterpreter.test_call`；
  - scope type = `project_level_p2p_broad`；
  - test framework = `unittest`；
  - exclude nodeid prefix = `test.test_download.TestDownload`；
  - manifest write = false。
- real P2P-broad construction 已完成：
  - manifest = `data/p2p_scopes/bugsinpy_youtube-dl_4_p2p_broad.json`；
  - collected tests = 1994；
  - excluded dynamic download nodeids = 1772；
  - excluded static external-dependency tests = 81；
  - excluded fail-to-pass oracle = 1；
  - excluded buggy-baseline failures = 3；
  - retained P2P-broad tests = 137；
  - retained dynamic download nodeids = 0。
- 新增 oracle 和 candidate builder：
  - `scripts/oracles/youtubedl_4_jsinterp_call.py`；
  - `scripts/build_youtubedl4_candidates.py`。
- retained-oracle validation 已通过 admission gate：
  - candidates = 4；
  - patch_applied = 4/4；
  - oracle_ran = 4/4；
  - oracle_all_passed = 1。
- candidate-level P2P validation 已通过：
  - P2P-broad test count = 137；
  - labels = 1 `correct_under_f2p_and_p2p_broad`,
    3 `incorrect_issue_not_fixed`。
- 已将 `bugsinpy_youtube-dl_4` 纳入
  `data/cohorts/task_cohort_registry.json` 的 `p2p_broad_main`，并将
  `data/tasks/evp7_controlled_probe_results.json` 更新为 admitted。
- 已重建 EVP-7 no-API artifacts：
  - main tasks = 12；
  - projects = 5；
  - promoted candidates = 62；
  - correct reference candidates = 12；
  - issue-not-fixed candidates = 50；
  - evidence packets = 248；
  - E0/E2/E4/E6 各 62；
  - visible outcomes = 62，59 completed / 3 error；
  - visible tool summaries = 62 complete；
  - G1 packet completeness = passed；
  - G2 leakage audit = passed；
  - G3 tool-only baseline readiness = passed；
  - G4 schema stability = passed；
  - G5 prompt manifest = 248 records，passed_without_api。
- 新增实验记录：
  `docs/experiments/youtubedl4_candidate_validation.md`。

验证结果：

- `build_evp7_protocol_manifests.py --check` 通过；
- `build_evp7_candidate_manifest.py --check` 通过；
- `run_evp7_visible_tests.py --run --check` 通过；
- `build_evp7_visible_tool_summaries.py --check` 在首次读取旧 packets 时
  暴露 58/62 依赖顺序问题；按 evidence packets -> tool summaries ->
  evidence packets 顺序重跑后通过；
- `run_evp7_tool_only_baselines.py --check` 通过；
- `run_evp7_merge_gate_schema_dry_run.py --check` 通过；
- `build_evp7_g5_llm_prompt_manifest.py --check` 通过；
- `analyze_evp7_schema_dry_run_metrics.py --check` 通过，当前 dry-run
  E4/E6 为 FAR 0.02、accepted precision 0.916667、correct recall 0.916667、
  Evidence Gain 20.5；
- `preflight_evp7_g5_llm_run.py` example config 结构预检通过，strict API
  readiness 因 example config 仍使用占位 provider/model/cost/smoke/full-run
  permission 而按预期阻止真实执行；
- 相关脚本 `py_compile` 通过。

当前边界：

- 第 12 个 bug 已完成 admission，主 structural/no-API cohort 已提升到
  12-task / 62-candidate / 248-packet；
- 最新真实 DeepSeek V4 G5 full run 仍只覆盖上一轮
  11-task / 58-candidate / 232-packet cohort；
- 当前 248-packet cohort 已完成 no-API gates，但尚未执行 fresh real LLM run；
- 因此不能把旧 232-run 的模型结果 claim 直接外推到第 12 个样本；
- 下一步应在同步本轮 admission 后，用已获批的 DeepSeek V4 路线执行
  fresh 248-packet G5 smoke/full run、raw-output-free summary 和 quality
  audit。

## 94. 2026-06-13 fresh DeepSeek V4 G5 run on 248-packet cohort

背景：

- `bugsinpy_youtube-dl_4` 已完成 formal admission，并已同步 GitHub；
- 当前 structural/no-API cohort = 12 tasks / 62 candidates / 248 packets；
- no-API gates 已通过：
  - G1 packet completeness = passed；
  - G2 leakage audit = passed；
  - G3 tool-only baseline readiness = passed；
  - G4 schema stability = passed；
  - G5 prompt manifest = 248 records，passed_without_api；
  - example config structural preflight = true，api_ready = false；
  - ignored local config exists and previously used DeepSeek V4 route。
- 最新真实 DeepSeek V4 G5 result 仍只覆盖上一版
  11-task / 58-candidate / 232-packet cohort，不能作为当前 248-packet
  cohort 的模型结果。

本轮小目标：

1. 用 `configs/evp7_g5_llm.local.json` 对当前 248-packet artifacts 运行
   strict local preflight；
2. 先执行 4-packet smoke run，覆盖同一候选的 E0/E2/E4/E6；
3. smoke 若满足 review_count=4、parse_status 全 valid、无 `run_error.json`、
   metrics scaffold 可构建，再执行 full 248-packet run；
4. full run 完成后检查 invalid rate、level counts、metrics scaffold；
5. 若 full run 有少量 API/model 空响应，在同一
   prompt/config/model/temperature/max_tokens 下只重试 empty-response
   invalid packets；若是非空 schema-invalid 输出，则作为模型输出质量边界报告；
6. 生成 raw-output-free tracked summary、quality audit，并同步文档与 GitHub。

边界：

- 使用用户已批准的 DeepSeek V4 provider/model 路线；
- 不修改 prompt、candidate labels、P2P scope 或 evidence packets；
- smoke 不作为论文结论；
- raw model responses 只留在 ignored `outputs/`；
- 如果 strict preflight、prompt-boundary、leakage、API authentication、
  smoke parse validity 或 full-run invalid rate 触发 stop condition，立即停止
  并诊断，不继续下一步。

验收条件：

- strict local preflight：structural_ready = true 且 api_ready = true；
- smoke：4 records，E0/E2/E4/E6 各 1，parse_status 全 valid；
- full/repaired full：248 records，E0/E2/E4/E6 各 62，invalid output 可解释且
  低于 stop condition；
- tracked summary 不包含 raw response text；
- quality audit 至少达到 `passed_with_limitations` 或明确给出阻塞诊断；
- 完成后同步 README、INDEX、protocol/pilot/G5 docs、current plan、
  engineering notes，并提交推送。

执行结果：

- strict local preflight 已通过：
  - structural_ready = true；
  - api_ready = true；
  - prompt manifest records = 248；
  - E0/E2/E4/E6 各 62。
- 4-packet smoke run 已完成：
  - review_count = 4；
  - parse_status = 4 valid / 0 invalid；
  - E0/E2/E4/E6 各 1；
  - 无 `run_error.json`；
  - smoke metrics 标记 `real_llm_verifier_outputs_incomplete`，这是因为
    smoke 只覆盖 4 条，不是 full-run 失败。
- full 248-packet run 已完成：
  - review_count = 248；
  - E0/E2/E4/E6 各 62；
  - parse_status = 247 valid / 1 invalid；
  - invalid record = `evp7_candidate_0030__E2`；
  - invalid reason = `invalid_json:No JSON object found in model response`；
  - raw response chars = 444；
  - output dir = ignored `outputs/evp7_g5_llm_248_full`；
  - concurrency = 6。

诊断：

- 这 1 条 invalid 不是空响应，而是非空截断 JSON；
- 根据既有 engineering note，空响应可以 targeted retry，非空 schema-invalid
  full-run 输出不应静默修复；
- 因此本轮不重试该记录，而是在 tracked raw-output-free summary 和 quality audit
  中显式报告；
- invalid-output rate = 1/248 = 0.004032，低于 stop condition。

指标与审计：

- tracked summary 已生成：
  - `data/reviews/evp7_g5_llm_full_run_summary.json`；
  - `docs/experiments/evp7_g5_llm_full_run_result.md`。
- quality audit 已生成并通过限制性审计：
  - `quality_status = passed_with_limitations`；
  - raw outputs read = false；
  - raw outputs tracked = false；
  - review count = 248；
  - candidate count = 62。
- full-run metrics：
  - G5 signal claim status =
    `real_llm_verifier_signal_observed_on_evp7`；
  - E4 false accept rate = 0.0；
  - E6 false accept rate = 0.0；
  - E4/E6 accepted precision = 1.0；
  - E4 correct recall = 0.166667；
  - E6 correct recall = 0.25；
  - E4/E6 Evidence Gain vs E0 = 7.25 / 7.5。

当前边界：

- 支持：当前 12-task / 62-candidate / 248-packet EVP-7 pilot 中，证据可见性
  改变 DeepSeek V4 merge-gate 决策，E4/E6 在 zero observed false accept 下
  提升 correct recall，并产生正 Evidence Gain；
- 不支持：规模泛化、LLM 优于 deterministic visible-test tool-only baseline、
  E6 严格优于 E4、DeepSeek 真实计费成本已知；
- 下一步必须在 controlled expansion 与 paper-result consolidation 之间做研究
  决策，不能再把“继续加一个 bug”当作默认目标。

## 95. 2026-06-14 paper-result consolidation and stale-doc repair

背景：

- 顶层 readiness、plan-progress 和 goal-completion 审计均已通过；
- 当前真实 DeepSeek V4 G5 结果已覆盖 12-task / 62-candidate /
  248-packet EVP-7 cohort；
- `docs/plans/final_paper_roadmap_zh.md` 已明确要求在继续扩量前统一论文草稿、
  README、计划和 cohort registry 的当前主线口径；
- 当前不应默认再加入一个 bug。

本轮小目标：

1. 选择 paper-result consolidation 作为当前最短路径，而不是继续 controlled
   expansion；
2. 审计并修复 stale 文档口径，重点是旧的 8/9/10/11-task、168/184/200/216/232
   历史结果不能被写成当前主结论；
3. 如果生成脚本仍输出旧口径，修脚本而不是手改生成物；
4. 重新运行最小文档/论文审计和本地质量门；
5. 同步更新 README、INDEX、current plan、engineering notes，并提交推送。

边界：

- 不调用真实模型 API；
- 不修改 prompt、candidate labels、P2P scope 或 evidence packets；
- 不继续扩新 bug；
- 不把 248-run 写成规模泛化、LLM 优于 tool-only 或已知成本结论；
- 如果发现论文生成链路仍只支持旧 30-candidate pilot，本轮只做最短路径修复
  或明确记录阻塞，不重构整篇论文。

验收条件：

- current plan 明确记录本轮选择和边界；
- stale 文档审计不再发现会误导当前 EVP-7 主结论的旧口径；
- 最小 paper/readiness/quality gate 通过，或阻塞原因被归类并记录；
- 代码或文档变更只暂存本轮相关文件，检查 diff 和敏感信息后同步 GitHub。

执行结果：

- 已选择 paper-result consolidation 作为本轮路线，不继续扩新 bug、不调用真实 API；
- 已扩展 `scripts/audit_paper_readiness.py`：
  - 保留旧 prompt-only positive claim 字段，继续报告旧 full-run gate 为
    `stop_or_redesign`；
  - 保留旧 tool-augmented conditional claim 字段；
  - 新增 `evp7_g5`、`evp7_bounded_pilot_claim_ready` 和
    `current_result_claim_ready` 字段；
  - EVP-7 readiness 只读取 raw-output-free tracked summary 和 quality audit，
    要求 248 reviews、E0/E2/E4/E6 各 62、raw outputs 未 tracked、
    `real_llm_verifier_signal_observed_on_evp7`、E4/E6 positive recall 和
    positive Evidence Gain。
- 已修正 `docs/plans/final_paper_roadmap_zh.md` 中当前 cohort 的 stale 口径：
  - 当前 `p2p_broad_main` = 12 completed project-level P2P-broad tasks；
  - 当前主 cohort = 12 bugs / 5 projects；
  - 旧 184/200/216/232 run 仍保留为历史运行边界。
- 已同步 README、INDEX 和 engineering notes，记录新的 paper readiness
  frontier 和三条 claim 边界。

验证结果：

- `python -m py_compile scripts\audit_paper_readiness.py` 通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md` 通过：
  - `prompt_only_positive_claim_ready = false`；
  - `tool_augmented_claim_ready = true`；
  - `evp7_bounded_pilot_claim_ready = true`；
  - `current_result_claim_ready = true`；
  - `evp7_blockers = []`。
- `python scripts\audit_goal_completion.py --out-json outputs\goal_completion\latest.json --out-md outputs\goal_completion\latest.md` 通过，`complete = true`；
- `git diff --check` 只有 Windows LF/CRLF 提示，无 whitespace error；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md` 通过，`passed = true`。

## 96. 2026-06-14 controlled expansion P2P retry: youtube-dl_3

背景：

- 用户明确当前目标是继续补充 bug 到计划中的 15-20 bugs；
- 当前 EVP-7 主 cohort = 12 tasks / 5 projects / 62 candidates /
  248 evidence packets，距离 15 个 bug 还差 3 个；
- `data/tasks/evp7_expansion_readiness.json` 当前只列出两个已建立 F2P 但尚未
  P2P admission 的候选：
  - `bugsinpy_youtube-dl_3`；
  - `bugsinpy_youtube-dl_11`。
- 此前对 `bugsinpy_youtube-dl_3` 的 bounded project-level P2P-broad 运行在
  外层约 1904 秒超时，未生成
  `data/p2p_scopes/bugsinpy_youtube-dl_3_p2p_broad.json`；
- 该失败命令缺少 youtube-dl 已验证 family policy 中的显式动态下载 nodeid 排除：
  `--exclude-nodeid-prefix "test.test_download.TestDownload"`。

Inspect 结果：

- 当前无残留 Python/Git 进程；
- Git 工作区干净，但本地 `main` 仍比 `origin/main` ahead 1；
- `bugsinpy_youtube-dl_2/4/5/6/7` 的成功 P2P manifests 均记录：
  - `scope_type = project_level_p2p_broad`；
  - `test_framework = unittest`；
  - `exclude_nodeid_prefixes = ["test.test_download.TestDownload"]`；
  - `scope_policy.policy_name = youtube_dl_dynamic_download_nodeid_exclusion_v1`；
  - retained P2P-broad tests 分别为 147、137、128、110、108。

本轮小目标：

1. 先用修正后的 ydl3 P2P 命令执行 `--dry-run`，验证命令边界且不写 manifest；
2. dry-run 通过后，使用同一 family policy 重跑 ydl3 bounded
   project-level P2P-broad；
3. 若 manifest retained P2P-broad tests >= 3，且记录动态下载排除 policy，
   进入 ydl3 oracle/candidate construction；
4. 若 ydl3 仍因 project-level P2P 超时或质量门失败，则记录 blocker 并转向
   `bugsinpy_youtube-dl_11`，不重复无边界长跑。

边界：

- 不调用模型 API；
- 不修改 prompt、既有候选标签或既有 P2P manifests；
- 不并行运行多个 youtube-dl P2P；
- 不引入 compatibility shim、dependency install、fixture shim 或 task-file P2P
  降级；
- 不重复执行缺少 `exclude-nodeid-prefix` 的旧命令；
- GitHub push 若继续超时，记录后继续本地任务。

验收条件：

- dry-run 输出显示 `manifest_write = false`；
- real P2P manifest 存在且为 `project_level_p2p_broad` / `unittest`；
- manifest 记录 `youtube_dl_dynamic_download_nodeid_exclusion_v1` 和
  `exclude_nodeid_prefixes = ["test.test_download.TestDownload"]`；
- retained P2P-broad tests >= 3；
- 完成后同步 current plan、engineering notes、INDEX/README，并只提交本轮相关文件。

执行结果：

- 修正后的 dry-run 已通过：
  - `will_write_manifest = false`；
  - `will_execute_tests = false`；
  - `exclude_nodeid_prefixes = ["test.test_download.TestDownload"]`；
  - `scope_type = project_level_p2p_broad`；
  - `test_framework = unittest`。
- 真实 ydl3 P2P 在外层 40 分钟超时后仍未生成
  `data/p2p_scopes/bugsinpy_youtube-dl_3_p2p_broad.json`；
- 超时后残留进程显示主 builder 仍在运行，子 unittest 卡在
  `test.test_utils.TestUtil.test_xpath_attr`，随后又残留
  `test.test_utils.TestUtil.test_xpath_element`；
- 已停止 ydl3 builder 和残留 unittest 子进程；
- 诊断：动态下载排除修复了已知 family-policy 漏洞，但 ydl3 仍触发
  project-level unittest P2P construction timeout，当前不能 admission；
- 决策：记录 ydl3 为 corrected-policy P2P timeout blocker，转向
  `bugsinpy_youtube-dl_11`，沿用同一
  `youtube_dl_dynamic_download_nodeid_exclusion_v1` policy。

## 97. 2026-06-14 controlled expansion admission: youtube-dl_11

本轮小目标：

1. 对 `bugsinpy_youtube-dl_11` 执行 bounded project-level P2P-broad；
2. 构造 retained oracle 和 4 个候选补丁；
3. 通过 retained-oracle validation 与 P2P-broad validation 后 admission；
4. 重建 EVP-7 no-API artifacts，并保持真实 G5 结论不越界到未实跑的
   264-packet cohort。

边界：

- 不调用模型 API；
- 不安装依赖、不修改 checkout、不引入 fixture shim；
- 不把 ydl3 timeout 降级为 task-file P2P；
- GitHub push 如果继续频繁失败，允许先保留本地提交继续任务；
- 最新真实 DeepSeek G5 结果仍只覆盖旧 12-task/62-candidate/248-packet
  cohort。

执行结果：

- `bugsinpy_youtube-dl_11` P2P-broad 成功：
  - collected/common nodeids = 2326；
  - excluded generated download nodeids = 2095；
  - excluded static external-dependency tests = 66；
  - excluded retained F2P oracle = 1；
  - excluded buggy-baseline failures = 4；
  - retained P2P-broad tests = 160；
  - scope policy =
    `youtube_dl_dynamic_download_nodeid_exclusion_v1`。
- 新增 retained oracle：
  `scripts/oracles/youtubedl_11_str_to_int.py`。
- 新增候选构造脚本：
  `scripts/build_youtubedl11_candidates.py`。
- retained-oracle validation 通过：
  - candidates = 4；
  - patch applied = 4/4；
  - oracle ran = 4/4；
  - oracle passed = 1/4。
- P2P validation 通过：
  - labels:
    - `correct_under_f2p_and_p2p_broad`: 1；
    - `incorrect_issue_not_fixed`: 3。
- 已更新 registry 与 controlled-probe ledger：
  - ydl11 admitted；
  - ydl3 记录为 corrected-policy P2P timeout blocker。

修复/诊断：

- ydl11 候选脚本的初版 hunk header 不正确，导致 patch apply 报
  `corrupt patch`；已按最短路径修正 hunk 行号后重新验证。
- 初次 13-task candidate manifest 生成时，字符串排序会把
  `youtube-dl_11` 插到 `youtube-dl_2` 前，造成既有 candidate ID 漂移；
  已改为按任务末尾数字自然排序，旧 62 条 candidate ID 保持稳定，
  ydl11 追加为 `evp7_candidate_0063` 到 `evp7_candidate_0066`。
- protocol manifest check 不能用 registry-known candidate count 作为
  62-candidate floor，因为 `httpie_5` 仍缺 registry candidate count；
  已删除该错误 gate，candidate manifest 本身仍生成实际 66 条。

重建结果：

- `python scripts\build_evp7_protocol_manifests.py --check` 通过：
  main tasks = 13；
- `python scripts\build_evp7_candidate_manifest.py --check` 通过：
  candidates = 66，correct = 13，incorrect = 53；
- `python scripts\run_evp7_visible_tests.py --run --check --timeout 90`
  通过：66 records，63 completed，3 error；
- `python scripts\build_evp7_visible_tool_summaries.py --check` 通过：
  66 complete summaries；
- `python scripts\build_evp7_evidence_packets.py --check` 通过：
  264 packets，E0/E2/E4/E6 各 66，G1/G2 passed；
- `python scripts\run_evp7_tool_only_baselines.py --check` 通过：
  198 decisions，G3 passed；
- `python scripts\run_evp7_merge_gate_schema_dry_run.py --check` 通过：
  264 valid parses，G4 passed；
- `python scripts\analyze_evp7_schema_dry_run_metrics.py --check` 通过：
  no-API metric scaffold passed，仍要求真实 LLM verifier outputs；
- `python scripts\build_evp7_g5_llm_prompt_manifest.py --check` 通过：
  264 prompt records，zero leakage failures；
- `python scripts\preflight_evp7_g5_llm_run.py --config configs\evp7_g5_llm.example.json --out data\reviews\evp7_g5_llm_preflight_example.json`
  通过：structural_ready = true，api_ready = false；
- `python scripts\run_evp7_g5_llm_workflow.py --check-only --summary-out data\reviews\evp7_g5_workflow_check_only_example.json`
  通过：未调用模型/API；
- `python scripts\summarize_evp7_expansion_readiness.py` 通过：
  当前 main tasks = 13，P2P candidate tasks = []。

当前边界：

- 当前结构化 EVP-7 cohort = 13 tasks / 5 projects / 66 candidates /
  264 evidence packets；
- 最新真实 DeepSeek G5 full run 仍为旧 12-task / 62-candidate /
  248-packet cohort；
- 不得把旧 248-run 的真实模型 claim 延伸到当前 264-packet structural
  cohort，除非后续显式授权并完成新的真实 264-packet run 与质量审计；
- 15 bug 目标仍差 2 个 admission，需要从 readiness 的其他 probe lanes
  继续寻找新的 F2P/P2P/candidate validation 路径。

## 98. 2026-06-14 next controlled probe lane: youtube-dl_13

背景：

- ydl11 admission 后，当前结构化 EVP-7 cohort = 13 tasks / 66 candidates /
  264 packets；
- 目标 15-20 bugs 仍至少差 2 个 admission；
- `data/tasks/evp7_expansion_readiness.json` 当前没有
  F2P-established/P2P-not-attempted candidates；
- fresh-project promising candidates 仍为 0，FastAPI/Sanic/Scrapy 等 top
  lanes 已有当前环境依赖阻塞记录；
- candidate pool 中仍有未探测的 `youtube-dl` unittest 候选。纯
  `test/test_utils.py` 候选比已阻塞依赖项目更短路径。

本轮小目标：

1. 只读确认本地 BugsInPy checkout 工具是否可用；
2. 若可用，串行 checkout `bugsinpy_youtube-dl_13` 的 buggy/fixed 版本；
3. 运行候选池记录的 F2P command：
   `python -m unittest -q test.test_utils.TestUtil.test_urljoin`；
4. 若 buggy fail 且 fixed pass，则记录 F2P established，并进入 bounded
   project-level P2P-broad dry-run；
5. 若 checkout 工具不可用、checkout 超时、或 F2P 不成立，则记录 blocker，
   不继续 P2P。

边界：

- 不调用模型 API；
- 不安装依赖、不修改 checkout、不引入 shim；
- 同一任务的 buggy/fixed checkout 必须串行；
- 不并行运行多个 youtube-dl P2P；
- 不复用 ydl3 的已知 timeout 命令；
- 如果本地 checkout 工具不可执行，停止该 lane 并记录阻塞。

验收条件：

- checkout 工具路径和可执行性被记录；
- 若 F2P 成立，buggy/fixed 测试输出和命令边界被记录；
- 若失败，阻塞类别明确归类为 checkout/tooling/F2P，而不是继续执行后续
  P2P；
- 任何代码或文档更新后继续执行最小验证并提交。

执行结果：

- 本地 `bugsinpy-checkout` 不在 PATH，但 retained BugsInPy archive 中存在
  `framework/bin/bugsinpy-checkout` 可执行入口；
- 通过 WSL bash 路径验证 `--help` 可执行；
- `projects/youtube-dl/bugs/13/bug.info` 确认：
  - `buggy_commit_id = 6945b9e78f38284eb4e440b7badea2fc60b66c2f`；
  - `fixed_commit_id = fad4ceb53404227f471af2f3544c4c14a5df4acb`；
  - `test_file = test/test_utils.py`；
  - target command =
    `python -m unittest -q test.test_utils.TestUtil.test_urljoin`。
- buggy checkout 在 10 分钟 bounded probe 窗口内超时，只产生不完整 `.git`
  目录，没有 `bugsinpy_run_test.sh`；
- 超时后残留 bash 进程已停止，不完整 `youtube-dl_13` workspace 已在确认
  路径边界后从 BugsInPy workspace root 删除；
- fixed checkout、F2P 测试、P2P dry-run、dependency install 和 checkout edit
  均未执行。

诊断与决策：

- `bugsinpy_youtube-dl_13` 当前归类为
  `f2p_blocked_checkout_timeout`；
- 这不是 F2P 失败，也不是 P2P 失败，而是 checkout/tooling 阶段阻塞；
- readiness 已刷新，当前 main cohort 仍为 13 tasks / 66 candidates /
  264 packets；
- 15 bug 目标仍差 2 个 admission，下一轮应继续选择新的 bounded probe lane，
  不复用该不完整 checkout。

验证修复计划：

- 本轮最小验证中的 `run_local_quality_gate.py` 在 Windows 子进程输出解码处
  崩溃：`subprocess.run(text=True)` 使用本地 GBK codec 读取 `rg` 输出时遇到
  非 GBK 字节，随后 `tail(None)` 触发二次异常；
- 问题类型归类为执行链路 bug，不是 ydl13 实验设计或数据问题；
- 最短路径修复是让本地质量门显式使用 UTF-8 解码并用
  `errors="replace"` 保留扫描结果，同时让 `tail` 对 `None` 返回空字符串；
- 首次修复后质量门继续失败，原因是本节记录了本机绝对路径，触发
  sensitive scan 和 anonymous artifact dry-run；已改为 archive/workspace
  相对描述；
- 修复后重新运行 `py_compile`、本地质量门和 diff 检查。

## 99. 2026-06-14 next controlled probe lane: youtube-dl_10

背景：

- ydl13 已记录为 checkout/tooling 阶段阻塞，未产生可复用 workspace；
- 当前结构化 EVP-7 cohort 仍为 13 tasks / 66 candidates / 264 packets；
- 目标 15-20 bugs 仍至少差 2 个 admission；
- 已有完整本地 checkout 但未入主 cohort 的任务均有明确既有阻塞：
  `youtube-dl_1` 为 project-level unittest discovery timeout，
  `httpie_2/3/4` 为 project-level scope timeout 或 requests 兼容性问题，
  `black_*` 为 `typed_ast` 依赖阻塞，`luigi_*` 为 large-suite/P2P blocker；
- 剩余未记录 `youtube-dl` 候选中，`bugsinpy_youtube-dl_10` 是无 metadata
  blocker 的 pure `test/test_utils.py` unittest lane，target command 为
  `python -m unittest -q test.test_utils.TestUtil.test_js_to_json_realworld`。

本轮小目标：

1. 串行 bounded checkout `bugsinpy_youtube-dl_10` buggy 版本；
2. 若 buggy checkout 完整，再运行 target F2P command；
3. 若 buggy fail，再串行 checkout fixed 版本并运行同一 target command；
4. 若 buggy fail 且 fixed pass，则记录 F2P established，并进入 corrected
   youtube-dl family P2P-broad dry-run；
5. 若 checkout 超时、target test 不成立或环境阻塞，则记录 blocker，不继续
   P2P。

边界：

- 不调用模型 API；
- 不安装依赖、不修改 checkout、不引入 shim；
- 同一任务 buggy/fixed checkout 串行，禁止并行；
- checkout 每个版本使用 10 分钟 bounded probe window；
- 不复用 ydl13 的不完整 workspace；
- 不把已有 blocked task 降级为 task-file P2P。

验收条件：

- checkout 结果明确记录完整/超时/阻塞；
- 如果 F2P 不成立，ledger 记录应停在 checkout/F2P 阶段；
- 如果 F2P 成立，后续 P2P 命令必须沿用
  `youtube_dl_dynamic_download_nodeid_exclusion_v1` 和
  `--exclude-nodeid-prefix "test.test_download.TestDownload"`；
- 每个关键动作后运行最小验证并更新 readiness/经验文档。

执行修订：

- 首次调用 retained BugsInPy checkout 进行 buggy checkout 未超时，但 GitHub
  clone 因 TLS connection terminated 中断，且 `bugsinpy-checkout` 仍返回 0；
- marker 验证显示 `bugsinpy_run_test.sh` 不存在，workspace 只有空的
  `buggy` 目录，因此不能视为完整 checkout；
- ydl10 的 buggy/fixed commit 均已在本地既有 `youtube-dl_11` Git checkout
  中验证存在；
- 为避免重复依赖不稳定 GitHub clone，本轮改用本地 Git clone 构造
  ydl10 workspace，但必须按 BugsInPy checkout 脚本同样流程执行：
  先 reset fixed commit 并复制 fixed test file，再 reset buggy commit，
  buggy 版本只放回 fixed test file；fixed 版本再放回 fixed commit 变更文件；
- 该修订不安装依赖、不修改 checkout 内容、不引入 shim；完成后必须验证
  marker 文件存在、HEAD 为 buggy commit，并分别运行 target unittest。

执行结果：

- 本地 clone checkout 构造成功：
  - buggy workspace marker `bugsinpy_run_test.sh` 存在；
  - fixed workspace marker `bugsinpy_run_test.sh` 存在；
  - buggy workspace diff 仅包含 fixed `test/test_utils.py`；
  - fixed workspace diff 包含 fixed `test/test_utils.py` 和
    `youtube_dl/utils.py`；
  - buggy/fixed workspace HEAD 均为
    `85d586617750d38d742a24f141b099f6b898d269`，fixed 版本通过放回
    fixed commit 变更文件表示修复态，符合 BugsInPy checkout 脚本逻辑。
- F2P target command 结果：
  - buggy: `python -m unittest -q test.test_utils.TestUtil.test_js_to_json_realworld`
    失败，`json.decoder.JSONDecodeError: Extra data`；
  - fixed: 同一命令通过。
- corrected-policy P2P dry-run 通过：
  - checkout 存在；
  - `will_write_manifest = false`；
  - `will_execute_tests = false`；
  - `exclude_nodeid_prefixes = ["test.test_download.TestDownload"]`；
  - `scope_policy_name = youtube_dl_dynamic_download_nodeid_exclusion_v1`。
- 真实 project-level P2P-broad 在 40 分钟外层超时：
  - 未生成 `data/p2p_scopes/bugsinpy_youtube-dl_10_p2p_broad.json`；
  - 输出目录仅留下 ignored `compat_shim`；
  - 残留 builder 和 unittest 子进程已停止。

诊断与决策：

- `bugsinpy_youtube-dl_10` 当前归类为
  `f2p_established_corrected_policy_p2p_timeout`；
- F2P 已成立，但 project-level P2P-broad 未完成，因此不能 admission；
- 该 lane 进一步说明 youtube-dl pure-utils 候选仍可能被 broader unittest
  scope 中的 subtitles/swf/utils 批次拖入超时；
- readiness 已刷新，当前 main cohort 仍为 13 tasks / 66 candidates /
  264 packets；
- 15 bug 目标仍差 2 个 admission，下一轮应继续寻找新的 bounded lane，优先
  避免重复进入同类 40 分钟 P2P 超时路径。

## 100. 2026-06-14 next controlled probe lane: youtube-dl_16

背景：

- ydl10 已建立 F2P，但 corrected-policy P2P-broad 超时，不能 admission；
- 继续重复旧版 ydl10/ydl3 的 40 分钟 P2P 路径收益低；
- `bugsinpy_youtube-dl_16` 是后续无 metadata blocker 的 pure
  `test/test_utils.py` lane，target command 为
  `python -m unittest -q test.test_utils.TestUtil.test_dfxp2srt`；
- ydl16 的 buggy/fixed commit 均已在本地既有 youtube-dl Git checkout 中验证
  存在，可以复用 ydl10 已审计的本地 clone checkout 流程，避免 GitHub clone
  TLS 中断。

本轮小目标：

1. 使用本地 Git clone 按 BugsInPy checkout 脚本逻辑构造 ydl16 buggy/fixed
   workspace；
2. 验证 marker、HEAD 和 diff 边界；
3. 串行运行 target F2P command；
4. 若 buggy fail 且 fixed pass，则执行 corrected-policy P2P-broad dry-run；
5. dry-run 通过后执行真实 P2P-broad；若 manifest retained tests >= 3，则进入
   oracle/candidate construction，否则记录 blocker。

边界：

- 不调用模型 API；
- 不安装依赖、不修改 checkout、不引入 shim；
- 不调用不稳定 GitHub clone；
- 同一任务 buggy/fixed 测试串行；
- P2P 必须沿用 `youtube_dl_dynamic_download_nodeid_exclusion_v1` 和
  `--exclude-nodeid-prefix "test.test_download.TestDownload"`；
- 若 P2P 再次超时，停止残留进程并记录，不降级为 task-file P2P。

验收条件：

- ydl16 workspace marker 与 diff 验证通过；
- F2P target command 形成 buggy fail / fixed pass；
- P2P manifest 若生成，必须是 `project_level_p2p_broad` 且 retained tests >= 3；
- 完成后同步 ledger、readiness、current plan、engineering notes 和 INDEX。

执行结果：

- ydl16 本地 clone checkout 构造成功：
  - buggy/fixed marker 文件存在；
  - buggy diff 仅包含 fixed `test/test_utils.py`；
  - fixed diff 包含 `ChangeLog`、fixed test file、
    `youtube_dl/postprocessor/ffmpeg.py` 和 `youtube_dl/utils.py`；
  - buggy/fixed HEAD 均为 `68d43a61b552007a718894967b869c0f1d8ff00f`，
    fixed 版本通过放回 fixed commit 变更文件表示修复态。
- F2P target command 结果：
  - buggy: `TypeError: a bytes-like object is required, not 'str'`；
  - fixed: pass。
- corrected-policy P2P-broad 成功：
  - collected/common nodeids = 2222；
  - excluded generated download nodeids = 1985；
  - excluded static external-dependency tests = 85；
  - excluded retained F2P oracle = 1；
  - excluded buggy-baseline failures = 4；
  - retained P2P-broad tests = 147；
  - collection error files = 0；
  - scope policy = `youtube_dl_dynamic_download_nodeid_exclusion_v1`。
- 新增 retained oracle：
  `scripts/oracles/youtubedl_16_dfxp2srt_bytes.py`；
- 新增 candidate builder：
  `scripts/build_youtubedl16_candidates.py`；
- retained-oracle validation 通过：
  - candidates = 4；
  - patch applied = 4/4；
  - oracle ran = 4/4；
  - oracle passed = 1/4。
- P2P validation 通过：
  - labels:
    - `correct_under_f2p_and_p2p_broad`: 1；
    - `incorrect_issue_not_fixed`: 3。
- `bugsinpy_youtube-dl_16` 已加入 `p2p_broad_main`。

修复/诊断：

- 初版 ydl16 candidate patch hunk 手写不精确，导致 patch apply failure；
  已改为直接复用 fixed workspace 的 source-only `git diff`；
- `validate_patch_candidates.py` 暴露执行链路 bug：validation workdir 位于
  当前 Git repo 的 ignored `outputs/` 下且没有 `.git`，`git apply` 会向上
  发现 research95 仓库，造成 patch apply false positive；已通过
  `GIT_CEILING_DIRECTORIES = workdir.parent` 阻止向上发现仓库，确保 patch
  应用到 candidate workdir；
- 同一修复被 `validate_candidates_with_p2p.py` 复用，因为它调用同一个
  `apply_patch`。

重建结果：

- `build_evp7_protocol_manifests.py --check` 通过：
  main tasks = 14；
- `build_evp7_candidate_manifest.py --check` 通过：
  candidates = 70，correct = 14，incorrect = 56；
- `run_evp7_visible_tests.py --run --check --timeout 90` 通过：
  70 records，67 completed，3 error；
- `build_evp7_visible_tool_summaries.py --check` 首次读取旧 66-summary；
  按 evidence packets -> tool summaries -> evidence packets 顺序重跑后通过：
  70 complete summaries；
- `build_evp7_evidence_packets.py --check` 通过：
  280 packets，E0/E2/E4/E6 各 70，G1/G2 passed；
- `run_evp7_tool_only_baselines.py --check` 通过：
  210 decisions，G3 passed；
- `run_evp7_merge_gate_schema_dry_run.py --check` 通过：
  280 valid parses，G4 passed；
- `analyze_evp7_schema_dry_run_metrics.py --check` 通过：
  no-API metric scaffold passed，仍要求真实 LLM verifier outputs；
- `build_evp7_g5_llm_prompt_manifest.py --check` 通过：
  280 prompt records，zero leakage failures；
- example preflight/check-only workflow 通过：
  structural_ready = true，api_ready = false，model_call_attempted = false。

ydl16 后边界：

- ydl16 admission 后结构化 EVP-7 cohort = 14 tasks / 5 projects / 70 candidates /
  280 evidence packets；
- 最新真实 DeepSeek G5 full run 仍为旧 12-task / 62-candidate /
  248-packet cohort；
- 不得把旧 248-run 的真实模型 claim 延伸到当前 280-packet structural
  cohort，除非后续显式授权并完成新的真实 280-packet run 与质量审计；
- 当时 15 bug 目标仍差 1 个 admission。

## 101. 2026-06-14 next controlled probe lane: youtube-dl_17

Inspect:

- 工作区在 ydl16 admission commit 后干净，本地 main ahead origin 5；
- `data/tasks/evp7_expansion_readiness.json` 当前 main cohort =
  14 tasks / 5 projects / 70 candidates / 280 packets；
- readiness 没有现成 P2P-candidate 队列，fresh-project promising candidates
  仍为 0；
- 未登记的 youtube-dl metadata-clean unittest lane 中，
  `bugsinpy_youtube-dl_17` 目标为单个
  `test.test_utils.TestUtil.test_cli_bool_option`；
- BugsInPy metadata:
  - buggy commit = `4bf22f7a1014c55e3358b5a419945071b152eafc`；
  - fixed commit = `5b232f46dcbdc805507c02edd4fd598f31d544d5`；
  - test file = `test/test_utils.py`；
  - requirements empty；
  - source patch 仅修改 `youtube_dl/utils.py`；
- 两个 commit 均已确认存在于本地 youtube-dl clone；
- 既有成功 P2P manifests 显示 `test_cli_bool_option` 可收集并稳定运行，
  因此 ydl17 是当前达到 15 bug 下限的最短可验证 lane。

Plan:

1. 复用本地 youtube-dl Git clone，串行构造 ydl17 buggy/fixed checkout；
2. 运行 retained F2P command，要求 buggy fail、fixed pass；
3. 若 F2P 成立，先 dry-run corrected-policy project-level P2P-broad：
   - `--exclude-nodeid-prefix "test.test_download.TestDownload"`；
   - canonical static tokens:
     `YoutubeDL(`, `download(`, `urlopen`, `http://`, `https://`；
4. dry-run 通过后再运行 bounded real P2P-broad；
5. 只有 F2P、P2P-broad、candidate construction 和 candidate validation 全部
   通过，才将 ydl17 纳入 `p2p_broad_main` 并重建 EVP-7 artifacts；
6. 若 checkout/F2P/P2P 任一失败，记录 blocker 到计划和经验文档，不做
   task-file P2P 降级，不引入兼容 shim 或依赖安装。

验收条件：

- 若 admission 成功：EVP-7 structural cohort 至少达到
  15 tasks / 74 candidates / 296 packets；
- 最新真实 DeepSeek G5 claim 仍限定在旧 12-task / 62-candidate /
  248-packet run，除非后续显式执行新的真实 G5 run。

执行结果：

- ydl17 本地 clone checkout 构造成功：
  - buggy/fixed marker 文件存在；
  - buggy diff 仅包含 fixed `test/test_utils.py`；
  - fixed diff 包含 fixed `test/test_utils.py` 和 `youtube_dl/utils.py`；
  - 两端 HEAD 均为 `4bf22f7a1014c55e3358b5a419945071b152eafc`，
    fixed 版本通过放回 fixed commit 变更文件表示修复态。
- F2P target command 结果：
  - buggy: `AssertionError`，因为缺失 optional boolean 参数仍进入
    `assert isinstance(param, bool)`；
  - fixed: pass。
- corrected-policy P2P-broad 成功：
  - collected/common nodeids = 2203；
  - excluded generated download nodeids = 1967；
  - excluded static external-dependency tests = 85；
  - excluded retained F2P oracle = 1；
  - excluded buggy-baseline failures = 4；
  - retained P2P-broad tests = 146；
  - collection error files = 0；
  - scope policy = `youtube_dl_dynamic_download_nodeid_exclusion_v1`。
- 新增 retained oracle：
  `scripts/oracles/youtubedl_17_cli_bool_option.py`；
- 新增 candidate builder：
  `scripts/build_youtubedl17_candidates.py`；
- retained-oracle validation 通过：
  - candidates = 4；
  - patch applied = 4/4；
  - oracle ran = 4/4；
  - oracle passed = 1/4。
- P2P validation 通过：
  - labels:
    - `correct_under_f2p_and_p2p_broad`: 1；
    - `incorrect_issue_not_fixed`: 3。
- `bugsinpy_youtube-dl_17` 已加入 `p2p_broad_main`。

修复/诊断：

- 初版 ydl17 oracle 直接在模块顶层 import `youtube_dl`，而
  `validate_patch_candidates.py` 用 research95 中的绝对脚本路径执行 oracle；
  此时 `sys.path[0]` 是 `scripts/oracles`，不是 candidate workdir，导致
  `ModuleNotFoundError: No module named 'youtube_dl'`；
- 已按既有 youtube-dl oracle 模式在 `main()` 中执行
  `sys.path.insert(0, str(Path.cwd()))` 后再 import project module；
- 修复后 retained-oracle validation 与 P2P candidate validation 均通过。

重建结果：

- `build_evp7_protocol_manifests.py --check` 通过：
  main tasks = 15；
- `build_evp7_candidate_manifest.py --check` 通过：
  candidates = 74，correct = 15，incorrect = 59；
- `run_evp7_visible_tests.py --run --check --timeout 90` 通过：
  74 records，71 completed，3 error；
- `build_evp7_visible_tool_summaries.py --check` 通过：
  74 complete summaries；
- `build_evp7_evidence_packets.py --check` 通过：
  296 packets，E0/E2/E4/E6 各 74，G1/G2 passed；
- `run_evp7_tool_only_baselines.py --check` 通过：
  222 decisions，G3 passed；
- `run_evp7_merge_gate_schema_dry_run.py --check` 通过：
  296 valid parses，G4 passed；
- `analyze_evp7_schema_dry_run_metrics.py --check` 通过：
  no-API metric scaffold passed，仍要求真实 LLM verifier outputs；
- `build_evp7_g5_llm_prompt_manifest.py --check` 通过：
  296 prompt records，zero leakage failures；
- example preflight/check-only workflow 通过：
  structural_ready = true，api_ready = false，model_call_attempted = false。

当前边界：

- 当前结构化 EVP-7 cohort = 15 tasks / 5 projects / 74 candidates /
  296 evidence packets；
- 15 bug 下限已达到，但计划上限仍允许继续 controlled expansion 到 20 bugs；
- 最新真实 DeepSeek G5 full run 仍为旧 12-task / 62-candidate /
  248-packet cohort；
- 不得把旧 248-run 的真实模型 claim 延伸到当前 296-packet structural
  cohort，除非后续显式授权并完成新的真实 296-packet run 与质量审计。

## 102. 2026-06-14 next controlled probe lane: youtube-dl_43

Inspect:

- ydl17 admission commit 后工作区干净，本地 main ahead origin 6；
- 15 bug 下限已达到，但计划上限仍允许继续 controlled expansion 到 20 bugs；
- 真实 G5 296-packet run 需要用户确认 API provider/model/cost/smoke/full-run
  permission，因此本轮不进入 API；
- 未登记且未记录 blocker 的 metadata-clean youtube-dl unittest lane 中，
  `bugsinpy_youtube-dl_43` 是最短 source diff：
  - target = `test.test_utils.TestUtil.test_url_basename`；
  - test file = `test/test_utils.py`；
  - source patch = `youtube_dl/utils.py` 中一行 `url_basename` regex 修复；
  - requirements empty；
  - buggy commit = `cecaaf3f58ad9f544dbb79af1e565d9353fa2b2d`；
  - fixed commit = `d6c7a367e88096bb17e323954002c084477fe908`；
- 两个 commit 均已确认存在于本地 youtube-dl clone；
- 最近 ydl16/ydl17 P2P manifests 显示 `test_url_basename` 可收集并稳定运行。

Plan:

1. 复用本地 youtube-dl Git clone，串行构造 ydl43 buggy/fixed checkout；
2. 运行 retained F2P command，要求 buggy fail、fixed pass；
3. 若 F2P 成立，先 dry-run corrected-policy project-level P2P-broad：
   - `--exclude-nodeid-prefix "test.test_download.TestDownload"`；
   - canonical static tokens:
     `YoutubeDL(`, `download(`, `urlopen`, `http://`, `https://`；
4. dry-run 通过后再运行 bounded real P2P-broad；
5. 只有 F2P、P2P-broad、candidate construction 和 candidate validation 全部
   通过，才将 ydl43 纳入 `p2p_broad_main` 并重建 EVP-7 artifacts；
6. 若 checkout/F2P/P2P 任一失败，记录 blocker，不做 task-file P2P 降级。

验收条件：

- 若 admission 成功：EVP-7 structural cohort 达到
  16 tasks / 78 candidates / 312 packets；
- 最新真实 DeepSeek G5 claim 仍限定在旧 12-task / 62-candidate /
  248-packet run，除非后续显式执行新的真实 run。

执行结果：

- ydl43 本地 clone checkout 构造成功：
  - buggy diff 仅包含 fixed `test/test_utils.py`；
  - fixed diff 包含 fixed `test/test_utils.py` 和 `youtube_dl/utils.py`；
  - 两端 HEAD 均为 `cecaaf3f58ad9f544dbb79af1e565d9353fa2b2d`，
    fixed 版本通过放回 fixed commit 变更文件表示修复态。
- F2P target command 结果：
  - buggy: `url_basename` 对多级路径 URL 返回空字符串；
  - fixed: pass。
- corrected-policy P2P-broad 成功：
  - collected/common nodeids = 324；
  - excluded generated download nodeids = 224；
  - excluded static external-dependency tests = 49；
  - excluded retained F2P oracle = 1；
  - excluded buggy-baseline failures = 32；
  - retained P2P-broad tests = 18；
  - collection error files = 0；
  - scope policy = `youtube_dl_dynamic_download_nodeid_exclusion_v1`。
- 新增 retained oracle：
  `scripts/oracles/youtubedl_43_url_basename.py`；
- 新增 candidate builder：
  `scripts/build_youtubedl43_candidates.py`；
- retained-oracle validation 通过：
  - candidates = 4；
  - patch applied = 4/4；
  - oracle ran = 4/4；
  - oracle passed = 1/4。
- P2P validation 通过：
  - labels:
    - `correct_under_f2p_and_p2p_broad`: 1；
    - `incorrect_issue_not_fixed`: 3。
- `bugsinpy_youtube-dl_43` 已加入 `p2p_broad_main`。

重建结果：

- `build_evp7_protocol_manifests.py --check` 通过：
  main tasks = 16；
- `build_evp7_candidate_manifest.py --check` 通过：
  candidates = 78，correct = 16，incorrect = 62；
- `run_evp7_visible_tests.py --run --check --timeout 90` 通过：
  78 records，75 completed，3 error；
- `build_evp7_visible_tool_summaries.py --check` 通过：
  78 complete summaries；
- `build_evp7_evidence_packets.py --check` 通过：
  312 packets，E0/E2/E4/E6 各 78，G1/G2 passed；
- `run_evp7_tool_only_baselines.py --check` 通过：
  234 decisions，G3 passed；
- `run_evp7_merge_gate_schema_dry_run.py --check` 通过：
  312 valid parses，G4 passed；
- `analyze_evp7_schema_dry_run_metrics.py --check` 通过：
  no-API metric scaffold passed，仍要求真实 LLM verifier outputs；
- `build_evp7_g5_llm_prompt_manifest.py --check` 通过：
  312 prompt records，zero leakage failures；
- example preflight/check-only workflow 通过：
  structural_ready = true，api_ready = false，model_call_attempted = false。

当前边界：

- 当前结构化 EVP-7 cohort = 16 tasks / 5 projects / 78 candidates /
  312 evidence packets；
- 15 bug 下限已达到，距 20 bug 上限还差 4 个 admission；
- 最新真实 DeepSeek G5 full run 仍为旧 12-task / 62-candidate /
  248-packet cohort；
- 不得把旧 248-run 的真实模型 claim 延伸到当前 312-packet structural
  cohort，除非后续显式授权并完成新的真实 312-packet run 与质量审计。

## 103. 2026-06-14 next controlled probe lane: youtube-dl_20

Inspect:

- ydl43 admission commit 后工作区干净，本地 main ahead origin 7；
- 当前结构化 EVP-7 cohort = 16 tasks / 5 projects / 78 candidates /
  312 packets，距 20 bug 上限还差 4 个 admission；
- 真实 G5 312-packet run 仍需用户确认 API/provider/model/cost/smoke/full-run
  permission，因此本轮继续 no-API controlled expansion；
- `bugsinpy_youtube-dl_20` 是 metadata-clean pure unittest lane：
  - target = `test.test_utils.TestUtil.test_get_element_by_attribute`；
  - test file = `test/test_utils.py`；
  - source patch = `youtube_dl/utils.py` 中
    `get_elements_by_attribute` HTML attribute regex 修复；
  - requirements empty；
  - buggy commit = `b6c9fe416243373bcb59eb8aa5ef0baca8f3c97c`；
  - fixed commit = `609ff8ca19f1c4c168a81121074b91cc0f0d4c47`；
- 两个 commit 均已确认存在于本地 youtube-dl clone。

Plan:

1. 复用本地 youtube-dl Git clone，串行构造 ydl20 buggy/fixed checkout；
2. 运行 retained F2P command，要求 buggy fail、fixed pass；
3. 若 F2P 成立，先 dry-run corrected-policy project-level P2P-broad；
4. dry-run 通过后运行 bounded real P2P-broad，继续使用
   `test.test_download.TestDownload` 动态下载 nodeid exclusion 和 canonical
   static tokens；
5. F2P、P2P-broad、candidate construction 和 candidate validation 全部通过后
   才 admission；
6. 失败则记录 blocker，不做 task-file P2P 降级。

验收条件：

- 若 admission 成功：EVP-7 structural cohort 达到
  17 tasks / 82 candidates / 328 packets；
- 最新真实 DeepSeek G5 claim 仍限定在旧 12-task / 62-candidate /
  248-packet run。

执行结果：

- ydl20 本地 clone checkout 构造成功：
  - buggy diff 仅包含 fixed `test/test_utils.py`；
  - fixed diff 包含 fixed `test/test_utils.py` 和 `youtube_dl/utils.py`；
  - 两端 HEAD 均为 `b6c9fe416243373bcb59eb8aa5ef0baca8f3c97c`，
    fixed 版本通过放回 fixed commit 变更文件表示修复态。
- F2P target command 结果：
  - buggy: `get_element_by_attribute` 对目标属性后的 valueless HTML
    attribute 返回 `None`；
  - fixed: pass。
- corrected-policy P2P-broad 成功：
  - collected/common nodeids = 2181；
  - excluded generated download nodeids = 1948；
  - excluded static external-dependency tests = 84；
  - excluded retained F2P oracle = 1；
  - excluded buggy-baseline failures = 6；
  - retained P2P-broad tests = 142；
  - collection error files = 0；
  - scope policy = `youtube_dl_dynamic_download_nodeid_exclusion_v1`。
- 新增 retained oracle：
  `scripts/oracles/youtubedl_20_get_element_by_attribute.py`；
- 新增 candidate builder：
  `scripts/build_youtubedl20_candidates.py`；
- retained-oracle validation 通过：
  - candidates = 4；
  - patch applied = 4/4；
  - oracle ran = 4/4；
  - oracle passed = 1/4。
- P2P validation 通过：
  - retained P2P-broad tests = 142；
  - labels:
    - `correct_under_f2p_and_p2p_broad`: 1；
    - `incorrect_issue_not_fixed`: 3。
- `bugsinpy_youtube-dl_20` 已加入 `p2p_broad_main`。

重建结果：

- `build_evp7_protocol_manifests.py --check` 通过：
  main tasks = 17；
- `build_evp7_candidate_manifest.py --check` 通过：
  candidates = 82，correct = 17，incorrect = 65；
- `run_evp7_visible_tests.py --run --check --timeout 90` 通过：
  82 records，79 completed，3 error；
- `build_evp7_visible_tool_summaries.py --check` 通过：
  82 complete summaries；
- `build_evp7_evidence_packets.py --check` 通过：
  328 packets，E0/E2/E4/E6 各 82，G1/G2 passed；
- `run_evp7_tool_only_baselines.py --check` 通过：
  246 decisions，G3 passed；
- `run_evp7_merge_gate_schema_dry_run.py --check` 通过：
  328 valid parses，G4 passed；
- `analyze_evp7_schema_dry_run_metrics.py --check` 通过：
  no-API metric scaffold passed，仍要求真实 LLM verifier outputs；
- `build_evp7_g5_llm_prompt_manifest.py --check` 通过：
  328 prompt records，zero leakage failures；
- example preflight/check-only workflow 通过：
  structural_ready = true，api_ready = false，model_call_attempted = false。

当前边界：

- 当前结构化 EVP-7 cohort = 17 tasks / 5 projects / 82 candidates /
  328 evidence packets；
- 15 bug 下限已达到，距 20 bug 上限还差 3 个 admission；
- 最新真实 DeepSeek G5 full run 仍为旧 12-task / 62-candidate /
  248-packet cohort；
- 不得把旧 248-run 的真实模型 claim 延伸到当前 328-packet structural
  cohort，除非后续显式授权并完成新的真实 328-packet run 与质量审计。

## 104. 2026-06-14 next controlled probe lane: youtube-dl_21

Inspect:

- ydl20 admission commit 后工作区干净，本地 main ahead origin 8；
- 当前结构化 EVP-7 cohort = 17 tasks / 5 projects / 82 candidates /
  328 packets，距 20 bug 上限还差 3 个 admission；
- readiness 当前没有新的 fresh-project promising lane，后续 admission 只能继续
  controlled youtube-dl pure-unittest lane，或等待用户确认真实 G5 API run；
- `bugsinpy_youtube-dl_21` 是 metadata-clean pure unittest lane：
  - target = `test.test_utils.TestUtil.test_urljoin`；
  - test file = `test/test_utils.py`；
  - source patch = `youtube_dl/utils.py` 中 `urljoin` 对 bytes base/path 的
    UTF-8 解码支持；
  - requirements empty；
  - buggy commit = `96182695e4e37795a30ab143129c91dab18a9865`；
  - fixed commit = `4b5de77bdb7765df4797bf068592926285ba709a`；
- local youtube-dl clone 已可读取该 commit pair 的 source/test diff：
  fixed test 新增 bytes base、bytes path、both-bytes 三个 F2P assertions。

Plan:

1. 复用本地 youtube-dl Git clone，串行构造 ydl21 buggy/fixed checkout；
2. 验证 marker、HEAD 和 diff 边界；
3. 运行 retained F2P command，要求 buggy fail、fixed pass；
4. 若 F2P 成立，先 dry-run corrected-policy project-level P2P-broad：
   - `--exclude-nodeid-prefix "test.test_download.TestDownload"`；
   - canonical static tokens:
     `YoutubeDL(`, `download(`, `urlopen`, `http://`, `https://`；
5. dry-run 通过后运行 bounded real P2P-broad；
6. F2P、P2P-broad、candidate construction 和 candidate validation 全部通过后
   才 admission；
7. 若 P2P 超时或 retained tests < 3，记录 blocker，不做 task-file P2P 降级。

验收条件：

- 若 admission 成功：EVP-7 structural cohort 达到
  18 tasks / 86 candidates / 344 packets；
- 最新真实 DeepSeek G5 claim 仍限定在旧 12-task / 62-candidate /
  248-packet run。

执行结果：

- ydl21 本地 clone checkout 构造成功：
  - buggy diff 仅包含 fixed `test/test_utils.py`；
  - fixed diff 包含 fixed `test/test_utils.py` 和 `youtube_dl/utils.py`；
  - 两端 HEAD 均为 `96182695e4e37795a30ab143129c91dab18a9865`，
    fixed 版本通过放回 fixed commit 变更文件表示修复态。
- F2P target command 结果：
  - buggy: bytes base URL 输入返回 `None`；
  - fixed: pass。
- corrected-policy P2P-broad 成功：
  - collected/common nodeids = 2107；
  - excluded generated download nodeids = 1879；
  - excluded static external-dependency tests = 81；
  - excluded retained F2P oracle = 1；
  - excluded buggy-baseline failures = 3；
  - retained P2P-broad tests = 143；
  - collection error files = 0；
  - scope policy = `youtube_dl_dynamic_download_nodeid_exclusion_v1`。
- 新增 retained oracle：
  `scripts/oracles/youtubedl_21_urljoin_bytes.py`；
- 新增 candidate builder：
  `scripts/build_youtubedl21_candidates.py`；
- retained-oracle validation 首次失败：
  - reference/base-only patch apply failed，原因是手写 diff hunk 末尾空白上下文
    被 builder normalize strip 后 hunk 行数不匹配；
  - 修复方式是调整 hunk 计数为实际输出行数，而不是依赖末尾空白上下文。
- retained-oracle validation 修复后通过：
  - candidates = 4；
  - patch applied = 4/4；
  - oracle ran = 4/4；
  - oracle passed = 1/4。
- P2P validation 通过：
  - retained P2P-broad tests = 143；
  - labels:
    - `correct_under_f2p_and_p2p_broad`: 1；
    - `incorrect_issue_not_fixed`: 3。
- `bugsinpy_youtube-dl_21` 已加入 `p2p_broad_main`。

重建结果：

- `build_evp7_protocol_manifests.py --check` 通过：
  main tasks = 18；
- `build_evp7_candidate_manifest.py --check` 通过：
  candidates = 86，correct = 18，incorrect = 68；
- `run_evp7_visible_tests.py --run --check --timeout 90` 通过：
  86 records，83 completed，3 error；
- 首次 `build_evp7_evidence_packets.py --check` 暴露 E6 仍只有旧的 82 个
  visible tool summaries；
- 按 evidence packets -> tool summaries -> evidence packets 顺序重跑后通过：
  344 packets，E0/E2/E4/E6 各 86，G1/G2 passed；
- `run_evp7_tool_only_baselines.py --check` 通过：
  258 decisions，G3 passed；
- `run_evp7_merge_gate_schema_dry_run.py --check` 通过：
  344 valid parses，G4 passed；
- `analyze_evp7_schema_dry_run_metrics.py --check` 通过：
  no-API metric scaffold passed，仍要求真实 LLM verifier outputs；
- `build_evp7_g5_llm_prompt_manifest.py --check` 通过：
  344 prompt records，zero leakage failures；
- example preflight/check-only workflow 通过：
  structural_ready = true，api_ready = false，model_call_attempted = false。

当前边界：

- 当前结构化 EVP-7 cohort = 18 tasks / 5 projects / 86 candidates /
  344 evidence packets；
- 15 bug 下限已达到，距 20 bug 上限还差 2 个 admission；
- 最新真实 DeepSeek G5 full run 仍为旧 12-task / 62-candidate /
  248-packet cohort；
- 不得把旧 248-run 的真实模型 claim 延伸到当前 344-packet structural
  cohort，除非后续显式授权并完成新的真实 344-packet run 与质量审计。

## 105. 2026-06-14 next controlled probe lane: youtube-dl_23

Inspect:

- ydl21 admission commit 后工作区干净，本地 main ahead origin 9；
- 当前结构化 EVP-7 cohort = 18 tasks / 5 projects / 86 candidates /
  344 packets，15 bug 下限已达成，距 20 bug 上限还差 2 个 admission；
- readiness 当前仍无新的 fresh-project promising lane；继续扩展时，最短可验证
  路径是已验证过 corrected-policy P2P 的 youtube-dl pure-unittest lane；
- `bugsinpy_youtube-dl_23` 是 metadata-clean pure unittest lane：
  - target = `test.test_utils.TestUtil.test_js_to_json_edgecases`；
  - test file = `test/test_utils.py`；
  - source patch = `youtube_dl/utils.py` 中 `js_to_json` 对 `//[^\n]*`
    single-line comment 的识别与删除；
  - buggy commit = `a22b2fd19bd8c08d50f884d1903486d4f00f76ec`；
  - fixed commit = `b3ee552e4b918fb720111b23147e24fa5475a74b`；
- 该 lane 与已超时的 ydl10/25/26 realworld lane 不同，目标是单一
  edgecases unittest；P2P 仍必须使用 canonical generated-download exclusion。

Plan:

1. 复用本地 youtube-dl Git clone，构造 ydl23 buggy/fixed checkout；
2. 验证 marker、HEAD 和 diff 边界；
3. 运行 retained F2P command，要求 buggy fail、fixed pass；
4. 若 F2P 成立，先 dry-run corrected-policy project-level P2P-broad：
   - `--exclude-nodeid-prefix "test.test_download.TestDownload"`；
   - canonical static tokens:
     `YoutubeDL(`, `download(`, `urlopen`, `http://`, `https://`；
5. dry-run 通过后运行 bounded real P2P-broad；
6. F2P、P2P-broad、candidate construction 和 candidate revalidation 全部通过后
   才 admission；
7. 若 P2P 超时或 retained tests < 3，记录 blocker，不做 task-file P2P 降级。

验收条件：

- 若 admission 成功：EVP-7 structural cohort 达到
  19 tasks / 90 candidates / 360 packets；
- 最新真实 DeepSeek G5 claim 仍限定在旧 12-task / 62-candidate /
  248-packet run。

执行结果：

- ydl23 本地 clone checkout 构造成功：
  - buggy diff 仅包含 fixed `test/test_utils.py`；
  - fixed diff 包含 fixed `test/test_utils.py` 和 `youtube_dl/utils.py`；
  - 两端 HEAD 均为 `a22b2fd19bd8c08d50f884d1903486d4f00f76ec`，
    fixed 版本通过放回 fixed commit 变更文件表示修复态。
- 初始 marker 从 ydl21 clone 复制后仍带 ydl21 commit pair 和 target command；
  已在 F2P 前修正为 ydl23 的 commit pair、source patch 和
  `test_js_to_json_edgecases` target。
- F2P target command 结果：
  - buggy: `// comment` case 生成不可解析 JSON，`json.loads` 抛出
    `JSONDecodeError`；
  - fixed: pass。
- corrected-policy P2P-broad 成功：
  - collected/common nodeids = 2059；
  - excluded generated download nodeids = 1836；
  - excluded static external-dependency tests = 82；
  - excluded retained F2P oracle = 1；
  - excluded buggy-baseline failures = 3；
  - retained P2P-broad tests = 137；
  - collection error files = 0；
  - scope policy = `youtube_dl_dynamic_download_nodeid_exclusion_v1`。
- 新增 retained oracle：
  `scripts/oracles/youtubedl_23_js_to_json_line_comments.py`；
- 新增 candidate builder：
  `scripts/build_youtubedl23_candidates.py`；
- retained-oracle validation 通过：
  - candidates = 4；
  - patch applied = 4/4；
  - oracle ran = 4/4；
  - oracle passed = 1/4。
- P2P validation 通过：
  - retained P2P-broad tests = 137；
  - labels:
    - `correct_under_f2p_and_p2p_broad`: 1；
    - `incorrect_issue_not_fixed`: 3。
- `bugsinpy_youtube-dl_23` 已加入 `p2p_broad_main`。

重建结果：

- `build_evp7_protocol_manifests.py --check` 通过：
  main tasks = 19；
- `build_evp7_candidate_manifest.py --check` 通过：
  candidates = 90，correct = 19，incorrect = 71；
- `run_evp7_visible_tests.py --run --check --timeout 90` 通过：
  90 records，87 completed，3 error；
- 首次 `build_evp7_evidence_packets.py --check` 暴露 E6 仍只有旧的 86 个
  visible tool summaries；
- 按 tool summaries -> evidence packets 顺序重跑后通过：
  360 packets，E0/E2/E4/E6 各 90，G1/G2 passed；
- `run_evp7_tool_only_baselines.py --check` 通过：
  270 decisions，G3 passed；
- `run_evp7_merge_gate_schema_dry_run.py --check` 通过：
  360 valid parses，G4 passed；
- `analyze_evp7_schema_dry_run_metrics.py --check` 通过：
  no-API metric scaffold passed，仍要求真实 LLM verifier outputs；
- `build_evp7_g5_llm_prompt_manifest.py --check` 通过：
  360 prompt records，zero leakage failures；
- example preflight/check-only workflow 通过：
  structural_ready = true，api_ready = false，model_call_attempted = false。

当前边界：

- 当前结构化 EVP-7 cohort = 19 tasks / 5 projects / 90 candidates /
  360 evidence packets；
- 15 bug 下限已达到，距 20 bug 上限还差 1 个 admission；
- 最新真实 DeepSeek G5 full run 仍为旧 12-task / 62-candidate /
  248-packet cohort；
- 不得把旧 248-run 的真实模型 claim 延伸到当前 360-packet structural
  cohort，除非后续显式授权并完成新的真实 360-packet run 与质量审计。

## 106. 2026-06-14 next controlled probe lane: youtube-dl_37

Inspect:

- ydl23 admission commit 后工作区干净，本地 main ahead origin 10；
- 当前结构化 EVP-7 cohort = 19 tasks / 5 projects / 90 candidates /
  360 packets，距 20 bug 上限还差 1 个 admission；
- readiness 当前仍无新的 fresh-project promising lane；继续扩展时，最短可验证
  路径仍是已验证过 corrected-policy P2P 的 youtube-dl pure-unittest lane；
- `bugsinpy_youtube-dl_37` 是 metadata-clean pure unittest lane：
  - target = `test.test_utils.TestUtil.test_uppercase_escpae`；
  - test file = `test/test_utils.py`；
  - source patch = `youtube_dl/utils.py` 中 `uppercase_escape` 改用
    `codecs.getdecoder('unicode_escape')`，避免 Python 3 `str.decode`；
  - buggy commit = `98b7cf1acefe398f792ca6ff4c5f84f1b7785fcb`；
  - fixed commit = `676eb3f2dd542be3e84780b18388253382d3e465`；
- 该 lane 不涉及网络或 downloader 业务，但 P2P 仍必须使用 canonical
  generated-download exclusion。

Plan:

1. 复用本地 youtube-dl Git clone，构造 ydl37 buggy/fixed checkout；
2. 验证 marker、HEAD 和 diff 边界；
3. 运行 retained F2P command，要求 buggy fail、fixed pass；
4. 若 F2P 成立，先 dry-run corrected-policy project-level P2P-broad：
   - `--exclude-nodeid-prefix "test.test_download.TestDownload"`；
   - canonical static tokens:
     `YoutubeDL(`, `download(`, `urlopen`, `http://`, `https://`；
5. dry-run 通过后运行 bounded real P2P-broad；
6. F2P、P2P-broad、candidate construction 和 candidate revalidation 全部通过后
   才 admission；
7. 若 P2P 超时或 retained tests < 3，记录 blocker，不做 task-file P2P 降级。

验收条件：

- 若 admission 成功：EVP-7 structural cohort 达到
  20 tasks / 94 candidates / 376 packets；
- 最新真实 DeepSeek G5 claim 仍限定在旧 12-task / 62-candidate /
  248-packet run。

执行结果：

- ydl37 本地 clone checkout 构造成功：
  - buggy diff 仅包含 fixed `test/test_utils.py`；
  - fixed diff 包含 fixed `test/test_utils.py` 和 `youtube_dl/utils.py`；
  - 两端 HEAD 均为 `98b7cf1acefe398f792ca6ff4c5f84f1b7785fcb`，
    fixed 版本通过放回 fixed commit 变更文件表示修复态。
- marker 在 checkout 构造时直接写入 ydl37 的 commit pair、source patch 和
  `test_uppercase_escpae` target，避免复用 clone 的旧 marker 污染审计记录。
- F2P target command 结果：
  - buggy: `uppercase_escape` 在 Python 3 `str.decode('unicode-escape')`
    调用处抛出 `AttributeError`；
  - fixed: pass。
- corrected-policy P2P-broad 成功：
  - collected/common nodeids = 528；
  - excluded generated download nodeids = 380；
  - excluded static external-dependency tests = 73；
  - excluded retained F2P oracle = 1；
  - excluded buggy-baseline failures = 44；
  - retained P2P-broad tests = 30；
  - collection error files = 0；
  - scope policy = `youtube_dl_dynamic_download_nodeid_exclusion_v1`。
- 新增 retained oracle：
  `scripts/oracles/youtubedl_37_uppercase_escape.py`；
- 新增 candidate builder：
  `scripts/build_youtubedl37_candidates.py`；
- retained-oracle validation 通过：
  - candidates = 4；
  - patch applied = 4/4；
  - oracle ran = 4/4；
  - oracle passed = 1/4。
- P2P validation 通过：
  - retained P2P-broad tests = 30；
  - labels:
    - `correct_under_f2p_and_p2p_broad`: 1；
    - `incorrect_issue_not_fixed`: 3。
- `bugsinpy_youtube-dl_37` 已加入 `p2p_broad_main`。

重建结果：

- `build_evp7_protocol_manifests.py --check` 通过：
  main tasks = 20；
- `build_evp7_candidate_manifest.py --check` 通过：
  candidates = 94，correct = 20，incorrect = 74；
- `run_evp7_visible_tests.py --run --check --timeout 90` 通过：
  94 records，91 completed，3 error；
- 先跑 `build_evp7_visible_tool_summaries.py --check` 时仍停在旧 90 条；
  原因是 evidence packet candidate universe 尚未更新；
- 按 evidence packets -> tool summaries -> evidence packets 顺序重跑后通过：
  376 packets，E0/E2/E4/E6 各 94，G1/G2 passed；
- `run_evp7_tool_only_baselines.py --check` 通过：
  282 decisions，G3 passed；
- `run_evp7_merge_gate_schema_dry_run.py --check` 通过：
  376 valid parses，G4 passed；
- `analyze_evp7_schema_dry_run_metrics.py --check` 通过：
  no-API metric scaffold passed，仍要求真实 LLM verifier outputs；
- `build_evp7_g5_llm_prompt_manifest.py --check` 通过：
  376 prompt records，zero leakage failures；
- example preflight/check-only workflow 通过：
  structural_ready = true，api_ready = false，model_call_attempted = false。

当前边界：

- 当前结构化 EVP-7 cohort = 20 tasks / 5 projects / 94 candidates /
  376 evidence packets；
- 15-20 bug 目标已达到上限；
- 最新真实 DeepSeek G5 full run 仍为旧 12-task / 62-candidate /
  248-packet cohort；
- 不得把旧 248-run 的真实模型 claim 延伸到当前 376-packet structural
  cohort，除非后续显式授权并完成新的真实 376-packet run 与质量审计。

## 107. 2026-06-14 freeze 20-task cohort and prepare G5 smoke

Inspect:

- 当前工作区干净，本地 main ahead origin 11；
- 当前结构化 EVP-7 cohort = 20 tasks / 5 projects / 94 candidates /
  376 evidence packets；
- 15-20 bug 目标已达到上限，继续补 bug 会进一步扩大 youtube-dl 占比，
  不应作为下一步；
- G5 no-API readiness 已通过：
  - prompt records = 376；
  - E0/E2/E4/E6 各 94；
  - prompt text not stored；
  - label leakage failures = 0；
  - API call attempted = false；
- 真实 G5 API smoke 仍缺少用户确认：
  provider、model、max_total_cost_usd、smoke_scope 和 full_run_permission。

Plan:

1. 冻结当前 20-task cohort 作为 EVP-7 structural cohort 上限；
2. 更新 G5 execution confirmation packet，明确 376-record 当前边界、
   必需用户确认和安全命令顺序；
3. 运行 strict preflight，预期因缺少用户确认而失败，但必须写出 JSON 证明
   structural_ready=true、api_ready=false、api_call_attempted=false；
4. 运行 guarded workflow check-only，证明 workflow 不会在未确认状态下调用模型；
5. 更新 README / docs index / readiness 文档 / engineering notes；
6. 不创建 `configs/evp7_g5_llm.local.json`，不读取凭证，不执行 `--execute`。

验收条件：

- tracked docs 明确 cohort frozen at 20 tasks / 94 candidates / 376 packets；
- strict preflight artifact 当前为“结构 ready、API not ready”；
- check-only summary 当前为 `model_call_attempted=false`；
- 后续真实 smoke 只能在用户确认 provider/model/cost/smoke/full-run 参数后执行。

执行结果：

- 已生成/刷新 G5 local config dry-run packet：
  - `data/reviews/evp7_g5_local_config_dry_run.json`；
  - `docs/experiments/evp7_g5_execution_confirmation_packet.md`；
  - local config write attempted = false；
  - api_call_attempted = false；
  - missing_or_unconfirmed =
    provider、model、max_total_cost_usd、smoke_scope、full_run_permission。
- strict preflight 已运行并按预期阻止 API-ready：
  - output = `data/reviews/evp7_g5_llm_preflight_strict_example.json`；
  - structural_ready = true；
  - api_ready = false；
  - api_call_attempted = false；
  - PowerShell wrapper 将预期 exit 1 视为 guard-pass。
- guarded workflow check-only 已运行：
  - output = `data/reviews/evp7_g5_workflow_check_only_example.json`；
  - structural_ready = true；
  - api_ready = false；
  - model_call_attempted = false；
  - api_call_attempted = false。
- 新增 freeze/smoke readiness 记录：
  `docs/experiments/evp7_20_task_freeze_and_g5_smoke_readiness.md`。
- `configs/evp7_g5_llm.local.json` 在工作区中已存在且被忽略；本轮 dry-run
  未创建、未修改、未暂存该 local config。

当前边界：

- EVP-7 cohort 冻结在 20 tasks / 5 projects / 94 candidates /
  376 evidence packets；
- 真实 G5 smoke 尚未执行，且不得在缺少用户确认时执行；
- 最新真实模型证据仍只来自旧 12-task / 62-candidate / 248-packet
  DeepSeek G5 run。

## 108. 2026-06-14 execute confirmed G5 smoke

Inspect:

- 当前工作区干净，本地 main ahead origin 12；
- EVP-7 cohort 已冻结在 20 tasks / 5 projects / 94 candidates /
  376 evidence packets；
- strict preflight/check-only example 已证明结构 ready，但因缺少用户确认
  API not ready；
- 用户已确认采用以下 G5 execution 参数：
  - api_provider = `deepseek_official`；
  - model = `deepseek-v4-pro`；
  - max_total_cost_usd = `10`；
  - smoke_scope = `4`；
  - full_run_permission = true。

Plan:

1. 用确认参数写入 ignored `configs/evp7_g5_llm.local.json`；
2. 运行 strict preflight，要求 structural_ready=true 且 api_ready=true；
3. 运行 guarded workflow check-only，要求 `model_call_attempted=false`；
4. 执行 4-packet real smoke：
   `run_evp7_g5_llm_workflow.py --execute --limit 4`；
5. 审计 smoke 输出：
   - review_count = 4；
   - `mock_run=false`；
   - `parse_status` invalid rate <= 0.2；
   - cost <= 10；
   - raw outputs 只保留在 ignored `outputs/`；
6. smoke 通过后再决定是否进入 376-record full run；不得在未完成 smoke
   审计前直接 full run。

验收条件：

- 如果 credentials/API 正常：生成 smoke outputs 并记录 smoke gate；
- 如果 credentials/API 失败：记录 blocker，不修改 prompt 或扩量；
- 本轮 API 调用仅限 smoke 4 packets。

执行结果：

- 已写入 ignored local config：
  `configs/evp7_g5_llm.local.json`；
- strict preflight 通过：
  - output = `outputs/evp7_g5_llm_376_smoke_001/preflight_strict.json`；
  - structural_ready = true；
  - api_ready = true；
  - api_call_attempted = false；
- check-only workflow 通过：
  - output = `outputs/evp7_g5_llm_376_smoke_001/check_only.json`；
  - model_call_attempted = false；
  - api_call_attempted = false；
- 4-packet real smoke 已执行：
  - run dir = `outputs/evp7_g5_llm_376_smoke_001`；
  - review_count = 4；
  - E0/E2/E4/E6 各 1 条，均属于 `evp7_candidate_0001`；
  - mock_run = false for 4/4；
  - api_call_attempted = true for 4/4；
  - parse_status = valid for 4/4；
  - invalid_output_rate = 0.0；
  - decisions = escalate for 4/4；
  - workflow observed cost = 0.0。
- 已生成 raw-output-free smoke summary：
  - `data/reviews/evp7_g5_llm_376_smoke_summary.json`；
  - `docs/experiments/evp7_g5_llm_376_smoke_result.md`。

诊断：

- smoke parser/API gate 通过；
- 但 provider response 未提供可用成本遥测，workflow 记录的
  `cost_usd=0.0` 不能证明真实成本为 0；
- 因此当前不能可靠执行 `max_total_cost_usd=10` 的成本上限。

当前边界：

- 不直接进入 376-record full run；
- full run blocked pending cost observability fix or explicit user override；
- smoke 仅证明真实 API/parser path 可用，不构成当前 376-packet cohort 的
  G5 full-run evidence。

## 109. 2026-06-14 repair G5 cost observability

Inspect:

- 当前工作区干净，本地 main ahead origin 13；
- 4-packet smoke 已证明 API/parser path 可用，但 review 记录只写入
  `cost_usd`，没有保留 provider `usage`；
- runner 当前只读取 `response["usage"]["cost"]`，DeepSeek official 的
  OpenAI-compatible response 通常提供 token usage 而非直接账单 cost；
- 因此 `cost_usd=0.0` 是 client 映射缺口，不能作为预算门依据。

Plan:

1. 在 G5 runner 内新增 provider/model cost extraction：
   - 优先使用 provider 返回的 `usage.cost`；
   - 如果 cost 缺失，则从 prompt/completion/cache token usage 按
     provider/model price estimate 计算；
   - 明确记录 `cost_observability`，区分 provider-reported、estimated、
     missing_usage 和 mock；
2. 每条 review 写入 raw-output-free 的 usage summary 和 cost estimate
   metadata，不写 prompt text 或 raw model content 到 tracked 文件；
3. workflow summary 使用同一成本聚合结果执行 `max_total_cost_usd` gate；
4. 用合成 DeepSeek response 做 no-API 最小验证，确认 token usage 能生成
   非零估算成本；
5. 更新 smoke result/readiness 文档、README、docs index 和 engineering notes；
6. 不执行新的真实 API smoke，不执行 376-record full run。

验收条件：

- 合成 DeepSeek usage 下 `cost_usd > 0` 且 `cost_source=estimated_from_tokens`；
- 缺失 usage 时明确标记 cost observability failure，不能被当作 0 成本通过；
- check-only 仍不调用 API；
- local quality gate 通过。

执行结果：

- 已修复 `scripts/run_evp7_g5_llm_workflow.py`：
  - 每条 review 保留 raw-output-free `usage` summary；
  - 新增 `cost_source`、`cost_observability`、`cost_pricing`；
  - 优先读取 provider-reported `usage.cost`；
  - 对 `deepseek_official` / `deepseek-v4-pro` 使用 DeepSeek official
    Models & Pricing token 单价估算成本；
  - 如果 provider usage 或受支持 pricing 缺失，则 `cost_usd=null`，
    workflow summary 写出后以 unknown cost 失败；
  - mock 路径继续标记 `mock_no_billing`，不污染真实成本统计。
- 已新增修复记录：
  `docs/experiments/evp7_g5_cost_observability_fix.md`。
- 已用合成 response 完成 no-API 最小验证：
  - prompt/completion token usage -> `cost_source=estimated_from_tokens`，
    `cost_usd=0.000609`；
  - cache hit/miss split usage -> non-zero estimate；
  - missing usage -> `cost_source=unknown` 且 aggregate unknown count = 1；
  - mock workflow `--limit 1` 未调用 API，记录 `mock_no_billing`。
- 本地质量门通过：`python scripts\run_local_quality_gate.py` -> `passed=true`。

当前边界：

- 旧 `outputs/evp7_g5_llm_376_smoke_001` 不能回填成本，因为 review 记录
  未保存 provider `usage`；
- 后续 G5 smoke/full run 具备成本可观测路径；
- 本轮未执行新的真实 API smoke，也未执行 376-record full run。

## 110. 2026-06-14 run post-repair G5 smoke cost check

Inspect:

- 当前工作区干净，本地 main ahead origin 14；
- ignored `configs/evp7_g5_llm.local.json` 仍使用用户确认配置：
  `deepseek_official` / `deepseek-v4-pro` / `max_total_cost_usd=10` /
  `smoke_scope=4` / `full_run_permission=true`；
- 新输出目录 `outputs/evp7_g5_llm_376_smoke_002` 尚不存在；
- 上一轮已修复成本可观测性，但尚未用真实 provider response 验证。

Plan:

1. 用现有 ignored local config 跑 strict preflight，要求
   `structural_ready=true`、`api_ready=true`、`api_call_attempted=false`；
2. 跑 workflow check-only，要求 `model_call_attempted=false`；
3. 执行新的 4-packet real smoke 到
   `outputs/evp7_g5_llm_376_smoke_002`，不覆盖旧 smoke；
4. 审计新 smoke：
   - review_count = 4；
   - mock_run=false for 4/4；
   - parse_status valid for 4/4；
   - `usage` summary 存在；
   - `cost_source` 为 `estimated_from_tokens` 或
     `provider_reported_usage_cost`；
   - `unknown_cost_record_count=0`；
   - `total_cost_usd <= 10`；
5. 仅在 smoke 审计通过后更新 raw-output-free tracked summary/docs；
6. 本轮不执行 376-record full run。

验收条件：

- 真实 API smoke 验证成本可观测性；
- raw model outputs 仍只留在 ignored `outputs/`；
- 如果 API 或 cost gate 失败，记录 blocker 并停止，不扩量。

执行结果：

- strict preflight 通过：
  - output = `outputs/evp7_g5_llm_376_smoke_002/preflight_strict.json`；
  - structural_ready = true；
  - api_ready = true；
  - api_call_attempted = false。
- check-only workflow 通过：
  - output = `outputs/evp7_g5_llm_376_smoke_002/check_only.json`；
  - model_call_attempted = false；
  - api_call_attempted = false。
- 4-packet real smoke 已执行：
  - run dir = `outputs/evp7_g5_llm_376_smoke_002`；
  - review_count = 4；
  - E0/E2/E4/E6 各 1 条，均属于 `evp7_candidate_0001`；
  - mock_run = false for 4/4；
  - api_call_attempted = true for 4/4；
  - parse_status = valid for 4/4；
  - invalid_output_rate = 0.0；
  - decisions = accept 1 / escalate 3；
  - usage summary present for 4/4；
  - `cost_source=estimated_from_tokens` for 4/4；
  - `cost_observability=estimated_from_provider_token_usage` for 4/4；
  - `unknown_cost_record_count=0`；
  - estimated total cost USD = 0.003392942；
  - budget gate passed against `max_total_cost_usd=10`。
- 已生成 raw-output-free smoke summary：
  - `data/reviews/evp7_g5_llm_376_smoke_002_summary.json`；
  - `docs/experiments/evp7_g5_llm_376_smoke_002_result.md`。
- 本地质量门通过：`python scripts\run_local_quality_gate.py` -> `passed=true`。

当前边界：

- 成本可观测性已被真实 smoke 验证；
- smoke_002 仍不是 376-packet full run evidence；
- 下一步可进入“是否执行 376-record full run”的决策和执行闭环，但本轮未执行 full run。

## 111. 2026-06-14 execute post-repair 376-packet G5 full run

Inspect:

- 当前工作区干净，本地 main ahead origin 15；
- ignored `configs/evp7_g5_llm.local.json` 仍使用用户确认配置：
  `deepseek_official` / `deepseek-v4-pro` / `max_total_cost_usd=10` /
  `smoke_scope=4` / `full_run_permission=true`；
- post-repair smoke_002 已验证真实 API/parser/cost-observability path：
  4/4 valid、4/4 usage summary、unknown cost = 0、estimated total cost
  USD = 0.003392942；
- 新 full-run 输出目录 `outputs/evp7_g5_llm_376_full_001` 尚不存在；
- `summarize_evp7_g5_llm_full_run.py` 支持指定 reviews/metrics/workflow
  和 summary 输出路径。

Plan:

1. 用现有 ignored local config 跑 full-run strict preflight，要求
   `structural_ready=true`、`api_ready=true`、`api_call_attempted=false`；
2. 跑 workflow check-only，要求 `model_call_attempted=false`；
3. 执行完整 376-packet real run：
   - `--execute --limit 0`；
   - 输出到 `outputs/evp7_g5_llm_376_full_001`；
   - `--concurrency 4`，保持 ordered JSONL；
4. 审计 full run：
   - review_count = 376；
   - E0/E2/E4/E6 各 94；
   - non-mock/API-attempted for 376/376；
   - parse invalid rate；
   - `unknown_cost_record_count=0`；
   - total cost <= 10；
5. 生成 raw-output-free tracked summary/report；
6. 更新 README、docs index、plan、engineering notes 和必要的 claim-boundary
   文档；
7. 本轮不改 prompt，不扩 cohort。

验收条件：

- full run 完整结束且成本可观测；
- raw model outputs 仍只保留在 ignored `outputs/`；
- 如果 API、parse、cost 或 completeness gate 失败，记录 blocker 并停止。

执行结果：

- strict preflight 通过：
  - output = `outputs/evp7_g5_llm_376_full_001/preflight_strict.json`；
  - structural_ready = true；
  - api_ready = true；
  - api_call_attempted = false。
- check-only workflow 通过：
  - output = `outputs/evp7_g5_llm_376_full_001/check_only.json`；
  - model_call_attempted = false；
  - api_call_attempted = false。
- 376-packet real full run 已完成：
  - run dir = `outputs/evp7_g5_llm_376_full_001`；
  - concurrency = 4；
  - review_count = 376；
  - E0/E2/E4/E6 各 94；
  - mock_run = false for 376/376；
  - api_call_attempted = true for 376/376；
  - parse_status = valid for 376/376；
  - invalid_output_rate = 0.0；
  - decisions = accept 9 / escalate 143 / reject 224；
  - by level:
    - E0: accept 1 / escalate 49 / reject 44；
    - E2: escalate 57 / reject 37；
    - E4: accept 1 / escalate 21 / reject 72；
    - E6: accept 7 / escalate 16 / reject 71；
  - `cost_source=estimated_from_tokens` for 376/376；
  - `cost_observability=estimated_from_provider_token_usage` for 376/376；
  - `unknown_cost_record_count=0`；
  - estimated total cost USD = 0.327352058；
  - budget gate passed against `max_total_cost_usd=10`；
  - `g5_signal_claim_status=real_llm_verifier_signal_observed_on_evp7`。
- Metrics:
  - G5 metric scaffold = passed；
  - E4 false_accept_rate = 0.0，accepted_precision = 1.0，
    correct_recall = 0.05，evidence_gain_vs_e0 = 7.0；
  - E6 false_accept_rate = 0.0，accepted_precision = 1.0，
    correct_recall = 0.35，evidence_gain_vs_e0 = 14.25。
- 已生成 tracked raw-output-free summary/report：
  - `data/reviews/evp7_g5_llm_376_full_summary.json`；
  - `docs/experiments/evp7_g5_llm_376_full_result.md`。
- 已生成 tracked quality audit：
  - `data/reviews/evp7_g5_376_full_quality_audit.json`；
  - `docs/experiments/evp7_g5_376_full_quality_audit.md`；
  - status = `passed_with_limitations`。
- 旧 `audit_api_run_completeness.py` 已试跑但不适配 G5 schema：
  它要求旧 API-pilot raw_response_path/raw_response_sha256/patch_id 字段。
  G5 full-run 完整性以 G5 summary + quality audit 为准。
- 本地质量门通过：`python scripts\run_local_quality_gate.py` -> `passed=true`。

当前边界：

- 最新真实 DeepSeek V4 G5 full run 已覆盖当前 frozen
  20-task / 94-candidate / 376-packet cohort；
- 支持 bounded EVP-7 pilot signal claim：当前 run 产生真实 LLM verifier
  signal，且 evidence-level metrics 有变化；
- 仍不支持：
  - scale-generalized paper claim；
  - LLM 明确优于 deterministic visible-test/tool-only baseline；
  - E6 严格优于 E4；
  - runner-estimated cost 等同外部 DeepSeek 账单。

## 112. 2026-06-15 refresh paper-facing artifacts for 376-run

Inspect:

- 当前工作区干净，本地 main ahead origin 16；
- 最新真实 DeepSeek V4 G5 full run 已覆盖 frozen
  20-task / 94-candidate / 376-packet cohort；
- `scripts/audit_paper_readiness.py` 默认仍读取旧
  `evp7_g5_llm_full_run_summary.json` / `evp7_g5_full_run_quality_audit.json`
  路径，且 hard-code 248 records / 62 candidates / 62 per evidence level；
- `scripts/write_paper_tables.py` 当前只生成 pre-API paper tables，文件头明确写
  “do not include real model-review results”；
- `docs/paper/patch_verification_draft.md` 仍是 2026-06-05 旧
  tool-augmented/full-run draft 叙述。

Plan:

1. 更新 `audit_paper_readiness.py`，让 EVP-7 G5 readiness 默认使用
   376-run summary/audit，并检查 376 records / 94 candidates / 94 per level；
2. 更新 `write_paper_tables.py`，在保留旧 pre-API tables 的同时新增
   EVP-7 G5 376-run result table 和 claim-boundary/cost summary；
3. 重新生成 `docs/paper/generated_tables.md` 和
   `docs/paper/generated_tables.tex`；
4. 运行 `audit_paper_readiness.py`，确认
   `evp7_bounded_pilot_claim_ready=true` 和
   `current_result_claim_ready=true`；
5. 更新 README / docs index / paper draft / engineering notes；
6. 运行 local quality gate；
7. 本轮不跑 API、不扩 cohort、不改 G5 prompt。

验收条件：

- generated tables 明确包含 376-run G5 real LLM metrics；
- paper readiness 不再误读旧 248-run 为当前结果；
- claim boundary 继续排除 scale-generalized、baseline-superiority、
  E6 strict superiority 和 external-billing claims。

Execute:

- 已更新 `scripts/audit_paper_readiness.py` 默认输入和 readiness cardinality：
  当前 EVP-7 G5 readiness 读取 376-run summary/audit，并检查
  376 records / 94 candidates / E0/E2/E4/E6 各 94；
- 已更新 `scripts/write_paper_tables.py`，在既有 dataset/baseline/repro
  tables 后新增 EVP-7 G5 376-run result table、cost observability summary
  和 claim-boundary table；
- 已重新生成 `docs/paper/generated_tables.md` 和
  `docs/paper/generated_tables.tex`；
- 已更新 `docs/paper/patch_verification_draft.md`，把当前 draft 边界改为
  EVP-7 376-run bounded-pilot result，并保留 prompt-only negative、
  tool-augmented conditional positive 和 EVP-7 bounded pilot 三阶段叙述；
- 已同步 README、docs index 和 engineering notes。

Verify:

- `python -m compileall scripts\write_paper_tables.py scripts\audit_paper_readiness.py`
  通过；
- `python scripts\write_paper_tables.py --out-md docs\paper\generated_tables.md --out-tex docs\paper\generated_tables.tex`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过：
  - `evp7_bounded_pilot_claim_ready=true`；
  - `current_result_claim_ready=true`；
  - `prompt_only_positive_claim_ready=false` 仍由旧
    `stop_or_redesign` gate 阻止，符合 claim boundary；
- `python -m json.tool outputs\paper_readiness\latest.json > $null` 通过；
- `git diff --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。
- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续运行两次均通过，生成 5-page PDF；第二次无 label rerun warning，
  仅保留 underfull hbox 和 MiKTeX update 提示。

结论：

- 本轮是按计划执行的 paper-facing refresh，没有调用 API、没有扩 cohort、
  没有修改 G5 prompt；
- 当前 paper readiness 已以 376-run 作为 EVP-7 G5 当前结果；
- 旧 248-run 文件只作为 historical artifact 保留。

## 113. 2026-06-15 refresh IEEE LaTeX draft for 376-run

Inspect:

- 当前工作区干净，本地 main ahead origin 17；
- 上一轮已完成 paper-facing 376-run refresh：
  `generated_tables.md/.tex`、Markdown paper draft、README、INDEX、
  engineering notes 和 paper readiness 都已指向当前
  20-task / 94-candidate / 376-packet G5 result；
- `docs/paper/ieee_submission_draft.tex` 和
  `scripts/write_ieee_latex_draft.py` 仍主要停留在 first API pilot +
  tool-augmented redesign 叙述，未在正文中解释 EVP-7 376-run bounded
  evidence-visibility result；
- `generated_tables.tex` 已包含 EVP-7 G5 376-run result table 和 claim
  boundary table，因此本轮不需要重做 cohort、API、prompt 或底层 metrics。

Plan:

1. 更新 `scripts/write_ieee_latex_draft.py`，让 IEEE draft generator 读取
   当前 376-run summary/audit，并在 abstract、RQ、结果、model boundary、
   threats 和 conclusion 中加入 bounded EVP-7 G5 结果；
2. 重新生成 `docs/paper/ieee_submission_draft.tex`；
3. 同步 README、docs index、engineering notes 和本计划；
4. 运行最小生成/编译/quality gates；
5. 本轮不跑 API、不扩 cohort、不改 G5 prompt。

验收条件：

- IEEE draft 正文不再只停留在 30-candidate/tool-augmented 阶段；
- IEEE draft 明确包含 376 records、20 tasks、94 candidates、EVP-7 G5
  bounded pilot、estimated cost 和 unsupported claims；
- generated tables 中的 EVP-7 表格继续被 IEEE draft 引用；
- local quality gate 通过。

Execute:

- 已更新 `scripts/write_ieee_latex_draft.py`：
  - 新增 `--evp7-summary` 和 `--evp7-quality-audit` 默认输入；
  - 从当前 376-run raw-output-free summary/audit 提取 provider/model、
    review_count、candidate_count、cost summary、E4/E6 metrics 和 unsupported
    claims；
  - 在 abstract、RQ5、EVP-7 result section、claim-boundary caption、
    model-selection boundary、threats 和 conclusion 中写入 bounded EVP-7
    G5 结果；
- 已重新生成 `docs/paper/ieee_submission_draft.tex`；
- 已同步 README、docs index 和 engineering notes。

Verify:

- `python -m compileall scripts\write_ieee_latex_draft.py` 通过；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，EVP-7 bounded pilot claim ready 仍为 true；
- IEEE draft 一致性检查命中 RQ5、`EVP-7 Evidence-Visibility Result`、
  `tab:evp7-g5-results`、`tab:evp7-claim-boundary`、94 candidates、
  376 evidence records、0.3274 cost 和 unsupported claims；
- stale-text check 未命中旧的 30-candidate-only/current-pilot-only 结论；
- `git diff --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮按计划完成 IEEE LaTeX draft refresh；
- 论文 Markdown draft、generated tables、paper readiness 和 IEEE submission
  draft 现在都对齐到当前 376-run bounded EVP-7 G5 claim boundary；
- 本轮未调用 API、未扩 cohort、未修改 G5 prompt。

## 114. 2026-06-15 refresh final-paper roadmap current state

Inspect:

- 当前工作区干净，本地 main ahead origin 18；
- `outputs/paper_readiness/latest.md` 显示：
  - `current_result_claim_ready=yes`；
  - `evp7_bounded_pilot_claim_ready=yes`；
  - `prompt-only positive claim ready=no`；
  - EVP-7 current result = 376 reviews / 94 candidates / E0-E6 各 94；
- `data/cohorts/task_cohort_registry.json` 当前 inferred main cohort =
  20 tasks / 5 projects，其中 youtube-dl 13、cookiecutter 3、PySnooper 2、
  httpie 1、tqdm 1；
- `docs/plans/final_paper_roadmap_zh.md` 作为 canonical roadmap，仍在
  Stage B/C 和 EVP-7 protocol 状态中保留 2026-06-11/12-task/248-packet
  口径，并写着下一阶段继续扩到 15-20 bugs；
- 当前 15-20 bugs 中期增强版上限已经达到，继续扩 bug 不应再作为默认下一步。

Plan:

1. 更新 `docs/plans/final_paper_roadmap_zh.md` 的当前状态段，明确当前主
   cohort 已冻结在 20 tasks / 94 candidates / 376 evidence packets；
2. 明确 248-run、12-task 叙述只保留为历史 checkpoint；
3. 更新 README / docs index / engineering notes 中仍暗示“下一步扩到
   15-20 bugs”的当前口径；
4. 运行 paper/readiness/local quality gate；
5. 本轮不跑 API、不扩 cohort、不改 prompt、不修改 tracked evidence 数据。

验收条件：

- canonical roadmap 不再把“扩到 15-20 bugs”写作当前下一步；
- roadmap 当前状态与 registry/summary 一致：20 tasks / 5 projects /
  94 candidates / 376 evidence packets；
- 248-run 明确是 historical checkpoint；
- quality gates 通过。

Execute:

- 已更新 `docs/plans/final_paper_roadmap_zh.md`：
  - 当前建议从“再扩到 15-20 bugs”改为“15-20 bugs 已达到上限，先巩固
    20-task 结果、论文口径、统计/图表和 claim boundary”；
  - Stage B/C 当前状态改为 2026-06-15，列出 frozen 20-task cohort；
  - 记录当前项目分布：youtube-dl 13、cookiecutter 3、PySnooper 2、
    httpie 1、tqdm 1；
  - 将 12-task/248-run 标为 historical checkpoint；
  - 新增 current 376-run 状态：376/376 parse-valid、94 candidates、
    E0/E2/E4/E6 各 94、estimated total cost USD 0.327352058、
    `passed_with_limitations` claim boundary；
- 已更新 README，说明 15-20 bug 目标已经达到并冻结，继续扩量需要新的
  30-50 bug decision boundary；
- 已更新 docs index，修正 EVP-7 protocol pilot 和 youtube-dl_4 admission
  的 historical/current result 关系；
- 已更新 engineering notes，记录 canonical roadmap current-state drift。

Verify:

- stale text search 未命中会把 12/248 或 13/264 当成当前结果、或把
  “扩到 15-20 bugs”当成当前下一步的文本；
- `git diff --check` 通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、
  `evp7_bounded_pilot_claim_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮按计划完成 canonical final-paper roadmap current-state refresh；
- 当前计划入口不再误导继续补 bug 到 15-20，下一步应围绕 frozen 20-task
  结果的统计/图表/claim consolidation 或新的 30-50 bug 决策展开；
- 本轮未调用 API、未扩 cohort、未修改 G5 prompt 或 tracked evidence 数据。

## 115. 2026-06-15 add EVP-7 evidence visibility curve figure

Inspect:

- 当前工作区干净，本地 main ahead origin 19；
- canonical roadmap 当前建议已经转为 frozen 20-task 结果巩固；
- `docs/plans/final_paper_roadmap_zh.md` 明确要求把 E0-E6 主结果组织为
  `Evidence Visibility Curve`，核心曲线至少包含 false accept rate、
  correct recall、accepted precision、escalation rate 和 safety/utility；
- `scripts/generate_paper_figures.py` 当前只生成 5 张旧 pilot 图，其中
  `fig4_result_tradeoff` 仍是 30-candidate prompt/tool-augmented 结果图，
  没有当前 376-run 的 evidence-level curve；
- 当前 376-run summary 已包含 E0/E2/E4/E6 的 false accept、correct recall、
  accepted precision、escalation rate 和 Evidence Gain，可直接生成 tracked
  reproducible figure。

Plan:

1. 更新 `scripts/generate_paper_figures.py`，读取
   `data/reviews/evp7_g5_llm_376_full_summary.json` 并新增
   `fig6_evp7_visibility_curve`；
2. 更新 figure manifest、figures README、artifact audit required files；
3. 更新 IEEE draft generator，让当前投稿稿引用 fig6；
4. 重新生成 figures 和 IEEE draft；
5. 同步 README / docs index / engineering notes / current plan；
6. 运行最小生成、LaTeX、paper readiness、local quality gates；
7. 本轮不跑 API、不扩 cohort、不改 G5 prompt。

验收条件：

- `docs/figures/fig6_evp7_visibility_curve.{pdf,svg,png}` 存在；
- figure manifest 记录 6 张图；
- IEEE draft 引用 fig6，并把 fig4 与 fig6 的语义区分清楚；
- quality gates 通过。

Execute:

- 已更新 `scripts/generate_paper_figures.py`：
  - 新增 `--evp7-summary` 默认输入
    `data/reviews/evp7_g5_llm_376_full_summary.json`；
  - 新增 `fig6_evp7_visibility_curve`，从当前 376-run summary 读取
    E0/E2/E4/E6 的 false accept rate、accepted precision、correct recall、
    escalation rate 和 Evidence Gain；
  - 对 E2 accepted precision 为空的情况使用散点缺口表示，避免把 undefined
    precision 误画为连续曲线；
  - 为 SVG/PDF 输出增加稳定 metadata，减少可重复生成时的无意义漂移；
- 已重新生成 `docs/figures/fig1` 到 `fig6` 的 PDF/SVG/PNG，并更新
  `docs/figures/figure_manifest.json` 到 6 张图；
- 已更新 `docs/figures/README.md`，明确 `fig4_result_tradeoff` 是 first-pilot
  tradeoff 图，`fig6_evp7_visibility_curve` 是当前 EVP-7 376-run evidence
  visibility curve；
- 已更新 `scripts/write_ieee_latex_draft.py` 和
  `docs/paper/ieee_submission_draft.tex`，在 EVP-7 结果段落后加入 fig6，并
  保持 fig4/fig6 语义边界；
- 已更新 `scripts/audit_anonymous_artifact.py`，将 fig6 PDF 纳入 anonymous
  artifact required files；
- 已同步 README、docs index、anonymous artifact 文档和 engineering notes；
- 本轮未调用 API、未扩 cohort、未修改 G5 prompt，也未跟踪 raw model outputs；
- 因 required files 变更后旧 zip 缺少 fig6 PDF，已重新生成 ignored
  `artifacts/research95_anonymous_artifact.zip` 与 manifest，并重新审计通过。

Verify:

- `python -m compileall scripts\generate_paper_figures.py scripts\write_ieee_latex_draft.py scripts\audit_anonymous_artifact.py`
  通过；
- `python scripts\generate_paper_figures.py` 通过，输出 `figure_count = 6`；
- `docs/figures/fig6_evp7_visibility_curve.png` 已人工检查：曲线、bar、legend
  和 E2 precision undefined 注释可读，未把 E2 precision 画成连续值；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；
- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续运行后通过，生成 6 页 IEEE draft PDF；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、
  `evp7_bounded_pilot_claim_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮按计划完成 frozen 20-task / 376-record EVP-7 evidence visibility curve
  图形补齐；
- 当前 paper figures、IEEE draft、artifact audit 和 local quality gate 已对齐
  到 fig6；
- 下一步应继续围绕 frozen cohort 的统计/图表/claim consolidation 推进，而
  不是默认继续补 bug。

## 116. 2026-06-15 add EVP-7 statistical analysis artifact

Inspect:

- 当前工作区干净，本地 main ahead origin 20；
- 第 115 节已完成 `fig6_evp7_visibility_curve`，local quality gate 通过；
- canonical roadmap 的下一步明确是 frozen 20-task cohort 的统计/图表和
  claim-boundary 巩固，不是继续默认补 bug；
- roadmap 的统计分析要求至少覆盖 Wilson confidence interval、bootstrap
  confidence interval、per-project breakdown、per-patch-source breakdown、
  per-evidence-level comparison、paired comparison 和 effect size；
- 当前 `docs/paper/generated_tables.md` 只有点估计和 claim boundary，尚未有
  tracked 统计区间或 paired delta artifact；
- ignored `outputs/evp7_g5_llm_376_full_001/reviews.jsonl` 可用于读取
  parse/decision/cost 等结构字段；tracked `data/patches/evp7_candidates.jsonl`
  提供 evaluator labels、project 和 patch source。统计输出必须保持
  raw-output-free，不写入 raw response 字段。

Plan:

1. 新增 `scripts/analyze_evp7_g5_statistics.py`，从 376-run ignored reviews
   和 tracked candidate labels 生成 raw-output-free 统计 JSON/Markdown；
2. 统计内容覆盖：
   - per-evidence-level Wilson CI；
   - candidate-level deterministic bootstrap CI；
   - E2/E4/E6 相对 E0 的 paired bootstrap delta 和 effect size；
   - per-project breakdown；
   - per-patch-source breakdown；
3. 将统计报告纳入 docs index、README 和 anonymous artifact required files；
4. 如有必要更新 paper table generator 或 IEEE draft，让论文入口能引用该
   统计 artifact；
5. 运行脚本、compile、paper readiness、artifact audit 和 local quality gate；
6. 本轮不调用 API、不扩 cohort、不修改 prompt、不跟踪 raw model outputs。

验收条件：

- `data/reviews/evp7_g5_376_statistical_analysis.json` 存在且不包含 raw
  response 字段；
- `docs/experiments/evp7_g5_376_statistical_analysis.md` 存在，包含 Wilson CI、
  bootstrap CI、paired delta、per-project 和 per-patch-source sections；
- README / docs index / artifact audit required files 指向新统计 artifact；
- quality gates 通过。

Execute:

- 已新增 `scripts/analyze_evp7_g5_statistics.py`：
  - 默认读取 ignored `outputs/evp7_g5_llm_376_full_001/reviews.jsonl`；
  - 只抽取 candidate id、evidence level、parse status、decision、project、
    patch source、label 和 cost 等结构字段；
  - 与 tracked `data/patches/evp7_candidates.jsonl` 连接 evaluator labels，
    只用于聚合统计；
  - 输出 raw-output-free
    `data/reviews/evp7_g5_376_statistical_analysis.json` 和
    `docs/experiments/evp7_g5_376_statistical_analysis.md`；
- 统计报告覆盖：
  - per-evidence-level Wilson 95% CI；
  - candidate-level bootstrap 95% CI，固定 seed = 9507，samples = 2000；
  - E2/E4/E6 相对 E0 的 paired bootstrap delta、effect size 和
    `P(delta > 0)`；
  - per-project breakdown；
  - per-patch-source breakdown；
- 已更新 `scripts/write_paper_tables.py`，让 generated tables 读取统计 JSON，
  并生成 `tab:evp7-statistical-intervals`；
- 已更新 `scripts/write_ieee_latex_draft.py`，在 EVP-7 结果叙述中明确
  Wilson / candidate-level paired bootstrap 的统计边界；
- 已重新生成 `docs/paper/generated_tables.md`、
  `docs/paper/generated_tables.tex` 和 `docs/paper/ieee_submission_draft.tex`；
- 已更新 README、docs index、anonymous artifact 文档、engineering notes；
- 已更新 anonymous artifact audit / package README 生成逻辑，将统计报告和脚本
  纳入 required files/snippets；
- 本轮未调用 API、未扩 cohort、未修改 prompt、未跟踪 raw model outputs。

Verify:

- `python -m compileall scripts\analyze_evp7_g5_statistics.py scripts\write_paper_tables.py scripts\write_ieee_latex_draft.py scripts\audit_anonymous_artifact.py scripts\prepare_anonymous_artifact.py`
  通过；
- `python scripts\analyze_evp7_g5_statistics.py` 通过，输出
  `raw_output_free=true`；
- raw marker 检查确认以下 tracked 文件均不包含 raw response 字段、prompt
  text 字段、本机路径或用户名：
  - `data/reviews/evp7_g5_376_statistical_analysis.json`；
  - `docs/experiments/evp7_g5_376_statistical_analysis.md`；
  - `docs/paper/generated_tables.md`；
  - `docs/paper/generated_tables.tex`；
  - `docs/paper/ieee_submission_draft.tex`；
- `python scripts\write_paper_tables.py --out-md docs\paper\generated_tables.md --out-tex docs\paper\generated_tables.tex`
  通过；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；
- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续运行后通过，生成 7 页 IEEE draft PDF；仅保留既有 underfull hbox /
  MiKTeX update 提示；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、
  `evp7_bounded_pilot_claim_ready=true`；
- `git diff --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮按计划补齐 frozen EVP-7 376-run 的统计分析 artifact；
- 当前论文表格和 IEEE draft 已从点估计推进到 Wilson / bootstrap / paired
  delta 的受限统计表达；
- 统计结果仍只支持 bounded EVP-7 pilot 观察，不改变 scale-generalized、
  deterministic-baseline superiority、E6 strictly > E4 或 external billing
  equivalence 的 unsupported claim 边界。

## 117. 2026-06-15 add paper claim-boundary traceability audit

Inspect:

- 当前工作区干净，本地 main ahead origin 21；
- 第 115/116 节已完成 EVP-7 evidence visibility curve 和统计区间 artifact；
- canonical roadmap 的剩余默认方向是 frozen 20-task cohort 的论文结果巩固、
  统计/图表和 claim-boundary 检查；
- 30-50 bugs 属于改变实验边界的后续选择，roadmap 明确不能由执行代理私自
  决定；
- 当前 `audit_paper_readiness.py` 能验证 run 质量、paper tables 和 claim
  readiness，但没有独立输出“每条 supported / unsupported claim 对应哪些证据、
  是否被论文 draft 覆盖”的 traceability artifact。

Plan:

1. 新增 `scripts/audit_paper_claim_boundary.py`，读取 EVP-7 376-run summary、
   quality audit、statistical analysis、paper generated tables、Markdown draft 和
   IEEE draft；
2. 输出 raw-output-free claim traceability JSON/Markdown，覆盖：
   - supported claims；
   - unsupported claims；
   - 每条 claim 的 evidence sources；
   - generated tables / Markdown draft / IEEE draft 中的覆盖状态；
   - IEEE draft 中必要边界 cue：bounded pilot、not scale-generalized、
     no deterministic-baseline superiority、no E6 strict superiority、no billing
     equivalence；
3. 将该审计纳入 `audit_paper_readiness.py` 的 required docs / readiness；
4. 更新 README、docs index、anonymous artifact required files 和 engineering
   notes；
5. 运行脚本、paper readiness、artifact audit、local quality gate；
6. 本轮不调用 API、不扩 cohort、不修改 prompt、不跟踪 raw model outputs。

验收条件：

- `data/reviews/evp7_g5_376_claim_traceability.json` 存在且 raw-output-free；
- `docs/experiments/evp7_g5_376_claim_traceability.md` 存在，列出 supported /
  unsupported claims 的 evidence sources 和 paper coverage；
- `audit_paper_readiness.py` 会检查 claim traceability artifact；
- README / docs index / artifact audit required files 指向新审计；
- quality gates 通过。

Execute:

- 已新增 `scripts/audit_paper_claim_boundary.py`：
  - 读取 tracked EVP-7 376-run summary、quality audit、statistical analysis、
    generated tables、Markdown draft 和 IEEE draft；
  - 生成 raw-output-free
    `data/reviews/evp7_g5_376_claim_traceability.json` 和
    `docs/experiments/evp7_g5_376_claim_traceability.md`；
  - 映射每条 supported / unsupported claim 到 evidence sources 和 paper
    coverage；
  - 检查 IEEE draft 中的必要边界 cue：bounded pilot、not scale-generalized、
    no deterministic-baseline superiority、no E6 strict superiority、no billing
    equivalence；
- 初次运行发现 Markdown paper draft 未明确覆盖 “raw-output-free tracked metrics
  from real DeepSeek verifier outputs” 这条 supported claim，已修正文稿而非放宽
  审计；
- 已更新 `scripts/audit_paper_readiness.py`，将 claim traceability audit 纳入
  EVP-7 bounded pilot claim readiness；
- 已更新 README、docs index、anonymous artifact 文档、engineering notes；
- 已更新 anonymous artifact required files/snippets 和 package README 生成逻辑；
- 本轮未调用 API、未扩 cohort、未修改 prompt、未跟踪 raw model outputs。

Verify:

- `python -m compileall scripts\audit_paper_claim_boundary.py scripts\audit_paper_readiness.py scripts\audit_anonymous_artifact.py scripts\prepare_anonymous_artifact.py`
  通过；
- `python scripts\audit_paper_claim_boundary.py` 通过，`passed=true`、
  `raw_output_free=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，EVP-7 readiness 中 `claim_traceability.exists=true`、
  `passed=true`、`raw_output_free=true`；
- raw/local marker 检查确认以下 tracked 文件不包含 raw response 字段、prompt
  text 字段、本机路径或用户名：
  - `data/reviews/evp7_g5_376_claim_traceability.json`；
  - `docs/experiments/evp7_g5_376_claim_traceability.md`；
  - `docs/paper/patch_verification_draft.md`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `git diff --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮按计划补齐 paper claim-boundary traceability audit；
- 当前 paper readiness 不再只依赖 run quality 和 generated tables，也会验证
  supported / unsupported claims 是否被当前论文 artifacts 覆盖；
- 该审计不改变 EVP-7 claim 边界：仍只支持 bounded pilot observations，不支持
  scale generality、deterministic-baseline superiority、E6 strictly > E4 或
  external billing equivalence。

## 118. 2026-06-15 add EVP-7 utility sensitivity analysis

Inspect:

- 当前工作区干净，本地 main ahead origin 22；
- 第 115/116/117 节已完成 evidence visibility curve、统计区间和 claim-boundary
  traceability；
- canonical roadmap 18.3 要求正式论文报告 utility 参数选择理由，并至少做一组
  敏感性分析；
- 当前 `evp7_g5_376_statistical_analysis` 已报告固定 utility formula
  `accept_correct - 5*accept_wrong - 0.25*escalate - reject_correct`，但还没有
  tracked sensitivity artifact；
- 该分析可从 ignored 376-run review records 的结构字段和 tracked candidate
  labels 生成 raw-output-free 聚合结果，不需要 API、prompt 或 cohort 改动。

Plan:

1. 新增 `scripts/analyze_evp7_utility_sensitivity.py`；
2. 在固定候选集合上计算 utility：
   `true_accept - lambda*false_accept - mu*escalated - nu*false_reject`；
3. 参数网格：
   - `lambda` false accept penalty: 1, 5, 10；
   - `mu` escalation penalty: 0.1, 0.25, 0.5；
   - `nu` false reject penalty: 0.5, 1, 2；
4. 输出 raw-output-free JSON/Markdown，记录每个 scenario 下 E0/E2/E4/E6 的
   utility、delta vs E0、best evidence level、ranking stability 和 sensitivity
   结论；
5. 将 sensitivity artifact 接入 generated tables / IEEE draft、README、
   docs index、anonymous artifact 和 paper readiness；
6. 运行 compile、analysis、paper generation、paper readiness、artifact audit 和
   local quality gate；
7. 本轮不调用 API、不扩 cohort、不修改 prompt、不跟踪 raw model outputs。

验收条件：

- `data/reviews/evp7_g5_376_utility_sensitivity.json` 存在且 raw-output-free；
- `docs/experiments/evp7_g5_376_utility_sensitivity.md` 存在，包含参数网格、
  per-scenario best level、ranking stability 和结论；
- generated tables / IEEE draft 至少引用一张 utility sensitivity summary；
- paper readiness 会检查 utility sensitivity artifact；
- README / docs index / artifact audit required files 指向新分析；
- quality gates 通过。

Execute:

- 已新增 `scripts/analyze_evp7_utility_sensitivity.py`：
  - 默认读取 ignored `outputs/evp7_g5_llm_376_full_001/reviews.jsonl`；
  - 与 tracked `data/patches/evp7_candidates.jsonl` 连接 labels，仅用于聚合；
  - 输出 raw-output-free
    `data/reviews/evp7_g5_376_utility_sensitivity.json` 和
    `docs/experiments/evp7_g5_376_utility_sensitivity.md`；
- 已实现 27 个 penalty scenarios：
  - false accept penalty `lambda`: 1, 5, 10；
  - escalation penalty `mu`: 0.1, 0.25, 0.5；
  - false reject penalty `nu`: 0.5, 1, 2；
- 当前 sensitivity 结果：
  - E6 在 27/27 scenarios 中为 best level；
  - dominant ranking = E6 > E4 > E0 > E2；
  - 由于当前 run 各 evidence level 的 observed false accepts 都为 0，
    false-accept penalty 不改变 ranking；
- 已更新 `scripts/write_paper_tables.py`，生成
  `tab:evp7-utility-sensitivity`；
- 已更新 `scripts/write_ieee_latex_draft.py` 和
  `docs/paper/ieee_submission_draft.tex`，在 EVP-7 结果中说明 utility
  sensitivity 的 penalty-grid 边界；
- 已更新 `docs/paper/patch_verification_draft.md`，让 Markdown paper draft 也
  覆盖 utility sensitivity；
- 已更新 `scripts/audit_paper_readiness.py`，将 utility sensitivity 纳入 EVP-7
  bounded pilot readiness；
- 已更新 README、docs index、anonymous artifact 文档、engineering notes、
  anonymous artifact audit 和 package README 生成逻辑；
- 本轮未调用 API、未扩 cohort、未修改 prompt、未跟踪 raw model outputs。

Verify:

- `python -m compileall scripts\analyze_evp7_utility_sensitivity.py scripts\write_paper_tables.py scripts\write_ieee_latex_draft.py scripts\audit_paper_readiness.py scripts\audit_anonymous_artifact.py scripts\prepare_anonymous_artifact.py`
  通过；
- `python scripts\analyze_evp7_utility_sensitivity.py` 通过，`scenario_count=27`；
- `python scripts\write_paper_tables.py --out-md docs\paper\generated_tables.md --out-tex docs\paper\generated_tables.tex`
  通过；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；
- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续运行后通过，生成 6 页 IEEE draft PDF；仅保留既有 underfull hbox /
  MiKTeX update 提示；
- `python scripts\audit_paper_claim_boundary.py` 通过，`passed=true`、
  `raw_output_free=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，EVP-7 readiness 中 `utility_sensitivity.exists=true`、
  `scenario_count=27`、`raw_output_free=true`、`dominant_best_level=E6`；
- raw/local marker 检查确认以下 tracked 文件不包含 raw response 字段、prompt
  text 字段、本机路径或用户名：
  - `data/reviews/evp7_g5_376_utility_sensitivity.json`；
  - `docs/experiments/evp7_g5_376_utility_sensitivity.md`；
  - `docs/paper/generated_tables.md`；
  - `docs/paper/generated_tables.tex`；
  - `docs/paper/ieee_submission_draft.tex`；
  - `docs/paper/patch_verification_draft.md`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `git diff --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮按计划补齐 EVP-7 utility sensitivity analysis；
- 当前 paper tables、Markdown draft、IEEE draft 和 paper readiness 都能显示
  utility 参数选择与 sensitivity 边界；
- 该结果仅强化 frozen 20-task pilot 内的 utility interpretation，不改变
  unsupported claim 边界。

## 119. 2026-06-15 align paper framing with evidence-visibility roadmap

Inspect:

- 当前工作区干净，本地 main ahead origin 23；
- `outputs/paper_readiness/latest.md` 显示 EVP-7 bounded pilot claim ready；
- canonical roadmap 明确当前论文题目和主线应使用
  `Evidence Visibility` / `Candidate Patches`，在真实 AI-generated patches
  未成为主体前不得过早写成 `AI-Generated Patches`；
- `docs/paper/patch_verification_outline.md` 仍使用旧标题
  `Verifiable Review of AI-Generated Patches`，并把主贡献写成
  tool-augmented verifier；
- `docs/paper/research_definition.md` 仍把最终贡献写成 tool-augmented
  verifier 正向路线，未反映当前 EVP-7 evidence-visibility bounded pilot；
- `docs/paper/patch_verification_draft.md` 和 IEEE generator 标题仍使用旧
  AI-generated patches 口径；
- 当前 readiness 只检查 outline 文件存在，尚未检查 paper framing 是否与
  roadmap 一致。

Plan:

1. 将 paper outline 改为 evidence-visibility / candidate-patch framing；
2. 将 research definition 的核心贡献和假设改为 evidence-level variation、
   prompt-only negative result、conditional tool-assisted result 和 bounded
   EVP-7 result；
3. 将 Markdown draft 与 IEEE generator 的标题改为 roadmap 推荐的
   `Evidence Visibility Matters: A Systematic Study of LLM-Based Verification
   for Candidate Patches`；
4. 在 `audit_paper_readiness.py` 中加入 paper-framing 检查，防止旧标题或
   tool-augmented-as-main-claim 文本重新进入 current readiness；
5. 同步 README / docs index / engineering notes；
6. 重新生成 IEEE draft，运行 paper readiness、artifact audit、local quality
   gate，并只提交本轮相关文件。

验收条件：

- paper outline / research definition / Markdown draft / IEEE draft 的标题和
  RQ framing 与 roadmap 一致；
- paper readiness 输出 paper framing check 且通过；
- stale old-title 检查不再命中 current paper artifacts；
- README / docs index / engineering notes 已同步；
- quality gates 通过。

Execute:

- 已重写 `docs/paper/patch_verification_outline.md`：
  - 工作标题改为 roadmap 推荐的
    `Evidence Visibility Matters: A Systematic Study of LLM-Based Verification
    for Candidate Patches`；
  - RQ 改为 LLM-only、prompt-only evidence discipline、E0-E6 evidence
    visibility、bounded claim boundary 和 tool-assisted result separation；
  - supported / non-claims 明确禁止 scale generality、deterministic-baseline
    superiority、E6 strict superiority、billing equivalence 和当前
    AI-generated-patches 标题化；
- 已更新 `docs/paper/research_definition.md`：
  - 将核心对象从 generated patch 改为 candidate patch；
  - 将目标贡献改为 evidence-visibility workflow；
  - 将假设改为 evidence visibility 对 safety/recall/escalation/utility 的影响；
  - 明确当前 EVP-7 只支持 bounded pilot observations；
- 已将 Markdown draft 标题改为 current roadmap title；
- 已更新 `scripts/write_ieee_latex_draft.py` 并重新生成
  `docs/paper/ieee_submission_draft.tex`；
- 已在 `scripts/audit_paper_readiness.py` 中加入 `paper_framing` 检查：
  - outline 必须使用当前标题；
  - outline 必须提到 evidence visibility 和 bounded EVP-7；
  - research definition 必须使用 evidence-visibility workflow 并保留 bounded
    current-claim wording；
  - Markdown draft 和 IEEE draft 必须使用当前标题；
  - current paper artifacts 不得继续使用旧
    `Verifiable Review of AI-Generated Patches` 标题；
- 已同步 README、docs index、anonymous artifact 文档和 engineering notes；
- 本轮未调用 API、未扩 cohort、未修改 prompt、未跟踪 raw model outputs。

Verify:

- `python -m compileall scripts\audit_paper_readiness.py scripts\write_ieee_latex_draft.py`
  通过；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`paper_framing.passed=true`、`current_result_claim_ready=true`、
  `evp7_bounded_pilot_claim_ready=true`；
- stale old-title 检查在 current paper artifacts / README / docs index /
  artifact docs 中未命中；
- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续运行通过，生成 6 页 IEEE draft PDF；仅保留既有 underfull hbox /
  MiKTeX update 提示；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`safe_to_package=true`、`file_count=280`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- 一次将 artifact prepare 与 audit 并行执行时，audit 读到正在写入的 ZIP 并报
  `BadZipFile`；已诊断为执行顺序问题，改为 prepare 完成后顺序 audit 并通过，
  engineering notes 已记录该约束；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮按计划修复 paper framing drift；
- paper readiness 现在会验证 high-level paper framing，不再只检查 outline /
  research definition 是否存在；
- 当前论文标题、outline、research definition、Markdown draft 和 IEEE draft
  已与 evidence-visibility / candidate-patches roadmap 对齐；
- 该修复只巩固 frozen 20-task EVP-7 paper readiness，不改变实验边界或 claim
  边界。

## 120. 2026-06-15 refresh active EVP-7 protocol current state

Inspect:

- 当前工作区干净，本地 main ahead origin 24；
- paper readiness、anonymous artifact audit 和 local quality gate 均通过；
- `docs/protocol/evidence_visibility_protocol.md` 是 active protocol 入口，
  但当前内容仍混有历史状态：
  - candidate manifest 写 86 promoted candidates；
  - G3 写 70 条/condition；
  - G4 写 280 E0/E2/E4/E6 records；
  - G5 主叙述仍是 248-packet historical run；
- 当前结构化 tracked summaries 已经是：
  - `data/tasks/evp7_manifest_summary.json`: 20 main tasks / 5 projects；
  - `data/patches/evp7_candidate_summary.json`: 94 candidates；
  - `data/evidence/evp7_evidence_packet_summary.json`: 376 packets, E0/E2/E4/E6
    each 94, leakage findings 0；
  - `data/baselines/evp7_tool_only_metrics.json`: 282 tool-only decisions,
    94 per condition；
  - `data/reviews/evp7_merge_gate_schema_dry_run_summary.json`: 376 schema
    dry-run records, 376 valid parses；
  - `data/reviews/evp7_g5_llm_376_full_summary.json`: 376 real LLM records,
    cost observability complete, bounded signal observed；
- paper readiness 当前只检查 protocol 文件存在，尚未检查 protocol 是否使用当前
  20/94/376 状态。

Plan:

1. 刷新 `docs/protocol/evidence_visibility_protocol.md` 的 frozen cohort、
   Phase A gate 和 post-A expansion 状态；
2. 保留 248-run 作为 historical checkpoint，但明确 current paper-facing G5
   result 是 376-run；
3. 在 `audit_paper_readiness.py` 中加入 protocol current-state check，验证
   protocol 文档包含 20 tasks / 94 candidates / 376 packets、282 tool-only
   decisions、376 schema dry-run records、376 real LLM records 和 bounded claim
   boundary；
4. 同步 README / docs index / artifact notes / engineering notes；
5. 运行 compile、paper readiness、artifact package + audit、local quality gate；
6. 本轮不调用 API、不扩 cohort、不修改 prompt、不跟踪 raw model outputs。

验收条件：

- protocol current-state text 与 tracked summaries 一致；
- paper readiness 输出 protocol current-state check 且通过；
- stale protocol-state 检查不再把 86 candidates、70/condition、280 records 或
  248-run 写成 current state；
- README / docs index / artifact notes / engineering notes 已同步；
- quality gates 通过。

Execute:

- 已刷新 `docs/protocol/evidence_visibility_protocol.md`：
  - 顶部说明改为 2026-06-15 controlled admissions 后的 20-task bounded
    pilot；
  - candidate manifest 状态改为 94 promoted candidates，20 correct reference
    patches，74 issue-not-fixed negatives，20 tasks / 5 projects；
  - G1/G2 保持通过；
  - G3 改为 apply-only、visible-tests、visible-tool-summary 各 94 条
    schema-valid decisions，共 282 tool-only decisions；
  - G4 改为 376 E0/E2/E4/E6 schema dry-run records，376 valid parses；
  - G5 改为当前 376-packet real DeepSeek official run：376/376 parse-valid
    non-mock records，E0/E2/E4/E6 各 94，E6 correct recall 0.35，
    Evidence Gain 14.25；
  - 248-packet run 被降级为 historical checkpoint，不再作为 current
    paper-facing G5 result；
  - Post-A expansion 改为 15-20 bug target 已达到并冻结，默认下一步不再是
    bug admission；
- 已更新 `scripts/audit_paper_readiness.py`：
  - 新增 `protocol_current_state` check；
  - current result / EVP-7 bounded pilot readiness 现在依赖 protocol current
    state 通过；
  - readiness Markdown 输出 protocol current-state checks；
- 已更新 anonymous artifact 审计：
  - required files 新增 active protocol、research definition、paper outline；
  - embedded ARTIFACT_README 必须包含当前 paper title 和 protocol 入口；
- 已同步 README、docs index、anonymous artifact 文档和 engineering notes；
- 本轮未调用 API、未扩 cohort、未修改 prompt、未跟踪 raw model outputs。

Verify:

- `python -m compileall scripts\audit_paper_readiness.py scripts\audit_anonymous_artifact.py scripts\prepare_anonymous_artifact.py`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`protocol_current_state.passed=true`、`current_result_claim_ready=true`、
  `evp7_bounded_pilot_claim_ready=true`；
- stale protocol-state 检查未命中：
  - `It contains 86 promoted candidates`；
  - `each produce 70 schema-valid decisions`；
  - `all 280 E0/E2/E4/E6`；
  - `G5 has a fresh 248-packet real DeepSeek official run`；
  - `outputs/evp7_g5_llm_248_full`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`safe_to_package=true`、`file_count=283`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮按计划修复 active EVP-7 protocol current-state drift；
- paper readiness 现在会验证 protocol 是否反映当前 20-task / 94-candidate /
  376-packet 状态；
- anonymous artifact 审计也要求携带 active protocol 和 current paper-framing
  入口；
- 该修复只巩固 frozen 20-task EVP-7 paper/artifact readiness，不改变实验边界
  或 claim 边界。

## 121. 2026-06-15 regenerate fig2 as EVP-7 evidence-level boundary

Inspect:

- 用户指出 `docs/figures/fig2_evidence_visibility` 与 PPT 中 E0/E2/E4/E6
  证据等级表信息不对等；
- 检查后确认旧 fig2 描述的是历史 `LLM-only` / prompt-only
  `evidence_first` / `tool_augmented_evidence` 三组 review condition；
- 当前中期报告和 paper-facing EVP-7 主线使用的是 E0/E2/E4/E6 evidence
  visibility level，因此旧 fig2 不应作为当前方法页图。

Plan:

1. 将 `scripts/generate_paper_figures.py` 中 fig2 改为当前 E0/E2/E4/E6
   证据等级边界矩阵；
2. 保留 evaluator truth labels 作为全部 prompt 隐藏、仅用于指标计算的评估端
   信息；
3. 同步 `docs/figures/README.md` 和 figure manifest purpose；
4. 重新生成 fig2 的 PDF/SVG/PNG，并人工检查新 PNG；
5. 不修改实验数据、prompt、API 或当前 claim 边界。

Execute:

- 已将 `fig2_evidence_visibility` 从旧三条件矩阵改为 EVP-7 E0/E2/E4/E6
  证据等级矩阵；
- 行包括 issue summary + patch diff、apply/static evidence、F2P/P2P test
  outcomes、tool/behavior summary 和 evaluator truth labels；
- evaluator truth labels 在 E0/E2/E4/E6 中均为 hidden，并在图下注明只用于指标
  计算；
- 已同步 `docs/figures/README.md` 和 `figure_manifest.json` 中 fig2 的 purpose。

Verify:

- `python scripts\generate_paper_figures.py` 通过，输出
  `figure_count=6`；
- 已人工检查 `docs/figures/fig2_evidence_visibility.png`：新图与当前 PPT
  证据等级表一致，不再混用旧 `LLM-only` / `Prompt-only Evidence-first` /
  `Tool-augmented Evidence` 三条件语义；
- 本轮未修改实验数据、prompt、API 调用或 claim 边界。

## 122. 2026-06-15 refresh EVP-7 protocol pilot report current state

Inspect:

- 当前工作区干净，本地 main ahead origin 25；
- active protocol 已刷新并通过 `protocol_current_state` readiness；
- `docs/experiments/evp7_protocol_pilot.md` 仍有多处历史状态：
  - Decision 段仍说 current tracked structural cohort 是 12 bugs / 5 projects；
  - Current Cohort Summary 写 18 completed tasks，但表格实际列出 20 tasks；
  - G5 real full-run status 仍把 248-run 写为主记录；
  - Current Next Step 仍说 latest real-LLM run remains scoped to previous
    12-task/62-candidate/248-packet cohort，并建议继续扩到 20 bugs 或运行 fresh
    376 G5；
- 当前事实已经是 20-task / 94-candidate / 376-packet structural cohort，且 fresh
  376-packet DeepSeek G5 full run 已完成并成为 paper-facing result；
- paper readiness 当前检查 active protocol，但尚未检查这个 protocol pilot report
  是否同步。

Plan:

1. 刷新 `docs/experiments/evp7_protocol_pilot.md` 的 Decision、Cohort Summary、
   G5 full-run status、quality audit 和 next-step 段；
2. 保留 248-run 为 historical checkpoint，不再作为 current latest run；
3. 在 `audit_paper_readiness.py` 中加入 protocol pilot report current-state
   check；
4. 将该 report 加入 anonymous artifact required files；
5. 同步 README / docs index / artifact notes / engineering notes；
6. 运行 compile、paper readiness、artifact package + audit、local quality gate；
7. 本轮不调用 API、不扩 cohort、不修改 prompt、不跟踪 raw model outputs。

验收条件：

- protocol pilot report 与 20/94/376 tracked summaries 一致；
- paper readiness 输出 protocol pilot report current-state check 且通过；
- stale report-state 检查不再把 12/62/248 或 fresh 376 run 当作 pending next
  step；
- README / docs index / artifact notes / engineering notes 已同步；
- quality gates 通过。

Execute:

- 已刷新 `docs/experiments/evp7_protocol_pilot.md`：
  - 2026-06-13 段落改为 historical checkpoint，不再把 12 bugs / 5 projects
    写作 current tracked cohort；
  - 新增 2026-06-15 update，记录 frozen 20 tasks / 5 projects / 94 candidates /
    376 E0/E2/E4/E6 evidence packets；
  - Current Cohort Summary 改为 20 completed project-level P2P-broad tasks；
  - G5 real full-run status 改为当前 376-record DeepSeek official API run：
    `outputs/evp7_g5_llm_376_full_001/`、376/376 parse-valid、0 invalid、
    cost observability 376/376、estimated total cost USD 0.327352058；
  - 质量审计入口改为 `docs/experiments/evp7_g5_376_full_quality_audit.md` 和
    `data/reviews/evp7_g5_376_full_quality_audit.json`；
  - 248-record run 明确保留为 previous 12-task / 62-candidate cohort 的
    historical checkpoint；
  - Current Next Step 改为继续巩固 frozen-cohort paper/artifact readiness，
    不再默认补 bug 或再跑 G5；
- 已更新 `scripts/audit_paper_readiness.py`：
  - 新增 `protocol_pilot_report` current-state check；
  - current result / EVP-7 bounded pilot readiness 现在依赖该 report 通过；
  - readiness Markdown 输出 protocol pilot report checks；
- 已更新 anonymous artifact 审计：
  - required files 新增 `docs/experiments/evp7_protocol_pilot.md`；
  - embedded ARTIFACT_README 同时指向 active protocol 和 protocol pilot report；
- 已同步 README、docs index、anonymous artifact 文档和 engineering notes；
- 本轮未调用 API、未扩 cohort、未修改 prompt、未跟踪 raw model outputs。

Verify:

- `python -m compileall scripts\audit_paper_readiness.py scripts\audit_anonymous_artifact.py scripts\prepare_anonymous_artifact.py`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`protocol_pilot_report.passed=true`、`protocol_current_state.passed=true`、
  `current_result_claim_ready=true`、`evp7_bounded_pilot_claim_ready=true`；
- stale protocol-pilot report 检查未命中：
  - `current tracked EVP-7 structural cohort is therefore 12`；
  - `contains 18 completed project-level`；
  - `outputs/evp7_g5_llm_248_full`；
  - `fresh G5 real-LLM pass for the current 376-packet`；
  - `latest real-LLM run remains scoped`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`safe_to_package=true`、`file_count=280`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮按计划修复 `evp7_protocol_pilot.md` current-state drift；
- paper readiness 现在同时验证 active protocol 和 protocol pilot report；
- anonymous artifact 审计也要求携带该 protocol pilot report；
- 该修复只巩固 frozen 20-task EVP-7 paper/artifact readiness，不改变实验边界
  或 claim 边界。

## 123. 2026-06-15 refresh final roadmap Phase A current state

Inspect:

- 当前工作区干净，`main...origin/main`；
- `outputs/local_quality_gate/latest.md` 显示 local quality gate 通过，计划阶段
  14/14 complete；
- `outputs/paper_readiness/latest.md` 显示 paper framing、active protocol 和
  protocol pilot report current-state checks 均通过；
- 但 canonical `docs/plans/final_paper_roadmap_zh.md` 的 Phase A 尾部仍用
  “当前通过”描述旧状态：
  - 46 candidates / 200 evidence packets；
  - E4/E6 50/50 complete；
  - 150 tool-only decisions；
  - 200 dry-run records；
  - 248 prompt manifest / four levels each 62；
- 同一段后面又写 376-run 是当前 paper-facing result，形成 roadmap 内部
  current-state drift。

Plan:

1. 将 `final_paper_roadmap_zh.md` 的 Phase A 状态段改成当前 20-task /
   94-candidate / 376-packet / 282-tool-only / 376-dry-run / 376-real-LLM
   口径；
2. 保留 248-run 和早期 10/11/12-task run 为 historical checkpoints；
3. 在 `audit_paper_readiness.py` 加入 final roadmap current-state check，防止
   canonical roadmap 再把旧 46/200/248 prompt 状态写成当前；
4. 同步 README / docs index / engineering notes；
5. 运行 compile、paper readiness、artifact package + audit、local quality gate；
6. 本轮不调用 API、不扩 cohort、不修改 prompt、不跟踪 raw model outputs。

验收条件：

- roadmap Phase A 当前状态与 tracked summaries 一致；
- paper readiness 输出 final roadmap current-state check 且通过；
- stale roadmap-state 检查不再命中旧 46/200/150/248 prompt 的 current wording；
- README / docs index / engineering notes 已同步；
- quality gates 通过。

Execute:

- 已刷新 `docs/plans/final_paper_roadmap_zh.md` 的 Phase A/G1-G5 当前状态：
  - 当前 candidate manifest = 94 candidates，20 correct reference，74
    issue-not-fixed negatives；
  - 当前 structural cohort = 20 tasks / 5 projects / 94 candidates；
  - 当前 evidence packets = 376 E0/E2/E4/E6 records，四层各 94；
  - 当前 tool-only baseline = 282 schema-valid decisions，三组各 94；
  - 当前 G4 dry-run = 376 records，invalid parse count 0；
  - 当前 G5 prompt manifest = 376 prompts，四层各 94；
  - 当前 paper-facing G5 run = 376/376 parse-valid DeepSeek V4 records，
    estimated total cost USD 0.327352058；
- 已将 10/11/12-task run 和 248-packet run 改为 historical checkpoints；
- 已在 `scripts/audit_paper_readiness.py` 新增 `final_roadmap` current-state
  check，并让 `current_result_claim_ready` 与 `evp7_bounded_pilot_claim_ready`
  依赖该 check；
- 已将 `docs/plans/final_paper_roadmap_zh.md` 加入 anonymous artifact required
  files，并在 embedded ARTIFACT_README 中列为 canonical roadmap；
- 已同步 README、docs index、anonymous artifact 文档和 engineering notes；
- 诊断并恢复了非本轮范围的 fig2/generate-figures diff，保留上一轮已确认的
  evaluator truth labels 图注；
- 本轮未调用 API、未扩 cohort、未修改 prompt、未跟踪 raw model outputs。

Verify:

- `python -m compileall scripts\audit_paper_readiness.py scripts\audit_anonymous_artifact.py scripts\prepare_anonymous_artifact.py`
  通过；
- stale roadmap-state 检查在 current roadmap/protocol/README/INDEX 入口未命中：
  - `共 46 条候选`；
  - `共 200 条`；
  - `50/50 complete`；
  - `150 条 schema-valid`；
  - `248 条 prompts`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`final_roadmap.passed=true`、`protocol_pilot_report.passed=true`、
  `protocol_current_state.passed=true`、`current_result_claim_ready=true`、
  `evp7_bounded_pilot_claim_ready=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`safe_to_package=true`、`file_count=280`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮按计划修复 canonical final-paper roadmap Phase A current-state drift；
- paper readiness 现在同时验证 paper framing、active protocol、protocol pilot
  report 和 final roadmap；
- anonymous artifact 审计也要求携带 canonical roadmap；
- 该修复只巩固 frozen 20-task EVP-7 paper/artifact readiness，不改变实验边界
  或 claim 边界。

## 124. 2026-06-15 compact fig2 evidence boundary layout

Inspect:

- 当前工作区有未提交图形改动：
  - `scripts/generate_paper_figures.py`；
  - `docs/figures/fig2_evidence_visibility.{pdf,png,svg}`；
- diff 显示改动只删除 `fig2_evidence_visibility` 底部长说明文字，并收紧底部
  留白；
- E0/E2/E4/E6 矩阵本体仍保留，`Evaluator truth labels` 行仍在四个 evidence
  levels 下全部显示为 hidden；
- 该改动不涉及实验数据、prompt、API、metrics 或 claim 边界。

Plan:

1. 保留 fig2 compact layout，前提是视觉检查确认矩阵、行列标签和 hidden
   boundary 清晰；
2. 运行 `scripts/generate_paper_figures.py` 重新生成 figures，确认脚本可复现；
3. 同步 `docs/figures/README.md` 和 engineering notes，记录 fig2 compact
   layout 仍必须保留 evaluator truth labels hidden 行；
4. 运行 paper readiness、artifact package + audit、local quality gate；
5. 本轮不调用 API、不扩 cohort、不修改 prompt、不改变 claim 边界。

验收条件：

- fig2 PNG 视觉检查通过；
- `scripts/generate_paper_figures.py` 可复现当前图；
- README/figure docs/engineering notes/current plan 已同步；
- paper readiness、anonymous artifact audit、local quality gate 通过；
- 只提交本轮 fig2 layout 与文档同步相关文件。

Execute:

- 已保留 `fig2_evidence_visibility` 的 compact layout：
  - 删除底部长说明文字；
  - 收紧底部留白；
  - 保持 E0/E2/E4/E6 矩阵本体；
  - 保持 `Evaluator truth labels` 行，且四个 evidence levels 均为 hidden；
- 已运行 `python scripts\generate_paper_figures.py` 重新生成 PDF/SVG/PNG；
- 已人工检查 `docs/figures/fig2_evidence_visibility.png`，矩阵、行列标签和
  hidden evaluator boundary 清晰；
- 已同步 `docs/figures/README.md`、`docs/INDEX.md` 和
  `docs/experience/engineering_notes.md`；
- 本轮未调用 API、未扩 cohort、未修改 prompt、未修改 metrics 或 claim 边界。

Verify:

- `python scripts\generate_paper_figures.py` 通过，输出 `figure_count=6`；
- `python -m compileall scripts\generate_paper_figures.py` 通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`evp7_bounded_pilot_claim_ready=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`safe_to_package=true`、`file_count=280`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮只压缩 fig2 版式，未改变 EVP-7 evidence boundary 语义；
- evaluator truth labels 的 hidden boundary 仍在矩阵中显式可见；
- 该修复服务于 paper/PPT figure readability，不改变实验边界或论文 claim
  边界。

## 125. 2026-06-15 IEEE fig2 caption submission audit

Inspect:

- 当前工作区干净，`main...origin/main`；
- `docs/figures/fig2_evidence_visibility.*` 已是 compact E0/E2/E4/E6
  evidence-level boundary 图；
- `outputs/paper_compile/ieee_submission_draft.pdf` 早于最新 fig2 生成时间，
  需要重新编译；
- `scripts/write_ieee_latex_draft.py` 仍把 fig2 caption 描述为旧的
  review-condition / tool-augmented condition 边界；
- 这会导致重新生成的 IEEE 草稿与当前 fig2 语义不一致，但不涉及实验数据、
  prompt、API、metrics 或 claim 边界。

Plan:

1. 修复 IEEE 草稿生成器中的 fig2 caption，使其明确描述 EVP-7
   E0/E2/E4/E6 evidence visibility levels；
2. 在 paper readiness audit 中加入旧 fig2 caption 阻断，防止 generated
   `.tex` 或生成器再次漂移；
3. 重新生成 `docs/paper/ieee_submission_draft.tex` 并重新编译 PDF；
4. 同步 README / docs index / engineering notes；
5. 运行 paper readiness、anonymous artifact audit、local quality gate；
6. 本轮不调用 API、不扩 cohort、不修改 prompt、不改变 claim 边界。

验收条件：

- IEEE draft 和生成器都不再包含旧 fig2 condition caption；
- readiness gate 能检查 fig2 caption 语义；
- PDF 重新编译成功；
- paper readiness、anonymous artifact audit、local quality gate 通过；
- 只提交本轮 caption/readiness/docs 相关文件。

Execute:

- 已修复 `scripts/write_ieee_latex_draft.py` 中 fig2 caption，使其描述
  EVP-7 E0/E2/E4/E6 evidence visibility levels；
- 已重新生成 `docs/paper/ieee_submission_draft.tex`；
- 已在 `scripts/audit_paper_readiness.py` 中加入 fig2 caption drift 检查：
  - IEEE draft 必须包含 EVP-7 evidence visibility levels；
  - caption 必须声明 evaluator truth labels remain hidden at all levels；
  - generated `.tex` 和生成器都不得继续使用旧 condition caption wording；
- 已同步 README、docs index 和 engineering notes；
- 本轮未调用 API、未扩 cohort、未修改 prompt、未修改 metrics 或 claim 边界。

Diagnose / Repair:

- 初版 readiness check 直接匹配原始 `.tex` 字符串，遇到 LaTeX caption 换行
  后误报 `ieee_fig2_caption_keeps_truth_labels_hidden=false`；
- 问题类型为执行链路审计 bug，不是论文内容或实验设计问题；
- 已将 caption 正向检查改为基于 whitespace-normalized text，重新运行后
  paper framing check 通过。

Verify:

- `python -m compileall scripts\write_ieee_latex_draft.py scripts\audit_paper_readiness.py`
  通过；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`paper_framing.passed=true`、`current_result_claim_ready=true`、
  `evp7_bounded_pilot_claim_ready=true`；
- `pdflatex` 连续两遍编译 `docs\paper\ieee_submission_draft.tex` 成功，输出
  `outputs\paper_compile\ieee_submission_draft.pdf` 共 6 页；
- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf -` 确认 PDF 中
  fig2 caption 为 `EVP-7 evidence visibility levels`，且包含
  `Evaluator truth labels remain hidden at all levels`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`safe_to_package=true`、`file_count=280`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮完成 IEEE fig2 caption submission audit；
- fig2 的生成器 caption、生成草稿和编译 PDF 现在都与 compact E0/E2/E4/E6
  evidence boundary 一致；
- readiness gate 已覆盖该 drift 类型，后续 paper refresh 不应重新引入旧
  condition caption；
- 该修复只巩固 frozen 20-task / 94-candidate / 376-packet EVP-7 bounded pilot
  paper readiness，不改变实验边界或 claim 边界。

## 2026-06-15 PPT 决策到指标流程图

Inspect:

- 用户需要一张流程图，解释模型在每个证据层级下如何输出 accept / reject /
  escalate，以及这些判断如何转化为 FAR、接收精确率、正确召回率、
  升级复核率和证据增益；
- 当前可复现图件由 `scripts/generate_paper_figures.py` 生成到
  `docs/figures/`，已有 fig1-fig6 和 manifest；
- 本轮只补充解释性方法图，不改变 EVP-7 数据、指标定义、实验结果、
  prompt 或 API 调用边界。

Plan:

1. 在可复现图件脚本中新增 `fig7_decision_metric_flow`；
2. 图中展示输入证据层级 E0/E2/E4/E6、LLM 审查器、三类输出、
   隐藏真实标签对齐，以及每层级指标公式；
3. 同步 figure manifest、figures README、README 和 docs index；
4. 重新生成 PDF/SVG/PNG 并人工检查 PNG 版面。

Execute:

- 已新增 `docs/figures/fig7_decision_metric_flow.{pdf,svg,png}`；
- 已将 figure manifest 更新为 7 张图；
- 已在 `docs/figures/README.md`、README 和 `docs/INDEX.md` 中补充 fig7
  或 decision-to-metric flow 入口；
- 已将 fig7 文案改为英文，并恢复全局 matplotlib 字体为 `DejaVu Sans`，
  避免为单张图引入中文字体选择导致 fig1-fig6 无关重渲染；
- 本轮未调用 API、未修改实验数据、未改变结果表格或 claim boundary。

Diagnose / Repair:

- 初版 fig7 为中文标签，并在 `ensure_style()` 中按系统字体切换到
  `Microsoft YaHei`；该全局字体改动会导致 fig1-fig6 的 PDF/SVG/PNG 出现
  与内容无关的渲染漂移；
- 问题类型为图件生成链路可复现性问题，不是实验结果或论文 claim 问题；
- 已改为英文 fig7，并保持全局字体稳定，使本轮 diff 收窄到 fig7 新增、
  figure manifest、生成脚本和文档入口。

Verify:

- `python -m compileall scripts\generate_paper_figures.py` 通过；
- `python scripts\generate_paper_figures.py` 通过，输出
  `figure_count = 7`；
- 已人工检查 `docs/figures/fig7_decision_metric_flow.png`：英文标题、
  证据层级、accept/reject/escalate 三类输出、隐藏标签对齐和底部指标公式
  均可读，未发现明显重叠；
- `git diff --stat` 确认 fig1-fig6 不再显示修改，本轮图件 diff 已收窄；
- 该图适合放在 PPT 公式页之前或实验结果表格之前，用来解释“模型判断
  如何变成表格指标”。

## 2026-06-15 Nature-guided IEEE draft consistency audit

Inspect:

- 已安装并加载 `nature-writing` / `nature-reviewer` 的必要规则：
  - 先写一行核心论点；
  - 每个主要 claim 必须有证据和边界；
  - 审稿视角优先检查 originality / significance / technical soundness /
    nonspecialist readability；
  - 不发明实验、引用、结果或 novelty；
- 当前 IEEE 草稿已包含 376-record EVP-7 G5 result、统计区间、utility
  sensitivity、claim boundary 和 fig2/fig6；
- 主要风险不是数据错误，而是结构排序：abstract 和 RQs 仍把旧
  30-candidate 三条件 pilot 放在中心，EVP-7 376-run 像追加结果；
- 按最终 roadmap，当前 paper-facing 主线应是 frozen
  20-task / 94-candidate / 376-packet EVP-7 evidence visibility pilot，旧
  30-candidate pilot 应作为前置动机、prompt-only negative result 和
  tool-assisted workflow boundary；
- 本轮不调用 API、不扩 cohort、不修改 prompt、不改变统计或 claim boundary。

Plan:

1. 修改 `scripts/write_ieee_latex_draft.py`，让 abstract、RQ 和 conclusion
   foreground EVP-7 bounded evidence-visibility result；
2. 将旧 30-candidate API/tool-augmented sections 明确写成 first-pilot
   diagnostic/redesign evidence，避免读者误解为当前主实验；
3. 重新生成 `docs/paper/ieee_submission_draft.tex` 并编译 PDF；
4. 用 `pdftotext` 和 readiness gate 抽查 unsupported claims 未被重新引入；
5. 同步 README / docs index / engineering notes（如新增论文结构经验）；
6. 运行 paper readiness、anonymous artifact audit、local quality gate。

验收条件：

- Abstract/RQs/Conclusion 的主线从旧 first pilot 转为 EVP-7 evidence
  visibility；
- 仍明确保留 unsupported claims：不做 scale-generalized、LLM over
  tool-only、E6 strict superiority、billing equivalence；
- 所有文本改动来自生成器，生成的 IEEE `.tex` 可复现；
- LaTeX 编译、paper readiness、artifact audit、local quality gate 通过。

Execute:

- 已按 `nature-writing` / `nature-reviewer` 规则执行 claim-evidence audit：
  - 核心论点改为 frozen EVP-7 evidence-visibility pilot；
  - 旧 30-candidate API pilots 保留为 diagnostic design evidence；
  - 不新增实验、引用、novelty 或 scale-generalized claim；
- 已修改 `scripts/write_ieee_latex_draft.py`：
  - abstract foreground EVP-7 20-task / 94-candidate / 376-packet bounded
    result；
  - RQs 改为 evidence-poor risk、prompt-only cost、E0/E2/E4/E6 evidence
    effect、baseline claim boundary、supported/unsupported claims；
  - first-pilot sections 改名为 `First-Pilot API Diagnostic` 和
    `First-Pilot Tool-Augmented Redesign`；
  - EVP-7 result 段改为 paper-facing frozen result；
  - conclusion foreground EVP-7 result，并将旧 first pilot 写成解释边界的
    diagnostic evidence；
- 已在 `scripts/audit_paper_readiness.py` 增加 narrative-center gate：
  - IEEE draft 和生成器必须包含 `We construct a frozen EVP-7 pilot`；
  - 必须把 `Earlier 30-candidate API pilots` 表述为 design boundary；
  - 不得回退到旧 abstract 的 `The first pilot contains...` /
    `We then run an EVP-7...` 结构；
- 已同步 README、docs index 和 engineering notes；
- 本轮未调用 API、未扩 cohort、未修改 prompt、未改统计结果或 claim
  boundary。

Verify:

- `python -m compileall scripts\write_ieee_latex_draft.py scripts\audit_paper_readiness.py`
  通过；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`paper_framing.passed=true`、`ieee_abstract_foregrounds_frozen_evp7=true`、
  `generator_abstract_foregrounds_frozen_evp7=true`、
  `ieee_abstract_not_centered_on_old_first_pilot=true`、
  `current_result_claim_ready=true`、`evp7_bounded_pilot_claim_ready=true`；
- `pdflatex` 连续两遍编译 `docs\paper\ieee_submission_draft.tex` 成功，输出
  `outputs\paper_compile\ieee_submission_draft.pdf` 共 6 页；
- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf -` 抽查确认：
  - PDF 包含 `Earlier 30-candidate API pilots motivate the design boundary`；
  - PDF 保留 `not scale-generalized`、deterministic-baseline superiority、
    E6 strict superiority 和 billing equivalence 边界；
  - 旧 `The first pilot contains 30...` / `We then run an EVP-7...` wording
    未命中；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`safe_to_package=true`、`file_count=283`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮完成 Nature-guided IEEE draft consistency audit；
- IEEE abstract/RQs/conclusion 现在以 frozen EVP-7 bounded result 为主线；
- 旧 first-pilot 结果仍保留，但只作为 prompt-only negative result、
  tool-assisted boundary 和设计动机；
- readiness gate 已覆盖该 narrative-center drift，后续刷新不应重新把旧
  first pilot 放回 paper-facing 主线。

## 2026-06-15 Nature-reviewer pre-submission assessment

Inspect:

- 当前工作区干净，`main` 本地领先 `origin/main` 3 个提交；
- `outputs/paper_readiness/latest.md` 显示 current result claim ready、
  EVP-7 bounded pilot claim ready 均为 yes；
- 唯一 blocker 是历史 prompt-only positive claim 的
  `stop_or_redesign` gate，不阻塞 EVP-7 bounded pilot；
- 已加载 `nature-reviewer` 规则和本地 Nature editorial criteria：
  评估轴限定为 originality、scientific importance、interdisciplinary
  readership、technical soundness 和 nonspecialist readability；
- 本轮输入范围限定为当前 IEEE submission draft、生成表格和 figure
  manifest；不调用 API、不扩 cohort、不修改 prompt、不改变统计。

Plan:

1. 新增一份 reviewer-style 预投稿评估文档，包含 3 份 reviewer reports
   和 1 份 cross-review synthesis；
2. 明确该评估是 Nature-style reviewer lens，不是编辑决定，也不是作者
   rebuttal；
3. 将主要风险集中到技术证据链、novelty/significance framing、跨领域
   可读性和 unsupported claims；
4. 同步 README、docs index 和 engineering notes；
5. 运行文档结构检查、paper readiness、local quality gate 和 diff check。

验收条件：

- 预审报告完整包含 Review setup、Reviewer 1/2/3、Cross-review
  synthesis、Risk / unsupported claims；
- 三位 reviewer 只按评估重点不同，不引入身份、单位、专业角色或隐藏
  知识；
- 所有 substantive comments 可追溯到当前草稿、表格、figure manifest
  或本地 Nature reviewer criteria；
- 不新增实验结果、引用、结论或投稿归属判断。

Execute:

- 已新增 `docs/paper/nature_reviewer_presubmission_report.md`；
- 报告采用 `nature-reviewer` 默认结构：
  - Review setup；
  - Reviewer 1：technical soundness / tool-only attribution 重点；
  - Reviewer 2：originality / significance / prior-work positioning 重点；
  - Reviewer 3：interdisciplinary readability / reader workflow 重点；
  - Cross-review synthesis；
  - Risk / unsupported claims；
- 报告将当前主要论文风险收敛为四项：
  1. EVP-7 LLM-plus-evidence 相对 deterministic tool-only 的归因还不够清楚；
  2. 需要少量 EVP-7 qualitative decision cases 解释 accept/reject/escalate
     机制；
  3. related work 需要说明 evidence visibility 与普通 prompt engineering、
     tool-use prompting、test-only validation 的区别；
  4. 读者路径应先解释 evidence packet -> model decision -> hidden-label
     join -> aggregate metric，再展开 first-pilot chronology；
- 已同步 README、`docs/INDEX.md` 和 `docs/experience/engineering_notes.md`；
- 本轮未调用 API、未扩 cohort、未新增实验 claim、未修改 prompt 或统计结果。

Verify:

- 预审报告结构检查通过，包含所有必需 section；
- 收窄后的 reviewer-boundary 检查通过，未发现 reviewer 身份发明或最终
  editorial decision assertion；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，current result claim ready 和 EVP-7 bounded pilot claim ready 仍为
  true；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git diff --check` 通过。

结论：

- 本轮完成 Nature-style pre-submission reviewer assessment；
- 下一步写作优先级不应是扩实验或重跑 G5，而是按预审报告处理
  tool-only attribution、EVP-7 qualitative cases、related-work positioning 和
  reader-flow simplification。

## 2026-06-15 EVP-7 deterministic tool-only attribution

Inspect:

- 当前分支本地领先 `origin/main` 4 个提交，工作区在本轮开始时干净；
- Nature-style pre-submission report 将 tool-only attribution 列为最高优先级；
- 现有 tracked `data/baselines/evp7_tool_only_decisions.jsonl` 覆盖
  94 candidates x 3 tool-only conditions；
- ignored real LLM run `outputs/evp7_g5_llm_376_full_001/reviews.jsonl`
  包含 candidate_id、evidence_level 和 parsed decision；
- 本轮只做 raw-output-free 结构分析，不读取或写入 raw response text 到
  tracked artifacts，不调用 API、不扩 cohort、不改 prompt。

Plan:

1. 新增 raw-output-free attribution 脚本，比较 E4 LLM vs
   `tool_only_visible_tests` 和 E6 LLM vs
   `tool_only_visible_tool_summary`；
2. 输出 tracked JSON/Markdown 分析报告；
3. 将 attribution 表接入 `write_paper_tables.py` 和 IEEE draft generator；
4. 更新 readiness gate，要求 attribution JSON/Markdown 存在、raw-output-free，
   且 IEEE draft 包含 attribution boundary；
5. 同步 README、docs index、Markdown draft、engineering notes；
6. 重新生成 tables、IEEE draft、paper readiness、PDF 和 local quality gate。

验收条件：

- E4/E6 attribution 数字来自 candidate-level matched decisions；
- 输出不包含 raw response text 或 prompt text；
- 论文只表述 bounded safety/recall tradeoff，不声称 LLM 优于 deterministic
  visible evidence；
- paper readiness 和 local quality gate 通过。

Execute:

- 新增 `scripts/analyze_evp7_tool_attribution.py`；
- 生成：
  - `data/reviews/evp7_g5_376_tool_attribution.json`；
  - `docs/experiments/evp7_g5_376_tool_attribution.md`；
- 分析结果：
  - E4：LLM 与 visible-tests tool-only baseline agreement = 72/94，
    recovered tool false accepts = 4/4，downgraded tool true accepts = 18/19；
  - E6：LLM 与 visible-tool-summary baseline agreement = 76/94，
    LLM accepts outside tool accepts = 0，recovered tool false accepts = 4/4，
    downgraded tool true accepts = 12/19；
- 已将 attribution 表接入 generated tables 和 IEEE draft；
- 已在 IEEE EVP-7 section 增加 attribution boundary 段落；
- 已更新 `scripts/audit_paper_readiness.py`，将 attribution 表和 boundary 纳入
  paper framing / EVP-7 readiness；
- 已同步 README、`docs/INDEX.md`、`docs/paper/patch_verification_draft.md` 和
  `docs/experience/engineering_notes.md`。

Verify:

- `python -m compileall scripts\analyze_evp7_tool_attribution.py scripts\write_paper_tables.py scripts\write_ieee_latex_draft.py scripts\audit_paper_readiness.py`
  通过；
- `python scripts\analyze_evp7_tool_attribution.py` 通过，
  `raw_output_free=true`；
- `python scripts\write_paper_tables.py --out-md docs\paper\generated_tables.md --out-tex docs\paper\generated_tables.tex`
  通过；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`evp7_bounded_pilot_claim_ready=true`，
  且 `tool_attribution.raw_output_free=true`；
- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续两遍通过，输出 `outputs\paper_compile\ieee_submission_draft.pdf`；
- `python scripts\audit_paper_claim_boundary.py` 通过，`passed=true`、
  `raw_output_free=true`；
- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf -` 检查确认
  PDF 包含 deterministic tool-only attribution、76/94 agreement、4 个
  tool-only false accepts 和 bounded safety/recall tradeoff；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git diff --check` 通过，仅有既有 LF/CRLF 工作区提示。

结论：

- 本轮完成预审报告第一项技术风险：EVP-7 LLM+evidence 相对 deterministic
  tool-only 的归因边界；
- 结论必须写成：LLM 在 E6 恢复 tool-only false accepts，但以降级一部分
  tool-only true accepts 为代价；这支持安全/召回权衡，不支持 LLM
  superiority claim；
- 下一步可以进入 EVP-7 qualitative decision cases 或 related-work positioning，
  不需要继续跑 API。

## 2026-06-15 EVP-7 qualitative decision cases

Inspect:

- 当前分支本地领先 `origin/main` 5 个提交，工作区在本轮开始时干净；
- Nature-style pre-submission report 的第二个硬缺口是 qualitative EVP-7
  decision evidence；
- 上一轮已完成 deterministic tool-only attribution，下一步不应扩实验、
  重跑 G5 或调用 API；
- ignored `outputs/evp7_g5_llm_376_full_001/reviews.jsonl` 含
  `raw_response_text`，因此 tracked qualitative artifacts 只能写结构化
  decision flow 和摘要级 interpretation，不能写 raw response/prompt text；
- qualitative case 必须区分 model-visible sequence 与 evaluator-only
  interpretation，避免把 hidden label 混进 reviewer-facing 叙述。

Plan:

1. 新增 `scripts/analyze_evp7_qualitative_cases.py`，从现有 376 条
   parse-valid review records、94 candidates 和 tool-only decisions 中抽取
   6 个固定代表性 cases；
2. 输出 raw-output-free tracked JSON/Markdown：
   - `data/reviews/evp7_g5_376_qualitative_cases.json`；
   - `docs/experiments/evp7_g5_376_qualitative_cases.md`；
3. 覆盖 case roles：
   - evidence enables accept；
   - tool-only false accept recovered by LLM；
   - correct patch downgraded by LLM；
   - tool-summary-only late accept；
   - no-op rejected after evidence；
   - partial patch stable reject；
4. 将 qualitative case boundary 接入 IEEE draft generator 和 Markdown draft；
5. 更新 `audit_paper_readiness.py`，要求 qualitative cases 存在、
   raw-output-free、case_count = 6，且论文/generator 明确包含 qualitative
   boundary；
6. 同步 README、`docs/INDEX.md` 和 engineering notes；
7. 运行最小验证、paper readiness、PDF compile、claim boundary、local quality
   gate、diff check 后提交。

验收条件：

- 不调用 API，不新增 cohort，不改 prompt；
- qualitative 输出不包含 `raw_response_text`、`prompt_text` 或原始响应；
- reviewer-facing sequence 不包含 evaluator-only truth label；
- evaluator-only interpretation 单独标注，只用于解释 false accept / recall
  tradeoff；
- paper readiness 和 local quality gate 通过。

Execute:

- 新增 `scripts/analyze_evp7_qualitative_cases.py`；
- 生成：
  - `data/reviews/evp7_g5_376_qualitative_cases.json`；
  - `docs/experiments/evp7_g5_376_qualitative_cases.md`；
- 固定 6 个代表性 cases：
  - QC1 `evidence_enabled_accept`；
  - QC2 `tool_false_accept_recovered_by_llm`；
  - QC3 `correct_patch_downgraded_by_llm`；
  - QC4 `tool_summary_late_accept`；
  - QC5 `no_op_rejected_after_evidence`；
  - QC6 `partial_patch_rejected_after_evidence`；
- 已将 qualitative case audit 段落接入 IEEE draft generator 和 Markdown draft；
- 已更新 `scripts/audit_paper_readiness.py`，要求 qualitative JSON/Markdown
  存在、case_count = 6、raw-output-free，且 reviewer-facing truth label 已隔离；
- 已同步 README、`docs/INDEX.md` 和 `docs/experience/engineering_notes.md`。

Verify:

- `python -m compileall scripts\analyze_evp7_qualitative_cases.py` 通过；
- `python scripts\analyze_evp7_qualitative_cases.py` 通过，`case_count=6`、
  `raw_output_free=true`、`reviewer_facing_truth_label_separated=true`；
- `python -m compileall scripts\analyze_evp7_qualitative_cases.py scripts\write_ieee_latex_draft.py scripts\audit_paper_readiness.py`
  通过；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`evp7_bounded_pilot_claim_ready=true`，qualitative cases gate 通过；
- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续两遍通过，输出 6 页 PDF；仅有 underfull hbox 和 MiKTeX update 提示；
- `python scripts\audit_paper_claim_boundary.py` 通过，`passed=true`、
  `raw_output_free=true`；
- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf -` 检查确认
  PDF 包含 qualitative case audit、model-visible decision sequence、
  evaluator-only interpretation 和 not additional scale evidence；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 本轮完成预审报告第二项技术风险：EVP-7 qualitative decision cases；
- 这些 cases 只能解释决策机制和安全/召回权衡，不能扩大样本量或支撑
  scale-generalized claim；
- 下一步应进入 related-work positioning，而不是继续跑 API。

## 2026-06-15 related-work positioning

Inspect:

- 当前分支本地领先 `origin/main` 6 个提交，工作区在本轮开始时干净；
- Nature-style reviewer report 的第三个硬缺口是 prior-work positioning：
  需要说明 evidence visibility 与普通 prompt engineering、tool-use prompting、
  benchmark pass rate 和 test-only patch validation 的区别；
- 当前 IEEE draft generator 没有 Related Work section，也没有
  `thebibliography`；
- Nature/CNS 严格引用范围不适合支撑软件工程相关工作；本轮按
  `nature-citation` 的保守原则使用已验证的领域主文献，不造 Nature/CNS
  不相关引用；
- 本轮不调用实验 API、不改 cohort、不改 prompt。

Plan:

1. 新增 related-work positioning 文档，记录引用范围、分段 claim、支撑来源和
   风险边界；
2. 新增 reference-manager-ready RIS 文件；
3. 在 IEEE draft generator 中加入简短 `Related Work and Positioning`
   section 和 `thebibliography`；
4. 同步 Markdown draft、outline、README、INDEX 和 engineering notes；
5. 更新 paper readiness，要求 related-work section、关键 citation keys、
   Evidence Gain descriptive boundary 和 bibliography 存在；
6. 重新生成 IEEE draft、运行 paper readiness、LaTeX、claim-boundary、local
   quality gate、diff check 后提交。

验收条件：

- related work 按机制分组，不做 citation dump；
- 每个引用只支撑其实际覆盖的 claim；
- 明确 Evidence Gain 是 descriptive pilot metric，不是 proposed universal
  benchmark score；
- PDF 编译通过且引用无未定义；
- paper readiness 和 local quality gate 通过。

Execute:

- 新增 `docs/experiments/evp7_related_work_positioning.md`，记录：
  - strict Nature/CNS citation scope 不适合本软件工程 claim；
  - benchmark / test-suite validation / LLM-agent repair 三类相关工作；
  - segment-to-reference map；
  - Evidence Gain 的 descriptive pilot metric 边界；
- 新增 `docs/references/evp7_related_work_references.ris`；
- 在 `scripts/write_ieee_latex_draft.py` 中加入
  `Related Work and Positioning` section 和 `thebibliography`；
- 同步 `docs/paper/patch_verification_draft.md`、
  `docs/paper/patch_verification_outline.md`、
  `docs/paper/research_definition.md`；
- 更新 `scripts/audit_paper_readiness.py`，要求：
  - IEEE/generator/Markdown draft 有 related-work section；
  - core citation keys 存在；
  - bibliography 存在；
  - Evidence Gain 是 descriptive pilot metric；
  - positioning doc 和 RIS export 存在；
- 已同步 README、`docs/INDEX.md` 和 engineering notes。

Verify:

- `python -m compileall scripts\write_ieee_latex_draft.py scripts\audit_paper_readiness.py`
  通过；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，related-work checks 全部为 yes；
- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续两遍通过，第二遍无 undefined citation/reference 警告；
- `python scripts\audit_paper_claim_boundary.py` 通过，`passed=true`、
  `raw_output_free=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf -` 检查确认
  PDF 正文包含 Real-bug benchmarks、Defects4J、BugsInPy、SWE-bench、
  Evidence Gain descriptive pilot metric 和 not a proposed universal benchmark
  score。

结论：

- 本轮完成预审报告第三项技术风险：related-work positioning；
- 论文现在明确区别 evidence visibility 与 benchmark pass rate、test-only
  validation、LLM repair 和 agentic software-engineering task solving；
- 下一步应处理 reader-flow simplification，而不是继续补实验或扩 cohort。

## 2026-06-15 reader-flow simplification

Inspect:

- 当前分支本地领先 `origin/main` 7 个提交，工作区在本轮开始时干净；
- Nature-style reviewer report 的第四个硬缺口是 reader workflow：
  当前正文要求读者先学习 first pilot、tool-augmented redesign、EVP-7、G5、
  statistics、utility 和 artifact controls，主线不够早；
- 当前 `docs/figures/fig7_decision_metric_flow.pdf` 已存在，但 IEEE draft
  尚未引用；
- 本轮只调整论文叙事和 readiness guard，不调用 API、不改 cohort、不改
  experimental metrics。

Plan:

1. 在 IEEE draft generator 的 Related Work 后加入
   `How to Read the Experiment` section；
2. 用五步路径解释 candidate patch -> visible evidence packet -> model
   decision -> hidden label join -> aggregate metric；
3. 引用 `fig7_decision_metric_flow.pdf`，让图文对应；
4. 将 first-pilot 路线明确写成 diagnostic motivation，避免和 EVP-7 主结果
   抢主线；
5. 同步 Markdown draft、outline、README、INDEX 和 engineering notes；
6. 更新 paper readiness，要求 IEEE/generator/Markdown draft 都包含 reader-flow
   bridge 和 fig7 reference；
7. 重新生成 IEEE draft、运行 paper readiness、LaTeX、claim-boundary、local
   quality gate、diff check 后提交。

验收条件：

- 早期正文必须出现五步 reader path；
- PDF 必须包含 fig7 / decision-to-metric flow 的正文或 caption；
- first-pilot 仍作为 diagnostic design evidence，不升级为主结果；
- paper readiness 和 local quality gate 通过。

Execute:

- 已在 IEEE generator 的 Related Work 后加入 `How to Read the Experiment`
  section；
- 已把 reader path 固定为 candidate patch -> model-visible evidence packet
  -> accept/reject/escalate decision -> hidden label join -> aggregate metrics；
- 已在 IEEE draft 中引用 `docs/figures/fig7_decision_metric_flow.pdf`，
  并加入 decision-to-metric flow caption；
- 已同步 Markdown draft、outline、research definition、README、INDEX 和
  engineering notes；
- 已扩展 `scripts/audit_paper_readiness.py`，要求 generator、IEEE draft 和
  Markdown draft 都包含 reader-flow bridge，并检查 fig7 reference 与
  first-pilot diagnostic framing。

Verify:

- `python -m compileall scripts\write_ieee_latex_draft.py scripts\audit_paper_readiness.py`
  通过；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，reader-flow、fig7 reference 和 first-pilot diagnostic checks 全部为 true；
- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续两遍通过，第二遍无 undefined reference；
- `python scripts\audit_paper_claim_boundary.py` 通过，`passed=true`、
  `raw_output_free=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf -` 检查确认
  PDF 包含 candidate patch、model-visible evidence packet、hidden label
  join、decision-to-metric flow、diagnostic design evidence 和 frozen EVP-7。

结论：

- 本轮完成预审报告第四项技术风险：reader-flow simplification；
- 论文读者现在可在进入 first-pilot / tool-augmented / EVP-7 细节前先看到
  统一的实验单位、决策链和指标链；
- 下一步应做 final manuscript polish / consistency pass，而不是继续补实验。

## 2026-06-15 final manuscript polish / consistency pass

Inspect:

- 当前分支本地领先 `origin/main` 8 个提交，工作区在本轮开始时干净；
- 使用 `nature-polishing`，轴线为 `paper_type=research`、
  `section=abstract/intro/results/discussion/conclusion`、`language=en`、
  `journal=generic`；
- 术语 ledger：
  - canonical title:
    `Evidence Visibility Matters: A Systematic Study of LLM-Based Verification for Candidate Patches`；
  - canonical protocol/cohort: `EVP-7`；
  - canonical metric: `Evidence Gain`；
  - canonical claim scope: `bounded evidence-level variation` /
    `bounded evidence-visibility pilot result`；
  - unsupported claims: no scale-generalized claims, no deterministic-baseline
    superiority claim, no strict E6-over-E4 claim, no external-billing claim；
- 初查发现正文和 Markdown draft 中仍有几处容易误读的措辞：
  `establishes` 用在结论/当前 artifact 上过强，unsupported-claim 串联句过长，
  `evidence gain` 大小写不一致。

Plan:

1. 只做论文文字和 guard 的最小一致性修订，不新增实验、不改 metrics、不调用 API；
2. 将结论中的强断言改为 bounded observation / reports / provides；
3. 将 unsupported claims 从长串句改为可读的分号列表；
4. 统一正文中的 `Evidence Gain` 大小写；
5. 同步 Markdown draft、README/INDEX、engineering notes 和 readiness guard；
6. 重新生成 IEEE draft、编译 PDF、运行 readiness、claim-boundary、local gate、
   PDF 文本核验和 diff check 后提交。

验收条件：

- IEEE draft、generator、Markdown draft 都不得把 EVP-7 写成 scale-generalized
  或 deterministic-baseline-superiority 结论；
- 结论段必须保留 bounded single-model/cohort scope；
- `Evidence Gain` 术语大小写一致；
- readiness 和 local quality gate 通过。

Execute:

- 已将 IEEE generator 结论中的 `establishes` 改为 `reports`，避免把
  bounded single-model pilot 写成更强的结论；
- 已将 EVP-7 result 段中的小写 `evidence gain` 改为 canonical
  `Evidence Gain`；
- 已将 unsupported claims 从一条长串审计文本改为四个显式 rejected
  interpretations；
- 已同步 Markdown draft、paper table generator、generated tables、README、
  INDEX 和 engineering notes；
- 已在 `scripts/audit_paper_readiness.py` 中增加 final-polish checks：
  bounded conclusion、unsupported-claim formatting、`Evidence Gain` title case。

Verify:

- `python scripts\write_paper_tables.py` 通过并刷新
  `docs/paper/generated_tables.md` 与 `docs/paper/generated_tables.tex`；
- `python -m compileall scripts\write_ieee_latex_draft.py scripts\write_paper_tables.py scripts\audit_paper_readiness.py`
  通过；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，新增 final-polish checks 全部为 true；
- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续两遍通过，输出仍为 7 页；
- `python scripts\audit_paper_claim_boundary.py` 通过，`passed=true`、
  `raw_output_free=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf -` 检查确认
  PDF 结论包含 bounded single-model scope、四项 rejected interpretations、
  `Evidence Gain 7.0000` 和 `Evidence Gain 14.2500`。

结论：

- 本轮完成 final manuscript polish / consistency pass；
- 论文当前主线为 frozen EVP-7 bounded evidence-visibility pilot，不再通过
  结论措辞暗示 scale-generalized、deterministic-baseline-superiority 或
  deployment-ready claim；
- 下一步应做 final artifact packaging / submission checklist，而不是继续扩实验。

## 2026-06-15 final artifact packaging / submission checklist

Inspect:

- 当前分支本地领先 `origin/main` 9 个提交，工作区在本轮开始时干净；
- `scripts/prepare_anonymous_artifact.py --dry-run` 通过，当前可打包文件数为
  290，`safe_to_package=true`；
- 当前 ignored artifact ZIP 已存在，但生成时间早于最新论文一致性修订，需要刷新；
- 发现一个 artifact guard 缺口：当前 IEEE draft 已引用
  `docs/figures/fig7_decision_metric_flow.pdf`，但
  `scripts/audit_anonymous_artifact.py` 的 required file list 尚未要求 fig7；
- 本轮只处理 artifact/submission checklist 与打包审计，不新增实验、不调用 API、
  不提交 `artifacts/`。

Plan:

1. 新增最终提交清单文档，列出 paper、figures、artifact、claim-boundary、
   reproducibility、excluded files 和 known non-blockers；
2. 更新 anonymous artifact 文档和 embedded artifact README，使 fig7 与
   final submission checklist 成为显式入口；
3. 更新 artifact audit required files/snippets，要求 fig7 和 checklist 存在；
4. 刷新匿名 artifact ZIP，并运行 artifact audit；
5. 运行 paper readiness、local quality gate、diff check 后只提交 tracked
   文档和脚本更新，不提交 ignored ZIP/audit outputs。

验收条件：

- artifact audit 必须通过并确认 fig7、submission checklist、paper draft、
  protocol、claim-boundary summaries 都在 ZIP 中；
- local quality gate 必须通过；
- `git status --short` 不得出现 tracked `artifacts/` 文件；
- 提交清单必须明确 old prompt-only gate blocker 是 known non-blocker，而不是
  当前 EVP-7 bounded claim blocker。

Execute:

- 新增 `docs/artifact/submission_checklist.md`，记录当前 paper package、
  七张 required PDF figures、claim-boundary evidence、rebuild/audit commands、
  artifact commands、exclusion boundary 和 ready-to-submit criteria；
- 更新 `docs/artifact/anonymous_artifact.md`，把 final submission checklist
  和 fig7 纳入当前 artifact audit 说明；
- 更新 `scripts/prepare_anonymous_artifact.py` 的 embedded
  `ARTIFACT_README.md`，在 ZIP 内说明 checklist、七张 figures 和
  `fig7_decision_metric_flow.pdf`；
- 更新 `scripts/audit_anonymous_artifact.py`，将
  `docs/artifact/submission_checklist.md` 与
  `docs/figures/fig7_decision_metric_flow.pdf` 加入 required files/snippets；
- 同步 README、docs/INDEX 和 engineering notes。

Verify:

- `python -m compileall scripts\prepare_anonymous_artifact.py scripts\audit_anonymous_artifact.py`
  通过；
- `python scripts\prepare_anonymous_artifact.py --dry-run --manifest-out artifacts\research95_anonymous_artifact_manifest_dry_run.json`
  通过，`safe_to_package=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，刷新 ignored ZIP，packaged file count 为 291；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`、`missing_required=[]`、`missing_readme_snippets=[]`、
  `forbidden_entries=[]`；
- ZIP 直接核验确认包含 `docs/artifact/submission_checklist.md`、
  `docs/figures/fig7_decision_metric_flow.pdf`、
  `docs/paper/ieee_submission_draft.tex` 和
  `docs/experiments/evp7_g5_376_claim_traceability.md`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，当前 result claim ready；
- `python scripts\audit_paper_claim_boundary.py` 通过，`passed=true`、
  `raw_output_free=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git status --short --branch --ignored=matching artifacts ...` 显示
  `artifacts/` 仍为 ignored，不是 tracked 待提交文件。

结论：

- 本轮完成 final artifact packaging / submission checklist；
- 匿名 ZIP 已在本地刷新并通过 audit，但 `artifacts/` 仍按规则不提交；
- 下一步应做 final pre-push / release handoff audit；如果仍不 push，则只需
  提供本地提交和明确的推送边界。

## 2026-06-15 final pre-push / release handoff audit

Inspect:

- 当前分支本地领先 `origin/main` 10 个提交，工作区在本轮开始时干净；
- 当前 remote 为 `https://github.com/gaoming-a/research95.git`；
- 旧 `outputs/handoff/git_sync_packet.md` 显示 `sync ready: yes`，但
  `git status --short --branch` 明确为 `ahead 10`；
- 问题类型：Git handoff 审计口径 bug。它只检查当前 repo 有 remote，
  没有检查 upstream ahead/behind，因此会把未 push 状态误报为已同步；
- 本轮不执行 `git push`，只修本地 handoff/sync audit、刷新 ignored
  handoff 报告并提交 tracked 修复。

Plan:

1. 修复 `scripts/write_git_sync_packet.py`，使用
   `git status --short --branch` 解析 upstream、ahead、behind、dirty；
2. 将 `sync_ready` 定义为 repo + remote + clean + upstream + ahead=0 + behind=0；
3. 更新 `scripts/audit_git_sync_packet.py`，要求 packet 暴露 ahead/behind，
   且 ahead 时必须需要 human decision；
4. 刷新 git sync packet、pre-API handoff、local quality gate；
5. 同步 README、INDEX、engineering notes 和计划；
6. 提交本轮 tracked 修复，不 push。

验收条件：

- 当前 ahead 10 时，git sync packet 必须显示 `sync_ready=false`、
  `requires_human_decision=true`；
- audit_git_sync_packet 必须通过；
- pre-API handoff 必须刷新并通过本地命令；
- local quality gate 必须通过；
- 工作区不得提交 ignored handoff/output/artifact 文件。

Execute:

- 已修复 `scripts/write_git_sync_packet.py`：
  - 使用 `git status --short --branch`；
  - 解析 `current_upstream`、`current_ahead`、`current_behind`、
    `current_status_clean`；
  - 将 `sync_ready` 定义为 repo + remote + clean + upstream + ahead=0 +
    behind=0；
  - 将 required decision 改为 push/defer 当前分支，而不是旧的 init/remote
    决策；
  - 将安全命令模板改为 inspect ignored paths、检查 `origin/main..HEAD`、
    最后 `git push origin main`；
- 已更新 `scripts/audit_git_sync_packet.py`：
  - 要求 ahead/behind 字段存在；
  - ahead 时必须 `requires_human_decision=true`；
  - `sync_ready=true` 时必须 ahead/behind 都为 0；
  - push 必须仍是最后一步；
- 已同步 README、docs/INDEX 和 engineering notes；
- 已刷新 ignored handoff outputs，不提交 `outputs/`。

Verify:

- `python -m compileall scripts\write_git_sync_packet.py scripts\audit_git_sync_packet.py`
  通过；
- `python scripts\write_git_sync_packet.py --out-json outputs\handoff\git_sync_packet.json --out-md outputs\handoff\git_sync_packet.md`
  通过，当前本地 ahead 状态下输出 `requires_human_decision=true`；
- `python scripts\audit_git_sync_packet.py --out-json outputs\git_sync_packet_audit\latest.json --out-md outputs\git_sync_packet_audit\latest.md`
  通过，`passed=true`；
- 刷新后的 git sync packet 明确记录：
  `current_upstream=origin/main`、`current_ahead=10`、
  `current_behind=0`、`sync_ready=false`、
  `requires_human_decision=true`；
- `python scripts\write_pre_api_handoff.py --out-json outputs\handoff\pre_api_handoff.json --out-md outputs\handoff\pre_api_handoff.md`
  通过，`commands_passed=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git status --short --branch --ignored=matching outputs artifacts` 显示
  `outputs/` 和 `artifacts/` 仍为 ignored，不是 tracked 待提交文件。

结论：

- 本轮完成 final pre-push / release handoff audit；
- 当前本地 release handoff 可用，但 GitHub sync 明确未完成：本地 main 仍
  ahead origin/main；
- 按此前“不 push”的边界，本轮只提交 handoff/audit 修复；真正远端同步需要
  用户显式允许后执行 `git push origin main`。

## 2026-06-16 plan/project file organization

Inspect:

- 当前 Git 状态为 `main...origin/main`，本地与远端已同步；
- `docs/plans/current_plan_zh.md` 是严格逐轮执行日志，但文件已接近 0.5 MB，
  不适合作为唯一入口；
- `docs/plans/final_paper_roadmap_zh.md` 仍是 canonical research route；
- `README.md` 和 `docs/INDEX.md` 信息完整，但缺少一个短的“当前状态与文件地图”
  入口；
- 本轮整理范围仅限非破坏性文档组织：不移动、不删除、不归档旧计划文件。

Plan:

1. 新增短入口 `docs/plans/current_project_state_zh.md`；
2. 在短入口中整理当前 Git 同步状态、bounded EVP-7 claim、继续实验前决策门、
   计划文档分工、项目文件地图、脚本入口和禁止误用；
3. 更新 README 的 Current Execution Target 和 Current Status；
4. 更新 `docs/INDEX.md` 的 Active Plan；
5. 运行最小检查后提交并同步。

验收条件：

- 新入口不替代 `current_plan_zh.md` 和 `final_paper_roadmap_zh.md`；
- README 和 INDEX 都指向新入口；
- 不删除或移动历史计划文件；
- Git 状态和当前 claim boundary 表述与最新同步状态一致。

Execute:

- 新增 `docs/plans/current_project_state_zh.md`，作为当前短入口和文件地图；
- 文件中整理了：
  - 当前 Git 同步状态；
  - 当前 bounded EVP-7 研究状态；
  - 继续实验前的三类决策门；
  - 计划文档分工；
  - 项目文件地图；
  - 脚本入口地图；
  - 禁止误用清单；
- 更新 README，使 Current Execution Target 和 Current Status 指向新入口；
- 更新 `docs/INDEX.md` 的 Active Plan，说明新入口的定位；
- 更新 `docs/experience/engineering_notes.md`，记录长计划文件整理经验；
- 移除短入口中的固定 latest commit hash，避免每次提交后状态入口立即过期；
- 未移动、删除或归档任何历史计划文件。

Verify:

- `Test-Path docs\plans\current_project_state_zh.md` 返回 true；
- `Select-String -Path README.md,docs\INDEX.md -Pattern 'current_project_state_zh.md'`
  确认 README 和 INDEX 都引用了新入口；
- `Select-String -Path README.md,docs\plans\current_project_state_zh.md -Pattern '5555260|最新已同步提交|latest pushed commit'`
  用于发现固定提交号会漂移，已改为只记录 `main` 与 `origin/main` 同步；
- `git diff --check` 通过，仅有 Windows 换行提示；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

结论：

- 当前计划和项目文件已完成非破坏性整理；
- 后续继续实验时应先读 `docs/plans/current_project_state_zh.md`，再决定进入
  EVP-7 cohort expansion、cross-model replication 或 new verifier design；
- 若要进一步“归档/删除/移动”旧计划文件，需要单独确认具体文件清单。

## 2026-06-16 EVP-7 cohort expansion gate

Inspect:

- 用户目标恢复为“完成扩 EVP-7 cohort”；
- 当前短入口 `docs/plans/current_project_state_zh.md` 明确要求扩 cohort 前先做
  no-API expansion plan 和 dry-run/preflight；
- canonical roadmap 记录当前主 cohort 已冻结为 20 tasks / 5 projects / 94
  candidates / 376 evidence packets，继续扩量会进入 30-50 bugs 的硕士论文
  稳健版方向，不能盲目补 bug；
- `docs/experiments/evp7_expansion_readiness.md` 和
  `data/tasks/evp7_expansion_readiness.json` 当前显示：metadata-promising pool
  没有 fresh-project promising candidates，controlled probe 没有
  `f2p_established_p2p_not_attempted` 任务；
- 本轮不调用真实 API，不修改 prompt，不把 dry-run/mock/schema 记录写成 real
  verifier result。

Plan:

1. 刷新 EVP-7 expansion readiness summary，确认当前候选池、probe lane 和
   main cohort 状态；
2. 审计是否已有任务满足“F2P established 但 P2P 未尝试”或可直接进入
   project-level P2P/candidate revalidation 的前置条件；
3. 若没有可直接 admission 的任务，记录为 expansion gate blocked by candidate
   availability，而不是伪造 cohort expansion；
4. 同步 README / INDEX / engineering notes / 当前状态入口中的下一步边界；
5. 运行最小 no-API quality gate，提交并同步本轮文档或脚本更新。

验收条件:

- 不新增 `p2p_broad_main` 任务，除非对应任务已有 F2P、project-level
  P2P-broad、candidate construction、candidate revalidation 的全链路证据；
- readiness 输出必须明确 main task count、project distribution、候选池状态和
  next execution boundary；
- 若 expansion 暂不可执行，必须给出可验证原因和下一步需要用户决策的边界；
- 工作区不得提交 `outputs/`、`artifacts/`、`.env` 或 local config。

Execute:

- 运行 `python scripts\summarize_evp7_expansion_readiness.py` 刷新 tracked
  readiness summary；
- 审计 registry、candidate manifest 和 evidence packet manifest 后发现
  `bugsinpy_httpie_5` 在 `data/patches/evp7_candidates.jsonl` 中有 6 条候选，
  但 `data/cohorts/task_cohort_registry.json` 缺少 `collection_summary`，
  导致 registry-derived candidate count 为 88；
- 根据 tracked candidate/P2P evidence 补齐 `bugsinpy_httpie_5`
  `collection_summary`：6 candidates，1 个
  `correct_under_f2p_and_p2p_broad`，5 个 `incorrect_issue_not_fixed`；
- 更新 `scripts/summarize_evp7_expansion_readiness.py`，使 readiness 显式报告
  `current_main_candidate_count_from_registry`；
- 重新运行 `scripts\build_evp7_protocol_manifests.py`，刷新 task manifest 和
  `data/tasks/evp7_manifest_summary.json`；
- 同步更新 README、`docs/INDEX.md`、`docs/plans/current_project_state_zh.md`、
  `docs/experiments/evp7_protocol_pilot.md` 和 engineering notes。

Verify:

- `python -m compileall scripts\summarize_evp7_expansion_readiness.py scripts\build_evp7_protocol_manifests.py`
  通过；
- JSON 解析检查覆盖 `data/cohorts/task_cohort_registry.json`、
  `data/tasks/evp7_manifest_summary.json`、
  `data/tasks/evp7_expansion_readiness.json`，通过；
- 数量一致性检查通过：
  - registry main task count = 20；
  - registry candidate count = 94；
  - `data/patches/evp7_candidates.jsonl` records = 94；
  - `data/evidence/evp7_evidence_packets.jsonl` records = 376；
  - readiness `current_main_candidate_count_from_registry` = 94；
  - readiness `f2p_established_p2p_not_attempted` = `[]`；
  - readiness fresh-project promising candidates = 0；
- 当前入口文档中不再出现旧的 `88-candidate` / `registry-known lower bound: 88`
  表述；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git diff --check` 通过，仅有 Windows 换行提示。

结论:

- 本轮完成 EVP-7 cohort expansion 的 no-API gate 修复和审计；
- 当前 cohort 仍为 20 tasks / 94 candidates / 376 packets，没有新增 main
  task；
- 没有任务满足直接 admission 前置条件：
  `f2p_established_p2p_not_attempted=[]`，fresh-project promising candidates =
  0；
- 因此不能安全地把 cohort 扩成 21+ tasks。继续扩 EVP-7 cohort 需要先明确新的
  受控 probe 边界或新数据源边界。

## 2026-06-16 EVP-7 fresh-project metadata screen repair

Inspect:

- 上轮 expansion gate 证明当前没有可直接 admission 的任务；
- 继续检查 broader BugsInPy candidate pool 后发现 `thefuck` 项目有 32 个
  pytest 任务，但全部被 `network_reference_in_metadata` 排除；
- 抽查 `bugsinpy_thefuck_1` 发现网络 URL 只出现在 requirements 的
  `-e git+https://github.com/nvbn/thefuck@...#egg=thefuck` 自项目 editable
  requirement 中，目标 `bug.info` 和 `run_test.sh` 不含网络引用；
- 这不是 admission 证据，但说明当前 metadata screen 过保守，把潜在 fresh
  project probe lane 误归为 blocker。

Plan:

1. 修复 `scripts/screen_bugsinpy_candidate_pool.py`：把 self editable Git
   requirement 记录为 metadata note，而不是 `network_reference_in_metadata`
   blocker；
2. 刷新 candidate pool screening 和 EVP-7 expansion readiness；
3. 验证 readiness 中 fresh-project promising candidates 不再错误为 0；
4. 更新 README / INDEX / current state / engineering notes，说明下一步应是
   `thefuck` 受控 checkout/F2P probe，而不是直接 admission；
5. 不安装依赖、不 checkout、不调用 API、不新增 main cohort task。

验收条件:

- `thefuck` 任务可作为 fresh-project metadata-promising probe lane 出现在
  readiness 中；
- 当前 main cohort 仍保持 20 tasks / 94 candidates / 376 packets；
- `p2p_broad_main` 不新增任务；
- GitHub push 若网络仍失败，必须明确记录本地 ahead 状态。

Execute:

- 修复 `scripts/screen_bugsinpy_candidate_pool.py`：
  - self editable Git requirement 通过 `metadata_notes` 记录为
    `self_editable_git_requirement`；
  - 只有非 self editable requirement、run command 或 test file 中的 URL 才继续
    触发 `network_reference_in_metadata`；
- 重新运行 broader BugsInPy candidate-pool screen，tracked markdown 刷新为：
  - total BugsInPy tasks = 501；
  - already registered tasks = 47；
  - new candidate tasks = 454；
  - promising metadata-level candidates = 202；
  - metadata blocker counts 不再包含 self editable Git requirement 造成的
    `network_reference_in_metadata`；
- 重新运行 `scripts\summarize_evp7_expansion_readiness.py`；
- readiness 现在显示 fresh-project promising candidates = 32，top probe lane
  包含 `bugsinpy_thefuck_1`，状态为 `metadata_only_not_admitted`；
- 更新 README、`docs/INDEX.md`、`docs/plans/current_project_state_zh.md` 和
  engineering notes，说明下一步是 `thefuck` bounded checkout/F2P probe，而不是
  admission。

Verify:

- `python -m compileall scripts\screen_bugsinpy_candidate_pool.py scripts\summarize_evp7_expansion_readiness.py`
  通过；
- `data/tasks/evp7_expansion_readiness.json` 检查通过：
  - `current_main_task_count=20`；
  - `current_main_candidate_count_from_registry=94`；
  - `fresh_project_promising_candidates=32`；
  - top probe lanes 包含 `bugsinpy_thefuck_1`；
- 当前未运行 checkout、未安装依赖、未新增 main cohort task。

结论:

- 本轮把“没有 fresh-project candidates”的错误边界推进为“存在 32 个
  fresh-project metadata candidates，首选 `bugsinpy_thefuck_1` 做受控探针”；
- 这仍不是 cohort admission。完成扩 EVP-7 cohort 的下一步是对
  `bugsinpy_thefuck_1` 执行 bounded checkout/F2P probe，并在通过后再进入
  project-level P2P-broad 和 candidate revalidation。

## 2026-06-16 bugsinpy_thefuck_1 bounded checkout/F2P probe

Inspect:

- `bugsinpy_thefuck_1` 当前是 fresh-project metadata-promising lane；
- BugsInPy metadata：
  - project = `thefuck`；
  - bug id = 1；
  - buggy commit = `2ced7a7f33ae0bec3ffc7a43ce95330bdf6cfcb9`；
  - fixed commit = `444908ce1c17767ef4aaf9e0b4950497914f7f63`；
  - target test = `pytest tests/rules/test_pip_unknown_command.py::test_get_new_command`；
- 本轮只做 checkout/F2P probe，不安装依赖、不修改 checkout、不构造候选、不
  admission。

Plan:

1. 在 ignored `outputs/evp7_thefuck1_f2p_probe/` 下创建 buggy/fixed checkout；
2. 顺序运行 BugsInPy checkout，禁止并行 checkout 同一任务；
3. 在 buggy 和 fixed checkout 中分别运行目标 pytest；
4. 根据结果更新 controlled probe status 和实验文档：
   - buggy fail + fixed pass 才能进入下一阶段 project-level P2P；
   - import/dependency/collection/checkout blocker 则记录为 blocked，不 admission；
5. 运行最小验证，提交并同步 tracked 记录。

验收条件:

- 不提交 checkout、raw test logs 或 `outputs/`；
- 如果 F2P 未建立，不得新增 `p2p_broad_main`；
- 如果 F2P 建立，也只记录 `f2p_established_p2p_not_attempted`，不直接
  admission。

Execute:

- 使用 WSL bash 路径运行 BugsInPy checkout；
- 在 ignored `outputs/evp7_thefuck1_f2p_probe/` 下顺序尝试：
  - buggy checkout：`bugsinpy-checkout -p thefuck -i 1 -v 0`；
  - fixed checkout：`bugsinpy-checkout -p thefuck -i 1 -v 1`；
- 两次 checkout 均在 `git clone https://github.com/nvbn/thefuck` 阶段因
  GitHub 443 连接不可达失败；
- BugsInPy checkout 脚本在 clone 失败后继续执行并最终返回 success，因此必须
  以目录/marker 文件验证 checkout 是否真实完成；
- 未运行目标 pytest，未安装依赖，未修改 checkout，未构造 candidates，未
  admission；
- 追加 `data/tasks/evp7_controlled_probe_results.json` 记录：
  `bugsinpy_thefuck_1` = `f2p_blocked_checkout_network`；
- 刷新 `docs/experiments/evp7_expansion_readiness.md` 和
  `data/tasks/evp7_expansion_readiness.json`。

Verify:

- checkout 目录检查：
  - `outputs/evp7_thefuck1_f2p_probe/buggy/thefuck` 不存在；
  - `outputs/evp7_thefuck1_f2p_probe/fixed/thefuck` 不存在；
- `git ls-remote https://github.com/nvbn/thefuck.git` 也因 GitHub 443 不可达失败；
- readiness 现在记录：
  - `f2p_blocked_checkout_network = 1`；
  - recorded tasks 包含 `bugsinpy_thefuck_1`；
  - top probe lane 中 `bugsinpy_thefuck_1` 状态为
    `f2p_blocked_checkout_network`；
  - main cohort 仍为 20 tasks / 94 candidates。

Diagnose:

- 问题类型：checkout/network/tooling blocker；
- 不是 F2P 设计问题、不是 candidate label 问题、不是 verifier/API 问题；
- 当前不能进入 P2P 或 candidate construction。

Repair:

- 记录 controlled probe result，避免后续把 metadata-only `thefuck_1` 当成未尝试；
- 更新 readiness decision：下一步需要 GitHub checkout 路径可达或 audited local
  mirror，之后才能重试 F2P。
- 清理本轮 ignored raw checkout 过程目录
  `outputs/evp7_thefuck1_f2p_probe/`；保留 tracked JSON/Markdown 结论作为审计
  记录，不保留 failed checkout logs 作为仓库证据。

结论:

- `bugsinpy_thefuck_1` 是有效 fresh-project metadata lane，但本轮 checkout
  network blocked；
- EVP-7 cohort 仍未扩到 21 tasks；
- 完成扩 cohort 的下一步外部条件是：GitHub clone 可达或提供经过审计的本地
  `thefuck` mirror。

## 2026-06-16 bugsinpy_thefuck_1 checkout reachability retry

Inspect:

- 工作区当前干净且已同步到 `origin/main`；
- readiness 仍显示 main cohort = 20 tasks / 94 candidates；
- `bugsinpy_thefuck_1` 已记录为 `f2p_blocked_checkout_network`；
- 本轮目标不是 admission，而是检查上轮外部条件是否解除。

Plan:

1. 先运行 `git ls-remote https://github.com/nvbn/thefuck.git`；
2. 如果 GitHub checkout 路径仍不可达，只记录连续 blocker，不创建 checkout；
3. 如果可达，再创建 ignored `outputs/evp7_thefuck1_f2p_probe_retry/`，顺序运行
   buggy/fixed checkout；
4. 只有两个 checkout 均通过目录/marker 验证后，才运行目标 pytest F2P；
5. 根据结果更新 tracked readiness/plan/experience，提交并同步。

验收条件:

- 不调用 API；
- 不安装依赖，除非 F2P checkout 已真实完成且计划另行记录；
- 不修改 checkout、不构造 candidates、不 admission；
- 不提交 `outputs/` raw logs。

Execute:

- `git ls-remote https://github.com/nvbn/thefuck.git HEAD` 在 Windows 和 WSL
  路径均成功，说明上轮 checkout 网络 blocker 已解除；
- 顺序 checkout `bugsinpy_thefuck_1` buggy/fixed 到 ignored
  `outputs/evp7_thefuck1_f2p_probe_retry/`；
- buggy/fixed checkout 目录均真实存在；
- BugsInPy fixed checkout 形态为 buggy HEAD 加 patched files，两个 checkout
  的 git HEAD 均为 buggy commit，这是该 checkout 工具的输出形态；
- 在未安装依赖的当前环境中运行目标 pytest，两个版本均在 collection 前因缺少
  `psutil` 失败，尚不能判断 F2P。

Repair Plan:

1. 在 ignored `outputs/envs/thefuck1_f2p_py311/` 创建隔离 venv；
2. 只安装 target pytest 所需依赖，不安装 editable self Git requirement，不改全局环境；
3. 在 venv 中顺序重跑 buggy/fixed 目标 pytest；
4. 若仍为依赖/兼容 blocker，记录为 environment blocked；
5. 若 buggy fail 且 fixed pass，只记录 `f2p_established_p2p_not_attempted`，不直接
   admission。

Repair Execute:

- 创建 ignored venv `outputs/envs/thefuck1_f2p_py311/`；
- 安装目标测试最小依赖：
  `pytest`, `psutil`, `six`, `decorator`, `colorama`, `pyte`,
  `win-unicode-console`；
- 未安装 editable self Git requirement，未修改 checkout，未修改全局环境；
- venv 中 buggy 目标 pytest：1 failed / 1 passed；
- venv 中 fixed 目标 pytest：2 passed；
- 更新 `data/tasks/evp7_controlled_probe_results.json`：
  `bugsinpy_thefuck_1 = f2p_established_p2p_not_attempted`；
- 修正 readiness decision：下一步是 bounded project-level P2P-broad，而不是重复
  checkout/F2P。

Verify:

- `data/tasks/evp7_expansion_readiness.json` 现在记录：
  - `p2p_candidate_tasks = ["bugsinpy_thefuck_1"]`；
  - `f2p_established_p2p_not_attempted = 1`；
  - `f2p_blocked_checkout_network` 已不再出现；
  - main cohort 仍为 20 tasks / 94 candidates；
- `docs/experiments/evp7_expansion_readiness.md` 同步显示
  `bugsinpy_thefuck_1` 的下一步为 project-level P2P-broad。

Diagnose:

- 问题类型从 checkout/network blocker 推进为 F2P established / P2P pending；
- 这不是 cohort expansion 完成状态，因为尚无 project-level P2P-broad manifest、
  candidate construction 或 candidate revalidation。

结论:

- `bugsinpy_thefuck_1` 已成为第一个 fresh-project
  `f2p_established_p2p_not_attempted` lane；
- 完成扩 EVP-7 cohort 的下一步是 bounded project-level P2P-broad construction；
- 通过 P2P-broad 前不得新增 `p2p_broad_main` task 或重新计算 21-task metrics。

## 2026-06-16 bugsinpy_thefuck_1 project-level P2P-broad dry-run

Inspect:

- F2P 已建立，但 main cohort 仍为 20 tasks / 94 candidates；
- `scripts/build_pass_to_pass_scope.py` 是现有 project-level P2P-broad builder；
- builder 期望 checkout source root 形态为
  `<source_root>/thefuck_1/{buggy,fixed}/thefuck`；
- 当前 F2P checkout 位于 ignored
  `outputs/evp7_thefuck1_f2p_probe_retry/{buggy,fixed}/thefuck`。

Plan:

1. 创建 ignored `outputs/thefuck1_p2p_workspace/thefuck_1/{buggy,fixed}/`；
2. 用目录 junction 指向已验证的 F2P buggy/fixed checkout，不复制到 tracked 区；
3. 运行 `build_pass_to_pass_scope.py --dry-run`，确认 project-level pytest test
   paths、F2P oracle nodeid、venv python、输出路径和 manifest 路径；
4. dry-run 通过后，再决定是否进入 bounded project-level P2P-broad execution。

验收条件:

- dry-run 不执行测试、不创建 manifest；
- 不 admission、不构造 candidates；
- 如果 dry-run 暴露路径或 oracle nodeid 问题，先修计划和命令，不运行 P2P。

Execute:

- 创建 ignored junction 工作区
  `outputs/thefuck1_p2p_workspace/thefuck_1/{buggy,fixed}/thefuck`，指向已验证
  F2P checkout；
- `build_pass_to_pass_scope.py --dry-run` 通过；
- dry-run 确认：
  - buggy/fixed checkout 均存在；
  - F2P oracle nodeid 为
    `tests/rules/test_pip_unknown_command.py::test_get_new_command[pip un+install thefuck-un+install-uninstall-pip uninstall thefuck]`；
  - test framework = `pytest`；
  - scope type = `project_level_p2p_broad`；
  - output dir = `outputs/thefuck1_project_p2p_scope_001`；
  - manifest out = `data/p2p_scopes/bugsinpy_thefuck_1_p2p_broad.json`；
  - dry-run 不执行测试、不创建 manifest。

Execution Plan:

1. 使用相同参数移除 `--dry-run`；
2. 运行 bounded project-level P2P-broad builder：
   - runs = 3；
   - per-test timeout = 30s；
   - batch timeout = 600s；
   - batch size = 50；
   - batch-first enabled；
3. 若 manifest 成功且 `p2p_broad_tests >= 3`，进入 candidate construction 计划；
4. 若 manifest 不足或 collection/runtime blocker，记录 blocker，不 admission。

Execute:

- 第一次 P2P execution 生成 0-test collection-error manifest；
- Diagnose：`build_pass_to_pass_scope.py` 的 compat shim 在 venv 已安装真实
  `psutil` 时仍注入 fallback `psutil`，导致 `thefuck.shells.Process(os.getpid())`
  报 `_Process() takes no arguments`；
- Repair：修复 builder shim，先 import real `psutil`，仅 import 失败时使用 fallback；
  fallback `Process` 也补齐 `__init__`, `name`, `parent`, `children`；
- 删除错误 shim 产生的 0-test manifest 和 raw P2P 输出，重新 dry-run 通过；
- 修复后重新执行 P2P builder，真实 pytest batches 开始运行，但达到 30 分钟
  外层超时仍无 manifest；
- 终止残留 builder/pytest 进程；
- 更新 controlled probe result：
  `bugsinpy_thefuck_1 = f2p_established_project_p2p_timeout`。

Verify:

- `data/p2p_scopes/bugsinpy_thefuck_1_p2p_broad.json` 不存在；
- `data/p2p_scopes/bugsinpy_thefuck_1_p2p_broad_collection_errors.json` 不存在；
- readiness 现在记录：
  - `p2p_candidate_tasks = []`；
  - `f2p_established_project_p2p_timeout = 1`；
  - main cohort 仍为 20 tasks / 94 candidates；
- 无残留 `bugsinpy_thefuck_1` / `thefuck1_p2p` / `thefuck1_f2p_py311` 相关
  python 进程。

结论:

- `bugsinpy_thefuck_1` 已建立 F2P，但 project-level P2P-broad 在当前 30 分钟
  bounded policy 下没有 manifest；
- 不得 admission，不得构造 candidates，不得更新 21-task metrics；
- 完成扩 cohort 的下一步需要：
  - 明确 `thefuck` P2P policy redesign；或
  - 选择另一条 fresh-project lane 做 checkout/F2P/P2P。

## 2026-06-16 bugsinpy_thefuck_1 pip-rule-family P2P policy probe

Inspect:

- 当前 readiness：main cohort 仍为 20 tasks / 94 candidates；
- `p2p_candidate_tasks = []`；
- registry-risk 排除后，fresh-project promising candidates 全部来自 `thefuck`
  项目，换 `thefuck_2` 等同项目任务不能绕开 project-level P2P 超时；
- 既有成功路线允许显式 project-level scope policy，例如
  `youtube_dl_dynamic_download_nodeid_exclusion_v1`；
- `build_pass_to_pass_scope.py` 的 `--static-include-token` 会在 collection 后、
  dynamic run 前过滤 nodeid，适合先做 no-API bounded policy experiment。

Plan:

1. 定义显式 policy：`thefuck_pip_rule_family_p2p_v1`；
2. 仍使用已验证 `thefuck_1` buggy/fixed checkout 和 project-level P2P builder；
3. 使用 `--static-include-token pip`，只动态验证源段含 `pip` 的 project-level
   collected tests；
4. 继续排除默认外部 token：`httpbin`, `http://`, `https://`；
5. 输出到 ignored `outputs/thefuck1_project_p2p_scope_pip_policy_001/` 和 tracked
   `data/p2p_scopes/bugsinpy_thefuck_1_p2p_broad_pip_policy.json`；
6. 该 manifest 即便成功，也只证明 policy experiment；进入 admission 前还必须
   candidate construction 和 candidate revalidation。

验收条件:

- 不调用 API；
- 不修改 checkout；
- 不构造 candidates；
- 不 admission；
- 如果 P2P-broad tests < 3 或 manifest 未生成，记录 blocker；
- 如果 P2P-broad tests >= 3，只进入 candidate construction 计划，不直接改
  registry main cohort。

Execute:

- 运行 `thefuck_pip_rule_family_p2p_v1` 时，builder 仍在 collection 阶段尝试
  收集 shell/functional 文件；
- 15 分钟外层预算内没有 manifest；
- 残留 builder / pytest collect-only 进程已终止；
- Diagnose：`--static-include-token pip` 是 collection 后过滤，不能避免非目标
  test files 的 collection blocker。

Repair Plan:

1. 改为 rules-root policy：`thefuck_rules_root_pip_p2p_v1`；
2. 使用 `--scope-type project_level_official_test_root --test-path tests/rules`，让
   builder 只收集 `tests/rules` 根；
3. 继续使用 `--static-include-token pip`，只动态验证 pip 相关 rule-family tests；
4. 该策略仍是 no-API policy experiment；manifest 成功也不直接 admission。

Repair Execute:

- `thefuck_rules_root_pip_p2p_v1` dry-run 通过，test paths 限定在
  `tests/rules`；
- policy run 生成 tracked manifest
  `data/p2p_scopes/bugsinpy_thefuck_1_p2p_broad_rules_pip_policy.json`；
- manifest 统计：
  - collected tests = 1431；
  - collection error files = 0；
  - excluded fail-to-pass oracle = 1；
  - static include filter excluded = 1425；
  - P2P-broad tests = 4；
- P2P-broad tests：
  - `tests/rules/test_fix_alt_space.py::test_match`；
  - `tests/rules/test_pip_install.py::test_get_new_command`；
  - `tests/rules/test_pip_unknown_command.py::test_get_new_command[pip instatl-instatl-install-pip install]`；
  - `tests/rules/test_pip_unknown_command.py::test_match`。

Next Gate:

- 该 policy manifest 已满足 >=3 P2P-broad tests，但还不是 admission；
- 下一步只允许进行 minimal candidate construction 和 F2P + P2P revalidation；
- 若 reference patch 不能通过 retained oracle + P2P，必须停止并记录 blocker。

Cleanup:

- 已清理本轮失败或冗余过程目录：
  - `outputs/thefuck1_project_p2p_scope_001/`；
  - `outputs/thefuck1_project_p2p_scope_pip_policy_001/`；
  - `outputs/thefuck1_candidate_validation_001/workdirs/`；
- `outputs/thefuck1_project_p2p_scope_rules_pip_policy_001/` 的 raw
  `p2p_scope.*` 已由 tracked
  `data/p2p_scopes/bugsinpy_thefuck_1_p2p_broad_rules_pip_policy.json`
  承接，但该 tracked manifest 引用的 `compat_shim/` 仍需保留，已恢复最小
  shim 目录；
- 已清理历史 candidate validation 中不再被 visible-test runner 读取的
  `oracle_workdirs/` 与空 `workdirs/`，保留 `p2p_workdirs/`、候选 JSON 和
  validation JSON；
- Verify：所有 tracked P2P manifest 的 enabled `compat_shim.path` 均存在；
  `scripts/build_evp7_candidate_manifest.py` 当前声明的候选输入 JSON 均存在。

## 2026-06-16 bugsinpy_thefuck_1 admission and EVP-7 21-task rebuild

Inspect:

- 当前 registry admission 前为 20 tasks / 94 candidates；
- `bugsinpy_thefuck_1` 已有：
  - rules-root pip-family P2P manifest：
    `data/p2p_scopes/bugsinpy_thefuck_1_p2p_broad_rules_pip_policy.json`；
  - 4 retained P2P-broad tests；
  - 4 candidate validation records；
  - label counts：1 correct, 2 issue-not-fixed, 1 regression。

Plan:

1. 只按已验证 policy boundary admission；
2. 明确 `thefuck_rules_root_pip_p2p_v1` 是 `tests/rules` + `pip`
   source-token policy，不写成 full-project coverage；
3. 更新 registry、controlled probe result、candidate manifest input mapping；
4. 重建 no-API deterministic artifacts；
5. 不调用真实 LLM API，不重写 376-record real G5 result。

Execute:

- `bugsinpy_thefuck_1` 已加入 `p2p_broad_main`；
- 新增 candidate builder：
  `scripts/build_thefuck1_candidates.py`；
- 新增 retained oracle：
  `scripts/oracles/thefuck_1_pip_unknown_command.py`；
- 新增 admission report：
  `docs/experiments/thefuck1_candidate_validation.md`；
- 修复 `scripts/run_evp7_visible_tests.py`：
  - retained oracle 若是包装脚本，不再误用包装脚本的 Python 解释器；
  - 从 tracked P2P manifest 的 batch command 取真实测试 Python；
  - 相对 Python 路径按 repo root 解析为绝对路径。

Verify:

- `python scripts/build_evp7_protocol_manifests.py --check`
  - main tasks = 21；
  - known candidates = 98；
  - projects = 6；
- `python scripts/build_evp7_candidate_manifest.py --check`
  - candidates = 98；
  - correct = 21；
  - issue-not-fixed = 76；
  - regression = 1；
- `python scripts/run_evp7_visible_tests.py --run --check --timeout 90`
  - visible outcomes = 98；
  - completed = 95；
  - error = 3；
  - `bugsinpy_thefuck_1` = 4 completed；
- `python scripts/build_evp7_visible_tool_summaries.py --check`
  - summaries = 98 complete；
- `python scripts/build_evp7_evidence_packets.py --check`
  - packets = 392；
  - E0/E2/E4/E6 each = 98 complete；
  - G1 = passed；
  - G2 leakage audit = passed；
- `python scripts/run_evp7_tool_only_baselines.py --check`
  - G3 = passed；
- `python scripts/run_evp7_merge_gate_schema_dry_run.py --check`
  - records = 392；
  - valid parses = 392；
  - G4 = passed；
- `python scripts/analyze_evp7_schema_dry_run_metrics.py --check`
  - G5 metric scaffold = passed；
  - still requires real LLM verifier outputs for model-effect claims；
- `python scripts/build_evp7_g5_llm_prompt_manifest.py --check`
  - prompt records = 392；
  - leakage failures = 0；
  - readiness = `passed_without_api`；
- G5 example preflight and workflow check-only:
  - structural ready = true；
  - API ready = false because provider/model/cost/smoke/full-run confirmation
    remains intentionally missing。

Conclusion:

- EVP-7 structural cohort expansion is now 21 tasks / 98 candidates / 392
  no-API evidence packets；
- The latest real DeepSeek G5 full run remains the historical
  20-task / 94-candidate / 376-packet result；
- The new 392-packet cohort is ready for a future user-confirmed G5 smoke/full
  run, but no real API call has been attempted in this admission round。

Next Boundary:

- Do not continue blind BugsInPy sweeping；
- Choose one of:
  - user-confirmed G5 rerun on the 392-packet cohort；
  - new 30-50 bug expansion decision boundary；
  - paper/manuscript synchronization that keeps 376-real-run and 392-no-API
    boundaries separate。

## 2026-06-16 EVP-7-30 controlled expansion start

Inspect:

- 当前 synced baseline：21 tasks / 98 candidates / 392 no-API evidence packets；
- 当前 main projects：
  - `youtube-dl`: 13；
  - `cookiecutter`: 3；
  - `PySnooper`: 2；
  - `httpie`: 1；
  - `thefuck`: 1；
  - `tqdm`: 1；
- 目标：扩到 30 tasks，至少 8 projects；
- 缺口：
  - tasks: +9；
  - projects: 至少 +2；
- `evp7_expansion_readiness` 当前显示 fresh-project promising candidates = 0，
  但 metadata-promising top lanes 仍包含 underrepresented/risky projects：
  `fastapi`, `sanic`, `scrapy`, `tornado`, `ansible`, `luigi`。

Plan:

1. 建立 `EVP-7-30 controlled expansion` 边界；
2. 优先 project-diverse lanes，不继续默认堆 `youtube-dl`；
3. 每个新 project 先尝试 1 个任务，除非第一个 admission 非常顺利；
4. 单任务 admission gate 不降低：
   - F2P established；
   - P2P-broad >= 3；
   - candidate construction + retained oracle + P2P revalidation；
5. 当前回合先选择一个 fresh/underrepresented lane 做 bounded checkout/F2P
   前置验证；不调用 LLM API，不做 bulk admission。

Candidate lane priority:

1. `sanic_2` / `sanic_3`：new project，当前 blocker 是 missing `aiofiles`
   或历史 project-level timeout，适合先用 isolated declared-dependency venv
   复核 F2P；
2. `fastapi_4` / nearby FastAPI tasks：new project，但当前 blocker 是
   Pydantic v2 compatibility，需更谨慎地按 declared dependency venv 复核；
3. `tornado_2`：new project，metadata-only 未 probe，但已有 Tornado
   project-level timeout risk；
4. `scrapy_2`：new project，但 Twisted dependency/native blocker 风险高；
5. `ansible_1`、`luigi_1`：Windows/POSIX or missing dependency blockers，先不
   作为首选。

Acceptance boundary:

- 如果 F2P 失败或暴露环境 blocker，记录 blocker，不进入 P2P；
- 如果 F2P 通过，再单独更新计划后做 P2P dry-run；
- P2P manifest 成功且 >=3 后，才允许 candidate construction。

## 2026-06-16 `bugsinpy_sanic_2` F2P recheck under isolated dependency env

Inspect:

- `bugsinpy_sanic_2` 的 buggy/fixed checkout marker 和目标测试文件完整；
- BugsInPy metadata:
  - command: `pytest tests/test_app.py::test_asyncio_server_start_serving`；
  - buggy commit: `ba9b432993019b0af0c4827a5ed42aaa091bd17d`；
  - fixed commit: `801595e24acdf8050b8d3ffa512d424147848d32`；
- 旧 probe 的 blocker 是当前环境缺少 `aiofiles`，未安装依赖、未修改 checkout、
  未到达目标测试。

Execute:

- 新建 ignored dependency env：`outputs/envs/sanic2_f2p_py311`；
- 安装 Sanic 2 F2P 所需的最小声明依赖组合，关键版本包括：
  `aiofiles==0.5.0`、`websockets==8.1`、`multidict==4.7.6`、
  `httpx==0.9.3`、`httpcore==0.3.0`；
- 沿用 Sanic 1 已记录的 Python 3.11 compatibility shim，只恢复旧 Sanic
  在 Python 3.11 下缺失的 asyncio API，不修改 checkout。

Verify:

- buggy target test 失败并到达预期行为点：
  `AttributeError: 'AsyncioServer' object has no attribute 'start_serving'`；
- fixed target test 通过：`1 passed, 1 warning`；
- 因此 `bugsinpy_sanic_2` 的 F2P gate 已建立。

Next Boundary:

- 不能直接 admission；
- 下一步只允许对 Sanic official test root `tests/` 做 P2P-broad dry-run /
  bounded construction；
- 由于 `bugsinpy_sanic_1` 已有 full project scope timeout，不能重跑无边界的
  `.` full project P2P；
- 若 official test root P2P-broad manifest 未能稳定产生至少 3 个 pass-to-pass
  tests，则 `bugsinpy_sanic_2` 继续保持 non-main pending/blocker 状态。

P2P Attempt Result:

- Dry-run 通过，Sanic official test root `tests/` 解析为 44 个 test files；
- bounded construction 使用：
  - scope type: `project_level_official_test_root`；
  - policy: `sanic_tests_root_py311_dependency_p2p_v1`；
  - runs = 3；
  - per-test timeout = 30s；
  - batch timeout = 120s；
  - outer budget = 15 minutes；
- 真实构造超过外层预算，未生成
  `data/p2p_scopes/bugsinpy_sanic_2_official_test_root_p2p_broad.json`；
- 终止后发现残留 pytest 进程卡在
  `tests/test_custom_request.py::test_custom_request`，已停止该 Sanic P2P
  相关进程；
- 已新增 timeout policy record：
  `data/p2p_scopes/bugsinpy_sanic_2_official_test_root_timeout.json`；
- 当前 admission 结论：
  - F2P established；
  - P2P-broad gate failed by official-root timeout/no manifest；
  - 不构造 candidates；
  - 不进入 `p2p_broad_main`；
  - EVP-7 cohort 仍为 21 tasks / 98 candidates / 392 no-API packets。

Next:

- `bugsinpy_sanic_2` 暂停，除非之后明确设计新的 bounded P2P policy；
- 下一扩量任务应转向另一个 fresh/underrepresented lane，优先
  `tornado_2` 或 FastAPI dependency-isolated recheck，而不是继续对 Sanic
  做 task-file-only fallback。

## 2026-06-16 `bugsinpy_tornado_2` bounded F2P probe start

Inspect:

- 当前 EVP-7 main cohort 仍为 21 tasks / 98 candidates / 392 no-API packets；
- 仍缺 9 tasks，且 project count 需要从 6 提升到至少 8；
- `bugsinpy_sanic_2` 已建立 F2P，但 Sanic official-root P2P 超时，无 admission；
- `bugsinpy_tornado_2` 是 readiness 中的 metadata-only lane：
  - framework: `unittest`；
  - command:
    `python -m unittest -q tornado.test.httpclient_test.HTTPClientCommonTestCase.test_redirect_put_without_body`；
  - buggy commit: `2ca8821d006f6693f920a4b183a3a7c985a5c8ad`；
  - fixed commit: `4f486a4aec746e9d66441600ee3b0743228b061c`；
  - requirements: `tornado==6.0.4`；
  - patch touches `tornado/http1connection.py` transfer-encoding handling。

Plan:

1. 串行准备 `bugsinpy_tornado_2` buggy/fixed checkout；
2. 验证 BugsInPy marker、目标测试文件和 checkout 状态；
3. 只运行 F2P target test，不调用 LLM API，不构造 candidates；
4. 若 Windows/Python 3.11 事件循环策略导致本地 Tornado server 无法运行，
   只允许复用已记录的 `asyncio.WindowsSelectorEventLoopPolicy()` runtime policy；
5. 若 F2P 不成立，记录 blocker 并停止；
6. 若 F2P 成立，本轮最多执行 P2P dry-run 或记录 P2P 边界，不重复 Tornado
   project-level long sweep。

Boundary:

- 不修改 Tornado source/test/fixture；
- 不允许外部网络服务；
- 不做 task-file-only P2P fallback；
- 由于 `bugsinpy_tornado_1` 和 `bugsinpy_tornado_9` 已有 Tornado
  project-level unittest scope timeout 记录，本轮不启动新的长时间真实 P2P
  construction，除非先有新的 bounded policy 和 dry-run 证据。

Execute / Verify:

- 已从 retained local Tornado Git clone 按 BugsInPy
  reset/copy-test-file/copy-fixed-file 流程构造 `bugsinpy_tornado_2`
  buggy/fixed checkout；
- marker 和目标测试文件验证通过：
  - `bugsinpy_run_test.sh`；
  - `bugsinpy_bug.info`；
  - `bugsinpy_requirements.txt`；
  - `tornado/test/httpclient_test.py`；
- buggy checkout 仅包含 fixed test 注入；
- fixed checkout 包含 fixed test 注入和 `tornado/http1connection.py` 修复；
- 使用已记录的 Windows selector event-loop policy 运行 F2P：
  - buggy：`HTTPStreamClosedError` 后 5s `TimeoutError`，失败；
  - fixed：`OK`；
- 因此 `bugsinpy_tornado_2` F2P established。

P2P Dry-run:

- `build_pass_to_pass_scope.py --dry-run` 通过；
- dry-run 参数：
  - `--test-framework unittest`；
  - `--unittest-start-dir tornado/test`；
  - `--unittest-pattern *_test.py`；
  - `--unittest-top-level-dir .`；
  - `--fail-to-pass-nodeid tornado.test.httpclient_test.HTTPClientCommonTestCase.test_redirect_put_without_body`；
  - runs = 3；
  - timeout = 8s；
  - batch timeout = 120s；
  - batch first enabled；
- 未启动真实 P2P construction，未生成 P2P manifest。

Decision:

- `bugsinpy_tornado_2` 记录为
  `f2p_established_shared_tornado_p2p_timeout_risk`；
- 不构造 candidates；
- 不进入 `p2p_broad_main`；
- EVP-7 cohort 仍为 21 tasks / 98 candidates / 392 no-API packets；
- 下一步应转向非 Tornado 的 fresh/underrepresented lane，或回到
  underrepresented admitted project 中寻找可复用 P2P policy 的任务。

## 2026-06-16 `bugsinpy_thefuck_5` underrepresented-policy expansion start

Inspect:

- 当前 main cohort 仍为 21 tasks / 98 candidates / 392 no-API packets；
- fresh-project lanes `sanic_2` 和 `tornado_2` 均已建立 F2P，但未通过 P2P
  admission gate；
- `thefuck` 目前只有 1 个 main task，但 `bugsinpy_thefuck_1` 已在
  `thefuck_rules_root_pip_p2p_v1` 下顺利完成 F2P、P2P-broad 和 candidate
  validation；
- `bugsinpy_thefuck_5` 是同项目 underrepresented rules-root candidate：
  - command: `pytest tests/rules/test_git_push.py::test_match_bitbucket`；
  - buggy commit: `7c858fadb3458be829d3d43666ccb46c3ed5b8a0`；
  - fixed commit: `c205683a8df8a57e2db1e9816a5a7ce3255b08fc`；
  - patch target: `thefuck/rules/git_push.py`；
  - target file `tests/rules/test_git_push.py` 中除 F2P 外还有多条
    `test_match`、`test_not_match` 和 `test_get_new_command` 用例，具备
    P2P-broad 候选空间。

Plan:

1. 从已验证的 local thefuck Git checkout 构造 `bugsinpy_thefuck_5`
   buggy/fixed workspace；
2. 验证 marker、目标测试文件、fixed source diff；
3. 使用 existing ignored env `outputs/envs/thefuck1_f2p_py311` 运行 F2P；
4. 若 F2P 不成立，记录 blocker 并停止；
5. 若 F2P 成立，再用 explicit rules-root git-push policy 做 P2P dry-run；
6. 只有 P2P-broad >= 3 后才允许 candidate construction 和 revalidation。

Boundary:

- 不调用 LLM API；
- 不修改 checkout source/test/fixture；
- 不使用 task-file-only fallback；
- 不把 `thefuck_1` 的 pip-specific P2P tests 直接复用给 git-push 任务；
- 新 policy 必须明确为 rules-root + git-push/test source bounded scope。

Execute / Diagnose:

- 已按 BugsInPy checkout 形态构造 `bugsinpy_thefuck_5` buggy/fixed workspace；
- 初次复用 `thefuck_1` 的 pytest 9 env 时，目标测试在旧
  `request.node.get_marker` API 处失败，属于工具链环境 blocker，不是 F2P
  结果；
- 根据 `thefuck_5` requirements 建立 ignored env
  `outputs/envs/thefuck5_f2p_py311`：
  - `pytest==3.10.1`；
  - `pluggy==0.13.1`；
  - `py==1.11.0`；
  - `pyte==0.8.0`；
  - `win-unicode-console==0.5`；
- Python 3.11 下运行旧 pytest 需要 `--assert=plain`，否则 assertion rewrite
  在 AST 兼容层失败；
- F2P 结果：
  - buggy：`test_match_bitbucket` 到达目标行为并 `AssertionError`；
  - fixed：`1 passed`；
  - 因此 F2P established。

P2P Attempts:

1. `thefuck_rules_root_git_push_p2p_v1`
   - scope: `project_level_official_test_root`；
   - root: `tests/rules`；
   - static include token: `git push`；
   - result: 只保留 2 条 P2P-broad tests，不满足 >=3；
2. `thefuck_rules_root_git_p2p_v1`
   - root: `tests/rules`；
   - static include token: `git`；
   - result: 15 分钟外层超时，未生成 manifest；
   - observed stuck test:
     `tests/rules/test_git_merge.py::test_match`。

Decision:

- `bugsinpy_thefuck_5` 记录为 `f2p_established_p2p_gate_failed`；
- 已删除不达标的 1MB generated P2P manifest 和 P2P 输出目录；
- 已保留小型 blocker record：
  `data/p2p_scopes/bugsinpy_thefuck_5_p2p_blocked_rules_git_policy.json`；
- 不构造 candidates；
- 不进入 `p2p_broad_main`；
- EVP-7 cohort 仍为 21 tasks / 98 candidates / 392 no-API packets；
- 已清理本轮 ignored checkout/env 过程目录：
  `outputs/thefuck5_p2p_workspace` 和 `outputs/envs/thefuck5_f2p_py311`。

## 2026-06-17 final roadmap evidence-level boundary optimization

Inspect:

- 当前 canonical final route 是 `docs/plans/final_paper_roadmap_zh.md`；
- roadmap 仍包含旧的完整 E0-E7 ladder 建议，并写有“核心曲线稳定后补齐
  E1/E3/E5”的分阶段消融建议；
- 当前实际 evidence packet builder 只生成 E0/E2/E4/E6，且 E0 已包含
  `issue_summary`、`patch_diff` 和 `touched_files`；
- 当前 E2 相比 E0 的主要新增证据是 `patch_applies`，`syntax_import_check`
  和 `static_analysis` 仍为 `not_run`；
- 因此 E1/E3/E5 不能作为当前 EVP-7 四层之间的自然中间层直接插入，否则会
  混淆 four-anchor pilot 与 full adjacent-difference ladder。

Plan:

1. 将 `final_paper_roadmap_zh.md` 中的短期路线明确改为 EVP-7
   four-anchor evidence visibility pilot；
2. 删除或替换“核心曲线稳定后补齐 E1/E3/E5”的旧执行建议；
3. 将完整 E0-E6 adjacent-difference ladder 下沉为未来 EVP-8 /
   EVP-7-v2 协议，要求从 E0 开始重新定义、重建 packets/prompts/baselines/
   LLM runs/statistics；
4. 同步更新 protocol、INDEX 和 engineering notes，防止后续继续按旧路线补
   E135；
5. 只做文档路线修订，不改实验数据、不调用 API、不重新生成 evidence packets。

Acceptance:

- roadmap 明确区分 short-term four-anchor paper 和 future full-ladder study；
- protocol 不再暗示当前 EVP-7 稳定后可直接补 E1/E3/E5；
- INDEX 和 engineering notes 能指向新的路线边界；
- 文档审计/最小检查通过，且 diff 不包含 raw outputs、credentials 或本地路径。

Execute:

- 已更新 `docs/plans/final_paper_roadmap_zh.md`：
  - 当前 paper-facing EVP-7 定义为 E0/E2/E4/E6 four-anchor pilot；
  - 删除“核心曲线稳定后补齐 E1/E3/E5”的后续执行路线；
  - 将完整 E0-E6 adjacent-difference ladder 下沉为未来 EVP-8 /
    EVP-7-v2，需要整体重做 packets/prompts/baselines/LLM runs/statistics；
  - 修正 historical checkpoint 中把四层 artifacts 误写为 `E0-E6 packets`
    的表述。
- 已同步 `docs/protocol/evidence_visibility_protocol.md`、`README.md`、
  `docs/INDEX.md`、`docs/plans/current_project_state_zh.md` 和
  `docs/experience/engineering_notes.md`。

Verify:

- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过 final roadmap / protocol / paper framing 检查；保留的唯一 blocker 仍是
  历史 prompt-only positive claim 的 `stop_or_redesign`，不影响当前 bounded
  EVP-7 claim。
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过。
- `git diff --check` 通过。

## 2026-06-18 final roadmap non-conflicting workload reinforcement options

Inspect:

- 当前 canonical final roadmap 已明确 EVP-7 是 E0/E2/E4/E6 four-anchor pilot；
- 当前路线已禁止把 E1/E3/E5 直接插入现有 EVP-7 artifacts；
- 当前 paper-facing real G5 run 仍为 20 tasks / 94 candidates / 376 packets；
- structural/no-API cohort 为 21 tasks / 98 candidates / 392 packets；
- 工作区仍有 `cookiecutter_4` 扩量残留，不属于本轮 roadmap 补强路线；
- 用户要求将“第二模型关键层级复现”或“工作量呈现”写入计划，且不能与现有
  four-anchor / no-E135 / future full-ladder 边界冲突。

Plan:

1. 在 `docs/plans/final_paper_roadmap_zh.md` 中新增非冲突补强路线：
   - 默认优先：工作量呈现强化，不调用 API，不扩 bug，不改 evidence levels；
   - 条件选项：第二模型关键锚点复现，只覆盖 E0/E4/E6，需用户确认 provider、
     model、预算、scope 和停止条件；
2. 明确两条路线都服务当前 four-anchor paper，不支持 full ladder claim；
3. 同步 README、INDEX、current project state 和 engineering notes；
4. 不改实验数据，不重建 packets，不调用 API；
5. 提交时不纳入既有 `cookiecutter_4` 未提交 P2P 残留。

Acceptance:

- final roadmap 将“工作量呈现”列为默认无 API 补强路径；
- final roadmap 将“第二模型关键锚点复现”列为需确认预算和 scope 的条件路径；
- 文档明确第二模型复现不补 E1/E3/E5、不扩 bug、不改当前 DeepSeek G5 结果边界；
- paper readiness / local quality / diff check 通过。

Execute:

- 已在 `docs/plans/final_paper_roadmap_zh.md` 新增
  `18.4.1 当前论文的非冲突补强路线`：
  - 默认优先路线：工作量呈现强化；
  - 条件补强路线：第二模型关键锚点复现；
  - 第二模型只覆盖 E0/E4/E6，必须先由用户确认 provider、model、预算、
    scope 和停止条件；
  - 两条路线都不得重开 E1/E3/E5、full-ladder claim、盲目扩 bug 或
    LLM 优于 tool-only baseline claim。
- 已同步 `README.md`、`docs/INDEX.md`、
  `docs/plans/current_project_state_zh.md` 和
  `docs/experience/engineering_notes.md`。

Verify:

- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过 final roadmap / protocol / paper framing 检查；保留的唯一 blocker 仍是
  历史 prompt-only positive claim 的 `stop_or_redesign`。
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过。
- `git diff --check` 通过。

## 2026-06-18 paper workload presentation reinforcement

Inspect:

- final roadmap 已把当前论文的默认补强路线定为工作量呈现强化；
- `docs/paper/patch_verification_draft.md` 和
  `docs/paper/ieee_submission_draft.tex` 尚未在前段集中呈现 cohort
  construction、candidate construction、evidence packets、tool-only baseline、
  real LLM review 和 claim audit 的完整工作量；
- 当前 structural/no-API pipeline 是 21 tasks / 98 candidates / 392
  E0/E2/E4/E6 packets；
- 当前 paper-facing real DeepSeek G5 run 仍限定为 20 tasks / 94 candidates /
  376 records；
- 本轮不属于 `cookiecutter_4` 扩量，不处理其未提交 P2P 残留。

Plan:

1. 在 Markdown paper draft 中加入 `Workload at a Glance`，把现有 pipeline
   工作量显式写成论文贡献；
2. 在 `scripts/write_paper_tables.py` 中生成 EVP-7 workload ledger，避免
   Markdown/LaTeX 表格手工漂移；
3. 在 `scripts/write_ieee_latex_draft.py` 中加入 IEEE draft 的
   `Workload at a Glance` reader bridge；
4. 同步 README、INDEX、current project state 和 engineering notes；
5. 不调用 API、不扩 bug、不补 E1/E3/E5、不改变当前 bounded four-anchor claim。

Execute:

- 已更新 `docs/paper/patch_verification_draft.md` 的摘要和
  `Workload at a Glance`；
- 已更新 `scripts/write_paper_tables.py`，从 tracked summaries 生成 EVP-7
  workload ledger，并重新生成 `docs/paper/generated_tables.md` 和
  `docs/paper/generated_tables.tex`；
- 已更新 `scripts/write_ieee_latex_draft.py`，并重新生成
  `docs/paper/ieee_submission_draft.tex`；
- 已修复 workload ledger 中 `1 regression negative` 的单复数问题；
- 已修复 IEEE generator 中与 hidden-evaluator 设计冲突的
  `hidden-evaluator-free` 表述。

Verify:

- `python -m py_compile scripts\write_paper_tables.py scripts\write_ieee_latex_draft.py`
  通过；
- `python scripts\write_paper_tables.py` 通过并重新生成表格；
- `python scripts\write_ieee_latex_draft.py` 通过并重新生成 IEEE draft；
- `rg -n "hidden-evaluator-free|regression negatives"` 无残留。
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过 current EVP-7 bounded-pilot claim readiness；保留的唯一 blocker 仍是
  历史 prompt-only positive claim 的 `stop_or_redesign`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过。
