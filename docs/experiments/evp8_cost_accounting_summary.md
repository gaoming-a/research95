# EVP-8 Cost Accounting Summary v0.1

This no-API cost accounting summary reads tracked raw-output-free passed summaries and ignored raw-output-free blocked-attempt summaries. It does not read raw model responses or prompt text.

## Summary

- status: `passed_results_complete_with_blocked_attempt_cost_overrun`
- API freeze: `true`
- passed-result USD excluding Qwen: `2.892118`
- passed Qwen CNY: `41.119548`
- blocked-attempt USD: `7.276121`
- observable USD including blocked attempts, excluding Qwen: `10.168239`
- later-model observable USD including blocked attempts: `9.379430`
- later-model planning ceiling USD: `30.000000`

## Passed Result Costs

| model | reviews | valid | USD | CNY | unknown cost |
|---|---:|---:|---:|---:|---:|
| `deepseek/deepseek-v4-pro` | 686 | 686 | 0.788809 | 0.000000 | 0 |
| `qwen/qwen3.7-max` | 686 | 686 | 0.000000 | 41.119548 | 0 |
| `moonshotai/kimi-k2.6` | 686 | 686 | 1.024510 | 0.000000 | 0 |
| `mistralai/devstral-2512` | 686 | 686 | 0.449371 | 0.000000 | 0 |
| `google/gemini-2.5-flash` | 686 | 686 | 0.629429 | 0.000000 | 0 |

## Blocked Attempt Costs

| model | gate | reviews | valid | invalid | USD | unknown cost |
|---|---|---:|---:|---:|---:|---:|
| `moonshotai/kimi-k2.6` | `blocked` | 686 | 607 | 79 | 6.222297 | 1 |
| `moonshotai/kimi-k2.6` | `blocked` | 686 | 682 | 4 | 1.053823 | 4 |

## Checks

| check | passed | observed |
|---|---:|---:|
| `no_api_call_attempted` | `true` | `` |
| `passed_summary_count` | `true` | `5` |
| `blocked_attempt_count_observed` | `true` | `2` |
| `later_observable_usd_within_planning_ceiling` | `true` | `9.37942977` |
| `blocked_attempt_cost_requires_freeze` | `true` | `7.27612053` |

## Claim Boundary

Blocked attempts are cost/engineering-risk evidence only. They are not valid model-result records and must not be included in five-model decision-pattern synthesis.
