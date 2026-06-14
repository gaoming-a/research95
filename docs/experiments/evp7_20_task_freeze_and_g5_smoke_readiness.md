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

## Smoke Execution Update

A 4-packet real smoke was executed after user confirmation:

- Run directory: `outputs/evp7_g5_llm_376_smoke_001`
- Raw-output-free summary:
  `data/reviews/evp7_g5_llm_376_smoke_summary.json`
- Report: `docs/experiments/evp7_g5_llm_376_smoke_result.md`
- Review count: 4
- Evidence levels: E0/E2/E4/E6 for `evp7_candidate_0001`
- Parse status: 4 valid / 0 invalid
- Mock records: 0
- API call attempted: true for 4 records
- Decision counts: 4 escalate

The smoke validates the real API and parser path, but it is not a full G5
result.

The workflow observed `cost_usd = 0.0` for all records. Treat this as missing
or non-reporting cost telemetry, not proof of zero cost. The 376-record full run
is blocked until cost observability is fixed or the user explicitly accepts the
telemetry limitation.

Cost-observability repair is recorded in
`docs/experiments/evp7_g5_cost_observability_fix.md`. Future G5 executions
record raw-output-free usage summaries, estimate `deepseek_official` /
`deepseek-v4-pro` cost from DeepSeek token pricing when provider cost is absent,
and fail if cost remains unknown. This does not backfill the old smoke because
its review records did not persist provider `usage`.

A post-repair 4-packet smoke was executed in
`outputs/evp7_g5_llm_376_smoke_002`; the tracked report is
`docs/experiments/evp7_g5_llm_376_smoke_002_result.md`. It produced 4 valid
non-mock records, 4 token-usage summaries, `unknown_cost_record_count=0`, and
estimated total cost USD `0.003392942`.

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

Only after the smoke run has acceptable parse status, invalid-output rate,
observable cost, and run summary should a 376-record full run be considered.
The post-repair smoke now satisfies this cost-observability gate, but it remains
smoke evidence only.

## Full Run Update

The post-repair 376-packet full run was executed in
`outputs/evp7_g5_llm_376_full_001`. The tracked raw-output-free report is
`docs/experiments/evp7_g5_llm_376_full_result.md`, and the quality audit is
`docs/experiments/evp7_g5_376_full_quality_audit.md`.

- Review count: 376
- E0/E2/E4/E6: 94 records each
- Parse status: 376 valid / 0 invalid
- Unknown cost records: 0
- Estimated total cost USD: 0.327352058
- G5 signal status: `real_llm_verifier_signal_observed_on_evp7`
- Quality audit: `passed_with_limitations`

This updates the latest real G5 evidence from the older 248-packet cohort to
the frozen 376-packet cohort. It does not support scale-generalized claims,
deterministic-baseline superiority, E6 strict superiority over E4, or treating
runner-estimated cost as an external billing statement.

## Forbidden Actions

- Do not run `--execute` with `configs/evp7_g5_llm.example.json`.
- Do not create or edit `configs/evp7_g5_llm.local.json` without explicit user
  confirmation.
- Do not skip strict preflight or check-only workflow.
- Do not treat dry-run, check-only, or mock outputs as real LLM signal evidence.
- Do not extend the older 248-record DeepSeek claim to the current 376-packet
  structural cohort.
