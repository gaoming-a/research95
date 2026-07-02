# Final Manuscript Claim Map v0.1

Date: 2026-07-03

- status: `passed`
- target: `stable CCF-C submission`

## One-Sentence Argument

In candidate patch verification, we show that evidence visibility shapes LLM merge-gate risk behavior using frozen hidden-evaluator evidence packets, supported by five-model decision-pattern synthesis, no-verdict and tool-contestation ablations, and a realistic source-acquisition gate audit, with claims bounded away from autonomous correctness verification.

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
| `C1` | Evidence visibility changes LLM merge-gate behavior on a frozen candidate-patch packet set. | `supported` | evp8_five_model_synthesis_v0_1, final_experiment_setting_validity_audit_v0_1 | Results: Evidence visibility changes merge-gate decisions | Descriptive decision-pattern result, not a claim of better correctness. |
| `C2` | The observed evidence effect is model-dependent and non-monotonic. | `supported` | per-level five-model decision counts | Results: Model-dependent, non-monotonic patterns | Do not rank evidence levels as universally better. |
| `C3` | Accept-aware protocol repairs are necessary to avoid over-interpreting earlier zero-accept artifacts. | `supported_as_setting_repair` | v0_2_accept_aware_synthesis, v0_3_qwen_label_conditioned_summary | Methods/Validity: Protocol repair and label-conditioned analysis | Historical v0.1 zero-accept behavior should remain protocol history. |
| `C4` | Verdict-like tool summaries can anchor model decisions; removing or contesting them changes behavior. | `supported_qualified` | evp8_e6_no_verdict_ablation_comparison, evp8_hard_tool_contestation_result_audit | Results: Verdict dependence and contestation | Measured as policy behavior, not semantic proof. |
| `C5` | Tool-contestation primarily improves safe handling through escalation rather than strict correction. | `supported` | EVP-8-HARD tool-contestation audit | Results: Tool-contestation as risk triage | Strict correction remains separate and limited. |
| `C6` | The fresh realistic hard-negative branch is a source-acquisition negative result, not a verifier-ready main experiment. | `supported_negative_boundary` | evp8_realistic_hardneg_combined_generation_gate_with_full_file_v0_1 | Threats/Discussion: Realistic hard-negative acquisition | Do not use it as three-project verifier evidence. |

## Forbidden Claims

- LLMs are reliable autonomous patch correctness verifiers.
- More visible evidence monotonically improves correctness verification.
- Escalation is equivalent to strict correction.
- The fresh realistic hard-negative branch is verifier-ready across three projects.
- The controlled EVP-8 or EVP-8-HARD cohorts prove broad external validity for real agent patch distributions.

## Figure Plan

| figure | title | conclusion | status |
| --- | --- | --- | --- |
| Fig. 1 | Hidden-evaluator evidence-visibility protocol | Model-visible evidence and evaluator-only labels are separated until post-decision analysis. | `planned_requires_backend` |
| Fig. 2 | Five-model evidence-level decision patterns | Escalation/rejection patterns vary by model and are non-monotonic across E0-E6. | `planned_requires_backend` |
| Fig. 3 | Claim boundary and setting-validity map | Supported findings are bounded by leakage controls, protocol repairs, and remaining external-validity threats. | `planned_requires_backend` |

## Checks

| check | passed | detail |
| --- | ---: | --- |
| `validity_audit_passed_with_bounded_claims` | true | `passed_with_bounded_claims` |
| `five_model_synthesis_passed` | true | `passed` |
| `no_verdict_comparison_checks_present` | true | `13` |
| `hard_tool_contestation_audit_passed` | true | `passed` |
| `realistic_gate_not_verifier_ready` | true | `{'minimum_count': 30, 'minimum_projects': 3, 'passed': False, 'required_property': 'patch_applied && declared_visible_tests_passed && hidden_oracle_failed', 'visible_pass_hidden_fail_count': 26, 'visible_pass_hidden_fail_projects': ['PySnooper', 'cookiecutter'], 'visible_pass_hidden_fail_tasks': ['bugsinpy_PySnooper_3', 'bugsinpy_cookiecutter_2', 'bugsinpy_cookiecutter_3']}` |
