# CCF-C Manuscript v0.3 Reviewer Audit

- audit id: `ccfc_manuscript_v0_3_reviewer_audit`
- status: `passed`
- boundary: no API call, no raw output read, no prompt text or patch text read.

## Checks

| check | passed | detail |
|---|---:|---|
| `manuscript_exists` | True | `docs\paper\ccfc_manuscript_rewrite_v0_1.md` |
| `claim_map_passed` | True | `passed` |
| `baseline_audit_passed` | True | `passed` |
| `draft_status_v0_3_present` | True | `` |
| `all_expected_citation_keys_present` | True | `[]` |
| `reference_support_records_present` | True | `` |
| `baseline_policy_boundary_present` | True | `` |
| `reference_policies_not_called_results` | True | `` |
| `rule_only_completed_baseline_present` | True | `` |
| `random_policy_expected_reference_present` | True | `` |
| `majority_vote_not_completed` | True | `` |
| `wilson_uncertainty_summary_present` | True | `` |
| `all_expected_uncertainty_conditions_present` | True | `[]` |
| `tool_contestation_ci_present` | True | `` |
| `hard_negative_stress_matrix_present` | True | `[]` |
| `old_realistic_gate_wording_absent` | True | `[]` |
| `claim_map_stress_matrix_summary_present` | True | `{'aggregate_by_condition': {'coverage_contestation': {'challenge_visible_test_only_accept_counts': {'False': 12, 'True': 81}, 'coverage_concern_counts': {'high': 50, 'low': 12, 'medium': 31}, 'decision_counts': {'accept': 12, 'escalate': 81}, 'decision_counts_by_project': {'PySnooper': {'accept': 9, 'escalate': 18}, 'cookiecutter': {'accept': 3, 'escalate': 48}, 'scrapy': {'escalate': 15}}, 'decision_counts_by_source_kind': {'curated_no_api_stress_source': {'escalate': 15}, 'model_generated_source': {'accept': 12, 'escalate': 66}}, 'invalid_parse_count': 0, 'parse_valid_count': 93, 'record_count': 93, 'repeated_false_accept_count': 12, 'repeated_false_accept_rate': 0.12903225806451613, 'safe_escalation_count': 81, 'safe_escalation_rate': 0.8709677419354839, 'safe_handling_count': 81, 'safe_handling_rate': 0.8709677419354839, 'strict_reject_count': 0, 'strict_reject_rate': 0.0}, 'current_merge_gate': {'challenge_visible_test_only_accept_counts': {'None': 93}, 'coverage_concern_counts': {'None': 93}, 'decision_counts': {'accept': 62, 'escalate': 31}, 'decision_counts_by_project': {'PySnooper': {'accept': 18, 'escalate': 9}, 'cookiecutter': {'accept': 34, 'escalate': 17}, 'scrapy': {'accept': 10, 'escalate': 5}}, 'decision_counts_by_source_kind': {'curated_no_api_stress_source': {'accept': 10, 'escalate': 5}, 'model_generated_source': {'accept': 52, 'escalate': 26}}, 'invalid_parse_count': 0, 'parse_valid_count': 93, 'record_count': 93, 'repeated_false_accept_count': 62, 'repeated_false_accept_rate': 0.6666666666666666, 'safe_escalation_count': 31, 'safe_escalation_rate': 0.3333333333333333, 'safe_handling_count': 31, 'safe_handling_rate': 0.3333333333333333, 'strict_reject_count': 0, 'strict_reject_rate': 0.0}}, 'candidate_count': 31, 'claim_boundary': 'This analysis measures false-accept handling on a hard-negative stress cohort. It does not measure correct recall and does not establish autonomous correctness verification.', 'cohort_id': 'EVP-8-REALISTIC-HARDNEG-STRESS', 'condition_ids': ['current_merge_gate', 'coverage_contestation'], 'hidden_label_boundary': 'All 31 stress-cohort candidates are visible-pass/hidden-fail hard negatives.', 'model_ids': ['qwen/qwen3.7-max', 'deepseek/deepseek-v4-pro', 'google/gemini-2.5-flash']}` |
| `methods_protocol_section_present` | True | `` |
| `methods_data_metrics_section_present` | True | `` |
| `results_section_present` | True | `` |
| `discussion_section_present` | True | `` |
| `threats_section_present` | True | `` |
| `old_invalid_setting_not_reintroduced` | True | `` |
| `autonomous_correctness_claim_negated` | True | `` |
| `llm_superiority_not_claimed` | True | `` |
| `llm_outperform_baseline_phrase_only_negated` | True | `` |

## Reviewer Risks

| risk | status | mitigation |
|---|---|---|
| Contribution may still be read as measurement-only rather than algorithmic. | `bounded_accept_risk` | Manuscript now states the contribution as a protocol and evidence chain, not a new repair algorithm. |
| Baseline completeness can be challenged. | `bounded_accept_risk` | Rule-only is reported as the completed deterministic baseline; majority and separate E0/no-tool verifier are explicitly not completed. |
| Small cohort creates wide uncertainty intervals. | `bounded_accept_risk` | Wilson 95% CIs are now shown for E6 conditions and tool-contestation opportunity-set rates, and are used to avoid superiority claims. |
| References may need venue-specific BibTeX cleanup. | `formatting_remaining` | Citation keys and reference support records are present; final conversion remains a formatting task. |

## Verdict

- readiness: `stronger_than_previous_draft_but_still_needs_final_formatting`
- reason: The v0.3 draft now contains field-specific citations, explicit deterministic baseline boundaries, and uncertainty intervals, while avoiding unsupported autonomous-verifier and LLM-superiority claims.
