# EVP-8 current-98 coverage-contestation analysis v0.1

Status: `passed`

## Boundary

- This is a prompt-sensitivity condition, not the repaired v0.3 main result.
- It uses the frozen current-98 E6/no-verdict packet set.
- Raw response text, rendered prompts, patch diffs, and credentials are not stored here.
- The separate hard-negative verifier gate remains blocked until the cohort reaches 30 cases and 3 projects.

## Main Metrics

| model | accept | reject | escalate | accepted precision | correct recall | recall loss | repeated FA | strict reject on wrong | safe escalation on wrong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `deepseek/deepseek-v4-pro` | 0 | 73 | 25 | n/a | 0.00% | 100.00% | 0.00% | 93.51% | 6.49% |
| `google/gemini-2.5-flash` | 0 | 73 | 25 | n/a | 0.00% | 100.00% | 0.00% | 93.51% | 6.49% |
| `qwen/qwen3.7-max` | 2 | 74 | 22 | 100.00% | 9.52% | 90.48% | 0.00% | 94.81% | 5.19% |

## Rule-Only Reference

- accepted precision: `80.00%`
- correct recall: `95.24%`
- false accept rate: `6.49%`
- decision counts: `{"accept": 25, "reject": 73}`

## Prompt-Specific Fields

| model | high coverage concern | visible tests insufficient | challenge visible-test-only accept | insufficient tool evidence |
| --- | ---: | ---: | ---: | ---: |
| `deepseek/deepseek-v4-pro` | 31 | 63 | 30 | 23 |
| `google/gemini-2.5-flash` | 6 | 49 | 25 | 25 |
| `qwen/qwen3.7-max` | 16 | 23 | 23 | 23 |

## Repeated False Accept Cases

| model | candidate | project | type | coverage concern | visible tests sufficient | tool reliability | challenge accept |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Claim Boundary

This analysis measures prompt sensitivity on the frozen current-98 E6/no-verdict cohort. It does not replace the repaired v0.3 main result and cannot establish general hard-negative robustness without the separate gated hard-negative cohort.

## Checks

| check | passed | detail |
| --- | --- | --- |
| `candidate_count` | true | `98` |
| `model_count` | true | `["deepseek/deepseek-v4-pro", "google/gemini-2.5-flash", "qwen/qwen3.7-max"]` |
| `review_count_per_model` | true | `{"deepseek/deepseek-v4-pro": 98, "google/gemini-2.5-flash": 98, "qwen/qwen3.7-max": 98}` |
| `rule_only_count` | true | `98` |
| `raw_response_text_not_read` | true | `true` |
| `rendered_prompt_text_not_read` | true | `true` |