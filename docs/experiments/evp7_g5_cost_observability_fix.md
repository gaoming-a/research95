# EVP-7 G5 Cost Observability Fix

Date: 2026-06-14

## Scope

This fixes the G5 runner cost path without making new model API calls. The
previous 4-packet smoke proved the DeepSeek API/parser path, but the review
records did not persist provider `usage`, so historical smoke cost cannot be
reconstructed from tracked artifacts.

## Fix

`scripts/run_evp7_g5_llm_workflow.py` now records a raw-output-free `usage`
summary, `cost_source`, `cost_observability`, and `cost_pricing` for each
review.

Cost handling is now:

- use provider-reported `usage.cost` when present;
- otherwise estimate `deepseek_official` / `deepseek-v4-pro` cost from token
  usage;
- if token usage or supported pricing is missing, mark cost as unknown and fail
  the executed workflow after writing outputs;
- keep mock runs at zero cost with `cost_source = mock`.

The DeepSeek estimate uses the official Models & Pricing page:
<https://api-docs.deepseek.com/quick_start/pricing>.

## No-API Verification

The fix was verified with synthetic responses only:

- prompt/completion token usage produced `cost_source =
  estimated_from_tokens` and non-zero `cost_usd`;
- cache-hit/cache-miss token usage produced a non-zero estimate without the
  cache-miss fallback;
- missing usage produced `cost_source = unknown` and a non-zero unknown record
  count in the aggregate cost summary;
- mock workflow still reports `mock_no_billing` and does not attempt API calls.

## Current Boundary

This repair makes future G5 runs cost-observable when DeepSeek returns token
usage. It does not change the claim boundary of the previous smoke: the latest
376-packet evidence remains a 4-packet smoke, not a full-run result.

## Post-Repair Smoke

The repair was subsequently validated against real DeepSeek responses in
`outputs/evp7_g5_llm_376_smoke_002`. The tracked raw-output-free report is
`docs/experiments/evp7_g5_llm_376_smoke_002_result.md`.

- 4/4 records parsed as valid JSON.
- 4/4 records were non-mock real API outputs.
- 4/4 records included provider token usage summaries.
- 4/4 costs used `cost_source = estimated_from_tokens`.
- `unknown_cost_record_count = 0`.
- Estimated total cost USD: 0.003392942.
