# EVP-7 G5 LLM Run Readiness

Date: 2026-06-13

## Purpose

This document records the no-API readiness package for the real LLM G5
signal-existence run. The package was later consumed by the fresh 184-record
DeepSeek official run summarized in
`docs/experiments/evp7_g5_llm_full_run_result.md`.

The goal of G5 is to test whether E0/E2/E4/E6 evidence visibility changes LLM
merge-gate decisions in an explainable way. This readiness step prepares the
prompt manifest, prompt version, leakage checks, run scope, and stop conditions
without calling any model API.

## Command

```powershell
python scripts\build_evp7_g5_llm_prompt_manifest.py --check
```

## Inputs

```text
data/evidence/evp7_evidence_packets.jsonl
```

## Outputs

```text
data/reviews/evp7_g5_llm_prompt_manifest.jsonl
data/reviews/evp7_g5_llm_run_readiness.json
```

The prompt manifest stores prompt hashes and lengths only. Full prompt text is
not stored in the tracked artifact.

## Prompt

Prompt id:

```text
patch_verify_evidence_visibility_merge_gate_v1
```

This is a new EVP-7 evidence-visibility prompt. It does not replace
`patch_verify_evidence_first_v1` or `patch_verify_tool_augmented_evidence_v1`.
It uses the fixed merge-gate schema from the EVP-7 protocol:

```json
{
  "decision": "accept | reject | escalate",
  "confidence": 0.0,
  "primary_reason": "...",
  "evidence_used": ["..."],
  "risk_flags": ["..."],
  "suspected_failure_type": "none | partial_fix | under_fix | regression | irrelevant | non_applicable | unknown",
  "human_review_needed": true
}
```

Generic schema enum values such as `partial_fix` are allowed because they are
not candidate-specific labels. Candidate-specific evaluator labels and
construction taxonomy remain forbidden in the rendered prompt payload.

## Readiness Result

- prompt records = 200;
- E0/E2/E4/E6 records = 50 each;
- prompt char range = 1880 to 4938;
- prompt char total = 572419;
- rough prompt-token estimate by chars/4 = 143105;
- leakage failed count = 0;
- G5 LLM run readiness = `passed_without_api`;
- API call attempted = false.

## Stop Conditions For Real Execution

Do not continue a real G5 run if any of the following occur:

- prompt boundary or leakage check fails;
- invalid output rate exceeds 0.2 in the initial smoke slice;
- API authentication, model selection, or preflight fails;
- observed cost growth exceeds the user-confirmed budget;
- `run_error.json` is produced.

## Required User Confirmation

Before any real G5 API call, the user must confirm:

- API provider;
- model;
- maximum total cost in USD;
- smoke scope;
- permission for the full 184-record run after smoke.

This readiness artifact is not model-result evidence and does not pass G5 by
itself; the later 184-record DeepSeek run provides the current model-result
evidence.

## Config And Preflight

Tracked example config:

```text
configs/evp7_g5_llm.example.json
```

No-API structural preflight:

```powershell
python scripts\preflight_evp7_g5_llm_run.py `
  --config configs\evp7_g5_llm.example.json `
  --out data\reviews\evp7_g5_llm_preflight_example.json
```

Current result:

- structural readiness = true;
- API readiness = false;
- API call attempted = false.

Strict preflight:

```powershell
python scripts\preflight_evp7_g5_llm_run.py `
  --config configs\evp7_g5_llm.example.json `
  --strict-api-ready `
  --out data\reviews\evp7_g5_llm_preflight_strict_example.json
```

The strict check correctly fails while provider, model, cost ceiling, smoke
scope, and full-run permission are still placeholders. This is intentional:
the example config proves structure, not permission to spend API budget.

## Guarded Workflow

Workflow script:

```text
scripts/run_evp7_g5_llm_workflow.py
```

Check-only command:

```powershell
python scripts\run_evp7_g5_llm_workflow.py `
  --check-only `
  --summary-out data\reviews\evp7_g5_workflow_check_only_example.json
```

Current check-only result:

- structural readiness = true;
- API readiness = false;
- model call attempted = false;
- API call attempted = false.

Mock command:

```powershell
python scripts\run_evp7_g5_llm_workflow.py `
  --mock-policy schema_visible_rule `
  --reviews-out data\reviews\evp7_g5_workflow_mock_reviews.jsonl `
  --metrics-out data\reviews\evp7_g5_workflow_mock_metrics.json `
  --summary-out data\reviews\evp7_g5_workflow_mock_summary.json
```

Current mock result:

- mock run = true;
- review records = 168;
- model call attempted = false;
- API call attempted = false;
- G5 metric scaffold = passed;
- G5 signal claim status = `requires_real_llm_verifier_outputs`.

The mock run validates the output and metric pipeline only. It does not support
any model-effect claim. This mock artifact was generated before `youtube-dl_7`
admission and remains scoped to the older 168-record cohort until explicitly
regenerated.

## Local Config Helper

Helper script:

```text
scripts/create_evp7_g5_llm_local_config.py
```

Dry-run command:

```powershell
python scripts\create_evp7_g5_llm_local_config.py `
  --dry-run `
  --dry-run-out data\reviews\evp7_g5_local_config_dry_run.json `
  --packet-md docs\experiments\evp7_g5_execution_confirmation_packet.md
```

Current dry-run result:

- local config write attempted = false;
- API call attempted = false;
- ready to write local config = false;
- missing confirmations = provider, model, cost ceiling, smoke scope, and
  full-run permission.

The helper refuses to write `configs/evp7_g5_llm.local.json` until all required
parameters are provided explicitly. The local config is ignored by Git and must
be checked with strict preflight before any API execution.
