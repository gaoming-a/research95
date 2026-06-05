# AI Agent 执行总计划：AI 生成补丁的可验证审查

最后更新：2026-06-05

本文档是可以直接交给 AI agent 执行的主计划。执行入口以本文件为准，文档索引用 `docs/INDEX.md`，代码根目录记为 `<repo_root>`。

## 0. 当前状态

已完成：

- 建立干净研究目录 `research95`，只保留新方向可复用资产。
- 明确新主线：验证 AI coding agent 生成的 patch 是否应该被接受。
- 实现 `scripts/build_patch_verification_dataset.py`。
- 实现 `scripts/analyze_patch_verification.py`。
- 完成当前 no-API pilot：
  - 7 个 retained real-bug tasks；
  - 30 个 patch candidates；
  - 90 条 deterministic baseline verifier outputs；
  - 3 个 no-API baselines：`accept_all`、`reject_all`、`oracle_upper_bound`。
- 模型可见 evidence packet 已使用匿名 `candidate_id`，并通过标签泄露检查。
- patch text 已从外部 retained buggy/fixed checkouts 生成真实 unified diff。
- 当前有 9 个 `partial_fix`，困难负例比例为 30%。
- `scripts/validate_patch_candidates.py` 已验证 30/30 candidates 均可 apply，并且 oracle 标签一致。

当前不能做：

- 不能马上调用 API 作为正式实验。
- 不能把当前 no-API pilot 当作论文结果。
- 不能扩大到多模型、多条件 API 实验；下一步只能先准备并运行最小 API pilot。

## 1. 研究目标

核心问题：

> 对 AI-generated patches，evidence-first verification 是否比 LLM-only review 更能减少错误 patch 被接受，同时不过度拒绝正确 patch？

目标贡献：

- 一个 patch-verification 数据构建流程。
- 一套模型可见输入与评估标签严格分离的 schema。
- 一个从真实 bug 出发的 candidate patch 数据集。
- 一个比较 `llm_only` 与 `evidence_first` 的小规模 API pilot。
- 一套 false accept / false reject / accepted precision / recall / escalation 指标。
- 一篇以 patch acceptance risk 为主线的论文草稿。

## 2. 禁止事项

执行过程中禁止：

- 把 `expected_outcome`、`candidate_type`、`patch_id`、hidden oracle 路径或 oracle 结果暴露给模型。
- 在 realistic patch diff gate 通过前运行 API reviewer。
- 把另一个 LLM opinion 当作 ground truth。
- 为了得到更好结果删除失败样本，除非样本被明确标记为 `environment_invalid` 并记录原因。
- 把旧方向的 cross-review / majority voting 写成主贡献。
- 复制或提交 `.env`、API key、local model configs、raw `data/`、`outputs/`、`tmp/`、benchmark checkouts。

## 3. 权威文档

执行时必须遵循：

- `README.md`：项目当前状态和下一步。
- `docs/INDEX.md`：文档与脚本索引。
- `docs/paper/research_definition.md`：研究问题、假设和 non-goals。
- `docs/experiments/patch_candidate_schema.md`：candidate、evidence packet、verifier output schema。
- `docs/experiments/evidence_first_protocol.md`：实验条件和 evidence-first workflow。
- `docs/experiments/patch_verification_metrics.md`：指标定义。
- `docs/experiments/pilot_dataset_construction.md`：pilot 数据构建规则。
- `docs/experience/engineering_notes.md`：工程经验和已知坑。
- `docs/prompts/prompt_change_log.md`：prompt 变更记录。

如果代码和文档冲突，先判断哪边错；修改后必须同步更新索引和相关计划。

## 3.1 AI agent 执行协议

任何 AI agent 接手后必须按以下顺序推进，不能跳阶段：

1. 先读 `README.md`、`docs/INDEX.md`、本文件和
   `docs/experience/engineering_notes.md`。
2. 运行 readiness audit：

   ```powershell
   python scripts\audit_execution_readiness.py `
     --out-json outputs\readiness_audit\latest.json `
     --out-md outputs\readiness_audit\latest.md
   ```

3. 运行阶段进度审计：

   ```powershell
   python scripts\audit_ai_plan_progress.py `
     --out-json outputs\plan_progress\latest.json `
     --out-md outputs\plan_progress\latest.md
   ```

