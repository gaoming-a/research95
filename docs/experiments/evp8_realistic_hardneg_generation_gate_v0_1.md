# EVP-8 Realistic Hard-Negative Generation Gate v0.1

Date: 2026-06-30

This raw-output-free analysis joins validation records with visible-test
outcomes. It does not store patch text, prompt text, or raw model responses.

- status: `passed`
- candidates: 54
- ready for verifier API: `False`

## Classification Counts

- `visible_fail_hidden_fail`: 19
- `visible_pass_hidden_fail`: 26
- `visible_pass_hidden_pass`: 9

## Hard-Negative Gate

- required property: `patch_applied && declared_visible_tests_passed && hidden_oracle_failed`
- visible-pass/hidden-fail count: 26
- projects: `PySnooper`, `cookiecutter`
- tasks: `bugsinpy_PySnooper_3`, `bugsinpy_cookiecutter_2`, `bugsinpy_cookiecutter_3`
- minimum count: 30
- minimum projects: 3
- gate passed: `False`

## By Task

| task | visible-pass hidden-fail | visible-pass hidden-pass | visible-fail hidden-fail | visible-fail hidden-pass |
| --- | ---: | ---: | ---: | ---: |
| `bugsinpy_PySnooper_1` | 0 | 9 | 0 | 0 |
| `bugsinpy_PySnooper_3` | 9 | 0 | 0 | 0 |
| `bugsinpy_cookiecutter_1` | 0 | 0 | 9 | 0 |
| `bugsinpy_cookiecutter_2` | 9 | 0 | 0 | 0 |
| `bugsinpy_cookiecutter_3` | 8 | 0 | 1 | 0 |
| `bugsinpy_tqdm_9` | 0 | 0 | 9 | 0 |

## Checks

- api_call_not_attempted_by_analysis: passed (False)
- raw_model_outputs_not_read: passed (False)
- patch_text_not_stored: passed (False)
- generation_audit_passed: passed (passed)
- visible_tests_completed: passed ({'completed': 54})
- validation_count_matches_visible_count: passed ({'validation': 54, 'visible': 54})
- visible_coverage_complete: passed ({'missing': [], 'extra': []})
- hard_negative_min_count_gate: failed (26)
- hard_negative_min_project_gate: failed (['PySnooper', 'cookiecutter'])

## Next Step

Add a supplement focused on missing project diversity and at least four more visible-pass/hidden-fail candidates.
