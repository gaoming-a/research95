# evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary

- Status: `passed`
- Model: `qwen/qwen3.7-max`
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
| E0 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 0.00% | 75.51% |
| E1 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 0.00% | 75.51% |
| E2 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 0.00% | 74.49% |
| E3 | 20 | 17 | 3 | 85.00% | 80.95% | 3.90% | 4.76% | 4.08% |
| E4 | 21 | 18 | 3 | 85.71% | 85.71% | 3.90% | 4.76% | 2.04% |
| E5 | 21 | 18 | 3 | 85.71% | 85.71% | 3.90% | 4.76% | 3.06% |
| E6 | 24 | 20 | 4 | 83.33% | 95.24% | 5.19% | 4.76% | 0.00% |

## Correct vs Incorrect Decision Counts

| level | correct decisions | incorrect decisions |
| --- | --- | --- |
| E0 | `{"escalate": 21}` | `{"escalate": 53, "reject": 24}` |
| E1 | `{"escalate": 21}` | `{"escalate": 53, "reject": 24}` |
| E2 | `{"escalate": 21}` | `{"escalate": 52, "reject": 25}` |
| E3 | `{"accept": 17, "escalate": 3, "reject": 1}` | `{"accept": 3, "escalate": 1, "reject": 73}` |
| E4 | `{"accept": 18, "escalate": 2, "reject": 1}` | `{"accept": 3, "reject": 74}` |
| E5 | `{"accept": 18, "escalate": 2, "reject": 1}` | `{"accept": 3, "escalate": 1, "reject": 73}` |
| E6 | `{"accept": 20, "reject": 1}` | `{"accept": 4, "reject": 73}` |

## False Accept Breakdown

| level | false accepts by expected outcome | false accepts by candidate type |
| --- | --- | --- |
| E0 | `{}` | `{}` |
| E1 | `{}` | `{}` |
| E2 | `{}` | `{}` |
| E3 | `{"partial": 2, "regression": 1}` | `{"partial_fix": 2, "regression_patch": 1}` |
| E4 | `{"partial": 3}` | `{"partial_fix": 3}` |
| E5 | `{"partial": 2, "regression": 1}` | `{"partial_fix": 2, "regression_patch": 1}` |
| E6 | `{"partial": 3, "regression": 1}` | `{"partial_fix": 3, "regression_patch": 1}` |

## E0-to-Level Accept Transitions

| target | correct non-accept -> accept | incorrect non-accept -> accept |
| --- | ---: | ---: |
| E1 | 0 | 0 |
| E2 | 0 | 0 |
| E3 | 17 | 3 |
| E4 | 18 | 3 |
| E5 | 18 | 3 |
| E6 | 20 | 4 |

## Interpretation Boundary

- Allowed: Report label-conditioned Qwen v0.3 descriptive metrics for the frozen 98-candidate E0-E6 packet set.
- Forbidden: Do not claim five-model effectiveness, DeepSeek/Qwen comparison, LLM superiority, or final evidence-level ranking from this Qwen-only analysis.
