# EVP-8 Realistic Hard-Negative Combined Generation Gate v0.1

Date: 2026-06-30

This combines raw-output-free gate analyses. It does not read raw
responses, prompt text, or patch text.

- status: `passed`
- candidates: 78
- visible-pass/hidden-fail: 26
- projects: `PySnooper`, `cookiecutter`
- gate passed: `False`
- ready for verifier API: `False`

## Classification Counts

- `visible_fail_hidden_fail`: 25
- `visible_pass_hidden_fail`: 26
- `visible_pass_hidden_pass`: 27

## By Project

| project | visible-pass hidden-fail | visible-pass hidden-pass | visible-fail hidden-fail | visible-fail hidden-pass |
| --- | ---: | ---: | ---: | ---: |
| `PySnooper` | 9 | 9 | 0 | 0 |
| `cookiecutter` | 17 | 0 | 10 | 0 |
| `httpie` | 0 | 18 | 6 | 0 |
| `tqdm` | 0 | 0 | 9 | 0 |

## Checks

- api_call_not_attempted_by_combiner: passed (False)
- raw_model_outputs_not_read: passed (False)
- patch_text_not_stored: passed (False)
- input_gate_analyses_passed: passed (['passed', 'passed', 'passed'])
- hard_negative_min_count_gate: failed (26)
- hard_negative_min_project_gate: failed (['PySnooper', 'cookiecutter'])

## Next Step

Do not run verifier API. Redesign source strategy for a third project or revise the paper claim to report a two-project hard-negative cohort.
