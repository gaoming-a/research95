# EVP-7 G5 376-Packet Cohort Smoke Result

Date: 2026-06-14

## Scope

- Cohort boundary: 20 tasks / 94 candidates / 376 evidence packets
- API provider: `deepseek_official`
- Model: `deepseek-v4-pro`
- Smoke packet limit: 4
- Run directory: `outputs/evp7_g5_llm_376_smoke_001`

## Result

- Review count: 4
- Parse status counts: `{'valid': 4}`
- Invalid output rate: 0.0
- Mock run counts: `{'False': 4}`
- API call attempted counts: `{'True': 4}`
- Evidence level counts: `{'E0': 1, 'E2': 1, 'E4': 1, 'E6': 1}`
- Decision counts: `{'escalate': 4}`
- Observed cost USD: 0.0

The smoke parser/API gate passed: all 4 records were valid, non-mock, real API records across E0/E2/E4/E6 for one candidate.

## Cost Boundary

The workflow observed `cost_usd = 0.0` for all records. This should be treated as missing or non-reporting provider cost telemetry, not proof that the run was free. Because the configured `max_total_cost_usd = 10` cannot be reliably enforced from the recorded provider response, the 376-record full run is blocked until cost observability is fixed or the user explicitly accepts this telemetry limitation.

## Claim Boundary

This smoke validates the real API path and parser/schema stability on 4 packets only. It is not a full G5 result and must not be used to extend the old 248-packet DeepSeek claim to the current 376-packet cohort.
