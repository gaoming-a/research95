# CCF-C Baseline Feasibility Audit v0.1

## Scope

- audit id: `ccfc_baseline_feasibility_audit_v0_1`
- status: `passed`
- boundary: tracked aggregate summaries only; no API call, no raw output read, no prompt text or patch text read.
- cohort: 98 candidates, 21 correct and 77 incorrect.

## Baseline Table Readiness

| baseline | status | accept | reject | escalate | accepted precision | correct recall | false accept rate | escalation rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| always_escalate | calculable_from_label_totals | 0 | 0 | 98 | NA | 0.00% | 0.00% | 100.00% |
| always_reject | calculable_from_label_totals | 0 | 98 | 0 | NA | 0.00% | 0.00% | 0.00% |
| always_accept | calculable_from_label_totals | 98 | 0 | 0 | 21.43% | 100.00% | 100.00% | 0.00% |
| uniform_random_three_way_expected | calculable_expected_reference_from_label_totals | 32.666666666666664 | 32.666666666666664 | 32.666666666666664 | 21.43% | 33.33% | 33.33% | 33.33% |
| rule_only_visible_tool | completed_existing_tracked_result | 25 | 73 | 0 | 80.00% | 95.24% | 6.49% | 0.00% |
| qwen_e6_full | completed_existing_tracked_result | 24 | 74 | 0 | 83.33% | 95.24% | 5.19% | 0.00% |
| deepseek_e6_full | completed_existing_tracked_result | 23 | 75 | 0 | 82.61% | 90.48% | 5.19% | 0.00% |

## Feasibility Decisions

| baseline or analysis | feasibility | paper role | reason/source |
|---|---|---|---|
| `always_escalate` | calculable_from_label_totals | conservative abstention reference, not a useful verifier. | Uses only aggregate correct/incorrect counts; no candidate text, prompt text, raw model output, or API call is needed. |
| `always_reject` | calculable_from_label_totals | safety-heavy lower-bound reference exposing recall collapse. | Uses only aggregate correct/incorrect counts. |
| `always_accept` | calculable_from_label_totals | unsafe throughput reference exposing base-rate risk. | Uses only aggregate correct/incorrect counts. |
| `uniform_random_three_way_expected` | calculable_expected_reference_from_label_totals | sanity-check reference for the decision space, not a completed verifier or a reported stochastic experiment. | Uses the expected value of a uniform random accept/reject/escalate policy over aggregate correct/incorrect counts; no stochastic simulation or candidate-level decisions are required. |
| `rule_only_visible_tool` | completed_existing_tracked_result | main deterministic baseline for E6 full/no-verdict comparison. | data\reviews\evp8_e6_no_verdict_ablation_comparison.json |
| `qwen_e6_full` | completed_existing_tracked_result | model condition to compare against rule-only and no-verdict ablations. | data\reviews\evp8_e6_no_verdict_ablation_comparison.json |
| `deepseek_e6_full` | completed_existing_tracked_result | secondary model condition in the E6 ablation package. | data\reviews\evp8_e6_no_verdict_ablation_comparison.json |
| `majority_vote_across_models` | not_feasible_from_current_aggregate_boundary | do not report as completed unless a separate candidate-level, raw-output-free audit is built. | Requires candidate-level aligned decisions across models and hidden labels. The current paper-facing boundary for this audit uses aggregate summaries only. |
| `separate_no_tool_e0_deterministic_verifier` | partial_only | report Qwen E0 and always-escalate separately; do not call this a completed deterministic E0 verifier. | Qwen E0 behavior exists, and always-escalate is calculable as a no-evidence conservative reference. A separate non-LLM E0 verifier policy has not been implemented as a tracked result. |

## Manuscript Boundary

Allowed:

- Report always-escalate/always-reject/always-accept as deterministic reference policies calculated from label totals.
- Report uniform-random three-way only as an expected reference policy, not as a completed stochastic baseline run.
- Report rule-only visible-tool as the completed deterministic E6 baseline.
- Use Phase A confidence intervals for rule-only and E6 model conditions.

Forbidden:

- Do not claim a completed majority-vote baseline from aggregate-only files.
- Do not call always-escalate a successful verifier.
- Do not present the uniform-random expected reference as a real randomized experiment.
- Do not claim LLM superiority over deterministic baselines as the paper's main result.

## Checks

| check | passed | detail |
|---|---:|---|
| `input_files_exist` | True | `` |
| `label_totals_match_record_count` | True | `{'correct_total': 21, 'incorrect_total': 77, 'record_count': 98}` |
| `no_verdict_comparison_checks_pass` | True | `` |
| `phase_a_checks_pass` | True | `` |
| `rule_only_record_count_matches` | True | `98` |
| `audit_api_call_attempted` | True | `False` |
| `raw_outputs_read_by_this_audit` | True | `False` |
| `prompt_or_patch_text_read_by_this_audit` | True | `False` |
