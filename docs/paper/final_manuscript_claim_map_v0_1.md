# Current Final Manuscript Claim Map

Date: 2026-07-03

- status: `passed`
- target: `stable CCF-C submission`

## One-Sentence Argument

In candidate patch verification, we show that a hidden-evaluator evidence-visibility protocol can measure evidence-conditioned LLM merge-gate behavior, supported by the accept-aware Qwen v0.3 label-conditioned analysis, E6 rule-only/no-verdict ablations, tool-contestation audits, and a realistic source-acquisition gate audit.

## Terminology Ledger

| canonical term | definition | decision |
| --- | --- | --- |
| candidate patch verification | the task of deciding accept/reject/escalate for a proposed patch under visible evidence | Use as the manuscript's central task name. |
| evidence visibility | the evidence fields available to the verifier at review time | Use as the main explanatory variable. |
| hidden evaluator | the evaluator-only label and oracle layer joined after model decisions | Spell out on first use; emphasize non-visibility to models. |
| merge-gate decision | one of accept, reject, or escalate | Use instead of generic review decision when discussing outputs. |
| strict correction | rejecting a known tool false accept | Keep separate from escalation. |
| safe handling | rejecting or escalating a known tool false accept | Use only when escalation is explicitly treated as human-review routing. |

## Claim-Evidence Map

| id | claim | status | evidence | paper location | boundary |
| --- | --- | --- | --- | --- | --- |
| `C1` | EVP-8 defines a valid hidden-evaluator evidence boundary for candidate patch verification. | `supported` | evp8_protocol_v0_3_qwen_first, final_experiment_setting_validity_audit | Methods: Evidence-visibility protocol | Protocol validity, not model effectiveness. |
| `C2` | In the Qwen v0.3 accept-aware run, visible executable and tool evidence changed correct-patch acceptance while introducing bounded false-accept risk. | `supported_qwen_only` | v0_2_accept_aware_synthesis, v0_3_qwen_label_conditioned_summary | Results: Accept-aware label-conditioned behavior | Qwen-only v0.3 descriptive result; not a five-model effectiveness claim or final evidence-level ranking. |
| `C3` | Verdict-like tool summaries can anchor model decisions; removing or contesting them changes behavior. | `supported_qualified` | evp8_e6_no_verdict_ablation_comparison, evp8_hard_tool_contestation_result_audit | Results: Verdict dependence and contestation | Measured as policy behavior, not semantic proof. |
| `C4` | Tool-contestation primarily improves safe handling through escalation rather than strict correction. | `supported` | EVP-8-HARD tool-contestation audit | Results: Tool-contestation as risk triage | Strict correction remains separate and limited. |
| `C5` | The fresh realistic hard-negative branch is a source-acquisition negative result, not a verifier-ready main experiment. | `supported_negative_boundary` | realistic_hardneg_generation_gate | Threats/Discussion: Realistic hard-negative acquisition | Do not use it as three-project verifier evidence. |

## Evidence Ladder

| level | name | added evidence class | model-visible field groups |
| --- | --- | --- | --- |
| E0 | issue_patch_seed | issue_patch_seed | issue_patch_seed |
| E1 | structured_patch_surface | patch_surface_map | issue_patch_seed, patch_surface_map |
| E2 | patch_apply_and_static_slots | patch_application_static_status | issue_patch_seed, patch_surface_map, patch_application_static_status |
| E3 | visible_fail_to_pass_tests | visible_fail_to_pass_test_evidence | issue_patch_seed, patch_surface_map, patch_application_static_status, visible_fail_to_pass_test_evidence |
| E4 | visible_pass_to_pass_regression_tests | visible_pass_to_pass_regression_evidence | issue_patch_seed, patch_surface_map, patch_application_static_status, visible_fail_to_pass_test_evidence, visible_pass_to_pass_regression_evidence |
| E5 | broader_visible_tool_diagnostics | broader_visible_tool_diagnostics | issue_patch_seed, patch_surface_map, patch_application_static_status, visible_fail_to_pass_test_evidence, visible_pass_to_pass_regression_evidence, broader_visible_tool_diagnostics |
| E6 | deterministic_visible_tool_summary | deterministic_visible_merge_gate_summary | issue_patch_seed, patch_surface_map, patch_application_static_status, visible_fail_to_pass_test_evidence, visible_pass_to_pass_regression_evidence, broader_visible_tool_diagnostics, deterministic_visible_merge_gate_summary |

