# EVP-8 Phase A Paper-Ready Analysis

- Status: `passed`
- API call attempted: `false`
- Raw response content stored: `false`
- Confidence interval method: Wilson score interval, 95%

## Confidence Intervals

| condition | correct recall | accepted precision | false accept rate | escalation rate | FA strict correction | FA safe handling | FR correction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| rule-only | 95.24% [77.33%, 99.15%] | 80.00% [60.87%, 91.14%] | 6.49% [2.81%, 14.32%] | 0.00% [0.00%, 3.77%] | n/a | n/a | n/a |
| deepseek/deepseek-v4-pro E6-full | 90.48% [71.09%, 97.35%] | 82.61% [62.86%, 93.02%] | 5.19% [2.04%, 12.61%] | 0.00% [0.00%, 3.77%] | 20.00% [3.62%, 62.45%] | 20.00% [3.62%, 62.45%] | 0.00% [0.00%, 79.35%] |
| deepseek/deepseek-v4-pro E6-no-verdict | 52.38% [32.37%, 71.66%] | 100.00% [74.12%, 100.00%] | 0.00% [0.00%, 4.75%] | 14.29% [8.70%, 22.56%] | 0.00% [0.00%, 43.45%] | 100.00% [56.55%, 100.00%] | 0.00% [0.00%, 79.35%] |
| qwen/qwen3.7-max E6-full | 95.24% [77.33%, 99.15%] | 83.33% [64.15%, 93.32%] | 5.19% [2.04%, 12.61%] | 0.00% [0.00%, 3.77%] | 20.00% [3.62%, 62.45%] | 20.00% [3.62%, 62.45%] | 0.00% [0.00%, 79.35%] |
| qwen/qwen3.7-max E6-no-verdict | 90.48% [71.09%, 97.35%] | 82.61% [62.86%, 93.02%] | 5.19% [2.04%, 12.61%] | 1.02% [0.18%, 5.56%] | 20.00% [3.62%, 62.45%] | 20.00% [3.62%, 62.45%] | 0.00% [0.00%, 79.35%] |

## Opportunity Cases

| candidate | task | type | expected | tool | Qwen full | Qwen no-verdict | DeepSeek full | DeepSeek no-verdict | missing visible evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `evp8_smoke_candidate_0039` | `bugsinpy_thefuck_1` | `regression_patch` | `regression` | `accept` | `accept` | `accept` | `accept` | `escalate` | Visible evidence did not include enough pass-to-pass/regression coverage to expose the regression. |
| `evp8_smoke_candidate_0049` | `bugsinpy_youtube-dl_11` | `partial_fix` | `partial` | `accept` | `reject` | `reject` | `accept` | `escalate` | Visible tests covered the obvious path, but hidden/P2P evidence shows missed edge behavior. |
| `evp8_smoke_candidate_0053` | `bugsinpy_youtube-dl_16` | `partial_fix` | `partial` | `accept` | `accept` | `accept` | `accept` | `escalate` | Visible tests covered the obvious path, but hidden/P2P evidence shows missed edge behavior. |
| `evp8_smoke_candidate_0066` | `bugsinpy_youtube-dl_20` | `partial_fix` | `partial` | `accept` | `accept` | `accept` | `accept` | `escalate` | Visible tests covered the obvious path, but hidden/P2P evidence shows missed edge behavior. |
| `evp8_smoke_candidate_0093` | `bugsinpy_youtube-dl_6` | `partial_fix` | `partial` | `accept` | `accept` | `accept` | `reject` | `escalate` | Visible tests covered the obvious path, but hidden/P2P evidence shows missed edge behavior. |
| `evp8_smoke_candidate_0011` | `bugsinpy_cookiecutter_1` | `correct_reference` | `correct` | `reject` | `reject` | `reject` | `reject` | `reject` | Visible tool summary reported failure despite evaluator-side correctness; this needs human review. |

## Utility / Risk Policy

Lower cost is better. Costs are illustrative policy weights, not measured money.

| condition | throughput-oriented | balanced-review | safety-critical |
| --- | ---: | ---: | ---: |
| rule-only | 27.00 | 52.00 | 255.00 |
| deepseek/deepseek-v4-pro E6-full | 24.00 | 44.00 | 210.00 |
| deepseek/deepseek-v4-pro E6-no-verdict | 16.00 | 16.00 | 19.00 |
| qwen/qwen3.7-max E6-full | 22.00 | 42.00 | 205.00 |
| qwen/qwen3.7-max E6-no-verdict | 23.00 | 43.00 | 206.00 |

## Interpretation

- The confidence intervals are wide for opportunity-set rates because there are only 6 opportunity cases.
- Qwen preserves recall but repeats most false accepts under both E6 conditions.
- DeepSeek `E6-no-verdict` is attractive only under safety-heavy policies where avoiding false accepts is worth many escalations.
- This Phase A analysis strengthens reporting discipline; it does not solve external validity by itself.

- Allowed: Use this analysis to report uncertainty, case-level failure modes, and risk-policy tradeoffs for the existing EVP-8 cohort.
- Forbidden: Do not claim production merge safety, external validity, or reliable LLM superiority from this Phase A analysis.
