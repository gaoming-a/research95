# EVP-8 Realistic Hard-Negative Combined Generation Gate v0.1

Date: 2026-07-06

This combines raw-output-free gate analyses. It does not read raw
responses, prompt text, or patch text.

- status: `passed`
- candidates: 104
- visible-pass/hidden-fail: 31
- projects: `PySnooper`, `cookiecutter`, `scrapy`
- gate passed: `True`
- ready for verifier API: `True`

## Classification Counts

- `visible_fail_hidden_fail`: 29
- `visible_pass_hidden_fail`: 31
- `visible_pass_hidden_pass`: 44

## By Project

| project | visible-pass hidden-fail | visible-pass hidden-pass | visible-fail hidden-fail | visible-fail hidden-pass |
| --- | ---: | ---: | ---: | ---: |
| `PySnooper` | 9 | 9 | 0 | 0 |
| `cookiecutter` | 17 | 0 | 10 | 0 |
| `httpie` | 0 | 18 | 6 | 0 |
| `scrapy` | 5 | 1 | 4 | 0 |
| `thefuck` | 0 | 12 | 0 | 0 |
| `tqdm` | 0 | 0 | 9 | 0 |
| `youtube-dl` | 0 | 4 | 0 | 0 |

## Checks

- api_call_not_attempted_by_combiner: passed (False)
- raw_model_outputs_not_read: passed (False)
- patch_text_not_stored: passed (False)
- input_gate_analyses_passed: passed (['passed', 'passed', 'passed', 'passed', 'passed', 'passed'])
- hard_negative_min_count_gate: passed (31)
- hard_negative_min_project_gate: passed (['PySnooper', 'cookiecutter', 'scrapy'])

## Next Step

Construct separated cohort and visible-tool headroom gate.
