# EVP-8 Realistic Hard-Negative Generation Gate v0.1

Date: 2026-06-30

This raw-output-free analysis joins validation records with visible-test
outcomes. It does not store patch text, prompt text, or raw model responses.

- status: `passed`
- candidates: 12
- ready for verifier API: `False`

## Classification Counts

- `visible_fail_hidden_fail`: 3
- `visible_pass_hidden_pass`: 9

## Hard-Negative Gate

- required property: `patch_applied && declared_visible_tests_passed && hidden_oracle_failed`
- visible-pass/hidden-fail count: 0
- projects: none
- tasks: none
- minimum count: 4
- minimum projects: 1
- gate passed: `False`

## By Task

| task | visible-pass hidden-fail | visible-pass hidden-pass | visible-fail hidden-fail | visible-fail hidden-pass |
| --- | ---: | ---: | ---: | ---: |
| `bugsinpy_httpie_1` | 0 | 0 | 3 | 0 |
| `bugsinpy_httpie_2` | 0 | 3 | 0 | 0 |
| `bugsinpy_httpie_3` | 0 | 3 | 0 | 0 |
| `bugsinpy_httpie_4` | 0 | 3 | 0 | 0 |

## Checks

- api_call_not_attempted_by_analysis: passed (False)
- raw_model_outputs_not_read: passed (False)
- patch_text_not_stored: passed (False)
- generation_audit_passed: passed (passed)
- visible_tests_completed: passed ({'completed': 12})
- validation_count_matches_visible_count: passed ({'validation': 12, 'visible': 12})
- visible_coverage_complete: passed ({'missing': [], 'extra': []})
- hard_negative_min_count_gate: failed (0)
- hard_negative_min_project_gate: failed ([])

## Next Step

Add a supplement focused on missing project diversity and at least four more visible-pass/hidden-fail candidates.
