# EVP-8 Hard-Case Extension Plan

Date: 2026-06-29

This plan extends the current EVP-8 evidence-visibility study only where the
current evidence is weak. It does not authorize API calls, prompt changes, or
candidate-set mutation by itself.

## Plain-Language Goal

The current experiment is useful, but its strongest weakness is that the tool
baseline has only 6 opportunity cases: 5 false accepts and 1 false reject. That
is enough to show a signal, but too small to make a strong claim about practical
value.

The next step is therefore not to add more models. The next step is to add
harder patch cases where tools are likely to be wrong:

- patches that pass visible tests but fail hidden checks;
- partial fixes that solve the obvious path but miss edge cases;
- regressions;
- plausible wrong AI-agent patches.

In simple terms:

> If we want a stronger paper, we need more cases where the tools can plausibly
> be fooled, then test whether Qwen or DeepSeek handles those cases better.

## Why This Is Needed

The current Qwen/DeepSeek `E6-no-verdict` result already answers a narrower
question:

- Qwen mostly keeps accepting/rejecting as before, and still repeats 4 tool
  false accepts.
- DeepSeek removes false accepts by escalating all tool false accepts, but it
  loses many correct accepts.

This is a meaningful model-dependent risk-control result. However, the paper
will be stronger if it can show that the same pattern holds on a small cohort
of naturally harder patches, not only on controlled reference/noop/partial/
regression candidates.

## Research Question

### RQ-H1: Does the observed risk-control pattern hold on harder patches?

Compare rule-only, Qwen, and DeepSeek on a new hard-case slice.

The expected outcomes are useful either way:

- If Qwen still repeats false accepts, the paper can argue that high recall
  comes with persistent merge risk.
- If DeepSeek still escalates false accepts, the paper can argue that
  conservative LLM verification is useful for triage but not auto-merge.
- If either model corrects tool false accepts without losing too much recall,
  that is stronger evidence of LLM-added value.

## Scope

Target size:

- 30-50 new hard-case candidates;
- at least 15 visible-test-passing but hidden-failing candidates if available;
- at least 10 partial or overfitted candidates;
- at least 5 regression candidates;
- at least 10 plausible AI-agent-generated wrong candidates if generation logs
  are available.

This is a hard-case extension, not a new benchmark.

## Non-Goals

- Do not expand to many models.
- Do not rerun Kimi, Devstral, Gemini, or OpenRouter later-models.
- Do not claim production merge safety.
- Do not change the main prompt unless a prompt-change audit is separately
  written.
- Do not mix new hard-case results into the old 98-candidate cohort as if they
  were one homogeneous sample.

## Phase A: Paper-Ready Analysis Without New API

Goal: make the current result publishable before adding new data.

2026-06-29 status: completed. The tracked outputs are:

- `data/reviews/evp8_phase_a_paper_ready_analysis.json`;
- `docs/experiments/evp8_phase_a_paper_ready_analysis.md`.

The analysis adds Wilson 95% confidence intervals, a 6-case opportunity table,
and utility/risk-policy comparisons. It does not call model APIs and stores no
raw response text or prompt text.

Tasks:

1. Add confidence intervals for current metrics:
   - correct recall;
   - accepted precision;
   - false accept rate;
   - escalation rate;
   - opportunity-set correction rate.
2. Write a case-study table for the 6 current opportunity cases:
   - 5 tool false accepts;
   - 1 tool false reject;
   - rule-only decision;
   - Qwen `E6-full`;
   - Qwen `E6-no-verdict`;
   - DeepSeek `E6-full`;
   - DeepSeek `E6-no-verdict`;
   - short explanation of missing visible evidence.
3. Add a utility/risk analysis:
   - false accept cost is highest;
   - false reject cost is medium;
   - escalation cost is human-review cost;
   - compare policies under multiple cost ratios.

Pass condition:

- no model API calls;
- no raw response text in tracked files;
- current claim boundary is explicit.

## Phase B: Hard-Case Candidate Construction

Goal: build a small hard-case cohort with stronger external validity.

2026-06-29 source-inventory status: completed, but candidate construction is
not complete. The tracked outputs are:

- `data/protocols/evp8_hard_case_source_inventory_v0_1.json`;
- `docs/experiments/evp8_hard_case_source_inventory_v0_1.md`.

