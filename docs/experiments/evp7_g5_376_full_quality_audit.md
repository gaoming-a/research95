# EVP-7 G5 Full-Run Quality Audit

This audit reads only the tracked raw-output-free full-run summary. It does not read or copy raw model responses.

## Status

- Quality status: `passed_with_limitations`
- API call attempted by audit: false
- Raw outputs read by audit: false
- Raw outputs tracked: false
- Review count: 376
- Candidate count: 94

## Checks

| Check | Passed | Observed |
| --- | --- | --- |
| `real_llm_run` | true | `real_llm` |
| `model_call_attempted` | true | `True` |
| `review_count_matches_levels` | true | `376` |
| `unique_review_ids` | true | `376` |
| `raw_outputs_not_tracked` | true | `False` |
| `invalid_output_rate_within_limit` | true | `0.0` |
| `has_metric_variation` | true | `True` |
| `cost_observability_complete` | true | `0` |
| `E0_record_count` | true | `94` |
| `E2_record_count` | true | `94` |
| `E4_record_count` | true | `94` |
| `E6_record_count` | true | `94` |
| `E4_false_accept_rate_zero` | true | `0.0` |
| `E4_accepted_precision_one` | true | `1.0` |
| `E4_correct_recall_positive` | true | `0.05` |
| `E4_evidence_gain_positive` | true | `7.0` |
| `E6_false_accept_rate_zero` | true | `0.0` |
| `E6_accepted_precision_one` | true | `1.0` |
| `E6_correct_recall_positive` | true | `0.35` |
| `E6_evidence_gain_positive` | true | `14.25` |

## Supported Claims

- The current EVP-7 run produced raw-output-free tracked metrics from real DeepSeek verifier outputs.
- The run shows evidence-level metric variation in the tracked summary.
- E4/E6 preserved zero observed false accepts and accepted precision 1.0.
- E4/E6 improved correct recall over E0 and produced positive Evidence Gain versus E0.

## Unsupported Claims

- Scale-generalized paper claims beyond EVP-7.
- A claim that the LLM outperforms the deterministic visible-test tool-only baseline.
- A claim that E6 strictly improves over E4 in this run.
- A claim that runner-estimated cost is an external DeepSeek billing statement.

## Limitations

- E4/E6 correct recall remains below the deterministic visible-test tool-only baseline recall.
- Runner cost is an estimate from provider token usage and configured pricing, not an external billing statement.
- The cohort remains a pilot-scale BugsInPy slice.
