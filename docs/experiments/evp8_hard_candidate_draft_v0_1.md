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
- visible outcome records: 35
- visible completed/error/timeout records: 9

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

- decision counts: `{'accept': 4, 'escalate': 26, 'reject': 5}`
- false accepts: 4
- false rejects: 0
- actionable false-accept/false-reject headroom: 4
- opportunity size including escalations: 30

The deterministic baseline uses only model-visible apply and visible-test
outcome evidence. Candidates with visible test errors are rejected; candidates
whose visible tests are blocked or only listed as hints are escalated.

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
- visible_test_outcomes_available: passed (9)
- actionable_false_accept_or_reject_headroom_at_least_10: failed (4)

API readiness: `blocked`

Blocked reasons:

- `nontrivial_hard_negative_count_at_least_20`
- `actionable_false_accept_or_reject_headroom_at_least_10`

Plain-language conclusion: the draft reaches the 30-50 candidate size and
has enough AI/agent wrong patches, and the visible-test runner now records
some executable outcomes. It still does not meet the 20 nontrivial-hard-
negative gate, and the current tool-only baseline exposes 4 actionable false accept/reject cases, still below the pre-API threshold of 10.
The next action is to add or validate harder non-control negatives and
improve visible-test execution coverage, not to run Qwen or DeepSeek.
