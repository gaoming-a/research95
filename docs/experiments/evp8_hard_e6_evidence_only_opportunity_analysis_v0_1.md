# EVP-8-HARD E6 Evidence-Only Opportunity Analysis v0.1

- Status: `passed`
- Opportunity set size: `9`
- API call attempted: `false`
- Raw model outputs read: `false`

## Purpose

This analysis focuses only on the nine candidates that the tool baseline,
Qwen E6-full, and DeepSeek E6-full all falsely accepted. It checks whether
the evidence-only ablation changes those accept decisions to reject or
escalate.

## Model Results

| Model | repeated accept | reject | escalate | safe handled | risk flags |
|---|---:|---:|---:|---:|---:|
| deepseek/deepseek-v4-pro | 4 | 0 | 5 | 5 | 5 |
| qwen/qwen3.7-max | 7 | 0 | 2 | 2 | 2 |

## Checks

- `api_call_not_attempted_by_analysis`: `true`
- `raw_model_outputs_not_read`: `true`
- `opportunity_set_size_is_9`: `true`
- `parsed_reviews_do_not_contain_raw_fields`: `true`
- `opportunity_coverage_complete_for_existing_models`: `true`
