# EVP-8-HARD Paper Claim Traceability v0.1

This audit maps EVP-8-HARD paper claims to tracked aggregate evidence. It does not call model APIs, read raw model responses, read patch diffs, modify prompts, or infer new model outputs.

## Summary

- passed: yes
- API call attempted: no
- raw outputs read: no
- patch diffs read: no
- prompt modified: no

## One-Sentence Argument

In controlled candidate patch verification, EVP-8-HARD shows that verdict-like tool evidence can dominate LLM decisions, while explicit tool-contestation can reduce unsafe autonomous accepts through escalation, but the evidence supports risk triage rather than autonomous correctness verification.

## Terminology Ledger

| term | definition | usage |
|---|---|---|
| `EVP-8-HARD` | The 47-candidate controlled hard-case cohort used in this branch. | Use as cohort name, not as a general benchmark claim. |
| `with-verdict` | The E6 setting where a verdict-like deterministic merge-gate summary is visible. | Use for tool-dominance analysis. |
| `evidence-only` | The ablation removing verdict-like fields while preserving lower-level visible evidence. | Use for verdict removal analysis. |
| `tool-contestation` | The prompt variant asking the model to challenge visible-test-only accept premises. | Use for conservative risk-triage analysis. |
| `strict correction` | Rejecting a known tool false accept. | Do not conflate with escalation. |
| `safe handling` | Rejecting or escalating a known tool false accept. | Report separately from strict correction. |

## Checks

| check | passed | detail |
|---|---:|---|
| `full_with_verdict_audit_passed` | true | `"passed"` |
| `evidence_only_audit_passed` | true | `"passed"` |
| `tool_contestation_audit_passed` | true | `"passed"` |
| `policy_case_analysis_passed` | true | `"passed"` |
| `candidate_count_consistent` | true | `null` |
| `raw_like_keys_absent` | true | `{}` |
| `with_verdict_models_match_tool` | true | `null` |
| `tool_contestation_strict_reject_zero` | true | `null` |
| `table_scaffold_has_required_rows` | true | `null` |

## Supported Claims

| id | status | evidence sources | allowed wording |
|---|---|---|---|
| `hard_cohort_scope` | supported | `full_with_verdict_audit`, `policy_case_analysis` | We study a controlled 47-candidate hard-case cohort with hidden evaluator labels. |
| `verdict_like_summary_dominance` | supported | `full_with_verdict_audit` | With a visible verdict-like tool summary, both models reproduced the deterministic baseline. |
| `evidence_only_partial_decoupling` | supported | `evidence_only_audit`, `policy_case_analysis` | Removing verdict-like fields changed decisions but did not produce strict corrections of known false accepts. |
| `tool_contestation_risk_triage` | supported | `tool_contestation_audit`, `policy_case_analysis` | Tool-contestation shifted known false accepts primarily from accept to escalation. |
| `policy_utility_tradeoff` | supported | `policy_case_analysis` | Under policies where false accepts are costly, contestation can be useful as a conservative triage layer. |

## Qualified Claims

| id | claim | condition |
|---|---|---|
| `risk_controller_not_merge_gate` | The system can be positioned as an evidence-aware risk controller, not as an autonomous merge gate. | Only valid when escalation is treated as human-review routing and not as automatic correctness verification. |
| `llm_added_value_is_policy_behavior` | The observed LLM-added value is policy behavior over evidence, not semantic proof. | Supported because known false accepts become escalations, while strict reject remains zero on the primary opportunity set. |

## Forbidden Claims

| id | forbidden claim | reason |
|---|---|---|
| `automatic_correctness_verifier` | The EVP-8-HARD system is a reliable automatic patch correctness verifier. | Tool-contestation does not strictly reject the nine known tool false accepts. |
| `llm_beats_tools_as_merge_gate` | Qwen or DeepSeek outperforms the deterministic tool-only baseline as an automatic merge gate. | With verdict, both models match the tool baseline; without verdict, gains are mostly escalation and correct recall collapses under tool-contestation. |
| `semantic_error_detection` | The LLM semantically identifies the wrong patches in the opportunity set. | Strict reject is 0/9 for both tool-contestation models. |
| `broad_external_validity` | The 47-candidate controlled cohort proves performance on real agent patch distributions. | The cohort is controlled and small; realistic hard-negative acquisition remains a separate boundary. |
| `monotonic_more_evidence_better` | More visible evidence monotonically improves verifier quality. | E6 with verdict repeats tool false accepts; tool-contestation improves safety by escalation but loses recall. |

## Paper Section Scaffold

| section | job | primary table |
|---|---|---|
| Results 1: Tool-verdict dominance | Show that Qwen and DeepSeek match tool-only under with-verdict. | `whole_cohort_rows` |
| Results 2: Verdict removal and tool-contestation | Show decision shifts after removing verdict fields and adding contestation. | `opportunity_set_rows` |
| Results 3: Policy utility | Show when conservative escalation is useful and when automation recall is lost. | `utility_rows` |
| Discussion | Interpret the result as risk triage, not autonomous verification. | `claim_traceability` |

## Linked Outputs

- Final table scaffold JSON: `data/reviews/evp8_hard_final_results_table_scaffold_v0_1.json`
- Final table scaffold Markdown: `docs/experiments/evp8_hard_final_results_table_scaffold_v0_1.md`
