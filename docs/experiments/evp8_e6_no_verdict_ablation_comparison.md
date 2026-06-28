# EVP-8 E6-no-verdict Ablation Comparison

- Status: `passed`
- Scope: Qwen and DeepSeek only
- Candidate count: `98`
- Analysis API call attempted: `false`
- Raw response content stored in tracked report: `false`

## Main Metrics

| model/condition | accept | reject | escalate | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| rule-only | 25 | 73 | 0 | 20 | 5 | 80.00% | 95.24% | 6.49% | 0.00% |
| deepseek/deepseek-v4-pro E6-full | 23 | 75 | 0 | 19 | 4 | 82.61% | 90.48% | 5.19% | 0.00% |
| deepseek/deepseek-v4-pro E6-no-verdict | 11 | 73 | 14 | 11 | 0 | 100.00% | 52.38% | 0.00% | 14.29% |
| qwen/qwen3.7-max E6-full | 24 | 74 | 0 | 20 | 4 | 83.33% | 95.24% | 5.19% | 0.00% |
| qwen/qwen3.7-max E6-no-verdict | 23 | 74 | 1 | 19 | 4 | 82.61% | 90.48% | 5.19% | 1.02% |

## Opportunity-Set Correction

Tool baseline has 6 opportunity cases: 5 false accepts and 1 false reject.

| model/condition | false accepts corrected to reject | false accepts repeated as accept | false accepts escalated | false reject corrected to accept | false reject repeated as reject | false reject escalated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| deepseek/deepseek-v4-pro E6-full | 1 | 4 | 0 | 0 | 1 | 0 |
| deepseek/deepseek-v4-pro E6-no-verdict | 0 | 0 | 5 | 0 | 1 | 0 |
| qwen/qwen3.7-max E6-full | 1 | 4 | 0 | 0 | 1 | 0 |
| qwen/qwen3.7-max E6-no-verdict | 1 | 4 | 0 | 0 | 1 | 0 |

## E6-full to E6-no-verdict Decision Changes

| model | changed decisions | transition counts |
| --- | ---: | --- |
| deepseek/deepseek-v4-pro | 14 | `{"correct:accept->accept": 11, "correct:accept->escalate": 8, "correct:reject->escalate": 1, "correct:reject->reject": 1, "incorrect:accept->escalate": 4, "incorrect:reject->escalate": 1, "incorrect:reject->reject": 72}` |
| qwen/qwen3.7-max | 1 | `{"correct:accept->accept": 19, "correct:accept->escalate": 1, "correct:reject->reject": 1, "incorrect:accept->accept": 4, "incorrect:reject->reject": 73}` |

## Interpretation

- Removing the explicit rule verdict tests whether the LLM follows the verdict field or reasons from the remaining visible evidence.
- Opportunity-set metrics are more important than aggregate accuracy because the practical question is whether the LLM fixes tool mistakes.
- Allowed claim: Report Qwen/DeepSeek E6-no-verdict ablation against rule-only and E6-full on the frozen 98-candidate EVP-8 cohort.
- Forbidden claim: Do not claim reliable automatic merge, generalization to real agent patches, or superiority without the opportunity-set evidence.
