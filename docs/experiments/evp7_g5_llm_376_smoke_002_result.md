# EVP-7 G5 376-Packet Cohort Smoke 002 Result

Date: 2026-06-14

## Scope

- Cohort boundary: 20 tasks / 94 candidates / 376 evidence packets
- API provider: `deepseek_official`
- Model: `deepseek-v4-pro`
- Smoke packet limit: 4
- Run directory: `outputs/evp7_g5_llm_376_smoke_002`
- Pricing source: <https://api-docs.deepseek.com/quick_start/pricing>

## Result

- Review count: 4
- Parse status counts: `{'valid': 4}`
- Invalid output rate: 0.0
- Mock run counts: `{'False': 4}`
- API call attempted counts: `{'True': 4}`
- Evidence level counts: `{'E0': 1, 'E2': 1, 'E4': 1, 'E6': 1}`
- Decision counts: `{'accept': 1, 'escalate': 3}`
- Usage present count: 4
- Cost source counts: `{'estimated_from_tokens': 4}`
- Cost observability counts: `{'estimated_from_provider_token_usage': 4}`
- Unknown cost record count: 0
- Estimated total cost USD: 0.003392942

The post-repair smoke validates the real API, parser/schema, and
cost-observability path on 4 packets. All records include provider token usage
summaries and non-zero token-price cost estimates.

## Gate

- Parse gate: passed
- Cost gate: passed
- Budget gate: passed against `max_total_cost_usd = 10`

## Claim Boundary

This smoke is still not a full G5 result. It only shows that the repaired
runner can execute real DeepSeek calls and observe estimated cost on a bounded
4-packet sample. A fresh 376-packet full run is still required before extending
real-model G5 claims to the current frozen cohort.
