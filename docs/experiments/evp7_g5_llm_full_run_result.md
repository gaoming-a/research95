# EVP-7 G5 LLM Full Run Result

This tracked summary excludes raw model responses. Raw outputs remain under ignored `outputs/`.

## Run

- Provider: `deepseek_official`
- Model: `deepseek-v4-pro`
- Prompt: `patch_verify_evidence_visibility_merge_gate_v1`
- Concurrency: 6
- Review count: 232
- API calls attempted: true
- Model calls attempted: true
- Runner-reported cost: 0.0
- Cost note: DeepSeek response did not expose billable cost in the stored usage field; runner total is not a billing estimate.

## Quality

- Unique review ids: 232
- Parse counts: `{"valid": 232}`
- Decision counts: `{"accept": 4, "escalate": 92, "reject": 136}`
- Invalid output count: 0
- Invalid output rate: 0.0

## Metrics

- Run kind: `real_llm`
- G5 metric scaffold: `passed`
- G5 signal claim status: `real_llm_verifier_signal_observed_on_evp7`
- Boundary: These metrics come from real LLM verifier outputs on the EVP-7 pilot. They can support EVP-7 pilot signal claims after quality audit, but not scale-generalized paper claims without controlled expansion.

| Evidence | Records | Decisions | Invalid | FAR | Accepted precision | Correct recall | Evidence gain vs E0 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| E0 | 58 | `{"escalate": 36, "reject": 22}` | 0.0 | 0.0 | None | 0.0 | 0.0 |
| E2 | 58 | `{"escalate": 37, "reject": 21}` | 0.0 | 0.0 | None | 0.0 | 0.75 |
| E4 | 58 | `{"accept": 3, "escalate": 8, "reject": 47}` | 0.0 | 0.0 | 1.0 | 0.272727 | 10.0 |
| E6 | 58 | `{"accept": 1, "escalate": 11, "reject": 46}` | 0.0 | 0.0 | 1.0 | 0.090909 | 7.25 |

## Invalid Records

- None
