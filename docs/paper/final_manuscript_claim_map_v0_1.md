# Current Final Manuscript Claim Map

Date: 2026-07-04

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
| reference policy | a deterministic policy calculated for baseline orientation rather than implemented as a verifier result | Use for always-escalate, always-reject, and always-accept. |
| rule-only visible-tool baseline | the completed deterministic E6 baseline using visible tool evidence | Use as the current completed deterministic baseline. |

## Claim-Evidence Map

| id | claim | status | evidence | paper location | boundary |
| --- | --- | --- | --- | --- | --- |
| `C1` | EVP-8 defines a valid hidden-evaluator evidence boundary for candidate patch verification. | `supported` | evp8_protocol_v0_3_qwen_first, final_experiment_setting_validity_audit | Methods: Evidence-visibility protocol | Protocol validity, not model effectiveness. |
| `C2` | In the Qwen v0.3 accept-aware run, visible executable and tool evidence changed correct-patch acceptance while introducing bounded false-accept risk. | `supported_qwen_only` | v0_2_accept_aware_synthesis, v0_3_qwen_label_conditioned_summary | Results: Accept-aware label-conditioned behavior | Qwen-only v0.3 descriptive result; not a five-model effectiveness claim or final evidence-level ranking. |
| `C3` | Verdict-like tool summaries can anchor model decisions; removing or contesting them changes behavior. | `supported_qualified` | evp8_e6_no_verdict_ablation_comparison, evp8_hard_tool_contestation_result_audit | Results: Verdict dependence and contestation | Measured as policy behavior, not semantic proof. |
| `C4` | Tool-contestation primarily improves safe handling through escalation rather than strict correction. | `supported` | EVP-8-HARD tool-contestation audit | Results: Tool-contestation as risk triage | Strict correction remains separate and limited. |
| `C5` | The fresh realistic hard-negative branch is a source-acquisition negative result, not a verifier-ready main experiment. | `supported_negative_boundary` | realistic_hardneg_generation_gate | Threats/Discussion: Realistic hard-negative acquisition | Do not use it as three-project verifier evidence. |

## Citation Support

| segment | paper location | claim | citation keys | boundary |
| --- | --- | --- | --- | --- |
| `S1` | Introduction / Related Work | Visible plausibility and test passing do not guarantee patch correctness. | `qi_issta_2015_patch_plausibility; legoues_icse_2012_genprog; just_issta_2014_defects4j` | Motivates the task; does not prove EVP-8 effectiveness. |
| `S2` | Related Work | APR and bug-fix studies commonly use controlled datasets and test-based evaluation. | `just_issta_2014_defects4j; legoues_icse_2012_genprog; tufano_icse_2019_bugfix_nmt` | Positions the setting; does not imply the same task distribution. |
| `S3` | Related Work | LLMs have been studied for repair and code editing, but verifier behavior is a separate decision problem. | `xia_zhang_icse_2023_llm_apr; tufano_icse_2019_bugfix_nmt` | Background only; not autonomous verifier evidence. |
| `S4` | Related Work / Method | Code review is a socio-technical merge-gate process rather than a pure test outcome. | `bacchelli_bird_icse_2013_code_review` | Supports merge-gate framing; not an industrial deployment claim. |
| `S5` | Method | The accept/reject/escalate output space is related to reject-option and selective-classification work. | `chow_tit_1970_reject_option; geifman_el_yaniv_2017_selective_classification` | Conceptual support; no calibrated probability claim. |
| `S6` | Method / Threats | Evaluator-only labels should remain separate because software testing has an oracle problem. | `barr_tse_2015_oracle_problem` | Supports hidden-evaluator separation and validity limits. |
| `S7` | Discussion | LLM-as-judge evaluations require bounded claims and controlled protocols. | `zheng_neurips_2023_llm_judge` | General evaluation caution; not direct patch-verifier transfer. |
| `S8` | Discussion | Automation outputs can induce misuse or over-reliance, motivating explicit evidence-boundary reporting. | `parasuraman_riley_1997_automation` | Supports reliance risk; not a patch-specific empirical result. |

## Reference Support Records