4. 运行人工输入包生成：

   ```powershell
   python scripts\write_human_input_packet.py `
     --out-json outputs\handoff\human_input_packet.json `
     --out-md outputs\handoff\human_input_packet.md
   ```

5. 运行一键 pre-API handoff：

   ```powershell
   python scripts\write_pre_api_handoff.py `
     --out-json outputs\handoff\pre_api_handoff.json `
     --out-md outputs\handoff\pre_api_handoff.md
   ```

6. 运行 Git 同步决策包：

   ```powershell
   python scripts\write_git_sync_packet.py `
     --out-json outputs\handoff\git_sync_packet.json `
     --out-md outputs\handoff\git_sync_packet.md
   ```

7. 先执行 no-API 复现和 validation，不允许直接调用 API。
8. 每个阶段结束后检查产物是否存在、数量是否匹配、验收标准是否通过。
9. 若验收失败，只能回到本阶段修复，不允许通过删除失败样本继续推进。
10. dry-run 只证明 prompt 渲染和标签边界；mock run 只证明本地输出链路。
11. 只有真实 `reviews.jsonl` 与 `metrics.json` 产生后，才允许写模型实验结论。
12. 每次代码、实验计划或 prompt 变更后，同步更新 README、索引、计划和经验文档。

推荐总执行顺序：

```text
环境检查
-> no-API dataset build
-> metrics analysis
-> executable validation
-> label leakage check
-> prompt dry-run
-> API preflight
-> 2-candidate smoke API run
-> smoke report
-> 30-candidate API run
-> result report
-> failure analysis
-> paper draft update
```

## 4. 阶段 A：复现当前 no-API pilot

目的：确认环境、脚本和数据边界可用。

推荐一键执行命令：

```powershell
python scripts\run_no_api_patch_pipeline.py `
  --out-dir outputs\patch_verification_pilot_repro_001
```

该命令会依次执行：

1. `build_patch_verification_dataset.py`
2. `analyze_patch_verification.py`
3. `validate_patch_candidates.py`
4. `preflight_api_pilot.py --allow-missing-credentials`
5. `run_patch_verification_api_pilot.py --dry-run`
6. `summarize_patch_verification_pilot.py`

它不会调用 OpenRouter，也不要求 `.env` 存在。最新本地验证输出为
`outputs/patch_verification_pilot_repro_001`，结果为 30 candidates、90
baseline verifier outputs、30/30 validations、60 prompt dry-run records。

随后生成 deterministic output manifest，并与原始 no-API pilot 对比：

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

当前对比结果：`outputs/reproducibility/pilot_compare.json` 中
`matched = true`，7 个 deterministic files 全部匹配。该检查不覆盖 raw API
responses、临时 workdirs、外部 checkout 或环境相关文件。

如果一键命令失败，再使用下面的分步命令定位问题。

执行命令：

```powershell
python scripts\build_patch_verification_dataset.py --help
python scripts\build_patch_verification_dataset.py --out-dir outputs\patch_verification_pilot_001
python scripts\analyze_patch_verification.py --help
python scripts\analyze_patch_verification.py `
  --candidates outputs\patch_verification_pilot_001\candidates.jsonl `
  --verifier-outputs outputs\patch_verification_pilot_001\verifier_outputs.jsonl `
  --out outputs\patch_verification_pilot_001\metrics.json
python scripts\validate_patch_candidates.py `
  --candidates outputs\patch_verification_pilot_001\candidates.jsonl `
  --out outputs\patch_verification_pilot_001\validation.jsonl `
  --summary-out outputs\patch_verification_pilot_001\validation_summary.json
