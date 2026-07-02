# EVP-8 Realistic Hard-Negative Uplift Packet v0.1

Date: 2026-07-02

This is a no-API planning gate. It reads tracked aggregate gate files only
and does not call model APIs, read raw model responses, read prompt text,
or read patch text.

## Status

- status: `blocked_needs_more_cases_and_third_project`
- passed as boundary packet: `True`
- ready for verifier API: `False`

## Current Gate Gap

- required property: `patch_applied && declared_visible_tests_passed && hidden_oracle_failed`
- visible-pass/hidden-fail cases: `26` / `30`
- missing cases: `4`
- projects: `PySnooper, cookiecutter`
- missing project count: `1`

## Checks

| check | passed | detail |
|---|---:|---|
| `api_call_not_attempted` | true | `false` |
| `raw_model_outputs_not_read` | true | `false` |
| `prompt_text_not_read` | true | `false` |
| `patch_text_not_read` | true | `false` |
| `input_gate_present` | true | `"data/protocols/evp8_realistic_hardneg_combined_generation_gate_with_full_file_v0_1.json"` |
| `input_gate_passed_as_analysis` | true | `"passed"` |
| `hard_negative_count_gate_passed` | false | `26` |
| `hard_negative_project_gate_passed` | false | `["PySnooper", "cookiecutter"]` |
| `verifier_api_still_blocked` | true | `false` |

## Allowed Next Work

- write a new no-API third-project source-selection packet
- freeze a source-acquisition protocol before any generation API
- generate or validate candidates only after prompt/schema/leakage gates pass
- rerun the combined hard-negative gate after validation

## Forbidden Next Work

- run Qwen or DeepSeek verifier API while ready_for_verifier_api is false
- merge this branch into the main verifier experiment as three-project ready
- count escalation as strict correctness correction
- reuse failed third-project attempts as successful verifier-ready evidence

## Paper Boundary

- current use: two-project source-acquisition / gate-readiness negative result
- uplift condition: Upgrade to a verifier-ready realistic supplement only after at least 30 visible-pass/hidden-fail cases across at least 3 projects pass the tracked gate.
- if gate still fails: keep the branch as a negative result and do not run verifier APIs
