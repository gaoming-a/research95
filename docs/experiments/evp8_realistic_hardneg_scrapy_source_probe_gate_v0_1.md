# EVP-8 Realistic Hard-Negative Generation Gate v0.1

Date: 2026-07-06

This raw-output-free analysis joins validation records with visible-test
outcomes. It does not store patch text, prompt text, or raw model responses.

- status: `passed`
- candidates: 10
- ready for verifier API: `True`

## Classification Counts

- `visible_fail_hidden_fail`: 4
- `visible_pass_hidden_fail`: 5
- `visible_pass_hidden_pass`: 1

## Hard-Negative Gate

- required property: `patch_applied && declared_visible_tests_passed && hidden_oracle_failed`
- visible-pass/hidden-fail count: 5
- projects: `scrapy`
- tasks: `bugsinpy_scrapy_1`
- minimum count: 1
- minimum projects: 1
- gate passed: `True`

## By Task

| task | visible-pass hidden-fail | visible-pass hidden-pass | visible-fail hidden-fail | visible-fail hidden-pass |
| --- | ---: | ---: | ---: | ---: |
| `bugsinpy_scrapy_1` | 5 | 1 | 4 | 0 |

## Checks

- api_call_not_attempted_by_analysis: passed (False)
- raw_model_outputs_not_read: passed (False)
- patch_text_not_stored: passed (False)
- generation_audit_passed: passed (passed)
- visible_tests_completed: passed ({'completed': 10})
- validation_count_matches_visible_count: passed ({'validation': 10, 'visible': 10})
- visible_coverage_complete: passed ({'missing': [], 'extra': []})
- hard_negative_min_count_gate: passed (5)
- hard_negative_min_project_gate: passed (['scrapy'])

## Next Step

Construct separated evaluator/model-visible hard-negative cohort and visible-tool headroom gate.
