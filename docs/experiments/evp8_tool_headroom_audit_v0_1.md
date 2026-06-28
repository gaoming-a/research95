# EVP-8 Tool-Only Headroom Audit v0.1

- Status: `passed`
- Tool condition: `tool_only_visible_tool_summary`
- Candidate count: `98`
- Correct / incorrect: `21` / `77`
- Headroom decision: `sufficient_for_ablation`
- API call attempted: `false`
- Raw model outputs read: `false`

## Rule-Only Metrics

| metric | value |
| --- | ---: |
| accept count | 25 |
| reject count | 73 |
| escalate count | 0 |
| true accepts | 20 |
| false accepts | 5 |
| false rejects | 1 |
| escalated correct | 0 |
| escalated incorrect | 0 |
| accepted precision | 80.00% |
| correct recall | 95.24% |
| false accept rate | 6.49% |
| false reject rate | 4.76% |
| opportunity-set size | 6 |

## False Accepts

| candidate | task | type | expected outcome |
| --- | --- | --- | --- |
| `evp8_smoke_candidate_0039` | `bugsinpy_thefuck_1` | `regression_patch` | `regression` |
| `evp8_smoke_candidate_0049` | `bugsinpy_youtube-dl_11` | `partial_fix` | `partial` |
| `evp8_smoke_candidate_0053` | `bugsinpy_youtube-dl_16` | `partial_fix` | `partial` |
| `evp8_smoke_candidate_0066` | `bugsinpy_youtube-dl_20` | `partial_fix` | `partial` |
| `evp8_smoke_candidate_0093` | `bugsinpy_youtube-dl_6` | `partial_fix` | `partial` |

## Interpretation

- The deterministic tool baseline has at least one false accept, false reject, or escalation opportunity.
- This audit does not prove LLM added value; it only shows whether there are tool-baseline mistakes for the ablation to test.
