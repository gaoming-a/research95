# EVP-7 G5 LLM Full Run Result

This tracked summary excludes raw model responses. Raw outputs remain under ignored `outputs/`.

## Run

- Provider: `deepseek_official`
- Model: `deepseek-v4-pro`
- Prompt: `patch_verify_evidence_visibility_merge_gate_v1`
- Concurrency: 6
- Review count: 200
- API calls attempted: true
- Model calls attempted: true
- Runner-reported cost: 0.0
- Cost note: DeepSeek response did not expose billable cost in the stored usage field; runner total is not a billing estimate.

## Quality

- Unique review ids: 200
- Parse counts: `{"invalid": 1, "valid": 199}`
- Decision counts: `{"accept": 3, "escalate": 71, "invalid_output": 1, "reject": 125}`
- Invalid output count: 1
- Invalid output rate: 0.005

## Metrics

- Run kind: `real_llm`
- G5 metric scaffold: `passed`
- G5 signal claim status: `real_llm_verifier_signal_observed_on_evp7`
- Boundary: These metrics come from real LLM verifier outputs on the EVP-7 pilot. They can support EVP-7 pilot signal claims after quality audit, but not scale-generalized paper claims without controlled expansion.

| Evidence | Records | Decisions | Invalid | FAR | Accepted precision | Correct recall | Evidence gain vs E0 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| E0 | 50 | `{"escalate": 28, "reject": 22}` | 0.0 | 0.0 | None | 0.0 | 0.0 |
| E2 | 50 | `{"escalate": 26, "reject": 24}` | 0.0 | 0.0 | None | 0.0 | 0.5 |
| E4 | 50 | `{"accept": 1, "escalate": 8, "invalid_output": 1, "reject": 40}` | 0.02 | 0.0 | 1.0 | 0.111111 | 5.0 |
| E6 | 50 | `{"accept": 2, "escalate": 9, "reject": 39}` | 0.0 | 0.0 | 1.0 | 0.222222 | 4.75 |

## Invalid Records

- `evp7_candidate_0021__E4` (E4): invalid_suspected_failure_type:test_overfitting; raw chars=540