```

期望输出：

- `outputs/patch_verification_pilot_001/candidates.jsonl`
- `outputs/patch_verification_pilot_001/evidence_packets.jsonl`
- `outputs/patch_verification_pilot_001/verifier_outputs.jsonl`
- `outputs/patch_verification_pilot_001/dataset_summary.json`
- `outputs/patch_verification_pilot_001/metrics.json`
- `outputs/patch_verification_pilot_001/validation.jsonl`
- `outputs/patch_verification_pilot_001/validation_summary.json`

验收标准：

- `candidate_count = 30`。
- `verifier_output_count = 90`。
- 包含 correct 与 negative candidates。
- `accept_all` 的 false accept rate 应为 1.0。
- `reject_all` 的 correct patch recall 应为 0.0。
- `oracle_upper_bound` 的 accepted precision 应为 1.0。
- `dataset_summary.json` 中 `api_readiness.ready` 应为 true。
- `validation_summary.json` 中 `all_validated` 应为 true。

## 5. 阶段 B：标签泄露检查

目的：确认模型可见 evidence packet 没有泄露评估标签。

执行检查：

```powershell
@'
import json
from pathlib import Path
path = Path("outputs/patch_verification_pilot_001/evidence_packets.jsonl")
forbidden_keys = {
    "patch_id", "expected_outcome", "candidate_type", "hidden_oracles",
    "oracle_command", "oracle_workdir", "construction_notes", "label_confidence"
}
forbidden_tokens = [
    "correct_reference", "buggy_noop", "irrelevant_patch", "reference_fix",
    "irrelevant_or_noop", "No-op", "no-op", "noop", "Irrelevant",
    "irrelevant nearby", "expected_outcome", "hidden_oracles"
]
violations = []
for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
    record = json.loads(line)
    key_hits = sorted(forbidden_keys.intersection(record.keys()))
    if key_hits:
        violations.append((line_no, "forbidden_keys", key_hits))
    blob = json.dumps(record, ensure_ascii=False)
    token_hits = [token for token in forbidden_tokens if token in blob]
    if token_hits:
        violations.append((line_no, "forbidden_tokens", token_hits))
if violations:
    raise SystemExit(json.dumps({"status": "failed", "violations": violations[:20]}, ensure_ascii=False))
print(json.dumps({"status": "passed", "checked_records": line_no}, ensure_ascii=False))
'@ | python -
```

验收标准：

- 输出 `status = passed`。
- 若失败，先修 schema 或构建脚本，不允许继续 API pilot。

## 6. 阶段 C：补齐真实困难负例

目的：在已经具备真实 unified diff 的基础上，补齐足够多的 realistic difficult negatives。这是进入 API 实验前的硬门槛。

已完成：

1. `correct_reference` 由 retained buggy/fixed checkout 生成 unified diff。
2. `irrelevant_patch` 使用同项目其他真实任务的 reference diff 作为跨任务真实负例。
3. `buggy_noop` 使用空 diff control。
4. `httpie_1` 已生成 1 个 `partial_fix`，来自多 hunk reference diff 的首个 hunk。
5. `patch_id` 仍只在 evaluator-facing candidate record 中出现；evidence packet 只用匿名 `candidate_id`。

已完成：

1. 增加到 9 个 `partial_fix` candidates。
2. 所有 30 个 candidates 已通过 apply + oracle validation。
3. 不再使用不可应用的跨任务 diff 作为 unrelated control；改为可应用的 comment-only source diff control。

负例优先级：

1. `test_passing_wrong`：能通过可见测试，但失败于 hidden oracle。
2. `partial`：修复一部分行为，但遗漏另一个 oracle-checkable 行为。
3. `overfitted`：明显针对可见测试或局部条件，不能泛化。
4. `buggy_noop` 与 `irrelevant_or_noop`：只作为低难度控制组，不应成为主结果。

建议新增或修改：

- `scripts/build_patch_verification_dataset.py`
- 必要时新增 `scripts/generate_difficult_patch_candidates.py`
- 必要时新增 `docs/experiments/patch_diff_sources.md`

验收标准：

- 至少 20 个 candidates 仍可生成。
- 至少 30% 是 realistic difficult negatives，即 `partial`、`overfitted` 或 `test_passing_wrong`。
- 每个 candidate 有可追溯的构造依据。
- 重新通过阶段 A 和阶段 B。
- `dataset_summary.json` 中 `api_readiness.ready = true`。
- `validation_summary.json` 中 `all_validated = true`。

## 7. 阶段 D：小规模 API pilot

阶段 C 已通过。下一步先准备 prompt 和 run metadata，再执行最小 API pilot。

第一轮只跑两个条件：

- `llm_only`
- `evidence_first`

暂时不跑 majority 和 agent-context，除非前两者稳定且结果有解释价值。

每次 API run 必须记录：

- model slug；
- provider；
- date；
- temperature；
- max tokens；
- prompt version；
- candidate ids；
- raw response path；
- cost；
- invalid outputs；
- retry policy。

执行前必须新增或更新：

- `docs/prompts/prompt_change_log.md`
- API run config 或命令文档
- 输出 JSONL schema 说明

已完成：

- `docs/prompts/api_pilot_prompts.md`
- `docs/prompts/prompt_change_log.md`
- `scripts/run_patch_verification_api_pilot.py`
- `configs/api_pilot.example.json`
- `scripts/preflight_api_pilot.py`
- `scripts/summarize_patch_verification_pilot.py`
- API dry-run 已完成：30 candidates x 2 conditions，共 60 个渲染 prompts，
  label-leakage check 全部通过。
- 当前 ignored 报告输出：`outputs/patch_verification_pilot_001/pilot_report.md`。
- 当前 tracked 报告摘要：`docs/experiments/patch_verification_pilot_report.md`。
- 当前 pre-API 论文草稿：`docs/paper/patch_verification_draft.md`。

Smoke run 命令格式：

```powershell
python scripts\create_model_selection_local.py `
  --model <concrete-openrouter-model-slug> `
  --provider <provider> `
  --selection-source <source-name> `
  --selection-source-url <source-url> `
  --capability-source <ranking-or-catalog-name> `
  --capability-band <single-model-pilot-or-near-peer-band> `
  --reason <selection-rationale>
python scripts\validate_model_selection.py `
  --selection configs\model_selection.local.json