## Qwen v0.3 Label-Conditioned Metrics

| level | accept | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 75.51% |
| E1 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 75.51% |
| E2 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 74.49% |
| E3 | 20 | 17 | 3 | 85.00% | 80.95% | 3.90% | 4.08% |
| E4 | 21 | 18 | 3 | 85.71% | 85.71% | 3.90% | 2.04% |
| E5 | 21 | 18 | 3 | 85.71% | 85.71% | 3.90% | 3.06% |
| E6 | 24 | 20 | 4 | 83.33% | 95.24% | 5.19% | 0.00% |

## E6 Baseline And No-Verdict Metrics

| condition | accept | reject | escalate | accepted precision | correct recall | false accept rate | escalation rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| rule-only | 25 | 73 | 0 | 80.00% | 95.24% | 6.49% | 0.00% |
| deepseek/deepseek-v4-pro E6-full | 23 | 75 | 0 | 82.61% | 90.48% | 5.19% | 0.00% |
| deepseek/deepseek-v4-pro E6-no-verdict | 11 | 73 | 14 | 100.00% | 52.38% | 0.00% | 14.29% |
| qwen/qwen3.7-max E6-full | 24 | 74 | 0 | 83.33% | 95.24% | 5.19% | 0.00% |
| qwen/qwen3.7-max E6-no-verdict | 23 | 74 | 1 | 82.61% | 90.48% | 5.19% | 1.02% |

## Forbidden Claims

- LLMs are reliable autonomous patch correctness verifiers.
- More visible evidence monotonically improves correctness verification.
- Escalation is equivalent to strict correction.
- The fresh realistic hard-negative branch is verifier-ready across three projects.
- The controlled EVP-8 or EVP-8-HARD cohorts prove broad external validity for real agent patch distributions.

## Figure Plan

| figure | title | conclusion | status |
| --- | --- | --- | --- |
| Fig. 1 | Hidden-evaluator evidence-visibility protocol | Model-visible evidence and evaluator-only labels are separated until post-decision analysis. | `generated_python` |
| Fig. 2 | Accept-aware and no-verdict metric evidence | Repaired evidence unlocks Qwen correct-patch acceptance while E6 ablations expose verdict-dependent risk tradeoffs. | `generated_python` |
| Fig. 3 | Claim boundary and setting-validity map | Supported findings are bounded by leakage controls, protocol repairs, and remaining external-validity threats. | `generated_python` |

## Checks

| check | passed | detail |
| --- | ---: | --- |
| `validity_audit_passed_with_bounded_claims` | true | `passed_with_bounded_claims` |
| `five_model_synthesis_passed` | true | `passed` |
| `no_verdict_comparison_checks_present` | true | `13` |
| `hard_tool_contestation_audit_passed` | true | `passed` |
| `realistic_gate_not_verifier_ready` | true | `{'minimum_count': 30, 'minimum_projects': 3, 'passed': False, 'required_property': 'patch_applied && declared_visible_tests_passed && hidden_oracle_failed', 'visible_pass_hidden_fail_count': 26, 'visible_pass_hidden_fail_projects': ['PySnooper', 'cookiecutter'], 'visible_pass_hidden_fail_tasks': ['bugsinpy_PySnooper_3', 'bugsinpy_cookiecutter_2', 'bugsinpy_cookiecutter_3']}` |
| `qwen_label_conditioned_checks_passed` | true | `9` |
| `phase_a_analysis_checks_passed` | true | `7` |
