# EVP-8-HARD Tool-Contestation Opportunity Analysis v0.1

- Status: `passed`
- Opportunity set size: `9`
- API call attempted: `false`
- Raw model outputs read: `false`

## Purpose

This analysis focuses only on the nine candidates that the tool baseline,
Qwen E6-full, and DeepSeek E6-full all falsely accepted. It checks whether
a tool-contestation prompt makes the model challenge a visible-test-only
accept premise, mark visible tests as insufficient, or move accept to
reject/escalate.

## Model Results

| Model | repeated accept | accept without challenge | challenge true | insufficient/challenged | reject | escalate | safe handled |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek/deepseek-v4-pro | 0 | 0 | 9 | 9 | 0 | 9 | 9 |
| qwen/qwen3.7-max | 1 | 1 | 8 | 8 | 0 | 8 | 8 |

## Claim Boundary

Challenge, insufficient-evidence, or escalation outcomes are risk-triage signals; they are not automatic proof that the model identified semantic incorrectness.

## Checks

- `api_call_not_attempted_by_analysis`: `true`
- `raw_model_outputs_not_read`: `true`
- `opportunity_set_size_is_9`: `true`
- `parsed_reviews_do_not_contain_raw_fields`: `true`
- `opportunity_coverage_complete_for_existing_models`: `true`
