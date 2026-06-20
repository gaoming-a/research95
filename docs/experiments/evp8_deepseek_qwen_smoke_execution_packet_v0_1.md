# EVP-8 DeepSeek/Qwen Smoke Execution Packet v0.1

- Status: `ready`
- API call attempted: `false`
- Raw outputs generated: `false`
- Execution authorized by this packet: `false`
- Local config: `configs/evp8_deepseek_qwen.local.json`

## Guard Commands

1. `git status --short --branch --untracked-files=all`
1. `python scripts\check_evp8_deepseek_qwen_g0.py --check`
1. `python scripts\audit_evp8_protocol_spec.py --check`
1. `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
1. `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`
1. `python scripts\write_evp8_smoke_execution_packet.py --check`
1. `python scripts\audit_evp8_smoke_results.py --self-test`
1. `python scripts\audit_evp8_smoke_results.py --check`
1. `python scripts\summarize_evp8_smoke_synthesis.py --self-test`
1. `python scripts\summarize_evp8_smoke_synthesis.py --check`
1. `git status --short --ignored configs\evp8_deepseek_qwen.local.json outputs artifacts .env`

## Execute Commands After Explicit User Authorization

- `deepseek_smoke_first`: `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --config configs\evp8_deepseek_qwen.local.json --model-id deepseek/deepseek-v4-pro`
  - request model: `deepseek-v4-pro`
  - provider route: `deepseek_official`
  - outputs: `data/reviews/evp8_deepseek_deepseek-v4-pro_smoke_summary.json`, `outputs/evp8_phase1_deepseek_qwen_smoke/deepseek_deepseek-v4-pro/raw_responses.jsonl`
  - proceed if: tracked_summary.smoke_gate == passed and tracked_summary.usage_cost_gate == passed
- `qwen_smoke_after_deepseek_gate`: `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --config configs\evp8_deepseek_qwen.local.json --model-id qwen/qwen3.7-max`
  - request model: `qwen3.7-max`
  - provider route: `qwen_official`
  - outputs: `data/reviews/evp8_qwen_qwen3.7-max_smoke_summary.json`, `outputs/evp8_phase1_deepseek_qwen_smoke/qwen_qwen3.7-max/raw_responses.jsonl`
  - proceed if: DeepSeek smoke gate passed first; this Qwen summary must also pass parse and usage/cost gates.

## Stop Gates

- Any guard command fails.
- Local config is not ignored under configs/*.local.json.
- Rendered prompt text or raw model response would be written to tracked files.
- DeepSeek smoke does not pass parse/schema/usage-cost gates.
- Qwen smoke is attempted before DeepSeek smoke passes.
- Any smoke summary has unknown_cost_record_count > 0.
- Any executed run changes protocol id, candidate set id, prompt hash policy, evidence levels, provider route, or model id.
- Any hidden evaluator label becomes model-visible.

## Checks

- local_config_path_boundary: `true`
- protocol_audit_passed: `true`
- protocol_ready_for_preflight: `true`
- protocol_audit_no_api: `true`
- preflight_passed: `true`
- preflight_ready_for_user_execute_command: `true`
- preflight_no_api: `true`
- preflight_no_key_values_printed: `true`
- check_only_passed: `true`
- check_only_packet_count: `true`
- check_only_no_api: `true`
- check_only_no_raw_outputs: `true`
- check_only_selection_includes_youtube_dl: `true`
- phase1_model_ids: `true`

## Claim Boundary

This packet is a no-API execution handoff. It is not LLM verifier evidence and does not authorize API calls without an explicit user command.
