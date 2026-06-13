# EVP-7 G5 Full-Run Quality Audit

This audit reads only the tracked raw-output-free full-run summary. It does not read or copy raw model responses.

## Status

- Quality status: `passed_with_limitations`
- API call attempted by audit: false
- Raw outputs read by audit: false
- Raw outputs tracked: false

## Checks

| Check | Passed | Observed |
| --- | --- | --- |
| `review_count` | true | `200` |
| `unique_review_ids` | true | `200` |
| `raw_outputs_not_tracked` | true | `False` |
| `invalid_output_count` | true | `1` |
| `invalid_output_rate` | true | `0.005` |
| `g5_signal_observed` | true | `real_llm_verifier_signal_observed_on_evp7` |
| `E0_record_count` | true | `50` |
| `E2_record_count` | true | `50` |
| `E4_record_count` | true | `50` |
| `E6_record_count` | true | `50` |
| `E4_false_accept_rate_zero` | true | `0.0` |
| `E4_accepted_precision_one` | true | `1.0` |
| `E4_correct_recall_positive` | true | `0.111111` |
| `E4_evidence_gain_positive` | true | `5.0` |
| `E6_false_accept_rate_zero` | true | `0.0` |
| `E6_accepted_precision_one` | true | `1.0` |
| `E6_correct_recall_positive` | true | `0.222222` |
| `E6_evidence_gain_positive` | true | `4.75` |

## Supported Claims

- The current EVP-7 9-task/50-candidate/200-packet run observed evidence-visibility signal in real DeepSeek verifier outputs.
- E4/E6 preserved zero observed false accepts and accepted precision 1.0.
- E4/E6 improved correct recall over E0 and produced positive Evidence Gain versus E0.

## Unsupported Claims

- Scale-generalized paper claims beyond EVP-7.
- A claim that the LLM outperforms the deterministic visible-test tool-only baseline.
- A claim that E6 strictly improves over E4 in this run.
- A claim that DeepSeek cost is known from runner output.

## Limitations

- One E4 record is schema-invalid.
- E4 correct recall is 0.111111 and E6 correct recall is 0.222222, below the deterministic visible-test tool-only baseline recall of 0.888889.
- Runner-reported cost is 0.0 because DeepSeek response usage did not expose billable cost in the stored field.
- The cohort remains a pilot-scale 9-task BugsInPy slice.
