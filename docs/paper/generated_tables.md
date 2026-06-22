# Paper Tables

These tables are generated from current tracked artifacts. Raw model responses are not included.

## Dataset By Project

| project | count |
|---|---:|
| `httpie` | 22 |
| `luigi` | 8 |

## Candidate Types

| candidate type | count |
|---|---:|
| `buggy_noop` | 7 |
| `correct_reference` | 7 |
| `irrelevant_patch` | 7 |
| `partial_fix` | 9 |

## Expected Outcomes

| expected outcome | count |
|---|---:|
| `correct` | 7 |
| `incorrect` | 7 |
| `irrelevant_or_noop` | 7 |
| `partial` | 9 |

## Patch Materialization

| materialization | count |
|---|---:|
| `buggy_fixed_unified_diff` | 7 |
| `empty_diff_against_buggy_checkout` | 7 |
| `first_hunk_of_reference_unified_diff` | 1 |
| `local_comment_only_unified_diff` | 7 |
| `reference_diff_with_one_change_omitted` | 6 |
| `reference_replace_with_one_line_reverted` | 2 |

## EVP-7 Workload Ledger

| pipeline stage | tracked workload evidence |
|---|---|
| Task admission | 21 tasks / 6 projects admitted through project-level P2P or documented bounded policies. |
| Candidate construction | 98 candidates: 21 correct references, 76 issue-not-fixed negatives, 1 regression negative. |
| Evidence packets | 392 E0/E2/E4/E6 packets for 98 candidates; G1=passed, G2=passed, leakage findings=0. |
| Visible evidence sources | visible tests completed=95, visible errors=3, tool summaries complete=98. |
| Tool-only baselines | 294 deterministic decisions across 3 conditions; G3=passed. |
| Real LLM G5 run | 376 DeepSeek G5 records over 20 tasks / 94 candidates; E0=94, E2=94, E4=94, E6=94; invalid rate=0.0000. |
| Audit and interpretation | quality=passed_with_limitations; qualitative cases=6; cost observability unknown=0. |

## Executable Validation

| item | value |
|---|---:|
| records | 30 |
| patch applied | 30 |
| oracle ran | 30 |
| oracle all passed | 7 |
| all validated | True |

## No-API Baselines

| baseline | accepted precision | false accept rate | correct recall | false reject rate | escalation rate | invalid output rate |
|---|---:|---:|---:|---:|---:|---:|
| accept-all | 0.2333 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| oracle upper bound | 1.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| reject-all | NA | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 |

## EVP-7 G5 Evidence Visibility Results

- cohort: 20 tasks / 94 candidates / 376 evidence packets
- provider/model: `deepseek_official` / `deepseek-v4-pro`
- quality audit: `passed_with_limitations`
- cost note: Runner cost is estimated from provider token usage when provider-reported cost is absent; see cost_summary for observability counts.
- cost summary: `{"cost_observability_counts": {"estimated_from_provider_token_usage": 376}, "cost_source_counts": {"estimated_from_tokens": 376}, "total_cost_usd": 0.327352058, "unknown_cost_record_count": 0}`

| evidence | records | decisions | invalid | false accept | accepted precision | correct recall | Evidence Gain vs E0 |
|---|---:|---|---:|---:|---:|---:|---:|
| E0 | 94 | `{"accept": 1, "escalate": 49, "reject": 44}` | 0.0000 | 0.0000 | 1.0000 | 0.0500 | 0.0000 |
| E2 | 94 | `{"escalate": 57, "reject": 37}` | 0.0000 | 0.0000 | NA | 0.0000 | -3.0000 |
| E4 | 94 | `{"accept": 1, "escalate": 21, "reject": 72}` | 0.0000 | 0.0000 | 1.0000 | 0.0500 | 7.0000 |
| E6 | 94 | `{"accept": 7, "escalate": 16, "reject": 71}` | 0.0000 | 0.0000 | 1.0000 | 0.3500 | 14.2500 |

## EVP-7 Statistical Intervals

- bootstrap unit: `candidate_id`
- bootstrap samples: 2000
- bootstrap seed: 9507

| evidence | false accept Wilson 95% CI | correct recall Wilson 95% CI | escalation bootstrap 95% CI | utility delta vs E0 bootstrap 95% CI |
|---|---:|---:|---:|---:|
| E0 | [0.0000, 0.0493] | [0.0089, 0.2361] | [0.4255, 0.6277] | -- |
| E2 | [0.0000, 0.0493] | [0.0000, 0.1611] | [0.5106, 0.7021] | [-6.7500, 0.5000] |
| E4 | [0.0000, 0.0493] | [0.0089, 0.2361] | [0.1383, 0.3085] | [2.5000, 11.7500] |
| E6 | [0.0000, 0.0493] | [0.1812, 0.5671] | [0.0957, 0.2553] | [7.7500, 21.5063] |

