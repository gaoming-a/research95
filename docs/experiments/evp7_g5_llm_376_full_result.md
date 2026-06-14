# EVP-7 G5 LLM Full Run Result

This tracked summary excludes raw model responses. Raw outputs remain under ignored `outputs/`.

## Run

- Provider: `deepseek_official`
- Model: `deepseek-v4-pro`
- Prompt: `patch_verify_evidence_visibility_merge_gate_v1`
- Concurrency: 4
- Review count: 376
- API calls attempted: true
- Model calls attempted: true
- Runner-reported cost: 0.327352058
- Cost note: Runner cost is estimated from provider token usage when provider-reported cost is absent; see cost_summary for observability counts.
- Cost summary: `{"cost_observability_counts": {"estimated_from_provider_token_usage": 376}, "cost_source_counts": {"estimated_from_tokens": 376}, "total_cost_usd": 0.327352058, "unknown_cost_record_count": 0}`

## Quality

- Unique review ids: 376
- Parse counts: `{"valid": 376}`
- Decision counts: `{"accept": 9, "escalate": 143, "reject": 224}`
- Invalid output count: 0
- Invalid output rate: 0.0

## Metrics

- Run kind: `real_llm`
- G5 metric scaffold: `passed`
- G5 signal claim status: `real_llm_verifier_signal_observed_on_evp7`
- Boundary: These metrics come from real LLM verifier outputs on the EVP-7 pilot. They can support EVP-7 pilot signal claims after quality audit, but not scale-generalized paper claims without controlled expansion.

| Evidence | Records | Decisions | Invalid | FAR | Accepted precision | Correct recall | Evidence gain vs E0 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| E0 | 94 | `{"accept": 1, "escalate": 49, "reject": 44}` | 0.0 | 0.0 | 1.0 | 0.05 | 0.0 |
| E2 | 94 | `{"escalate": 57, "reject": 37}` | 0.0 | 0.0 | None | 0.0 | -3.0 |
| E4 | 94 | `{"accept": 1, "escalate": 21, "reject": 72}` | 0.0 | 0.0 | 1.0 | 0.05 | 7.0 |
| E6 | 94 | `{"accept": 7, "escalate": 16, "reject": 71}` | 0.0 | 0.0 | 1.0 | 0.35 | 14.25 |

## Invalid Records

- None
