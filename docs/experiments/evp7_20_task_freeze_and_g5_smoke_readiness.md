# EVP-7 20-Task Freeze And G5 Smoke Readiness

Date: 2026-06-14

## Freeze Decision

The EVP-7 structural cohort is frozen at:

- 20 tasks
- 5 projects
- 94 candidates
- 376 E0/E2/E4/E6 evidence packets

This satisfies the planned 15-20 bug expansion target. Further task admission is
not the next step because the current expansion already reaches the upper bound
and additional admissions would increase the `youtube-dl` concentration.

## Current Evidence Boundary

The current 376-packet package is structurally ready for a future G5 LLM run,
but it is not real model evidence.

The latest real DeepSeek G5 run still covers only the earlier
12-task / 62-candidate / 248-packet cohort. Any paper claim about the current
20-task cohort needs a fresh real G5 run on the 376-packet package.

## No-API Smoke Preparation

Tracked readiness artifacts:

- `data/reviews/evp7_g5_llm_run_readiness.json`
- `data/reviews/evp7_g5_llm_preflight_example.json`
- `data/reviews/evp7_g5_llm_preflight_strict_example.json`
- `data/reviews/evp7_g5_workflow_check_only_example.json`
- `data/reviews/evp7_g5_local_config_dry_run.json`
- `docs/experiments/evp7_g5_execution_confirmation_packet.md`

Current gate status:

- structural readiness: passed
- prompt records: 376
- E0/E2/E4/E6 records: 94 each
- prompt text stored: false
- label leakage failures: 0
- strict API readiness: false
- API call attempted: false
- model call attempted: false

## Required User Confirmations

Before any real smoke run, the user must explicitly confirm:

- API provider: `deepseek_official` or `openrouter`
- model id
- maximum total cost in USD
- smoke scope as an explicit packet count
- whether full-run permission is granted after smoke passes

Do not infer these values from old runs.

## Safe Command Order After Confirmation

```powershell
python scripts\create_evp7_g5_llm_local_config.py `
  --api-provider <provider> `
  --model <model> `
  --max-total-cost-usd <usd> `
  --smoke-scope <packet-count> `
  --full-run-permission

python scripts\preflight_evp7_g5_llm_run.py `
  --config configs\evp7_g5_llm.local.json `
  --strict-api-ready

python scripts\run_evp7_g5_llm_workflow.py `
  --config configs\evp7_g5_llm.local.json `
  --check-only

python scripts\run_evp7_g5_llm_workflow.py `
  --config configs\evp7_g5_llm.local.json `
  --execute `
  --limit <smoke-packet-count>
```

Only after the smoke run has acceptable parse status, invalid-output rate, cost,
and run summary should a 376-record full run be considered.

## Forbidden Actions

- Do not run `--execute` with `configs/evp7_g5_llm.example.json`.
- Do not create or edit `configs/evp7_g5_llm.local.json` without explicit user
  confirmation.
- Do not skip strict preflight or check-only workflow.
- Do not treat dry-run, check-only, or mock outputs as real LLM signal evidence.
- Do not extend the older 248-record DeepSeek claim to the current 376-packet
  structural cohort.