## EVP-7 Utility Sensitivity

- utility formula: `true_accept - lambda*false_accept - mu*escalated - nu*false_reject`
- scenario count: 27
- dominant best level: `E6`
- dominant best-level share: 1.0000
- dominant ranking: `E6 > E4 > E0 > E2`
- dominant ranking share: 1.0000
- interpretation: The current grid changes escalation and false-reject penalties but does not change false-accept penalties in this run because observed false accept counts are zero at every evidence level.

| evidence level | scenarios as best |
|---|---:|
| E0 | 0 |
| E2 | 0 |
| E4 | 0 |
| E6 | 27 |

## EVP-7 Tool-Only Attribution

- boundary: This artifact compares deterministic tool-only decisions with LLM decisions at matching EVP-7 evidence levels. It reads ignored review records structurally but writes only candidate-level decision aggregates and raw-output-free summaries. It does not support a claim that the LLM outperforms deterministic tool evidence.

| evidence | tool condition | agreement | LLM accepts outside tool accepts | recovered tool false accepts | downgraded tool true accepts |
|---|---|---:|---:|---:|---:|
| E4 | `tool_only_visible_tests` | 72/94 (0.7660) | 0 | 4/4 | 18/19 |
| E6 | `tool_only_visible_tool_summary` | 76/94 (0.8085) | 0 | 4/4 | 12/19 |

## EVP-8 Five-Model Decision Patterns

- synthesis status: `passed`
- protocol: `evp8_journal_full_ladder_v0_1`
- candidate set: `evp8_smoke_from_evp7_structural_98_v0_1`
- allowed claim: Only after status is passed, report descriptive five-model per-level decision patterns for the frozen EVP-8 v0.1 packet set.
- forbidden claim: Do not report five-model journal conclusions, LLM superiority over deterministic baselines, or final evidence-level effectiveness while this scaffold is waiting or partial.

| model | E0 | E1 | E2 | E3 | E4 | E5 | E6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `deepseek/deepseek-v4-pro` | E66/R32 | E58/R40 | E65/R33 | E81/R17 | E74/R24 | E71/R27 | E86/R12 |
| `qwen/qwen3.7-max` | E75/R23 | E70/R28 | E71/R27 | E79/R19 | E80/R18 | E78/R20 | E91/R7 |
| `moonshotai/kimi-k2.6` | E98 | E92/R6 | E91/R7 | E98 | E97/R1 | E98 | E98 |
| `mistralai/devstral-2512` | E98 | E98 | E98 | E98 | E98 | E98 | E98 |
| `google/gemini-2.5-flash` | E98 | E98 | E98 | E96/R2 | E97/R1 | E98 | E98 |


## EVP-8 Cost Accounting

- status: `passed_results_complete_with_blocked_attempt_cost_overrun`
- API freeze: `true`
- passed-result USD excluding Qwen: `2.8921`
- passed Qwen CNY: `41.1195`
- blocked-attempt USD: `7.2761`
- observable USD including blocked attempts, excluding Qwen: `10.1682`

| category | model | reviews | valid | invalid | USD | CNY |
|---|---|---:|---:|---:|---:|---:|
| passed | `deepseek/deepseek-v4-pro` | 686 | 686 | 0 | 0.7888 | 0 |
| passed | `qwen/qwen3.7-max` | 686 | 686 | 0 | 0 | 41.1195 |
| passed | `moonshotai/kimi-k2.6` | 686 | 686 | 0 | 1.0245 | 0 |
| passed | `mistralai/devstral-2512` | 686 | 686 | 0 | 0.4494 | 0 |
| passed | `google/gemini-2.5-flash` | 686 | 686 | 0 | 0.6294 | 0 |
| blocked | `moonshotai/kimi-k2.6` | 686 | 607 | 79 | 6.2223 | 0 |
| blocked | `moonshotai/kimi-k2.6` | 686 | 682 | 4 | 1.0538 | 0 |

- boundary: Blocked attempts are cost/engineering-risk evidence only. They are not valid model-result records and must not be included in five-model decision-pattern synthesis.


## EVP-7 Claim Boundary

| supported claims | unsupported claims |
|---|---|
| The current EVP-7 run produced raw-output-free tracked metrics from real DeepSeek verifier outputs. | Scale-generalized paper claims beyond EVP-7. |
| The run shows evidence-level metric variation in the tracked summary. | A claim that the LLM outperforms the deterministic visible-test tool-only baseline. |
| E4/E6 preserved zero observed false accepts and accepted precision 1.0. | A claim that E6 strictly improves over E4 in this run. |
| E4/E6 improved correct recall over E0 and produced positive Evidence Gain versus E0. | A claim that runner-estimated cost is an external DeepSeek billing statement. |

## Deterministic Reproducibility

| item | value |
|---|---:|
| matched | True |
| checked deterministic files | 7 |
| mismatches | 0 |
| missing | 0 |
