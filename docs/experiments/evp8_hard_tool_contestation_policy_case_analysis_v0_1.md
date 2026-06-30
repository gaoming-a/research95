# EVP-8-HARD Tool-Contestation Policy and Case Analysis

This is a no-API, raw-output-free analysis over tracked labels,
deterministic baseline decisions, and parsed review schema fields.

## Whole-cohort policy metrics

| System | accept | reject | escalate | true accept | false accept | correct recall | accepted precision | false accept rate | escalation rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| tool_only_baseline | 17 | 30 | 0 | 8 | 9 | 80.00% | 47.06% | 24.32% | 0.00% |
| qwen_evidence_only | 15 | 30 | 2 | 8 | 7 | 80.00% | 53.33% | 18.92% | 4.26% |
| deepseek_evidence_only | 6 | 30 | 11 | 2 | 4 | 20.00% | 33.33% | 10.81% | 23.40% |
| qwen_tool_contestation | 1 | 30 | 16 | 0 | 1 | 0.00% | 0.00% | 2.70% | 34.04% |
| deepseek_tool_contestation | 0 | 29 | 18 | 0 | 0 | 0.00% | n/a | 0.00% | 38.30% |

## Utility scenarios

### merge_gate_strict (FA penalty=20.0, FR penalty=1.0, escalation cost=0.25)

| Rank | System | Score | Score/candidate |
|---:|---|---:|---:|
| 1 | deepseek_tool_contestation | -6.500 | -0.138 |
| 2 | qwen_tool_contestation | -26.000 | -0.553 |
| 3 | deepseek_evidence_only | -82.750 | -1.761 |
| 4 | qwen_evidence_only | -134.500 | -2.862 |
| 5 | tool_only_baseline | -174.000 | -3.702 |

### balanced_triage (FA penalty=5.0, FR penalty=1.0, escalation cost=0.25)

| Rank | System | Score | Score/candidate |
|---:|---|---:|---:|
| 1 | deepseek_tool_contestation | -6.500 | -0.138 |
| 2 | qwen_tool_contestation | -11.000 | -0.234 |
| 3 | deepseek_evidence_only | -22.750 | -0.484 |
| 4 | qwen_evidence_only | -29.500 | -0.628 |
| 5 | tool_only_baseline | -39.000 | -0.830 |

### review_cost_sensitive (FA penalty=5.0, FR penalty=1.0, escalation cost=1.0)

| Rank | System | Score | Score/candidate |
|---:|---|---:|---:|
| 1 | deepseek_tool_contestation | -20.000 | -0.426 |
| 2 | qwen_tool_contestation | -23.000 | -0.489 |
| 3 | qwen_evidence_only | -31.000 | -0.660 |
| 4 | deepseek_evidence_only | -31.000 | -0.660 |
| 5 | tool_only_baseline | -39.000 | -0.830 |

### automation_recall (FA penalty=5.0, FR penalty=2.0, escalation cost=0.5)

| Rank | System | Score | Score/candidate |
|---:|---|---:|---:|
| 1 | deepseek_tool_contestation | -13.000 | -0.277 |
| 2 | qwen_tool_contestation | -17.000 | -0.362 |
| 3 | deepseek_evidence_only | -27.500 | -0.585 |
| 4 | qwen_evidence_only | -32.000 | -0.681 |
| 5 | tool_only_baseline | -41.000 | -0.872 |

## Sensitivity summary

Across the penalty grid `false_accept_penalty in {2,5,10,20}` x `escalation_cost in {0,0.25,0.5,1,2}`:

| Winner | Grid cells |
|---|---:|
| deepseek_tool_contestation | 16 |
| qwen_evidence_only | 3 |
| qwen_evidence_only + tool_only_baseline | 1 |

## Opportunity-set cases

The opportunity set contains the nine candidates that the deterministic tool-only baseline false-accepted.

| System | repeated accept | escalate | strict reject | safe handled |
|---|---:|---:|---:|---:|
| qwen_evidence_only | 7 | 2 | 0 | 2 |
| deepseek_evidence_only | 4 | 5 | 0 | 5 |
| qwen_tool_contestation | 1 | 8 | 0 | 8 |
| deepseek_tool_contestation | 0 | 9 | 0 | 9 |

## Residual and conservative cases

- Qwen residual false accepts under tool-contestation: 1.
  - `evp8_hard_candidate_0012` / `bugsinpy_httpie_4` / `agent_plausible_wrong`: Qwen accepted with visible_tests_sufficient=True and reliability=sufficient_for_accept; DeepSeek decision=escalate.
- DeepSeek escalated correct patches under tool-contestation: 8.

## Interpretation

- The result has practical value only as a risk-policy finding: explicit tool-contestation greatly reduces unsafe autonomous accepts when false accepts are expensive.
- It is not evidence that the LLM semantically verifies correctness: strict reject remains 0/9 on known tool false accepts, and the main improvement is accept-to-escalate.
- The usable paper claim is therefore a tradeoff claim: tool-contestation can be a conservative triage layer, but it sacrifices automation recall and still needs human or stronger semantic evidence for final correctness.
