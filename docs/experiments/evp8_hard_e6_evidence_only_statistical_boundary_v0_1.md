# EVP-8-HARD E6 Evidence-Only Statistical Boundary v0.1

- API call attempted: `false`
- Raw model outputs read: `false`
- Bootstrap samples: `2000`
- Bootstrap seed: `9508`

## Whole-Cohort Wilson 95% CI

| System | false accept rate | accepted precision | correct recall | escalation rate |
|---|---:|---:|---:|---:|
| tool-only baseline | 0.243 [0.134, 0.401] | 0.471 [0.262, 0.690] | 0.800 [0.490, 0.943] | 0.000 [0.000, 0.076] |
| deepseek/deepseek-v4-pro | 0.108 [0.043, 0.247] | 0.333 [0.097, 0.700] | 0.200 [0.057, 0.510] | 0.234 [0.136, 0.372] |
| qwen/qwen3.7-max | 0.189 [0.095, 0.342] | 0.533 [0.301, 0.752] | 0.800 [0.490, 0.943] | 0.043 [0.012, 0.142] |

## Nine-Case Opportunity Set

| Model | safe handling Wilson 95% CI | repeated accept Wilson 95% CI | strict reject Wilson 95% CI | safe delta vs tool bootstrap 95% CI |
|---|---:|---:|---:|---:|
| deepseek/deepseek-v4-pro | 0.556 [0.267, 0.811] | 0.444 [0.189, 0.733] | 0.000 [0.000, 0.299] | 0.556 [0.222, 0.889] |
| qwen/qwen3.7-max | 0.222 [0.063, 0.547] | 0.778 [0.453, 0.937] | 0.000 [0.000, 0.299] | 0.222 [0.000, 0.556] |

## DeepSeek Minus Qwen on Opportunity Set

| Metric | paired bootstrap 95% CI |
|---|---:|
| repeated_accept_rate | -0.333 [-0.667, 0.000] |
| risk_flag_rate | 0.333 [0.000, 0.667] |
| safe_handling_rate | 0.333 [0.000, 0.667] |
| strict_reject_rate | 0.000 [0.000, 0.000] |

## Claim Boundary

Intervals are wide because the hard-case cohort has 47 candidates and the primary opportunity set has only nine known false accepts. Use these results as evidence of behavior shift and triage tradeoff, not as a reliability guarantee.

## Checks

- `audit_passed`: `true`
- `opportunity_analysis_passed`: `true`
- `api_call_not_attempted_by_statistics`: `true`
- `raw_model_outputs_not_read`: `true`
