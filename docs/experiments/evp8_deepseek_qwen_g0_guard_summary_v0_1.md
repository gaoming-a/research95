# EVP-8 DeepSeek/Qwen G0 Guard Summary v0.1

- Status: `passed`
- API call attempted: `false`
- Raw outputs read: `false`
- Raw outputs generated: `false`
- Rendered prompt text read: `false`
- Post-smoke status before execution: `waiting_for_execution`

## Commands

- `protocol_audit`: `true`
  - command: `python scripts\audit_evp8_protocol_spec.py --check`
  - parsed: `{"api_call_attempted": false, "phase0_api_readiness": "ready_for_api_preflight", "protocol_spec_audit_status": "passed"}`
- `strict_preflight`: `true`
  - command: `python scripts\preflight_evp8_deepseek_qwen.py --config configs/evp8_deepseek_qwen.local.json --strict-api-ready`
  - parsed: `{"api_call_attempted": false, "api_key_values_printed": false, "preflight_status": "passed", "ready_for_user_execute_command": true}`
- `smoke_check_only`: `true`
  - command: `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs/evp8_deepseek_qwen.local.json`
  - parsed: `{"api_call_attempted": false, "check_only_status": "passed", "packet_count": 35, "prompt_hashes_unique_count": 35, "raw_outputs_generated": false}`
- `execution_packet`: `true`
  - command: `python scripts\write_evp8_smoke_execution_packet.py --check`
  - parsed: `{"api_call_attempted": false, "execution_authorized_by_packet": false, "packet_status": "ready", "raw_outputs_generated": false}`
- `post_smoke_audit_self_test`: `true`
  - command: `python scripts\audit_evp8_smoke_results.py --self-test`
  - parsed: `{"api_call_attempted": false, "case_count": 9, "raw_outputs_generated": false, "raw_outputs_read": false, "self_test_status": "passed", "tracked_outputs_written": false}`
- `post_smoke_audit_check`: `true`
  - command: `python scripts\audit_evp8_smoke_results.py --check`
  - parsed: `{"api_call_attempted": false, "audit_status": "waiting_for_execution", "raw_outputs_generated_by_audit": false, "raw_outputs_read": false, "rendered_prompt_text_read": false}`
- `smoke_synthesis_self_test`: `true`
  - command: `python scripts\summarize_evp8_smoke_synthesis.py --self-test`
  - parsed: `{"api_call_attempted": false, "case_count": 4, "raw_outputs_generated": false, "raw_outputs_read": false, "self_test_status": "passed", "tracked_outputs_written": false}`
- `smoke_synthesis_check`: `true`
  - command: `python scripts\summarize_evp8_smoke_synthesis.py --check`
  - parsed: `{"api_call_attempted": false, "audit_status": "waiting_for_execution", "raw_outputs_generated_by_synthesis": false, "raw_outputs_read": false, "synthesis_status": "waiting_for_execution"}`
- `expected_output_absence`: `true`
  - command: `read data/protocols/evp8_deepseek_qwen_smoke_execution_packet_v0_1.json`
  - parsed: `{"checked_output_count": 4, "existing_output_count": 0}`
  - `raw_responses` `outputs/evp8_phase1_deepseek_qwen_smoke/deepseek_deepseek-v4-pro/raw_responses.jsonl` exists: `false`
  - `tracked_summary` `data/reviews/evp8_deepseek_deepseek-v4-pro_smoke_summary.json` exists: `false`
  - `raw_responses` `outputs/evp8_phase1_deepseek_qwen_smoke/qwen_qwen3.7-max/raw_responses.jsonl` exists: `false`
  - `tracked_summary` `data/reviews/evp8_qwen_qwen3.7-max_smoke_summary.json` exists: `false`
- `ignored_boundary_status`: `true`
  - command: `git status --short --branch --ignored configs/evp8_deepseek_qwen.local.json outputs artifacts .env`

## Boundary

Only after explicit user authorization, execute DeepSeek smoke first.
