# EVP-8-HARD Candidate Draft v0.1

Date: 2026-06-29

This is a no-API hard-case draft and baseline gate. It creates separate
evaluator-only and model-visible manifests, but it does not call model APIs,
render prompts, read raw model responses, or mutate the old 98-candidate
controlled cohort.

## Outputs

- evaluator_manifest: `data/patches/evp8_hard_evaluator_manifest_v0_1.jsonl`
- model_visible_seed_manifest: `data/evidence/evp8_hard_model_visible_seed_v0_1.jsonl`
- tool_only_baseline: `data/baselines/evp8_hard_tool_only_baseline_v0_1.jsonl`

## Candidate Summary

- candidates: 35
- tasks: 5
- projects: 1
- nontrivial hard negatives: 17
- AI/agent hard negatives: 10

Candidate types:

- `agent_plausible_wrong`: 10
- `correct_reference`: 8
- `irrelevant_or_noop_control`: 10
- `partial_fix`: 7

Labels:

- `agent_plausible_wrong`: 10
- `correct`: 8
- `irrelevant_or_noop`: 10
- `partial`: 7

## Tool-Only Baseline

- decision counts: `{'escalate': 35}`
- false accepts: 0
- false rejects: 0
- actionable false-accept/false-reject headroom: 0
- opportunity size including escalations: 35

The deterministic baseline escalates these candidates because the current
source files provide visible test hints but not model-visible test execution
outcomes. This is intentionally conservative: the draft must not pretend
that visible tests passed when only hidden oracle validation is available.

## Gate Checks

- api_call_not_attempted: passed (False)
- raw_model_outputs_not_read: passed (False)
- rendered_prompt_not_generated: passed (False)
- old_evp8_controlled_cohort_not_mutated: passed (False)
- source_inventory_passed: passed (passed)
- candidate_count_30_to_50: passed (35)
- nontrivial_hard_negative_count_at_least_20: failed (17)
- ai_or_agent_hard_negative_count_at_least_10: passed (10)
- model_visible_label_leakage_absent: passed ([])
- visible_test_outcomes_available: failed (0)
- actionable_false_accept_or_reject_headroom_at_least_10: failed (0)

API readiness: `blocked`

Blocked reasons:

- `nontrivial_hard_negative_count_at_least_20`
- `visible_test_outcomes_available`
- `actionable_false_accept_or_reject_headroom_at_least_10`

Plain-language conclusion: the draft reaches the 30-50 candidate size and
has enough AI/agent wrong patches, but it does not yet meet the 20
nontrivial-hard-negative gate and lacks visible test outcomes that could
create meaningful tool false accepts or false rejects. The next action is
to add or validate harder non-control negatives and visible test outcomes,
not to run Qwen or DeepSeek.
