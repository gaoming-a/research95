# EVP-8-HARD Qwen/DeepSeek Execution Packet v0.1

- Status: `ready`
- API call attempted: `false`
- Raw outputs generated: `false`
- Execution authorized by this packet: `false`
- Planned calls per model: `47`
- Local config: `configs/evp8_hard_qwen_deepseek.local.json`

## Guard Commands

1. `git status --short --branch --untracked-files=all`
1. `python -m py_compile scripts\run_evp8_hard_qwen_deepseek.py scripts\audit_evp8_hard_qwen_deepseek_results.py scripts\write_evp8_hard_qwen_deepseek_execution_packet.py`
1. `python scripts\run_evp8_hard_qwen_deepseek.py --check-only --config configs\evp8_hard_qwen_deepseek.local.json --summary-out data\protocols\evp8_hard_qwen_deepseek_check_only_v0_1.json`
1. `python scripts\audit_evp8_hard_qwen_deepseek_results.py --out data\protocols\evp8_hard_qwen_deepseek_result_audit_v0_1.json`
1. `python scripts\write_evp8_hard_qwen_deepseek_execution_packet.py --check`
1. `git status --short --ignored configs\evp8_hard_qwen_deepseek.local.json outputs .env data\reviews`

## Execute Commands After Explicit User Authorization

- `qwen_hard_full_first`: `python scripts\run_evp8_hard_qwen_deepseek.py --execute --config configs\evp8_hard_qwen_deepseek.local.json --model-id qwen/qwen3.7-max`
  - request model: `qwen3.7-max`
  - provider route: `qwen_official`
  - outputs:
    - `ignored_raw_responses`: `outputs/evp8_hard_qwen_deepseek_full/qwen_qwen3.7-max/raw_responses.jsonl`
    - `tracked_summary`: `data/reviews/evp8_hard_qwen_qwen3.7-max_full_summary.json`
    - `tracked_parsed_reviews`: `data/reviews/evp8_hard_qwen_qwen3.7-max_full_reviews.jsonl`
  - proceed if: summary.run_gate == passed and parsed reviews contain exactly 47 candidate decisions
- `audit_after_qwen`: `python scripts\audit_evp8_hard_qwen_deepseek_results.py --out data\protocols\evp8_hard_qwen_deepseek_result_audit_v0_1.json`
  - outputs:
    - `tracked_result_audit`: `data/protocols/evp8_hard_qwen_deepseek_result_audit_v0_1.json`
  - proceed if: audit_status == passed and qwen model coverage is complete
- `deepseek_hard_full_second`: `python scripts\run_evp8_hard_qwen_deepseek.py --execute --config configs\evp8_hard_qwen_deepseek.local.json --model-id deepseek/deepseek-v4-pro`
  - request model: `deepseek-v4-pro`
  - provider route: `deepseek_official`
  - outputs:
    - `ignored_raw_responses`: `outputs/evp8_hard_qwen_deepseek_full/deepseek_deepseek-v4-pro/raw_responses.jsonl`
    - `tracked_summary`: `data/reviews/evp8_hard_deepseek_deepseek-v4-pro_full_summary.json`
    - `tracked_parsed_reviews`: `data/reviews/evp8_hard_deepseek_deepseek-v4-pro_full_reviews.jsonl`
  - proceed if: Qwen audit passed first; DeepSeek summary.run_gate == passed
- `audit_after_deepseek`: `python scripts\audit_evp8_hard_qwen_deepseek_results.py --out data\protocols\evp8_hard_qwen_deepseek_result_audit_v0_1.json`
  - outputs:
    - `tracked_result_audit`: `data/protocols/evp8_hard_qwen_deepseek_result_audit_v0_1.json`
  - proceed if: audit_status == passed and both model coverages are complete

## Stop Gates

- Any guard command fails.
- Any expected model output path already exists before execution.
- User has not explicitly authorized API execution in this thread.
- Local config is not ignored under configs/*.local.json.
- Tracked example config is used for --execute.
- Rendered prompt text or raw model response would be written to tracked files.
- A model summary has run_gate != passed.
- Parsed review JSONL contains raw_response_text, provider response object, rendered prompt, or prompt text.
- Parsed review JSONL does not contain exactly 47 unique hard-case candidate decisions per executed model.
- Qwen audit does not pass before starting DeepSeek.
- Any hidden evaluator label or hidden oracle outcome becomes model-visible.

## Checks

- local_config_path_boundary: `true`
- local_config_execution_not_pre_authorized: `true`
- check_only_passed: `true`
- check_only_candidate_count: `true`
- check_only_packet_count_per_model: `true`
- check_only_only_e6: `true`
- check_only_no_api: `true`
- check_only_no_raw_outputs: `true`
- check_only_no_prompt_text_stored: `true`
- qwen_deepseek_credentials_present: `true`
- result_audit_waiting_or_passed: `true`
- result_audit_no_raw_read: `true`
- model_ids_qwen_first_configured: `true`
- expected_model_outputs_absent: `true`

## Claim Boundary

This packet is a no-API execution handoff for the EVP-8-HARD hard-case cohort. It is not an experiment result and does not authorize API calls without a separate explicit user command.