python scripts\create_api_pilot_local_config.py `
  --model <concrete-openrouter-model-slug> `
  --out configs\api_pilot.local.json `
  --smoke-limit 2
python scripts\validate_model_selection.py `
  --selection configs\model_selection.local.json `
  --api-config configs\api_pilot.local.json `
  --out outputs\model_selection\latest.json
python scripts\preflight_api_pilot.py --config configs\api_pilot.local.json
python scripts\run_api_pilot_workflow.py `
  --config configs\api_pilot.local.json `
  --execute
```

如果 model slug、provider、来源、能力分档和选择理由已经由用户明确确认，
可以先用 `scripts\bootstrap_api_prereqs.py --dry-run --allow-missing-credentials`
预览将写入的
`configs\model_selection.local.json` 和 `configs\api_pilot.local.json`。
确认无误后去掉 `--dry-run`，该脚本会写入两份 ignored local config、
验证 model 一致性并运行 preflight。正式写入模式要求 `.env` 已包含
`OPENROUTER_API_KEY`，否则不会写入 local config；它不会创建 `.env` 或替
用户选择模型。

`run_api_pilot_workflow.py` 会先执行严格 preflight；只有传入 `--execute`
且 preflight 通过时才会调用模型 API。检查但不调用 API 时使用：

```powershell
python scripts\run_api_pilot_workflow.py `
  --config configs\api_pilot.local.json `
  --check-only `
  --summary-out outputs\api_workflow_check\latest.json
```

`configs/api_pilot.local.json` 不应提交。它应由
`configs/api_pilot.example.json` 复制得到，或用
`scripts/create_api_pilot_local_config.py` 生成，并填入真实 OpenRouter model slug。
`configs/model_selection.local.json` 也不应提交；它应由
`configs/model_selection.example.json` 复制得到，记录模型选择来源、日期、能力分档、
OpenRouter slug 和选择限制。
默认 `smoke_limit = 2`，smoke run 通过后推荐不修改 local config，而是用
workflow 覆盖输出目录和 candidate limit：

```powershell
python scripts\run_api_pilot_workflow.py `
  --config configs\api_pilot.local.json `
  --run-dir outputs\patch_verification_api_pilot_002 `
  --limit 0 `
  --execute
```

不调用 API 的 dry-run 命令：

```powershell
python scripts\run_patch_verification_api_pilot.py `
  --config configs\api_pilot.example.json `
  --out-dir outputs\patch_verification_api_pilot_dry_run_001 `
  --dry-run
```

当前 dry-run 结果：

- prompt records: 60；
- `llm_only`: 30；
- `evidence_first`: 30；
- label-leakage check: 60/60 passed；
- prompt length range: 1074 到 2794 chars。

Mock smoke 命令：

```powershell
python scripts\run_patch_verification_api_pilot.py `
  --config configs\api_pilot.example.json `
  --out-dir outputs\patch_verification_api_pilot_mock_smoke_001 `
  --limit 2 `
  --mock-policy patch_surface
