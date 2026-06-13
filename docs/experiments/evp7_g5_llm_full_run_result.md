# EVP-7 G5 LLM Full Run Result

This tracked summary excludes raw model responses. Raw outputs remain under ignored `outputs/`.

## Run

- Provider: `deepseek_official`
- Model: `deepseek-v4-pro`
- Prompt: `patch_verify_evidence_visibility_merge_gate_v1`
- Concurrency: 6
- Review count: 184
- API calls attempted: true
- Model calls attempted: true
- Runner-reported cost: 0.0
- Cost note: DeepSeek response did not expose billable cost in the stored usage field; runner total is not a billing estimate.

## Quality

- Unique review ids: 184
- Parse counts: `{"invalid": 1, "valid": 183}`
- Decision counts: `{"accept": 6, "escalate": 64, "invalid_output": 1, "reject": 113}`
- Invalid output count: 1
- Invalid output rate: 0.005435

## Metrics

- Run kind: `real_llm`
- G5 metric scaffold: `passed`
- G5 signal claim status: `real_llm_verifier_signal_observed_on_evp7`
- Boundary: These metrics come from real LLM verifier outputs on the EVP-7 pilot. They can support EVP-7 pilot signal claims after quality audit, but not scale-generalized paper claims without controlled expansion.

| Evidence | Records | Decisions | Invalid | FAR | Accepted precision | Correct recall | Evidence gain vs E0 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| E0 | 46 | `{"escalate": 26, "reject": 20}` | 0.0 | 0.0 | None | 0.0 | 0.0 |
| E2 | 46 | `{"escalate": 28, "invalid_output": 1, "reject": 17}` | 0.021739 | 0.0 | None | 0.0 | -0.5 |
| E4 | 46 | `{"accept": 3, "escalate": 4, "reject": 39}` | 0.0 | 0.0 | 1.0 | 0.375 | 7.5 |
| E6 | 46 | `{"accept": 3, "escalate": 6, "reject": 37}` | 0.0 | 0.0 | 1.0 | 0.375 | 7.0 |

## Invalid Records

- `evp7_candidate_0004__E2` (E2): invalid_json:No JSON object found in model response; raw chars=0
