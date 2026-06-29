# EVP-8-HARD DeepSeek After Qwen Packet v0.1

- Status: `ready`
- API call attempted: `false`
- Execution authorized by this packet: `false`
- Planned DeepSeek calls: `47`

## Precondition

- Qwen summary: `data/reviews/evp8_hard_qwen_qwen3.7-max_full_summary.json`
- Qwen audit: `data/protocols/evp8_hard_qwen_deepseek_result_audit_v0_1.json`
- Qwen run gate: `passed`
- Qwen decisions: `{'accept': 17, 'reject': 30}`

## Execute Command After Explicit User Authorization

- `python scripts\run_evp8_hard_qwen_deepseek.py --execute --config configs\evp8_hard_qwen_deepseek.local.json --model-id deepseek/deepseek-v4-pro`
  - outputs: `data/reviews/evp8_hard_deepseek_deepseek-v4-pro_full_summary.json`, `data/reviews/evp8_hard_deepseek_deepseek-v4-pro_full_reviews.jsonl`, `outputs/evp8_hard_qwen_deepseek_full/deepseek_deepseek-v4-pro/raw_responses.jsonl`
  - proceed if: summary.run_gate == passed and parsed reviews contain exactly 47 candidate decisions

## Post-Run Audit

- `python scripts\audit_evp8_hard_qwen_deepseek_results.py --out data\protocols\evp8_hard_qwen_deepseek_result_audit_v0_1.json`

## Stop Gates

- User has not explicitly authorized EVP-8-HARD DeepSeek API execution.
- Any DeepSeek expected output path already exists before execution.
- Qwen summary or Qwen audit is not passed.
- Local config is not ignored under configs/*.local.json.
- Tracked example config is used for --execute.
- DeepSeek run_gate or usage_cost_gate is not passed.
- DeepSeek parsed reviews do not contain exactly 47 unique candidate decisions.
- Tracked DeepSeek parsed reviews contain raw response text or provider response objects.

## Checks

- local_config_path_boundary: `true`
- local_config_execution_not_pre_authorized: `true`
- check_only_passed: `true`
- credential_presence_ready: `true`
- qwen_summary_passed: `true`
- qwen_parse_complete: `true`
- qwen_audit_passed: `true`
- qwen_audit_complete: `true`
- deepseek_outputs_absent: `true`

## Claim Boundary

This is a no-API DeepSeek-after-Qwen handoff. It records that Qwen has passed and DeepSeek outputs are absent; it does not authorize DeepSeek API execution.
