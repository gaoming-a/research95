# EVP-7 G5 LLM Full Run Result

This tracked summary excludes raw model responses. Raw outputs remain under ignored `outputs/`.

## Run

- Provider: `deepseek_official`
- Model: `deepseek-v4-pro`
- Prompt: `patch_verify_evidence_visibility_merge_gate_v1`
- Concurrency: 4
- Review count: 168
- API calls attempted: true
- Model calls attempted: true
- Runner-reported cost: 0.0
- Cost note: DeepSeek response did not expose billable cost in the stored usage field; runner total is not a billing estimate.

## Quality

- Unique review ids: 168
- Parse counts: `{"invalid": 1, "valid": 167}`
- Decision counts: `{"accept": 3, "escalate": 59, "invalid_output": 1, "reject": 105}`
- Invalid output count: 1
- Invalid output rate: 0.005952

## Metrics

- Run kind: `real_llm`
- G5 metric scaffold: `passed`
- G5 signal claim status: `real_llm_verifier_signal_observed_on_evp7`
- Boundary: These metrics come from real LLM verifier outputs on the EVP-7 pilot. They can support EVP-7 pilot signal claims after quality audit, but not scale-generalized paper claims without controlled expansion.

| Evidence | Records | Decisions | Invalid | FAR | Accepted precision | Correct recall | Evidence gain vs E0 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| E0 | 42 | `{"escalate": 23, "invalid_output": 1, "reject": 18}` | 0.02381 | 0.0 | None | 0.0 | 0.0 |
| E2 | 42 | `{"escalate": 24, "reject": 18}` | 0.0 | 0.0 | None | 0.0 | -0.25 |
| E4 | 42 | `{"accept": 1, "escalate": 5, "reject": 36}` | 0.0 | 0.0 | 1.0 | 0.142857 | 4.5 |
| E6 | 42 | `{"accept": 2, "escalate": 7, "reject": 33}` | 0.0 | 0.0 | 1.0 | 0.285714 | 5.0 |

## Invalid Records

- `evp7_candidate_0012__E0` (E0): missing_keys:primary_reason; raw chars=395
