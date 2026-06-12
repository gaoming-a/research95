# EVP-7 G5 Execution Confirmation Packet

This packet is generated without reading credentials and without calling APIs.

## Current Status

- local config write attempted: false
- API call attempted: false
- ready to write local config: false
- missing or unconfirmed: api_provider, model, max_total_cost_usd, smoke_scope, full_run_permission

## Required User Confirmations

- API provider: `deepseek_official` or `openrouter`
- model id
- maximum total cost in USD
- smoke scope, such as an explicit packet count
- whether full-run permission is granted after smoke passes

## Safe Command Order

1. `python scripts\create_evp7_g5_llm_local_config.py --api-provider <provider> --model <model> --max-total-cost-usd <usd> --smoke-scope <scope> --full-run-permission`
2. `python scripts\preflight_evp7_g5_llm_run.py --config configs\evp7_g5_llm.local.json --strict-api-ready`
3. `python scripts\run_evp7_g5_llm_workflow.py --config configs\evp7_g5_llm.local.json --check-only`
4. `python scripts\run_evp7_g5_llm_workflow.py --config configs\evp7_g5_llm.local.json --execute --limit <smoke-packet-count>`
5. `inspect smoke invalid-output rate, cost, and run summary before any full run`
6. `python scripts\run_evp7_g5_llm_workflow.py --config configs\evp7_g5_llm.local.json --execute --limit 0`

## Forbidden Actions

- do not edit tracked example config with real provider/model/cost decisions
- do not run --execute with configs/evp7_g5_llm.example.json
- do not skip strict preflight and check-only workflow
- do not treat mock or dry-run outputs as LLM signal evidence