The inventory scanned 34 non-raw local candidate source files and found 20
unique non-promoted eligible hard negatives, including 13 unique AI/agent
eligible hard negatives. This is only a source inventory: it does not create an
`EVP-8-HARD` manifest, does not mutate the old 98-candidate cohort, and does
not authorize API calls. The next Phase B action is no-API candidate curation
and a separate hard-case tool-only baseline.

2026-06-29 candidate-draft status: generated but API-blocked. The tracked
outputs are:

- `data/patches/evp8_hard_evaluator_manifest_v0_1.jsonl`;
- `data/evidence/evp8_hard_model_visible_seed_v0_1.jsonl`;
- `data/baselines/evp8_hard_tool_only_baseline_v0_1.jsonl`;
- `data/protocols/evp8_hard_candidate_draft_v0_1.json`;
- `docs/experiments/evp8_hard_candidate_draft_v0_1.md`.

The draft contains 35 applied candidates and separates evaluator-only labels
from model-visible seed records. However, it is not ready for API execution:
only 17 candidates are non-trivial hard negatives, visible test execution
outcomes are not available, and the deterministic tool-only baseline escalates
all 35 candidates. The next action is to add or validate more non-control hard
negatives and generate model-visible visible test outcomes.

Candidate sources, in priority order:

1. Existing local validated candidates that already have hidden oracle or P2P
   labels.
2. Existing AI-agent patch logs if they can be mapped to a task and validated.
3. New generated candidates only if the first two sources cannot reach the
   target size.

For every candidate, require:

- task id;
- patch diff;
- visible evidence;
- hidden evaluator label;
- patch application status;
- candidate type:
  - `correct_reference`;
  - `partial_fix`;
  - `regression_patch`;
  - `overfitted_patch`;
  - `agent_plausible_wrong`;
  - `irrelevant_or_noop_control`.

Pass condition:

- 30-50 candidates collected;
- at least 20 non-trivial hard negatives;
- hidden labels are stored evaluator-only;
- no hidden label appears in model-visible packets;
- deterministic tool-only baseline has at least 10 opportunity cases or at
  least 20% opportunity-set rate.

Stop condition:

- if fewer than 10 opportunity cases exist, do not run model APIs; report that
  the extension still lacks enough headroom.

## Phase C: No-API Packet and Baseline Gate

Goal: prepare hard-case packets without calling models.

Create a separate cohort id:

- `EVP-8-HARD`

Create separate outputs:

- candidate manifest;
- tool-only baseline summary;
- packet dry-run summary;
- prompt-boundary summary;
- schema dry-run summary.

Evidence conditions:

- `rule-only`;
- `E6-full`;
- `E6-no-verdict`.

Pass condition:

- all hard-case packets render without hidden labels;
- `E6-no-verdict` removes:
  - `rule_based_visible_merge_gate_decision`;
  - `rule_based_visible_merge_gate_reasons`;
  - `source_decision`;
- no rendered prompt text is stored in tracked outputs;
- no raw model output is generated.

## Phase D: Qwen/DeepSeek Hard-Case Run

Only after Phases B-C pass and the user explicitly authorizes API execution:

Run only:

- Qwen `E6-full`;
- Qwen `E6-no-verdict`;
- DeepSeek `E6-full`;
- DeepSeek `E6-no-verdict`.

Do not run lower evidence levels unless there is a separate reason. The goal is
not to rebuild the whole ladder; the goal is to test LLM-added value on hard
cases.

Pass condition:

- 100% parse-valid or a documented blocked gate;
- cost and model metadata present;
- tracked summaries are raw-output-free;
- label-conditioned metrics computed only after execution.

## Phase E: Paper Integration

The paper should separate two cohorts:

1. Controlled EVP-8 cohort:
   - shows evidence-visibility behavior and verdict-removal effects.
2. Hard-case extension:
   - tests whether the risk-control pattern holds when tools are more likely
     to be fooled.

Allowed strengthened claim:

> On a controlled cohort and a small hard-case extension, LLM patch verifiers
> show model-dependent risk-control behavior. Qwen preserves accept behavior
> but may repeat false accepts, while DeepSeek can reduce false accepts through
> escalation at the cost of correct-patch recall.

Forbidden claim:

> The system is a reliable automated patch verifier or production merge gate.

## Immediate Next Step

Do not run more APIs next.

Phase A, the Phase B source inventory, and the first no-API candidate draft are
complete. API execution remains blocked. Next add at least three more validated
non-control hard negatives and generate real model-visible visible test outcomes
for the hard-case candidates, then rebuild the tool-only baseline. Stop before
API if actionable false-accept/false-reject headroom remains below 10.
