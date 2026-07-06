# EVP-8 hard-negative stress-test packet v0.1

Status: `blocked_needs_more_cases_and_third_project`

## Current Gate

- visible-pass/hidden-fail cases: `26` / `30`
- projects: `PySnooper`, `cookiecutter`
- missing cases: `4`
- missing projects: `1`
- ready for verifier API: `false`

## Selected Next Source

- project: `luigi`
- tasks: `bugsinpy_luigi_3`, `bugsinpy_luigi_4`
- new visible-pass/hidden-fail cases needed: `4`
- required protocol change: Freeze a separate source-acquisition/materialization protocol before generation. Do not silently retry the exact search/replace edit-plan interface.

## Planned Stress Matrix After Gate Passes

| axis | values |
| --- | --- |
| models | `qwen/qwen3.7-max`, `deepseek/deepseek-v4-pro`, `google/gemini-2.5-flash` |
| conditions | `rule_only_visible_tool_baseline`, `current_merge_gate_prompt`, `e6_no_verdict_prompt`, `coverage_contestation_prompt` |
| metrics | `strict_reject`, `safe_escalation`, `repeated_false_accept`, `correct_recall_loss`, `coverage_challenge_rate`, `verdict_dependence` |

## Checks

| check | passed | detail |
| --- | --- | --- |
| `api_call_not_attempted` | true | `false` |
| `raw_model_outputs_not_read` | true | `false` |
| `prompt_text_not_read` | true | `false` |
| `patch_text_not_read` | true | `false` |
| `current_hard_negative_case_gate_passed` | false | `26` |
| `current_hard_negative_project_gate_passed` | false | `["PySnooper", "cookiecutter"]` |
| `verifier_api_blocked_until_gate_passes` | true | `false` |
| `third_project_source_selected` | true | `{"minimum_success_gate_after_future_validation": {"new_project_needed": "luigi", "new_visible_pass_hidden_fail_cases_needed": 4, "required_property": "patch_applied && declared_visible_tests_passed && hidden_oracle_failed"}, "project": "luigi", "required_protocol_change": "Freeze a separate source-acquisition/materialization protocol before generation. Do not silently retry the exact search/replace edit-plan interface.", "selection_status": "selected_for_new_source_acquisition_protocol", "tasks": ["bugsinpy_luigi_3", "bugsinpy_luigi_4"], "why_selected": ["The current gate needs a third project; existing visible-pass/hidden-fail projects are only PySnooper and cookiecutter.", "Luigi is not already counted as a gate-passing project, so it can add genuine project diversity if validation succeeds.", "The previous Luigi supplement failed before candidate construction, so its blocker is materialization/interface design rather than an observed visible-pass/hidden-fail yield failure.", "Both selected Luigi tasks exist in tracked source-bug definitions, enabling a no-API protocol to be written before any generation call."]}` |

## Forbidden Next Work

- run Qwen, DeepSeek, or Gemini hard-negative verifier API while ready_for_verifier_api is false
- treat the current 26-case two-project branch as the stress-test main cohort
- count escalation as strict rejection
- merge stress-test results into the main E0-E6 table without labeling the prompt condition
