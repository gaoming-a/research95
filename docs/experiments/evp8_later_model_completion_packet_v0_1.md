# EVP-8 Later-Model Completion Packet v0.1

- Status: `ready`
- API call attempted: `false`
- Raw outputs generated/read: `false` / `false`
- Execution authorized by this packet: `false`
- Planned calls per later model: `686`
- Planned total later-model calls: `2058`
- Planning cost ceiling: `USD 30.0`

## Models

| model id | provider route | tracked summary | raw responses |
|---|---|---|---|
| `moonshotai/kimi-k2.6` | `openrouter_pinned_exact_model_id` | `data/reviews/evp8_moonshotai_kimi-k2.6_full_summary.json` | `outputs/evp8_phase2_later_models_full/moonshotai_kimi-k2.6/raw_responses.jsonl` |
| `mistralai/devstral-2512` | `openrouter_pinned_exact_model_id` | `data/reviews/evp8_mistralai_devstral-2512_full_summary.json` | `outputs/evp8_phase2_later_models_full/mistralai_devstral-2512/raw_responses.jsonl` |
| `google/gemini-2.5-flash` | `openrouter_pinned_exact_model_id` | `data/reviews/evp8_google_gemini-2.5-flash_full_summary.json` | `outputs/evp8_phase2_later_models_full/google_gemini-2.5-flash/raw_responses.jsonl` |

## Guard Commands

1. `git status --short --branch --untracked-files=all`
1. `python scripts\audit_evp8_protocol_spec.py --check`
1. `python scripts\audit_openrouter_model_catalog.py --model moonshotai/kimi-k2.6 --model mistralai/devstral-2512 --model google/gemini-2.5-flash --out-json data\protocols\evp8_later_model_openrouter_catalog_audit_v0_1.json --out-md docs\experiments\evp8_later_model_openrouter_catalog_audit_v0_1.md`
1. `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --run-scope full --config configs\evp8_deepseek_qwen.local.json`
1. `python scripts\audit_evp8_first_batch_full_results.py --check`
1. `python scripts\summarize_evp8_first_batch_full_synthesis.py --check`
1. `python scripts\write_evp8_later_model_completion_packet.py --check`

## Planned Execute Command Templates

- `moonshotai/kimi-k2.6`: `python scripts\run_evp8_later_model_full.py --execute --run-scope full --config configs\evp8_later_models.local.json --model-id moonshotai/kimi-k2.6`
  - proceed if: G7 packet passed, later-model runner/preflight are implemented and checked, OPENROUTER_API_KEY is present in ignored local env, and user explicitly authorizes this model.
- `mistralai/devstral-2512`: `python scripts\run_evp8_later_model_full.py --execute --run-scope full --config configs\evp8_later_models.local.json --model-id mistralai/devstral-2512`
  - proceed if: G7 packet passed, later-model runner/preflight are implemented and checked, OPENROUTER_API_KEY is present in ignored local env, and user explicitly authorizes this model.
- `google/gemini-2.5-flash`: `python scripts\run_evp8_later_model_full.py --execute --run-scope full --config configs\evp8_later_models.local.json --model-id google/gemini-2.5-flash`
  - proceed if: G7 packet passed, later-model runner/preflight are implemented and checked, OPENROUTER_API_KEY is present in ignored local env, and user explicitly authorizes this model.

## Stop Gates

- Any G7 packet check fails.
- OpenRouter public catalog no longer contains one of the pinned model IDs.
- OPENROUTER_API_KEY is missing from ignored local environment before execution.
- Later-model runner or local preflight is missing or unaudited.
- Any expected later-model output already exists before execution without an explicit resume path.
- Any raw response or rendered prompt text would be written to tracked files.
- Any model silently changes model ID or provider route without being recorded.
- Any summary has invalid parse, unknown cost, missing usage, or missing per-level aggregate.
- Any protocol, prompt, schema, candidate-set, or evaluator-join bug requires a protocol version bump and affected-model rerun.

## Checks

- protocol_audit_passed: `true`
- protocol_ready_for_preflight: `true`
- full_check_only_passed: `true`
- full_packet_count: `true`
- full_candidate_count: `true`
- full_prompt_hashes_unique: `true`
- first_batch_audit_passed: `true`
- first_batch_audit_no_raw_outputs_read: `true`
- first_batch_synthesis_passed: `true`
- first_batch_synthesis_no_raw_outputs_read: `true`
- later_model_ids_match_protocol: `true`
- openrouter_catalog_all_available: `true`
- openrouter_catalog_ids_match_protocol: `true`
- expected_later_outputs_absent: `true`

## Claim Boundary

This packet is a no-API later-model completion handoff. It does not authorize Kimi, Devstral, or Gemini API calls and does not support five-model journal conclusions until the later-model runs and audits pass.