```

Mock smoke 当前结果：

- reviewer records: 4；
- 自动生成 `reviews.jsonl`、`metrics.json`、`run_summary.md`；
- `mock records: 4`；
- 该输出只验证本地链路，不是模型实验结果。

Mock smoke 结果报告命令：

```powershell
python scripts\summarize_api_pilot_results.py `
  --reviews outputs\patch_verification_api_pilot_mock_smoke_001\reviews.jsonl `
  --metrics outputs\patch_verification_api_pilot_mock_smoke_001\metrics.json `
  --run-summary outputs\patch_verification_api_pilot_mock_smoke_001\run_summary.md `
  --out outputs\patch_verification_api_pilot_mock_smoke_001\api_pilot_report.md
```

该报告只能用于确认 `reviews.jsonl -> metrics.json -> report` 链路可用，
不能作为模型实验结果。

当前 pilot 报告生成命令：

```powershell
python scripts\summarize_patch_verification_pilot.py `
  --dataset-summary outputs\patch_verification_pilot_001\dataset_summary.json `
  --validation-summary outputs\patch_verification_pilot_001\validation_summary.json `
  --metrics outputs\patch_verification_pilot_001\metrics.json `
  --prompt-manifest outputs\patch_verification_api_pilot_dry_run_004\prompt_manifest.jsonl `
  --out outputs\patch_verification_pilot_001\pilot_report.md
python scripts\summarize_patch_verification_pilot.py `
  --dataset-summary outputs\patch_verification_pilot_001\dataset_summary.json `
  --validation-summary outputs\patch_verification_pilot_001\validation_summary.json `
  --metrics outputs\patch_verification_pilot_001\metrics.json `
  --prompt-manifest outputs\patch_verification_api_pilot_dry_run_004\prompt_manifest.jsonl `
  --out docs\experiments\patch_verification_pilot_report.md
```

报告只总结 no-API baselines、candidate validation 和 prompt dry-run；不能作为模型实验结果。

论文草稿边界：

- `docs/paper/patch_verification_draft.md` 可以作为方法与当前验证结果草稿；
- 其中 API 结果必须在真实 `reviews.jsonl` 和 `metrics.json` 产生后再填写；
- 不允许把 dry-run 或 mock smoke 写成模型实验结果。
- `scripts/write_paper_tables.py` 可重新生成
  `docs/paper/generated_tables.md` 和 `docs/paper/generated_tables.tex`；
  当前表格只包含 pre-API/no-API 数据，不包含模型结果。
- `scripts/write_ieee_latex_draft.py` 可重新生成
  `docs/paper/ieee_preapi_draft.tex`；当前 LaTeX 草稿保留真实 API 结果占位，
  不能作为最终投稿版。

输出目录：

```text
outputs/patch_verification_api_pilot_001/
```

应包含：

- `reviews.jsonl`
- `metrics.json`
- `run_summary.md`
- raw responses 或 raw response 索引
- `api_pilot_report.md`

真实 API smoke run 后立即生成报告：

```powershell
python scripts\summarize_api_pilot_results.py `
  --reviews outputs\patch_verification_api_pilot_001\reviews.jsonl `
  --metrics outputs\patch_verification_api_pilot_001\metrics.json `
  --run-summary outputs\patch_verification_api_pilot_001\run_summary.md `
  --out outputs\patch_verification_api_pilot_001\api_pilot_report.md
```

Smoke run 验收标准：

- `reviews.jsonl` 中 reviewer records 数量等于 `candidate_count * condition_count`。
- `metrics.json` 的 `verifier_output_count` 与 `reviews.jsonl` 行数一致。
- `run_summary.md` 中 `mock records = 0`。
- `api_pilot_report.md` 中 report kind 为 `real API pilot`。
- `invalid_output_rate` 不应高到使结果不可解释；若明显偏高，先修 prompt 或 parser。
- 至少人工抽查 2 条 raw response，确认 JSON parsing 没有系统性误读。

成功门槛：

- `evidence_first` 的 false accept rate 低于 `llm_only`。
- accepted precision 提升。
- correct patch recall 不应崩溃。
- 提升不能只靠全部 reject 或全部 escalate。
- 至少有 3 个清晰 failure examples 可以写入论文分析。

失败处理：

- 如果 `evidence_first` 只是在拒绝一切，停止扩展。
- 如果 LLM-only 与 evidence-first 差异很小，回到 evidence design，而不是扩大模型数量。
- 如果负例太弱，回到阶段 C，而不是继续 API 消耗。

Full run 执行条件：

- smoke run 已通过；
- 不修改 candidate set；
- 不修改 prompt，除非重新跑 dry-run、preflight 和 smoke；
- local config 中 `smoke_limit` 已设为 0，或命令显式覆盖全量运行；
- 输出目录使用新的递增编号，避免覆盖 smoke run。

Full run 后必须执行：

优先运行一键后处理：

```powershell
python scripts\postprocess_api_pilot_run.py `
  --run-dir <full_run_dir> `
  --expected-candidates 30
