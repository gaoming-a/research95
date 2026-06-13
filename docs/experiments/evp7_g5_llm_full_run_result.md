# EVP-7 G5 LLM Full Run Result

This tracked summary excludes raw model responses. Raw outputs remain under ignored `outputs/`.

## Run

- Provider: `deepseek_official`
- Model: `deepseek-v4-pro`
- Prompt: `patch_verify_evidence_visibility_merge_gate_v1`
- Concurrency: 6
- Review count: 216
- API calls attempted: true
- Model calls attempted: true
- Runner-reported cost: 0.0
- Cost note: DeepSeek response did not expose billable cost in the stored usage field; runner total is not a billing estimate.

## Quality

- Unique review ids: 216
- Parse counts: `{"invalid": 1, "valid": 215}`
- Decision counts: `{"accept": 4, "escalate": 75, "invalid_output": 1, "reject": 136}`
- Invalid output count: 1
- Invalid output rate: 0.00463

## Metrics

- Run kind: `real_llm`
- G5 metric scaffold: `not_passed`
- G5 signal claim status: `real_llm_verifier_outputs_incomplete`
- Boundary: These metrics come from real LLM verifier outputs on the EVP-7 pilot. They can support EVP-7 pilot signal claims after quality audit, but not scale-generalized paper claims without controlled expansion.

| Evidence | Records | Decisions | Invalid | FAR | Accepted precision | Correct recall | Evidence gain vs E0 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| E0 | 54 | `{"accept": 1, "escalate": 32, "reject": 21}` | 0.0 | 0.0 | 1.0 | 0.1 | 0.0 |
| E2 | 54 | `{"escalate": 26, "reject": 28}` | 0.0 | 0.0 | None | 0.0 | -0.5 |
| E4 | 54 | `{"accept": 1, "escalate": 9, "invalid_output": 1, "reject": 43}` | 0.018519 | 0.0 | 1.0 | 0.1 | 4.75 |
| E6 | 54 | `{"accept": 2, "escalate": 8, "reject": 44}` | 0.0 | 0.0 | 1.0 | 0.2 | 6.0 |

## Invalid Records

- `evp7_candidate_0034__E4` (E4): invalid_json:No JSON object found in model response; raw chars=0
