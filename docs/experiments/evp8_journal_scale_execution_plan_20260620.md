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
- `data/protocols/evp8_deepseek_qwen_smoke_check_only_v0_1.json`
- `data/protocols/evp8_deepseek_qwen_smoke_execution_packet_v0_1.json`
- `docs/experiments/evp8_deepseek_qwen_smoke_execution_packet_v0_1.md`
- `data/protocols/evp8_deepseek_qwen_smoke_result_audit_v0_1.json`
- `docs/experiments/evp8_deepseek_qwen_smoke_result_audit_v0_1.md`
- `data/protocols/evp8_deepseek_qwen_smoke_synthesis_v0_1.json`
- `docs/experiments/evp8_deepseek_qwen_smoke_synthesis_v0_1.md`

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
- guarded smoke runner check-only: passed for 35 project-frequency-stratified
  smoke packets, including the dominant youtube-dl project, without storing
  rendered prompt text, generating raw outputs, or calling APIs;
- smoke execution packet: ready, with exact G0 guard commands, post-smoke
  audit checks, G4 synthesis checks, and DeepSeek-then-Qwen execute commands;
  it explicitly does not authorize API calls by itself;
- Phase 1 DeepSeek/Qwen smoke: executed after explicit user authorization on
  2026-06-20 for the frozen 5-candidate x 7-level subset;
- post-smoke audit: `passed` for DeepSeek V4 Pro and Qwen3.7 Max tracked
  raw-output-free summaries, without reading raw responses;
- G4 smoke synthesis: `passed`; it reports only descriptive per-level decision
  counts from tracked summaries. In the smoke subset both models returned
  `escalate` for all five records at every E0-E6 level;
- cost-observability repair: DeepSeek uses controlled USD token-pricing
  estimate after the 4096-token budget repair; Qwen uses controlled CNY
  token-pricing estimate and does not invent USD cost or exchange-rate
  conversion;
- G5 no-API first-batch full-run packet: `ready`. It records the exact
  DeepSeek/Qwen 686-call full-run commands, expected raw/summary paths,
  USD/CNY cost fields, per-level aggregate requirements, and post-full-run
  audit/synthesis commands. It does not authorize API execution;
- DeepSeek G6 first-batch full run: executed after explicit user authorization
  on 2026-06-20. The run produced 686 raw records under ignored `outputs/` and
  a tracked raw-output-free summary with 686/686 parse-valid records, passed
  first-batch full gate, passed usage/cost gate, and estimated USD cost
  `0.788808816`;
- Qwen G6 first-batch full run: executed after explicit user authorization on
  2026-06-21. The run produced 686 raw records under ignored `outputs/` and a
  tracked raw-output-free summary with 686/686 parse-valid records, passed
  first-batch full gate, passed usage/cost gate, and estimated CNY cost
  `41.119548`;
- post-full-run audit: `passed` for both DeepSeek V4 Pro and Qwen3.7 Max
  tracked summaries, without reading raw responses;
- first-batch synthesis: `passed`; it reports only descriptive DeepSeek/Qwen
  per-level decision counts for the frozen EVP-8 v0.1 98-candidate packet set;
- current next gate: prepare a no-API later-model completion packet before
  Kimi K2.6, Devstral 2, and Gemini 2.5 Flash API calls.

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

Historical smoke execution order, now completed through G4:

1. Commit the DeepSeek/Qwen local preflight artifacts.
2. Wait for the user to explicitly say to execute the EVP-8 Phase 1 smoke.
3. After that command, rerun the no-API guards:
   - `python scripts\check_evp8_deepseek_qwen_g0.py --check`
   - `python scripts\audit_evp8_protocol_spec.py --check`
   - `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
   - `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`
   - `python scripts\write_evp8_smoke_execution_packet.py --check`
   - `python scripts\audit_evp8_smoke_results.py --self-test`
   - `python scripts\audit_evp8_smoke_results.py --check`
   - `python scripts\summarize_evp8_smoke_synthesis.py --self-test`
   - `python scripts\summarize_evp8_smoke_synthesis.py --check`
   - `git status --short --ignored configs\evp8_deepseek_qwen.local.json`
4. Only if those guards pass, run DeepSeek V4 Pro smoke and Qwen3.7 Max smoke
   on the frozen 5-candidate x 7-level subset.
5. Stop after the two smoke runs and audit their raw-output-free summaries; do
   not start the 686-call full runs without a separate gate.

Immediate next execution order:

1. Review the G5 no-API first-batch full-run packet:
   `data/protocols/evp8_deepseek_qwen_first_batch_full_run_packet_v0_1.json`.
2. If the user explicitly authorizes the first-batch full run, run only the
   DeepSeek command first:
   `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --run-scope full --config configs\evp8_deepseek_qwen.local.json --model-id deepseek/deepseek-v4-pro`.
3. Run `python scripts\audit_evp8_first_batch_full_results.py --check`.
4. Run Qwen only if the DeepSeek first-batch full audit passes.
5. Run `python scripts\summarize_evp8_first_batch_full_synthesis.py --check`
   only after both first-batch summaries pass audit.
6. Do not start Kimi/Devstral/Gemini or five-model synthesis from this
   authorization.

### Immediate DeepSeek/Qwen Follow-up Plan

This is the next executable sequence once the user explicitly authorizes real
EVP-8 Phase 1 smoke/API execution. A generic "continue" is not enough; the
authorization must clearly refer to executing the smoke/API step under this
plan.

Gate G0: no-API revalidation immediately before any model call.

- Run:
  - `python scripts\check_evp8_deepseek_qwen_g0.py --check`
  - `python scripts\audit_evp8_protocol_spec.py --check`
  - `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
  - `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`
  - `python scripts\write_evp8_smoke_execution_packet.py --check`
  - `python scripts\audit_evp8_smoke_results.py --self-test`
  - `python scripts\audit_evp8_smoke_results.py --check`
  - `python scripts\summarize_evp8_smoke_synthesis.py --self-test`
  - `python scripts\summarize_evp8_smoke_synthesis.py --check`
  - `git status --short --branch --ignored configs\evp8_deepseek_qwen.local.json`
- Acceptance:
  - G0 guard summary, protocol audit, strict preflight, smoke check-only,
    execution packet, current post-smoke audit self-test/check, and G4
    synthesis self-test/check all pass;
  - expected DeepSeek/Qwen raw-response and tracked-summary output paths do not
    already exist;
  - no `.env`, `configs/*.local.json`, `outputs/`, `artifacts/`, raw responses,
    or rendered prompt text are staged;
  - current post-smoke audit remains `waiting_for_execution` before the first
    model call.
- If any guard fails, stop and diagnose before API execution.

Gate G1: DeepSeek V4 Pro smoke.

- Run only after G0 passes:
  `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --config configs\evp8_deepseek_qwen.local.json --model-id deepseek/deepseek-v4-pro`
- Scope:
  project-frequency-stratified 5 candidates x 7 evidence levels = 35 planned
  calls.
- Expected boundary:
  raw responses only under ignored `outputs/`; tracked output is the
  raw-output-free smoke summary.
- Stop if parse/schema validity, usage/cost observability, returned model id,
  raw-output boundary, or provider route checks fail.

Gate G2: DeepSeek smoke audit.

- Run:
  `python scripts\audit_evp8_smoke_results.py --check`
- Acceptance:
  - DeepSeek summary exists and passes audit;
  - summary `protocol_id` and `candidate_set_id` match the execution packet;
  - summary `request_model_id_counts`, `provider_route_counts`, and
    `actual_model_id_counts` support model/provider drift checks without
    opening raw responses;
  - summary `review_count_by_evidence_level`,
    `parse_valid_count_by_evidence_level`,
    `invalid_parse_count_by_evidence_level`, and
    `decision_counts_by_evidence_level` cover every `E0-E6` level without
    reading raw responses;
  - `review_count=35`, `parse_valid_count=35`, `invalid_parse_count=0`;
  - raw response paths match the execution packet and stay under ignored
    `outputs/`;
  - tracked summary contains no API key, local config value, rendered prompt
    text, or raw response body.
- If DeepSeek does not pass, do not run Qwen. Diagnose first and record the
  blocker.

Gate G3: Qwen3.7 Max smoke.

- Run only after G2 passes:
  `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --config configs\evp8_deepseek_qwen.local.json --model-id qwen/qwen3.7-max`
- Scope:
  the exact same 5 candidates x 7 evidence levels and same frozen prompt/schema
  as DeepSeek.
- Stop if parse/schema validity, usage/cost observability, returned model id,
  raw-output boundary, or provider route checks fail.
- Do not invent Qwen USD cost. If token usage is present and the official
  Alibaba Cloud Model Studio qwen3.7-max pricing is used, record it as
  controlled `cost_cny` with `cost_currency = CNY`. Do not silently convert it
  to USD inside the smoke runner.

Gate G4: two-model smoke synthesis.

- Run:
  `python scripts\summarize_evp8_smoke_synthesis.py --check`
- Update raw-output-free summaries, audit notes, current plan, engineering
  notes, and index entries as needed.