```

该命令会生成：

- `<full_run_dir>/api_pilot_report.md`
- `<full_run_dir>/failure_examples.json`
- `<full_run_dir>/failure_examples.md`
- `<full_run_dir>/gate_report.json`
- `<full_run_dir>/gate_report.md`
- `<full_run_dir>/run_completeness.json`
- `<full_run_dir>/run_completeness.md`
- `<full_run_dir>/paper_readiness.json`
- `<full_run_dir>/paper_readiness.md`
- `<full_run_dir>/postprocess_summary.json`

如果需要分步排错，再使用以下命令。

```powershell
python scripts\summarize_api_pilot_results.py `
  --reviews <full_run_dir>\reviews.jsonl `
  --metrics <full_run_dir>\metrics.json `
  --run-summary <full_run_dir>\run_summary.md `
  --out <full_run_dir>\api_pilot_report.md
```

随后抽取 failure-analysis 样本：

```powershell
python scripts\extract_api_failure_examples.py `
  --candidates outputs\patch_verification_pilot_001\candidates.jsonl `
  --evidence-packets outputs\patch_verification_pilot_001\evidence_packets.jsonl `
  --reviews <full_run_dir>\reviews.jsonl `
  --out-json <full_run_dir>\failure_examples.json `
  --out-md <full_run_dir>\failure_examples.md
```

最后执行 stop/continue gate：

```powershell
python scripts\evaluate_api_pilot_gate.py `
  --metrics <full_run_dir>\metrics.json `
  --reviews <full_run_dir>\reviews.jsonl `
  --out-json <full_run_dir>\gate_report.json `
  --out-md <full_run_dir>\gate_report.md
```

Full run 后必须回答四个问题：

1. `evidence_first` 是否降低 false accept rate？
2. accepted precision 是否提升？
3. correct-patch recall 是否明显下降？
4. 改善是否只是来自 reject/escalate 几乎所有样本？

如果第 1 或第 2 不成立，不能继续包装成正向结论；只能写负结果或回到数据/方法设计。

Gate 判定规则：

- `continue`：可以进入论文结果分析，但仍需结合 failure examples 人工检查。
- `stop_or_redesign`：不能写成正向结论，应回到数据、evidence design 或 prompt。
- `indeterminate`：指标不足以判断，不能扩大实验。
- `not_evidence`：输入包含 mock outputs，只能说明本地链路可运行。

## 7.1 阶段 D 之后的 failure analysis

真实 API full run 后，必须从 `reviews.jsonl` 和 `metrics.json` 中抽取：

- 至少 3 个 LLM-only false accepts；
- 至少 3 个 evidence-first escalations 或 rejects；
- 如果存在，至少 3 个 correct patch 被拒绝或升级的样本；
- 每个样本记录 task、candidate type、decision、visible evidence、模型理由和 oracle label。

自动抽取命令：

```powershell
python scripts\extract_api_failure_examples.py `
  --candidates outputs\patch_verification_pilot_001\candidates.jsonl `
  --evidence-packets outputs\patch_verification_pilot_001\evidence_packets.jsonl `
  --reviews <full_run_dir>\reviews.jsonl `
  --out-json <full_run_dir>\failure_examples.json `
  --out-md <full_run_dir>\failure_examples.md
