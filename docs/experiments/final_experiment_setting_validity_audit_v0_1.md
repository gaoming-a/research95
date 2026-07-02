# Final Experiment-Setting Validity Audit v0.1

Date: 2026-07-03

This is a no-API, raw-output-free validity packet for the stable CCF-C paper route.
It audits whether the current results can be treated as real bounded evidence rather
than artifacts of prompt, label, leakage, parser, or post-hoc setting errors.

## Bottom Line

- overall status: `passed_with_bounded_claims`
- paper target: `stable CCF-C submission`
- conclusion: The current results are usable as real bounded evidence for evidence-conditioned risk behavior, provided the paper does not claim reliable autonomous correctness verification.

## Checks

| check | passed | detail |
| --- | ---: | --- |
| `api_call_not_attempted_by_validity_audit` | true | `False` |
| `raw_model_outputs_not_read_by_validity_audit` | true | `False` |
| `patch_text_not_read_by_validity_audit` | true | `False` |
| `prompt_text_not_read_by_validity_audit` | true | `False` |
| `five_model_synthesis_passed` | true | `passed` |
| `five_model_all_source_checks_passed` | true | `10` |
| `v0_2_accept_aware_synthesis_passed` | true | `passed` |
| `v0_3_qwen_synthesis_passed` | true | `passed` |
| `qwen_label_conditioned_matrix_complete` | true | `9` |
| `qwen_hidden_labels_joined_after_execution` | true | `{'api_call_attempted': False, 'correct_label': 'correct_under_f2p_and_p2p_broad', 'decision_parse_source': 'raw_response_text final JSON content only', 'incorrect_definition': 'any selected candidate whose label_with_p2p_broad is not the correct label', 'prompt_text_stored': False, 'raw_response_content_stored': False, 'reasoning_content_used': False}` |
| `e6_no_verdict_comparison_checks_passed` | true | `13` |
| `hard_claim_traceability_passed` | true | `True` |
| `hard_tool_contestation_audit_passed` | true | `passed` |
| `hard_tool_contestation_complete_coverage` | true | `['deepseek/deepseek-v4-pro', 'qwen/qwen3.7-max']` |
| `realistic_hardneg_gate_analysis_passed` | true | `passed` |
| `realistic_hardneg_gate_not_overclaimed` | true | `{'next_step': 'Do not run verifier API. Redesign source strategy for a third project or revise the paper claim to report a two-project hard-negative cohort.', 'ready_for_verifier_api': False}` |
| `prompt_boundary_v0_3_no_rendered_prompt_stored` | true | `{'prompt_boundary_audit_status': 'passed', 'api_call_attempted': False, 'rendered_prompt_text_stored': False, 'evidence_packets_generated': False}` |

## Supported Results

| id | status | allowed wording | setting validity |
| --- | --- | --- | --- |
| `evp8_five_model_decision_patterns` | `supported_descriptive` | On the frozen EVP-8 packet set, five models show descriptive per-level decision-pattern differences. | run/parse/model coverage passed; raw outputs are summarized through tracked aggregate audits. |
| `accept_aware_v0_2_v0_3_repair` | `supported_as_setting_repair` | Accept-aware construction repairs the earlier zero-accept artifact and allows descriptive recall/false-accept analysis. | matrix completeness, no duplicate/missing cells, and post-execution label-conditioned analysis pass. |
| `verdict_dependence_and_no_verdict_ablation` | `supported_qualified` | Removing verdict-like fields changes model behavior, with model-dependent risk-control tradeoffs. | same frozen 98-candidate matrix is checked across rule-only, E6-full, and E6-no-verdict rows. |
| `tool_contestation_risk_triage` | `supported_qualified` | Tool-contestation shifts known false accepts mostly toward escalation, supporting risk triage rather than strict semantic correction. | 47-candidate coverage is complete and strict correction remains separated from escalation. |
| `realistic_hardneg_source_acquisition_boundary` | `supported_negative_boundary` | The fresh realistic branch currently supports a two-project source-acquisition/gate-readiness negative result, not a verifier-ready main experiment. | tracked gate has 26/30 visible-pass/hidden-fail cases across two projects and keeps verifier API blocked. |

## Setting Artifacts And Controls

| risk | status | paper handling |
| --- | --- | --- |
| v0.1 zero-accept artifact | `controlled_by_repair_and_claim_boundary` | Do not use v0.1 zero-accept as the main behavioral claim; use it only as protocol history. |
| hidden evaluator leakage | `controlled_by_packet_boundary_and_post_execution_join` | State that hidden labels are evaluator-only and used after execution for analysis. |
| verdict anchoring | `measured_not_eliminated` | Report with-verdict and no-verdict/tool-contestation separately. |
| escalation counted as correction | `controlled_by_metric_boundary` | Keep strict correction and safe handling separate. |
| third-project external-validity gap | `not_controlled_must_be_threat` | Write as limitation and negative source-acquisition result unless the gate is later repaired. |

## Remaining Threats

| threat | severity | required paper response |
| --- | --- | --- |
| Cohort size and project diversity remain limited for broad generalization. | `medium_for_ccf_c_high_for_ccf_b` | Scope the claim to candidate patch verification and report project/task counts explicitly. |
| Realistic hard-negative third-project gate remains blocked. | `medium` | Use it as a source-acquisition negative result, not as main verifier evidence. |
| Prompt and evidence formatting can influence model policy behavior. | `medium` | Present results as evidence-conditioned risk behavior, not intrinsic semantic proof. |
| Some historical experiments are diagnostic rather than paper-facing. | `low_if_claim_map_is_followed` | Keep historical versions in appendix/method provenance and avoid mixing them into main claims. |

## Forbidden Claims

- LLMs are reliable autonomous patch correctness verifiers.
- More visible evidence monotonically improves correctness verification.
- Escalation is equivalent to strict correction.
- The fresh realistic hard-negative branch is verifier-ready across three projects.
- The controlled EVP-8 or EVP-8-HARD cohorts prove broad external validity for real agent patch distributions.

## Next Action

Freeze this validity boundary into the manuscript claim map and threats-to-validity section before further experiments.
