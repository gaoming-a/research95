# EVP-8 DeepSeek/Qwen First-Batch Full-Run Packet v0.1

- Status: `ready`
- API call attempted: `false`
- Raw outputs generated: `false`
- Execution authorized by this packet: `false`
- Planned calls per model: `686`
- Local config: `configs/evp8_deepseek_qwen.local.json`

## Guard Commands

1. `git status --short --branch --untracked-files=all`
1. `python scripts\audit_evp8_protocol_spec.py --check`
1. `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
1. `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --run-scope full --config configs\evp8_deepseek_qwen.local.json`
1. `python scripts\write_evp8_first_batch_full_run_packet.py --check`
1. `python scripts\audit_evp8_first_batch_full_results.py --check`
1. `python scripts\summarize_evp8_first_batch_full_synthesis.py --check`
1. `git status --short --ignored configs\evp8_deepseek_qwen.local.json outputs artifacts .env data\reviews`

## Execute Commands After Explicit User Authorization

- `deepseek_first_batch_full_first`: `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --run-scope full --config configs\evp8_deepseek_qwen.local.json --model-id deepseek/deepseek-v4-pro`
  - request model: `deepseek-v4-pro`
  - provider route: `deepseek_official`
  - outputs: `data/reviews/evp8_deepseek_deepseek-v4-pro_full_summary.json`, `outputs/evp8_phase1_deepseek_qwen_full/deepseek_deepseek-v4-pro/raw_responses.jsonl`
  - proceed if: tracked_summary.first_batch_full_gate == passed and tracked_summary.usage_cost_gate == passed
- `qwen_first_batch_full_after_deepseek_gate`: `python scripts\run_evp8_deepseek_qwen_smoke.py --execute --run-scope full --config configs\evp8_deepseek_qwen.local.json --model-id qwen/qwen3.7-max`
  - request model: `qwen3.7-max`
  - provider route: `qwen_official`
  - outputs: `data/reviews/evp8_qwen_qwen3.7-max_full_summary.json`, `outputs/evp8_phase1_deepseek_qwen_full/qwen_qwen3.7-max/raw_responses.jsonl`
  - proceed if: DeepSeek first-batch full audit passed first; this Qwen summary must also pass parse and usage/cost gates.

## Post-Full-Run Commands

1. `python scripts\audit_evp8_first_batch_full_results.py --check`
1. `python scripts\summarize_evp8_first_batch_full_synthesis.py --check`

## Stop Gates

- Any guard command fails.
- Any expected first-batch full output path already exists before execution.
- Local config is not ignored under configs/*.local.json.
- Rendered prompt text or raw model response would be written to tracked files.
- DeepSeek first-batch full run does not pass parse/schema/usage-cost gates.
- Qwen first-batch full run is attempted before DeepSeek first-batch full audit passes.
- Any first-batch full summary has unknown_cost_record_count > 0.
- Any executed run changes protocol id, candidate set id, prompt hash policy, evidence levels, provider route, model id, temperature, or max output tokens.
- Any hidden evaluator label becomes model-visible.
- Any protocol, prompt, schema, candidate-set, or evaluator-join bug requires a protocol version bump and affected-model rerun.

## Checks

- local_config_path_boundary: `true`
- protocol_audit_passed: `true`
- protocol_ready_for_preflight: `true`
- preflight_passed: `true`
- preflight_ready_for_user_execute_command: `true`
- preflight_no_key_values_printed: `true`
- full_check_only_passed: `true`
- full_check_only_scope: `true`
- full_packet_count: `true`
- full_candidate_count: `true`
- full_prompt_count: `true`
- full_prompt_hashes_unique: `true`
- full_check_no_api: `true`
- full_check_no_raw_outputs: `true`
- smoke_audit_passed: `true`
- smoke_synthesis_passed: `true`
- phase1_model_ids: `true`
- expected_full_outputs_absent: `true`

## Claim Boundary

This packet is a no-API first-batch full-run handoff. It is not LLM verifier evidence and does not authorize 686-call model runs without a separate explicit user command.