```

验收标准：

- `failure_examples.json` 中 `review_count` 与 `reviews.jsonl` 行数一致。
- `mock_review_count = 0`，除非只是本地 smoke test。
- `bucket_counts` 至少覆盖真实 run 中存在的 false accepts 或 evidence-first reject/escalate。
- `failure_examples.md` 只能作为人工分析起点；写入论文前必须再检查 raw response 和 oracle label。

分析目的不是挑好看的例子，而是判断方法是否真的有价值：

- 如果 evidence-first 能识别 partial/irrelevant/noop patch，记录具体证据链。
- 如果 evidence-first 错拒正确 patch，判断是 prompt 过严、context 不足，还是 patch 本身不可验证。
- 如果 LLM-only 和 evidence-first 结论接近，说明当前 evidence 设计可能没有提供新增信息。

## 8. 阶段 E：论文初稿

只有 no-API pilot、realistic diff gate 和小 API pilot 都完成后，才开始写完整初稿。

写完整结果初稿前，必须先运行 paper readiness audit：

```powershell
python scripts\audit_paper_readiness.py `
  --full-run-dir <full_run_dir> `
  --out-json outputs\paper_readiness\latest.json `
  --out-md outputs\paper_readiness\latest.md
```

如果 `positive_claim_ready = false`，不能写正向实验结论；只能继续维护
pre-API 方法草稿、负结果讨论或回到实验阶段。

先更新：

```text
docs/paper/patch_verification_outline.md
```

再新增：

```text
docs/paper/patch_verification_draft.md
```

论文结构：

1. Introduction：AI-generated patch acceptance risk。
2. Motivation：旧实验说明 LLM-only review 不能当 merge gate。
3. Problem Definition：patch verification，不是传统 bug finding。
4. Method：candidate construction、label integrity、evidence-first protocol。
5. Experiment：dataset、conditions、models、metrics。
6. Results：false accept、false reject、accepted precision、recall、escalation。
7. Failure Analysis：unsupported claims、overfitting、partial fixes、evidence gaps。
8. Threats：oracle incompleteness、patch realism、model drift、dataset size。
9. Conclusion。

初稿写作前的最低输入：

- `docs/experiments/patch_verification_pilot_report.md`
- `<full_run_dir>/api_pilot_report.md`
- full run 的 `reviews.jsonl`
- full run 的 `metrics.json`
- failure analysis 摘要
- `<full_run_dir>/gate_report.json`
- `outputs/paper_readiness/latest.json`

初稿中必须明确区分：

- no-API baselines；
- dry-run prompt boundary checks；
- mock pipeline checks；
- real API model results。

匿名 supplemental package 生成命令：

```powershell
python scripts\prepare_anonymous_artifact.py `
  --out artifacts\research95_anonymous_artifact.zip `
  --manifest-out artifacts\research95_anonymous_artifact_manifest.json
python scripts\audit_anonymous_artifact.py `
  --artifact artifacts\research95_anonymous_artifact.zip `
  --out-json artifacts\research95_anonymous_artifact_audit.json `
  --out-md artifacts\research95_anonymous_artifact_audit.md
```

该 package 当前只包含源码、配置模板、示例、文档和 prompt/schema；不包含
`.env`、local config、`outputs/`、`data/`、raw API responses、本地 benchmark
checkouts 或已有 artifact zip。

## 9. 每轮结束检查

每轮修改后执行：

```powershell
python scripts\audit_goal_completion.py `
  --out-json outputs\goal_completion\latest.json `
  --out-md outputs\goal_completion\latest.md
python scripts\audit_credential_boundary.py `
  --out-json outputs\credential_boundary\latest.json `
  --out-md outputs\credential_boundary\latest.md
python scripts\audit_bootstrap_safety.py `
  --out-json outputs\bootstrap_safety\latest.json `
  --out-md outputs\bootstrap_safety\latest.md
python scripts\audit_workflow_guard.py `
  --out-json outputs\workflow_guard\latest.json `
  --out-md outputs\workflow_guard\latest.md
python scripts\audit_command_templates.py `
  --out-json outputs\command_templates\latest.json `
  --out-md outputs\command_templates\latest.md
python scripts\run_local_quality_gate.py `
  --out-json outputs\local_quality_gate\latest.json `
  --out-md outputs\local_quality_gate\latest.md