| key | reference |
| --- | --- |
| `qi_issta_2015_patch_plausibility` | Zichao Qi, Fan Long, Sara Achour, and Martin Rinard. "An Analysis of Patch Plausibility and Correctness for Generate-and-Validate Patch Generation Systems." ISSTA 2015. DOI: 10.1145/2771783.2771791. |
| `legoues_icse_2012_genprog` | Claire Le Goues, ThanhVu Nguyen, Stephanie Forrest, and Westley Weimer. "A Systematic Study of Automated Program Repair: Fixing 55 out of 105 Bugs for $8 Each." ICSE 2012. DOI: 10.1109/ICSE.2012.6227211. |
| `just_issta_2014_defects4j` | Rene Just, Darioush Jalali, and Michael D. Ernst. "Defects4J: A Database of Existing Faults to Enable Controlled Testing Studies for Java Programs." ISSTA 2014. DOI: 10.1145/2610384.2628055. |
| `barr_tse_2015_oracle_problem` | Earl T. Barr, Mark Harman, Phil McMinn, Muzammil Shahbaz, and Shin Yoo. "The Oracle Problem in Software Testing: A Survey." IEEE TSE 2015. DOI: 10.1109/TSE.2014.2372785. |
| `xia_zhang_icse_2023_llm_apr` | Chunqiu Steven Xia and Lingming Zhang. "Automated Program Repair in the Era of Large Pre-trained Language Models." ICSE 2023. DOI: 10.1109/ICSE48619.2023.00129. |
| `tufano_icse_2019_bugfix_nmt` | Michele Tufano, Cody Watson, Gabriele Bavota, Massimiliano Di Penta, Martin White, and Denys Poshyvanyk. "An Empirical Investigation into Learning Bug-Fixing Patches in the Wild via Neural Machine Translation." ICSE 2019. DOI: 10.1109/ICSE.2019.00064. |
| `bacchelli_bird_icse_2013_code_review` | Alberto Bacchelli and Christian Bird. "Expectations, Outcomes, and Challenges of Modern Code Review." ICSE 2013. DOI: 10.1109/ICSE.2013.6606617. |
| `chow_tit_1970_reject_option` | C. K. Chow. "On Optimum Recognition Error and Reject Tradeoff." IEEE Transactions on Information Theory 1970. DOI: 10.1109/TIT.1970.1054406. |
| `geifman_el_yaniv_2017_selective_classification` | Yonatan Geifman and Ran El-Yaniv. "Selective Classification for Deep Neural Networks." arXiv:1705.08500, 2017. |
| `zheng_neurips_2023_llm_judge` | Lianmin Zheng et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." NeurIPS 2023. arXiv:2306.05685. |
| `parasuraman_riley_1997_automation` | Raja Parasuraman and Victor Riley. "Humans and Automation: Use, Misuse, Disuse, Abuse." Human Factors 1997. DOI: 10.1518/001872097778543886. |

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

## Baseline Policy Boundaries

| policy | status | accept | reject | escalate | role |
| --- | --- | ---: | ---: | ---: | --- |
| `always_escalate` | `calculable_from_label_totals` | 0 | 0 | 98 | conservative abstention reference, not a useful verifier. |
| `always_reject` | `calculable_from_label_totals` | 0 | 98 | 0 | safety-heavy lower-bound reference exposing recall collapse. |
| `always_accept` | `calculable_from_label_totals` | 98 | 0 | 0 | unsafe throughput reference exposing base-rate risk. |
| `uniform_random_three_way_expected` | `calculable_expected_reference_from_label_totals` | 32.666666666666664 | 32.666666666666664 | 32.666666666666664 | sanity-check reference for the decision space, not a completed verifier or a reported stochastic experiment. |
| `rule_only_visible_tool` | `completed_existing_tracked_result` | 25 | 73 | 0 | main deterministic baseline for E6 full/no-verdict comparison. |

## Phase A Uncertainty Summary

| condition | accepted precision 95% CI | correct recall 95% CI | false accept rate 95% CI | escalation rate 95% CI |
| --- | ---: | ---: | ---: | ---: |
| rule-only | 80.00% [60.87%, 91.14%] | 95.24% [77.33%, 99.15%] | 6.49% [2.81%, 14.32%] | 0.00% [0.00%, 3.77%] |
| qwen/qwen3.7-max E6-full | 83.33% [64.15%, 93.32%] | 95.24% [77.33%, 99.15%] | 5.19% [2.04%, 12.61%] | 0.00% [0.00%, 3.77%] |
| qwen/qwen3.7-max E6-no-verdict | 82.61% [62.86%, 93.02%] | 90.48% [71.09%, 97.35%] | 5.19% [2.04%, 12.61%] | 1.02% [0.18%, 5.56%] |
| deepseek/deepseek-v4-pro E6-full | 82.61% [62.86%, 93.02%] | 90.48% [71.09%, 97.35%] | 5.19% [2.04%, 12.61%] | 0.00% [0.00%, 3.77%] |
| deepseek/deepseek-v4-pro E6-no-verdict | 100.00% [74.12%, 100.00%] | 52.38% [32.37%, 71.66%] | 0.00% [0.00%, 4.75%] | 14.29% [8.70%, 22.56%] |

## Tool-Contestation Opportunity Uncertainty

| model | opportunity cases | safe handling 95% CI | strict correction 95% CI | repeated accept 95% CI |
| --- | ---: | ---: | ---: | ---: |
| deepseek/deepseek-v4-pro | 9 | 100.00% [70.09%, 100.00%] | 0.00% [0.00%, 29.91%] | 0.00% [0.00%, 29.91%] |
| qwen/qwen3.7-max | 9 | 88.89% [56.50%, 98.01%] | 0.00% [0.00%, 29.91%] | 11.11% [1.99%, 43.50%] |

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
| `baseline_feasibility_audit_passed` | true | `passed` |
| `citation_support_bank_present` | true | `docs\paper\ccfc_citation_support_bank_v0_1.md` |
