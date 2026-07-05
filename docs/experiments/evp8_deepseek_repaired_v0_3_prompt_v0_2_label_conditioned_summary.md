# evp8_deepseek_repaired_v0_3_prompt_v0_2_label_conditioned_summary

- Status: `passed`
- Model: `deepseek/deepseek-v4-pro`
- Protocol: `evp8_accept_aware_qwen_first_main_v0_3`
- Candidate count: `98`
- Correct / incorrect: `21` / `77`
- API call attempted by analysis: `false`
- Raw response content stored: `false`
- Prompt text stored: `false`
- Reasoning content used: `false`

## Per-Level Label-Conditioned Metrics

| level | accept | correct accept | false accept | accepted precision | correct recall | false accept rate | false reject rate | escalation rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 0.00% | 96.94% |
| E1 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 0.00% | 98.98% |
| E2 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 0.00% | 98.98% |
| E3 | 16 | 13 | 3 | 81.25% | 61.90% | 3.90% | 9.52% | 8.16% |
| E4 | 7 | 7 | 0 | 100.00% | 33.33% | 0.00% | 4.76% | 18.37% |
| E5 | 1 | 1 | 0 | 100.00% | 4.76% | 0.00% | 4.76% | 24.49% |
| E6 | 21 | 17 | 4 | 80.95% | 80.95% | 5.19% | 4.76% | 4.08% |

## Correct vs Incorrect Decision Counts

| level | correct decisions | incorrect decisions |
| --- | --- | --- |
| E0 | `{"escalate": 21}` | `{"escalate": 74, "reject": 3}` |
| E1 | `{"escalate": 21}` | `{"escalate": 76, "reject": 1}` |
| E2 | `{"escalate": 21}` | `{"escalate": 76, "reject": 1}` |
| E3 | `{"accept": 13, "escalate": 6, "reject": 2}` | `{"accept": 3, "escalate": 2, "reject": 72}` |
| E4 | `{"accept": 7, "escalate": 13, "reject": 1}` | `{"escalate": 5, "reject": 72}` |
| E5 | `{"accept": 1, "escalate": 19, "reject": 1}` | `{"escalate": 5, "reject": 72}` |
| E6 | `{"accept": 17, "escalate": 3, "reject": 1}` | `{"accept": 4, "escalate": 1, "reject": 72}` |

## False Accept Breakdown

| level | false accepts by expected outcome | false accepts by candidate type |
| --- | --- | --- |
| E0 | `{}` | `{}` |
| E1 | `{}` | `{}` |
| E2 | `{}` | `{}` |
| E3 | `{"partial": 2, "regression": 1}` | `{"partial_fix": 2, "regression_patch": 1}` |
| E4 | `{}` | `{}` |
| E5 | `{}` | `{}` |
| E6 | `{"partial": 3, "regression": 1}` | `{"partial_fix": 3, "regression_patch": 1}` |

## E0-to-Level Accept Transitions

| target | correct non-accept -> accept | incorrect non-accept -> accept |
| --- | ---: | ---: |
| E1 | 0 | 0 |
| E2 | 0 | 0 |
| E3 | 13 | 3 |
| E4 | 7 | 0 |
| E5 | 1 | 0 |
| E6 | 17 | 4 |

## Interpretation Boundary

- Allowed: Report label-conditioned DeepSeek repaired v0.3 descriptive metrics for the frozen 98-candidate E0-E6 packet set.
- Forbidden: Do not claim three-model effectiveness, LLM superiority, or final evidence-level ranking from this two-model repaired analysis.