- Allowed claim:
  DeepSeek/Qwen smoke execution readiness and parse/cost/boundary status for
  the frozen EVP-8 v0.1 smoke subset, plus descriptive evidence-level
  decision patterns computed only from tracked per-level summary aggregates.
- Forbidden claim:
  final five-model journal result, full-cohort generalization, LLM superiority
  over deterministic baselines, or evidence-level effectiveness beyond the
  smoke subset.

Gate G5: post-smoke decision and first-batch full-run packet.

- Status: `ready` as of 2026-06-20.
- The separate no-API full-run packet for the first-batch DeepSeek/Qwen
  686-call runs is:
  `data/protocols/evp8_deepseek_qwen_first_batch_full_run_packet_v0_1.json`.
- Do not start the 686-call full runs in the same step unless the user gives a
  separate full-run authorization after reviewing the smoke audit.
- If a protocol, prompt, schema, candidate-set, or evaluator-join bug is found
  after any model call, bump the EVP-8 protocol version and rerun affected
  models from scratch; do not mix v0.1 and repaired results as one experiment.
- The no-API full-run packet must state:
  - protocol id, prompt id, candidate-set id, output schema id, and evaluator
    join version;
  - exact DeepSeek and Qwen execute commands;
  - expected raw-response and tracked-summary paths;
  - per-model planned call count of 686;
  - cost/usage observability fields;
  - post-full-run audit and synthesis commands;
  - the boundary that the packet is not itself execution authorization.

Gate G6: DeepSeek/Qwen first-batch full run.

- Execute only after a separate user authorization for the first-batch full
  run, not as part of the smoke step.
- DeepSeek has been run first on the frozen 98 candidates x 7 evidence levels =
  686 calls and passed the full-run audit.
- Qwen has been run on the same frozen 98 candidates x 7 evidence levels = 686
  calls and passed the full-run audit.
- Do not rerun the G5 first-batch full-run packet check after DeepSeek full
  outputs exist. That packet is the pre-full-run handoff snapshot and includes
  an expected-output absence guard. Before Qwen, use strict preflight,
  full-scope check-only, first-batch full-result audit, and synthesis status as
  the gate.
- Qwen must use the same EVP-8 v0.1 frozen packets, prompt, schema, parser,
  temperature, retry policy, and evaluator joins as DeepSeek.
- The tracked two-model first-batch synthesis has passed. It may report
  cross-model stability and disagreement patterns on the frozen EVP-8 v0.1
  packet set, but it remains a first-batch result rather than the final
  five-model journal conclusion.

Gate G7: later model completion packet.

- Add Kimi K2.6, Devstral 2, and Gemini 2.5 Flash only after the DeepSeek/Qwen
  first batch has a stable full-run boundary.
- They must use the same frozen packets, prompt version, schema, evaluator
  joins, temperature, retry policy, and output parser.
- If using OpenRouter, require `OPENROUTER_API_KEY`, pin exact model IDs, and
  record actual returned provider/model for every review record.
- Prepare a no-API execution packet before later-model API calls. The packet
  must include provider route, model ids, expected outputs, cost ceiling, retry
  policy, and stop gates for all three later models.

Gate G8: five-model journal synthesis.

- Run only after all selected model audits pass on the same frozen EVP-8 input
  set.
- Produce per-level metrics, model-by-level comparison, uncertainty analysis,
  utility sensitivity, qualitative cases, and claim-boundary audit.
- Allowed claim depends on observed results. If trends are inconsistent, write
  a robustness-boundary result rather than selecting only favorable models or
  levels.

Gate G9: paper writing and artifact freeze.

- Update the manuscript, generated tables, figures, artifact checklist, and
  anonymous package only after the synthesis and claim-boundary audit are
  complete.
- Keep EVP-7 as the bounded four-anchor pilot and motivation. Do not merge its
  E0/E2/E4/E6 artifacts with EVP-8 E0-E6 results as one dataset.
- Before submission freeze, run local quality gate, paper readiness audit,
  artifact audit, and Git sync checks.

### Phase 1: DeepSeek + Qwen First Batch

After Phase 0 passes and the user explicitly says to execute:

1. Run DeepSeek V4 Pro smoke on a stratified 5-candidate x 7-level subset
   (35 planned calls).
2. Run Qwen3.7 Max smoke on the same subset and same frozen prompt/schema.
3. Use `scripts/run_evp8_deepseek_qwen_smoke.py`, which is check-only by
   default, requires explicit `--execute` for API calls, refuses tracked
   example config execution, writes raw responses only under ignored `outputs/`,
   and writes tracked raw-output-free summaries only.
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
