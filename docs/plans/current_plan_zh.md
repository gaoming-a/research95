# 当前计划：AI 生成补丁的可验证审查

最后更新：2026-06-29

## 0. 2026-06-29 本轮小目标：EVP-8-HARD Phase B 源盘点

本轮目标是执行
`docs/experiments/evp8_hard_case_extension_plan_20260629.md` 的 Phase B
前置盘点：检查本地已有候选补丁、验证记录和 agent patch 记录是否足够支撑
一个单独的 `EVP-8-HARD` hard-case 扩展。

边界：

- 不调用任何模型 API；
- 不修改旧 98-candidate EVP-8 controlled cohort；
- 不生成新的 hard-case candidate manifest；
- 不保存 patch diff、prompt text 或 raw model response 到 tracked 输出；
- 只输出候选源级别的聚合统计和是否可进入下一步的判断。

验收条件：

- 盘点脚本能复现候选源、验证源和 agent patch 源的数量统计；
- 明确区分已用于旧 controlled cohort 的候选和可作为新增 hard-case 来源的候选；
- 给出是否满足 Phase B 目标规模和 opportunity-set 前置条件的保守判断；
- 同步更新计划、索引、经验文档和当前状态。

## 0.1 2026-06-29 本轮小目标：EVP-8-HARD candidate draft 与 baseline gate

本轮目标是在已完成 source inventory 的基础上，构造一个单独的 no-API
`EVP-8-HARD` candidate draft，并生成对应的 deterministic tool-only baseline
和 headroom gate。

边界：

- 不调用任何模型 API；
- 不生成 rendered prompt；
- 不读取 raw model responses；
- 不修改旧 98-candidate controlled cohort；
- 不把 source inventory 等同于最终 hard-case 实验结果；
- 如果可见测试证据只有 test hint 而没有 outcome，不得假装工具 baseline
  看到了 passing tests。

验收条件：

- 输出 evaluator-only manifest 和 model-visible seed manifest；
- hidden labels、hidden oracles、expected outcome 不进入 model-visible seed；
- 至少生成 30-50 条 applied candidate records，或明确 blocked 原因；
- 计算 hard-negative、AI/agent、correct/control 分布；
- 生成 hard-case tool-only baseline；
- 若 false-accept/false-reject headroom 或 hard-negative gate 不足，必须把
  API readiness 标记为 blocked。

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

## 2026-06-16 `bugsinpy_cookiecutter_4` underrepresented-project expansion start

Inspect:

- 当前 main cohort 仍为 21 tasks / 98 candidates / 392 no-API packets / 6
  projects；
- fresh-project lanes 中，FastAPI/Sanic/Tornado/Scrapy/Ansible/Luigi 均已有
  明确 dependency、Windows 或 project-level P2P blocker；
- underrepresented existing projects 中：
  - `httpie_1` 到 `httpie_4` 已记录 collection/timeout/compatibility
    blocker；
  - `tqdm_1` 和 `tqdm_2` 的 P2P-broad size 只有 1，`tqdm_3` 到
    `tqdm_8` 共享 missing nose / insufficient collectable P2P blocker；
  - `PySnooper_2` 需要 test-fixture/compatibility shim，已按用户确认冻结；
- `cookiecutter` 已有 3 个 admitted tasks，project-level P2P 环境和
  candidate validation 路径稳定；
- `bugsinpy_cookiecutter_4` 是剩余 Cookiecutter task：
  - buggy commit: `9568ab6ecd2d6836646006c59473c4a4ac0dee04`；
  - fixed commit: `457a1a4e862aab4102b644ff1d2b2e2b5a766b3c`；
  - target: `tests/test_hooks.py::TestExternalHooks::test_run_failing_hook`；
  - test file: `tests/test_hooks.py`；
  - command in BugsInPy metadata: `tox tests/test_hooks.py::TestExternalHooks::test_run_failing_hook`。

Plan:

1. 构造 `bugsinpy_cookiecutter_4` buggy/fixed checkout；
2. 验证 marker、目标测试文件、bug patch 与 fixed patch 作用文件；
3. 使用已审计 Cookiecutter isolated env 运行目标 F2P；
4. 若 F2P 不成立或 oracle 与既有 Cookiecutter bug 重复/污染，记录 blocker
   并停止；
5. 若 F2P 成立，再复用 Cookiecutter project-level P2P builder policy；
6. 只有 P2P-broad >= 3 后，才补 retained oracle、构造 candidates，并执行
   retained-oracle + P2P validation。

Boundary:

- 不调用 LLM API；
- 不修改 checkout source/test fixture；
- 不使用 task-file-only fallback；
- 不把其他 Cookiecutter task 的 P2P manifest 直接复用为 admission 证据；
- 若目标 oracle 已经被证明只是其他 Cookiecutter bug 的重复标签，停止并记录，
  不强行扩 cohort。

Execute:

- 已检查本地残留的 `bugsinpy_cookiecutter_4` project-level P2P 构造输出；
- 该输出不构成 admissible P2P-broad manifest：collection/batch 执行被
  missing `yaml` / `ruamel` / `past`、不可用的 `cookiecutter` console command
  invocation，以及 external template tests fail/timeout 主导；
- 已新增小型 blocker policy：
  `data/p2p_scopes/bugsinpy_cookiecutter_4_p2p_blocked_environment_policy.json`；
- 已将 `data/tasks/evp7_controlled_probe_results.json` 追加
  `p2p_blocked_dependency_environment` 记录；
- 已重新运行 `scripts/summarize_evp7_expansion_readiness.py`，刷新
  `data/tasks/evp7_expansion_readiness.json` 和
  `docs/experiments/evp7_expansion_readiness.md`；
- 已同步 README、INDEX、current project state 和 engineering notes。

Decision:

- `bugsinpy_cookiecutter_4` 不进入 `p2p_broad_main`；
- 不构造 candidates；
- 不使用 task-file P2P downgrade；
- 不修改 source/test fixture；
- 不调用 LLM API；
- 完整 builder 失败输出仅作为本地诊断残留，不提交为 tracked admission
  artifact。

Verify:

- `python -m json.tool data\tasks\evp7_controlled_probe_results.json` 通过；
- `python -m json.tool data\tasks\evp7_expansion_readiness.json` 通过；
- `python -m json.tool data\p2p_scopes\bugsinpy_cookiecutter_4_p2p_blocked_environment_policy.json`
  通过；
- `python scripts\summarize_evp7_expansion_readiness.py` 通过，并显示
  `bugsinpy_cookiecutter_4` 已进入 controlled probe records、
  `p2p_blocked_dependency_environment = 1`、main cohort 仍为 21 tasks /
  98 candidates；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过 current EVP-7 bounded-pilot claim readiness；保留的唯一 blocker 仍是
  历史 prompt-only positive claim 的 `stop_or_redesign`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过。

## 2026-06-18 paper readiness requires advisor workload packet

Inspect:

- 上一轮已将 `docs/paper/advisor_workload_response_zh.md` 纳入 anonymous
  artifact required gate；
- `scripts/audit_paper_readiness.py` 的 required docs 尚未包含该 advisor packet；
- 因此当前 artifact audit 会在 advisor packet 缺失时失败，但 paper readiness
  仍可能报告 submission package ready，两个提交包 readiness gate 不一致。

Plan:

1. 将 `docs/paper/advisor_workload_response_zh.md` 加入
   `audit_paper_readiness.py` 的 required docs；
2. 不改变 `current_result_claim_ready`、`evp7_bounded_pilot_claim_ready`、
   prompt-only/tool-augmented claim 或 paper framing 逻辑；
3. 用正向 readiness run 和临时缺失 advisor packet 的负向 run 验证；
4. 同步 README/INDEX/engineering notes 中的 readiness gate 说明；
5. 不调用 API、不扩 cohort、不补 E1/E3/E5、不修改实验数据。

Acceptance:

- 当前正常 paper readiness 继续通过，`submission_package_ready=true`；
- 临时缺失 advisor packet 时，paper readiness 表现为
  `required_docs_ready=false`、`minimum_inputs_ready=false`、
  `negative_or_methods_draft_ready=false` 和 `submission_package_ready=false`；
- local quality gate 通过；
- diff check 和 staged sensitive scan 通过。

Execute:

- 已更新 `scripts/audit_paper_readiness.py`：
  - required docs 新增 `advisor_workload_response`；
  - 输出 `required_docs_ready`；
  - `submission_package_ready` 现在同时要求 required docs 全部存在；
  - 未改变 `current_result_claim_ready`、`evp7_bounded_pilot_claim_ready`、
    prompt-only/tool-augmented claim 逻辑；
- 已同步 README、docs/INDEX 和 engineering notes，说明 paper readiness required
  docs 也包含 advisor-facing workload response。

Verify:

- `python -m py_compile scripts\audit_paper_readiness.py scripts\audit_anonymous_artifact.py scripts\prepare_anonymous_artifact.py scripts\run_local_quality_gate.py`
  通过；
- 正向 `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`required_docs_ready=true`、
  `required_docs.advisor_workload_response.exists=true`、
  `submission_package_ready=true`；
- 负向 readiness：临时重命名 `docs/paper/advisor_workload_response_zh.md`
  后运行 `audit_paper_readiness.py`，输出
  `required_docs_ready=false`、`minimum_inputs_ready=false`、
  `negative_or_methods_draft_ready=false`、`submission_package_ready=false`、
  `required_docs.advisor_workload_response.exists=false`；随后已恢复文件；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`。

## 2026-06-18 default no-API paper maintenance continuation

Inspect:

- 当前本地 `main` 比 `origin/main` ahead 2，两个未推送提交已记录为 GitHub
  网络层同步失败边界；
- `docs/experiments/evp7_next_decision_packet_20260618.md` 明确：没有新的
  实验决策时，只能继续 no-API paper-submission maintenance；
- 当前允许的默认路线是 Option A：提交当前 four-anchor paper package；
- 第二模型关键锚点复现、30-50 bug 扩量和新 verifier design 都需要用户确认
  provider/model/budget/scope 或实验边界，不属于本轮。

Plan:

1. 重新生成 paper tables 和 IEEE LaTeX draft，确认 tracked paper outputs 与
   tracked summaries 一致；
2. 连续两遍编译 IEEE PDF，并抽查 PDF 文本中的 workload ledger、376-record
   real G5 run 和 bounded EVP-7 conclusion；
3. 重建 ignored anonymous artifact ZIP，并运行 artifact audit；
4. 运行 paper readiness 和 local quality gate；
5. 若 tracked 文档需要刷新，只同步 submission checklist / handoff / INDEX /
   current plan 等 no-API readiness 文档；
6. 不调用 API、不扩 cohort、不补 E1/E3/E5、不修改 evidence levels、不提交
   `outputs/` 或 `artifacts/`。

Acceptance:

- paper table/draft generators 运行成功；
- PDF 两遍编译成功，文本抽查命中工作量和 bounded conclusion；
- artifact audit、paper readiness、local quality gate 通过；
- 工作区只包含本轮相关 tracked 文档/脚本变化；
- GitHub 若继续网络失败，记录事实并不阻塞后续任务。

Execute:

- `python scripts\write_paper_tables.py` 通过，重新生成
  `docs/paper/generated_tables.md` 和 `docs/paper/generated_tables.tex`；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；因 draft 依赖刚生成的 LaTeX table，已顺序重跑一次以避免读取时序歧义；
- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续两遍通过，输出 7 页 PDF；
- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf - | rg ...`
  抽查确认 PDF 包含 abstract 工作量、Table III workload ledger、20/94/376
  real G5 run、bounded EVP-7 conclusion 和 unsupported scale-generalized
  claim boundary；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=300`、`safe_to_package=true`。
- 已同步 `docs/experience/engineering_notes.md`，记录 Windows inline Python
  JSON audit read 必须显式使用 UTF-8 encoding。

Verify:

- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`、`missing_required=[]`、
  `missing_readme_snippets=[]`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、
  `submission_package_ready=true`、`submission_handoff.passed=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`，且 `artifact_zip_audit.passed=true`、
  `submission_handoff_audit.passed=true`；
- 首次直接读取 latest JSON 使用 Windows 默认 GBK 解码失败；已用 UTF-8 重读并确认
  上述字段成立。该问题是本地检查命令的编码问题，不是实验或 artifact 问题；
- 重新生成 paper tables / IEEE draft 未造成 tracked paper output 漂移；当前
  tracked diff 仅为本轮 `current_plan_zh.md` 和 engineering notes 记录。

## 2026-06-18 advisor-facing workload response packet

Inspect:

- `docs/experiments/evp7_next_decision_packet_20260618.md` 的 Option A 允许
  `response-to-advisor summary`；
- 当前 README、INDEX、paper draft 和 submission checklist 已有 workload
  ledger，但缺少一个中文短文档，直接回应“工作量是否够”和“当前能投什么 claim”；
- 当前默认边界仍是 no-API paper-submission maintenance，不启动第二模型、
  30-50 bug 扩量或新 verifier design。

Plan:

1. 新增中文 advisor/workload response packet，总结当前 structural pipeline、
   real G5 run、验证/审计/论文 artifact 工作量；
2. 明确论文可写 claim、不能写 claim、为什么不是“只跑四组 prompt”；
3. 同步 README、INDEX、current project state 和 submission checklist 的入口；
4. 不改实验数据、不重建 evidence packets、不调用 API、不扩 cohort、不补
   E1/E3/E5。

Acceptance:

- 新文档能独立说明当前工作量和投稿边界；
- 所有新增表述保持 bounded four-anchor EVP-7 pilot，不引入 scale-generalized、
  LLM-over-tool-only、E6-strict 或 full-ladder claim；
- paper readiness / local quality / diff check 通过。

Execute:

- 已新增 `docs/paper/advisor_workload_response_zh.md`；
- 已同步 README、docs/INDEX、current project state、submission checklist 和
  submission handoff 入口；
- 文档明确当前工作量包括 21/98/392 structural pipeline、294 tool-only
  decisions、20/94/376 real G5 run、statistics、qualitative cases、
  claim-boundary audit 和 artifact readiness；
- 文档明确不能声称 scale-generalized、LLM-over-tool-only、E6 strict
  superiority、external billing equivalence 或 current E1/E3/E5 full ladder。

Verify:

- `rg -n "advisor_workload_response_zh|21 real-bug tasks|98 candidate patches|392|294 deterministic|376|scale-generalized|LLM 明确优于|E1/E3/E5|prompt comparison|bounded EVP-7" ...`
  确认新文档和入口均可检索，且 overclaim 关键词只作为禁止主张出现；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=301`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`、`missing_required=[]`、
  `missing_readme_snippets=[]`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`submission_package_ready=true`、
  `submission_handoff.passed=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`、`artifact_zip_audit.passed=true`、
  `submission_handoff_audit.passed=true`；
- 直接检查 ZIP 确认 `docs/paper/advisor_workload_response_zh.md` 已包含在匿名
  artifact 中。

Commit / Git Sync:

- 本轮只暂存 advisor/workload packet 及其入口文档；
- staged diff check 与敏感信息扫描通过；
- 由于当前分支已有连续 GitHub 网络层同步失败记录，本轮不再反复重试
  `git push origin main`，只保留本地提交并在最终状态中报告 ahead 数。

## 2026-06-18 advisor packet artifact required gate

Inspect:

- `docs/paper/advisor_workload_response_zh.md` 已被创建并包含在当前匿名 ZIP 中；
- `scripts/audit_anonymous_artifact.py` 的 required file / README snippet 清单
  尚未显式要求 advisor/workload packet；
- `scripts/prepare_anonymous_artifact.py` 生成的 embedded `ARTIFACT_README.md`
  尚未指向该文档；
- 若只依赖通用 docs 打包规则，后续 artifact 可以在缺失该说明文档时仍通过
  audit，不符合当前 Option A 的工作量呈现强化目标。

Plan:

1. 将 `docs/paper/advisor_workload_response_zh.md` 加入 anonymous artifact
   required files；
2. 将该路径加入 embedded `ARTIFACT_README.md` 的 paper package 说明；
3. 将该路径加入 artifact README required snippets；
4. 同步 anonymous artifact 文档、README/INDEX 或 engineering notes 中必要的入口；
5. 重建 ZIP 并运行 artifact audit、paper readiness、local quality gate；
6. 不调用 API、不修改实验数据、不扩 cohort、不补 E1/E3/E5。

Acceptance:

- artifact audit 在缺少 advisor packet 时会失败；
- 当前 rebuilt artifact audit 通过，且 ZIP 中包含 advisor packet；
- paper readiness / local quality / diff check 通过。

Execute:

- 已更新 `scripts/audit_anonymous_artifact.py`：
  - required files 新增 `docs/paper/advisor_workload_response_zh.md`；
  - required `ARTIFACT_README.md` snippets 新增该路径；
- 已更新 `scripts/prepare_anonymous_artifact.py`，使 generated
  `ARTIFACT_README.md` 明确指向 advisor-facing workload response；
- 已同步 README、docs/INDEX、anonymous artifact 文档、submission checklist、
  submission handoff 和 engineering notes。

Verify:

- `python -m py_compile scripts\audit_anonymous_artifact.py scripts\prepare_anonymous_artifact.py scripts\run_local_quality_gate.py scripts\audit_paper_readiness.py`
  通过；
- `rg -n "advisor_workload_response_zh|advisor-facing workload response|advisor packet artifact gate" ...`
  确认脚本、README、INDEX、artifact 文档、engineering notes 和 current plan 均有入口；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=301`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`、`missing_required=[]`、
  `missing_readme_snippets=[]`；
- 负向审计：构造删除 `docs/paper/advisor_workload_response_zh.md` 的临时 ZIP 后，
  `audit_anonymous_artifact.py` 返回 `safe=false`，且
  `missing_required=["docs/paper/advisor_workload_response_zh.md"]`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`submission_package_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- 直接检查 ZIP 确认 advisor packet 在 ZIP 中，且 embedded `ARTIFACT_README.md`
  包含该路径。

## 2026-06-18 paper readiness checks submission handoff

Inspect:

- `scripts/audit_submission_handoff.py` 已进入 local quality gate 和 anonymous
  artifact required checks；
- `scripts/audit_paper_readiness.py` 仍只报告 paper/result readiness，没有把
  submission handoff boundary 显式纳入 paper-readiness 输出；
- 为避免“claim ready”和“submission package ready”混淆，应新增独立字段，而不是
  改写既有 `current_result_claim_ready` 定义。

Plan:

1. 在 `audit_paper_readiness.py` 中复用 `audit_submission_handoff.py` 的
   `audit_handoff`；
2. required docs 增加 `submission_checklist` 和 `submission_handoff`；
3. 输出独立 `submission_handoff` 子状态和 `submission_package_ready` 字段；
4. 不改变 `current_result_claim_ready`、`evp7_bounded_pilot_claim_ready` 或
   prompt-only/tool-augmented claim 逻辑；
5. 同步 README、INDEX、submission checklist 和 engineering notes。

Execute:

- 已更新 `scripts/audit_paper_readiness.py`：
  - 兼容脚本运行和模块运行的 `audit_submission_handoff` import；
  - required docs 新增 submission checklist / handoff；
  - 输出 `submission_handoff` 子状态；
  - 输出 `submission_package_ready`，其含义为 current result claim readiness
    且 handoff boundary passed；
  - Markdown report 新增 `Submission Handoff` 小节；
- 已同步 README、INDEX、submission checklist 和 engineering notes。

Verify:

- `python -m py_compile scripts\audit_paper_readiness.py scripts\audit_submission_handoff.py`
  通过；
- 首次直接运行发现 `scripts.audit_submission_handoff` 在脚本模式下不能解析；
  已增加 fallback import；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，输出 `submission_handoff.passed=true`、
  `submission_package_ready=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=300`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`、`missing_required=[]`、
  `missing_readme_snippets=[]`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- 直接读取 latest JSON 确认：
  - `paper_current_result_claim_ready=true`；
  - `paper_submission_package_ready=true`；
  - `paper_submission_handoff_passed=true`；
  - `local_quality_handoff_passed=true`；
  - `artifact_safe=true`；
- `git diff --check` 通过。

Commit / Git Sync:

- 已只暂存本轮相关 6 个文件，并运行 staged diff check 与敏感信息扫描；
- 已创建本地提交 `f6d5a9d Add submission package readiness gate`；
- `git push origin main` 失败：`Error in the HTTP2 framing layer`；
- `git -c http.version=HTTP/1.1 push origin main` 重试失败：无法连接
  `github.com:443`；
- 按用户规则，GitHub 频繁同步失败时不继续阻塞后续任务；当前本地 `main`
  保留未推送提交。

## 2026-06-18 submission handoff semantic audit

Inspect:

- 当前 `main` 与 `origin/main` 同步，工作区干净；
- `docs/artifact/submission_handoff_20260618.md` 已进入 anonymous artifact
  required files；
- 但目前 artifact audit 只能证明 handoff 被打包，不能证明 handoff 内容仍保留
  four-anchor counts、默认 no-API continuation 和 forbidden-action boundary；
- 下一步应在 no-API local quality gate 中加入 handoff semantic audit，防止后续
  文案漂移。

Plan:

1. 新增 `scripts/audit_submission_handoff.py`，只检查 tracked handoff 文本和
   next-decision packet 存在性；
2. 将该 audit 接入 `scripts/run_local_quality_gate.py`；
3. 将该脚本和命令纳入 anonymous artifact required files/snippets 与 generated
   `ARTIFACT_README.md`；
4. 同步 README、INDEX、submission checklist、anonymous artifact 文档和
   engineering notes；
5. 不调用 API、不扩 bug、不修改 evidence packets 或实验数据。

Execute:

- 已新增 `scripts/audit_submission_handoff.py`；
- 已将 submission handoff audit 接入 `scripts/run_local_quality_gate.py`；
- 已将 `scripts/audit_submission_handoff.py` 加入 anonymous artifact required
  files/snippets；
- 已更新 `scripts/prepare_anonymous_artifact.py`，在 generated
  `ARTIFACT_README.md` 的 local quality/readiness block 中写入 handoff audit
  命令；
- 已同步 README、INDEX、submission checklist、anonymous artifact 文档和
  engineering notes。

Verify:

- `python -m py_compile scripts\audit_submission_handoff.py scripts\run_local_quality_gate.py scripts\audit_anonymous_artifact.py scripts\prepare_anonymous_artifact.py`
  通过；
- 首次 `python scripts\audit_submission_handoff.py ...` 暴露规则问题：
  forbidden phrase `LLM beats deterministic tool-only baselines` 会误伤 handoff
  中正确的 `no claim that ...` 禁止动作；已改为只禁止正向支持表述；
- 修复后 `python scripts\audit_submission_handoff.py --out-json outputs\submission_handoff_audit\latest.json --out-md outputs\submission_handoff_audit\latest.md`
  通过；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，新增 audit script 后 `file_count=300`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过 current bounded EVP-7 claim readiness；保留的唯一 blocker 仍是旧
  prompt-only positive claim 的 `stop_or_redesign`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，且已覆盖 submission handoff audit；
- `git diff --check` 通过。

## 2026-06-18 artifact audit requires submission handoff

Inspect:

- 当前 `main` 与 `origin/main` 同步，工作区干净；
- `docs/artifact/submission_handoff_20260618.md` 已被新增并纳入 artifact
  文档入口；
- 但 `scripts/audit_anonymous_artifact.py` 的 required file/snippet 清单尚未把
  submission handoff 设为强制项；
- `scripts/prepare_anonymous_artifact.py` 生成的 embedded `ARTIFACT_README.md`
  也尚未显式提到 handoff，因此不能只改 audit required snippets。

Plan:

1. 将 `docs/artifact/submission_handoff_20260618.md` 加入 anonymous artifact
   audit required files；
2. 在 generated `ARTIFACT_README.md` 中加入 handoff 入口；
3. 将 handoff 路径加入 audit required README snippets；
4. 同步 `docs/artifact/anonymous_artifact.md` 与 `docs/INDEX.md`；
5. 重新打包 ignored artifact ZIP 并运行 artifact audit；
6. 运行最小代码/质量验证，不调用 API、不扩 bug、不改实验数据。

Execute:

- 已更新 `scripts/audit_anonymous_artifact.py`：
  - required files 新增 `docs/artifact/submission_handoff_20260618.md`；
  - required README snippets 新增
    `docs/artifact/submission_handoff_20260618.md`；
- 已更新 `scripts/prepare_anonymous_artifact.py`，使 embedded
  `ARTIFACT_README.md` 明确指向 no-API submission handoff；
- 已同步 `docs/artifact/anonymous_artifact.md` 和 `docs/INDEX.md`。

Verify:

- `python -m py_compile scripts\audit_anonymous_artifact.py scripts\prepare_anonymous_artifact.py`
  通过；
- `rg -n "submission_handoff_20260618|no-API submission handoff|required files|required README|ARTIFACT_README" ...`
  确认 audit required files/snippets、generated `ARTIFACT_README.md` 和文档入口均
  包含 submission handoff；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=299`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- 直接读取 `artifacts/research95_anonymous_artifact_audit.json` 确认
  `missing_required=[]`、`missing_readme_snippets=[]`、
  `forbidden_entries=[]`、`manifest_matches_zip=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过 current bounded EVP-7 claim readiness；保留的唯一 blocker 仍是旧
  prompt-only positive claim 的 `stop_or_redesign`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过。

## 2026-06-18 no-API submission handoff refresh

Inspect:

- 当前 `main` 与 `origin/main` 同步，工作区干净；
- 最新决策包已规定：没有明确 provider/model/预算/scope 决策时，只能继续
  no-API paper-submission maintenance；
- 当前 tracked paper/artifact 文档已经记录 workload-ledger 后的 submission
  readiness，但缺少一个短 handoff 文件把最新 no-API rebuild/audit 状态集中给
  下个会话使用。

Plan:

1. 重新生成 paper tables 和 IEEE draft，确认 tracked paper outputs 无漂移；
2. 连续两遍编译 IEEE PDF，并抽查 PDF 文本中的 workload ledger 和 bounded
   EVP-7 conclusion；
3. 重建 ignored anonymous artifact ZIP，并运行 artifact audit；
4. 新增 tracked submission handoff，记录当前可提交状态、验证命令、默认下一步和
   禁止动作；
5. 同步 README、INDEX、current project state 和 submission checklist；
6. 不调用 API、不扩 bug、不补 E1/E3/E5、不改实验数据。

Execute:

- `python scripts\write_paper_tables.py` 通过；
- `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`
  通过；
- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续两遍通过，输出 7 页 PDF；
- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf - | rg -n ...`
  确认 PDF 包含 21/98/392 structural workload、20/94/376 real G5 run 和
  bounded EVP-7 conclusion；
- `python scripts\audit_paper_claim_boundary.py` 通过，`raw_output_free=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过 current bounded EVP-7 claim readiness；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  生成 299-file ignored artifact，`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- 已新增 `docs/artifact/submission_handoff_20260618.md`；
- 已同步 `README.md`、`docs/INDEX.md`、
  `docs/plans/current_project_state_zh.md` 和
  `docs/artifact/submission_checklist.md`。

Verify:

- 本轮 rebuild/audit 没有修改 tracked paper outputs；
- handoff 明确默认下一步仍是 no-API paper-submission maintenance；
- handoff 明确禁止在未确认前执行 second-model API、cohort expansion、
  E1/E3/E5 insertion 或 new verifier design run；
- `rg -n "submission_handoff_20260618|299 files|second-model API|E1/E3/E5|no-API paper-submission maintenance" ...`
  确认 README、INDEX、current project state、submission checklist、handoff 和
  current plan 均可检索到新 handoff 与禁止动作边界；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过 current bounded EVP-7 claim readiness；保留的唯一 blocker 仍是旧
  prompt-only positive claim 的 `stop_or_redesign`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过。

## 2026-06-18 no-API next-decision packet

Inspect:

- 当前 `main` 本地有 `a9e1ca9` 未推送，GitHub push 仍因 443 连接失败；
- 工作区在本轮开始时没有 tracked diff；
- 当前 paper/artifact 已通过 no-API readiness re-audit；
- 剩余实验分支包括第二模型关键锚点复现、30-50 bug 扩量和新 verifier
  design，均需要用户确认 provider/model/budget/scope 或实验边界；
- 为避免后续 agent 把普通 `continue` 误解为 API 调用或盲目扩量，需要一个
  明确的 no-API next-decision packet。

Plan:

1. 新增 no-API next-decision packet，列出可选路线、前置确认和禁止动作；
2. 同步 INDEX 和 current project state；
3. 不调用 API、不扩 bug、不改 evidence levels、不修改实验数据；
4. 验证文档可检索、paper readiness 和 local quality gate 仍通过。

Execute:

- 已新增 `docs/experiments/evp7_next_decision_packet_20260618.md`；
- 已将后续路线分为：
  - submit current four-anchor paper package；
  - second-model E0/E4/E6 key-anchor replication；
  - new 30-50 bug expansion boundary；
  - new verifier design；
- 已明确默认无决策时只能做 no-API paper-submission maintenance；
- 已同步 `docs/INDEX.md` 和 `docs/plans/current_project_state_zh.md`。

Verify:

- `rg -n "evp7_next_decision_packet_20260618|second-model|30-50|provider|model|E1/E3/E5|API"`
  覆盖 next-decision packet、INDEX、current project state 和 current plan，
  确认第二模型复现只作为需确认的 E0/E4/E6 条件路线出现；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过 final roadmap / protocol / paper framing 检查；保留的唯一 blocker 仍是
  历史 prompt-only positive claim 的 `stop_or_redesign`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过。

## 2026-06-18 final submission checklist re-audit

Inspect:

- 当前 `main` 已与 `origin/main` 同步，工作区干净；
- `bugsinpy_cookiecutter_4` 已收束为 tracked blocker policy，本地 raw builder
  失败输出已删除；
- 当前继续实验的第二模型复现、30-50 bug 扩量和新 verifier design 都需要用户
  明确确认边界；
- 当前可无歧义推进的事项是按 `docs/artifact/submission_checklist.md` 做
  no-API final submission readiness re-audit。

Plan:

1. 重新生成 paper tables 和 IEEE draft；
2. 连续两遍编译 IEEE PDF；
3. 运行 claim-boundary audit、paper readiness、anonymous artifact audit 和
   local quality gate；
4. 抽查 PDF 文本仍包含 workload ledger 和 bounded conclusion；
5. 不调用模型 API、不扩 bug、不改 evidence levels、不提交 ignored outputs 或
   artifacts。

Acceptance:

- checklist 中列出的 no-API rebuild/audit commands 均通过；
- PDF 文本抽查通过；
- 工作区只包含本轮 current_plan 审计记录；
- 若提交成功，GitHub 同步成功或明确记录同步失败。

Execute:

- 已重新运行 `python scripts\write_paper_tables.py`；
- 已重新运行 `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`；
- 已连续两遍编译 `docs/paper/ieee_submission_draft.tex` 到
  `outputs/paper_compile/ieee_submission_draft.pdf`；
- 已运行 claim-boundary audit、anonymous artifact build/audit、paper readiness
  和 local quality gate。

Verify:

- `python scripts\audit_paper_claim_boundary.py` 通过，`passed: true` 且
  `raw_output_free: true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe: true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过 current EVP-7 bounded-pilot claim readiness；保留的唯一 blocker 仍是
  历史 prompt-only positive claim 的 `stop_or_redesign`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf - | rg ...`
  确认 PDF 包含 workload ledger、20 tasks / 94 candidates 和 bounded EVP-7
  conclusion；
- `git diff --check` 通过。

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

## 2026-06-18 submission artifact readiness refresh

Inspect:

- 最新 commit `acfe037` 已完成 paper workload presentation reinforcement；
- 当前 `docs/paper/ieee_submission_draft.tex` 已更新，但 ignored PDF
  `outputs/paper_compile/ieee_submission_draft.pdf` 需要用最新 draft 重新编译；
- 当前继续实验的第二模型复现、30-50 bug 扩量或新 verifier design 都需要
  用户确认边界，不是本轮默认动作；
- `cookiecutter_4` 的未提交 P2P scope 残留显示 dependency/command/timeout
  blocker，不构成 admission evidence，本轮不继续扩量；
- 本轮目标是 no-API submission readiness：编译最新 IEEE PDF，必要时重建并
  审计 ignored anonymous artifact。

Plan:

1. 重新生成 paper tables 和 IEEE draft，确保 script outputs 与 tracked summaries
   一致；
2. 使用最新 `docs/paper/ieee_submission_draft.tex` 连续编译 IEEE PDF；
3. 用 `pdftotext` 或可用文本抽查确认 workload ledger 和 bounded conclusion
   进入 PDF；
4. 构建 ignored anonymous artifact ZIP，并运行 artifact audit；
5. 同步 submission checklist、README/INDEX 或 engineering notes 中需要更新的
   no-API readiness 状态；
6. 不调用模型 API、不扩 bug、不修改 E0/E2/E4/E6 evidence levels、不提交
   `outputs/` 或 `artifacts/`。

Acceptance:

- IEEE PDF 从最新 LaTeX draft 成功编译；
- PDF 文本包含 `Workload at a Glance` / workload ledger 和 bounded EVP-7
  conclusion；
- anonymous artifact audit 通过；
- paper readiness / local quality / diff check 通过；
- 本轮提交只包含文档和生成器/清单更新，不纳入 `cookiecutter_4` 残留。

Execute:

- 已重新运行 `python scripts\write_paper_tables.py` 和
  `python scripts\write_ieee_latex_draft.py`；
- 已连续两遍编译 `docs/paper/ieee_submission_draft.tex`，输出
  `outputs/paper_compile/ieee_submission_draft.pdf`，共 7 页；
- 已用 `pdftotext` 抽查 PDF，确认 structural workload ledger、20/94/376
  real G5 run 和 bounded EVP-7 conclusion 进入最新 PDF；
- 已重建 ignored artifact ZIP：
  `artifacts/research95_anonymous_artifact.zip`；
- 已更新 `docs/artifact/submission_checklist.md`、
  `docs/artifact/anonymous_artifact.md` 和 `docs/INDEX.md`，记录
  2026-06-18 workload-ledger 后的 PDF/artifact readiness。

Verify:

- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续两遍通过；第二遍无 unresolved references；
- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf - | rg ...`
  确认 PDF 包含 workload ledger 和 bounded conclusion 关键文本；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe: true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过 current EVP-7 bounded-pilot claim readiness；保留的唯一 blocker 仍是
  历史 prompt-only positive claim 的 `stop_or_redesign`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过。

## 2026-06-18 non-conflicting reinforcement plan wording audit

Inspect:

- 当前 canonical final roadmap 已包含“工作量呈现强化”和“第二模型关键锚点
  复现”两条非冲突补强路线；
- 现有边界仍是 EVP-7 four-anchor E0/E2/E4/E6 pilot，不补 E1/E3/E5，不写
  full-ladder claim；
- `docs/experiments/evp7_next_decision_packet_20260618.md` 已把第二模型复现
  写成需要用户确认 provider、model、预算、scope 和停止条件的 Option B；
- 本轮检查发现一个措辞冲突：final roadmap 的工作量呈现说明把当前 pipeline
  写成“不带 hidden evaluator”的形式，这与 hidden-evaluator separation 设计
  相反；
- README 中原先的 Git 同步状态已经过期；当前应以
  `git status --short --branch` 为准，并承认 GitHub push failure 后可能
  local-only 继续。

Plan:

1. 保留最终路线中的两条非冲突补强路线：
   - 默认优先：工作量呈现强化，不调用 API、不扩 bug、不改 E0/E2/E4/E6；
   - 条件执行：第二模型关键锚点复现，只覆盖 E0/E4/E6，且必须先由用户确认
     provider、model、预算、scope 和停止条件；
2. 修正 final roadmap 中与 hidden-evaluator separation 冲突的措辞；
3. 修正 README 的 Git 同步状态，避免与当前 ahead/push-failure 边界冲突；
4. 同步工程经验记录；
5. 不修改实验数据、不生成 packets、不调用模型 API、不改变论文 claim。

Acceptance:

- final roadmap 明确“工作量呈现”是默认 no-API 路线；
- second-model replication 仍是需确认的 E0/E4/E6 条件路线；
- 文档不再把当前主 pipeline 写成不带 hidden evaluator 的形式；
- README 不再声称本地 main 一定与 origin/main 同步；
- paper readiness / local quality / diff check 通过。

Execute:

- 已将 `docs/plans/final_paper_roadmap_zh.md` 中的工作量呈现表述改为
  “带 hidden-evaluator separation 的 candidate patch verification
  pipeline”；
- 已将 README 的 Git 状态说明改为以 `git status --short --branch` 为准，并
  记录 2026-06-18 GitHub push failure 后允许 local-only 继续；
- 已在 `docs/experience/engineering_notes.md` 记录非冲突补强路线的措辞和同步
  状态经验。

Verify:

- targeted `rg` checks 确认 final roadmap 和 README 不再保留旧的
  hidden-evaluator / Git 同步冲突表述；
- `rg -n "工作量呈现强化|第二模型关键锚点复现|provider、model、预算、scope|hidden-evaluator separation" ...`
  确认默认工作量呈现和条件第二模型复现边界仍存在；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过 current EVP-7 bounded-pilot claim readiness；保留的唯一 blocker 仍是
  历史 prompt-only positive claim 的 `stop_or_redesign`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过。

## 2026-06-18 submission freeze-candidate packet

Inspect:

- 当前 `git status --short --branch` 为 `main...origin/main [ahead 7]`，
  工作区在本轮开始时干净；此前 GitHub push 已频繁失败，当前可 local-only
  继续；
- `docs/experiments/evp7_next_decision_packet_20260618.md` 明确：没有新决策时
  只能做 no-API paper-submission maintenance；
- 当前 handoff/checklist 已说明需要确认 target venue/format 与是否冻结当前
  7-page IEEE PDF，但缺少单独的 submission freeze-candidate packet；
- 本轮不调用 API、不扩 bug、不补 E1/E3/E5、不修改 evidence packets、不把当前
  候选包标成 final freeze。

Plan:

1. 新增 tracked no-API `docs/artifact/submission_freeze_candidate_20260618.md`；
2. 记录当前可冻结候选状态：bounded EVP-7 claim、21/98/392 structural
   pipeline、20/94/376 real G5 run、7-page IEEE PDF target、artifact
   readiness、advisor workload packet；
3. 明确仍需用户确认：target venue/format、是否冻结当前 7-page IEEE PDF、
   是否保持 no-API/no-expansion 边界、是否稍后重试 GitHub sync；
4. 将该 packet 纳入 README/INDEX/current project state/checklist/handoff/
   anonymous artifact 文档；
5. 将该 packet 加入 `audit_anonymous_artifact.py` required files/snippets 和
   `audit_paper_readiness.py` required docs；
6. 重建 ignored anonymous artifact 并运行 paper readiness、artifact audit、
   local quality、diff check。

Acceptance:

- freeze-candidate packet 存在并明确不是最终冻结版；
- paper readiness 的 required docs 包含该 packet；
- anonymous artifact audit 强制包含该 packet 和 embedded README entry；
- readiness/artifact/local gates 均通过；
- 本轮提交只包含相关 tracked 文档和 gate 脚本，不提交 ignored outputs/artifacts。

Execute:

- 已新增 `docs/artifact/submission_freeze_candidate_20260618.md`，记录当前
  paper/artifact package 是 freeze candidate 而非 final freeze；
- 已同步 README、docs/INDEX、current project state、submission checklist、
  submission handoff、anonymous artifact 文档和 engineering notes；
- 已将 freeze-candidate packet 加入 `scripts/audit_anonymous_artifact.py`
  required files/snippets；
- 已更新 `scripts/prepare_anonymous_artifact.py`，使 embedded
  `ARTIFACT_README.md` 指向 freeze-candidate packet；
- 已将 freeze-candidate packet 加入 `scripts/audit_paper_readiness.py`
  required docs。

Verify:

- `python -m py_compile scripts\audit_paper_readiness.py scripts\audit_anonymous_artifact.py scripts\prepare_anonymous_artifact.py scripts\run_local_quality_gate.py`
  通过；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=302`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`required_docs.submission_freeze_candidate.exists=true`、
  `submission_package_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- direct JSON/ZIP inspection 确认 `manifest_file_count=302`、
  `missing_required=[]`、`missing_readme_snippets=[]`、
  `zip_has_freeze_packet=true`。

## 2026-06-18 submission freeze-candidate semantic audit

Inspect:

- `docs/artifact/submission_freeze_candidate_20260618.md` 已纳入 artifact
  和 paper readiness required docs；
- 但当前只有存在性/packaging gate，尚无语义 gate 防止该 packet 漂移成
  final freeze、API 授权、扩量授权或 E1/E3/E5 插入；
- 现有 `scripts/audit_submission_handoff.py` 已提供 no-API handoff semantic
  audit 模式，可以用最短路径为 freeze-candidate packet 建立同类审计；
- 本轮检查还发现 freeze-candidate 文档中的 artifact file count 会随提交包
  required 文件增长而漂移；纳入该 packet 和语义审计脚本后最新 manifest
  file count 为 303。

Plan:

1. 新增 `scripts/audit_submission_freeze_candidate.py`，只检查 tracked packet
   的语义边界，不调用 API、不读 ignored raw outputs；
2. 修正 freeze-candidate 文档中的 artifact file count 为 303；
3. 将新审计接入 `scripts/run_local_quality_gate.py` 和 anonymous artifact
   required files/snippets；
4. 在 paper readiness 中调用该审计，并让 `submission_package_ready` 同时要求
   freeze-candidate semantic audit 通过；
5. 同步 README、INDEX、artifact/checklist/handoff/current state/engineering
   notes；
6. 用正向 gate 和临时破坏文档的负向检查验证审计有效。

Acceptance:

- freeze-candidate semantic audit 通过正向文档；
- 临时把 packet 改成 final freeze 或 API 授权时，审计失败；
- local quality gate 覆盖该审计；
- paper readiness 的 `submission_package_ready` 依赖该审计；
- anonymous artifact 必须包含该审计脚本和 README 命令；
- artifact/readiness/local gates 均通过。

Execute:

- 已新增 `scripts/audit_submission_freeze_candidate.py`；
- 已将 freeze-candidate packet 的 artifact file count 从旧 301/302 边界更新为
  当前 303；
- 已将 freeze-candidate audit 接入 `scripts/run_local_quality_gate.py`；
- 已将 freeze-candidate audit 接入 `scripts/audit_paper_readiness.py`，并使
  `submission_package_ready` 依赖该 semantic audit；
- 已将 `scripts/audit_submission_freeze_candidate.py` 和对应命令加入 anonymous
  artifact required files/snippets 与 generated `ARTIFACT_README.md`；
- 已同步 README、INDEX、current project state、submission checklist、
  submission handoff、anonymous artifact 文档和 engineering notes。

Verify:

- `python scripts\audit_submission_freeze_candidate.py --out-json outputs\submission_freeze_candidate_audit\latest.json --out-md outputs\submission_freeze_candidate_audit\latest.md`
  通过；
- 负向检查：临时复制 freeze packet 并改为 final freeze/API authorization 后，
  `audit_submission_freeze_candidate.py` 按预期失败，临时文件已删除；
- `python -m py_compile scripts\audit_submission_freeze_candidate.py scripts\audit_paper_readiness.py scripts\audit_anonymous_artifact.py scripts\prepare_anonymous_artifact.py scripts\run_local_quality_gate.py`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`submission_freeze_candidate.passed=true` 且
  `submission_package_ready=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，且 `submission_freeze_candidate_audit.passed=true`；
- `git diff --check` 通过；
- direct JSON/ZIP inspection 确认 `manifest_file_count=303`、
  `zip_has_freeze_audit_script=true`、`zip_has_freeze_packet=true`。

## 2026-06-18 current plan freeze-candidate chronology repair

Inspect:

- 当前 `current_plan_zh.md` 中 `submission freeze-candidate packet` section
  的 Execute/Verify 记录被后续 semantic audit section 隔开；
- 该记录还保留 `manifest_file_count=302`，这是新增 semantic audit 脚本前的
  历史验证结果，但放在 semantic audit 之后会误导为当前最新 artifact 状态；
- 当前最新 artifact 状态应以 semantic audit section 的 `file_count=303` 为准。

Plan:

1. 将 freeze-candidate packet 的 Execute/Verify 记录移回该 section 内；
2. 将该 section 的计划文字从具体 `301-file` 改为不易漂移的 artifact
   readiness 边界；
3. 保留 semantic audit section 的最新 `303` artifact 状态；
4. 重建 ignored anonymous artifact，并重新运行 artifact/readiness/local gates；
5. 不调用 API、不扩 bug、不改 evidence packets。

Acceptance:

- `current_plan_zh.md` 的 freeze-candidate packet 与 semantic audit sections
  顺序清晰；
- 最新 artifact/readiness/local gates 仍通过；
- 提交只包含本轮文档顺序修复和必要的 regenerated ignored artifact state。

Execute:

- 已将 `submission freeze-candidate packet` section 的 Execute/Verify 记录移回
  该 section 内；
- 已将该 section 中易漂移的 `301-file artifact readiness` 改为
  `artifact readiness`；
- 已保留后续 semantic audit section 的最新 `file_count=303` / audit-script
  packaging 状态。

Verify:

- `git diff -- docs\plans\current_plan_zh.md` 确认 freeze-candidate packet
  Execute/Verify 不再落在 semantic audit section 之后；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；

- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- direct JSON/ZIP inspection 确认 `manifest_file_count=303`、
  `paper_submission_package_ready=true`、`artifact_safe=true`、
  `local_quality_passed=true`、`zip_has_freeze_audit_script=true`、
  `zip_has_freeze_packet=true`。

## 2026-06-18 non-conflicting reinforcement route recording

Inspect:

- 用户要求把“第二模型关键层级复现”或“工作量呈现”写入计划，并且不能与
  现有路线互相冲突；
- canonical final roadmap 已有 `18.4.1 当前论文的非冲突补强路线`，但当前
  计划仍需要把这次决策边界记录为本轮可执行约束；
- 当前 EVP-7 paper-facing route 仍是 four-anchor E0/E2/E4/E6 bounded pilot；
- 当前 freeze-candidate / submission handoff 边界仍禁止未确认的 API 调用、
  cohort expansion、E1/E3/E5 insertion 和 full-ladder claim。

Plan:

1. 将 **工作量呈现强化** 记录为默认优先路线：不调用 API、不扩 bug、不改变
   E0/E2/E4/E6 evidence levels；只把已完成的 admission、candidate
   construction、F2P/P2P validation、evidence packets、LLM review、tool-only
   baseline、qualitative cases、claim traceability 和 artifact audit 写清楚；
2. 将 **第二模型关键层级复现** 记录为条件补强路线：只覆盖关键锚点
   `E0`、`E4`、`E6`，默认沿用当前 paper-facing 20-task / 94-candidate
   cohort；
3. 第二模型路线必须先由用户确认 provider、model、预算、smoke scope、
   full-run permission 和停止条件，并通过 no-API preflight 后才能调用模型；
4. 两条路线都不能重开 E1/E3/E5、盲目扩 bug、新 verifier design，或把当前
   结果写成 scale-generalized / LLM beats tool-only claim；
5. 本轮只做计划记录和一致性验证，不修改实验数据、不生成 packets、不调用 API。

Acceptance:

- `current_plan_zh.md` 明确默认 no-API 工作量呈现路线和条件 second-model
  E0/E4/E6 key-anchor replication 路线；
- 该记录不覆盖 final roadmap、next-decision packet、freeze-candidate packet
  或 submission handoff 中的既有边界；
- targeted 文档检查确认没有引入 E1/E3/E5、full-ladder、API 自动执行或
  LLM 优于 tool-only 的新 claim；
- readiness/artifact/local gates 仍通过。

Execute:

- 已在 `current_plan_zh.md` 追加本轮非冲突补强路线记录；
- 已将“工作量呈现强化”写为默认 no-API 路线；
- 已将“第二模型关键层级复现”写为条件路线：仅 `E0`/`E4`/`E6` key anchors，
  默认沿用当前 paper-facing 20-task / 94-candidate cohort，并要求用户先确认
  provider、model、预算、smoke scope、full-run permission 和停止条件。

Verify:

- targeted `rg` 检查确认 final roadmap、next-decision packet 和 current plan
  都保留 four-anchor / no-E1/E3/E5 / user-confirmed second-model boundary；
- `git diff --check` 通过；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`submission_package_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

## 2026-06-18 no-API paper package rebuild after reinforcement routing

Inspect:

- 当前工作区干净，`main...origin/main [ahead 10]`；
- `docs/experiments/evp7_next_decision_packet_20260618.md` 指定无新决策时只继续
  Option A no-API paper-submission maintenance；
- 上一轮已把“工作量呈现强化”和“第二模型关键层级复现”写入 current plan；
- 当前仍没有用户确认 second-model provider/model/budget/scope/stop rule，也没有
  venue/format 或 final PDF freeze confirmation。

Plan:

1. 重新生成 paper tables、paper figures 和 IEEE LaTeX draft；
2. 连续两遍编译 `docs/paper/ieee_submission_draft.tex` 到 ignored
   `outputs/paper_compile/ieee_submission_draft.pdf`；
3. 抽查 PDF 文本，确认 workload ledger、20/94/376 real G5 run、
   21/98/392 structural pipeline 和 bounded EVP-7 conclusion 仍进入 PDF；
4. 重建 anonymous artifact 并运行 artifact/readiness/local gates；
5. 不调用模型 API、不扩 bug、不补 E1/E3/E5、不修改 evidence packets、不把
   freeze-candidate 写成 final freeze。

Acceptance:

- 表格、图、IEEE draft 和 PDF 可从 tracked inputs 重建；
- PDF 文本包含工作量呈现和 bounded claim 的关键文本；
- artifact/readiness/local gates 通过；
- 若 tracked generated paper artifacts 有变化，只提交本轮相关文件。

Execute:

- 已重新运行 `python scripts\write_paper_tables.py --out-md docs\paper\generated_tables.md --out-tex docs\paper\generated_tables.tex`；
- 已重新运行 `python scripts\generate_paper_figures.py`，输出 7 张 paper figures
  的 PDF/SVG/PNG；
- 已重新运行 `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`；
- 已连续两遍编译 `docs/paper/ieee_submission_draft.tex` 到
  `outputs/paper_compile/ieee_submission_draft.pdf`；
- 本轮 paper generation 未造成 tracked generated paper artifacts 漂移，除本
  current plan 记录外无 tracked paper diff。

Verify:

- `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`
  连续两遍通过，输出 7 页 PDF；
- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf - | rg -n ...`
  确认 PDF 包含 structural/no-API `21 tasks / 98 candidates / 392`
  workload、paper-facing `20 tasks / 94 candidates / 376` real G5 run、
  `bounded single-model` 和 `not scale-generalized` 边界；
- `pdfinfo outputs\paper_compile\ieee_submission_draft.pdf` 确认 `Pages: 7`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git diff --check` 通过。

## 2026-06-18 submission checklist latest-verification refresh

Inspect:

- 当前工作区干净，`main...origin/main [ahead 11]`；
- 上一轮已完成 reinforcement-routing 后的 no-API paper package rebuild；
- `docs/artifact/submission_checklist.md` 的 `Latest Local Verification` 仍写成
  `after the advisor workload packet artifact gate`，没有反映最新 PDF/artifact
  rebuild 和 freeze-candidate semantic gate；
- `docs/INDEX.md` 对 checklist 的说明仍提到 `after the workload-ledger refresh`，
  容易让后续 agent 低估最近的 no-API submission package maintenance。

Plan:

1. 刷新 `docs/artifact/submission_checklist.md` 的 latest local verification
   段落，使其指向最新 no-API paper package rebuild；
2. 同步 `docs/INDEX.md` 中 checklist 的说明，去掉过期的 workload-ledger-only
   口径；
3. 在 `docs/experience/engineering_notes.md` 记录该类 submission checklist
   状态漂移的处理经验；
4. 不修改实验数据、不重建 evidence packets、不调用 API、不把 freeze-candidate
   写成 final freeze；
5. 运行最小文档检索、paper readiness、artifact audit、local quality 和 diff
   checks。

Acceptance:

- checklist latest local verification 反映最新 no-API rebuild、7-page PDF、
  303-file artifact、handoff/freeze semantic gates；
- INDEX 对 checklist 的说明不再停留在 workload-ledger refresh；
- engineering notes 记录状态字段需要跟随提交包 rebuild 更新；
- readiness/artifact/local gates 仍通过。

Execute:

- 已刷新 `docs/artifact/submission_checklist.md` 的 Latest Local Verification，
  改为记录 reinforcement-route clarification 后的 no-API paper package rebuild；
- 已同步 `docs/INDEX.md` 中 submission checklist 的说明，改为 latest local
  PDF/artifact verification after the no-API paper package rebuild；
- 已在 `docs/experience/engineering_notes.md` 增加 submission checklist latest
  verification drift 经验记录。

Verify:

- targeted `rg` 检查确认 checklist/INDEX/engineering notes 使用最新 no-API
  paper package rebuild 口径；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- direct JSON/ZIP inspection 确认 `manifest_file_count=303`、
  `paper_submission_package_ready=true`、`artifact_safe=true`、
  `local_quality_passed=true`、`zip_has_submission_checklist=true`、
  `zip_has_current_plan=true`。

## 2026-06-18 submission handoff latest-run refresh

Inspect:

- 当前工作区干净，`main...origin/main [ahead 12]`；
- `docs/artifact/submission_handoff_20260618.md` 的 semantic audit 通过，但
  `Latest No-API Maintenance Run` 仍未记录 reinforcement-route 后的
  `generate_paper_figures.py` 和 submission checklist latest-verification refresh；
- handoff 是新会话/下一个 agent 的入口之一，latest-run 细节漂移会降低交接
  可信度，但不影响当前实验数据或 claim 本身。

Plan:

1. 刷新 `docs/artifact/submission_handoff_20260618.md` 的 latest no-API
   maintenance command/result bullets；
2. 在 `docs/experience/engineering_notes.md` 记录 handoff latest-run drift
   经验；
3. 保持 handoff semantic audit 所需 no-API / no-expansion / no-E1/E3/E5 边界；
4. 不修改实验数据、不重建 evidence packets、不调用 API、不把 freeze-candidate
   写成 final freeze；
5. 运行 handoff audit、paper readiness、artifact audit、local quality 和 diff
   checks。

Acceptance:

- handoff latest maintenance run 明确包含 paper figures、7-page PDF、303-file
  artifact、submission checklist refresh 和 freeze-candidate semantic gate；
- handoff semantic audit 仍通过；
- readiness/artifact/local gates 仍通过。

Execute:

- 已将 `python scripts\generate_paper_figures.py` 加入
  `docs/artifact/submission_handoff_20260618.md` 的 latest maintenance command
  block；
- 已在 handoff observed results 中记录 7 张 paper figures 的 PDF/SVG/PNG
  rebuild 和 submission checklist latest local verification refresh；
- 已在 `docs/experience/engineering_notes.md` 增加 submission handoff
  latest-run drift 经验记录。

Verify:

- targeted `rg` 检查确认 handoff 包含 figure regeneration、checklist refresh
  和 no-API/no-expansion/no-E1/E3/E5 boundaries；
- `python scripts\audit_submission_handoff.py --out-json outputs\submission_handoff_audit\latest.json --out-md outputs\submission_handoff_audit\latest.md`
  通过，`passed=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`、
  `submission_handoff.passed=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true` 且 `submission_handoff_audit.passed=true`；
- direct JSON/ZIP inspection 确认 `manifest_file_count=303`、
  `paper_submission_package_ready=true`、`artifact_safe=true`、
  `local_quality_passed=true`、`zip_has_submission_handoff=true`、
  `zip_has_current_plan=true`。

## 2026-06-18 submission rebuild-command and artifact-audit refresh

Inspect:

- 当前工作区干净，`main...origin/main [ahead 13]`；
- `docs/artifact/submission_checklist.md` 的 Rebuild Commands 仍缺少
  `python scripts\generate_paper_figures.py`，但最新 no-API rebuild 已重新生成
  7 张 paper figures；
- `docs/artifact/anonymous_artifact.md` 的 Current Audit 仍写成
  `after the freeze-candidate semantic audit gate`，没有反映后续 no-API paper
  package rebuild、checklist refresh 和 handoff refresh；
- 这些是提交包维护记录漂移，不改变实验数据或 paper claim。

Plan:

1. 将 `generate_paper_figures.py` 加入 submission checklist rebuild commands；
2. 刷新 `anonymous_artifact.md` 的 Current Audit 口径，指向最新 no-API paper
   package rebuild / handoff refresh；
3. 在 engineering notes 记录 rebuild-command / artifact-current-audit drift；
4. 不调用 API、不扩 bug、不补 E1/E3/E5、不重建 evidence packets；
5. 运行 targeted checks、paper readiness、artifact audit、local quality 和 diff
   checks。

Acceptance:

- checklist rebuild commands 能完整复现 tables、figures、IEEE draft 和 PDF；
- anonymous artifact current audit 不再停留在旧 freeze-candidate-only gate；
- readiness/artifact/local gates 仍通过。

Execute:

- 已将 `python scripts\generate_paper_figures.py` 加入
  `docs/artifact/submission_checklist.md` 的 Rebuild Commands；
- 已刷新 `docs/artifact/anonymous_artifact.md` 的 Current Audit 口径，改为
  no-API paper package rebuild、submission checklist refresh 和 submission
  handoff refresh 后的 ZIP audit；
- 已在 `docs/experience/engineering_notes.md` 增加 submission rebuild-command
  drift 经验记录。

Verify:

- targeted `rg` 检查确认 checklist rebuild commands 包含
  `generate_paper_figures.py`，anonymous artifact Current Audit 指向最新 no-API
  rebuild/handoff refresh；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- direct JSON/ZIP inspection 确认 `manifest_file_count=303`、
  `paper_submission_package_ready=true`、`artifact_safe=true`、
  `local_quality_passed=true`、`zip_has_anonymous_artifact_doc=true`、
  `zip_has_submission_checklist=true`、`zip_has_current_plan=true`。

## 2026-06-18 no-API submission maintenance continuation

Inspect:

- 当前工作区干净，`main...origin/main [ahead 14]`；
- `docs/experiments/evp7_next_decision_packet_20260618.md` 指定无明确新决策时，
  只能继续 no-API paper-submission maintenance；
- 当前未获得 second-model provider/model/budget/scope/stop rule 确认，不能启动
  第二模型复现；
- 当前未获得 30-50 bug expansion 或新 verifier design 的边界确认，不能扩
  cohort 或重开旧 prompt-only 路线；
- submission checklist 已包含 tables、figures、IEEE draft/PDF、readiness、
  local quality 和 anonymous artifact audit 的 rebuild/audit 命令。

Plan:

1. 重建 paper tables、paper figures 和 IEEE LaTeX draft；
2. 连续两遍编译 IEEE PDF，并抽查 PDF 文本中的 workload ledger 和 bounded
   EVP-7 conclusion；
3. 重跑 claim-boundary、paper readiness、submission handoff、freeze-candidate、
   anonymous artifact 和 local quality gates；
4. 如重建发现 tracked drift，仅更新提交包维护相关文档，不改实验数据；
5. 不调用 API、不扩 bug、不补 E1/E3/E5、不重建 evidence packets、不把
   freeze-candidate 写成 final freeze。

Acceptance:

- paper tables / figures / IEEE draft 可重建；
- IEEE PDF 两遍编译成功且仍为当前 bounded four-anchor paper；
- readiness、artifact 和 local gates 仍通过；
- 若有文档漂移，记录原因、验证结果并只提交本轮相关文件。

Execute:

- 已运行 `python scripts\write_paper_tables.py`，重新生成
  `docs/paper/generated_tables.md` 和 `docs/paper/generated_tables.tex`；
- 已运行 `python scripts\generate_paper_figures.py`，重新生成 7 张 paper
  figures 的 PDF/SVG/PNG；
- 已运行 `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`；
- 已连续两遍运行 `pdflatex`，输出
  `outputs/paper_compile/ieee_submission_draft.pdf`，7 pages；
- 已重建匿名 artifact ZIP，保持 `file_count=303`。

Verify:

- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf - | rg ...`
  确认 PDF 包含 `20 tasks`、`94 candidates`、`376 records`、`21 tasks`、
  `98 candidates`、`392`、`bounded EVP-7`、`not scale-generalized` 和
  `single-model`；
- PowerShell PDF file inspection 确认 PDF 存在且 size 为 `258854` bytes；
- `python scripts\audit_paper_claim_boundary.py` 通过，`passed=true`、
  `raw_output_free=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\audit_submission_handoff.py --out-json outputs\submission_handoff_audit\latest.json --out-md outputs\submission_handoff_audit\latest.md`
  通过，`passed=true`；
- `python scripts\audit_submission_freeze_candidate.py --out-json outputs\submission_freeze_candidate_audit\latest.json --out-md outputs\submission_freeze_candidate_audit\latest.md`
  通过，`passed=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- direct JSON/ZIP inspection 确认 `paper_current_result_claim_ready=True`、
  `paper_submission_package_ready=True`、`artifact_safe=True`、
  `local_quality_passed=True`、`manifest_file_count=303`、
  `zip_has_current_plan=True`、`zip_has_submission_handoff=True`、
  `zip_has_submission_checklist=True`、`zip_has_fig7=True`。

## 2026-06-18 short project-state sync refresh

Inspect:

- 当前工作区干净，`main...origin/main [ahead 15]`；
- 最近提交为 `6423ecf Record no-API submission maintenance`；
- `docs/plans/current_project_state_zh.md` 是短入口，但其 Git 同步段仍主要描述
  2026-06-17 的早期本地残留状态，没有显式反映当前 clean / ahead 15 /
  最新 no-API submission maintenance verification；
- README 和 `docs/INDEX.md` 对短入口的说明保持泛化，没有发现必须同步改动的
  新入口或索引漂移；
- 本轮仍没有 second-model、30-50 bug expansion 或新 verifier design 的明确
  用户确认。

Plan:

1. 刷新 `docs/plans/current_project_state_zh.md` 的当前同步状态，记录 clean、
   ahead 15、最新本地 no-API 维护提交和 GitHub sync 延后边界；
2. 在 `docs/experience/engineering_notes.md` 记录短状态页同步漂移经验；
3. 不改 README/INDEX，因为没有新增入口且现有入口描述仍正确；
4. 不调用 API、不扩 bug、不补 E1/E3/E5、不重建 evidence packets。

Acceptance:

- 短状态页不再把 2026-06-17 残留描述作为当前同步状态；
- 文档仍要求 `git status --short --branch` 作为最终 Git source of truth；
- 第二模型、扩量、新 verifier 和 final freeze 边界不被放宽；
- targeted rg、paper readiness、artifact audit、local quality 和 diff checks 通过。

Execute:

- 已刷新 `docs/plans/current_project_state_zh.md` 的当前同步状态，记录本轮检查为
  `main...origin/main [ahead 15]`、工作区干净、最近本地提交 `6423ecf` 已记录
  no-API submission maintenance；
- 已明确 GitHub sync 失败时可按用户授权暂缓同步，不能把 ahead 状态解读为未完成
  实验工作；
- 已保留 `bugsinpy_cookiecutter_4` blocker policy 和本地诊断残留不得提交的边界；
- 已在 `docs/experience/engineering_notes.md` 增加 short project-state drift
  经验记录；
- README 和 `docs/INDEX.md` 未修改，因为现有短入口索引仍正确且没有新增文件入口。

Verify:

- targeted `rg` 检查确认 `current_project_state_zh.md`、`current_plan_zh.md` 和
  `engineering_notes.md` 包含 `ahead 15`、`6423ecf`、GitHub sync 延后边界、
  no-API submission maintenance 和 no-E1/E3/E5 / no-final-freeze 边界；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git diff --check` 通过；
- 当前 tracked drift 限于 `docs/plans/current_project_state_zh.md`、
  `docs/plans/current_plan_zh.md` 和 `docs/experience/engineering_notes.md`。

## 2026-06-18 non-cyclic Git ahead wording refresh

Inspect:

- 当前工作区干净，`main...origin/main [ahead 16]`；
- 最近提交为 `1766932 Refresh short project state`；
- `docs/plans/current_project_state_zh.md` 已要求以
  `git status --short --branch` 为准，但仍把 `ahead 15` 写在“当前同步状态”
  第一段，后续每次本地提交都会让该数字过期；
- `docs/experience/engineering_notes.md` 已记录“committing the refresh itself
  can increase the local ahead count”，因此本轮应把短状态页改成非循环措辞，而
  不是继续追精确 ahead 数；
- 本轮仍没有 second-model、30-50 bug expansion、新 verifier design 或 final
  freeze 的明确用户确认。

Plan:

1. 将 `docs/plans/current_project_state_zh.md` 的 Git 同步段改成非循环措辞：
   精确 ahead 数以当前 `git status` 为准，文档只记录最近检查为 clean/local
   ahead 和最近 no-API maintenance 提交；
2. 在 `docs/experience/engineering_notes.md` 补充不要反复追 ahead 数的经验；
3. 运行 targeted rg、paper readiness、artifact audit、local quality 和 diff
   checks；
4. 不调用 API、不扩 bug、不补 E1/E3/E5、不重建 evidence packets、不提交 ignored
   outputs/artifacts。

Acceptance:

- 短状态页不再把某个 ahead 数写成长期 current truth；
- 文档仍记录 GitHub sync 失败时可按用户授权暂缓同步；
- 当前 bounded EVP-7 paper/package readiness 不退化；
- tracked drift 只限本轮文档维护文件。

Execute:

- 已将 `docs/plans/current_project_state_zh.md` 的 Git 同步段改为非循环措辞：
  精确 ahead 数以 `git status --short --branch` 为准，短状态页只记录最近几轮
  检查为 clean/local-ahead；
- 已保留最近 no-API 维护提交 `6423ecf` 和短状态页刷新提交 `1766932` 作为
  handoff anchors；
- 已在 `docs/experience/engineering_notes.md` 补充不要每轮追写 ahead 数的经验；
- 未修改 README/INDEX，因为入口索引和 Git sync 说明仍正确。

Verify:

- targeted `rg` 检查确认 `current_project_state_zh.md` 不再将 `ahead 15` 或
  `ahead 16` 写成 current truth，并仍保留 `git status --short --branch`、
  GitHub sync 延后、no-E1/E3/E5 和 no-final-freeze 边界；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git diff --check` 通过；
- tracked drift 限于 `docs/plans/current_project_state_zh.md`、
  `docs/plans/current_plan_zh.md` 和 `docs/experience/engineering_notes.md`。

## 2026-06-18 ignored handoff refresh without tracked drift

Inspect:

- 当前工作区干净，`main...origin/main [ahead 17]`；
- 最近提交为 `6a220e0 Avoid fixed ahead count in project state`；
- `docs/experiments/evp7_next_decision_packet_20260618.md` 仍指定无明确新决策时
  只能继续 no-API paper-submission maintenance；
- 未发现需要再次追写 tracked ahead 数的稳定文档漂移；
- 但 ignored `outputs/handoff/*` 和 `outputs/git_sync_packet_audit/*` 是本地交接
  状态，适合在不改实验数据、不调用 API 的前提下刷新。

Plan:

1. 刷新 ignored Git sync packet 和 audit；
2. 刷新 ignored pre-API handoff；
3. 重跑 paper readiness、anonymous artifact audit 和 local quality gate；
4. 若 tracked 文件除本计划日志外无漂移，则只提交本轮计划记录；
5. 不调用 API、不扩 bug、不补 E1/E3/E5、不重建 evidence packets、不提交
   `outputs/` 或 `artifacts/`。

Acceptance:

- ignored handoff reports 能反映当前 local-ahead / GitHub-sync-deferred 状态；
- paper/package gates 继续通过；
- tracked drift 不包含 ignored reports 或 generated artifacts。

Execute:

- 已运行 `python scripts\write_git_sync_packet.py --out-json outputs\handoff\git_sync_packet.json --out-md outputs\handoff\git_sync_packet.md`；
- 已运行 `python scripts\audit_git_sync_packet.py --out-json outputs\git_sync_packet_audit\latest.json --out-md outputs\git_sync_packet_audit\latest.md`；
- 已运行 `python scripts\write_pre_api_handoff.py --out-json outputs\handoff\pre_api_handoff.json --out-md outputs\handoff\pre_api_handoff.md`；
- 这些输出均位于 ignored `outputs/`，不提交。

Verify:

- direct JSON inspection 确认 `git_requires_human_decision=True`、
  `git_sync_ready=False`、`git_audit_passed=True`、
  `pre_api_commands_passed=True`、`pre_api_ready_for_real_api=True`、
  `pre_api_git_decision_required=True`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git diff --check` 通过；
- `git status --short --branch` 显示 tracked drift 仅为
  `docs/plans/current_plan_zh.md`。

## 2026-06-18 markdown draft RQ alignment

Inspect:

- 当前工作区干净，`main...origin/main [ahead 18]`；
- `docs/experiments/evp7_next_decision_packet_20260618.md` 仍要求无新决策时只做
  no-API paper-submission maintenance；
- targeted paper-text search 发现 `docs/paper/patch_verification_draft.md` 的
  Research Questions 仍停留在早期 LLM-only / prompt-only /
  tool-augmented pilot 四问；
- 当前 `docs/paper/ieee_submission_draft.tex` 已使用 paper-facing EVP-7
  evidence-visibility 五问：evidence-poor risk、prompt-only cost、
  E0/E2/E4/E6 evidence-level effect、deterministic/tool-assisted baseline
  claim boundary、frozen 20-task pilot claim boundary；
- 这是论文文本一致性漂移，不是实验数据问题。

Plan:

1. 将 `docs/paper/patch_verification_draft.md` 的 draft status 更新到当前
   2026-06-18 bounded four-anchor submission draft；
2. 将 Markdown draft 的 Research Questions 改为与 IEEE submission draft
   一致的 RQ1-RQ5；
3. 在 `docs/experience/engineering_notes.md` 记录 Markdown/IEEE RQ drift 经验；
4. 不调用 API、不扩 bug、不补 E1/E3/E5、不修改实验数据或 evidence packets。

Acceptance:

- Markdown draft 和 IEEE submission draft 的 RQ framing 一致；
- 不引入 scale-generalized、LLM-over-tool-only 或 final-freeze claim；
- paper readiness、artifact audit、local quality 和 diff checks 通过。

Execute:

- 已将 `docs/paper/patch_verification_draft.md` 的 draft status 更新为
  `EVP-7 bounded four-anchor submission draft, 2026-06-18`；
- 已将 Markdown draft RQ1-RQ5 对齐到 IEEE submission draft 的当前
  evidence-visibility framing；
- 已在 `docs/experience/engineering_notes.md` 增加 Markdown and IEEE RQ drift
  经验记录；
- 未修改 IEEE generator、实验数据、evidence packets 或模型输出。

Verify:

- targeted `rg` 检查确认 Markdown draft 和 IEEE submission draft 都包含当前
  RQ1-RQ5 framing，Markdown draft status 已更新为 2026-06-18 bounded
  four-anchor submission draft；
- targeted `rg` 同时确认 Markdown draft 仍保留 `not scale-generalized`、
  no LLM superiority 和 no full-ladder 边界；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git diff --check` 通过；
- tracked drift 限于 Markdown paper draft、current plan 和 engineering notes。

## 2026-06-18 outline RQ alignment

Inspect:

- 当前工作区干净，`main...origin/main [ahead 19]`；
- 最近提交为 `10f2371 Align markdown draft research questions`；
- `docs/experiments/evp7_next_decision_packet_20260618.md` 仍要求无明确新决策时只做
  no-API paper-submission maintenance；
- 上一轮已对齐 `docs/paper/patch_verification_draft.md` 和
  `docs/paper/ieee_submission_draft.tex` 的 RQ1-RQ5；
- 本轮继续 targeted paper-facing search 发现
  `docs/paper/patch_verification_outline.md` 的 Research Questions 仍保留早期
  LLM-only / prompt-only / tool-assisted framing，并写有 `E0 through E6`，
  容易被误读为 full ladder。

Plan:

1. 将 `docs/paper/patch_verification_outline.md` 的 RQ1-RQ5 同步为当前
   evidence-visibility framing；
2. 把 outline 中的 evidence-level wording 改为 `E0/E2/E4/E6`，避免暗示完整
   E0-E6 ladder；
3. 补充 `docs/experience/engineering_notes.md`，记录 outline 也必须和 Markdown /
   IEEE draft 同步；
4. 不调用 API、不扩 bug、不补 E1/E3/E5、不修改实验数据或 evidence packets。

Acceptance:

- outline、Markdown draft 和 IEEE submission draft 的 RQ framing 一致；
- outline 不再暗示 full E0-E6 ladder；
- paper readiness、artifact audit、local quality 和 diff checks 通过。

Execute:

- 已将 `docs/paper/patch_verification_outline.md` 的 RQ1-RQ5 同步为当前
  evidence-visibility framing；
- 已将 outline 的 evidence-level wording 改为 `E0/E2/E4/E6`；
- 已在 `docs/experience/engineering_notes.md` 补充 outline RQ drift 经验记录；
- 未修改实验数据、IEEE generator、evidence packets 或模型输出。

Verify:

- targeted `rg` 检查确认 outline、Markdown draft 和 IEEE submission draft 的
  RQ1-RQ5 framing 已保持一致，outline 使用 `E0/E2/E4/E6` 而不是
  `E0 through E6`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `git diff --check` 通过。

## 2026-06-18 non-conflicting second-model/workload plan entry

Inspect:

- 用户要求把补“第二模型关键层级复现”或“工作量呈现”写到计划里，并且不能与
  其他内容冲突矛盾；
- `docs/plans/final_paper_roadmap_zh.md` 已有“工作量呈现强化”和
  “第二模型关键锚点复现”两条非冲突路线，但“关键层级”这个说法仍可能被误读为
  连续 E0-E6 ladder；
- 当前 paper-facing route 仍是 EVP-7 four-anchor E0/E2/E4/E6 bounded
  pilot，不补插 E1/E3/E5；
- `docs/experiments/evp7_next_decision_packet_20260618.md` 仍要求：无明确
  provider/model/预算/scope/停止条件时，不启动第二模型 API。

Plan:

1. 在 `docs/plans/final_paper_roadmap_zh.md` 中明确：第二模型“关键层级”
   复现等价于 `E0`、`E4`、`E6` key-anchor replication，不是完整 E0-E6
   adjacent-difference ladder；
2. 在 `docs/plans/current_project_state_zh.md` 同步同一表述，方便新会话先读
   短状态页时不误判；
3. 在 `docs/experience/engineering_notes.md` 记录该措辞归一规则；
4. 默认优先执行工作量呈现强化；第二模型只作为需用户确认 provider、model、
   预算、scope 和停止条件后的条件补强路线；
5. 不调用 API、不扩 bug、不补 E1/E3/E5、不重建 evidence packets、不改变
   当前 DeepSeek G5 376-record 主结果边界。

Acceptance:

- 计划明确包含“工作量呈现强化”和“第二模型关键层级/关键锚点复现”；
- “关键层级”被限定为 `E0`、`E4`、`E6`，不与 no-E1/E3/E5 和
  future EVP-8/full-ladder 边界冲突；
- 默认路线仍是 no-API 工作量呈现，第二模型路线仍需明确授权；
- targeted rg、paper readiness、artifact audit、local quality 和 diff checks 通过。

Execute:

- 已将 `docs/plans/final_paper_roadmap_zh.md` 的条件补强路线改为
  “第二模型关键层级/关键锚点复现”，并声明“关键层级”只指 `E0`、`E4`、`E6`
  三个 key anchors；
- 已将 `docs/plans/current_project_state_zh.md` 的短状态页同步为同一口径；
- 已在 `docs/experience/engineering_notes.md` 补充：用户说“第二模型关键层级
  复现”时，应归一为 `E0`/`E4`/`E6` key anchors，不得解释为 E1/E3/E5
  插入或 full ladder 授权。

Verify:

- targeted `rg` 检查确认 `final_paper_roadmap_zh.md`、
  `current_project_state_zh.md`、`current_plan_zh.md`、`engineering_notes.md`、
  `evp7_next_decision_packet_20260618.md` 和 `docs/INDEX.md` 中保留：
  工作量呈现默认 no-API、第二模型仅 `E0`/`E4`/`E6` key anchors、需用户确认
  provider/model/预算/scope/停止条件、no-E1/E3/E5 和 future full-ladder 边界；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git diff --check` 通过。

## 2026-06-18 no-API package rebuild after branch clarification

Inspect:

- 当前工作区干净，`main...origin/main [ahead 20]`；
- 最新提交为 `2249665 Clarify reinforcement plan branches`；
- `docs/experiments/evp7_next_decision_packet_20260618.md` 仍规定：无明确
  provider/model/预算/scope/停止条件时，只能继续 Option A no-API
  paper-submission maintenance；
- `docs/artifact/submission_checklist.md` 和
  `docs/artifact/submission_handoff_20260618.md` 已列出可复现 rebuild 命令；
- 当前没有 target venue/final freeze 确认，也没有第二模型、30-50 bug 扩量、
  E1/E3/E5 或新 verifier design 授权。

Plan:

1. 按 submission checklist 重新生成 paper tables、figures 和 IEEE draft；
2. 连续两遍编译 IEEE PDF，并抽查 PDF 文本中的 workload ledger 与 bounded
   EVP-7 conclusion；
3. 运行 claim-boundary、paper readiness、local quality、anonymous artifact
   rebuild 和 artifact audit；
4. 若 tracked 生成物没有 drift，只提交本轮 `current_plan_zh.md` 执行日志；
5. 不调用 API、不扩 bug、不补 E1/E3/E5、不重建 evidence packets、不提交
   ignored `outputs/` 或 `artifacts/`。

Acceptance:

- tables/figures/IEEE draft/PDF 可由 tracked scripts 复现；
- PDF 仍为当前 7-page paper package，并包含 21/98/392 structural workload 和
  20/94/376 paper-facing G5 boundary；
- paper readiness、claim-boundary、artifact audit、local quality 和 diff checks
  通过；
- tracked drift 不包含 ignored outputs/artifacts 或实验数据。

Execute:

- 已运行 `python scripts\write_paper_tables.py`，重建
  `docs/paper/generated_tables.md` 和 `docs/paper/generated_tables.tex`；
- 已运行 `python scripts\generate_paper_figures.py`，重建 7 张 paper figures 的
  PDF/SVG/PNG 输出；
- 已运行 `python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex`；
- 已连续两遍运行 `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex`，
  输出 7-page `outputs/paper_compile/ieee_submission_draft.pdf`；
- 已运行 PDF 文本抽查、claim-boundary audit、paper readiness、local quality、
  anonymous artifact rebuild 和 artifact audit；
- 生成步骤未造成 tracked tables/figures/IEEE draft 漂移，当前 tracked drift 仅为
  本轮 `docs/plans/current_plan_zh.md` 日志。

Verify:

- `pdftotext outputs\paper_compile\ieee_submission_draft.pdf - | rg -n "Workload at a Glance|20 tasks|94 candidates|376 records|21 tasks|98 candidates|392|bounded EVP-7|not scale-generalized|not claim"`
  命中 workload ledger、21/98/392 structural pipeline、20/94/376 paper-facing
  DeepSeek G5 run 和 bounded EVP-7 conclusion；
- `python scripts\audit_paper_claim_boundary.py` 通过，`passed=true`、
  `raw_output_free=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`。

## 2026-06-18 local completion audit boundary

Inspect:

- 当前工作区干净，`main...origin/main [ahead 21]`；
- 最新提交为 `3b3865c Record no-API package rebuild`；
- 用户未提供 target venue/final freeze、第二模型 provider/model/预算/scope、30-50
  bug 扩量或新 verifier design 授权；
- `docs/experiments/evp7_next_decision_packet_20260618.md` 仍要求无明确决策时
  只做 no-API paper-submission maintenance。

Plan:

1. 运行 `audit_goal_completion.py`、`audit_ai_plan_progress.py` 和
   `audit_execution_readiness.py`，区分本地计划完成状态、提交包状态和 GitHub
   sync 状态；
2. 将审计结果记录为 local completion boundary，不把它误写成 final freeze 或
   GitHub synchronized；
3. 不调用 API、不扩 bug、不补 E1/E3/E5、不重建 evidence packets、不提交
   ignored `outputs/`。

Acceptance:

- 本地目标/计划审计结果可追溯到 ignored audit outputs；
- plan 明确 GitHub sync 仍未成立，不能 claimed synced；
- no-API submission package readiness 不退化；
- artifact audit、local quality、diff checks 通过。

Execute:

- 已运行 `python scripts\audit_goal_completion.py --out-json outputs\goal_completion\latest.json --out-md outputs\goal_completion\latest.md`；
- 已运行 `python scripts\audit_ai_plan_progress.py --out-json outputs\plan_progress\latest.json --out-md outputs\plan_progress\latest.md`；
- 已运行 `python scripts\audit_execution_readiness.py --out-json outputs\readiness_audit\latest.json --out-md outputs\readiness_audit\latest.md`；
- 未调用模型 API，未修改实验数据，未重建 evidence packets。

Verify:

- `outputs/goal_completion/latest.json` 显示 `complete=true`，18/18 required
  checks passed；
- `outputs/plan_progress/latest.json` 显示 `stage_counts={"complete": 14}`，
  next actions 为空；
- `outputs/readiness_audit/latest.json` 显示 worktree clean、ahead 21、behind 0，
  但 `synced_with_upstream=false`，next action 是 push local commits before
  claiming GitHub sync；
- 该审计结果只支持 local no-API/package completion boundary，不代表 target
  venue/final freeze 已确认，也不代表 GitHub 已同步；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git diff --check` 通过。

## 2026-06-18 GitHub sync retry remains network-blocked

Inspect:

- 当前工作区干净，`main...origin/main [ahead 22]`；
- 最新提交为 `2b67f5e Record local completion audit boundary`；
- local completion audit 已确认本地 no-API/package boundary 成立，但
  `audit_execution_readiness.py` 仍显示 `synced_with_upstream=false`；
- 用户已明确允许 GitHub 频繁同步失败时跳过同步并继续执行后续任务。

Plan:

1. 在不修改实验数据、不调用 API 的前提下尝试一次 `git push origin main`；
2. 若 push 成功，重新检查 Git 状态；
3. 若 push 仍因网络层失败，记录为 GitHub sync deferred，不把它解释为实验或
   paper/package readiness 失败。

Acceptance:

- push 结果被记录；
- 若失败，计划明确该失败只影响 GitHub sync claim，不影响 local no-API
  completion/package readiness；
- 不提交 ignored `outputs/`、`artifacts/`、`.env` 或 local config。

Execute:

- 已运行 `git push origin main`；
- push 失败，错误为 `fatal: unable to access 'https://github.com/gaoming-a/research95.git/': Recv failure: Connection was reset`；
- `git status --short --branch` 仍显示 `main...origin/main [ahead 22]`，工作区干净；
- 已在 `docs/experience/engineering_notes.md` 记录该 connection-reset retry 仍属于
  network-level GitHub sync failure；
- 未调用 API、未修改实验数据、未重建 evidence packets。

Verify:

- GitHub sync 仍未成立，不能声称本地 `main` 已同步到 `origin/main`；
- 本轮失败符合既有 network-level sync failure boundary；
- 按用户授权，后续可以继续本地计划执行，不因该网络失败阻塞 no-API
  submission maintenance；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

## 2026-06-18 short state latest-anchor refresh

Inspect:

- 当前工作区干净，`main...origin/main [ahead 23]`；
- 最新提交为 `f15c621 Record GitHub sync retry failure`；
- `docs/plans/current_project_state_zh.md` 的当前同步状态仍只列出较早的
  `6423ecf` 和 `1766932` 作为 recent local no-API maintenance commits；
- 之后已经新增更关键的 local anchors：`3b3865c` no-API package rebuild、
  `2b67f5e` local completion audit boundary、`f15c621` GitHub sync retry
  failure；
- 本轮仍没有 target venue/final freeze、second-model provider/model/budget、
  30-50 bug expansion 或 new verifier design 授权。

Plan:

1. 将 `docs/plans/current_project_state_zh.md` 的同步状态改为 latest semantic
   anchors，而不是旧提交列表；
2. 保持精确 ahead 数仍以 `git status --short --branch` 为准，避免下一次提交后
   又产生循环漂移；
3. 在 `docs/experience/engineering_notes.md` 补充短状态页应记录最新语义锚点而
   不是老提交快照；
4. 不调用 API、不扩 bug、不补 E1/E3/E5、不重建 evidence packets。

Acceptance:

- 短状态页能指向最新 local completion、package rebuild 和 GitHub sync retry
  anchors；
- 文档不声称 GitHub 已同步，也不把 push failure 写成 paper/package failure；
- paper readiness、artifact audit、local quality 和 diff checks 通过。

Execute:

- 已将 `docs/plans/current_project_state_zh.md` 的最近提交说明改为 semantic
  anchors：`3b3865c` package rebuild、`2b67f5e` local completion audit
  boundary、`f15c621` GitHub sync retry failure；
- 已保留精确 ahead 数以 `git status --short --branch` 为准的规则；
- 已在 `docs/experience/engineering_notes.md` 补充短状态页应保持最新语义锚点，
  而不是只追写旧 ahead 快照；
- 未调用 API、未修改实验数据、未重建 evidence packets。

Verify:

- targeted `rg` 检查确认 `current_project_state_zh.md` 包含 `3b3865c`、
  `2b67f5e`、`f15c621` 三个 latest semantic anchors，并仍保留
  `git status --short --branch` source-of-truth 规则；
- targeted `rg` 检查确认 `engineering_notes.md` 记录短状态页应优先维护语义
  anchor commits，而不是旧 ahead snapshot；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json`
  通过，`file_count=303`、`safe_to_package=true`；
- `python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md`
  通过，`safe=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git diff --check` 通过。

## 2026-06-20 EVP-8 journal-scale follow-up plan

Inspect:

- 用户明确表示希望升级到期刊版本，并确认可先做 DeepSeek + Qwen，后续再补
  Kimi / Devstral / Gemini；
- 当前工作区检查前为 `main...origin/main`；
- 现有 canonical roadmap 仍规定：当前 EVP-7 是 `E0/E2/E4/E6`
  four-anchor pilot，E1/E3/E5 只能作为 EVP-8 / EVP-7-v2 新协议整体重做；
- `docs/experiments/evp7_next_decision_packet_20260618.md` 原先只有 Option A-D，
  其中第二模型路线仍是当前 EVP-7 的 `E0/E4/E6` key-anchor replication；
- 用户询问模型选择、排行榜适用性和 OpenRouter 成本后，当前更优方向是
  EVP-8 journal-scale full-ladder protocol，而不是继续旧 EVP-7 key-anchor
  add-on。

Plan:

1. 新增 no-API EVP-8 期刊版执行计划，明确当前 EVP-7 只作为 pilot 和设计动机；
2. 在最终路线图中加入 `EVP-8 journal-scale full-ladder` 路线；
3. 在 next-decision packet 中新增 Option E，避免后续 generic continue 回到旧
   Option A 或旧第二模型 key-anchor route；
4. 同步 README、docs index、current project state 和 engineering notes；
5. 不调用模型 API、不扩 cohort、不生成 EVP-8 packets、不提交 ignored outputs /
   artifacts / local configs；
6. 写清 DeepSeek/Qwen 第一批执行和 Kimi/Devstral/Gemini 后续补跑的冻结输入
   约束。

Acceptance:

- 新计划必须要求先 no-API protocol freeze，再执行任何 DeepSeek/Qwen API；
- EVP-8 必须是新协议，不能补插 E1/E3/E5 到现有 EVP-7 artifacts；
- 模型选择理由不能依赖排行榜权威性，只能把 leaderboard 作为 secondary sanity
  check；
- DeepSeek + Qwen 可以作为 two-model interim result，但不能写成最终五模型
  journal conclusion；
- 后续 Kimi/Devstral/Gemini 必须使用同一 frozen packets/prompts/schema；
- 文档检索、diff check 和 Git 状态检查通过后提交同步。

Execute:

- 新增 `docs/experiments/evp8_journal_scale_execution_plan_20260620.md`；
- 更新 `docs/plans/final_paper_roadmap_zh.md`，加入 18.7 EVP-8 期刊版
  full-ladder 路线；
- 更新 `docs/experiments/evp7_next_decision_packet_20260618.md`，新增 Option E；
- 更新 `docs/plans/current_project_state_zh.md`，将 EVP-8 期刊版计划列为当前
  继续实验前的第一决策门；
- 更新 `README.md` 和 `docs/INDEX.md`，加入 EVP-8 计划入口；
- 更新 `docs/experience/engineering_notes.md`，记录模型选择和冻结协议边界。

Verify:

- targeted `rg` 检查确认 README、INDEX、final roadmap、current project state、
  current plan、next decision packet、EVP-8 execution plan 和 engineering notes
  均包含 EVP-8 期刊版入口、DeepSeek/Qwen 第一批执行、Kimi/Devstral/Gemini
  后续补跑、排行榜仅作 secondary sanity check 等边界；
- `git diff --check` 通过；仅报告若干 tracked Markdown 文件的 LF/CRLF
  工作区提示，无 whitespace error；
- `git status --short` 显示本轮 tracked drift 仅为 README、docs index、计划、
  decision packet、engineering notes 和新增 EVP-8 execution plan；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- 本轮仍未调用模型 API，未改实验数据，未生成新 packets。

## 2026-06-20 EVP-8 Phase 0 protocol-spec audit

Inspect:

- 当前工作区为 `main...origin/main [ahead 1]`，本地最新提交已记录 EVP-8
  journal-scale execution plan，但 GitHub push 因网络失败尚未完成；
- `docs/experiments/evp8_journal_scale_execution_plan_20260620.md` 要求先执行
  no-API protocol freeze，之后才允许 DeepSeek/Qwen API smoke；
- 现有 EVP-7 已有 evidence packet、prompt manifest 和 schema dry-run 脚本，但
  EVP-8 目前还只有文字计划，没有机器可检查的协议定义；
- `docs/experiments/patch_evidence_bench_schema.md` 和
  `docs/experiments/leakage_policy.md` 已有长期 E0-E7 概念边界，EVP-8 新协议
  应复用这些边界，同时避免修改 EVP-7 artifacts。

Plan:

1. 新增 tracked EVP-8 protocol spec，冻结 `E0-E6` 可见字段、每级新增证据类、
   evaluator-only `E7`、模型计划、prompt/output schema、candidate-set policy 和
   stop gates；
2. 新增 no-API audit 脚本，验证相邻层级只新增一个 evidence class、可见字段不
   含 evaluator-only labels、模型批次和 OpenRouter routing policy 已固定；
3. 生成 tracked audit summary，作为 Phase 0 协议冻结的第一道机器检查；
4. 同步 README、docs index、EVP-8 execution plan 和 engineering notes，写清
   该步骤仍不授权 API、cohort expansion 或 packet generation；
5. 运行最小验证：EVP-8 protocol audit、paper readiness、local quality gate、
   `git diff --check`。

Acceptance:

- `E0-E6` 必须是连续 ladder，`E7` 只能是 evaluator-only upper bound；
- 每个 `Ek - E(k-1)` 只能新增一个命名证据类，不能把 EVP-7 的 E2/E4/E6
  直接移植为中间层；
- 所有 model-visible field groups 不得包含 `expected_outcome`、
  `candidate_type`、`failure_type_label`、hidden oracle 或 evaluator label；
- DeepSeek/Qwen 是第一批，Kimi/Devstral/Gemini 是后续批次，且必须复用同一
  frozen protocol/prompt/schema；
- 审计脚本必须明确 `api_call_attempted=false`，不读取 local API config；
- 本轮不生成 EVP-8 evidence packets，不调用任何模型 API。

Execute:

- 新增 `data/protocols/evp8_protocol_v0_1.json`，记录 EVP-8 v0.1
  full-ladder machine spec：
  - `E0` issue/patch seed；
  - `E1` structured patch surface；
  - `E2` patch-apply/static status slots；
  - `E3` visible fail-to-pass evidence；
  - `E4` visible pass-to-pass/regression evidence；
  - `E5` broader visible tool diagnostics；
  - `E6` deterministic visible merge-gate summary；
  - `E7` evaluator-only oracle upper bound；
- 新增 `scripts/audit_evp8_protocol_spec.py`，检查相邻差分、visible/hidden
  字段边界、DeepSeek/Qwen 第一批模型、Kimi/Devstral/Gemini 后续批次、
  routing policy、cost observability 和 stop gates；
- 运行审计后生成
  `data/protocols/evp8_protocol_v0_1_audit_summary.json`；
- 更新 `.gitignore`，允许 tracked `data/protocols/*.json`，因为 protocol spec
  和 audit summary 属于可复现协议数据，不是 raw experiment output；
- 同步更新 README、docs index、EVP-8 execution plan、final roadmap、current
  project state 和 engineering notes；
- 未调用模型 API，未读取 local API config，未生成 EVP-8 evidence packets，未扩
  cohort。

Verify:

- `python scripts\audit_evp8_protocol_spec.py --check` 通过：
  - `protocol_spec_audit_status = passed`；
  - `model_visible_levels = E0-E6`；
  - `adjacent_delta_count = 6`；
  - `E7` 是 evaluator-only；
  - `phase1_models = deepseek/deepseek-v4-pro, qwen/qwen3.7-max`；
  - `phase2_models = moonshotai/kimi-k2.6, mistralai/devstral-2512,
    google/gemini-2.5-flash`；
  - `api_call_attempted = false`；
  - `phase0_api_readiness = not_ready`，blockers 为 candidate set not frozen、
    prompt text not frozen，以及 packet/schema/prompt/cost/baseline dry-run
    outputs missing；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`；
- `git diff --check` 初次通过，仅有 LF/CRLF 提示；最终提交前需在 `.gitignore`
  和 current plan 更新后再复跑。

## 2026-06-20 EVP-8 Phase 0 candidate-set manifest

Inspect:

- 上一步已完成 EVP-8 protocol spec audit，本地提交 `f80fae7`；
- GitHub push 仍因 `Could not connect to server` 失败，当前按用户授权继续本地
  no-API 计划；
- `data/patches/evp7_candidates.jsonl` 当前 tracked structural cohort 为
  21 tasks / 98 candidates；
- `data/reviews/evp7_g5_llm_376_full_summary.json` 的历史 real DeepSeek G5 run
  是 20 tasks / 94 candidates，但 tracked raw-output-free summaries 不完整保留
  94 个 candidate id；
- `data/evidence/evp7_evidence_packet_summary.json` 当前已是 98 candidates /
  392 E0/E2/E4/E6 packets。

Plan:

1. 将 EVP-8 Phase 0 smoke/protocol-validation candidate set 冻结为当前 tracked
   structural 21-task / 98-candidate cohort；
2. 明确该 candidate set 只用于 EVP-8 packet/prompt/schema dry-run 和后续 smoke
   候选，不是期刊最终 full-scale 30-50 bug 结论；
3. 新增 candidate-set manifest builder，只输出 model-visible safe candidate
   selection records，不把 evaluator labels、expected outcomes、hidden oracle
   paths 写入 model-visible records；
4. summary 可以保留 aggregate label counts 用于 selection audit，但必须标记为
   evaluator-side aggregate，不进入 prompt；
5. 更新 EVP-8 protocol spec 的 `current_candidate_set_version` 与 manifest path，
   并让 protocol audit 不再报告 `candidate_set_not_frozen`；
6. 同步 README/INDEX/EVP-8 plan/current state/engineering notes。

Acceptance:

- candidate set summary 应为 21 tasks / 6 projects / 98 candidates；
- candidate records 不得包含 `expected_outcome`、`candidate_type`、
  `failure_type_label`、hidden oracle 或 evaluator label；
- protocol audit 仍必须 no-API，并将 API readiness 保持为 `not_ready`，因为
  prompt text、packets、schema、cost 和 baseline dry-run 还没完成；
- 该步骤不得生成 EVP-8 evidence packets，不调用模型 API。

Execute:

- 新增 `scripts/build_evp8_candidate_set_manifest.py`；
- 从 `data/patches/evp7_candidates.jsonl` 生成：
  - `data/protocols/evp8_candidate_set_v0_1.json`；
  - `data/protocols/evp8_candidate_set_v0_1_summary.json`；
- 更新 `data/protocols/evp8_protocol_v0_1.json`：
  - `current_candidate_set_version =
    evp8_smoke_from_evp7_structural_98_v0_1`；
  - candidate set scope 为 `phase0_smoke_protocol_validation_only`；
  - manifest 指向 `data/protocols/evp8_candidate_set_v0_1.json`；
- 更新 `scripts/audit_evp8_protocol_spec.py`，使 protocol audit 在 candidate
  manifest 存在时不再报告 `candidate_set_not_frozen`；
- 同步 README、docs index、EVP-8 execution plan、final roadmap、current
  project state 和 engineering notes；
- 未调用模型 API，未生成 EVP-8 evidence packets，未扩 cohort。

Verify:

- `python scripts\build_evp8_candidate_set_manifest.py --check` 通过：
  - `candidate_count = 98`；
  - `task_count = 21`；
  - `project_count = 6`；
  - `record_leakage_findings_count = 0`；
  - `api_call_attempted = false`；
  - `evidence_packets_generated = false`；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过：
  - `candidate_set_version =
    evp8_smoke_from_evp7_structural_98_v0_1`；
  - `candidate_set_manifest = data/protocols/evp8_candidate_set_v0_1.json`；
  - `api_blockers` 不再包含 `candidate_set_not_frozen`；
  - `api_blocker_count = 2`，剩余 blocker 为 prompt text not frozen 和
    packet/schema/prompt/cost/baseline dry-run outputs missing；
  - `phase0_api_readiness = not_ready`；
  - `api_call_attempted = false`。
- `git diff --check` 通过，仅有 LF/CRLF 工作区提示；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  初次并行调用超时无诊断；单独重跑通过，`passed=true`。

## 2026-06-20 EVP-8 Phase 0 prompt-template freeze

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 3]`；
- `data/protocols/evp8_protocol_v0_1_audit_summary.json` 当前
  `protocol_spec_audit_status=passed`，`phase0_api_readiness=not_ready`；
- 当前 blockers 为 `prompt_text_not_frozen` 以及 missing
  packet/schema/prompt/cost/baseline dry-run outputs；
- EVP-7 prompt builder `scripts/build_evp7_g5_llm_prompt_manifest.py` 使用
  merge-gate verifier prompt，要求只看 visible packet，不推断 hidden labels；
- EVP-8 protocol spec 已定义更严格 output schema：
  `decision/confidence/primary_reason/evidence_used/visible_contradictions/
  risk_flags/human_review_needed`；
- `docs/INDEX.md` 已引用 `prompts/prompt_change_log.md` 和
  `prompts/api_pilot_prompts.md`，但当前工作区没有 `prompts/` 目录，说明 prompt
  记录入口存在漂移。

Plan:

1. 新增 tracked EVP-8 prompt template，冻结 `evp8_visible_evidence_merge_gate_v0_1`
   的 prompt text；
2. 新增 prompt manifest / boundary audit 脚本，只审计模板和 minimal sample
   render，不生成 EVP-8 evidence packets、不调用 API；
3. 输出 tracked `data/protocols/evp8_prompt_manifest_v0_1.json` 和
   `data/protocols/evp8_prompt_boundary_audit_v0_1.json`；
4. 更新 EVP-8 protocol spec，使 `prompt_text_frozen=true` 并记录 prompt template、
   prompt manifest、boundary audit path 和 template hash；
5. 更新 protocol audit，使 prompt template/manifest/boundary audit 存在时不再
   报告 `prompt_text_not_frozen` 或 missing `prompt_manifest` /
   `prompt_boundary_audit`；
6. 创建或更新 `prompts/prompt_change_log.md`，记录本次新增 prompt 与 EVP-7
   prompt 的关系、差异和无冲突结论；
7. 同步 README、INDEX、EVP-8 execution plan、current project state 和
   engineering notes。

Acceptance:

- prompt template 必须只要求使用 visible evidence packet；
- prompt template 不得包含 `expected_outcome`、`candidate_type`、
  `failure_type_label`、hidden oracle、reference provenance 或 evaluator label；
- output schema 必须与 `data/protocols/evp8_protocol_v0_1.json` 保持一致；
- prompt manifest / boundary audit 必须明确 `api_call_attempted=false`、
  `evidence_packets_generated=false`；
- protocol audit 应继续 `protocol_spec_audit_status=passed`，并保持
  `phase0_api_readiness=not_ready`，因为 packet/schema/cost/baseline dry-run
  还未完成；
- 本轮不得调用模型 API，不读取 local API config，不生成 EVP-8 evidence packets。

Execute:

- 新增 `prompts/evp8_visible_evidence_merge_gate_v0_1.md`，冻结
  `evp8_visible_evidence_merge_gate_v0_1` prompt template；
- 新增 `prompts/prompt_change_log.md`，记录 EVP-8 prompt 是新协议 prompt，
  不替换 EVP-7 `patch_verify_evidence_visibility_merge_gate_v1`，并记录 schema
  差异和无冲突结论；
- 新增 `scripts/build_evp8_prompt_manifest.py`；
- 生成：
  - `data/protocols/evp8_prompt_manifest_v0_1.json`；
  - `data/protocols/evp8_prompt_boundary_audit_v0_1.json`；
- 更新 `data/protocols/evp8_protocol_v0_1.json`：
  - `prompt_text_frozen = true`；
  - `prompt_template_path =
    prompts/evp8_visible_evidence_merge_gate_v0_1.md`；
  - `prompt_template_sha256 =
    a31d23d74f5130c9ce06262c4a9f016a303da8e77683c007e7cfb142fb74066c`；
  - prompt manifest 和 prompt boundary audit 指向 tracked protocol artifacts；
- 更新 `scripts/audit_evp8_protocol_spec.py`，在 prompt manifest 和 boundary
  audit 存在时不再报告 prompt blocker；
- 同步 README、docs index、EVP-8 execution plan、final roadmap、current project
  state 和 engineering notes；
- 未调用模型 API，未读取 local API config，未生成 EVP-8 evidence packets。

Verify:

- `python scripts\build_evp8_prompt_manifest.py --check` 通过：
  - `prompt_manifest_status = passed`；
  - `prompt_boundary_audit_status = passed`；
  - `template_boundary_findings = []`；
  - `sample_render_boundary_findings = []`；
  - `missing_required_schema_keys_in_template = []`；
  - `api_call_attempted = false`；
  - `evidence_packets_generated = false`；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过：
  - `protocol_spec_audit_status = passed`；
  - `warning_count = 0`；
  - `api_blockers` 不再包含 `prompt_text_not_frozen`、
    `prompt_manifest` 或 `prompt_boundary_audit`；
  - 剩余 blocker 仅为 `cost_observability_dry_run`、
    `deterministic_tool_baseline_dry_run`、`evidence_packet_dry_run_summary`、
    `schema_dry_run_summary`；
  - `phase0_api_readiness = not_ready`；
  - `api_call_attempted = false`。
- `git diff --check` 通过，仅有 LF/CRLF 工作区提示；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md`
  通过，`current_result_claim_ready=true`、`submission_package_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过，`passed=true`。

## 2026-06-20 EVP-8 Phase 0 packet/schema dry-run summaries

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 4]`；
- 最新本地提交 `9255f65 Freeze EVP-8 prompt template`；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过；
- 当前 EVP-8 blocker 缩小为：
  `cost_observability_dry_run`、`deterministic_tool_baseline_dry_run`、
  `evidence_packet_dry_run_summary`、`schema_dry_run_summary`；
- `data/protocols/evp8_candidate_set_v0_1.json` 已冻结 98 candidates；
- `data/protocols/evp8_protocol_v0_1.json` 已冻结 E0-E6 field groups 和 output
  schema；
- `prompts/evp8_visible_evidence_merge_gate_v0_1.md` 已冻结 prompt template。

Plan:

1. 新增 no-API packet/schema dry-run 脚本；
2. 只在内存构造 `98 candidates x 7 model-visible levels = 686` 个 EVP-8 packet
   skeleton，验证每个 level 的 cumulative field groups、required fields 和
   visible/hidden 边界；
3. 不写完整 evidence packet JSONL，不把它当作最终 EVP-8 packet generation；
4. 生成 tracked packet dry-run summary 和 schema dry-run summary；
5. 更新 protocol spec 和 protocol audit，使这两个 summary 存在时解除对应
   blocker；
6. 同步 README、INDEX、EVP-8 plan、current state、engineering notes。

Acceptance:

- packet dry-run summary 必须报告 686 planned packet skeletons，E0-E6 每层 98；
- summary 必须明确 `full_evidence_packets_generated=false`、
  `api_call_attempted=false`、`raw_prompt_text_stored=false`；
- schema dry-run summary 必须报告 686 valid parse records、0 invalid、0 leakage；
- 每个 dry-run output schema 必须匹配 EVP-8 protocol output schema；
- protocol audit 剩余 blocker 应只包含 cost observability 和 deterministic
  baseline dry-run；
- 本轮不得调用 API，不生成真实 EVP-8 evidence packet JSONL。

Execute:

- 新增 `scripts/build_evp8_packet_schema_dry_run.py`；
- 在内存构造 EVP-8 planned packet skeletons，不写完整 packet JSONL；
- 生成：
  - `data/protocols/evp8_evidence_packet_dry_run_summary_v0_1.json`；
  - `data/protocols/evp8_schema_dry_run_summary_v0_1.json`；
- 更新 `data/protocols/evp8_protocol_v0_1.json`，新增
  `phase0_dry_run_artifacts`，指向 packet/schema dry-run summaries；
- 更新 `scripts/audit_evp8_protocol_spec.py`，在 packet/schema dry-run summary
  存在时不再报告对应 blocker；
- 同步 README、docs index、EVP-8 execution plan、final roadmap、current project
  state 和 engineering notes；
- 未调用 API，未生成真实 EVP-8 evidence packet JSONL。

Verify:

- `python scripts\build_evp8_packet_schema_dry_run.py --check` 通过：
  - `planned_packet_skeleton_count = 686`；
  - E0-E6 每层 98 planned skeletons；
  - `packet_dry_run_status = passed`；
  - `schema_dry_run_record_count = 686`；
  - `valid_parse_count = 686`；
  - `invalid_parse_count = 0`；
  - `leakage_findings_count = 0`；
  - `full_evidence_packets_generated = false`；
  - `api_call_attempted = false`；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过：
  - `protocol_spec_audit_status = passed`；
  - `api_blockers = missing_phase0_outputs_before_api:cost_observability_dry_run,deterministic_tool_baseline_dry_run`；
  - `phase0_api_readiness = not_ready`；
  - `api_call_attempted = false`。

## 2026-06-20 EVP-8 next execution plan before DeepSeek/Qwen

Inspect:

- 用户当前要求先写入后续计划，稍后再按计划执行；
- 当前 EVP-8 Phase 0 已完成 protocol spec、candidate set、prompt template、
  prompt boundary audit、packet/schema dry-run summaries；
- protocol audit 仍禁止 API：剩余 blocker 为 `cost_observability_dry_run` 和
  `deterministic_tool_baseline_dry_run`；
- 当前第一批可执行模型仍是 DeepSeek V4 Pro 与 Qwen3.7 Max；
- Kimi K2.6、Devstral 2、Gemini 2.5 Flash 只能作为后续补跑模型，且必须复用
  同一 frozen packets/prompts/schema；
- 本轮只写计划，不调用模型 API，不读取 local API config。

Plan:

1. 先收口并提交当前 packet/schema dry-run 相关变更；GitHub 若继续连接失败，
   记录事实后不阻塞后续本地执行；
2. 新增 cost-observability dry-run：
   - 不调用 API；
   - 固定模型 ID、provider routing policy、temperature、max tokens、retry
     policy 和 token/cost accounting fields；
   - 对 `98 candidates x 7 levels = 686` 个 planned calls 输出 summary-only
     成本可观测性检查；
   - 明确 unknown usage 或 missing provider/model id 会阻塞 API；
3. 新增 deterministic tool-baseline dry-run：
   - 不调用 API；
   - 只使用 EVP-8 model-visible evidence slots；
   - 生成 schema-valid rule decisions 或 summary-only audit，验证不会读取
     evaluator-only labels；
   - 输出 tracked baseline dry-run summary；
4. 更新 `data/protocols/evp8_protocol_v0_1.json` 和
   `scripts/audit_evp8_protocol_spec.py`，使 cost/baseline dry-run 通过后
   protocol audit 从 `not_ready` 进入 `ready_for_api_preflight`；
5. 在 API 前新增 DeepSeek/Qwen local preflight：
   - 只检查 ignored local config、`.env` key presence、模型 ID、输出目录、
     overwrite boundary、cost budget 和 raw-output policy；
   - preflight 通过仍不等于自动执行，必须等待用户明确说执行；
6. Phase 1 smoke 顺序固定为 DeepSeek 后 Qwen：
   - 每个模型先跑 stratified smoke，覆盖 5 个 candidates x 7 levels = 35 calls；
   - smoke 必须通过 parse-valid、schema、usage/cost、quality 和 leakage gates；
   - 任一模型 smoke 失败，先诊断并修 protocol/runner，不进入 full run；
7. 两个 smoke 均通过后，才运行 DeepSeek/Qwen 第一批 full interim：
   - 使用同一 frozen packet set、prompt version、schema、temperature 和
     evaluator joins；
   - 当前 Phase 0 cohort full interim 为 98 candidates x 7 levels = 686 calls
     per model；
   - 输出 raw-output-free summaries、quality audits、per-level metrics、
     cross-model comparison、claim-boundary update 和 cost observability；
8. DeepSeek/Qwen 第一批完成后，只能写成 two-model interim result；
   不得写成最终五模型 journal conclusion；
9. 后续补跑 Kimi/Devstral/Gemini 前，不改 protocol/prompt/schema/candidate set。
   如果第一批暴露协议缺陷，必须 bump protocol version，并从头重跑受影响模型。

Acceptance:

- 下一轮执行的第一个 concrete task 必须仍是 no-API cost/baseline dry-run，不得
  直接进入 DeepSeek/Qwen API；
- protocol audit 未进入 `ready_for_api_preflight` 前，禁止真实模型调用；
- DeepSeek/Qwen preflight 必须显式记录 provider/model id、exact prompt
  version、expected call count、overwrite policy、raw-output ignored path、
  usage/cost fields 和 stop gates；
- smoke/full run 使用的 packets/prompts/schema 必须完全同版；
- 若 GitHub push 继续失败，只记录网络事实，不改变实验计划和本地执行顺序。

## 2026-06-20 EVP-8 Phase 0 cost/baseline dry-run summaries

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 5]`；
- 最新本地提交 `424336e Add EVP-8 packet schema dry-run plan`；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过；
- 当前 EVP-8 blocker 仅剩：
  `cost_observability_dry_run` 和 `deterministic_tool_baseline_dry_run`；
- 本轮仍是 no-API Phase 0 收口，不读取 local API config、不调用模型、不生成
  raw outputs。

Plan:

1. 新增 no-API cost/baseline dry-run builder；
2. cost dry-run 只基于 frozen protocol、candidate set 和 planned E0-E6 call
   matrix，检查 provider/model id、actual provider/model recording、token/cost
   accounting fields、retry policy 和 planned call counts；
3. deterministic baseline dry-run 只使用 EVP-8 model-visible evidence slots，
   为 686 planned records 生成 schema-valid deterministic decisions summary，
   并确认不读取 per-candidate evaluator-only labels；
4. 输出 tracked summary-only artifacts：
   - `data/protocols/evp8_cost_observability_dry_run_v0_1.json`；
   - `data/protocols/evp8_deterministic_tool_baseline_dry_run_v0_1.json`；
5. 更新 `data/protocols/evp8_protocol_v0_1.json` 和
   `scripts/audit_evp8_protocol_spec.py`，使两项 dry-run 通过后 protocol audit
   进入 `ready_for_api_preflight`；
6. 同步 README、docs index、EVP-8 execution plan、final roadmap、current
   project state 和 engineering notes。

Acceptance:

- cost dry-run 必须报告 686 planned calls per model、DeepSeek/Qwen 第一批模型、
  Kimi/Devstral/Gemini 后续模型、usage/cost required fields 全部 present；
- deterministic baseline dry-run 必须报告 686 planned records、E0-E6 每层 98、
  0 schema invalid、0 leakage findings；
- 两个 dry-run summary 必须明确 `api_call_attempted=false`、
  `local_api_config_read=false`、`raw_outputs_generated=false`；
- protocol audit 必须从 `phase0_api_readiness=not_ready` 更新为
  `phase0_api_readiness=ready_for_api_preflight`，且仍不得表示已经执行 API；
- 本轮不得调用模型 API，不读取 `.env` 或 local config。

Execute:

- 新增 `scripts/build_evp8_cost_baseline_dry_run.py`；
- 生成：
  - `data/protocols/evp8_cost_observability_dry_run_v0_1.json`；
  - `data/protocols/evp8_deterministic_tool_baseline_dry_run_v0_1.json`；
- 更新 `data/protocols/evp8_protocol_v0_1.json` 的
  `phase0_dry_run_artifacts`，挂载 cost/baseline dry-run summaries；
- 更新 `scripts/audit_evp8_protocol_spec.py`，要求 cost/baseline summaries
  status passed 且 no-API/local-config/raw-output flags 为 false 后，才移除
  blocker；
- 将 protocol audit 的 readiness 从通用 `ready` 规范为
  `ready_for_api_preflight`；
- 同步 README、docs index、EVP-8 execution plan、final roadmap、current project
  state 和 engineering notes；
- 未调用模型 API，未读取 `.env` 或 local API config，未生成 raw outputs。

Verify:

- `python scripts\build_evp8_cost_baseline_dry_run.py --check` 通过：
  - `planned_calls_per_model = 686`；
  - `phase1_first_batch_models = deepseek/deepseek-v4-pro, qwen/qwen3.7-max`；
  - `phase2_later_batch_models = moonshotai/kimi-k2.6, mistralai/devstral-2512,
    google/gemini-2.5-flash`；
  - `missing_usage_cost_fields = []`；
  - `planned_baseline_record_count = 686`；
  - `valid_schema_count = 686`；
  - `invalid_schema_count = 0`；
  - `leakage_findings_count = 0`；
  - `api_call_attempted = false`；
  - `local_api_config_read = false`；
  - `raw_outputs_generated = false`；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过：
  - `protocol_spec_audit_status = passed`；
  - `api_blocker_count = 0`；
  - `phase0_api_readiness = ready_for_api_preflight`；
  - `next_step = Run ignored local DeepSeek/Qwen preflight next; this audit still does not authorize API execution.`；
  - `api_call_attempted = false`。

## 2026-06-20 EVP-8 DeepSeek/Qwen local preflight

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 6]`；
- 最新本地提交 `5b40306 Add EVP-8 cost baseline dry-run gate`；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过，且
  `phase0_api_readiness = ready_for_api_preflight`；
- 下一步仍不是 API execution，而是 ignored local DeepSeek/Qwen preflight；
- 本轮可以读取 ignored local config 和 `.env` 的 key presence，但不得输出 key
  value，不得调用 API。

Plan:

1. 新增 tracked EVP-8 DeepSeek/Qwen example config，记录 exact protocol/model/
   prompt/candidate/call-count boundary，不包含密钥；
2. 新增 local config helper，支持 dry-run 和写入 ignored
   `configs/evp8_deepseek_qwen.local.json`；
3. 新增 preflight checker，验证：
   - protocol audit 已是 `ready_for_api_preflight`；
   - local config 是 ignored local path；
   - Phase 1 模型严格为 DeepSeek V4 Pro 和 Qwen3.7 Max；
   - prompt/schema/candidate set/call counts 与 frozen protocol 一致；
   - raw-output paths 位于 ignored `outputs/`；
   - overwrite policy、usage/cost fields 和 stop gates 已记录；
   - `.env` 只检查 `DEEPSEEK_API_KEY` / `QWEN_API_KEY` 是否存在，不输出值；
4. 生成 tracked preflight summary，只记录 no-secret 状态：
   `data/protocols/evp8_deepseek_qwen_preflight_summary_v0_1.json`；
5. 同步 README、INDEX、EVP-8 execution plan、current project state、final
   roadmap 和 engineering notes。

Acceptance:

- preflight 必须明确 `api_call_attempted=false`、`raw_outputs_generated=false`；
- tracked summary 不得包含 API key、raw prompt text、local config content 或 raw
  outputs；
- strict preflight 若通过，只能进入“等待用户明确执行 smoke”的状态，不得自动调用
  DeepSeek/Qwen；
- 若缺 key 或 local config 不成立，只记录 blocker，不降级或跳过执行边界。

Execute:

- 新增 `configs/evp8_deepseek_qwen.example.json`，记录 no-secret Phase 1
  DeepSeek/Qwen preflight config；
- 新增 `scripts/create_evp8_deepseek_qwen_local_config.py`；
- 新增 `scripts/preflight_evp8_deepseek_qwen.py`；
- 生成 tracked no-secret local config plan：
  `data/protocols/evp8_deepseek_qwen_local_config_plan_v0_1.json`；
- 写入 ignored local config：
  `configs/evp8_deepseek_qwen.local.json`；
- 运行 strict preflight 并生成 tracked no-secret summary：
  `data/protocols/evp8_deepseek_qwen_preflight_summary_v0_1.json`；
- 同步 README、docs index、EVP-8 execution plan、final roadmap、current project
  state 和 engineering notes；
- 未调用模型 API，未生成 raw outputs，未提交 local config。

Verify:

- `python -m py_compile scripts\create_evp8_deepseek_qwen_local_config.py scripts\preflight_evp8_deepseek_qwen.py`
  通过；
- `python scripts\create_evp8_deepseek_qwen_local_config.py --write` 通过：
  - `target_is_ignored_local_config = true`；
  - `local_config_write_attempted = true`；
  - `contains_api_key_values = false`；
  - `api_call_attempted = false`；
- `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
  通过：
  - `preflight_status = passed`；
  - `structural_ready = true`；
  - `credential_presence_ready = true`；
  - `ready_for_user_execute_command = true`；
  - `api_key_values_printed = false`；
  - `local_config_content_stored_in_tracked_summary = false`；
  - `api_call_attempted = false`；
  - `raw_outputs_generated = false`；
- `git status --short --ignored configs\evp8_deepseek_qwen.local.json` 显示
  local config 为 ignored：`!! configs/evp8_deepseek_qwen.local.json`。

## 2026-06-20 EVP-8 Phase 1 smoke follow-up plan

Inspect:

- DeepSeek/Qwen ignored local preflight 已通过，且明确
  `api_call_attempted=false`、`raw_outputs_generated=false`；
- 当前 EVP-8 Phase 0 protocol/candidate/prompt/schema/cost/baseline gates 已经
  支持进入“等待用户明确执行 smoke”的状态；
- 本轮用户只要求写入后续计划，不授权模型 API 调用；
- 下一步必须先提交当前 preflight 与计划 artifacts，再等待用户明确执行命令。

Plan:

1. 先完成本轮 preflight/plan artifacts 的提交；GitHub 若继续同步失败，按用户
   授权记录失败后继续，不阻塞本地计划执行；
2. 在用户明确说“执行 EVP-8 Phase 1 smoke”之前，不运行任何 `--execute`
   模型命令；
3. 收到执行命令后，第一步仍是只读守卫检查：
   - `git status --short --branch --untracked-files=all`；
   - `python scripts\audit_evp8_protocol_spec.py --check`；
   - `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`；
   - `git status --short --ignored configs\evp8_deepseek_qwen.local.json`；
4. 若发现 EVP-8 smoke runner 尚不存在，只允许补一个最小 guarded runner：
   - 默认 check-only，不调用 API；
   - 真实调用必须显式 `--execute`；
   - 拒绝 tracked example config；
   - 只读取 ignored local config；
   - raw model responses 只写入 ignored `outputs/`；
   - tracked summary 只保存 raw-output-free parse、usage/cost、model/provider、
     level 和 gate 结果；
   - 不修改 frozen protocol、prompt、candidate set 或 evidence ladder；
5. smoke 执行顺序固定：
   - 先 DeepSeek V4 Pro，5 candidates x 7 levels = 35 calls；
   - DeepSeek smoke 通过 parse/schema/usage-cost/raw-output policy 后，再执行
     Qwen3.7 Max 同一 35 calls；
   - 任一模型 smoke 失败，立即停止，先诊断为 runner bug、API/provider 问题、
     prompt/schema 问题、数据/证据问题或成本可观测性问题；
6. 两个 smoke 均通过后，只更新 raw-output-free smoke summary、质量审计、
   cost-observability summary、docs 和 claim boundary；
7. Phase 1 full run 仍需下一道显式 gate，不因 smoke 通过自动执行。

Acceptance:

- 本轮计划写入后仍不得产生模型 API 调用或 raw outputs；
- 后续 smoke 最大范围为 DeepSeek 35 calls + Qwen 35 calls，不进入 686-call
  full run；
- smoke 使用的 protocol id、candidate set id、prompt hash、levels 和 model ids
  必须与 preflight summary 一致；
- `configs/evp8_deepseek_qwen.local.json` 必须保持 ignored 且不得 staged；
- 如果 smoke runner 需要新增，必须先通过 py_compile、check-only/preflight 和
  secret scan，再允许真实 API；
- smoke 结果只能写成 two-model smoke/interim readiness，不能写成五模型期刊结论。

## 2026-06-20 EVP-8 smoke runner scaffold

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 7]`；
- 最新提交为 `f3d4805 Add EVP-8 DeepSeek Qwen preflight plan`；
- 已存在 EVP-8 protocol、candidate set、prompt manifest、packet/schema dry-run、
  cost/baseline dry-run 和 DeepSeek/Qwen preflight；
- 尚未存在 EVP-8 专用 smoke runner；
- 本轮不是 API 执行授权，不能运行任何真实模型调用。

Plan:

1. 新增最小 EVP-8 DeepSeek/Qwen smoke runner；
2. runner 默认只支持 check-only，并可在未来显式 `--execute` 时执行单个模型；
3. runner 必须拒绝 tracked example config，真实执行只能使用 ignored local config；
4. runner 在内存中从 frozen candidate set + EVP-7 model-visible seed 构造
   5-candidate x 7-level smoke packets；
5. smoke subset 使用 deterministic project-frequency-stratified 选择，避免只取
   manifest 前 5 条导致单项目 smoke，并确保主导项目进入 smoke；
6. rendered prompt 不写入 tracked artifact；check-only summary 只记录 prompt
   hash、packet count、selected candidate ids、schema/gate 状态；
7. raw model responses 只允许未来写入 ignored `outputs/`，本轮不生成；
8. 同步 README、docs index、EVP-8 execution plan、current project state 和
   engineering notes。

Acceptance:

- 本轮 `api_call_attempted=false`、`raw_outputs_generated=false`；
- `python -m py_compile` 通过；
- runner check-only 通过，且不读取或打印 API key value；
- `python scripts\audit_evp8_protocol_spec.py --check` 继续通过；
- `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
  继续通过；
- `configs/evp8_deepseek_qwen.local.json` 保持 ignored；
- staged diff 不包含 `.env`、`outputs/`、`artifacts/` 或 local config。

Execute:

- 新增 `scripts/run_evp8_deepseek_qwen_smoke.py`；
- runner 支持：
  - check-only no-API path；
  - future real execution only with ignored local config、strict preflight、
    explicit `--execute` and configured `--model-id`；
  - DeepSeek official and Qwen official routes through existing clients；
  - raw responses only under ignored `outputs/` for future execution；
  - tracked raw-output-free summary for check-only/executed smoke state；
- check-only 在内存中构造 deterministic project-frequency-stratified
  5 candidates x 7 levels = 35 smoke packets；
- 生成 tracked no-API summary：
  `data/protocols/evp8_deepseek_qwen_smoke_check_only_v0_1.json`；
- 同步 README、docs index、EVP-8 execution plan、final roadmap、current project
  state 和 engineering notes；
- 本轮未调用模型 API，未生成 raw outputs，未提交 local config。

Verify:

- `python -m py_compile scripts\run_evp8_deepseek_qwen_smoke.py` 通过；
- `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`
  通过：
  - `check_only_status = passed`；
  - `packet_count = 35`；
  - `prompt_count = 35`；
  - `prompt_hashes_unique_count = 35`；
  - `boundary_error_count = 0`；
  - `schema_error_count = 0`；
  - `api_call_attempted = false`；
  - `raw_outputs_generated = false`；
  - selected smoke candidates =
    `evp8_smoke_candidate_0001`, `evp8_smoke_candidate_0011`,
    `evp8_smoke_candidate_0030`, `evp8_smoke_candidate_0040`,
    `evp8_smoke_candidate_0047`；
- 下一步仍是等待用户明确执行真实 DeepSeek/Qwen smoke，不自动调用 API。

## 2026-06-20 EVP-8 post-smoke audit scaffold

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 11]`；
- 最新提交为 `bbf0c6f Add EVP-8 smoke execution packet`；
- 真实 DeepSeek/Qwen smoke 仍未执行；
- 当前已有 execution packet，但尚无 future smoke summaries 的统一审计入口；
- 本轮仍不是 API 执行授权，不能运行任何真实模型调用。

Plan:

1. 新增 no-API EVP-8 post-smoke audit script；
2. 审计脚本读取 execution packet 和未来 tracked smoke summaries，不读取 raw
   responses；
3. 当前无真实 smoke summaries 时，输出 `waiting_for_execution` 而非失败；
4. 如果未来只有 Qwen summary 而 DeepSeek 未通过，必须判为失败；
5. 如果未来 summary 存在，必须检查 model id、review_count=35、parse_valid=35、
   invalid_parse=0、smoke_gate、usage_cost_gate、raw output path under ignored
   `outputs/`；
6. 生成 JSON/Markdown audit artifact，并同步 README、INDEX、EVP-8 execution
   plan、current project state 和 engineering notes。

Acceptance:

- 当前 audit status 应为 `waiting_for_execution`；
- `api_call_attempted=false`、`raw_outputs_read=false`；
- 不读取或提交 raw outputs、local config 或 `.env`；
- execution packet `--check`、runner check-only、strict preflight、protocol audit
  和 local quality gate 继续通过。

Execute:

- 新增 `scripts/audit_evp8_smoke_results.py`；
- 生成 no-API post-smoke audit scaffold：
  - `data/protocols/evp8_deepseek_qwen_smoke_result_audit_v0_1.json`；
  - `docs/experiments/evp8_deepseek_qwen_smoke_result_audit_v0_1.md`；
- 当前无真实 smoke summaries，因此 audit status 为 `waiting_for_execution`；
- 同步 README、docs index、EVP-8 execution plan、final roadmap、current project
  state 和 engineering notes；
- 本轮未调用模型 API，未读取 raw outputs，未生成 raw outputs，未提交 local
  config。

Verify:

- `python -m py_compile scripts\audit_evp8_smoke_results.py` 通过；
- `python scripts\audit_evp8_smoke_results.py --check` 通过：
  - `audit_status = waiting_for_execution`；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
  - `raw_outputs_generated_by_audit = false`；
  - `qwen_requires_deepseek_passed = true`；
- 下一步仍是等待用户明确执行真实 DeepSeek/Qwen smoke，不自动调用 API。

## 2026-06-20 EVP-8 smoke subset selection repair

Inspect:

- 当前 runner check-only 已通过，但当时的 smoke subset policy 还是旧的
  first-project-order strategy；
- EVP-8 candidate set project distribution 为 youtube-dl 52、cookiecutter 19、
  PySnooper 10、tqdm 7、httpie 6、thefuck 4；
- 现有 5-candidate smoke subset 选中了 PySnooper、cookiecutter、httpie、
  thefuck、tqdm，漏掉占比最高的 youtube-dl；
- 本轮仍不是 API 执行授权，不能运行任何真实模型调用。

Plan:

1. 将 smoke subset policy 改为 deterministic project-frequency stratified：
   按项目 candidate count 降序选每个项目的首个 candidate，数量相同时按 manifest
   首次出现顺序稳定排序；
2. 5-candidate smoke subset 应覆盖 youtube-dl、cookiecutter、PySnooper、tqdm、
   httpie，排除最小项目 thefuck；
3. 重新生成 tracked check-only summary；
4. 同步 README、EVP-8 execution plan、current project state、engineering notes
   和当前执行日志；
5. 只做 no-API check-only，不生成 raw outputs，不执行 `--execute`。

Acceptance:

- check-only 仍为 passed；
- `packet_count = 35`、`prompt_hashes_unique_count = 35`；
- selected candidates 必须包含 `evp8_smoke_candidate_0047`；
- `api_call_attempted=false`、`raw_outputs_generated=false`；
- protocol audit、preflight 和 local quality gate 继续通过。

Execute:

- 修改 `scripts/run_evp8_deepseek_qwen_smoke.py` 的 smoke subset selection；
- policy 从首次出现项目顺序改为
  `deterministic_project_frequency_stratified_first_candidate_per_top_project`；
- 重新生成
  `data/protocols/evp8_deepseek_qwen_smoke_check_only_v0_1.json`；
- 同步 README、docs index、EVP-8 execution plan、final roadmap、current project
  state 和 engineering notes；
- 本轮未调用模型 API，未生成 raw outputs，未提交 local config。

Verify:

- `python -m py_compile scripts\run_evp8_deepseek_qwen_smoke.py` 通过；
- `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`
  通过：
  - `check_only_status = passed`；
  - `packet_count = 35`；
  - `prompt_hashes_unique_count = 35`；
  - `boundary_error_count = 0`；
  - `schema_error_count = 0`；
  - `api_call_attempted = false`；
  - `raw_outputs_generated = false`；
  - selected smoke candidates =
    `evp8_smoke_candidate_0001`, `evp8_smoke_candidate_0011`,
    `evp8_smoke_candidate_0030`, `evp8_smoke_candidate_0040`,
    `evp8_smoke_candidate_0047`；
- 下一步仍是等待用户明确执行真实 DeepSeek/Qwen smoke，不自动调用 API。

Commit And Sync:

- 已提交本轮 no-API selection 修正：
  `21b78c8 Refine EVP-8 smoke subset selection`；
- 尝试 `git push origin main`；
- GitHub sync 失败：
  `Failed to connect to github.com port 443 after 21079 ms`；
- 按用户授权，GitHub 连续同步失败时不阻塞后续计划执行；本地 `main` 继续作为
  当前工作状态源。

## 2026-06-20 EVP-8 smoke execution packet

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 10]`；
- 最新提交为 `4aca3ad Record EVP-8 smoke sync failure`；
- EVP-8 protocol audit、DeepSeek/Qwen strict preflight、runner check-only 和
  local quality gate 均已通过；
- 真实 smoke 仍未获得用户明确执行授权；
- GitHub push 仍为网络级失败，已记录为不阻塞本地计划执行。

Plan:

1. 新增 no-API EVP-8 smoke execution packet builder；
2. 读取 tracked protocol/preflight/check-only summaries，输出 raw-output-free
   JSON/Markdown packet；
3. 明确 DeepSeek 先执行、Qwen 后执行；Qwen 只能在 DeepSeek smoke gate 通过后
   执行；
4. packet 必须记录 exact guard commands、execute commands、expected output
   paths、stop gates、cost-observability gate 和 claim boundary；
5. packet 必须明确 `api_call_attempted=false`、`raw_outputs_generated=false`，
   且不是 API 授权；
6. 同步 README、INDEX、EVP-8 execution plan、current project state 和
   engineering notes。

Acceptance:

- execution packet status 必须为 ready，且仍不调用 API；
- packet 中不得包含 API key value、rendered prompt text 或 raw output；
- exact execute commands 只能使用 ignored local config；
- `python scripts\audit_evp8_protocol_spec.py --check`、strict preflight、
  runner check-only 和 local quality gate 继续通过；
- staged diff 不包含 `.env`、`outputs/`、`artifacts/` 或 local config。

Execute:

- 新增 `scripts/write_evp8_smoke_execution_packet.py`；
- 生成 no-API execution packet：
  - `data/protocols/evp8_deepseek_qwen_smoke_execution_packet_v0_1.json`；
  - `docs/experiments/evp8_deepseek_qwen_smoke_execution_packet_v0_1.md`；
- packet 记录：
  - guard commands；
  - DeepSeek first execute command；
  - Qwen after-DeepSeek-gate execute command；
  - expected raw response paths under ignored `outputs/`；
  - tracked raw-output-free summary paths；
  - stop gates 和 claim boundary；
- 同步 README、docs index、EVP-8 execution plan、final roadmap、current project
  state 和 engineering notes；
- 本轮未调用模型 API，未生成 raw outputs，未提交 local config。

Verify:

- `python -m py_compile scripts\write_evp8_smoke_execution_packet.py` 通过；
- `python scripts\write_evp8_smoke_execution_packet.py --check` 通过：
  - `packet_status = ready`；
  - `api_call_attempted = false`；
  - `raw_outputs_generated = false`；
  - `rendered_prompt_text_stored = false`；
  - `execution_authorized_by_packet = false`；
  - `requires_explicit_user_command = true`；
  - DeepSeek command is first, Qwen command is gated after DeepSeek；
- 下一步仍是等待用户明确执行真实 DeepSeek/Qwen smoke，不自动调用 API。

## 2026-06-20 EVP-8 DeepSeek/Qwen 后续执行计划写入

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 12]`；
- 当前用户要求是“写入后续计划”，不是立即执行实验或调用 API；
- `docs/experiments/evp8_journal_scale_execution_plan_20260620.md` 已记录
  EVP-8 v0.1 protocol、DeepSeek/Qwen smoke runner、execution packet 和
  post-smoke audit scaffold；
- 真实 EVP-8 smoke 仍未执行，当前 post-smoke audit 预期状态仍是
  `waiting_for_execution`。

Plan:

1. 将后续计划写成 gate-based 执行序列，避免“一会儿继续”时误把普通继续当作
   API 授权；
2. 明确 G0 no-API revalidation、G1 DeepSeek smoke、G2 DeepSeek audit、G3
   Qwen smoke、G4 two-model smoke synthesis、G5 full-run decision、G6 later
   model completion；
3. 明确 DeepSeek 先于 Qwen，Qwen 必须等待 DeepSeek smoke audit 通过；
4. 明确 686-call full run 需要 smoke audit 后的单独授权；
5. 明确不发明 Qwen USD cost，不混合 protocol version，不把 two-model smoke
   写成 final five-model journal result；
6. 同步执行计划和索引入口，不生成 raw outputs，不读取 local config value，不调用
   API。

Acceptance:

- 后续计划必须给出可执行命令、验收条件、stop gates 和禁止 claim；
- 计划本身不得授权 API；
- 本轮不新增实验数据，不修改 prompt/schema/candidate set；
- `docs/experiments/evp8_journal_scale_execution_plan_20260620.md` 成为后续
  执行的 canonical gate 入口。

Execute:

- 在 `docs/experiments/evp8_journal_scale_execution_plan_20260620.md` 中新增
  `Immediate DeepSeek/Qwen Follow-up Plan`；
- 该计划要求：
  - G0 先重新运行 no-API guards；
  - G1 执行 `deepseek/deepseek-v4-pro` 35-call smoke；
  - G2 审计 DeepSeek summary，通过后才允许 Qwen；
  - G3 执行 `qwen/qwen3.7-max` 同一 frozen subset smoke；
  - G4 只做 two-model smoke synthesis，不写 final journal claim；
  - G5 后才决定是否准备 first-batch 686-call full-run packet；
  - G6 后续 Kimi/Devstral/Gemini 必须复用同一 frozen inputs；
- 本轮不调用 API，不生成 raw outputs。

Verify:

- 初次 patch 命中了非唯一的“下一步仍是等待用户明确执行真实 DeepSeek/Qwen
  smoke”锚点，新增段落一度插入到较早的 post-smoke 段前；
- 已按 long-plan patch anchor boundary 修复，将本节移动到当前执行日志末尾；
- `rg -n "EVP-8 DeepSeek/Qwen 后续执行计划写入|Immediate DeepSeek/Qwen Follow-up Plan"`
  确认：
  - execution plan 中新增 `Immediate DeepSeek/Qwen Follow-up Plan`；
  - current plan 中本节只出现一次且位于当前日志末尾；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过，
  `api_call_attempted=false`；
- `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
  通过，key value 未打印，API 未调用；
- `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`
  通过：
  - `packet_count = 35`；
  - `prompt_hashes_unique_count = 35`；
  - `api_call_attempted = false`；
  - `raw_outputs_generated = false`；
- `python scripts\write_evp8_smoke_execution_packet.py --check` 通过，
  `packet_status=ready` 且 `execution_authorized_by_packet=false`；
- `python scripts\audit_evp8_smoke_results.py --check` 通过，
  `audit_status=waiting_for_execution`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅提示 CRLF 工作区转换 warning；
- 本轮未调用模型 API，未生成 raw outputs，未读取 local config value。

## 2026-06-20 EVP-8 post-smoke audit self-test gate

Inspect:

- 当前工作区 clean，`main...origin/main`；
- 最新后续计划已明确普通 `continue` 不是真实 API 授权；
- 当前 `scripts/audit_evp8_smoke_results.py --check` 只能验证现有 tracked
  summary 状态；真实 smoke 前，它不会自然覆盖未来 summary 分支；
- 这留下一个 no-API 执行链路风险：DeepSeek-only partial、both-model passed、
  Qwen-before-DeepSeek order failure、parse/cost failure 等未来状态没有自测。

Plan:

1. 给 `scripts/audit_evp8_smoke_results.py` 增加 `--self-test`；
2. self-test 只使用临时目录中的 packet/summary JSON，不读取 raw outputs、不写
   tracked artifacts、不调用 API；
3. 覆盖五类状态：
   - no summaries => `waiting_for_execution`；
   - only DeepSeek passed => `partial_waiting_for_remaining_model`；
   - DeepSeek and Qwen passed => `passed`；
   - Qwen present before DeepSeek passed => `failed`；
   - parse/cost gate failed => `failed`；
4. 将 `--self-test` 加入 EVP-8 G0 no-API revalidation；
5. 同步 INDEX 和 engineering notes。

Acceptance:

- `python scripts\audit_evp8_smoke_results.py --self-test` 必须通过；
- `--self-test` 不得写 tracked outputs，不得生成 raw outputs，不得调用 API；
- `python scripts\audit_evp8_smoke_results.py --check` 当前仍应为
  `waiting_for_execution`；
- EVP-8 G0 no-API guards 和 local quality gate 继续通过。

Execute:

- 修改 `scripts/audit_evp8_smoke_results.py`，新增 `--self-test`；
- self-test 使用系统临时目录生成 synthetic packet/summary JSON，覆盖
  waiting、DeepSeek-only partial、both-model passed、Qwen-before-DeepSeek
  failed、parse/cost failed 五类状态；
- self-test 不写 tracked artifacts，不创建 raw outputs，不调用 API；
- 修改 `scripts/write_evp8_smoke_execution_packet.py`，将
  `python scripts\audit_evp8_smoke_results.py --self-test` 写入 future guard
  commands；
- 重新生成：
  - `data/protocols/evp8_deepseek_qwen_smoke_execution_packet_v0_1.json`；
  - `docs/experiments/evp8_deepseek_qwen_smoke_execution_packet_v0_1.md`；
- 同步 `docs/experiments/evp8_journal_scale_execution_plan_20260620.md`、
  `docs/INDEX.md` 和 `docs/experience/engineering_notes.md`。

Verify:

- `python -m py_compile scripts\audit_evp8_smoke_results.py scripts\write_evp8_smoke_execution_packet.py`
  通过；
- `python scripts\audit_evp8_smoke_results.py --self-test` 通过：
  - `case_count = 5`；
  - `waiting_for_execution`；
  - `partial_waiting_for_remaining_model`；
  - `passed`；
  - `qwen_without_deepseek => failed`；
  - `deepseek_parse_cost_failed => failed`；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
  - `raw_outputs_generated = false`；
  - `tracked_outputs_written = false`；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过；
- `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
  通过，key value 未打印，API 未调用；
- `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`
  通过，`packet_count = 35`，`prompt_hashes_unique_count = 35`；
- `python scripts\write_evp8_smoke_execution_packet.py --check` 通过，guard
  commands 已包含 self-test；
- `python scripts\audit_evp8_smoke_results.py --check` 通过，当前仍为
  `waiting_for_execution`；
- `git status --short --branch --ignored configs\evp8_deepseek_qwen.local.json outputs artifacts .env`
  确认 `.env`、local config、outputs、artifacts 仍为 ignored；
- 本轮未调用模型 API，未生成 raw outputs，未读取 local config value。

Commit And Sync:

- 已提交本轮 no-API self-test gate：
  `108a7b8 Add EVP-8 smoke audit self-test gate`；
- 尝试 `git push origin main`；
- GitHub sync 失败：
  `fatal: unable to access 'https://github.com/gaoming-a/research95.git/': Recv failure: Connection was reset`；
- 这是 network-level sync failure；按用户授权，GitHub 连续同步失败时不阻塞后续
  本地计划执行。

## 2026-06-20 EVP-8 post-smoke audit summary-contract tightening

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 2]`；
- 最新本地提交为 `0dead70 Record EVP-8 self-test sync failure`；
- GitHub push 仍处于网络失败边界，用户已允许不阻塞后续；
- `scripts/run_evp8_deepseek_qwen_smoke.py` 的 future executed summary 会写入
  `protocol_id`、`candidate_set_id`、`raw_responses_out`、`prompt_text_stored`
  等字段；
- `scripts/audit_evp8_smoke_results.py` 当前检查 parse/count/cost/model id，
  但未显式检查 protocol/candidate/raw-path/prompt-text summary contract。

Plan:

1. 收紧 post-smoke audit：执行后 summary 必须匹配 packet 的 `protocol_id` 和
   `candidate_set_id`；
2. 执行后 summary 的 `raw_responses_out` 必须等于 packet 中预声明的 raw
   response path，且仍位于 ignored `outputs/`；
3. 执行后 summary 必须记录 `prompt_text_stored=false`；
4. 扩展 `--self-test`，增加 raw path mismatch 失败用例；
5. 同步 EVP-8 execution plan 和 engineering notes。

Acceptance:

- `python scripts\audit_evp8_smoke_results.py --self-test` 必须通过，且新增
  mismatch 用例应失败；
- `python scripts\audit_evp8_smoke_results.py --check` 当前仍应为
  `waiting_for_execution`；
- 不调用 API，不读取 raw outputs，不生成 raw outputs；
- G0 no-API guards 和 local quality gate 继续通过。

Execute:

- 修改 `scripts/audit_evp8_smoke_results.py`：
  - executed summary 必须匹配 packet `protocol_id`；
  - executed summary 必须匹配 packet `candidate_set_id`；
  - executed summary `raw_responses_out` 必须匹配 packet 中预声明 raw path；
  - executed summary 必须记录 `prompt_text_stored=false`；
  - `--self-test` 新增 `deepseek_raw_path_mismatch` 失败用例；
- 同步 `docs/experiments/evp8_journal_scale_execution_plan_20260620.md` 中
  G2 DeepSeek audit 的验收条件；
- 同步 `docs/experience/engineering_notes.md`，记录 protocol/candidate/raw-path
  contract tightening。

Verify:

- `python -m py_compile scripts\audit_evp8_smoke_results.py` 通过；
- `python scripts\audit_evp8_smoke_results.py --self-test` 通过：
  - `case_count = 6`；
  - `deepseek_raw_path_mismatch => failed`；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
  - `raw_outputs_generated = false`；
  - `tracked_outputs_written = false`；
- `python scripts\audit_evp8_smoke_results.py --check` 通过，当前仍为
  `waiting_for_execution`；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过；
- `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
  通过，API 未调用、key value 未打印；
- `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`
  通过，`packet_count=35`、`prompt_hashes_unique_count=35`；
- `python scripts\write_evp8_smoke_execution_packet.py --check` 通过；
- `git status --short --branch --ignored configs\evp8_deepseek_qwen.local.json outputs artifacts .env`
  确认 `.env`、local config、outputs、artifacts 仍为 ignored；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- 本轮未调用模型 API，未读取 raw outputs，未生成 raw outputs。

Commit And Sync:

- 已提交本轮 post-smoke audit summary-contract tightening：
  `0c9ab98 Tighten EVP-8 smoke audit summary contract`；
- 尝试 `git push origin main`；
- GitHub sync 失败：
  `fatal: unable to access 'https://github.com/gaoming-a/research95.git/': Recv failure: Connection was reset`；
- 这是连续 network-level sync failure；按用户授权，不阻塞后续本地计划执行，且
  不继续为同一网络问题循环制造 push-failure-only 提交。

## 2026-06-20 EVP-8 actual model/provider summary contract

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 4]`；
- 最新本地提交为 `2783545 Record EVP-8 contract audit sync failure`；
- 这条自动续跑不是明确 API 授权，因此本轮仍只能做 no-API gate/contract work；
- `scripts/run_evp8_deepseek_qwen_smoke.py` 的 future raw records 会写入
  `actual_model_id`，但 tracked executed summary 当前不聚合实际返回 model id；
- `scripts/audit_evp8_smoke_results.py` 不读取 raw outputs，因此如果 tracked
  summary 不记录 actual model/provider aggregate，未来 audit 无法检查
  provider/model drift；
- execution packet 的 execute command records 当前也未显式记录 expected
  request model id 和 provider route。

Plan:

1. 让 smoke runner executed summary 写入 raw-output-free model/provider
   aggregate：
   - `request_model_id_counts`；
   - `actual_model_id_counts`；
   - `actual_model_id_missing_count`；
   - `provider_route_counts`；
2. 让 execution packet 的 execute command records 显式记录 expected
   `request_model_id` 和 `provider_route`；
3. 让 post-smoke audit 在 tracked summary 上检查：
   - expected request model id；
   - expected provider route；
   - actual model id 不缺失；
   - request/provider aggregate 只包含 expected value；
4. 扩展 no-API `--self-test`，增加 actual model missing/drift failure cases；
5. 同步 execution plan、INDEX/engineering notes/current plan；
6. 不调用 API，不读取 raw outputs，不生成 raw outputs。

Acceptance:

- `python scripts\audit_evp8_smoke_results.py --self-test` 必须覆盖 actual model
  missing/drift 并通过；
- `python scripts\write_evp8_smoke_execution_packet.py --check` 必须重新生成
  packet，并包含 expected request/provider fields；
- 当前 `python scripts\audit_evp8_smoke_results.py --check` 仍应为
  `waiting_for_execution`；
- G0 no-API guards 和 local quality gate 继续通过。

Execute:

- 修改 `scripts/run_evp8_deepseek_qwen_smoke.py`：
  - executed parsed records 增加 `request_model_id`、`configured_model_id`、
    `actual_model_id`、`provider_route`；
  - executed summary 增加 `request_model_id_counts`、
    `configured_model_id_counts`、`actual_model_id_counts`、
    `actual_model_id_missing_count`、`provider_route_counts`；
- 修改 `scripts/write_evp8_smoke_execution_packet.py`：
  - execute command records 增加 expected `request_model_id` 和
    `provider_route`；
  - Markdown packet 输出 request model/provider route；
- 修改 `scripts/audit_evp8_smoke_results.py`：
  - audit summary 检查 expected request model id；
  - audit summary 检查 expected provider route；
  - audit summary 检查 request/provider aggregate counts；
  - audit summary 检查 actual model id 不缺失；
  - `--self-test` 新增 actual model missing 和 request model drift 失败用例；
- 重新生成 execution packet JSON/Markdown；
- 同步 EVP-8 execution plan、docs index 和 engineering notes。

Verify:

- `python -m py_compile scripts\run_evp8_deepseek_qwen_smoke.py scripts\write_evp8_smoke_execution_packet.py scripts\audit_evp8_smoke_results.py`
  通过；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过；
- `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
  通过，API 未调用、key value 未打印；
- `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`
  通过，`packet_count=35`、`prompt_hashes_unique_count=35`；
- `python scripts\write_evp8_smoke_execution_packet.py --check` 通过，packet
  execute records 包含 `request_model_id` 和 `provider_route`；
- `python scripts\audit_evp8_smoke_results.py --self-test` 通过：
  - `case_count = 8`；
  - `deepseek_actual_model_missing => failed`；
  - `deepseek_request_model_drift => failed`；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
  - `raw_outputs_generated = false`；
  - `tracked_outputs_written = false`；
- `python scripts\audit_evp8_smoke_results.py --check` 通过，当前仍为
  `waiting_for_execution`；
- `git status --short --branch --ignored configs\evp8_deepseek_qwen.local.json outputs artifacts .env`
  确认 `.env`、local config、outputs、artifacts 仍为 ignored；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅提示 CRLF 工作区转换 warning；
- 本轮未调用模型 API，未读取 raw outputs，未生成 raw outputs。

Commit And Sync:

- 已提交本轮 actual model/provider aggregate contract：
  `5a1e69c Track EVP-8 smoke actual model aggregates`；
- `git push origin main` 成功；
- 远端 `origin/main` 已同步到本轮提交。

## 2026-06-20 EVP-8 G0 guard one-command summary

Inspect:

- 当前工作区 clean，`main...origin/main`；
- 最新提交为 `cf4ace5 Record EVP-8 actual model sync`；
- 自动续跑不是明确 API 授权，本轮仍不得执行 `--execute`；
- EVP-8 G0 guards 已写在 execution plan 和 execution packet 中，但仍需要人工
  逐条运行：
  - protocol audit；
  - strict local preflight；
  - smoke runner check-only；
  - execution packet check；
  - post-smoke audit self-test；
  - post-smoke audit check；
  - ignored boundary status；
- 这会增加真实 API 前漏跑 guard 或运行顺序漂移的风险。

Plan:

1. 新增 no-API G0 guard 汇总脚本，一键运行上述 guard commands；
2. 脚本只记录命令、exit code、parsed status、raw-output/API/prompt-text
   boundary，不保存 API key、local config 内容、raw responses 或 rendered
   prompts；
3. 生成 tracked summary artifact：
   - `data/protocols/evp8_deepseek_qwen_g0_guard_summary_v0_1.json`；
   - `docs/experiments/evp8_deepseek_qwen_g0_guard_summary_v0_1.md`；
4. 将 execution plan 的 G0 入口改为优先运行该脚本，再保留单条 commands
   作为展开明细；
5. 同步 docs index 和 engineering notes。

Acceptance:

- `python scripts\check_evp8_deepseek_qwen_g0.py --check` 必须通过；
- summary 必须明确 `api_call_attempted=false`、`raw_outputs_read=false`、
  `raw_outputs_generated=false`、`rendered_prompt_text_read=false`；
- 当前 post-smoke audit 仍应为 `waiting_for_execution`；
- ignored `.env`、local config、outputs、artifacts 不得被 staged；
- local quality gate 和 `git diff --check` 继续通过。

Execute:

- 新增 `scripts/check_evp8_deepseek_qwen_g0.py`；
- 脚本按固定顺序运行：
  - `python scripts\audit_evp8_protocol_spec.py --check`；
  - `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`；
  - `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`；
  - `python scripts\write_evp8_smoke_execution_packet.py --check`；
  - `python scripts\audit_evp8_smoke_results.py --self-test`；
  - `python scripts\audit_evp8_smoke_results.py --check`；
  - `git status --short --branch --ignored configs\evp8_deepseek_qwen.local.json outputs artifacts .env`；
- 生成 tracked summary artifacts：
  - `data/protocols/evp8_deepseek_qwen_g0_guard_summary_v0_1.json`；
  - `docs/experiments/evp8_deepseek_qwen_g0_guard_summary_v0_1.md`；
- summary 只保存 parsed no-secret status 和 ignored-boundary stdout，不保存
  parsed JSON command 的长 stdout，不保存本机 Python 绝对路径；
- 同步 EVP-8 execution plan、docs index 和 engineering notes。

Verify:

- `python -m py_compile scripts\check_evp8_deepseek_qwen_g0.py scripts\run_evp8_deepseek_qwen_smoke.py scripts\write_evp8_smoke_execution_packet.py scripts\audit_evp8_smoke_results.py`
  通过；
- `python scripts\check_evp8_deepseek_qwen_g0.py --check` 通过：
  - `guard_status = passed`；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
  - `raw_outputs_generated = false`；
  - `rendered_prompt_text_read = false`；
  - `post_smoke_observed_status = waiting_for_execution`；
  - ignored boundary entries include `.env`、`artifacts/`、
    `configs/evp8_deepseek_qwen.local.json`、`outputs/`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- 本轮未调用模型 API，未读取 raw outputs，未生成 raw outputs。

Commit And Sync:

- 已提交本轮 G0 guard one-command summary：
  `6721bc4 Add EVP-8 G0 guard summary check`；
- 尝试 `git push origin main`；
- GitHub sync 失败：
  `fatal: unable to access 'https://github.com/gaoming-a/research95.git/': Failed to connect to github.com port 443 after 21134 ms: Could not connect to server`；
- 这是连续 network-level sync failure；按用户授权，不阻塞后续本地计划执行。

## 2026-06-20 EVP-8 G0 expected-output absence guard

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 2]`；
- 最新本地提交为 `fdce346 Record EVP-8 G0 guard sync failure`；
- 自动续跑不是明确 API 授权，本轮仍不得执行 `--execute`；
- 当前 G0 guard 已能一键验证 protocol/preflight/check-only/execution
  packet/post-smoke audit/ignored boundary；
- 但 G0 guard 尚未检查 execution packet 中预声明的 DeepSeek/Qwen raw
  responses 和 tracked summary 输出路径是否已经存在；
- 若这些路径有旧残留，真实 `--execute` 会触发 overwrite refusal，但会延迟到 API
  执行入口才发现，不利于真实执行前的 no-API readiness。

Plan:

1. 扩展 `scripts/check_evp8_deepseek_qwen_g0.py`，读取 execution packet；
2. 检查每个 execute command 的 expected raw response path 和 tracked summary
   path 当前均不存在；
3. 将该检查写入 tracked G0 summary 和 Markdown；
4. 同步 execution plan、docs index 和 engineering notes；
5. 重新运行 G0 guard 和 local quality gate；
6. 不调用 API，不读取 raw outputs，不生成 raw outputs。

Acceptance:

- `python scripts\check_evp8_deepseek_qwen_g0.py --check` 必须通过；
- G0 summary 必须包含 expected output absence check；
- 若未来 expected raw/summary output 已存在，G0 应先失败并阻止 API 前进；
- 当前 post-smoke audit 仍应为 `waiting_for_execution`；
- ignored `.env`、local config、outputs、artifacts 不得被 staged。

Execute:

- 扩展 `scripts/check_evp8_deepseek_qwen_g0.py`：
  - 读取 `data/protocols/evp8_deepseek_qwen_smoke_execution_packet_v0_1.json`；
  - 对每个 execute command 检查 `raw_responses` 和 `tracked_summary` 当前均不存在；
  - 将 `expected_output_absence` 写入 JSON/Markdown summary；
  - 若任一预期输出已存在，`guard_status` 变为 `failed`；
- 同步 EVP-8 execution plan、docs index 和 engineering notes，明确 G0 会在 API
  前检查 stale outputs。

Verify:

- `python -m py_compile scripts\check_evp8_deepseek_qwen_g0.py` 通过；
- `python scripts\check_evp8_deepseek_qwen_g0.py --check` 通过：
  - `guard_status = passed`；
  - `expected_outputs_exist = false`；
  - `checked_output_count = 4`；
  - `existing_output_count = 0`；
  - DeepSeek/Qwen expected `raw_responses` 和 `tracked_summary` 均不存在；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
  - `raw_outputs_generated = false`；
  - `post_smoke_observed_status = waiting_for_execution`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- 本轮仍未调用模型 API，未读取 raw outputs，未生成 raw outputs。

## 2026-06-20 EVP-8 G5 no-API first-batch full-run packet closure

Inspect:

- 当前 Git 状态 clean，`main...origin/main`；
- 最新提交为 `b596333 Close EVP-8 DeepSeek Qwen smoke`；
- smoke audit 与 G4 synthesis 均已 `passed`；
- canonical 下一步为 G5 no-API first-batch full-run packet，不是自动执行
  686-call full run。

Execute:

- 扩展 `scripts/run_evp8_deepseek_qwen_smoke.py`：
  - 新增 `--run-scope smoke|full`；
  - 默认保持 `smoke`，旧 smoke 命令兼容；
  - `full` scope 覆盖 frozen EVP-8 v0.1 的 98 candidates x 7 levels =
    686 prompts；
  - `execute` summary 在 full scope 写入 `run_gate` 和
    `first_batch_full_gate`，并继续保留 per-level aggregates、model/provider
    counts 和 USD/CNY cost observability；
- 新增 G5 first-batch full-run check-only artifact：
  `data/protocols/evp8_deepseek_qwen_first_batch_full_check_only_v0_1.json`；
- 新增 G5 no-API first-batch full-run packet：
  `data/protocols/evp8_deepseek_qwen_first_batch_full_run_packet_v0_1.json`
  及 Markdown companion；
- 新增 post-full-run audit scaffold：
  `scripts/audit_evp8_first_batch_full_results.py`；
- 新增 first-batch synthesis scaffold：
  `scripts/summarize_evp8_first_batch_full_synthesis.py`；
- 同步 canonical execution plan、short-state、final roadmap、INDEX 和
  engineering notes。

Verify:

- `python -m py_compile scripts\run_evp8_deepseek_qwen_smoke.py scripts\write_evp8_first_batch_full_run_packet.py scripts\audit_evp8_first_batch_full_results.py scripts\summarize_evp8_first_batch_full_synthesis.py`
  通过；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过；
- `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
  通过；
- `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`
  通过，smoke scope 仍为 35 packets；
- `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --run-scope full --config configs\evp8_deepseek_qwen.local.json`
  通过：
  - `packet_count = 686`；
  - `candidate_count = 98`；
  - `prompt_count = 686`；
  - `prompt_hashes_unique_count = 686`；
  - `api_call_attempted = false`；
  - `raw_outputs_generated = false`；
- `python scripts\write_evp8_first_batch_full_run_packet.py --check` 通过：
  `packet_status = ready`，`execution_authorized_by_packet = false`；
- `python scripts\audit_evp8_first_batch_full_results.py --check` 通过：
  `audit_status = waiting_for_execution`；
- `python scripts\summarize_evp8_first_batch_full_synthesis.py --check` 通过：
  `synthesis_status = waiting_for_execution`。

Next Gate:

- 当前 G5 已完成；下一步只有在用户再次明确授权 first-batch full run 后，才可
  执行 DeepSeek 686-call full run；
- Qwen 686-call full run 仍必须等待 DeepSeek full-run audit 通过；
- 本轮没有调用模型 API，没有生成 raw outputs，没有启动 686-call full run。

## 2026-06-20 EVP-8 G5 no-API first-batch full-run packet

Inspect:

- 当前 Git 状态 clean，`main...origin/main`；
- 最新提交为 `b596333 Close EVP-8 DeepSeek Qwen smoke`；
- EVP-8 Phase 1 DeepSeek/Qwen smoke 已闭合：
  - post-smoke audit `passed`；
  - G4 smoke synthesis `passed`；
  - 两模型各 35/35 parse-valid；
- canonical EVP-8 plan 的当前 next gate 是 G5：生成独立 no-API
  first-batch full-run packet；
- 当前 `scripts/run_evp8_deepseek_qwen_smoke.py` 只支持 smoke scope；config
  已有 `full` planned fields，但还没有可审计的 full-scope check-only /
  execute command。

Plan:

1. 扩展现有 guarded runner，使其支持 `--run-scope smoke|full`：
   - 默认仍为 `smoke`，保持旧 smoke 命令兼容；
   - `full` scope 只使用同一 frozen EVP-8 v0.1 candidate set、levels、
     prompt、schema、parser、temperature、4096 output budget 和 evaluator
     joins；
   - 本轮只运行 `full` check-only，不执行 API；
2. 新增 G5 no-API first-batch full-run packet：
   - 记录 DeepSeek/Qwen 686-call full-run exact execute commands；
   - 记录 expected raw outputs、tracked summaries、cost fields、per-level
     aggregate requirements、audit/synthesis commands 和 stop gates；
   - packet 本身必须 `execution_authorized_by_packet = false`；
3. 同步 `docs/experiments/evp8_journal_scale_execution_plan_20260620.md`、
   `docs/plans/current_project_state_zh.md`、`docs/plans/final_paper_roadmap_zh.md`、
   `docs/INDEX.md` 和 `docs/experience/engineering_notes.md`；
4. 运行 no-API validations、local quality gate、diff/sensitive checks；
5. 提交并同步 GitHub。

Acceptance:

- `full` check-only 必须生成 tracked summary，且：
  - `packet_count = 686`；
  - `candidate_count = 98`；
  - `prompt_count = 686`；
  - `prompt_hashes_unique_count = 686`；
  - `api_call_attempted = false`；
  - `raw_outputs_generated = false`；
  - `prompt_text_stored = false`；
- G5 packet 必须 ready，但不授权 API；
- G5 packet 的 execute commands 必须只指向 first-batch DeepSeek/Qwen full
  scope，不包含 Kimi/Devstral/Gemini；
- 不启动 686-call full run；后续 full run 仍需要用户再次明确授权。

## 2026-06-20 EVP-8 Phase 1 DeepSeek/Qwen smoke execution closure

Inspect:

- 用户已明确授权执行：`按当前计划执行 EVP-8 Phase 1 DeepSeek/Qwen smoke`；
- 本轮范围只覆盖 EVP-8 G0-G4 smoke path，不授权 686-call full run、不授权
  Kimi/Devstral/Gemini、不授权 five-model journal conclusion；
- 当前本地仍为 `main...origin/main [ahead 1]`，远端停在
  `1d235ee Sync EVP-8 smoke packet guards`，本地已有未推送 staged follow-up
  plan commit。

Plan:

1. API 前先更新本计划并运行 G0 no-API guard；
2. DeepSeek V4 Pro smoke 先执行并立刻 audit；
3. 只有 DeepSeek audit 通过才执行 Qwen3.7 Max smoke；
4. Qwen 后运行 post-smoke audit 和 G4 smoke synthesis；
5. 若遇到 parse/cost/model/provider/raw-output gate 失败，先诊断和修复，不进入
   后续模型或 full run。

Execute:

- G0 no-API revalidation 在 API 前通过：
  - `guard_status = passed`；
  - `expected_outputs_exist = false`；
  - `post_smoke_observed_status = waiting_for_execution`；
  - `api_call_attempted = false`；
- 首次 DeepSeek smoke 使用 `max_output_tokens = 1024`，写出 35 条 ignored raw
  records，但 15/35 parse invalid，runner 以 `smoke_gate = blocked` 退出；
- 诊断确认 DeepSeek invalid records 均为 output budget failure：
  `finish_reason = length`，大量 completion budget 用于 `reasoning_content`，
  final content 为空或非 JSON；
- 已将失败的 1024-token outputs 移入 ignored diagnostic path，并把 EVP-8
  DeepSeek/Qwen routing budget 从 1024 调整为 4096；
- 修复后重新运行 protocol audit、cost/baseline dry-run、strict preflight、
  smoke check-only、execution packet check、post-smoke audit self-test/check、
  G4 synthesis self-test/check 和 G0 guard，均通过；
- 4096-budget DeepSeek smoke 通过：
  - `review_count = 35`；
  - `parse_valid_count = 35`；
  - `invalid_parse_count = 0`；
  - `usage_cost_gate = passed`；
  - `smoke_gate = passed`；
  - tracked summary 不存 raw response body 或 rendered prompt text；
- DeepSeek audit 通过后执行 Qwen3.7 Max smoke。Qwen 35/35 parse valid，但官方
  response 只返回 token usage，不返回 provider USD cost，初次 summary 因
  `unknown_cost_record_count = 35` 阻塞；
- 修复成本可观测性：
  - 不发明 USD 成本、不做汇率换算；
  - 依据阿里云百炼官方 qwen3.7-max CNY pricing，新增 `cost_cny` 和
    `cost_currency`；
  - 保留 `cost_usd` 给 DeepSeek/provider USD 成本；
  - 从已有 ignored Qwen raw 的 usage 字段重建 ignored summary，没有重复调用
    Qwen API；
- Qwen repaired summary：
  - `review_count = 35`；
  - `parse_valid_count = 35`；
  - `invalid_parse_count = 0`；
  - `usage_cost_gate = passed`；
  - `smoke_gate = passed`；
  - `cost_currency_counts = {"CNY": 35}`；
  - `total_cost_cny = 1.8813`；
- `python scripts\audit_evp8_smoke_results.py --check` 通过，两个模型 status
  均为 `passed`；
- `python scripts\summarize_evp8_smoke_synthesis.py --check` 通过，G4 synthesis
  status 为 `passed`，仅报告 frozen smoke subset 的 descriptive per-level
  decision counts：DeepSeek/Qwen 在 E0-E6 每层均为 5 个 `escalate`。

Diagnose / Repair Notes:

- DeepSeek 1024-token failure 是 execution-budget bug，不是 protocol/prompt/
  schema/candidate/evaluator-join bug，因此保留 protocol id
  `evp8_journal_full_ladder_v0_1`；
- Qwen cost blocker 是 non-USD cost observability gap。修复后 gate 只承认可控
  CNY token-pricing estimate，不把它写成 provider-reported USD bill；
- G0 guard 是执行前 guard。smoke 输出存在后，G0 的 expected-output absence
  会按设计失败；post-smoke 验收必须使用 result audit 和 G4 synthesis。

Verify:

- `python -m py_compile scripts\preflight_evp8_deepseek_qwen.py scripts\run_evp8_deepseek_qwen_smoke.py scripts\audit_evp8_protocol_spec.py scripts\build_evp8_cost_baseline_dry_run.py`
  通过；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过；
- `python scripts\build_evp8_cost_baseline_dry_run.py --check` 通过；
- `python scripts\audit_evp8_smoke_results.py --check` 通过：
  `audit_status = passed`；
- `python scripts\summarize_evp8_smoke_synthesis.py --check` 通过：
  `synthesis_status = passed`；
- `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
  通过，仍不打印 key value、不调用 API；
- `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`
  通过，仍不生成 raw outputs；
- `python scripts\audit_evp8_smoke_results.py --self-test` 和
  `python scripts\summarize_evp8_smoke_synthesis.py --self-test` 均通过；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅有 Windows CRLF 工作区转换 warning；
- 本轮真实 API 调用仅限已授权的 DeepSeek/Qwen 5-candidate x 7-level smoke；
  没有启动 686-call full run。

Next Gate:

- 下一步不是继续跑模型，而是 G5：生成并审计独立 no-API first-batch
  full-run packet；
- 686-call DeepSeek/Qwen first-batch full run 需要用户再次明确授权；
- 如果后续要改 protocol/prompt/schema/candidate/evaluator join，必须 bump
  EVP-8 protocol version 并重跑受影响模型。

## 2026-06-20 EVP-8 Phase 1 DeepSeek/Qwen smoke execution

Inspect:

- 用户已明确给出授权目标：
  `按当前计划执行 EVP-8 Phase 1 DeepSeek/Qwen smoke`；
- 当前工作区 clean，`main...origin/main [ahead 1]`；
- 最新本地提交为 `17d7312 Plan EVP-8 staged follow-up gates`，远端仍停在
  `1d235ee Sync EVP-8 smoke packet guards`；
- 该 ahead 状态是已知 GitHub network-level sync failure，不阻塞本轮本地执行；
- `docs/experiments/evp8_journal_scale_execution_plan_20260620.md` 明确本轮只覆盖
  G0-G4：G0 no-API revalidation、DeepSeek smoke、DeepSeek audit、Qwen smoke、
  two-model smoke synthesis；
- 本轮不得启动 G5 之后的 first-batch 686-call full run，不得补 Kimi/Devstral/Gemini，
  不得写 final five-model journal conclusion。

Plan:

1. 运行 G0 no-API revalidation：
   - `python scripts\check_evp8_deepseek_qwen_g0.py --check`；
   - 若 G0 发现 stale expected outputs、preflight/check-only/audit/self-test
     failure 或 ignored-boundary failure，停止并诊断；
2. 若 G0 通过，执行 DeepSeek V4 Pro smoke：
   - `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --config configs\evp8_deepseek_qwen.local.json --model-id deepseek/deepseek-v4-pro`；
3. 立刻运行 post-smoke audit：
   - `python scripts\audit_evp8_smoke_results.py --check`；
4. 只有 DeepSeek audit 通过，才执行 Qwen3.7 Max smoke：
   - `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --config configs\evp8_deepseek_qwen.local.json --model-id qwen/qwen3.7-max`；
5. 再次运行 post-smoke audit 和 G4 synthesis：
   - `python scripts\audit_evp8_smoke_results.py --check`；
   - `python scripts\summarize_evp8_smoke_synthesis.py --check`；
6. 更新 raw-output-free tracked summaries、current plan、short-state、execution
   plan、engineering notes 和 docs index；
7. 运行 local quality gate、diff/sensitive checks；
8. 只暂存本轮相关 tracked artifacts/docs，提交并尝试 GitHub push。若 push 仍为
   network-level failure，记录后按用户规则继续。

Acceptance:

- G0 guard 通过，且 API 前 expected DeepSeek/Qwen raw-response 和 tracked-summary
  paths 均不存在；
- DeepSeek smoke 产生 35 条 planned review records，tracked summary 不含 raw
  response body、rendered prompt text、API key 或 local config value；
- Qwen smoke 只能在 DeepSeek audit 通过后执行，并使用同一 frozen EVP-8 v0.1
  smoke subset、prompt/schema 和 evaluator joins；
- G4 synthesis 只基于 tracked summary/audit fields，允许描述 frozen 5-candidate
  smoke subset 的 two-model readiness 和 per-level decision pattern；
- 不声明 full-cohort、five-model、LLM superiority 或 evidence-level effectiveness
  final result；
- 本轮 raw responses 只能留在 ignored `outputs/`，不得提交。

Execute:

- G0 no-API revalidation 已通过：
  - `guard_status = passed`；
  - `expected_outputs_exist = false`；
  - `post_smoke_observed_status = waiting_for_execution`；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
  - `raw_outputs_generated = false`；
- 执行 DeepSeek V4 Pro smoke：
  `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --config configs\evp8_deepseek_qwen.local.json --model-id deepseek/deepseek-v4-pro`；
- DeepSeek smoke 写出 35 条 ignored raw records 和 ignored raw-output-free summary，
  但 runner 以 `smoke_gate = blocked` 退出；
- `python scripts\audit_evp8_smoke_results.py --check` 失败，正式 gate 阻止
  Qwen 执行；
- tracked audit 显示：
  - `review_count = 35`；
  - `parse_valid_count = 20`；
  - `invalid_parse_count = 15`；
  - `usage_cost_gate = passed`；
  - `smoke_gate = blocked`；
  - DeepSeek model/provider/cost observability checks 通过；
- 受控读取 ignored raw output 仅用于失败归因，不把 raw response body 写入 tracked
  docs：15 条 invalid 都是 `invalid_json:No JSON object found in model response`；
  这些记录均为 `finish_reason = length`、`completion_tokens = 1024`，多数 final
  `content` 为空且 completion budget 被 `reasoning_content` 消耗；
- 诊断：`max_output_tokens = 1024` 对 DeepSeek V4 Pro 的 EVP-8 prompt 太低，
  属于 execution-budget bug，不是 protocol/prompt/schema/candidate-set/evaluator
  join bug。

Repair Plan:

1. 不执行 Qwen；
2. 保留 failed 1024-token run 到 ignored diagnostic paths，释放默认 smoke 输出路径；
3. 将 tracked example config 和 ignored local config 的 `max_output_tokens` 从
   1024 提高到 4096；
4. 重新运行 strict preflight、smoke check-only、execution packet 和 G0 guard；
5. 只有 repaired G0 重新通过，才重新执行 DeepSeek smoke；
6. 仍不改变 EVP-8 v0.1 packets、prompt、schema、candidate set 或 evaluator joins。

Commit And Sync:

- 已提交本轮 G0 expected-output absence guard：
  `d94437c Check EVP-8 G0 expected output absence`；
- `git push origin main` 成功；
- 远端 `origin/main` 已同步到本轮提交，并包含此前本地 ahead 的提交。

## 2026-06-20 EVP-8 Phase 1 DeepSeek/Qwen smoke follow-up plan

Inspect:

- 当前 EVP-8 Phase 0 no-API gates 已达到真实 smoke 前的 readiness：
  - protocol spec audit passed；
  - strict local preflight passed；
  - smoke runner check-only passed；
  - execution packet ready；
  - post-smoke audit scaffold/self-test passed；
  - G0 one-command guard passed；
  - expected DeepSeek/Qwen raw-response 和 tracked-summary 输出路径均不存在；
- 当前计划仍未授权任何模型 API 调用；
- 下一次执行必须从本段重新 Inspect 开始，不得只凭本段记录直接调用 API。

Authorization Boundary:

- 只有当用户明确指向本段或 EVP-8 Phase 1 DeepSeek/Qwen smoke/API 执行时，才可进入
  真实 API 步骤；
- 泛泛的“继续”仍只能做 no-API 检查、文档修订或执行链路修复；
- 本阶段只允许执行 DeepSeek/Qwen 5-candidate x 7-level smoke，不允许顺手进入
  686-call full run，也不允许补 Kimi/Devstral/Gemini。

Plan:

1. 重新检查 `AGENTS.md`、`docs/plans/current_plan_zh.md`、EVP-8 execution
   plan、G0 guard summary、smoke execution packet 和 Git 状态；
2. 运行 G0 no-API revalidation：
   - `python scripts\check_evp8_deepseek_qwen_g0.py --check`；
   - `git diff --check`；
   - 检查 `.env`、`configs/*.local.json`、`outputs/`、`artifacts/` 仍未 staged；
3. 如果 G0 重新生成 tracked summary，使工作区出现仅限 no-API guard summary 的
   diff，则先提交并尝试同步该 no-API guard refresh，再进入真实 API；
4. 运行 DeepSeek V4 Pro smoke：
   - `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --config configs\evp8_deepseek_qwen.local.json --model-id deepseek/deepseek-v4-pro`；
5. 立刻运行 post-smoke audit：
   - `python scripts\audit_evp8_smoke_results.py --check`；
6. 只有 DeepSeek audit 通过，才运行 Qwen3.7 Max smoke：
   - `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --config configs\evp8_deepseek_qwen.local.json --model-id qwen/qwen3.7-max`；
7. 再次运行 post-smoke audit，并更新 raw-output-free summaries、current plan、
   engineering notes 和 docs index；
8. 提交并同步本阶段 tracked artifacts/docs；
9. 停在 two-model smoke synthesis，不启动 full run。

Acceptance:

- G0 guard 通过，且 `api_call_attempted=false`、`raw_outputs_read=false`、
  `raw_outputs_generated=false`、`rendered_prompt_text_read=false`；
- DeepSeek smoke 产生 35 条 planned review records，tracked summary 无 raw
  response body、无 rendered prompt text、无 API key/local config value；
- DeepSeek audit 通过后才允许 Qwen smoke；
- Qwen smoke 使用完全相同的 frozen EVP-8 v0.1 smoke subset、prompt/schema 和
  evaluator joins；
- Qwen audit 通过后，只能声明：
  DeepSeek/Qwen 在 EVP-8 v0.1 frozen smoke subset 上的执行、解析、边界和初步
  evidence-level decision pattern；
- 不得声明：
  five-model journal conclusion、full-cohort generalization、LLM superiority over
  deterministic baselines、E0-E6 effectiveness final result。

Stop Conditions:

- 任一 G0 guard/preflight/check-only/audit/self-test 失败；
- expected raw/summary output 在 API 前已经存在；
- smoke runner 拒绝执行、API auth/route/model id 不匹配、parse/schema invalid；
- usage/cost observability 缺失或返回模型/provider drift 未被 tracked summary
  记录；
- tracked summary 出现 raw response、rendered prompt、API key 或 local config
  value；
- DeepSeek audit 未通过时，禁止运行 Qwen；
- Qwen audit 未通过时，禁止写 two-model positive conclusion；
- GitHub sync 若再次出现 network-level failure，按用户授权记录后继续本地计划，
  不为同一网络问题反复制造 push-failure-only 提交。

Next Manual Command:

- 若用户接下来要真实执行，应明确说：
  `按当前计划执行 EVP-8 Phase 1 DeepSeek/Qwen smoke`。

## 2026-06-20 EVP-8 short-state handoff refresh

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 1]`；
- 未同步本地语义提交为：
  `7426556 Plan EVP-8 DeepSeek Qwen smoke execution`；
- 最近 `git push origin main` 仍失败在 network-level GitHub connection；
- 用户已允许连续 GitHub 同步失败时继续本地计划执行；
- `docs/plans/current_project_state_zh.md` 是新会话短入口，但其 Git 同步段仍列出
  较早的语义锚点，且 EVP-8 下一步段尚未明确记录 G0 expected-output absence
  guard 和 `7426556` 本地计划提交；
- 当前继续指令不是明确 EVP-8 Phase 1 smoke/API 授权，因此本轮仍不得执行
  `--execute`。

Plan:

1. 刷新 `docs/plans/current_project_state_zh.md` 的当前同步状态：
   - 记录 latest local semantic commit 为 `7426556`；
   - 记录 `origin/main` 当前仍停在 `d94437c`；
   - 明确 ahead 1 是 GitHub network sync failure，不是 tracked 工作区脏状态；
2. 在 EVP-8 决策门中补充：
   - G0 one-command guard；
   - expected raw/summary output absence；
   - 明确下一步人工授权语句；
3. 不改实验协议、不调用 API、不生成 tracked model outputs；
4. 运行 targeted 文档检查、G0 no-API guard 到 ignored `outputs/`、local quality
   gate 和 `git diff --check`；
5. 仅提交本轮文档刷新；GitHub push 若继续网络失败，按既定规则不阻塞。

Acceptance:

- `current_project_state_zh.md` 不再只停留在旧 Git 同步锚点；
- 该短入口明确下一步不是自动 API，而是等待：
  `按当前计划执行 EVP-8 Phase 1 DeepSeek/Qwen smoke`；
- no-API G0 guard 仍通过，且 `expected_outputs_exist=false`；
- 工作区不 staged `.env`、`configs/*.local.json`、`outputs/`、`artifacts/`。

## 2026-06-20 EVP-8 smoke per-level summary contract

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 2]`；
- 当前继续指令不是明确 EVP-8 Phase 1 smoke/API 授权，本轮不得执行
  `--execute`；
- `scripts/run_evp8_deepseek_qwen_smoke.py` 的 executed summary 已记录整体
  `decision_counts`、request/configured/actual model aggregates 和 provider
  route aggregates；
- 但 G4 two-model smoke synthesis 允许的 claim 包含 evidence-level decision
  pattern，而当前 tracked summary 尚未记录 `E0-E6` per-level decision/count
  aggregates；
- 如果不在 tracked raw-output-free summary 中补齐 per-level aggregates，未来
  smoke 后只能读取 ignored raw responses 才能做 evidence-level pattern，这违反
  post-smoke audit 不读取 raw outputs 的边界。

Plan:

1. 扩展 smoke runner executed summary，加入 raw-output-free per-level aggregates：
   - `review_count_by_evidence_level`；
   - `parse_valid_count_by_evidence_level`；
   - `invalid_parse_count_by_evidence_level`；
   - `decision_counts_by_evidence_level`；
2. 扩展 post-smoke audit：
   - 检查每个 `E0-E6` 均有 5 条 review；
   - 检查每个 `E0-E6` 均有 5 条 parse-valid；
   - 检查 per-level decision counts 总和与每层 review count 一致；
3. 扩展 `--self-test` 覆盖缺失或漂移的 per-level aggregate failure case；
4. 同步 execution plan、short-state、INDEX 和 engineering notes；
5. 运行 no-API py_compile、self-test、G0 guard、local quality gate 和 diff check；
6. 不调用 API，不读取 raw outputs，不生成 raw outputs。

Acceptance:

- `python scripts\audit_evp8_smoke_results.py --self-test` 必须覆盖 per-level
  aggregate drift 并通过；
- `python scripts\check_evp8_deepseek_qwen_g0.py --check --json-out outputs\evp8_g0_guard_latest.json --md-out outputs\evp8_g0_guard_latest.md`
  必须通过，且 `api_call_attempted=false`；
- docs 明确未来 G4 synthesis 不需要读取 ignored raw outputs。

Execute:

- 修改 `scripts/run_evp8_deepseek_qwen_smoke.py`：
  - parsed records 增加 raw-output-free `risk_flags` 和
    `human_review_needed`；
  - executed tracked summary 增加
    `review_count_by_evidence_level`、
    `parse_valid_count_by_evidence_level`、
    `invalid_parse_count_by_evidence_level`、
    `decision_counts_by_evidence_level`；
  - 新增 helper 生成完整 `E0-E6` level counts，避免缺失层被误当作 0 之外的
    状态；
- 修改 `scripts/audit_evp8_smoke_results.py`：
  - 检查每个 `E0-E6` 都有 5 条 review 和 5 条 parse-valid；
  - 检查每个 `E0-E6` 的 invalid parse count 为 0；
  - 检查 `decision_counts_by_evidence_level` 覆盖所有 `E0-E6`，且每层总数为
    5；
  - `--self-test` 新增 `deepseek_per_level_aggregate_drift` 失败用例；
- 同步 EVP-8 execution plan、short-state、INDEX 和 engineering notes，明确
  G4 synthesis 使用 tracked per-level aggregates，不读取 ignored raw outputs。

Verify:

- `python -m py_compile scripts\run_evp8_deepseek_qwen_smoke.py scripts\audit_evp8_smoke_results.py`
  通过；
- `python scripts\audit_evp8_smoke_results.py --self-test` 通过：
  - `case_count = 9`；
  - 新增 `deepseek_per_level_aggregate_drift => failed`；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
  - `raw_outputs_generated = false`；
  - `tracked_outputs_written = false`；
- `python scripts\check_evp8_deepseek_qwen_g0.py --check --json-out outputs\evp8_g0_guard_latest.json --md-out outputs\evp8_g0_guard_latest.md`
  通过：
  - `guard_status = passed`；
  - `expected_outputs_exist = false`；
  - `post_smoke_observed_status = waiting_for_execution`；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
  - `raw_outputs_generated = false`；
- `python scripts\check_evp8_deepseek_qwen_g0.py --check` 通过，并刷新 tracked
  G0 summary artifacts，使 post-smoke audit self-test `case_count = 9`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅有 CRLF 工作区转换 warning；
- 本轮未调用模型 API，未读取 raw outputs，未生成 raw outputs。

Commit And Sync:

- 已提交并同步本轮 per-level smoke aggregate contract：
  `16cca2a Track EVP-8 smoke per-level aggregates`；
- 远端 `origin/main` 已同步到本轮提交；
- 工作区 clean。

## 2026-06-20 EVP-8 G4 smoke synthesis scaffold

Inspect:

- 当前工作区 clean，`main...origin/main`；
- 最新提交为 `16cca2a Track EVP-8 smoke per-level aggregates`；
- 当前继续指令不是明确 EVP-8 Phase 1 smoke/API 授权，本轮不得执行
  `--execute`；
- `scripts/audit_evp8_smoke_results.py` 已能在 tracked summaries 上审计
  DeepSeek/Qwen 顺序、parse/cost/model drift 和 `E0-E6` per-level aggregates；
- 但当前还没有 G4 two-model smoke synthesis 专用入口。未来真实 smoke 后若没有
  synthesis scaffold，容易把 audit 结果和论文 claim 边界手工混在一起，或误读
  ignored raw outputs。

Plan:

1. 新增 no-API G4 synthesis scaffold：
   - 读取 smoke execution packet 和 tracked post-smoke audit result；
   - 不读取 ignored raw responses；
   - 当前无真实 summaries 时输出 `waiting_for_execution`；
   - DeepSeek-only pass 时输出 `partial_waiting_for_qwen`；
   - 双模型均通过时输出 `passed`，并只报告 tracked per-level decision counts；
2. 增加 `--self-test`，覆盖 waiting、DeepSeek-only、both-passed 和
   Qwen-without-DeepSeek failed 分支；
3. 更新 execution plan、short-state、INDEX 和 engineering notes；
4. 运行 no-API py_compile、synthesis self-test/check、G0 guard、local quality gate
   和 diff check；
5. 不调用 API，不读取 raw outputs，不生成 raw outputs。

Acceptance:

- G4 synthesis scaffold 当前必须通过 `waiting_for_execution`；
- `--self-test` 必须证明 partial/passed/failed 分支；
- synthesis output 的 claim boundary 明确禁止 full-run、five-model 和
  evidence-level effectiveness final claim；
- G0 guard 和 local quality gate 保持通过。

Execute:

- 新增 `scripts/summarize_evp8_smoke_synthesis.py`：
  - 复用 post-smoke audit 的 tracked summary 读取路径；
  - 当前无真实 summaries 时输出 `waiting_for_execution`；
  - DeepSeek-only pass 时输出 `partial_waiting_for_qwen`；
  - 双模型均通过时输出 `passed`，并仅汇总 tracked per-level decision counts；
  - `--self-test` 覆盖 waiting、DeepSeek-only、both-passed、
    Qwen-without-DeepSeek failed；
- 扩展 `scripts/check_evp8_deepseek_qwen_g0.py`：
  - G0 guard 加入 `summarize_evp8_smoke_synthesis.py --self-test`；
  - G0 guard 加入 `summarize_evp8_smoke_synthesis.py --check`；
  - G0 summary 记录 synthesis status、audit status 和 no-raw-output boundary；
- 生成 tracked synthesis scaffold artifacts：
  - `data/protocols/evp8_deepseek_qwen_smoke_synthesis_v0_1.json`；
  - `docs/experiments/evp8_deepseek_qwen_smoke_synthesis_v0_1.md`；
- 同步 EVP-8 execution plan、short-state、INDEX 和 engineering notes。

Verify:

- `python -m py_compile scripts\check_evp8_deepseek_qwen_g0.py scripts\summarize_evp8_smoke_synthesis.py scripts\audit_evp8_smoke_results.py`
  通过；
- `python scripts\summarize_evp8_smoke_synthesis.py --self-test` 通过：
  - `case_count = 4`；
  - `waiting_for_execution`、`partial_waiting_for_qwen`、`passed` 分支通过；
  - `qwen_without_deepseek` 分支失败且被 `--check` 拒绝；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
  - `raw_outputs_generated = false`；
- `python scripts\check_evp8_deepseek_qwen_g0.py --check` 通过：
  - `guard_status = passed`；
  - `smoke_synthesis_self_test.case_count = 4`；
  - `smoke_synthesis_check.synthesis_status = waiting_for_execution`；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
  - `expected_outputs_exist = false`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅有 CRLF 工作区转换 warning；
- ignored boundary 确认 `.env`、`artifacts/`、
  `configs/evp8_deepseek_qwen.local.json`、`outputs/` 仍未 staged；
- 本轮仍未调用模型 API，未读取 raw outputs，未生成 raw outputs。

Commit And Sync:

- 已提交并同步本轮 G4 smoke synthesis scaffold：
  `4f1136b Add EVP-8 smoke synthesis scaffold`；
- 远端 `origin/main` 已同步到本轮提交；
- 工作区 clean。

## 2026-06-20 EVP-8 smoke execution packet guard sync

Inspect:

- 当前工作区 clean，`main...origin/main`；
- 最新提交为 `4f1136b Add EVP-8 smoke synthesis scaffold`；
- 当前继续指令不是明确 EVP-8 Phase 1 smoke/API 授权，本轮不得执行
  `--execute`；
- G0 one-command guard 已加入 G4 synthesis self-test/check；
- EVP-8 execution plan 已要求真实 smoke 前运行 synthesis self-test/check；
- 但 `data/protocols/evp8_deepseek_qwen_smoke_execution_packet_v0_1.json` 的
  `guard_commands_before_execute` 仍停留在旧 guard list，尚未列出
  `summarize_evp8_smoke_synthesis.py --self-test` 和 `--check`。

Plan:

1. 更新 `scripts/write_evp8_smoke_execution_packet.py`，把 G4 synthesis
   self-test/check 加入 future execution packet 的 guard commands；
2. 重新生成 tracked execution packet JSON/Markdown；
3. 同步 execution plan、short-state、INDEX 和 engineering notes；
4. 运行 no-API py_compile、execution packet check、G0 guard、local quality gate
   和 diff check；
5. 不调用 API，不读取 raw outputs，不生成 raw outputs。

Acceptance:

- smoke execution packet 的 guard commands 明确包含：
  - `python scripts\summarize_evp8_smoke_synthesis.py --self-test`；
  - `python scripts\summarize_evp8_smoke_synthesis.py --check`；
- `execution_authorized_by_packet` 仍为 false；
- G0 guard 仍通过，且当前 synthesis status 为 `waiting_for_execution`。

Execute:

- 更新 `scripts/write_evp8_smoke_execution_packet.py` 的 `guard_commands`
  生成逻辑；
- 重新生成 tracked smoke execution packet JSON/Markdown；
- 新 guard list 现在包含：
  - `python scripts\check_evp8_deepseek_qwen_g0.py --check`；
  - `python scripts\write_evp8_smoke_execution_packet.py --check`；
  - `python scripts\audit_evp8_smoke_results.py --check`；
  - `python scripts\summarize_evp8_smoke_synthesis.py --self-test`；
  - `python scripts\summarize_evp8_smoke_synthesis.py --check`；
- 同步 EVP-8 execution plan、short-state、INDEX 和 engineering notes。

Verify:

- `python -m py_compile scripts\write_evp8_smoke_execution_packet.py` 通过；
- `python scripts\write_evp8_smoke_execution_packet.py --check` 通过：
  - `packet_status = ready`；
  - `execution_authorized_by_packet = false`；
  - `api_call_attempted = false`；
  - guard commands 包含 G0、execution-packet self-check、post-smoke audit
    check 和 G4 synthesis checks；
- `python scripts\check_evp8_deepseek_qwen_g0.py --check` 通过：
  - `guard_status = passed`；
  - `smoke_synthesis_check.synthesis_status = waiting_for_execution`；
  - `expected_outputs_exist = false`；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅有 CRLF 工作区转换 warning；
- 本轮仍未调用模型 API，未读取 raw outputs，未生成 raw outputs。

## 2026-06-20 EVP-8 staged follow-up plan write

Inspect:

- 当前工作区 clean，`main...origin/main`；
- 最新提交为 `1d235ee Sync EVP-8 smoke packet guards`；
- 用户要求“写入后续计划，一会儿会让按计划执行”，因此本轮只写计划，不执行
  `--execute`，不调用 API，不读取 raw outputs；
- 当前 EVP-8 已具备 Phase 1 DeepSeek/Qwen smoke 前的 no-API readiness：
  G0 guard、execution packet、post-smoke audit scaffold 和 G4 smoke synthesis
  scaffold 均已存在；
- 现有计划已经覆盖 smoke 的 G0-G4 和 smoke 后的 G5 决策，但需要把 smoke 之后
  如何进入 first-batch full run、later-model completion 和 paper/artifact freeze
  写成更明确的 staged gates。

Plan:

1. 在 canonical EVP-8 execution plan 中补充 smoke 之后的 G5-G9 后续 gate：
   - no-API first-batch full-run packet；
   - DeepSeek/Qwen first-batch 686-call full run；
   - later-model completion packet；
   - five-model journal synthesis；
   - paper writing and artifact freeze；
2. 在 `docs/plans/final_paper_roadmap_zh.md` 中同步期刊版路线的后续执行顺序；
3. 在 `docs/plans/current_project_state_zh.md` 中刷新当前 Git 同步锚点，并把后续
   执行顺序写入短入口；
4. 同步 `docs/INDEX.md` 和 `docs/experience/engineering_notes.md`，记录 staged
   execution boundary；
5. 运行 no-API 文档/计划验证、G0 guard、local quality gate 和 diff check；
6. 只提交本轮文档计划更新并尝试同步 GitHub。

Acceptance:

- 后续计划必须明确区分 smoke、first-batch full run、later-model completion、
  five-model synthesis 和 paper/artifact freeze；
- 不得把用户稍后的 smoke 执行授权自动扩展为 686-call full run 或五模型补跑；
- 后续模型必须使用同一 frozen EVP-8 packets、prompt、schema、parser、
  temperature、retry policy 和 evaluator joins；
- 若 DeepSeek/Qwen 后发现协议问题，必须 bump protocol version 并从头重跑受影响
  模型；
- 本轮不调用 API、不读取 raw outputs、不生成 raw outputs。

Execute:

- 更新 `docs/experiments/evp8_journal_scale_execution_plan_20260620.md`：
  - 将 G5 明确为 post-smoke decision and first-batch full-run packet；
  - 新增 G6 DeepSeek/Qwen first-batch full run；
  - 新增 G7 later model completion packet；
  - 新增 G8 five-model journal synthesis；
  - 新增 G9 paper writing and artifact freeze；
- 更新 `docs/plans/final_paper_roadmap_zh.md`，同步期刊版后续执行顺序；
- 更新 `docs/plans/current_project_state_zh.md`，刷新当前同步锚点并写入 staged
  follow-up sequence；
- 更新 `docs/INDEX.md`，把 EVP-8 计划索引从 immediate G0-G6 扩展为
  G0-G4 smoke gates 与 G5-G9 staged path；
- 更新 `docs/experience/engineering_notes.md`，记录 staged execution boundary；
- 运行 G0 guard，刷新 tracked G0 summary 的 `run_utc`，未改变 no-API 边界。

Verify:

- `git diff --check` 通过，仅有 CRLF 工作区转换 warning；
- `python scripts\check_evp8_deepseek_qwen_g0.py --check` 通过：
  - `guard_status = passed`；
  - `expected_outputs_exist = false`；
  - `post_smoke_observed_status = waiting_for_execution`；
  - `smoke_synthesis_check.synthesis_status = waiting_for_execution`；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
  - `raw_outputs_generated = false`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- 本轮未调用模型 API，未读取 raw outputs，未生成 raw outputs。

Commit And Sync:

- 已提交本轮 staged follow-up plan，初始本地 hash 为
  `27e2d21 Plan EVP-8 staged follow-up gates`；若后续将同步状态修正 amend 进
  该未推送提交，最终 hash 以 `git log -1 --oneline` 为准；
- `git push origin main` 连续两次失败在 GitHub network-level connection：
  - `Recv failure: Connection was reset`；
  - `Could not connect to server`；
- 按用户既定规则，该 GitHub 网络同步失败不阻塞后续本地计划执行；
- 下一轮若仍无明确 smoke/API 授权，只能继续 no-API 审计、文档漂移修复或同步重试。

## 2026-06-20 EVP-8 Git sync drift repair after staged follow-up commit

Inspect:

- 当前工作区 clean，`main...origin/main [ahead 1]`；
- 最新本地提交为 `27e2d21 Plan EVP-8 staged follow-up gates`；
- 远端仍停在 `1d235ee Sync EVP-8 smoke packet guards`；
- 用户当前续跑指令不是明确 EVP-8 Phase 1 smoke/API 授权，本轮仍不得执行
  `--execute`；
- `docs/plans/current_project_state_zh.md` 的同步状态段仍可能被读成最近检查已
  完全同步，需要修正为“以命令为准，当前有未推送 plan-only 提交”。

Plan:

1. 修正 `docs/plans/current_project_state_zh.md` 的当前同步状态；
2. 将本次漂移修复记录写入 `docs/plans/current_plan_zh.md`；
3. 运行 no-API G0 guard、local quality gate 和 diff check；
4. 因上一提交尚未推送，将本轮文档修正 amend 进 `27e2d21`，避免制造新的
   push-failure-only 提交；
5. 再次尝试 GitHub push；若仍为 network-level failure，则按用户规则继续本地计划。

Acceptance:

- 短入口明确当前远端锚点、本地未推送 plan-only 锚点和 push network failure；
- 本轮不调用 API，不读取 raw outputs，不生成 raw outputs；
- amend 后仍只有一个本地 plan-only ahead 提交。

Execute:

- 修正 `docs/plans/current_project_state_zh.md`：
  - 当前状态明确为本地 clean 且存在未推送 plan-only 提交；
  - 远端已同步锚点仍为 `1d235ee Sync EVP-8 smoke packet guards`；
  - 本地未推送语义锚点改为以 `git log -1 --oneline` 为准，避免 amend 后
    hash 漂移；
  - GitHub sync failure 明确为 network-level，不代表实验或工作区未完成；
- 修正 `docs/plans/current_plan_zh.md`：
  - 记录 `27e2d21` 是 staged follow-up plan 的初始本地 hash；
  - 记录本轮将同步状态修正 amend 进该未推送提交，最终 hash 以 `git log -1`
    为准；
- 重新运行 no-API G0 guard，刷新 tracked G0 summary 的 ignored-boundary status
  和 `run_utc`。

Verify:

- `git diff --check` 通过，仅有 CRLF 工作区转换 warning；
- `python scripts\check_evp8_deepseek_qwen_g0.py --check` 通过：
  - `guard_status = passed`；
  - `expected_outputs_exist = false`；
  - `post_smoke_observed_status = waiting_for_execution`；
  - `smoke_synthesis_check.synthesis_status = waiting_for_execution`；
  - `api_call_attempted = false`；
  - `raw_outputs_read = false`；
  - `raw_outputs_generated = false`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- 本轮仍未调用模型 API，未读取 raw outputs，未生成 raw outputs。

## 2026-06-20 EVP-8 G5 packet verification and next-step decision

Inspect:

- 当前工作区存在本轮 G5 no-API first-batch full-run packet 相关未提交改动；
- G5 packet、post-full-run audit scaffold 和 post-full-run synthesis scaffold 已生成；
- 用户当前问题是“下一步应该做什么、计划是否有影响”，不是明确授权 686-call
  full run。

Plan:

1. 先完成本轮 no-API gate 验证、diff 检查、敏感信息检查、提交和 GitHub 同步；
2. 若同步后继续执行实验，下一步只能是用户明确授权后的 DeepSeek first-batch
   full run；
3. Qwen first-batch full run 必须等待 DeepSeek full-run audit 通过；
4. 本轮不调用模型 API，不读取 raw outputs，不生成 raw outputs。

Verify:

- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅有 CRLF 工作区转换 warning；
- `python scripts\write_evp8_first_batch_full_run_packet.py --check` 通过：
  - `packet_status = ready`；
  - `candidate_count = 98`；
  - `planned_calls_per_model = 686`；
  - `execution_authorized_by_packet = false`；
- `python scripts\audit_evp8_first_batch_full_results.py --check` 通过：
  - `audit_status = waiting_for_execution`；
  - `raw_outputs_read = false`；
- `python scripts\summarize_evp8_first_batch_full_synthesis.py --check` 通过：
  - `synthesis_status = waiting_for_execution`；
  - `raw_outputs_read = false`。

Decision:

- 计划没有被推翻；G5 的作用是把 smoke 后的 full-run 入口从“口头下一步”
  收束为可审计的 no-API handoff packet；
- 当前执行边界从 G4 smoke closure 前进到 G5 packet ready；
- 真正影响成本和结论的下一步是 G6 DeepSeek/Qwen first-batch full run，仍需要用户
  单独明确授权。

## 2026-06-20 EVP-8 post-push state correction

Inspect:

- `git status --short --branch` 显示 `main...origin/main`，工作区 clean；
- `git log -1 --oneline` 显示 `930bc73 Prepare EVP-8 first batch full packet`；
- `docs/plans/current_project_state_zh.md` 仍保留“有未推送 plan-only 提交”的旧描述，
  与当前 Git 状态矛盾。

Plan:

1. 修正短入口的 Git 同步锚点为 `930bc73`；
2. 明确当前没有 GitHub 同步阻塞；
3. 记录本轮是 no-API 文档漂移修复，不改变 EVP-8 G6 执行门；
4. 运行 no-API 验证、提交并同步。

Decision:

- 计划没有影响：canonical 下一步仍是 G6 DeepSeek first-batch full run；
- 由于 G6 是 686-call API 实验，仍需要用户明确授权后才能执行；
- 本轮不调用 API、不读取 raw outputs、不生成 raw outputs。

Verify:

- `python scripts\write_evp8_first_batch_full_run_packet.py --check` 通过：
  - `packet_status = ready`；
  - `planned_calls_per_model = 686`；
  - `execution_authorized_by_packet = false`；
- `python scripts\audit_evp8_first_batch_full_results.py --check` 通过：
  - `audit_status = waiting_for_execution`；
  - `raw_outputs_read = false`；
- `python scripts\summarize_evp8_first_batch_full_synthesis.py --check` 通过：
  - `synthesis_status = waiting_for_execution`；
  - `raw_outputs_read = false`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅有 CRLF 工作区转换 warning。

## 2026-06-20 EVP-8 G6 DeepSeek first-batch full-run authorization

Inspect:

- 用户回复“授权”，结合前序明确等待的授权句“授权执行 DeepSeek G6 first-batch
  full run”，本轮解释为授权执行 DeepSeek G6 first-batch full run；
- `git status --short --branch` 显示 `main...origin/main`，工作区 clean；
- `git log -1 --oneline` 显示 `93f1467 Record EVP-8 G6 sync recovery`；
- G5 first-batch full-run packet 当前 `ready`；
- DeepSeek full-run expected outputs 当前不存在：
  - `outputs/evp8_phase1_deepseek_qwen_full/deepseek_deepseek-v4-pro/raw_responses.jsonl`；
  - `data/reviews/evp8_deepseek_deepseek-v4-pro_full_summary.json`。

Plan:

1. 重新运行 no-API preflight and full-run guards；
2. 若所有 guard 通过，执行 DeepSeek G6 first-batch full run：
   `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --run-scope full --config configs\evp8_deepseek_qwen.local.json --model-id deepseek/deepseek-v4-pro`；
3. 执行后立即运行 `python scripts\audit_evp8_first_batch_full_results.py --check`；
4. 只有 DeepSeek full audit 通过后，后续才允许考虑 Qwen first-batch full run；
5. 本轮不得改变 protocol、prompt、schema、candidate set、evaluator joins、temperature、
   output parser 或 evidence levels。

Acceptance:

- DeepSeek full summary 必须 raw-output-free；
- ignored raw responses 只能写入 `outputs/`；
- tracked summary 必须包含 parse/schema/usage-cost gates；
- 若 DeepSeek full audit 失败，停止并诊断，不运行 Qwen。

## 2026-06-20 EVP-8 G6 DeepSeek full-run observability repair

Inspect:

- DeepSeek G6 full run 已按授权启动，但外层工具在 2 小时后超时；
- 超时后原 Python 子进程仍在运行，命令行为 DeepSeek full run；
- 监控 10 分钟后仍未生成：
  - `outputs/evp8_phase1_deepseek_qwen_full/deepseek_deepseek-v4-pro/raw_responses.jsonl`；
  - `data/reviews/evp8_deepseek_deepseek-v4-pro_full_summary.json`；
- `scripts/run_evp8_deepseek_qwen_smoke.py` 的 `execute()` 当前把所有 raw records
  保存在内存，循环结束后才写 raw JSONL，因此 long run 中断时没有 partial
  artifact 可审计；
- 已停止该 unobservable Python 子进程，避免继续产生不可审计成本。

Diagnosis:

- 问题类型：执行链路 bug / 成本可观测性 bug；
- 不是 protocol、prompt、schema、candidate set 或 evaluator join 问题；
- 不运行 Qwen，不扩大实验，不改变 EVP-8 v0.1 inputs。

Plan:

1. 修复 `scripts/run_evp8_deepseek_qwen_smoke.py`：
   - 每完成一条 API response 后立即 append 到 ignored raw JSONL；
   - 新增显式 `--resume`，仅在 raw JSONL 已存在且 tracked summary 不存在时
     从 existing raw prefix 续跑；
   - 默认不放宽 overwrite policy：无 `--resume` 时仍拒绝覆盖任何既有 raw/summary；
2. 重新运行 no-API check-only / packet / audit gates；
3. 再次执行 DeepSeek G6 full run；
4. 若仍失败，先依据 partial raw 和 audit 定位，不运行 Qwen。

Acceptance:

- `--check-only --run-scope full` 仍通过；
- smoke check-only 仍通过；
- `--resume` 不会把 raw response body 写入 tracked summary；
- interrupted full run 后至少有 ignored raw prefix 可审计；
- no-API gates 通过前不重启真实 API。

Execute:

- 已停止残留 DeepSeek full-run Python 子进程；
- 已修改 `scripts/run_evp8_deepseek_qwen_smoke.py`：
  - `execute()` 每条 API response 完成后立即 append 一行 raw JSONL；
  - 新增显式 `--resume` 参数；
  - `--resume` 只接受 existing raw records 是 planned packet order 的前缀；
  - resume 记录必须匹配 candidate id、evidence level、configured model 和 provider
    route；
  - tracked summary 新增 `resume_enabled`、`resumed_raw_record_count` 和
    `new_api_call_count`，不包含 raw response body；
- 已更新 `docs/experience/engineering_notes.md`，记录 long API run checkpointing
  经验。

Verify:

- `python -m py_compile scripts\run_evp8_deepseek_qwen_smoke.py` 通过；
- `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --run-scope full --config configs\evp8_deepseek_qwen.local.json`
  通过；
- `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`
  通过；
- 临时目录 resume-prefix self-test 通过；
- 当前 DeepSeek full raw 和 summary 仍不存在，允许修复后重新执行 DeepSeek G6。

Commit And Sync:

- 初始提交为 `8983abd Record EVP-8 G6 authorization boundary`；
- `git push origin main` 连续两次失败在 GitHub network-level connection：
  - `Recv failure: Connection was reset`；
  - `Could not connect to server`；
- 按用户既定规则，该 GitHub 网络同步失败不阻塞后续本地计划执行；
- 将本同步状态修正 amend 进 `8983abd`，最终 hash 以 `git log -1 --oneline`
  为准。

## 2026-06-20 EVP-8 G6 boundary push recovery

Inspect:

- `git status --short --branch` 显示 `main...origin/main [ahead 1]`；
- `git log -1 --oneline` 显示 `95efbdc Record EVP-8 G6 authorization boundary`；
- G5 packet 仍明确：
  - `packet_status = ready`；
  - `planned_calls_per_model = 686`；
  - `execution_authorized_by_packet = false`；
  - `requires_explicit_user_command = true`。

Plan:

1. 重试 GitHub push，优先清掉上一轮 network-level sync residue；
2. 若 push 成功，修正短入口为 `main...origin/main` 已同步；
3. 不运行 G6 `--execute --run-scope full`，因为当前仍不是明确 API 授权。

Execute:

- `git push origin main` 成功，将 `95efbdc` 推送到远端；
- 修正 `docs/plans/current_project_state_zh.md`：
  - 当前 Git 状态改为 `main...origin/main` 已同步；
  - 当前远端同步锚点新增 `95efbdc Record EVP-8 G6 authorization boundary`；
  - GitHub sync 边界改为当前没有同步阻塞。

Decision:

- GitHub 同步残留已恢复；
- 计划没有变化：G6 仍是下一步，但仍需用户明确授权 DeepSeek 686-call
  first-batch full run；
- 本轮不调用 API、不读取 raw outputs、不生成 raw outputs。

Verify:

- `python scripts\write_evp8_first_batch_full_run_packet.py --check` 通过：
  - `packet_status = ready`；
  - `planned_calls_per_model = 686`；
  - `execution_authorized_by_packet = false`；
  - `requires_explicit_user_command = true`；
- `python scripts\audit_evp8_first_batch_full_results.py --check` 通过：
  - `audit_status = waiting_for_execution`；
  - `raw_outputs_read = false`；
- `python scripts\summarize_evp8_first_batch_full_synthesis.py --check` 通过：
  - `synthesis_status = waiting_for_execution`；
  - `raw_outputs_read = false`；
- `git diff --check` 通过，仅有 CRLF 工作区转换 warning。

## 2026-06-20 EVP-8 G6 authorization boundary re-check

Inspect:

- `git status --short --branch` 显示 `main...origin/main`，工作区 clean；
- `git log -1 --oneline` 显示 `422f956 Fix EVP-8 post-push state entry`；
- `data/protocols/evp8_deepseek_qwen_first_batch_full_run_packet_v0_1.json`
  明确：
  - `packet_status = ready`；
  - `planned_calls_per_model = 686`；
  - `execution_authorized_by_packet = false`；
  - `requires_explicit_user_command = true`；
- `docs/plans/current_project_state_zh.md` 已写明下一步不是自动 API，而是等待用户审阅
  G5 packet 后再次明确授权 DeepSeek/Qwen 686-call first-batch full run。

Plan:

1. 修正短入口的最新远端同步锚点到 `422f956`；
2. 不运行 `--execute --run-scope full`，因为当前续跑信号仍不是明确的 G6 API
   授权；
3. 运行 no-API gate，提交并同步本轮文档状态修正。

Decision:

- 计划没有变化：G5 已完成，G6 的第一步仍是 DeepSeek first-batch full run；
- 当前不能自动执行 G6，因为该步骤是 686-call API 实验，必须由用户明确授权；
- 若用户明确说“执行 DeepSeek G6 full run”或等价命令，下一轮可以先运行
  DeepSeek full command，然后立即运行 full-result audit。

Verify:

- `python scripts\write_evp8_first_batch_full_run_packet.py --check` 通过：
  - `packet_status = ready`；
  - `execution_authorized_by_packet = false`；
  - `requires_explicit_user_command = true`；
- `python scripts\audit_evp8_first_batch_full_results.py --check` 通过：
  - `audit_status = waiting_for_execution`；
  - `raw_outputs_read = false`；
- `python scripts\summarize_evp8_first_batch_full_synthesis.py --check` 通过：
  - `synthesis_status = waiting_for_execution`；
  - `raw_outputs_read = false`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅有 CRLF 工作区转换 warning。

## 2026-06-20 EVP-8 G6 DeepSeek full-run result closure

Inspect:

- `git status --short --branch` 显示本地 `main` 相对 `origin/main` ahead 1，
  未推送提交为 `72f1fb5 Checkpoint EVP-8 full-run raw responses`；
- `origin/main` 当前锚点为 `d79cb1e Authorize EVP-8 DeepSeek G6 full run`；
- DeepSeek full raw responses 已生成 686 行：
  `outputs/evp8_phase1_deepseek_qwen_full/deepseek_deepseek-v4-pro/raw_responses.jsonl`；
- DeepSeek tracked summary 已生成：
  `data/reviews/evp8_deepseek_deepseek-v4-pro_full_summary.json`；
- 该 summary 被 `.gitignore` 的 `data/*` 规则忽略，但内容不含 prompt text 或
  raw response text，属于本轮应强制跟踪的 raw-output-free summary；
- post-full-run audit/synthesis 已从 `waiting_for_execution` 推进到：
  - audit: `partial_waiting_for_remaining_model`；
  - synthesis: `partial_waiting_for_qwen`。

Plan:

1. 将 DeepSeek G6 full-run passed 状态写入 short-state、EVP-8 execution plan
   和 INDEX；
2. 将新的 DeepSeek raw-output-free summary 强制加入 Git，继续禁止提交
   ignored raw JSONL、runner logs、`.env`、`configs/*.local.json` 和 `outputs/`；
3. 重新运行 first-batch full audit、synthesis、local quality gate 和 diff check；
4. 提交并尝试 push。若 GitHub network-level push 再次失败，按用户授权继续保留
   本地提交并在最终状态中明确。

Execute:

- DeepSeek G6 full run 已完成：
  - `review_count = 686`；
  - `parse_valid_count = 686`；
  - `invalid_parse_count = 0`；
  - `new_api_call_count = 686`；
  - `resume_enabled = false`；
  - `run_gate = passed`；
  - `first_batch_full_gate = passed`；
  - `usage_cost_gate = passed`；
  - `unknown_cost_record_count = 0`；
  - `cost_summary.total_cost_usd = 0.788808816`；
- DeepSeek per-level decision counts:
  - `E0`: `{"escalate": 66, "reject": 32}`；
  - `E1`: `{"escalate": 58, "reject": 40}`；
  - `E2`: `{"escalate": 65, "reject": 33}`；
  - `E3`: `{"escalate": 81, "reject": 17}`；
  - `E4`: `{"escalate": 74, "reject": 24}`；
  - `E5`: `{"escalate": 71, "reject": 27}`；
  - `E6`: `{"escalate": 86, "reject": 12}`；
- Qwen full run 尚未执行；当前 synthesis 只能写成 DeepSeek-only partial，
  不能写成 two-model first-batch result。

Decision:

- DeepSeek G6 first-batch full run 的执行链路、parse/schema、usage/cost、
  model/provider-route、per-level aggregate 和 raw-output boundary 均已通过；
- 按 canonical G6 顺序，下一技术步骤是 Qwen first-batch full run；但本轮用户
  授权已在计划中记录为 DeepSeek G6 full run 授权，因此 Qwen 仍应作为下一步
  明确授权/决策点处理；
- 不改变 EVP-8 v0.1 protocol、prompt、candidate set、schema、temperature、
  retry policy 或 evaluator joins。

Verify:

- `python scripts\audit_evp8_first_batch_full_results.py --check` 通过：
  - `audit_status = partial_waiting_for_remaining_model`；
  - DeepSeek model audit `status = passed`；
  - Qwen `status = waiting_for_execution`；
  - `raw_outputs_read = false`；
- `python scripts\summarize_evp8_first_batch_full_synthesis.py --check` 通过：
  - `synthesis_status = partial_waiting_for_qwen`；
  - `raw_outputs_read = false`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅有 CRLF 工作区转换 warning。

Commit And Sync:

- 已提交 DeepSeek full-run checkpointing 修复：
  `72f1fb5 Checkpoint EVP-8 full-run raw responses`；
- 已提交 DeepSeek G6 full-run 结果收口：
  `d9a8391 Record EVP-8 DeepSeek G6 full result`；
- `git push origin main` 成功，远端 `main` 已同步到 `d9a8391`；
- raw JSONL、runner logs、`.env`、`configs/*.local.json`、`outputs/` 和
  `artifacts/` 均未提交。

## 2026-06-20 EVP-8 G6 sync-state wording correction

Inspect:

- DeepSeek G6 result closure commit 已成功 push；
- 随后的 sync-state 文档修正第一次 push 出现 GitHub network-level
  `Recv failure: Connection was reset`，第二次重试成功；
- 写死“当前远端锚点 = 某个刚提交 hash”会在下一次文档修正后再次漂移。

Plan:

1. 将 short-state 的 Git 状态描述改成以 `git status --short --branch` 和
   `git log -1 --oneline` 为准；
2. 保留语义锚点：远端至少应包含 `72f1fb5` checkpointing 修复和 `d9a8391`
   DeepSeek G6 full-result closure；
3. 不改变实验结果、protocol、summary 或 raw-output boundary。

Decision:

- 这是同步状态措辞修正，不是新实验；
- Qwen full run 仍未执行，下一步仍是是否授权 Qwen 686-call first-batch
  full run。

## 2026-06-21 EVP-8 G6 Qwen first-batch full-run authorization

Inspect:

- 用户回复“授权 继续”，结合上一轮最终边界“Qwen 需要单独明确授权后再执行”，
  本轮解释为授权执行 Qwen G6 first-batch full run；
- `git status --short --branch` 显示 `main...origin/main`，工作区 clean；
- `git log -5 --oneline` 显示远端已包含：
  - `9e4a756 Clarify EVP-8 G6 sync state wording`；
  - `d9a8391 Record EVP-8 DeepSeek G6 full result`；
  - `72f1fb5 Checkpoint EVP-8 full-run raw responses`；
- Qwen full-run expected outputs 当前不存在：
  - `outputs/evp8_phase1_deepseek_qwen_full/qwen_qwen3.7-max/raw_responses.jsonl`；
  - `data/reviews/evp8_qwen_qwen3.7-max_full_summary.json`；
- 当前 Python 进程中没有 `run_evp8_deepseek_qwen_smoke.py` 残留 runner。

Plan:

1. 重新运行 no-API / no-raw gates：
   - strict local preflight；
   - full-scope check-only；
   - first-batch full-result audit；
   - first-batch synthesis；
2. 若 gates 仍保持 DeepSeek passed / Qwen waiting，则执行 Qwen G6 full run：
   `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --run-scope full --config configs\evp8_deepseek_qwen.local.json --model-id qwen/qwen3.7-max`；
3. 使用 checkpointing 后的 runner，监控 ignored raw JSONL 行数，避免 long run
   再次不可观测；
4. 执行完成后立即运行 first-batch full audit 和 synthesis；
5. 只在 audit 通过后同步更新 short-state、EVP-8 execution plan、INDEX 和
   engineering notes；提交并同步 GitHub。

Acceptance:

- Qwen summary 必须 raw-output-free，不包含 prompt text 或 raw response text；
- Qwen 必须使用同一 EVP-8 v0.1 frozen candidate set、prompt、schema、parser、
  temperature、retry policy 和 evaluator joins；
- audit 必须从 `partial_waiting_for_remaining_model` 推进到 `passed`；
- synthesis 必须从 `partial_waiting_for_qwen` 推进到 first-batch two-model
  passed status；
- 若 Qwen parse/schema/cost/model/provider/raw-output boundary 失败，停止并诊断，
  不启动 later-model execution。

Diagnose:

- 首轮 pre-Qwen gate 中误运行了
  `python scripts\write_evp8_first_batch_full_run_packet.py --check`；
- 该脚本是 G5 pre-full-run packet gate，要求 DeepSeek/Qwen full outputs 均不存在；
- DeepSeek full run 已完成后再次运行它，会因为 DeepSeek raw/summary 已存在而把
  packet 快照改写为 `blocked`，并连带使 result audit 报 `failed`；
- 问题类型：执行链路/计划 gate 顺序问题，不是 Qwen API、protocol、prompt、
  schema、candidate set 或 DeepSeek summary 问题。

Repair:

- 恢复 G5 packet 和 first-batch result audit 快照到 DeepSeek passed /
  Qwen waiting 的 committed partial 状态；
- Qwen 前置 gate 改为：
  - strict local preflight；
  - full-scope check-only；
  - first-batch full-result audit；
  - first-batch synthesis；
- 不再在 DeepSeek full outputs 已存在后运行 G5 packet `--check`；
- 同步更新 engineering notes 和 EVP-8 execution plan，避免后续会话重复误用。

Verify:

- `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
  通过：
  - `preflight_status = passed`；
  - `credential_presence_ready = true`；
  - `api_key_values_printed = false`；
- `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --run-scope full --config configs\evp8_deepseek_qwen.local.json`
  通过：
  - `check_only_status = passed`；
  - `packet_count = 686`；
  - `prompt_hashes_unique_count = 686`；
  - `api_call_attempted = false`；
- `python scripts\audit_evp8_first_batch_full_results.py --check` 通过：
  - `audit_status = partial_waiting_for_remaining_model`；
  - DeepSeek `status = passed`；
  - Qwen `status = waiting_for_execution`；
- `python scripts\summarize_evp8_first_batch_full_synthesis.py --check` 通过：
  - `synthesis_status = partial_waiting_for_qwen`；
  - `raw_outputs_read = false`。

## 2026-06-21 EVP-8 G6 Qwen full-run result closure

Inspect:

- Qwen runner PID `44764` 正常退出；
- Qwen full raw responses 已生成 686 行：
  `outputs/evp8_phase1_deepseek_qwen_full/qwen_qwen3.7-max/raw_responses.jsonl`；
- Qwen tracked summary 已生成：
  `data/reviews/evp8_qwen_qwen3.7-max_full_summary.json`；
- runner stderr 为空；
- raw JSONL 和 runner logs 仍位于 ignored `outputs/`，不提交。

Execute:

- Qwen G6 full run 已完成：
  - `review_count = 686`；
  - `parse_valid_count = 686`；
  - `invalid_parse_count = 0`；
  - `new_api_call_count = 686`；
  - `resume_enabled = false`；
  - `run_gate = passed`；
  - `first_batch_full_gate = passed`；
  - `usage_cost_gate = passed`；
  - `unknown_cost_record_count = 0`；
  - `cost_summary.total_cost_cny = 41.119548`；
- Qwen per-level decision counts:
  - `E0`: `{"escalate": 75, "reject": 23}`；
  - `E1`: `{"escalate": 70, "reject": 28}`；
  - `E2`: `{"escalate": 71, "reject": 27}`；
  - `E3`: `{"escalate": 79, "reject": 19}`；
  - `E4`: `{"escalate": 80, "reject": 18}`；
  - `E5`: `{"escalate": 78, "reject": 20}`；
  - `E6`: `{"escalate": 91, "reject": 7}`。

Verify:

- `python scripts\audit_evp8_first_batch_full_results.py --check` 通过：
  - `audit_status = passed`；
  - DeepSeek `status = passed`；
  - Qwen `status = passed`；
  - `raw_outputs_read = false`；
- `python scripts\summarize_evp8_first_batch_full_synthesis.py --check` 通过：
  - `synthesis_status = passed`；
  - `per_level_decision_counts_by_model` 同时包含 DeepSeek 和 Qwen；
  - `raw_outputs_read = false`；
- Qwen summary 明确：
  - `prompt_text_stored = false`；
  - `raw_response_text_stored_in_tracked_summary = false`。
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅有 CRLF 工作区转换 warning；
- Qwen ignored raw JSONL 行数确认为 686。

Decision:

- EVP-8 first-batch DeepSeek/Qwen two-model full run 已完成并通过 audit/synthesis；
- 当前允许的 claim 仍是 frozen EVP-8 v0.1 98-candidate packet set 上的
  DeepSeek/Qwen descriptive per-level decision patterns；
- 仍禁止写成 five-model journal conclusion、LLM superiority over deterministic
  baselines 或最终 evidence-level effectiveness；
- 下一步按 G7：准备 later-model completion packet，再补 Kimi/Devstral/Gemini。

Commit And Sync:

- 已提交 Qwen G6 first-batch full-run result closure：
  `d59021e Record EVP-8 Qwen G6 full result`；
- 该提交包含 Qwen raw-output-free summary、first-batch passed audit/synthesis、
  INDEX、short-state、execution plan 和 current plan 更新；
- raw JSONL、runner logs、`.env`、`configs/*.local.json`、`outputs/` 和
  `artifacts/` 均未提交；
- 本段 sync-state 文档修正将单独提交，最终远端状态以 `git status --short --branch`
  和 `git log -1 --oneline` 为准。

## 2026-06-21 EVP-8 G7 later-model completion packet

Inspect:

- `git status --short --branch` 显示 `main...origin/main`，工作区 clean；
- `git log -8 --oneline` 显示远端已包含：
  - `6f3c8f0 Sync EVP-8 Qwen G6 result state`；
  - `d59021e Record EVP-8 Qwen G6 full result`；
  - `9c8f4d2 Authorize EVP-8 Qwen G6 full run`；
- `python scripts\audit_evp8_first_batch_full_results.py --check` 已通过，
  `audit_status = passed`；
- `python scripts\summarize_evp8_first_batch_full_synthesis.py --check` 已通过，
  `synthesis_status = passed`；
- `docs/experiments/evp8_journal_scale_execution_plan_20260620.md` 的 G7 要求：
  后续 Kimi K2.6、Devstral 2、Gemini 2.5 Flash 必须先生成 no-API execution
  packet，且复用同一 frozen EVP-8 packets、prompt、schema、temperature、
  retry policy 和 evaluator joins。

Plan:

1. 新增 `scripts/write_evp8_later_model_completion_packet.py`；
2. 从 tracked protocol、full check-only、first-batch audit/synthesis 生成
   G7 no-API packet：
   - exact later-model IDs；
   - provider route policy；
   - expected ignored raw outputs；
   - expected tracked raw-output-free summaries；
   - cost/usage observability fields；
   - guard commands、execute commands、post-run audit/synthesis placeholders；
   - stop gates 和 claim boundary；
3. 生成 tracked JSON/Markdown packet；
4. 运行 `--check`、现有 first-batch audit/synthesis、local quality gate 和
   `git diff --check`；
5. 更新 short-state、execution plan、INDEX 和 engineering notes；
6. 提交并同步 GitHub。

Boundary:

- 本轮不调用 Kimi/Devstral/Gemini API；
- 不读取或提交 raw model responses；
- 不把 DeepSeek/Qwen first-batch synthesis 写成 five-model journal conclusion；
- 不修改 EVP-8 protocol、prompt、candidate set、schema、temperature、retry
  policy 或 evaluator joins。

Execute:

- 已刷新 OpenRouter public catalog audit，不使用 API key、不调用模型：
  - `moonshotai/kimi-k2.6`；
  - `mistralai/devstral-2512`；
  - `google/gemini-2.5-flash`；
  - tracked 输出：
    `data/protocols/evp8_later_model_openrouter_catalog_audit_v0_1.json`；
    `docs/experiments/evp8_later_model_openrouter_catalog_audit_v0_1.md`；
  - `all_available = true`；
- 新增 `scripts/write_evp8_later_model_completion_packet.py`；
- 生成 G7 no-API packet：
  - `data/protocols/evp8_later_model_completion_packet_v0_1.json`；
  - `docs/experiments/evp8_later_model_completion_packet_v0_1.md`；
  - `packet_status = ready`；
  - `planned_calls_per_later_model = 686`；
  - `planned_total_later_model_calls = 2058`；
  - `planning_cost_ceiling_usd = 30.0`；
  - `execution_authorized_by_packet = false`；
  - `runner_implementation_required_before_execution = true`；
  - `later_model_preflight_required_before_execution = true`。

Verify:

- `python -m py_compile scripts\write_evp8_later_model_completion_packet.py`
  通过；
- `python scripts\write_evp8_later_model_completion_packet.py --check` 通过；
- `python scripts\audit_evp8_first_batch_full_results.py --check` 通过；
- `python scripts\summarize_evp8_first_batch_full_synthesis.py --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅有 Git LF/CRLF 工作区转换 warning；
- G7 packet 明确：
  - 没有 Kimi/Devstral/Gemini API call；
  - 没有生成或读取 later-model raw outputs；
  - expected later-model raw/summary outputs 均不存在；
  - 后续命令模板仍依赖尚未实现的 later-model runner/preflight。

Decision:

- G7 no-API later-model completion packet 已准备完成；
- 下一步不是直接运行三模型 API，而是实现并验证
  `scripts\run_evp8_later_model_full.py` 和 later-model local preflight；
- 即使后续用户继续授权，执行前仍必须先通过 runner/preflight/no-raw-output
  gates，并逐模型显式执行；
- 当前允许 claim 仍停留在 DeepSeek/Qwen first-batch descriptive patterns，
  不支持 five-model journal conclusion。

## 2026-06-21 EVP-8 G7.1 later-model runner/preflight

Inspect:

- `git status --short --branch` 显示 `main...origin/main`，工作区 clean；
- `git log -5 --oneline` 当前顶部为
  `79ff382 Prepare EVP-8 later-model packet`；
- G7 packet 当前 `ready`，但明确：
  - `runner_implementation_required_before_execution = true`；
  - `later_model_preflight_required_before_execution = true`；
  - `execution_authorized_by_packet = false`；
- `docs/plans/current_project_state_zh.md` 指向下一步：
  先实现并验证 later-model runner/preflight，不直接运行三模型 API；
- 已读取 DeepSeek/Qwen runner/preflight/config creator 的实现，后续应复用：
  - ignored local config；
  - strict preflight；
  - `--check-only` 默认无 API；
  - `--execute` 才能调用 API；
  - raw responses 只进 ignored `outputs/`；
  - tracked summary 不含 prompt text/raw response text/API key；
  - checkpoint/resume prefix guard；
- 已核对 OpenRouter 官方文档边界：
  - chat completions 是 OpenAI-compatible；
  - request body 支持 `provider` preferences；
  - `X-OpenRouter-Metadata: enabled` 可让 response 带
    `openrouter_metadata`；
  - non-streaming response 有 `usage`，`usage.cost` 为可选字段；
  - provider route/fallback 和 cost 字段必须在 runner summary 中显式审计。

Plan:

1. 新增 tracked no-secret `configs/evp8_later_models.example.json`；
2. 新增 later-model local config creator，只写 ignored
   `configs/evp8_later_models.local.json`，默认 dry-run；
3. 新增 `scripts/preflight_evp8_later_models.py`：
   - structural preflight 可在缺失 `OPENROUTER_API_KEY` 时通过；
   - strict API ready 必须要求 ignored `.env` 中 key present；
   - tracked summary 不记录 key value；
4. 新增 `scripts/run_evp8_later_model_full.py`：
   - `--check-only` 只验证 98 candidates x 7 levels = 686 packet matrix；
   - `--execute` 必须使用 ignored local config、strict preflight、单个
     model id 和 explicit flag；
   - OpenRouter request pin exact model id，不使用 `models` fallback array；
   - provider preferences 禁止 unrecorded fallback；
   - raw JSONL 只写 ignored `outputs/evp8_phase2_later_models_full/`；
   - tracked summary 记录 parse/cost/model/provider metadata aggregates；
5. 扩展 `src/cross_review/openrouter.py`，让现有兼容客户端支持 optional
   provider preferences 和 OpenRouter metadata header，同时不破坏
   DeepSeek/Qwen runner；
6. 生成 no-API local-config plan、preflight summary、later-model full
   check-only summary；
7. 刷新 G7 packet，使它记录 runner/preflight/check-only 已实现但仍不授权 API；
8. 更新 short-state、canonical plan、INDEX、engineering notes；
9. 运行 py_compile、preflight/check-only/packet checks、first-batch
   audit/synthesis、local quality gate 和 `git diff --check`；
10. 只提交本轮相关 tracked files 并 push。

Boundary:

- 本轮仍不调用 Kimi/Devstral/Gemini API；
- 不读取或提交 later-model raw outputs；
- 不生成 local config with secrets，除非只写 ignored placeholder config；
- 不修改 EVP-8 protocol、prompt、candidate set、schema 或已完成的
  DeepSeek/Qwen summaries；
- 不把 runner readiness 写成五模型实验结果。

Execute:

- 扩展 `src/cross_review/openrouter.py`：
  - `chat_completion` / `chat_completion_messages` 支持 optional
    `provider` preferences；
  - 支持 `metadata_enabled=True` 时发送
    `X-OpenRouter-Metadata: enabled`；
  - 保持现有 DeepSeek/Qwen 调用路径兼容；
- 新增 tracked no-secret config：
  `configs/evp8_later_models.example.json`；
- 新增 later-model local config creator：
  `scripts/create_evp8_later_model_local_config.py`；
- 新增 later-model preflight：
  `scripts/preflight_evp8_later_models.py`；
- 新增 guarded later-model full runner：
  `scripts/run_evp8_later_model_full.py`；
- 生成 ignored local config：
  `configs/evp8_later_models.local.json`；
- 生成 tracked no-API artifacts：
  - `data/protocols/evp8_later_model_local_config_plan_v0_1.json`；
  - `data/protocols/evp8_later_model_preflight_summary_v0_1.json`；
  - `data/protocols/evp8_later_model_full_check_only_v0_1.json`；
- 刷新 G7 completion packet：
  - `runner_implementation_checked = true`；
  - `later_model_structural_preflight_checked = true`；
  - `later_model_full_check_only_passed = true`；
  - `later_model_strict_preflight_ready_for_user_execute_command = false`；
  - `later_model_credential_presence_ready = false`；
  - `execution_authorized_by_packet = false`。

Verify:

- `python -m py_compile src\cross_review\openrouter.py scripts\create_evp8_later_model_local_config.py scripts\preflight_evp8_later_models.py scripts\run_evp8_later_model_full.py scripts\write_evp8_later_model_completion_packet.py`
  通过；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过；
- `python scripts\create_evp8_later_model_local_config.py --write --force`
  通过：
  - target local config ignored；
  - contains_api_key_values false；
  - planned_total_later_model_calls = 2058；
- `python scripts\preflight_evp8_later_models.py --config configs\evp8_later_models.local.json --allow-missing-credentials`
  通过：
  - `structural_ready = true`；
  - `preflight_status = structural_only`；
  - `credential_presence_ready = false`；
  - `OPENROUTER_API_KEY` state = `missing`；
  - `api_call_attempted = false`；
  - `api_key_values_printed = false`；
- `python scripts\run_evp8_later_model_full.py --check-only --run-scope full --config configs\evp8_later_models.local.json --allow-missing-credentials`
  通过：
  - `check_only_status = passed`；
  - `packet_count_per_model = 686`；
  - `expected_total_later_model_calls = 2058`；
  - `prompt_hashes_unique_count = 686`；
  - no API / no raw outputs；
- `python scripts\write_evp8_later_model_completion_packet.py --check` 通过；
- `python scripts\audit_evp8_first_batch_full_results.py --check` 通过；
- `python scripts\summarize_evp8_first_batch_full_synthesis.py --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅有 Git LF/CRLF 工作区转换 warning；
- sensitive-boundary scan 只命中环境变量名、runner 内部 raw-output 字段名和
  no-key boolean fields；未发现 API key value 或 tracked raw response text；
- G7 packet 当前清楚区分：
  - runner/preflight/check-only structural readiness；
  - strict credential readiness false；
  - no execution authorization。

Decision:

- G7.1 runner/preflight 已按计划完成到无 API structural-ready；
- 当前不能继续执行 later-model API，因为 `OPENROUTER_API_KEY` 在 ignored
  `.env` 中 missing，strict preflight 未通过；
- 下一步应二选一：
  - 用户提供/配置 `OPENROUTER_API_KEY` 后，重跑 strict preflight，再逐模型
    显式授权执行；
  - 在 API 前继续补 later-model post-run audit/synthesis scaffold，减少跑完后
    缺审计脚本的风险。

Commit And Sync:

- 已提交本轮 G7.1 runner/preflight：
  `ddca89f Add EVP-8 later-model runner preflight`；
- 第一次 `git push origin main` 失败：
  `Recv failure: Connection was reset`；
- 第二次 `git push origin main` 失败：
  `Failed to connect to github.com port 443 after 21102 ms`；
- 当前 `git status --short --branch` 显示
  `main...origin/main [ahead 1]`；
- 根据用户已授权的 GitHub 频繁同步失败处理规则，本轮不继续卡在 push；
  后续会话可在网络恢复后直接重试 push。

## 2026-06-21 EVP-8 G7.2 OpenRouter strict preflight

Inspect:

- 用户说明 OpenRouter API key 已加入；
- `git status --short --branch --untracked-files=all` 显示
  `main...origin/main [ahead 2]`，工作区 clean；
- `git log -5 --oneline` 当前顶部为：
  - `b2729b9 Record EVP-8 G7.1 sync blocker`；
  - `ddca89f Add EVP-8 later-model runner preflight`；
  - `79ff382 Prepare EVP-8 later-model packet`；
- 上轮 G7.1 状态是 structural preflight/check-only passed，但
  `OPENROUTER_API_KEY` missing，因此 strict API-ready blocked；
- 本轮用户只说明 key 已加入，不等同于三模型 API 授权。

Plan:

1. 重跑 `scripts\preflight_evp8_later_models.py` strict preflight；
2. 若 strict preflight 通过，刷新 G7 completion packet，使
   `later_model_strict_preflight_ready_for_user_execute_command=true`；
3. 继续不调用 Kimi/Devstral/Gemini API；
4. 更新 current plan、short-state、EVP-8 execution plan 和 INDEX 如有状态变化；
5. 运行 completion packet check、later-model check-only、local quality gate、
   `git diff --check`；
6. 提交本轮 strict-preflight 状态；GitHub push 若继续失败则记录并继续。

Boundary:

- 本轮只验证 credential presence，不打印或提交 key value；
- 不执行 `run_evp8_later_model_full.py --execute`；
- 不生成 later-model raw outputs；
- 不把 strict preflight ready 写成模型结果或五模型结论。

Execute / Diagnose / Repair:

- 第一次 strict preflight 仍失败，tracked summary 显示
  `credential_presence_ready=false`、`OPENROUTER_API_KEY=missing`；
- 安全核对 `.env` 时只打印 key metadata，不打印 key value；发现第 5 行变量名是
  lowercase `openrouter_api_key`，PowerShell case-insensitive probe 会误判为
  present，但 Python preflight 精确匹配 `OPENROUTER_API_KEY`；
- 仅修正 ignored `.env` 中变量名大小写，保留密钥值不输出、不提交；
- 重新运行 strict preflight 后通过：
  - `preflight_status = passed`；
  - `credential_presence_ready = true`；
  - `ready_for_user_execute_command = true`；
  - `api_call_attempted = false`；
  - `api_key_values_printed = false`；
- 运行 `python scripts\write_evp8_later_model_completion_packet.py` 刷新
  completion packet；
- 运行
  `python scripts\run_evp8_later_model_full.py --check-only --run-scope full --config configs\evp8_later_models.local.json --allow-missing-credentials`
  通过：
  - `packet_count_per_model = 686`；
  - `expected_total_later_model_calls = 2058`；
  - `preflight_ready_for_user_execute_command = true`；
  - no API / no raw outputs。

Decision:

- G7.2 strict OpenRouter preflight 已通过，当前可以进入“等待用户逐模型明确
  execute 授权”的状态；
- 这仍不等同于 Kimi/Devstral/Gemini 真实 API 授权；
- 若继续保守推进，API 前还可以先实现 later-model post-run audit/synthesis
  scaffold，避免跑完后缺审计闭环。

Verify:

- `python scripts\write_evp8_later_model_completion_packet.py --check` 通过；
- `python scripts\run_evp8_later_model_full.py --check-only --run-scope full --config configs\evp8_later_models.local.json --allow-missing-credentials`
  通过；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅有 LF/CRLF 工作区转换 warning；
- completion packet、preflight summary、later-model check-only summary、
  README、INDEX、EVP-8 execution plan、short-state 和 engineering notes 已同步到
  strict-ready 状态；
- 本轮未调用 OpenRouter/Kimi/Devstral/Gemini API，未生成 later-model raw
  outputs，未输出 API key value。

Commit And Sync:

- 已提交 strict preflight readiness：
  `40ae224 Record EVP-8 OpenRouter strict preflight`；
- `git push origin main` 成功，将本地 `79ff382..40ae224` 同步到远端；
- push 后 `git status --short --branch --untracked-files=all` 显示
  `main...origin/main`；
- 发现 `docs/plans/current_project_state_zh.md` 仍保留 push 前 ahead 文本，
  因此追加本 post-push state repair，避免下一会话误判 GitHub 仍阻塞。
- post-push repair 验证：
  - stale-status 搜索只命中 G7.1 历史日志，不命中当前 short-state/README/INDEX；
  - `git diff --check` 通过，仅有 LF/CRLF 工作区转换 warning；
  - `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
    通过。
- post-push repair 提交后再次尝试 `git push origin main`，失败：
  `Failed to connect to github.com port 443 after 21082 ms`；
- 因该提交尚未推送，已将本 post-push repair commit amend 为当前真实状态：
  `40ae224` 已远端同步，post-push state repair 本地 ahead 1。

## 2026-06-21 EVP-8 G7.3 later-model post-run audit/synthesis scaffold

Inspect:

- 用户选择“先补”，按上一轮建议解释为先补 later-model post-run
  audit/synthesis scaffold，而不是执行 Kimi/Devstral/Gemini API；
- `git status --short --branch --untracked-files=all` 当前为
  `main...origin/main [ahead 1]`；
- 本地 ahead 1 是上一轮 post-push state repair：
  `8ceeef2 Fix EVP-8 post-push state entry`；
- 远端已包含 `40ae224 Record EVP-8 OpenRouter strict preflight`，即
  G7.2 strict preflight readiness 已同步；
- 已读取 existing first-batch full-run audit/synthesis 脚本，later-model
  runner summary schema，以及 G7 later-model completion packet；later-model
  packet 使用 `models` records，不同于 first-batch packet 的 execute list，
  因此需要独立 later-model audit 脚本。

Plan:

1. 新增 later-model full-result audit scaffold：
   - 读取 G7 completion packet 的三模型 expected tracked summary paths；
   - 在 summary 不存在时返回 `waiting_for_execution` 并通过 check；
   - 在 summary 存在时验证 686 records、98 per level、parse-valid、model/
     provider route、actual model/provider metadata、usage/cost gate、raw-output
     boundary 和 no prompt/raw text in tracked summary；
   - audit 本身不读 raw JSONL、不调用 API。
2. 新增 five-model synthesis scaffold：
   - 读取 first-batch synthesis 和 later-model audit；
   - 在 later models 未跑时返回 `waiting_for_later_models`；
   - 在部分 later model 通过时返回 partial waiting；
   - 只有 DeepSeek/Qwen first batch passed 且三 later models 均 audit passed
     后才允许 `passed` five-model synthesis；
   - synthesis 不读 raw outputs，不生成最终 claims。
3. 更新 completion packet guard command list、EVP-8 canonical plan、short-state、
   README/INDEX 和 engineering notes。
4. 运行 py_compile、later audit check、five-model synthesis check、completion
   packet check、later-model check-only、local quality gate、diff check。
5. 提交本轮 scaffold；GitHub push 若继续失败则记录，不阻塞后续本地计划。

Boundary:

- 本轮不执行 `run_evp8_later_model_full.py --execute`；
- 不调用 OpenRouter/Kimi/Devstral/Gemini API；
- 不读取 ignored raw responses；
- 不把 waiting scaffold 写成 later-model 结果或 five-model journal conclusion。

Execute:

- 新增 `scripts\audit_evp8_later_model_full_results.py`：
  - 当前三 later-model tracked summaries 均不存在时，输出
    `audit_status = waiting_for_execution`；
  - 未来 summary 存在时检查 686 records、98 per level、parse-valid、configured/
    request/actual model、actual provider、OpenRouter metadata、cost gate、
    raw path 和 tracked summary 不含 raw/prompt text；
  - audit 本身 `api_call_attempted=false`、`raw_outputs_read=false`。
- 新增 `scripts\summarize_evp8_five_model_synthesis.py`：
  - 读取 first-batch full synthesis 和 later-model audit；
  - 当前输出 `synthesis_status = waiting_for_later_models`；
  - 只有 later audit 三模型均 passed 后才允许 five-model synthesis 进入
    `passed`；
  - synthesis 本身 `api_call_attempted=false`、`raw_outputs_read=false`。
- 更新 `scripts\write_evp8_later_model_completion_packet.py`，把两个新脚本加入
  G7 guard command list 和 post-later-model requirements；
- 刷新 G7 completion packet JSON/Markdown；
- 新增 tracked scaffold artifacts：
  - `data/protocols/evp8_later_model_full_result_audit_v0_1.json`；
  - `docs/experiments/evp8_later_model_full_result_audit_v0_1.md`；
  - `data/protocols/evp8_five_model_synthesis_v0_1.json`；
  - `docs/experiments/evp8_five_model_synthesis_v0_1.md`；
- 同步 README、INDEX、EVP-8 canonical execution plan、short-state 和
  engineering notes。

Verify:

- `python -m py_compile scripts\audit_evp8_later_model_full_results.py scripts\summarize_evp8_five_model_synthesis.py scripts\write_evp8_later_model_completion_packet.py`
  通过；
- `python scripts\write_evp8_later_model_completion_packet.py --check` 通过；
- `python scripts\audit_evp8_later_model_full_results.py --check` 通过，当前
  `audit_status = waiting_for_execution`、summary present count = 0/3；
- `python scripts\summarize_evp8_five_model_synthesis.py --check` 通过，当前
  `synthesis_status = waiting_for_later_models`、later summary present count =
  0/3；
- 当前仍未调用 API，未读取 ignored raw outputs，未生成 later-model raw outputs。
- `python scripts\run_evp8_later_model_full.py --check-only --run-scope full --config configs\evp8_later_models.local.json --allow-missing-credentials`
  通过；
- `python scripts\audit_evp8_protocol_spec.py --check` 通过；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md`
  通过；
- `git diff --check` 通过，仅有 LF/CRLF 工作区转换 warning；
- sensitive scan 未发现 API key pattern。

Commit And Sync:

- 已提交本轮 scaffold：
  `eaecfeb Add EVP-8 later-model audit scaffold`；
- `git push origin main` 成功，将 `40ae224..eaecfeb` 同步到远端；
- push 后 `git status --short --branch --untracked-files=all` 显示
  `main...origin/main`；
- 本 post-push state repair 只修正短状态和 current plan 的同步记录。

## 2026-06-21 EVP-8 G8 later-model full execution authorization

Inspect:

- 用户回复“全部授权”，按上一轮 gate 解释为授权三 later models 的真实 full
  execution：
  - `moonshotai/kimi-k2.6`；
  - `mistralai/devstral-2512`；
  - `google/gemini-2.5-flash`；
- `git status --short --branch --untracked-files=all` 显示
  `main...origin/main`；
- `git log -5 --oneline` 顶部为：
  - `6973a57 Sync EVP-8 G7.3 state entry`；
  - `eaecfeb Add EVP-8 later-model audit scaffold`；
  - `8ceeef2 Fix EVP-8 post-push state entry`；
  - `40ae224 Record EVP-8 OpenRouter strict preflight`；
- G7 completion packet 当前 `packet_status=ready`，三模型 expected raw/summary
  outputs 均 absent；strict preflight ready 为 true；
- G7.3 audit/synthesis scaffold 当前 waiting-state passed。

Plan:

1. 先重跑 no-API / no-model-call guards：
   - OpenRouter public catalog audit；
   - strict preflight；
   - later-model full check-only；
   - G7 completion packet check；
   - later-model result audit check；
   - five-model synthesis check。
2. 若 guards 全部通过，按 packet 顺序逐模型执行：
   1. `moonshotai/kimi-k2.6`；
   2. `mistralai/devstral-2512`；
   3. `google/gemini-2.5-flash`。
3. 每个模型执行后立刻运行 later-model audit：
   - 若 parse/cost/provider/model/raw-boundary 任一失败，停止后续模型并诊断；
   - 若 audit 是 partial waiting 或 passed，继续下一授权模型。
4. 三模型均通过后运行 five-model synthesis check，刷新 docs/current state/index。
5. 运行 local quality gate、diff check、sensitive scan，提交并同步 GitHub。

Boundary:

- 本轮可以调用 OpenRouter later-model API，仅限上述三 model id 和 frozen EVP-8
  v0.1 98 candidates x 7 levels；
- 不修改 prompt/schema/candidate set/evaluator joins；
- raw responses 只能写入 ignored `outputs/evp8_phase2_later_models_full/`；
- tracked summaries 只能是不含 prompt/raw response text 的 aggregate JSON；
- 若发现协议、parser、cost、provider 或 raw-boundary 问题，先停止诊断，不把
  partial run 写成 five-model result。

Execute / Diagnose:

- `git commit -m "Authorize EVP-8 later-model full runs"` 已创建本地提交
  `9db3c4e`；
- `git push origin main` 失败：
  `Failed to connect to github.com port 443 after 21073 ms`；
- 按用户既定规则，GitHub 网络同步失败不阻塞本地执行；
- 已重跑 execution guards：
  - OpenRouter public catalog audit：`all_available=true`；
  - strict preflight：`preflight_status=passed`、
    `credential_presence_ready=true`；
  - later-model full check-only：`check_only_status=passed`、
    `packet_count_per_model=686`；
  - G7 completion packet check passed；
  - later-model audit check：`waiting_for_execution`；
  - five-model synthesis check：`waiting_for_later_models`；
- 开始执行 `moonshotai/kimi-k2.6` 后，外层 2 小时命令超时；
- 核查发现 Kimi 执行进程仍在运行，ignored raw prefix 持续增长但速度约
  1 条 / 1-2 分钟；串行完成三模型耗时不可接受；
- 停止 Kimi 串行进程后，ignored raw prefix 保留 99 条，tracked summary 尚未
  生成；
- 该问题类型定位为执行链路吞吐问题，不是 protocol/prompt/schema/candidate
  问题。

Repair:

- 给 `scripts\run_evp8_later_model_full.py` 增加显式 `--concurrency` 参数；
- 默认仍为 `--concurrency 1`，check-only 不允许使用 concurrency；
- execute 并发模式下请求可并行完成，但 raw JSONL 仍按 frozen packet order
  写入，保持 `--resume` 的 prefix 校验语义；
- tracked summary 新增 `concurrency` 字段；
- 已验证：
  - `python -m py_compile scripts\run_evp8_later_model_full.py` 通过；
  - `python scripts\run_evp8_later_model_full.py --check-only --run-scope full --config configs\evp8_later_models.local.json --allow-missing-credentials`
    通过；
  - 当前无活跃 Kimi execution process；
  - Kimi ignored raw prefix = 99 records。

Next Execute:

- 提交并尝试同步本 concurrency repair；
- 若 push 仍失败，继续本地执行；
- 使用
  `python scripts\run_evp8_later_model_full.py --execute --run-scope full --config configs\evp8_later_models.local.json --model-id moonshotai/kimi-k2.6 --resume --concurrency 4`
  从 99-record prefix 继续。

Second Diagnose / Repair:

- Kimi `--resume --concurrency 4` 从 99 条 prefix 继续后，在 154 条 raw prefix
  处停止；
- 失败原因为 OpenRouter 返回非 JSON body，`OpenRouter response was not valid
  JSON`；
- 当前无 Kimi execution 残留进程，tracked summary 仍不存在；
- 问题类型定位为 API/transport transient response classification，不是 model
  parse/result failure，也不是 protocol/prompt/schema 问题；
- 修复 `src\cross_review\openrouter.py`：
  - 将 `json.JSONDecodeError` 纳入已有 retry budget；
  - 最终仍失败时只输出 sanitized/truncated body，不输出 API key；
  - 不改变 request payload、prompt、schema、candidate set 或 evidence packets；
- 下一步重新 py_compile/check-only 后提交，再从 154-record prefix resume。

Third Diagnose / Repair:

- Kimi clean-up resume 最终写满 686 条 ignored raw records，并生成
  `data\reviews\evp8_moonshotai_kimi-k2.6_full_summary.json`，但 runner
  正确阻断：`later_model_full_gate=blocked`；
- 结构化诊断结果：
  - `review_count=686`；
  - `parse_valid_count=607`；
  - `invalid_parse_count=79`；
  - invalid 全部为 `invalid_json:No JSON object found in model response`；
  - invalid 分布覆盖 E0-E6，不是单一 evidence 层或 candidate 的局部问题；
  - 78/79 条仍有 provider-reported cost，1 条缺 usage/provider metadata；
  - 主要失败形态是 Kimi `message.reasoning` 非空而 `message.content`
    为空或不可解析，且 finish_reason 多为 `length`。
- 问题类型定位为 later-model routing/inference setting 问题，不是
  prompt/schema/candidate/frozen packet 问题；
- 不允许只重跑 79 个 invalid packets，因为这会让同一个 Kimi 模型内混用
  两套 inference settings，破坏模型内一致性；
- OpenRouter public model catalog 显示 `moonshotai/kimi-k2.6` 的 reasoning
  `default_enabled=true`、`mandatory=false`，并支持 `reasoning` 与
  `include_reasoning` 参数；
- 最短且更严谨的 repair 是：
  1. 将本次 Kimi 686-record run 作为 ignored blocked attempt 保留；
  2. 在 EVP-8 routing policy 中显式加入 Kimi
     `reasoning.enabled=false`、`include_reasoning=false`；
  3. 使用同一 frozen candidates / packets / prompt / schema 重新跑完整
     Kimi 686 records；
  4. clean rerun 通过 later-model audit 前，不启动 Devstral/Gemini，也不写
     five-model claim。

本轮执行边界：

- 可以修改 OpenRouter client、later-model runner、preflight、protocol audit
  和 tracked docs，使 Kimi reasoning control 成为可审计 routing policy；
- 不改变 evidence levels、candidate set、prompt template、output schema 或
  DeepSeek/Qwen first-batch 结果；
- 提交同步后，移动 ignored blocked Kimi raw/summary 到 ignored backup，再用
  canonical Kimi 路径重新执行 clean full run。

Fourth Execute Gate:

- Kimi reasoning-disabled clean full rerun 已从 canonical ignored path 重新开始；
- 当前 canonical raw prefix 为 551 / 686 records，tracked summary 尚未生成；
- runner 已退出，当前无活跃 `run_evp8_later_model_full.py` Python 进程；
- 最新 stderr 显示 OpenRouter provider returned HTTP 429，message 为
  `moonshotai/kimi-k2.6 is temporarily rate-limited upstream`；
- 问题类型定位为 API/provider rate-limit interruption，不是
  prompt/schema/candidate/frozen packet 或 Kimi parse validity failure；
- ordered raw prefix 已存在且 summary absent，因此不能删除 prefix、不能切换到
  Devstral/Gemini、不能把 partial prefix 写成 result。

Next Execute:

- 先提交并同步本 429 resume boundary 文档；
- 之后使用同一 ignored local config、同一 frozen EVP-8 packet set、同一
  Kimi reasoning-disabled request policy，从 551-record prefix 继续：
  `python scripts\run_evp8_later_model_full.py --execute --run-scope full --config configs\evp8_later_models.local.json --model-id moonshotai/kimi-k2.6 --resume --concurrency 2`；
- 若再次 provider 429，则继续按执行链路问题处理：降低并发或等待后 resume；
- 只有当 Kimi clean rerun 生成 summary 且 later-model audit 通过后，才允许进入
  Devstral/Gemini 或 five-model synthesis。

Fifth Diagnose / Repair:

- `--resume --concurrency 2` 已写满 686 条 canonical ignored raw records，并生成
  Kimi clean summary，但 final gate 仍正确阻断；
- 结构化结果：
  - `review_count=686`；
  - `parse_valid_count=682`；
  - `invalid_parse_count=4`；
  - invalid 分布为 E0=2、E2=1、E6=1；
  - `usage_cost_gate=blocked`、`provider_metadata_gate=blocked`；
  - actual model/provider missing 均为 4；
  - `request_reasoning={"enabled": false}`、`request_include_reasoning=false`
    已记录在 summary/raw metadata；
- 4 条 invalid raw record 的共同结构是：
  - `raw_response_text` 为空；
  - response 顶层只有 `error`、`latency_ms`、`request_attempts`；
  - `error.code=429`、`error.message="Provider returned error"`；
  - 无 choices、usage、actual model、actual provider 或 OpenRouter metadata。
- 问题类型定位为执行链路 bug：OpenRouter 返回 HTTP 200 JSON 但顶层含 retryable
  `error.code=429` 时，client 没有把它当作 transport/rate-limit failure 重试，
  runner 因而把 provider error 写入 raw prefix。
- Repair:
  1. `src/cross_review/openrouter.py` 将顶层 JSON `error.code` 为 429/5xx
     的 response 纳入已有 retry budget；最终失败时仍只输出 sanitized detail；
  2. 同步 redaction，避免 OpenRouter error detail 中的 `user_id` 被写入
     human-facing output；
  3. `scripts/run_evp8_later_model_full.py` 用 local config/protocol 中的
     `retry_policy.max_retries_per_record` 创建 OpenRouter client，并把
     retry policy 写入 tracked summary；
  4. 将本次 682/686 blocked clean attempt 移入 ignored backup；
  5. 提交同步后，从空 canonical Kimi path 重新跑完整 reasoning-disabled Kimi。
- 不允许修补 4 条 raw record 后把本次 run 当作 passed；该 raw 文件已经包含
  provider error records，必须作为 ignored blocked attempt 保留。

Sixth Execute Result:

- 按 repair 后代码从空 canonical path 重跑 Kimi reasoning-disabled full run，
  `--concurrency 2`，无 stderr，进程正常退出；
- Kimi clean summary 已生成：
  - `review_count=686`；
  - `parse_valid_count=686`；
  - `invalid_parse_count=0`；
  - `later_model_full_gate=passed`；
  - `usage_cost_gate=passed`；
  - `provider_metadata_gate=passed`；
  - `request_reasoning={"enabled": false}`；
  - `request_include_reasoning=false`；
  - `actual_model_id_counts={"moonshotai/kimi-k2.6-20260420":686}`；
  - `actual_provider_counts={"Chutes":686}`；
  - `cost_observability_counts={"provider_reported_cost":686}`；
  - `total_cost_usd=1.02450976`；
  - decision counts 为 `escalate=672`、`reject=14`。
- `scripts/audit_evp8_later_model_full_results.py --check` 已通过当前 partial
  状态：Kimi `status=passed`，Devstral/Gemini 仍 `waiting_for_execution`，
  overall audit 为 `partial_waiting_for_remaining_later_models`；
- `scripts/summarize_evp8_five_model_synthesis.py --check` 已通过 partial
  状态：DeepSeek/Qwen/Kimi 三模型 per-level counts 可读，但 forbidden claim
  仍禁止 five-model journal conclusion；
- 本轮可提交：
  - Kimi raw-output-free tracked summary；
  - later-model audit JSON/Markdown partial artifact；
  - 当前计划、README、INDEX、short-state 和 engineering notes；
- raw responses 和 blocked attempts 仍只保留在 ignored `outputs/`。

Next Execute:

- 提交并尝试同步 Kimi passed result；
- 若 GitHub 继续网络失败，按用户授权保留本地 ahead 并继续；
- 下一模型按 packet 顺序为 `mistralai/devstral-2512`，但必须在 Kimi result
  commit 后执行，并复用同一 frozen EVP-8 packets、prompt、schema、parser、
  cost/provider audit 和 OpenRouter exact model route policy。

## 2026-06-22 EVP-8 Devstral later-model result closure

Inspect:

- Kimi result commit 已同步后，工作区回到 `main...origin/main`；
- strict later-model preflight 和 full check-only 均已通过；
- Devstral canonical raw/summary path 起跑前不存在 tracked result；
- 用户已给出后续 later-model API 授权，且 `OPENROUTER_API_KEY` presence 已由
  strict preflight 记录在 no-secret summary 中。

Plan:

1. 按 G7/G8 frozen packet 顺序执行 `mistralai/devstral-2512` full run；
2. 使用同一 EVP-8 v0.1 frozen candidate set、prompt、schema、parser、
   temperature、OpenRouter exact model route policy 和 cost/provider audit；
3. Devstral 完成后立刻运行 later-model audit 和 five-model synthesis check；
4. 只有 Devstral summary 通过 parse/cost/provider/model/raw-boundary gates 后，
   才允许提交并继续 Gemini；
5. partial synthesis 仍不得写成 five-model journal conclusion。

Execute Result:

- Devstral full run 使用 `--concurrency 2` 正常退出，stderr 为空；
- tracked raw-output-free summary 已生成：
  - `review_count=686`；
  - `parse_valid_count=686`；
  - `invalid_parse_count=0`；
  - `later_model_full_gate=passed`；
  - `run_gate=passed`；
  - `usage_cost_gate=passed`；
  - `provider_metadata_gate=passed`；
  - `actual_model_id_counts={"mistralai/devstral-2512":686}`；
  - `actual_provider_counts={"Mistral":686}`；
  - `cost_observability_counts={"provider_reported_cost":686}`；
  - `total_cost_usd=0.44937088`；
  - decision counts 为 `escalate=686`。

Verify:

- `scripts/audit_evp8_later_model_full_results.py --check` 已通过当前 partial
  状态：Kimi 和 Devstral `status=passed`，Gemini 仍
  `waiting_for_execution`，overall audit 为
  `partial_waiting_for_remaining_later_models`；
- `scripts/summarize_evp8_five_model_synthesis.py --check` 已通过 partial
  状态：DeepSeek/Qwen/Kimi/Devstral 四模型 per-level counts 可读，但
  forbidden claim 仍禁止 five-model journal conclusion；
- Devstral tracked summary 不存储 prompt text 或 raw response text；
- raw responses 和 stdout/stderr logs 仍只保留在 ignored `outputs/`。

Next Execute:

- 提交并尝试同步 Devstral passed result；
- 若 GitHub 继续网络失败，按用户授权记录同步失败并继续；
- 同步后按 packet 顺序进入 `google/gemini-2.5-flash`，先重跑 strict
  preflight/check-only 和 expected-output absence，再执行 Gemini full run。

## 2026-06-22 EVP-8 Gemini later-model and five-model synthesis closure

Inspect:

- Devstral result 已本地提交为 `68aa683 Record EVP-8 Devstral later-model
  result`；
- `git push origin main` 连续出现 GitHub network-level connection failure，
  本地 `main` 因此保持 ahead；用户已明确允许 GitHub 同步频繁失败时继续计划；
- 无残留 later-model runner；Gemini raw/summary canonical path 起跑前不存在；
- strict later-model preflight 重新通过，`OPENROUTER_API_KEY` presence 为 set；
- Gemini 单模型 check-only 通过：686 prompts，schema/boundary error 为 0，
  未生成 raw outputs。

Plan:

1. 使用同一 frozen EVP-8 v0.1 packets、prompt、schema、parser、temperature、
   retry policy、OpenRouter exact model route policy 执行
   `google/gemini-2.5-flash`；
2. 使用 `--concurrency 2`，stderr/raw prefix 监控到进程结束；
3. Gemini 完成后立刻检查 summary gates；
4. 运行 later-model audit 和 five-model synthesis check；
5. 只在 tracked summary/audit/synthesis 全部通过后更新 docs/index/state 并提交。

Execute Result:

- Gemini full run 正常退出，stderr 为空，ignored raw JSONL 为 686/686 lines；
- tracked raw-output-free summary 已生成：
  - `review_count=686`；
  - `parse_valid_count=686`；
  - `invalid_parse_count=0`；
  - `later_model_full_gate=passed`；
  - `run_gate=passed`；
  - `usage_cost_gate=passed`；
  - `provider_metadata_gate=passed`；
  - `actual_model_id_counts={"google/gemini-2.5-flash":686}`；
  - `actual_provider_counts={"Google":686}`；
  - `cost_observability_counts={"provider_reported_cost":686}`；
  - `total_cost_usd=0.6294286`；
  - decision counts 为 `escalate=683`、`reject=3`。

Verify:

- `scripts/audit_evp8_later_model_full_results.py --check` 已通过：
  Kimi、Devstral、Gemini 三个 later models 均 `status=passed`，
  `passed_model_count=3`，`summary_present_count=3`；
- `scripts/summarize_evp8_five_model_synthesis.py --check` 已通过：
  `synthesis_status=passed`，DeepSeek/Qwen/Kimi/Devstral/Gemini 五模型
  per-level counts 可读；
- audit/synthesis 均不读取 raw outputs，不触发 API；
- Gemini tracked summary 不存储 prompt text 或 raw response text；
- 当前允许 claim：仅报告 frozen EVP-8 v0.1 packet set 上的描述性五模型
  per-level decision patterns；
- 当前仍禁止 claim：LLM superiority over deterministic baselines、最终
  evidence-level effectiveness、跨规模 generalization。

Next Execute:

- 暂存并提交 Gemini summary、later-model audit、five-model synthesis、README、
  INDEX、short-state、current plan、engineering notes 和 EVP-8 execution plan；
- 尝试 GitHub sync；若继续网络失败，记录 ahead 状态并进入本地 paper/table/
  artifact freeze；
- 下一阶段不再补模型，先生成论文可用的 five-model tables/figures、claim
  boundary audit 和 artifact freeze checklist。

## 2026-06-22 EVP-8 cost overrun audit and G9 paper-table freeze

Inspect:

- 用户指出成本完全超预算；必须先停止所有 API 路径，不再补模型；
- 本地 `main...origin/main [ahead 2]`，未同步提交为 Devstral result 和
  Gemini five-model synthesis；GitHub push 已多次 connection reset；
- tracked passed summaries 显示 EVP-8 五模型均 `686/686` valid；
- 成本拆分：
  - passed tracked USD，不含 Qwen：`2.892118056`；
  - Qwen passed tracked CNY：`41.119548`；
  - ignored Kimi blocked attempts USD：`7.27612053`；
  - 实际可观测 USD 合计，不含 Qwen：`10.168238586`；
- later-model completion packet 的 USD 30 planning ceiling 是 later-model
  batch planning ceiling，不包含 DeepSeek/Qwen，也不是失败重跑的保护机制。

Plan:

1. 新增 no-API cost accounting summary builder，只读取 raw-output-free
   summaries 和 ignored blocked-attempt summaries，不读取 raw response text；
2. 生成 tracked cost accounting JSON/Markdown，明确 passed-result cost、
   blocked-attempt cost、预算解释和 API freeze decision；
3. 扩展 `write_paper_tables.py`，把 EVP-8 five-model decision patterns 和
   cost accounting ledger 写入 generated paper tables；
4. 更新 README、INDEX、short-state 和 engineering notes；
5. 运行 cost builder、paper table builder、audit/synthesis checks、diff/sensitive
   checks；
6. 提交本轮 no-API G9 成本审计和表格更新；不再尝试任何模型 API。

Boundary:

- 本轮不得调用 OpenRouter、DeepSeek、Qwen 或任何模型 API；
- blocked attempts 只能作为成本/执行风险审计，不得作为有效模型结果；
- five-model synthesis 只支持 frozen EVP-8 v0.1 descriptive decision-pattern
  reporting，不支持 deterministic-baseline superiority 或 final effectiveness。

## 2026-06-22 SQJ low-cost submission route final-plan update

Inspect:

- 用户要求将 D 类及以上、低经济成本、稳定中稿和含金量尽量高的目标写入最终计划；
- 学校文件《太原理工大学学术论文类别认定办法》显示 CCF C 类国际期刊/会议论文
  属于 C 类，C 类高于 D 类；EI 正刊也属于 C 类，但会议论文集/增刊等口径不同；
- 当前最短路径不是继续补模型或扩量，而是冻结 EVP-8 五模型结果，转入 SQJ
  software quality/reliability 期刊稿；
- Git 当前仍以 `git status --short --branch` 为准，本地 main 可能因 GitHub
  connection reset 保持 ahead。

Plan:

1. 在 canonical `docs/plans/final_paper_roadmap_zh.md` 中加入 SQJ 低成本投稿
   路线，明确学校 D 类及以上认定链路、CCF C 类确认门、非 OA / subscription
   route、Springer `sn-jnl` LaTeX 模板和投稿前学校确认；
2. 将 EVP-8 后续执行顺序从“继续模型/API”修正为 no-API SQJ paper route：
   claim-boundary audit -> SQJ framing -> Springer `sn-jnl` draft ->
   figures/tables -> artifact freeze -> school-recognition confirmation ->
   submission；
3. 同步 README、docs index、short-state、EVP-8 execution plan 和 engineering
   notes，避免后续 agent 继续维护 IEEEtran 作为下一投稿主稿；
4. 运行 targeted consistency checks、diff checks、敏感信息扫描；
5. 提交并尝试 GitHub sync；若继续 connection reset，记录 ahead 状态并继续本地。

Boundary:

- 本轮不调用任何模型 API，不扩量，不补新 bug；
- SQJ 只是当前首选低成本路线，不是学校最终认定保证；投稿前必须由学院/科研秘书
  确认 SQJ 当前 CCF C 类、学校 C 类口径、发表当年目录和高风险/预警名单状态；
- 不选择 Open Access，除非用户另行明确批准 APC；
- 不把录用通知当作学校认定材料；认定以正式发表或在线发表为准；
- 不把 `docs/paper/ieee_submission_draft.tex` 继续作为下一投稿主格式；下一主稿应
  转为 Springer Nature `sn-jnl` LaTeX。

Execute Result:

- 已更新 `docs/plans/final_paper_roadmap_zh.md`，新增 `18.8 SQJ 低成本投稿路线`；
- 已将 EVP-8 执行状态从“等待 first-batch/later-model 授权”修正为 five-model
  synthesis passed + API freeze；
- 已同步 README、docs index、short-state、EVP-8 execution plan 和 engineering
  notes；
- 已将 IEEEtran draft 降级为 historical/source draft，下一主稿格式改为 Springer
  Nature `sn-jnl` LaTeX。

Verify:

- targeted `rg` 检查确认 SQJ、`sn-jnl`、non-OA/APC、学校认定确认门和 API
  freeze 边界均已写入；
- targeted stale-plan 检查确认后续路线已收敛为 SQJ no-API paper route；
- `git diff --check` 通过，仅有 Windows LF/CRLF 提示；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness_audit\sqj_plan_update.json --out-md outputs\paper_readiness_audit\sqj_plan_update.md`
  已运行，`current_result_claim_ready=true` 且 `submission_package_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\sqj_plan_update.json --out-md outputs\local_quality_gate\sqj_plan_update.md`
  已运行，`passed=true`；
- 最终提交前仍需 staged diff、敏感信息扫描、commit 和 GitHub sync attempt。

## 2026-06-22 SQJ framing and claim-boundary packet

Inspect:

- 当前工作区干净且 `main...origin/main`；
- canonical final roadmap 已将下一步收敛为 SQJ no-API paper route；
- 旧 artifact handoff/checklist/freeze-candidate 仍保留 IEEE 投稿包语境，不能直接当作
  SQJ final freeze；
- 当前可直接执行的最短路径是先写 SQJ framing / claim-boundary packet，再进入
  Springer `sn-jnl` draft generation。

Plan:

1. 新增 `docs/paper/sqj_submission_framing.md`，明确 SQJ title、paper type、
   contribution、RQ、allowed claims、forbidden claims、EVP-8 result mapping、
   cost/risk framing、school-recognition gate 和 no-API boundary；
2. 同步 README、docs index、short-state 和 engineering notes；
3. 运行 no-API paper readiness / local quality gate，以及 targeted SQJ checks；
4. 提交并同步 GitHub。

Boundary:

- 本轮不新建模型 API、实验、候选 bug 或 raw output；
- 本轮不把旧 IEEE artifact handoff/checklist 直接改成 final SQJ freeze；
- SQJ 认可仍需学院/科研秘书确认，文档只记录投稿路线和 claim boundary。

Execute Result:

- 已新增 `docs/paper/sqj_submission_framing.md`；
- 该文档固定 SQJ target、non-OA/subscription route、Springer `sn-jnl` 下一格式、
  working title、RQ、allowed claims、forbidden claims、EVP-8 result mapping、
  cost/risk framing、school-recognition gate 和 no-API boundary；
- 已同步 README、docs index、short-state 和 engineering notes；
- 未生成 raw output，未调用任何模型 API，未改旧 IEEE artifact freeze-candidate。

Verify:

- `python scripts\summarize_evp8_five_model_synthesis.py --check` 已通过，
  `synthesis_status=passed` 且 `api_call_attempted=false`；
- `python scripts\summarize_evp8_cost_accounting.py --check` 已通过，
  `api_freeze=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness_audit\sqj_framing.json --out-md outputs\paper_readiness_audit\sqj_framing.md`
  已运行，当前 bounded readiness 仍为 `current_result_claim_ready=true` 和
  `submission_package_ready=true`；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\sqj_framing.json --out-md outputs\local_quality_gate\sqj_framing.md`
  已运行，`passed=true`；
- `git diff --check` 通过，仅有 Windows LF/CRLF 提示。

## 2026-06-22 SQJ sn-jnl source draft generation

Inspect:

- 当前 `docs/paper/sqj_submission_framing.md` 已固定 SQJ claim boundary；
- `kpsewhich sn-jnl.cls` 未找到本地 Springer Nature class，MiKTeX 提示尚未检查更新；
- 因此本轮只能生成 `sn-jnl` source draft 并做 source-structure gate，不做 PDF
  compile gate。

Plan:

1. 新建 `scripts/write_sqj_latex_draft.py`；
2. 从 EVP-8 five-model synthesis、cost accounting、generated tables 和 SQJ
   framing packet 生成 `docs/paper/sqj_submission_draft.tex`；
3. 生成 `docs/paper/sqj_references.bib`；
4. 用脚本内 `--check` 验证 `sn-jnl` class declaration、abstract、keywords、
   main sections、backmatter、bibliography、bounded claims 和 forbidden snippets；
5. 同步 README、INDEX、short-state 和 engineering notes。

Execute Result:

- 已新增 `scripts/write_sqj_latex_draft.py`；
- 已生成 `docs/paper/sqj_submission_draft.tex`，使用
  `\documentclass[pdflatex,sn-basic]{sn-jnl}`；
- 已生成 `docs/paper/sqj_references.bib`；
- SQJ source draft 当前包含 Introduction、Background and Related Work、
  Evidence Visibility Protocol、Candidate Patch and Evidence Packet
  Construction、Multi-Model Study、Results、Software Quality Risks、Threats to
  Validity、Artifact and Reproducibility、Conclusion，以及 Data availability、
  Code availability、Competing interests、Author contributions 和 Funding。

Verify:

- `python -m py_compile scripts\write_sqj_latex_draft.py` 通过；
- `python scripts\write_sqj_latex_draft.py --check` 通过，输出
  `api_call_attempted=false`、`compile_attempted=false`、`passed=true`；
- targeted `rg` 检查确认 `sn-jnl`、abstract、keywords、bounded claim、
  backmatter 和 bibliography 存在，且没有正向 LLM superiority 或 E6 strict
  superiority claim；
- 本轮未调用 API，未读取 raw model responses，未生成 PDF。

## 2026-06-22 SQJ submission checklist and audit gate

Inspect:

- 当前 `main...origin/main` 干净；
- SQJ `sn-jnl` source draft 已生成并通过 source-structure gate；
- 旧 `docs/artifact/submission_checklist.md` 和
  `docs/artifact/submission_handoff_20260618.md` 仍是 IEEE / EVP-7 四层
  投稿包语境，不能直接作为 SQJ final freeze；
- `docs/paper/sqj_submission_framing.md` 明确要求准备 SQJ-specific artifact
  checklist；
- 本机仍缺少 `sn-jnl.cls`，因此本轮不做 PDF compile gate。

Plan:

1. 新增 SQJ 专用 submission checklist，记录 manuscript source、BibTeX、
   generated tables、figures、claim boundary、cost boundary、school-recognition
   confirmation gate、non-OA route 和 no-API boundary；
2. 新增 SQJ checklist audit script，验证 required snippets、forbidden claims、
   source draft、BibTeX、figures 和 generator/check command；
3. 将 SQJ checklist audit 接入 local quality gate，避免后续只检查旧 IEEE
   handoff/checklist；
4. 同步 README、docs index、short-state 和 engineering notes；
5. 运行 py_compile、SQJ source/checklist audits、paper readiness、local quality、
   diff 和敏感信息检查；
6. 提交并同步 GitHub。

Boundary:

- 本轮不调用模型 API，不扩量，不补 bug，不读取 raw model responses；
- 本轮不下载或提交 Springer 模板文件；
- SQJ 学校认定仍是投稿前人工确认门，不写成保证；
- 本轮不把 SQJ package 标记为 final freeze，因为 PDF compile gate 仍被
  `sn-jnl.cls` 缺失阻塞。

Execute Result:

- 已新增 `docs/artifact/sqj_submission_checklist.md`；
- 已新增 `scripts/audit_sqj_submission_checklist.py`；
- 已将 SQJ checklist audit 接入 `scripts/audit_paper_readiness.py` 和
  `scripts/run_local_quality_gate.py`；
- 已同步 README、docs index、short-state、final roadmap 和 engineering notes；
- 未调用模型 API，未下载 Springer 模板，未编译 PDF。

Diagnose / Repair:

- 首次 SQJ checklist audit 失败属于执行链路 bug：
  1. cost accounting 字段读取错把 `decision.api_freeze` 和 `totals.*` 当作
     top-level 字段；
  2. forbidden-phrase scan 误把 checklist 中的 forbidden-claims section 当作
     正向越界声明。
- 已修复 audit 脚本，使其读取嵌套成本字段，并只拦截 checklist 中的正向越界声明。

Verify:

- `python -m py_compile scripts\audit_sqj_submission_checklist.py scripts\audit_paper_readiness.py scripts\run_local_quality_gate.py`
  通过；
- `python scripts\write_sqj_latex_draft.py --check` 通过，`api_call_attempted=false`、
  `compile_attempted=false`；
- `python scripts\audit_sqj_submission_checklist.py --out-json outputs\sqj_submission_checklist_audit\sqj_checklist.json --out-md outputs\sqj_submission_checklist_audit\sqj_checklist.md`
  通过；
- `python scripts\summarize_evp8_five_model_synthesis.py --check` 通过；
- `python scripts\summarize_evp8_cost_accounting.py --check` 通过，`api_freeze=true`；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness_audit\sqj_checklist_final.json --out-md outputs\paper_readiness_audit\sqj_checklist_final.md`
  通过，`submission_package_ready=true`，且旧 prompt-only positive claim blocker
  仍保留为边界；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\sqj_checklist.json --out-md outputs\local_quality_gate\sqj_checklist.md`
  通过，`passed=true`；
- `git diff --check` 通过，仅有 Windows LF/CRLF 提示。

## 2026-06-22 SQJ EVP-8 figure/layout pass

Inspect:

- 当前本地 `main...origin/main [ahead 1]`，ahead commit 为上一轮 SQJ checklist
  gate；工作区无未提交改动；
- SQJ draft 当前主结果是 EVP-8 five-model full-ladder study；
- 现有 `scripts/generate_paper_figures.py` 和 `docs/figures/figure_manifest.json`
  仍以旧 IEEE / EVP-7 figure set 为主；
- `docs/artifact/sqj_submission_checklist.md` 已明确 SQJ-specific figure
  placement and caption audit 仍待后续 layout pass；
- 本机仍缺少 `sn-jnl.cls`，因此本轮仍只做 source/figure gate，不做 PDF compile。

Plan:

1. 新增 Python/matplotlib 的 SQJ 专用 figure generator；
2. 生成 `docs/figures/sqj/` 下的三张 SQJ/EVP-8 主图：
   - protocol schematic；
   - five-model decision-pattern heatmap/aggregate curve；
   - valid-result cost 与 blocked-attempt cost boundary；
3. 将 SQJ draft generator 改为引用这三张 SQJ figures，并把 captions 绑定到
   bounded EVP-8 claim；
4. 将 SQJ checklist/audit 改为验证 SQJ-specific figures，而不是只验证旧
   EVP-7 figure set；
5. 同步 README、INDEX、short-state、figure README、engineering notes 和 current
   plan；
6. 运行 figure generation、SQJ source/checklist audits、paper readiness、local
   quality、diff/sensitive checks；
7. 提交，并尝试 GitHub sync；若 GitHub 仍连接失败，记录 ahead 状态并继续。

Boundary:

- 本轮不调用模型 API，不生成/读取 raw model responses，不扩量；
- 本轮不下载 Springer 模板、不编译 PDF；
- 不把三张 SQJ figures 解释为 LLM superiority 或 final evidence-level ranking；
- 保留旧 `docs/figures/` EVP-7 figures 作为 historical/reproducible assets，
  不覆盖旧 IEEE draft。

Execute Result:

- 已新增 `scripts/generate_sqj_figures.py`；
- 已生成 `docs/figures/sqj/` 下三张 SQJ/EVP-8 figures：
  `sqj_fig1_evp8_protocol`、`sqj_fig2_decision_patterns`、
  `sqj_fig3_cost_boundary`，每张均有 PDF/SVG/PNG；
- 已更新 `scripts/write_sqj_latex_draft.py`，使
  `docs/paper/sqj_submission_draft.tex` 引用三张 SQJ figures；
- 已更新 `scripts/audit_sqj_submission_checklist.py`，验证 SQJ-specific
  figure set 和非空 figure files；
- 已同步 README、docs index、short-state、figure README 和 engineering notes；
- 未调用模型 API，未读取 raw model responses，未下载 Springer 模板，未编译 PDF。

Diagnose / Repair:

- 初次把 `generate_sqj_figures.py` 和 figure audit 并行执行时，audit 在
  `sqj_fig2_decision_patterns.pdf` 写入过程中读到 size=0；该问题属于执行链路
  竞态，不是数据或实验问题。
- 已修复：
  1. 依赖链改为顺序执行：tables -> SQJ figures -> SQJ source -> SQJ audit ->
     paper readiness -> local quality；
  2. SQJ checklist audit 从只检查文件存在改为检查 figure 文件存在且
     `size_bytes > 0`；
  3. 修复 Fig.1 底部说明文字重叠；
  4. 修复 Fig.2 heatmap 因 `imshow` 默认等比例显示造成的水平留白。

Verify:

- `python -m py_compile scripts\generate_sqj_figures.py scripts\write_sqj_latex_draft.py scripts\audit_sqj_submission_checklist.py scripts\audit_paper_readiness.py scripts\run_local_quality_gate.py`
  通过；
- `python scripts\write_paper_tables.py` 通过；
- `python scripts\generate_sqj_figures.py` 通过，输出 3 figures x PDF/SVG/PNG；
- `Get-Item docs\figures\sqj\sqj_fig*.pdf,docs\figures\sqj\sqj_fig*.svg,docs\figures\sqj\sqj_fig*.png`
  确认所有 SQJ figure files 非空；
- `python scripts\write_sqj_latex_draft.py --check` 通过；
- `python scripts\audit_sqj_submission_checklist.py --out-json outputs\sqj_submission_checklist_audit\sqj_figures_final.json --out-md outputs\sqj_submission_checklist_audit\sqj_figures_final.md`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness_audit\sqj_figures_final.json --out-md outputs\paper_readiness_audit\sqj_figures_final.md`
  通过，`submission_package_ready=true`，旧 prompt-only positive claim blocker
  仍保留；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\sqj_figures.json --out-md outputs\local_quality_gate\sqj_figures.md`
  通过，`passed=true`。

## 2026-06-22 SQJ final-freeze readiness packet

Inspect:

- 当前 `main...origin/main` 已同步，工作区干净；
- SQJ source draft、BibTeX、SQJ checklist、SQJ figures 和 local quality gate
  已在上一轮通过；
- 本机仍缺少 `sn-jnl.cls`，因此不能把 PDF compile 作为已通过条件；
- 学校/学院 D 类及以上认可、作者信息、基金/致谢/利益冲突文本、最终 artifact
  package rebuild 仍是外部或后续 gate；
- 旧 `submission_handoff_20260618` 和 `submission_freeze_candidate_20260618`
  是历史 IEEE/EVP-7 边界，不应被当成 SQJ final freeze。

Plan:

1. 新增 SQJ final-freeze readiness 文档，只记录当前可提交前状态、缺口和安全重建命令；
2. 新增 no-API audit，验证该文档没有把 readiness 误写成 final submission freeze；
3. 将该 audit 接入 paper readiness / local quality gate，使后续代理能自动检查 SQJ
   冻结前边界；
4. 同步 README、INDEX、short-state、SQJ checklist、engineering notes；
5. 运行 py_compile、SQJ checklist audit、SQJ freeze-readiness audit、paper readiness、
   local quality gate；
6. 只提交本轮相关文件并尝试 GitHub sync。

Boundary:

- 本轮不调用模型 API，不读取 ignored raw responses；
- 本轮不下载 Springer 模板、不编译 PDF；
- 本轮不声明学校认可、Open Access/APC 批准、final freeze complete 或 submission
  authorized；
- 本轮不扩 bug、不扩模型、不改 EVP-8 结果 claim。

Execute Result:

- 已新增 `docs/artifact/sqj_final_freeze_readiness.md`；
- 已新增 `scripts/audit_sqj_final_freeze_readiness.py`；
- 已将 SQJ final-freeze readiness audit 接入：
  - `scripts/audit_paper_readiness.py`；
  - `scripts/run_local_quality_gate.py`；
  - `docs/artifact/sqj_submission_checklist.md` /
    `scripts/audit_sqj_submission_checklist.py`；
- 已同步 README、docs index、current project state、final roadmap 和 engineering
  notes；
- 该 readiness packet 明确记录：
  - 当前 source package ready；
  - 学校/学院认定、`sn-jnl.cls`/PDF compile、作者/基金/利益冲突、artifact rebuild
    和最终用户授权仍是 blocker；
  - `final_freeze_complete=false`；
  - 不授权投稿、不授权新模型 API。

Diagnose / Repair:

- 初次 readiness audit 失败，因为文档中的
  `This packet does not authorize submission.` 被 Markdown 自动换行拆开，导致
  required snippet 未命中；
- 已修复文档，将该边界句保持为单行；没有放宽审计条件。

Verify:

- `python -m py_compile scripts\audit_sqj_final_freeze_readiness.py scripts\audit_sqj_submission_checklist.py scripts\audit_paper_readiness.py scripts\run_local_quality_gate.py`
  通过；
- `python scripts\audit_sqj_submission_checklist.py --out-json outputs\sqj_submission_checklist_audit\sqj_freeze_readiness.json --out-md outputs\sqj_submission_checklist_audit\sqj_freeze_readiness.md`
  通过；
- `python scripts\audit_sqj_final_freeze_readiness.py --out-json outputs\sqj_final_freeze_readiness\sqj_freeze_readiness.json --out-md outputs\sqj_final_freeze_readiness\sqj_freeze_readiness.md`
  通过；
- `python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness_audit\sqj_freeze_readiness.json --out-md outputs\paper_readiness_audit\sqj_freeze_readiness.md`
  通过，`submission_package_ready=true`、`sqj_freeze_readiness_ready=true`、
  `sqj_final_freeze_complete=false`；
- `python scripts\write_sqj_latex_draft.py --check` 通过，仍为 source-structure
  gate，未编译 PDF；
- `python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\sqj_freeze_readiness.json --out-md outputs\local_quality_gate\sqj_freeze_readiness.md`
  通过，`passed=true`。

## 2026-06-26 EVP-8 accept-aware v0.2 DeepSeek/Qwen retest

Inspect:

- 用户指出 EVP-8 最终 `0 accept` 可能由实验设置造成，并要求新建分支修改后对
  DeepSeek 和 Qwen 重新测试；
- 当前 `main...origin/main` 干净，已新建分支
  `evp8-accept-aware-retest`；
- 检查发现 v0.1 prompt 允许 `accept`，但要求 visible evidence 直接支持 patch；
- v0.1 runner 在 full scope 中把 visible fail-to-pass / static / P2P / broader
  diagnostics 写成 `not_run_in_first_batch_full`、`not_materialized` 或
  `not_recorded`，且 E6 deterministic visible merge-gate summary 只有默认
  `escalate` 和失败时 `reject`，没有 `accept` 分支；
- 因此 v0.1 的 `0 accept` 不能解释为模型自然不会接受 patch，而应视作
  accept-evidence construction 缺失导致的保守门控现象。

Plan:

1. 保留 EVP-8 v0.1 结果不变，新增 accept-aware v0.2 输出路径和文档边界；
2. 在 EVP-8 DeepSeek/Qwen runner 中加入 v0.2 可见证据构造：
   - 从既有 model-visible EVP-7 visible-test / visible-tool-summary artifacts
     派生 E3-E6 可见测试与工具摘要；
   - E6 deterministic visible merge-gate summary 必须支持 `accept`、`reject`
     和 `escalate` 三种分支；
   - 不向模型暴露 expected outcome、candidate type、hidden oracle、reference
     provenance 或 evaluator labels；
3. 新增 v0.2 tracked config/example、check-only summary、DeepSeek/Qwen tracked
   result summaries和 two-model synthesis；
4. 先运行 no-API prompt-boundary / schema / check-only 验证，确认 v0.2 预期
   E6 deterministic summary 中存在 accept 分支且无泄露；
5. 在 no-API gate 通过后，按用户本轮明确要求仅重测：
   - `deepseek/deepseek-v4-pro`；
   - `qwen/qwen3.7-max`；
   预计 98 candidates x 7 levels x 2 models = 1372 model calls；
6. 重测后运行 raw-output-free result audit/synthesis，更新 README、docs index、
   current state 和 engineering notes；
7. 只暂存本轮相关文件，检查 diff / sensitive scan，提交并推送该分支。

Boundary:

- 本轮不修改 v0.1 tracked result summaries，不覆盖 v0.1 raw outputs；
- 本轮不跑 Kimi、Devstral、Gemini；
- 本轮不把 v0.2 结果写成最终五模型结论，只能报告 DeepSeek/Qwen two-model
  accept-aware retest；
- 任何 raw model response 仍只能写入 ignored `outputs/`；
- 如果 v0.2 no-API boundary 检查发现泄露、accept 分支来自 hidden/evaluator
  label，或 API preflight 不通过，必须暂停真实 API；
- 如果真实 API 产生 parse/cost/model metadata 缺口，必须先诊断，不得继续写正向
  论文结论。

Execute / Diagnose Update:

- 已完成 v0.2 accept-aware evidence construction 和 prompt v0.2 no-API gates：
  - prompt manifest / boundary audit 通过；
  - protocol audit 通过；
  - strict preflight 通过；
  - full check-only 通过，`schema_rule_decision_counts = accept:25,
    escalate:588, reject:73`，E6 deterministic branch 为
    `accept:25, reject:73`；
- 旧 prompt v0.1 路径下的一次 DeepSeek v0.2 尝试因 1 条 invalid risk flag
  被判定为 blocked attempt，未计入结果；
- prompt v0.2 路径下的 DeepSeek full rerun 已完成 686 calls，但
  `run_gate=blocked`：
  - `parse_valid_count=683`；
  - `invalid_parse_count=3`；
  - `usage_cost_gate=passed`；
  - `actual_model_id_counts.deepseek-v4-pro=686`；
  - 3 条 invalid 均为 `message.content` 为空、无 JSON object；
  - response metadata 显示 token 被写入 `reasoning_content`，其中 2 条
    `finish_reason=length`。

Repair Plan Before Any Further API:

1. 不启动 Qwen，直到 DeepSeek 通过 parse/cost/model gate；
2. 保留 blocked DeepSeek raw/summary 在 ignored 输出中，只作为诊断，不作为
   passed evidence；
3. 将 DeepSeek/Qwen runner 与 config 修为显式 JSON-mode request：
   - DeepSeek official route: `thinking: {"type":"disabled"}`；
   - DeepSeek/Qwen: `response_format: {"type":"json_object"}`；
   - 不读取或解析 `reasoning_content` 作为结果；
4. 新增干净输出路径，避免复用 blocked raw；
5. 先跑 DeepSeek smoke 验证 JSON-mode request 与 parse gate，再跑 DeepSeek
   full；只有 DeepSeek full audit 通过后，才启动 Qwen retest。

Repair / Verify Result:

- 已修复 `src/cross_review/openrouter.py`，为 OpenAI-compatible client 增加
  `thinking` 和 `response_format` request fields；
- 已修复 `scripts/run_evp8_deepseek_qwen_smoke.py`，从 model config 透传
  `reasoning`、`include_reasoning`、`thinking`、`response_format`，并在 summary
  中记录 request controls；
- 已修复 `scripts/preflight_evp8_deepseek_qwen.py`，校验 config 中的
  direct-provider request controls 与 protocol 一致；
- 已更新 `data/protocols/evp8_protocol_v0_2.json` 和
  `configs/evp8_deepseek_qwen_accept_v0_2.example.json`：
  - DeepSeek: `response_format={"type":"json_object"}` 且
    `thinking={"type":"disabled"}`；
  - Qwen: `response_format={"type":"json_object"}`；
- 已运行并通过：
  - `python -m py_compile src\cross_review\openrouter.py scripts\preflight_evp8_deepseek_qwen.py scripts\audit_evp8_protocol_spec.py scripts\run_evp8_deepseek_qwen_smoke.py`；
  - prompt manifest / boundary audit v0.2；
  - protocol audit v0.2；
  - strict preflight；
  - full check-only；
  - waiting-state result audit / synthesis；
  - DeepSeek json-mode smoke：35/35 parse-valid；
  - DeepSeek json-mode full：686/686 parse-valid，`run_gate=passed`，
    `usage_cost_gate=passed`；
  - Qwen json-mode smoke：35/35 parse-valid；
  - Qwen json-mode full：686/686 parse-valid，`run_gate=passed`，
    `usage_cost_gate=passed`；
  - final result audit：`audit_status=passed`；
  - final two-model synthesis：`synthesis_status=passed`。

Result Boundary:

- DeepSeek v0.2 json-mode full summary：
  - total decisions: `accept=80, escalate=287, reject=319`；
  - E6: `accept=23, reject=75`；
  - estimated cost: USD `0.4300004`；
- Qwen v0.2 json-mode full summary：
  - total decisions: `accept=82, escalate=238, reject=366`；
  - E6: `accept=24, reject=74`；
  - estimated cost: CNY `40.96758`；
- 结论：最终 `0 accept` 与 v0.1 实验设置有关。v0.1 缺少可见正向测试/工具
  evidence 和 E6 accept 分支；v0.2 在不暴露 hidden labels 的前提下补齐
  model-visible accept evidence 后，DeepSeek 和 Qwen 都产生非零 accept；
- 该结果仅支持 accept-aware DeepSeek/Qwen two-model retest 的描述性结论，
  不替代 EVP-8 v0.1 five-model synthesis，不支持 LLM superiority 或最终
  evidence-level effectiveness claim。

## 2026-06-26 EVP-8 v0.3 main-experiment Qwen-first run

Inspect:

- 用户要求在讨论“主实验一如何设置”后继续执行，并明确“先只做 qwen”；
- 当前工作从 `evp8-accept-aware-retest` 派生到新分支
  `evp8-v03-qwen-main-exp`，避免把 v0.2 诊断性 retest 继续混作主实验；
- v0.1 五模型结果有同一 frozen packet set 和五模型覆盖，但 visible positive
  evidence 构造不足，不能作为确认性主实验；
- v0.2 修复了 accept-aware visible evidence 并通过 DeepSeek/Qwen 诊断性重测，
  但它是在观察到 v0.1 `0 accept` 后形成，不能直接写成 confirmatory
  main experiment；
- 因此本轮目标是冻结一个 EVP-8 v0.3 Qwen-first 主实验入口，先只执行
  `qwen/qwen3.7-max`，后续模型必须另行授权。

Plan:

1. 新增 EVP-8 v0.3 protocol/prompt/config/run-packet，基于 v0.2 的
   accept-aware visible evidence，但明确标记为 confirmatory Qwen-first
   protocol；
2. v0.3 必须保持 visible/hidden separation：不暴露 expected outcome、
   candidate type、failure type、hidden oracle、reference provenance 或 final
   evaluator label；
3. v0.3 Qwen-first 使用当前 98-candidate / E0-E6 frozen structural cohort，
   只支持 bounded Qwen-first 主实验描述，不支持五模型最终结论或规模泛化；
4. 先运行 no-API gates：
   - protocol audit；
   - prompt manifest / boundary audit；
   - Qwen strict preflight；
   - smoke/full check-only；
   - waiting-state result audit/synthesis；
5. no-API gates 全部通过且 expected output path 不存在后，按用户本轮授权只调用
   Qwen：
   - smoke: 5 candidates x 7 levels = 35 calls；
   - smoke 通过 parse/cost/model gate 后再 full；
   - full: 98 candidates x 7 levels = 686 calls；
6. Qwen full 结束后运行 raw-output-free audit/synthesis，更新 README、docs
   index、current project state、engineering notes 和必要实验报告；
7. 只暂存本轮相关文件，运行 diff/sensitive checks，提交并推送
   `evp8-v03-qwen-main-exp`。

Boundary:

- 本轮不调用 DeepSeek、Kimi、Devstral、Gemini；
- 本轮不覆盖 v0.1 或 v0.2 raw outputs / tracked summaries；
- raw model responses 只能写入 ignored `outputs/`；
- 如果 no-API gate、strict preflight、smoke parse gate、usage/cost gate 或
  actual model/provider metadata gate 失败，必须先诊断修复，不能继续 full run
  或写正向结论；
- Qwen-first 结果只能作为 v0.3 主实验第一批结果，不能写成最终五模型主实验一；
- 后续是否继续其他模型需要用户再次明确授权。

Execute / Verify Result:

- 已新建分支 `evp8-v03-qwen-main-exp`；
- 已新增 EVP-8 v0.3 Qwen-first protocol/config/packet：
  - `data/protocols/evp8_protocol_v0_3_qwen_first.json`；
  - `configs/evp8_qwen_first_main_v0_3.example.json`；
  - ignored local config `configs/evp8_qwen_first_main_v0_3.local.json`；
  - `data/protocols/evp8_qwen_first_main_v0_3_prompt_v0_2_full_run_packet.json`；
- v0.3 复用冻结的 prompt v0.2 文本，没有修改 prompt 正文；
- no-API gates 已通过：
  - prompt manifest / prompt boundary audit passed；
  - protocol audit passed，`phase0_api_readiness=ready_for_api_preflight`；
  - Qwen-only strict preflight passed，仅验证 `QWEN_API_KEY` presence；
  - smoke check-only passed：35 packets，0 boundary/schema errors；
  - full check-only passed：686 packets，0 boundary/schema errors；
  - waiting-state result audit/synthesis passed before API execution；
- Qwen smoke 已执行：
  - 35/35 parse-valid；
  - `run_gate=passed`，`usage_cost_gate=passed`；
  - decision counts: `accept=16, escalate=15, reject=4`；
  - estimated cost: CNY `2.130804`；
- Qwen full 已执行：
  - 686/686 parse-valid；
  - `first_batch_full_gate=passed`，`usage_cost_gate=passed`；
  - actual model id counts: `qwen3.7-max=686`；
  - decision counts: `accept=86, escalate=230, reject=370`；
  - per-level decision counts:
    - E0: `escalate=74, reject=24`；
    - E1: `escalate=74, reject=24`；
    - E2: `escalate=73, reject=25`；
    - E3: `accept=20, escalate=4, reject=74`；
    - E4: `accept=21, escalate=2, reject=75`；
    - E5: `accept=21, escalate=3, reject=74`；
    - E6: `accept=24, reject=74`；
  - estimated cost: CNY `40.88994`；
- post-run raw-output-free result audit passed；
- Qwen-first synthesis passed，不读取 raw outputs。

Diagnose / Repair:

- Qwen smoke 和 full 的 shell command 均先触发工具超时，但底层 Python 进程仍在
  正常运行并继续写入 raw prefix；该问题属于长运行命令观察窗口问题，不是 API
  或实验设计失败；
- 处理方式：未启动并发 resume，先检查进程命令行与 raw 行数，等待原进程自然结束；
- full 运行期间 raw prefix 从 160/686 继续增长到 686/686，最终生成 summary；
- 一次 result audit 和 synthesis 并行运行时，synthesis 先读到旧的 waiting audit；
  已按依赖顺序重新运行 synthesis，最终 `synthesis_status=passed`。

Result Boundary:

- 本轮只完成 EVP-8 v0.3 Qwen-first 主实验第一批结果；
- 该结果可报告为 frozen 98-candidate / E0-E6 packet set 上的 Qwen 描述性
  decision pattern；
- 不能写成五模型主实验最终结果、DeepSeek/Qwen 对比结论、LLM superiority over
  deterministic baseline，或最终 evidence-level effectiveness claim；
- 后续继续 DeepSeek、Kimi、Devstral 或 Gemini 需要用户再次明确授权。

## 2026-06-27 EVP-8 v0.3 Qwen label-conditioned analysis

Inspect:

- 当前分支为 `evp8-v03-qwen-main-exp`，已同步到
  `origin/evp8-v03-qwen-main-exp`；
- Qwen-first v0.3 full synthesis 已通过，聚合决策显示 E0-E2 无 accept，
  E3-E6 accept 数逐步上升；
- 仅凭 per-level aggregate 不能推出“正确补丁被 accept 的概率上升”，必须把
  Qwen 决策与 evaluator-only 标签 join 后计算 label-conditioned metrics。

Plan:

1. 不调用任何模型 API，不改 protocol、prompt、candidate set 或已有 raw outputs；
2. 从 tracked candidate-set manifest 读取 anonymous EVP-8 candidate id 到
   source candidate id 的映射；
3. 从 evaluator-only candidate metadata 读取 hidden label，仅用于本地统计；
4. 从 ignored Qwen v0.3 full raw JSONL 解析最终 `accept/reject/escalate`
   decision，禁止使用 `reasoning_content`；
5. 生成 raw-output-free label-conditioned JSON/Markdown 汇总，报告：
   correct recall、accepted precision、false accept rate、false reject rate、
   escalation rate、correct-patch decision counts 和 paired transitions；
6. 同步 README、docs index、current project state 和 engineering notes，
   并提交推送本轮统计产物。

Boundary:

- 本轮统计只支持 Qwen v0.3 frozen 98-candidate / E0-E6 packet set 的
  label-conditioned 描述；
- 不写成五模型主实验结论、DeepSeek/Qwen 对比结论或最终 evidence-level
  effectiveness claim；
- 若 label join、raw-line count、decision parse 或 label coverage 不完整，
  必须停止并诊断，不输出正向论文结论。

Execute / Verify Result:

- 新增 `scripts/analyze_evp8_qwen_first_label_conditioned.py`；
- 已生成 raw-output-free 统计产物：
  - `data/reviews/evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.json`；
  - `docs/experiments/evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.md`；
- 统计输入覆盖 98 candidates x 7 evidence levels = 686 Qwen decisions；
- hidden label 分布：21 correct、77 non-correct；
- label-conditioned 结果：
  - E0/E1/E2：correct recall = 0，false accept rate = 0；
  - E3：correct accept = 17/21，false accept = 3/77，accepted precision =
    17/20；
  - E4/E5：correct accept = 18/21，false accept = 3/77，accepted precision =
    18/21；
  - E6：correct accept = 20/21，false accept = 4/77，accepted precision =
    20/24；
- 解释边界：可说 Qwen v0.3 在该 frozen batch 中随证据量增加显著提高
  correct-patch acceptance；但 E3-E6 同时产生 partial/regression false
  accepts，不能写成无代价的单调改进。

Diagnose / Repair:

- 首次脚本 check 失败，原因是 `api_call_attempted=false` 的检查项把
  `passed` 参数也写成 `false`；
- 问题类型：执行链路 bug，不是数据、标签或 Qwen 结果问题；
- 修复方式：将检查项改为 `api_call_not_attempted` 且
  `passed=true, detail=false`；
- 修复后同一 `--check` gate 通过。

## 2026-06-29 EVP-8 LLM-vs-tool headroom / E6 ablation plan

Inspect:

- 当前分支为 `evp8-v03-qwen-main-exp`，已同步到
  `origin/evp8-v03-qwen-main-exp`；
- Qwen v0.3 label-conditioned analysis 已显示 E6 correct recall 高但仍有
  partial/regression false accepts；
- 用户指出如果 LLM 与工具基线一致，可能来自实验设置、bug 强度不足或工具证据太强；
- 因此下一步不应直接重跑模型，而应先计划一个 no-API headroom audit 和
  E6 no-verdict ablation，区分“有效负结果”与“实验没有增益空间”。

Plan:

1. 新增 no-API 计划文档
   `docs/experiments/evp8_llm_tool_headroom_ablation_plan_20260629.md`；
2. 计划核心研究问题改为：
   LLM verifier 是否在 visible tool evidence 之后提供额外判断价值；
3. 第一阶段必须是 no-API headroom audit：
   - join deterministic tool-only decisions 与 evaluator-only labels；
   - 统计 tool false accepts、false rejects、unnecessary escalations；
   - 明确 opportunity set 大小；
4. 第二阶段才设计 `E6-no-verdict`：
   - 去掉 `rule_based_visible_merge_gate_decision`；
   - 去掉 `rule_based_visible_merge_gate_reasons`；
   - 去掉 `source_decision`；
   - 保留 visible tests、tool counts、contradictions、patch apply/status 等证据；
5. 只有 no-API packet/prompt/schema gates 通过，并且用户另行授权后，才允许
   Qwen-only smoke/full ablation；
6. 同步 README、docs index、current project state 和 engineering notes；
7. 本轮只写计划，不调用 API、不生成 raw outputs、不修改 prompt 或 candidate set。

Boundary:

- 当前计划不授权 `E6-no-verdict` API 执行；
- 如果 Phase 0 发现 tool baseline 已近乎无错，必须先报告当前 cohort 对
  LLM-added-value 问题缺乏 headroom，而不是继续烧 API；
- 如果 tool baseline 有错但 LLM 也不改正，应写成有效负结果，不得强行改实验直到
  结果变好；
- 若需要新增真实 agent patch cohort，必须另行制定候选生成、标签验证和成本计划。

## 2026-06-29 plan-document sync for headroom target

Inspect:

- 用户要求同步目前文档中的计划文档，检查是否和当前目标冲突；
- 当前分支仍为 `evp8-v03-qwen-main-exp`，本地提交
  `c194551 Plan EVP-8 LLM tool headroom ablation` 因 GitHub 网络失败尚未推送；
- 检查发现 `final_paper_roadmap_zh.md`、`evp8_journal_scale_execution_plan_20260620.md`
  和 `current_project_state_zh.md` 仍把 SQJ paper/artifact freeze 写成下一步；
- 这与当前“先做 no-API headroom audit / E6 ablation”的目标冲突。

Plan:

1. 不删除 SQJ 历史路线，只把它标记为暂停/备用；
2. 将当前 canonical next step 改为
   `docs/experiments/evp8_llm_tool_headroom_ablation_plan_20260629.md` 的
   Phase 0 no-API headroom audit；
3. 更新 README、INDEX、final roadmap、EVP-8 journal plan 和 current project
   state；
4. 本轮只同步计划文档，不调用 API、不生成 raw outputs、不修改 prompt 或
   candidate set。

Boundary:

- 不把 headroom audit 写成已完成实验；
- 不授权 `E6-no-verdict` API；
- 不把 SQJ route 删除，只防止它继续覆盖当前下一步。

## 2026-06-29 local env API-key readiness check

Inspect:

- 用户要求检查 `.env` 中的 API key 配置是否足够；
- 本轮只做凭证存在性和项目 preflight 检查，不调用任何模型 API；
- `.env` 存在，并包含非占位的 `DEEPSEEK_API_KEY`、`QWEN_API_KEY` 和
  `OPENROUTER_API_KEY`；
- `DEEPSEEK_BASE_URL` 已设置为 `https://api.deepseek.com`；
- `.env.example` 仍只是占位模板，不能代表真实执行凭证。

Verify:

1. `python scripts\preflight_evp8_deepseek_qwen.py --config
   configs\evp8_deepseek_qwen.local.json --out
   $env:TEMP\evp8_deepseek_qwen_preflight_env_check.json --strict-api-ready`
   passed；
2. `python scripts\preflight_evp8_deepseek_qwen.py --config
   configs\evp8_qwen_first_main_v0_3.local.json --out
   $env:TEMP\evp8_qwen_v03_preflight_env_check.json --strict-api-ready`
   passed；
3. `python scripts\preflight_evp8_later_models.py --config
   configs\evp8_later_models.local.json --out
   $env:TEMP\evp8_later_models_preflight_env_check.json --strict-api-ready`
   passed；
4. 三个 preflight 均报告 `api_call_attempted=false`、
   `api_key_values_printed=false`、`credential_presence_ready=true`。

Conclusion:

- 对现有已配置路径而言，DeepSeek/Qwen 首批、Qwen v0.3 和 OpenRouter
  later-model 的 key presence 已足够通过 strict preflight；
- 这只说明本地凭证和结构性 preflight 就绪，不授权任何真实 API 执行；
- 当前研究默认下一步仍是 no-API headroom audit；未来 `E6-no-verdict` 的真实
  Qwen API ablation 仍需要单独用户授权和对应 dry-run gate。

## 2026-06-29 execute Qwen/DeepSeek E6-no-verdict ablation

Inspect:

- 用户更新目标为：按计划执行新的实验，只需要做 Qwen 和 DeepSeek；
- 用户同时说明如果频繁 GitHub 同步失败，可忽略同步失败继续后续内容；
- 当前原始计划的立即下一步仍是 Phase 0 no-API headroom audit，不能跳过；
- 原计划文档只写了 future Qwen-only ablation，本轮用户授权将真实 API 范围扩展为
  Qwen + DeepSeek，但不包括 Kimi、Devstral、Gemini 或 OpenRouter later-model；
- 当前本地有 `177115a Record local API key readiness check` 尚未推送；这不阻塞
  实验执行。

Plan:

1. 实现并运行 Phase 0 no-API headroom audit；
2. 如果 tool-only baseline 存在足够 false accept / false reject / escalation
   opportunity set，则继续；
3. 新增专用 `E6-no-verdict` ablation runner/config，移除：
   - `rule_based_visible_merge_gate_decision`；
   - `rule_based_visible_merge_gate_reasons`；
   - `source_decision`；
4. 先跑 no-API check-only gate，确认 98 candidates x 1 E6-no-verdict packet、
   无 hidden labels、无 prompt/raw 存储；
5. 若 gate 通过，执行 Qwen 和 DeepSeek 两个模型的 full E6-no-verdict run；
6. 汇总 rule-only、E6-full、E6-no-verdict 的 label-conditioned metrics 和
   opportunity-set correction metrics；
7. 更新 README、INDEX、current project state、engineering notes 和实验报告；
8. 尝试提交/推送；如 GitHub 反复失败，记录失败但继续完成本地实验与分析。

Boundary:

- 本轮授权只覆盖 Qwen 和 DeepSeek 的 `E6-no-verdict` ablation；
- 不调用 later-model / OpenRouter；
- 不新增或变更 candidate set；
- 不修改旧 prompt 语义；若必须修改 prompt，先做 prompt-change audit；
- 不把 negative result 改写成 positive claim。

Verify / Result:

1. Phase 0 headroom audit:
   - command: `python scripts\analyze_evp8_tool_headroom.py --check`；
   - status: passed；
   - rule-only baseline: `accept=25, reject=73`；
   - tool errors: 5 false accepts、1 false reject，opportunity-set size = 6；
2. E6-no-verdict no-API gates:
   - smoke check-only passed: 5 packets；
   - full check-only passed: 98 packets；
   - removed fields verified:
     `rule_based_visible_merge_gate_decision`、
     `rule_based_visible_merge_gate_reasons`、`source_decision`；
   - prompt boundary errors = 0，schema errors = 0；
3. Qwen full:
   - command: `python scripts\run_evp8_e6_no_verdict_ablation.py --config
     configs\evp8_e6_no_verdict_ablation.local.json --execute --run-scope full
     --model-id qwen/qwen3.7-max`；
   - shell timeout occurred after 93/98 raw records, but the Python process
     continued and completed 98/98; no concurrent resume was launched；
   - summary:
     `data/reviews/evp8_e6_no_verdict_qwen_qwen3.7-max_full_summary.json`；
   - gate: passed，98/98 parse-valid；
   - decisions: `accept=23, reject=74, escalate=1`；
   - estimated cost: CNY `5.778804`；
4. DeepSeek full:
   - command: `python scripts\run_evp8_e6_no_verdict_ablation.py --config
     configs\evp8_e6_no_verdict_ablation.local.json --execute --run-scope full
     --model-id deepseek/deepseek-v4-pro`；
   - summary:
     `data/reviews/evp8_e6_no_verdict_deepseek_deepseek-v4-pro_full_summary.json`；
   - gate: passed，98/98 parse-valid；
   - decisions: `accept=11, reject=73, escalate=14`；
   - estimated cost: USD `0.079322105`；
5. Comparison:
   - command: `python scripts\analyze_evp8_e6_no_verdict_ablation.py --check`；
   - status: passed；
   - tracked outputs:
     `data/reviews/evp8_e6_no_verdict_ablation_comparison.json` and
     `docs/experiments/evp8_e6_no_verdict_ablation_comparison.md`。

Conclusion:

- Qwen: `E6-no-verdict` is very close to `E6-full`; false accepts remain
  4/77, correct recall drops from 20/21 to 19/21, and only one correct patch is
  escalated. This suggests Qwen is not merely copying the explicit verdict
  field, but it also does not fix the dangerous tool false accepts.
- DeepSeek: removing the verdict makes the model substantially more
  conservative. False accepts drop from 4/77 to 0/77, but correct recall drops
  from 19/21 to 11/21 and escalation rises to 14/98. This is useful as
  risk-control / triage evidence, not as automatic acceptance evidence.
- The practical claim should be narrowed: LLMs can alter risk posture after
  verdict removal, but this cohort does not show a clean LLM-added-value
  verifier that both preserves correct recall and fixes tool false accepts.

## 2026-06-29 hard-case extension plan for stronger paper

Inspect:

- 用户希望“冲更好一点”，需要基于当前结果补全后续计划；
- 当前主要短板不是模型数量，而是外部有效性和 opportunity-set 太小；
- 现有 98-candidate cohort 中 tool baseline 只有 6 个 opportunity cases，
  能支持受控诊断结论，但不足以支持更强 practical-value claim；
- Qwen `E6-no-verdict` 仍重复 4 个 false accepts；DeepSeek `E6-no-verdict`
  消除 false accepts 的方式是 escalation，不是直接正确 reject。

Plan:

1. 新增计划文档
   `docs/experiments/evp8_hard_case_extension_plan_20260629.md`；
2. 下一阶段不先跑 API，而是先完成 Phase A：
   - confidence intervals；
   - 6-case opportunity analysis；
   - utility/risk-policy table；
3. 之后构建 `EVP-8-HARD` 小型 hard-case extension：
   - 30-50 candidates；
   - visible-test-passing hidden failures；
   - partial / overfitted fixes；
   - regression patches；
   - plausible AI-agent wrong patches；
4. hard-case cohort 必须先通过 no-API candidate/label/packet/baseline gates；
5. 只有 hard-case tool baseline 有至少 10 个 opportunity cases 或至少 20%
   opportunity-set rate，并且用户再次授权，才运行 Qwen/DeepSeek；
6. 后续真实 API 只跑 Qwen/DeepSeek 的 `E6-full` 和 `E6-no-verdict`，
   不扩 Kimi/Devstral/Gemini，不重建完整 E0-E6 ladder。

Boundary:

- 本计划不授权 API；
- 不把新 hard-case 与旧 98-candidate cohort 混成一个同质样本；
- 不修改 prompt；
- 不声称 production merge safety；
- 若 hard-case opportunity-set 仍不足，停止 API 并报告 cohort headroom
  不足。

Verify / Result:

1. 新增脚本 `scripts/analyze_evp8_phase_a_paper_ready.py`；
2. 执行 `python scripts\analyze_evp8_phase_a_paper_ready.py --check`；
3. 输出：
   - `data/reviews/evp8_phase_a_paper_ready_analysis.json`；
   - `docs/experiments/evp8_phase_a_paper_ready_analysis.md`；
4. gate passed：
   - source comparison id 正确；
   - opportunity case count = 6；
   - confidence intervals present；
   - utility scenarios present；
   - `api_call_attempted=false`；
   - `raw_response_content_stored=false`；
   - `prompt_text_stored=false`。

Key findings:

- 当前 point estimates 必须配合不确定性解释。以 opportunity-set rate 为例，
  DeepSeek `E6-no-verdict` 对 5 个 tool false accepts 的 safe handling 为
  5/5，但 Wilson 95% CI 仍为 56.55%-100.00%；
- Qwen `E6-no-verdict` 对 false accepts 的 strict correction/safe handling
  均为 1/5，Wilson 95% CI 为 3.62%-62.45%，说明当前样本不足以支撑强
  LLM-added-value claim；
- utility/risk-policy table 显示 DeepSeek `E6-no-verdict` 在 safety-critical
  policy 下成本最低，但这是因为它用 escalation 避免 false accept，不是因为它
  自动识别正确补丁；
- Phase A 已完成。下一步应 no-API inspect 本地候选来源，准备
  `EVP-8-HARD` Phase B candidate source inventory。

## 2026-06-29 EVP-8-HARD Phase B source inventory

Inspect:

- Phase B 要求先确认本地是否已有足够 hard-case 来源，不能直接跑 API；
- 旧 98-candidate EVP-8 cohort 只能作为 controlled evidence，不能混入新的
  `EVP-8-HARD` 扩展当作新样本；
- 本地 `outputs/` 中同时存在 candidate validation、agent patch、pilot
  duplicate 和 raw response 路径，必须分开处理。

Plan:

1. 新增 no-API source inventory 脚本；
2. 只读取 tracked labels 和非 raw 的 local candidate/validation JSONL；
3. 输出 raw-output-free 聚合 JSON/Markdown；
4. 明确是否可以进入 hard-case manifest 和 baseline gate。

Execute / Verify:

1. 新增脚本 `scripts/inventory_evp8_hard_case_sources.py`；
2. 执行：
   - `python -m py_compile scripts\inventory_evp8_hard_case_sources.py`；
   - `python scripts\inventory_evp8_hard_case_sources.py --check`；
3. 输出：
   - `data/protocols/evp8_hard_case_source_inventory_v0_1.json`；
   - `docs/experiments/evp8_hard_case_source_inventory_v0_1.md`；
4. gate passed：
   - `api_call_attempted=false`；
   - `raw_model_outputs_read=false`；
   - `old_evp8_controlled_cohort_mutated=false`；
   - `candidate_manifest_created=false`；
   - `prompt_text_stored=false`；
   - old cohort count = 98。

Key findings:

- 旧 controlled cohort 的 rule-only E6 opportunity cases 仍为 6：5 个 false
  accepts 和 1 个 false reject；
- 本地共扫描 34 个非 raw candidate source files、260 条 candidate records；
- 非 promoted candidate records 为 68 条，去重后 49 条；
- 非 promoted eligible hard negatives 为 48 条，去重后 20 条；
- AI/agent candidate records 为 38 条，去重后 19 条；
- AI/agent eligible hard negatives 为 23 条，去重后 13 条；
- 这说明 Phase B 有可用来源，但还没有完成 hard-case cohort construction。

Next:

- 不调用 API；
- 从 inventory 中去重构建 `EVP-8-HARD` no-API candidate draft；
- 为该 draft 生成独立 tool-only baseline；
- 如果 hard-case tool-only opportunity cases 少于 10，则停止 API 并报告
  headroom 不足。

## 2026-06-29 EVP-8-HARD candidate draft and baseline gate

Inspect:

- Source inventory 已完成，但还没有独立 candidate draft；
- 非 promoted 来源里 relabeled agent 文件优先于 pending 文件；
- Luigi stability records 缺少 validation record，不能进入 API-facing draft；
- `httpie_ai_patch_stage_ab_001` 中有 6 条 patch apply failed，不能作为
  applied hard-case candidates；
- 当前来源只有 visible test hints，没有 model-visible visible test execution
  outcomes。

Plan:

1. 新增 `scripts/build_evp8_hard_candidate_draft.py`；
2. 输出 evaluator-only manifest、model-visible seed、tool-only baseline 和
   gate summary；
3. 检查 model-visible seed 不包含 hidden labels / hidden oracles / source
   patch id / validation status / raw response paths；
4. 如果 hard-negative 数量或 actionable baseline headroom 不足，明确 blocked。

Execute / Verify:

1. 执行：
   - `python -m py_compile scripts\build_evp8_hard_candidate_draft.py`；
   - `python scripts\build_evp8_hard_candidate_draft.py --check`；
2. 输出：
   - `data/patches/evp8_hard_evaluator_manifest_v0_1.jsonl`；
   - `data/evidence/evp8_hard_model_visible_seed_v0_1.jsonl`；
   - `data/baselines/evp8_hard_tool_only_baseline_v0_1.jsonl`；
   - `data/protocols/evp8_hard_candidate_draft_v0_1.json`；
   - `docs/experiments/evp8_hard_candidate_draft_v0_1.md`；
3. 额外检索 model-visible seed，确认无 `expected_outcome`、`hidden_oracles`、
   `oracle_passed`、`candidate_type`、`patch_id`、`raw_generation`、
   `validation_status`、`model_candidate_id`、`label_confidence` 字段。

Result:

- Draft 生成 35 条 applied candidates，覆盖 5 个 tasks、1 个 project；
- label 分布：
  - correct = 8；
  - agent_plausible_wrong = 10；
  - partial = 7；
  - irrelevant_or_noop = 10；
- nontrivial hard negatives = 17，未达到 20；
- AI/agent hard negatives = 10，达到最低目标；
- 第一版 tool-only baseline 因缺少 visible test outcomes，对 35 条全部 escalate；
- false accepts = 0，false rejects = 0，actionable false-accept/false-reject
  headroom = 0；
- API readiness = `blocked`。

Next:

- 不运行 Qwen/DeepSeek API；
- 至少补 3 条 validated non-control hard negatives；
- 生成真实 model-visible visible test outcomes；
- 重新生成 hard-case tool-only baseline；
- 只有 actionable false-accept/false-reject headroom >= 10 时，才考虑再次请求
  用户授权 API。

## 2026-06-29 EVP-8-HARD visible-test outcome run

Inspect:

- Candidate draft 的 model-visible seed 仍只有 visible test hints；
- 需要生成真实 visible test outcomes 后才能重建 baseline；
- 本地只有 agent workdirs 可用，构造型 httpie_stage_ab 和 direct AI patch
  workdirs 缺失或为空；
- 不能把 hidden oracle validation 当作 visible test outcome。

Plan:

1. 新增 `scripts/run_evp8_hard_visible_tests.py`；
2. 从 evaluator manifest 解析 source candidate file，只用于定位 workdir；
3. 输出 model-visible visible-test outcome records；
4. 禁止输出 hidden labels、hidden oracle outcomes、source patch id、prompt
   或 raw model response；
5. 将 visible outcomes 接入 `build_evp8_hard_candidate_draft.py`，重建 baseline。

Execute / Verify:

1. `python -m py_compile scripts\run_evp8_hard_visible_tests.py`；
2. `python scripts\run_evp8_hard_visible_tests.py --check`：
   - dry-run records = 35；
   - planned = 9；
   - blocked = 26；
3. `python scripts\run_evp8_hard_visible_tests.py --run --check --timeout 60`：
   - run records = 35；
   - error = 9；
   - blocked = 26；
4. `python scripts\build_evp8_hard_candidate_draft.py --check` 重建 baseline；
5. model-visible outcome 泄漏扫描无 forbidden marker 命中。

Result:

- visible-test 真实运行没有得到 passed/failed 业务结果；
- 9 条 error 主要是环境/collection error：
  - 缺少 `pytest_httpbin`；
  - 当前 `requests.compat` 缺少旧 HTTPie 测试期望的 `is_py26` /
    `is_windows`；
- 26 条因 missing candidate workdir blocked；
- 重建 baseline 后：
  - reject = 9；
  - escalate = 26；
  - false accepts = 0；
  - false rejects = 0；
  - actionable false-accept/false-reject headroom = 0；
- API readiness 仍为 `blocked`。

Next:

- 不运行 Qwen/DeepSeek API；
- 修复 hard-case visible-test execution environment 或重新构建可执行
  candidate workdirs；
- 至少补 3 条 validated non-control hard negatives；
- 只有重建 baseline 后 actionable false-accept/false-reject headroom >= 10，
  才能进入 API 授权讨论。

## 2026-06-29 EVP-8-HARD visible-test environment repair

本轮目标：

- 不调用模型 API；
- 不修改旧 98-candidate controlled cohort；
- 只修复 `EVP-8-HARD` 中 HTTPie 旧测试在当前 Python 3.11 环境下的可见测试执行链路；
- 修复后重新生成 visible outcomes 和 tool-only baseline gate。

执行结果：

- 新增 legacy pytest wrapper，随后泛化为
  `scripts/run_pytest_legacy_py311.py`，只处理旧测试运行所需的
  Python/runtime 兼容问题，不读取 evaluator labels、hidden oracles、raw model
  responses 或 prompt；
- `python scripts\run_evp8_hard_visible_tests.py --run --check --timeout 60`
  重新生成 35 条 visible-test records：
  - `completed=9`；
  - `blocked=26`；
  - test outcomes 为 `passed=4, failed=5, not_run_blocked=26`；
- `python scripts\build_evp8_hard_candidate_draft.py --check` 重新生成 baseline：
  - decision counts 为 `accept=4, reject=5, escalate=26`；
  - tool false accepts = 4；
  - tool false rejects = 0；
  - actionable false-accept/false-reject headroom = 4。

当前结论：

- 执行链路问题已修复到现有 workdir 范围内的 9 条可执行候选，visible-test
  证据从全 error/blocker 推进到 pass/fail；
- 这说明 hard-case draft 已经出现工具基线误接收错误补丁的现象，有研究价值；
- 但当前仍不满足 API 前置门：
  - nontrivial hard negatives = 17，低于 20；
  - actionable headroom = 4，低于 10；
- 因此下一步仍然不是跑 Qwen/DeepSeek，而是继续扩充或验证更难的非控制负例，
  并优先处理剩余 `httpie_4` visible-test error 或补充其他可执行 hard cases。

## 2026-06-29 EVP-8-HARD Luigi ingestion and gate update

本轮目标：

- 不调用模型 API；
- 不修改旧 98-candidate controlled cohort；
- 接入已有 Luigi validation outputs，并补一个 tracked Luigi4 extra partial；
- 重新生成 hard-case manifest、visible outcomes 和 tool-only baseline。

执行结果：

- `scripts/build_evp8_hard_candidate_draft.py` 现在读取
  `validation_run1.jsonl`，使 Luigi stability-audit candidates 进入 draft；
- `scripts/run_evp8_hard_visible_tests.py` 现在能定位：
  - Luigi `*_p2p_validation/candidate_000N` workdirs；
  - source-level `p2p_workdirs/candidate_000N`；
- legacy pytest wrapper 泛化为 `scripts/run_pytest_legacy_py311.py`；
- 新增 tracked `data/patches/evp8_hard_extra_luigi4_partial/`，记录一个
  not-promoted Luigi4 wrong-guard partial candidate 及其 oracle-failing
  validation summary；
- 未使用 `cookiecutter3_candidate_validation_001`，因为 inventory 标明它已进入
  旧 EVP-7/EVP-8 controlled cohort。

最新 no-API gate：

- candidates = 44；
- tasks = 7；
- projects = 2；
- nontrivial hard negatives = 20，已达到门槛；
- AI/agent hard negatives = 10；
- visible outcome records = 44；
- visible completed/error/timeout = 18；
- visible outcomes = `passed=9, failed=9, not_run_blocked=26`；
- deterministic baseline decisions = `accept=9, reject=9, escalate=26`；
- false accepts = 7；
- false rejects = 0；
- actionable false-accept/false-reject headroom = 7。

当前结论：

- hard-negative 数量门已通过；
- API readiness 仍为 `blocked`，唯一剩余 blocker 是
  `actionable_false_accept_or_reject_headroom_at_least_10`；
- 由于当前 headroom 只有 7/10，单纯追加少量候选不一定能解决问题；
- 下一步应做 cohort composition repair：替换低信息量 escalated/control
  candidates，引入更多 validated、visible-test-passing 但 hidden-incorrect
  的 hard cases，或能制造 tool false reject 的 correct cases；
- 在 headroom 达到 10 前，不运行 Qwen/DeepSeek。

## 2026-06-29 EVP-8-HARD headroom gate repair

本轮目标：

- 不调用模型 API；
- 不修改旧 98-candidate controlled cohort；
- 修复 visible-test workdir 选择中的候选 ID 碰撞问题；
- 在 no-API 范围内把 actionable false-accept/false-reject headroom 提到
  >= 10。

执行结果：

- `scripts/run_evp8_hard_visible_tests.py` 现在优先使用 validation 记录中
  `.candidate.patch` 所在 workdir，再回退到 source-level 或 task-level P2P
  workdir；
- 重建 ignored HTTPie workdirs 后，44 条旧候选全部获得 visible outcome；
- 发现并修复一个污染统计的问题：Luigi4 extra candidate 的
  `candidate_0001` 曾误命中通用 Luigi4 P2P workdir，修复后不再被错误计为
  false accept；
- 新增 tracked
  `data/patches/evp8_hard_extra_httpie1_errno_partials/`，包含 3 条
  HTTPie1 EINVAL fallback partial hard negatives；
- 这 3 条均满足：
  - patch applied；
  - hidden oracle ran；
  - hidden oracle failed；
  - visible `test_unique_filename` passed。

最新 no-API gate：

- candidates = 47；
- tasks = 7；
- projects = 2；
- nontrivial hard negatives = 23；
- AI/agent hard negatives = 10；
- visible outcome records = 47；
- visible completed/error/timeout = 47；
- visible outcomes = `passed=17, failed=28, timeout=2`；
- deterministic baseline decisions = `accept=17, reject=30`；
- false accepts = 9；
- false rejects = 2；
- actionable false-accept/false-reject headroom = 11；
- API readiness = `ready`。

当前结论：

- no-API 前置门已经通过；
- 现在可以进入 Qwen/DeepSeek API 实验授权讨论；
- 但在用户显式授权前，仍不得调用模型 API。

## 2026-06-29 EVP-8-HARD Qwen/DeepSeek check-only

本轮目标：

- 不调用模型 API；
- 不复用旧 98-candidate EVP-8 runner 直接跑 hard-case cohort；
- 构造 EVP-8-HARD 专用的 E6-only Qwen/DeepSeek check-only 入口；
- 验证 prompt boundary、schema-rule output、credential key presence 和输出路径
  guard。

执行结果：

- 新增 tracked `configs/evp8_hard_qwen_deepseek.example.json`；
- 新增 `scripts/run_evp8_hard_qwen_deepseek.py`；
- 已创建 ignored local config
  `configs/evp8_hard_qwen_deepseek.local.json`；
- `python scripts\run_evp8_hard_qwen_deepseek.py --check-only --config configs\evp8_hard_qwen_deepseek.local.json --summary-out data\protocols\evp8_hard_qwen_deepseek_check_only_v0_1.json`
  已通过；
- check-only 摘要：
  - candidate_count = 47；
  - packet_count_per_model = 47；
  - model_visible_levels = `E6`；
  - prompt boundary errors = 0；
  - schema errors = 0；
  - schema rule decision counts = `accept=17, reject=30`；
  - `.env` 中 `QWEN_API_KEY` 和 `DEEPSEEK_API_KEY` 均为 set；
  - api_call_attempted = false；
  - raw_outputs_generated = false；
  - prompt_text_stored = false；
- 负向 guard 已验证：用 tracked example config 执行
  `--execute --model-id qwen/qwen3.7-max` 会拒绝，并且没有生成
  `outputs/should_not_exist.json`。

当前结论：

- EVP-8-HARD 已完成 Qwen/DeepSeek API 授权前的本地 check-only；
- 下一步若继续实验，需要用户明确授权模型 API；
- 未获授权前不得执行 `--execute`。

## 2026-06-29 EVP-8-HARD parsed-review audit boundary

本轮目标：

- 不调用模型 API；
- 修复 hard-case runner，使真实执行后除 ignored raw responses 外，还写出
  tracked、raw-output-free 的 parsed review JSONL；
- 新增结果审计脚本，使后续 Qwen/DeepSeek 结果能直接和 evaluator-only
  labels、tool-only baseline 对齐；
- 在模型结果尚未生成时，审计脚本必须输出明确的
  `waiting_for_model_results`，不能误报为实验失败。

执行结果：

- `scripts/run_evp8_hard_qwen_deepseek.py` 现在支持
  `--parsed-reviews-out`，默认写入
  `data/reviews/evp8_hard_<model>_full_reviews.jsonl`；
- parsed review 只包含结构化字段，例如 decision、risk flags、confidence、
  primary reason、evidence used、visible contradictions、model/cost/usage metadata；
- parsed review 明确不保存 `raw_response_text`、provider response object 或
  rendered prompt；
- 新增 `scripts/audit_evp8_hard_qwen_deepseek_results.py`；
- 当前审计输出为
  `data/protocols/evp8_hard_qwen_deepseek_result_audit_v0_1.json`，
  状态为 `waiting_for_model_results`；
- 审计脚本在 waiting 状态下复现 tool-only baseline：
  `accept=17, reject=30`，false accepts = 9，false rejects = 2，
  accepted precision = 47.06%，correct recall = 80.00%，false accept rate =
  24.32%；
- 最小验证已通过：
  - `python -m py_compile scripts\run_evp8_hard_qwen_deepseek.py scripts\audit_evp8_hard_qwen_deepseek_results.py`
  - `python scripts\run_evp8_hard_qwen_deepseek.py --check-only --config configs\evp8_hard_qwen_deepseek.local.json --summary-out data\protocols\evp8_hard_qwen_deepseek_check_only_v0_1.json`
  - `python scripts\audit_evp8_hard_qwen_deepseek_results.py --out data\protocols\evp8_hard_qwen_deepseek_result_audit_v0_1.json`

当前结论：

- EVP-8-HARD 的 no-API 执行链路已经具备后续统计所需的 raw-output-free
  结果入口；
- 下一步如要产生 Qwen/DeepSeek 真实结果，仍必须由用户明确授权 API；
- 授权后建议先跑 Qwen，再 rerun 审计；DeepSeek 可作为第二个模型复现。

## 2026-06-29 EVP-8-HARD execution packet and coverage gate

本轮目标：

- 不调用模型 API；
- 为 EVP-8-HARD Qwen/DeepSeek 真实执行前新增一个 no-API execution packet；
- 固定 Qwen-first 执行顺序、post-Qwen audit、DeepSeek second run 和
  post-DeepSeek audit；
- 增强 result audit，防止部分 parsed review 被误判为完整模型结果。

执行结果：

- 新增 `scripts/write_evp8_hard_qwen_deepseek_execution_packet.py`；
- 新增 tracked JSON：
  `data/protocols/evp8_hard_qwen_deepseek_execution_packet_v0_1.json`；
- 新增 Markdown companion：
  `docs/experiments/evp8_hard_qwen_deepseek_execution_packet_v0_1.md`；
- execution packet 当前状态为 `ready`：
  - planned calls per model = 47；
  - model-visible level = `E6`；
  - Qwen-first execution order = true；
  - expected model outputs absent = true；
  - local config remains ignored and `api_execution_authorized=false`；
  - execution packet itself does not authorize API calls；
- `scripts/audit_evp8_hard_qwen_deepseek_results.py` 现在检查每个已执行模型是否
  恰好有 47 条 unique candidate decisions；缺失、重复或 extra candidate id
  会使 audit `blocked`；
- tracked example config 的负向 guard 已重新验证：使用 example config 执行
  `--execute --model-id qwen/qwen3.7-max` 会拒绝，且没有生成
  `outputs/should_not_exist.json` 或
  `outputs/should_not_exist_reviews.jsonl`。

最小验证：

- `python -m py_compile scripts\run_evp8_hard_qwen_deepseek.py scripts\audit_evp8_hard_qwen_deepseek_results.py scripts\write_evp8_hard_qwen_deepseek_execution_packet.py`
- `python scripts\run_evp8_hard_qwen_deepseek.py --check-only --config configs\evp8_hard_qwen_deepseek.local.json --summary-out data\protocols\evp8_hard_qwen_deepseek_check_only_v0_1.json`
- `python scripts\audit_evp8_hard_qwen_deepseek_results.py --out data\protocols\evp8_hard_qwen_deepseek_result_audit_v0_1.json`
- `python scripts\write_evp8_hard_qwen_deepseek_execution_packet.py --check`

当前结论：

- EVP-8-HARD 的 API 前置链路已经完整到可以安全接收显式授权；
- 真实实验结果仍未产生；
- 下一步必须由用户明确授权，例如“授权运行 EVP-8-HARD Qwen API”，才能执行
  Qwen 的 47-call hard-case run。
