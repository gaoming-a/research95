# EVP-7 G5 Full-Run Quality Audit

This audit reads only the tracked raw-output-free full-run summary. It does not read or copy raw model responses.

## Status

- Quality status: `passed_with_limitations`
- API call attempted by audit: false
- Raw outputs read by audit: false
- Raw outputs tracked: false
- Review count: 216
- Candidate count: 54

## Checks

| Check | Passed | Observed |
| --- | --- | --- |
| `real_llm_run` | true | `real_llm` |
| `model_call_attempted` | true | `True` |
| `review_count_matches_levels` | true | `216` |
| `unique_review_ids` | true | `216` |
| `raw_outputs_not_tracked` | true | `False` |
| `invalid_output_rate_within_limit` | true | `0.00463` |
| `has_metric_variation` | true | `True` |
| `E0_record_count` | true | `54` |
| `E2_record_count` | true | `54` |
| `E4_record_count` | true | `54` |
| `E6_record_count` | true | `54` |
| `E4_false_accept_rate_zero` | true | `0.0` |
| `E4_accepted_precision_one` | true | `1.0` |
| `E4_correct_recall_positive` | true | `0.1` |
| `E4_evidence_gain_positive` | true | `4.75` |
| `E6_false_accept_rate_zero` | true | `0.0` |
| `E6_accepted_precision_one` | true | `1.0` |
| `E6_correct_recall_positive` | true | `0.2` |
| `E6_evidence_gain_positive` | true | `6.0` |

## Supported Claims

- The current EVP-7 run produced raw-output-free tracked metrics from real DeepSeek verifier outputs.
- The run shows evidence-level metric variation in the tracked summary.
- E4/E6 preserved zero observed false accepts and accepted precision 1.0.
- E4/E6 improved correct recall over E0 and produced positive Evidence Gain versus E0.

## Unsupported Claims

- Scale-generalized paper claims beyond EVP-7.
- A claim that the LLM outperforms the deterministic visible-test tool-only baseline.
- A claim that E6 strictly improves over E4 in this run.
- A claim that DeepSeek cost is known from runner output.

## Limitations

- 1 record(s) are schema-invalid.
- E4/E6 correct recall remains below the deterministic visible-test tool-only baseline recall.
- G5 signal claim status remains `real_llm_verifier_outputs_incomplete` in the metrics scaffold.
- Runner-reported cost is 0.0 because DeepSeek response usage did not expose billable cost in the stored field.
- The cohort remains a pilot-scale BugsInPy slice.
