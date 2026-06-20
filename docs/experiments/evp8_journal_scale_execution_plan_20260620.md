# EVP-8 Journal-Scale Execution Plan

Date: 2026-06-20

This is a no-API execution plan. It records the journal-upgrade route requested
by the user, but it does not authorize model calls, cohort expansion, or
evidence-packet generation by itself.

## Decision

The current EVP-7 paper package remains a bounded four-anchor pilot:
`E0/E2/E4/E6`, 20 paper-facing tasks, 94 candidates, and 376 DeepSeek G5
records. It must not be modified by inserting `E1/E3/E5`.

The journal version should be a new EVP-8 protocol:

- full adjacent-difference evidence ladder from `E0` through `E6`;
- journal-scale cohort target of 30-50 validation-stable bugs and 100-180
  candidates;
- multi-model evaluation under one frozen packet/prompt/schema version;
- current EVP-7 results used only as pilot evidence and design motivation.

## Evidence Levels

Every level must add exactly one clear evidence class over the previous level.
The final definitions must be frozen before any model call.

| Level | Model-visible evidence |
|---|---|
| E0 | Issue summary, candidate patch diff, and touched filenames. |
| E1 | Structured patch surface: changed files, functions/classes, hunk locations, neighboring symbols, and related imports/modules. |
| E2 | Patch-apply result plus syntax/import/static-check slots. |
| E3 | Visible fail-to-pass test evidence. |
| E4 | Visible pass-to-pass/regression test evidence. |
| E5 | Broader tool diagnostics, such as lint/static/test-log observations, without hidden evaluator labels. |
| E6 | Deterministic visible tool-summary / rule-based merge-gate evidence. |
| E7 | Oracle upper bound for evaluation only; never shown to the LLM verifier. |

The protocol must preserve visible/hidden separation: hidden evaluator labels,
oracle paths, expected outcomes, and ground-truth joins are evaluator-only.

## Current Phase 0 Artifacts

The first machine-checkable protocol artifact is:

- `data/protocols/evp8_protocol_v0_1.json`
- `data/protocols/evp8_candidate_set_v0_1.json`
- `data/protocols/evp8_candidate_set_v0_1_summary.json`
- `prompts/evp8_visible_evidence_merge_gate_v0_1.md`
- `data/protocols/evp8_prompt_manifest_v0_1.json`
- `data/protocols/evp8_prompt_boundary_audit_v0_1.json`
- `data/protocols/evp8_evidence_packet_dry_run_summary_v0_1.json`
- `data/protocols/evp8_schema_dry_run_summary_v0_1.json`
- `data/protocols/evp8_cost_observability_dry_run_v0_1.json`
- `data/protocols/evp8_deterministic_tool_baseline_dry_run_v0_1.json`
- `configs/evp8_deepseek_qwen.example.json`
- `data/protocols/evp8_deepseek_qwen_local_config_plan_v0_1.json`
- `data/protocols/evp8_deepseek_qwen_preflight_summary_v0_1.json`

It freezes the draft v0.1 ladder as a tracked protocol spec:

- `E0`: issue/patch seed;
- `E1`: structured patch surface;
- `E2`: patch-apply and static status slots;
- `E3`: visible fail-to-pass test evidence;
- `E4`: visible pass-to-pass/regression evidence;
- `E5`: broader visible tool diagnostics;
- `E6`: deterministic visible merge-gate summary;
- `E7`: evaluator-only oracle upper bound.

The corresponding audit command is:

```powershell
python scripts\audit_evp8_protocol_spec.py --check
```

Current audit status:

- protocol spec audit: passed;
- candidate set: frozen for Phase 0 smoke/protocol validation at 21 tasks, 6
  projects, and 98 candidates from the tracked EVP-7 structural cohort;
- prompt template: frozen and boundary-audited without API calls;
- packet/schema dry-run summaries: passed for 686 planned packet skeletons and
  686 deterministic schema outputs;
- cost-observability dry-run: passed for 686 planned calls per model;
- deterministic-baseline dry-run: passed for 686 schema-valid placeholder
  decisions using only model-visible evidence slots;
- DeepSeek/Qwen ignored local preflight: passed without printing key values or
  calling APIs;
- API readiness: waiting for explicit user smoke execution command;
- current blockers before smoke: no tracked Phase 0 or local preflight blockers.

This audit is intentionally no-API and does not authorize model calls, cohort
expansion, or EVP-8 evidence-packet generation.

## Model Plan

The intended five-model journal set is:

1. `deepseek/deepseek-v4-pro`
2. `qwen/qwen3.7-max`
3. `moonshotai/kimi-k2.6`
4. `mistralai/devstral-2512`
5. `google/gemini-2.5-flash`

Model selection must be justified by execution suitability rather than leaderboard
rank alone:

- fixed model IDs;
- sufficient context windows;
- structured-output compatibility;
- comparable practical cost/capability band;
- at least two non-Chinese provider families to reduce single-ecosystem
  confounding;
- software-engineering or code-task suitability where available.

Public leaderboards may only be cited as a secondary sanity check that selected
models are not obviously out of distribution.

## Phased Execution

### Phase 0: No-API Protocol Freeze

Before any model call:

1. Define and freeze `E0-E6` field schemas and prompt wording.
2. Use the current frozen Phase 0 smoke/protocol-validation candidate set:
   21 tasks, 6 projects, and 98 candidates. This is not the final journal-scale
   30-50 bug cohort.
3. Generate dry-run evidence packets and prompt manifests.
4. Run leakage, schema, prompt-boundary, cost-observability, and deterministic
   tool-baseline dry-run checks.
5. Record protocol version, prompt version, candidate-set version, model list,
   provider routing policy, temperature, max tokens, retry policy, and stop
   rules.

Immediate next execution order:

1. Commit the DeepSeek/Qwen local preflight artifacts.
2. Wait for the user to explicitly say to execute the EVP-8 Phase 1 smoke.
3. After that command, rerun the no-API guards:
   - `python scripts\audit_evp8_protocol_spec.py --check`
   - `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
   - `git status --short --ignored configs\evp8_deepseek_qwen.local.json`
4. Only if those guards pass, run DeepSeek V4 Pro smoke and Qwen3.7 Max smoke
   on the frozen 5-candidate x 7-level subset.
5. Stop after the two smoke runs and audit their raw-output-free summaries; do
   not start the 686-call full runs without a separate gate.

### Phase 1: DeepSeek + Qwen First Batch

After Phase 0 passes and the user explicitly says to execute:

1. Run DeepSeek V4 Pro smoke on a stratified 5-candidate x 7-level subset
   (35 planned calls).
2. Run Qwen3.7 Max smoke on the same subset and same frozen prompt/schema.
3. If the smoke runner is missing, add only the minimal guarded runner needed
   for this phase: check-only by default, explicit `--execute` for API calls,
   refusal to run against tracked example config, raw responses under ignored
   `outputs/`, and tracked raw-output-free summaries only.
4. If either smoke fails parse, schema, usage/cost, provider/model-id, or
   raw-output policy gates, stop and diagnose before any full run.
5. If both pass parse, usage/cost, and quality gates, run their full EVP-8
   evaluations on the frozen Phase 0 packet set: 98 candidates x 7 levels =
   686 planned calls per model, but only after a separate explicit full-run
   gate.
6. Report these results only as a two-model interim result.

This phase must not change evidence levels, prompt schema, candidate set, or
evaluator joins after the first model call. If a protocol bug is found, bump the
protocol version and rerun affected models from scratch.

### Phase 2: Later Model Completion

Kimi K2.6, Devstral 2, and Gemini 2.5 Flash can be added later. They must use
the same frozen EVP-8 packets and prompts as Phase 1.

If routed through OpenRouter, separate Gemini and Devstral official API keys are
not required; an `OPENROUTER_API_KEY` is sufficient. The runner must pin exact
model IDs and avoid automatic model substitution. If provider fallback is used,
the actual returned model/provider must be recorded per review record.

Estimated OpenRouter cost for the three later models only, excluding DeepSeek
and Qwen:

| Scope | Model-call cost plus 5.5% OpenRouter fee |
|---|---:|
| 100 candidates x 7 levels | about USD 7.12 |
| 180 candidates x 7 levels | about USD 12.82 |
| smoke/retry-safe planning budget | USD 10-30 |

The estimate assumes about 1200 input tokens and 1000 output tokens per review
call. It is a planning estimate, not a billing statement.

## Required Outputs

Each model run must produce:

- ignored raw responses;
- tracked raw-output-free summary;
- parse/quality audit;
- token usage and cost-observability summary;
- per-level metrics;
- model-by-level comparison table;
- candidate-level bootstrap or equivalent uncertainty analysis;
- utility sensitivity;
- claim-boundary update;
- qualitative cases that separate model-visible evidence from evaluator labels.

## Stop Gates

Stop before full run if any of the following occurs:

- leakage audit fails;
- prompt/schema dry-run fails;
- smoke parse-valid rate is below the predeclared threshold;
- usage/cost observability is missing;
- a model silently changes model ID/provider route without being recorded;
- the same packet/prompt version cannot be used across models;
- hidden evaluator labels are visible to the model.

## Forbidden Shortcuts

- Do not insert `E1/E3/E5` into existing EVP-7 artifacts.
- Do not compare Phase 1 two-model results as the final five-model journal
  conclusion.
- Do not change the protocol after DeepSeek/Qwen have started and then append
  later models as if inputs were identical.
- Do not select models solely by leaderboard rank.
- Do not claim LLM superiority over deterministic tool-only baselines unless
  the EVP-8 results directly establish it.
