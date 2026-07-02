# EVP-8 Realistic Hard-Negative Third-Project Source Selection Packet v0.1

Date: 2026-07-02

This is a no-API source-selection packet. It does not call model APIs,
authorize generation, authorize verifier APIs, read raw model outputs,
read prompt text, or read patch text.

## Status

- packet status: `passed`
- selected project: `luigi`
- selected tasks: `bugsinpy_luigi_3`, `bugsinpy_luigi_4`
- generation API authorized: `False`
- verifier API authorized: `False`

## Current Gate

- visible-pass/hidden-fail cases: `26` / `30`
- visible-pass/hidden-fail projects: `PySnooper`, `cookiecutter`
- minimum projects: `3`
- ready for verifier API: `False`

## Selection Rationale

- The current gate needs a third project; existing visible-pass/hidden-fail projects are only PySnooper and cookiecutter.
- Luigi is not already counted as a gate-passing project, so it can add genuine project diversity if validation succeeds.
- The previous Luigi supplement failed before candidate construction, so its blocker is materialization/interface design rather than an observed visible-pass/hidden-fail yield failure.
- Both selected Luigi tasks exist in tracked source-bug definitions, enabling a no-API protocol to be written before any generation call.

Required protocol change:

Freeze a separate source-acquisition/materialization protocol before generation. Do not silently retry the exact search/replace edit-plan interface.

Minimum future validation success gate:

- new visible-pass/hidden-fail cases needed: `4`
- new project needed: `luigi`
- required property: `patch_applied && declared_visible_tests_passed && hidden_oracle_failed`

## Rejected Direct Sources

| project | observed counts | decision reason |
| --- | --- | --- |
| `httpie` | `{'visible_fail_hidden_fail': 6, 'visible_pass_hidden_pass': 18}` | observed hidden-failing candidates failed visible tests; direct repeats do not target visible-pass/hidden-fail. |
| `thefuck` | `{'visible_pass_hidden_pass': 12}` | observed candidates were visible-pass/hidden-pass; this project behaved as correct-like under the current setup. |
| `tqdm` | `{'visible_fail_hidden_fail': 9}` | observed wrong candidates failed visible tests, so the current source does not create false-accept opportunity cases. |
| `youtube-dl` | `{'visible_pass_hidden_pass': 4}` | one supplement failed before candidate construction and the later full-file attempt produced visible-pass/hidden-pass cases. |

## Checks

| check | passed | detail |
| --- | ---: | --- |
| `api_call_not_attempted` | true | `False` |
| `raw_model_outputs_not_read` | true | `False` |
| `prompt_text_not_read` | true | `False` |
| `patch_text_not_read` | true | `False` |
| `combined_gate_passed_as_analysis` | true | `passed` |
| `current_gate_not_ready_for_verifier_api` | true | `False` |
| `current_hard_negative_gate_failed` | true | `False` |
| `selected_project_not_already_gate_passing` | true | `['PySnooper', 'cookiecutter']` |
| `selected_tasks_in_source_bug_definitions` | true | `['bugsinpy_luigi_3', 'bugsinpy_luigi_4']` |
| `selected_project_previous_failure_before_candidate_construction` | true | `generation stopped before candidate construction due to exact find-snippet apply failure` |
| `source_target_matrix_does_not_already_solve_third_project` | true | `{'PySnooper': 18, 'cookiecutter': 27, 'tqdm': 9}` |

## Allowed Next Work

- write a no-API Luigi source-acquisition/materialization protocol
- define dry-run materialization checks and validation commands without calling APIs
- run only protocol/check-only gates before asking for any generation API authorization
- after any future generated candidates, rerun validation and the combined hard-negative gate

## Forbidden Actions

- run Qwen or DeepSeek verifier API while ready_for_verifier_api is false
- run generation API from this packet alone
- retry the same exact search/replace interface for Luigi without a new protocol
- count Luigi task-file smoke artifacts as a passed realistic third-project gate
- reuse failed third-project attempts as successful verifier-ready evidence

## Decision

Proceed only to a no-API Luigi source-acquisition/materialization protocol.
Do not run verifier APIs, and do not run generation APIs from this packet alone.
