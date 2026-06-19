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
2. Decide the initial candidate set:
   - either use the current 20-task / 94-candidate cohort for EVP-8 smoke and
     protocol validation;
   - or first expand to the journal-scale 30-50 bug / 100-180 candidate target.
3. Generate dry-run evidence packets and prompt manifests.
4. Run leakage, schema, prompt-boundary, cost-observability, and deterministic
   tool-baseline dry-run checks.
5. Record protocol version, prompt version, candidate-set version, model list,
   provider routing policy, temperature, max tokens, retry policy, and stop
   rules.

### Phase 1: DeepSeek + Qwen First Batch

After Phase 0 passes and the user explicitly says to execute:

1. Run DeepSeek V4 Pro smoke.
2. Run Qwen3.7 Max smoke.
3. If both pass parse, usage/cost, and quality gates, run their full EVP-8
   evaluations on the frozen packet set.
4. Report these results only as a two-model interim result.

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