```

如需手工排错，再分步执行：

```powershell
python -m compileall src scripts
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
$secretPattern = "sk-" + "or-v1|OPENROUTER_API_KEY=.*[A-Za-z0-9_-]{20,}|" + "[A-Z]:\\\\Users\\\\|/mnt/|" + "models\\.coder\\.local|models\\.weak\\.local|models\\.matched\\.local"
rg -a -n $secretPattern .
```

如果 `rg` 命中 `outputs/`，优先确认是否为 ignored raw output；如果命中 tracked docs/code，必须修复。

每次代码或实验计划变更后更新：

- `README.md`
- `docs/INDEX.md`
- `docs/plans/current_plan.md`
- `docs/plans/current_plan_zh.md`
- 相关 `docs/experiments/*.md`
- `docs/experience/engineering_notes.md`
- 如有 prompt 变化，更新 `docs/prompts/prompt_change_log.md`

## 10. 当前下一步

下一位 AI agent 应从这里继续：

1. 先运行 `scripts\audit_execution_readiness.py`，确认 no-API、API 和 Git readiness。
2. 运行 `scripts\audit_ai_plan_progress.py`，确认计划阶段 complete、partial、blocked、pending 状态。
3. 运行 `scripts\write_human_input_packet.py`，生成真实 API 前缺失输入和安全命令顺序。
4. 运行 `scripts\write_pre_api_handoff.py`，刷新本地 pre-API 交接状态。
5. 运行 `scripts\write_git_sync_packet.py`，记录 Git 状态和 remote 决策。
6. 运行 `scripts\write_reproducibility_manifest.py`，确认原始 no-API pilot 与 repro run 的 deterministic outputs 仍然匹配。
7. 运行 `scripts\audit_goal_completion.py`，确认哪些完整目标条件仍缺失；真实 API、
   postprocess、paper gate、artifact、local quality 和 Git 证据未齐时不能声明完成。
8. 编写 `llm_only` 与 `evidence_first` prompt，并记录到 `docs/prompts/prompt_change_log.md`。
   状态：已完成。
9. 实现或改造 API runner，输出 `reviews.jsonl`、`metrics.json`、`run_summary.md`。
   状态：runner 已实现；真实 run 后会自动写 `reviews.jsonl`、`metrics.json`、`run_summary.md`。
10. 下一步执行 smoke API run：只取 2 个 candidates，条件只用 `llm_only` 和 `evidence_first`。
   前置条件：`.env` 中存在 `OPENROUTER_API_KEY`，并明确 OpenRouter model slug。
11. Smoke run 正常后再运行当前已验证的 30 candidates，不扩大模型和条件。
12. 运行后用 `scripts\summarize_api_pilot_results.py` 生成
   `api_pilot_report.md`。
13. 真实 full API run 后，用 `scripts\extract_api_failure_examples.py` 生成
   `failure_examples.json` 和 `failure_examples.md`。
14. 用 `scripts\evaluate_api_pilot_gate.py` 生成 `gate_report.json` 和
   `gate_report.md`。
15. 分析 false accept、accepted precision、correct-patch recall、escalation 和 invalid-output。
16. 每次更新 validation、dry-run 或 API run 后重新生成 pilot/report 文档。

当前硬性前置条件：

- `.env` 必须存在，且包含 `OPENROUTER_API_KEY`。
- `configs/model_selection.local.json` 必须存在，且通过 `scripts/validate_model_selection.py`。
- `configs/api_pilot.local.json` 必须存在，且 model 不能是 placeholder。
- `configs/model_selection.local.json` 中的 model 必须和
  `configs/api_pilot.local.json` 中的 model 一致。
- `scripts/preflight_api_pilot.py` 必须返回 `api_ready = true`。
- 若当前目录还不是 Git 仓库，不能宣称已完成 GitHub 同步。

模型选择辅助：

- 先查看 `docs/experiments/model_selection_shortlist.md`。
- shortlist 只是候选依据，不能替代用户确认。
- 用 `scripts/audit_openrouter_model_catalog.py` 检查候选 slug 是否仍在
  OpenRouter 公开 catalog 中可见。
- 生成 `configs/model_selection.local.json` 和 `configs/api_pilot.local.json`
  时优先加 `--require-openrouter-catalog`，在写入 local config 前阻止不可见
  slug。
- 推荐候选目前是 `anthropic/claude-sonnet-4.6`，但只有用户确认后才能写入
  `configs/model_selection.local.json` 和 `configs/api_pilot.local.json`。
