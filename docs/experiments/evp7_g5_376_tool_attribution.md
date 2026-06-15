# EVP-7 G5 Tool-Only Attribution Analysis

This artifact compares deterministic tool-only decisions with LLM decisions at matching EVP-7 evidence levels. It reads ignored review records structurally but writes only candidate-level decision aggregates and raw-output-free summaries. It does not support a claim that the LLM outperforms deterministic tool evidence.

## Summary

- candidate count: 94
- comparison levels: `E4, E6`
- raw-output-free check passed: true

## Matched Decision Overlap

| evidence | tool condition | agreement | LLM accepts outside tool accepts | recovered tool false accepts | downgraded tool true accepts |
|---|---|---:|---:|---:|---:|
| E4 | `tool_only_visible_tests` | 72/94 (0.7660) | 0 | 4/4 | 18/19 |
| E6 | `tool_only_visible_tool_summary` | 76/94 (0.8085) | 0 | 4/4 | 12/19 |

## Decision Pair Counts

### E4

| pair | count |
|---|---:|
| `tool_accept__llm_accept` | 1 |
| `tool_accept__llm_escalate` | 21 |
| `tool_accept__llm_reject` | 1 |
| `tool_reject__llm_reject` | 71 |

### E6

| pair | count |
|---|---:|
| `tool_accept__llm_accept` | 7 |
| `tool_accept__llm_escalate` | 14 |
| `tool_accept__llm_reject` | 2 |
| `tool_reject__llm_escalate` | 2 |
| `tool_reject__llm_reject` | 69 |

## Interpretation Boundary

- The LLM accepted no candidate that the matched deterministic tool-only baseline rejected.
- The LLM recovered the observed tool-only false accepts at E4 and E6, but this came with lower correct-patch recall because many tool-only true accepts were downgraded to reject or escalate.
- The result supports a bounded safety/recall attribution claim, not LLM superiority over deterministic tool evidence.
