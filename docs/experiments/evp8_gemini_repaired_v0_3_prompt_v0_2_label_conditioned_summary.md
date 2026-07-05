# evp8_gemini_repaired_v0_3_prompt_v0_2_label_conditioned_summary

- Status: `passed`
- Model: `google/gemini-2.5-flash`
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
| E0 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 0.00% | 98.98% |
| E1 | 1 | 0 | 1 | 0.00% | 0.00% | 1.30% | 0.00% | 95.92% |
| E2 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 0.00% | 98.98% |
| E3 | 25 | 20 | 5 | 80.00% | 95.24% | 6.49% | 0.00% | 3.06% |
| E4 | 25 | 20 | 5 | 80.00% | 95.24% | 6.49% | 4.76% | 0.00% |
| E5 | 25 | 20 | 5 | 80.00% | 95.24% | 6.49% | 4.76% | 0.00% |
| E6 | 25 | 20 | 5 | 80.00% | 95.24% | 6.49% | 4.76% | 0.00% |

## Correct vs Incorrect Decision Counts

| level | correct decisions | incorrect decisions |
| --- | --- | --- |
| E0 | `{"escalate": 21}` | `{"escalate": 76, "reject": 1}` |
| E1 | `{"escalate": 21}` | `{"accept": 1, "escalate": 73, "reject": 3}` |
| E2 | `{"escalate": 21}` | `{"escalate": 76, "reject": 1}` |
| E3 | `{"accept": 20, "escalate": 1}` | `{"accept": 5, "escalate": 2, "reject": 70}` |
| E4 | `{"accept": 20, "reject": 1}` | `{"accept": 5, "reject": 72}` |
| E5 | `{"accept": 20, "reject": 1}` | `{"accept": 5, "reject": 72}` |
| E6 | `{"accept": 20, "reject": 1}` | `{"accept": 5, "reject": 72}` |

## False Accept Breakdown

| level | false accepts by expected outcome | false accepts by candidate type |
| --- | --- | --- |
| E0 | `{}` | `{}` |
| E1 | `{"partial": 1}` | `{"partial_fix": 1}` |
| E2 | `{}` | `{}` |
| E3 | `{"partial": 4, "regression": 1}` | `{"partial_fix": 4, "regression_patch": 1}` |
| E4 | `{"partial": 4, "regression": 1}` | `{"partial_fix": 4, "regression_patch": 1}` |
| E5 | `{"partial": 4, "regression": 1}` | `{"partial_fix": 4, "regression_patch": 1}` |
| E6 | `{"partial": 4, "regression": 1}` | `{"partial_fix": 4, "regression_patch": 1}` |

## E0-to-Level Accept Transitions

| target | correct non-accept -> accept | incorrect non-accept -> accept |
| --- | ---: | ---: |
| E1 | 0 | 1 |
| E2 | 0 | 0 |
| E3 | 20 | 5 |
| E4 | 20 | 5 |
| E5 | 20 | 5 |
| E6 | 20 | 5 |

## Interpretation Boundary

- Allowed: Report label-conditioned Gemini repaired v0.3 descriptive metrics for the frozen 98-candidate E0-E6 packet set.
- Forbidden: Do not claim broad LLM superiority, autonomous correctness verification, or final evidence-level ranking from this repaired analysis.
