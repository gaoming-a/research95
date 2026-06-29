# EVP-8-HARD E6 Evidence-Only Execution Packet v0.1

- Status: `ready`
- Packet variant: `e6_evidence_only_no_verdict`
- API call attempted: `false`
- Execution authorized by this packet: `false`
- Planned calls per model: `47`

## Removed Fields

- `rule_based_visible_merge_gate_decision`
- `rule_based_visible_merge_gate_reasons`
- `source_decision`

## Execute Commands After Explicit User Authorization

- `qwen_evidence_only_first`: `python scripts\run_evp8_hard_qwen_deepseek.py --execute --config configs\evp8_hard_e6_evidence_only.local.json --model-id qwen/qwen3.7-max`
  - proceed if: summary.run_gate == passed and parsed reviews contain exactly 47 candidate decisions
  - outputs:
    - `ignored_raw_responses`: `outputs/evp8_hard_e6_evidence_only_full/qwen_qwen3.7-max/raw_responses.jsonl`
    - `tracked_summary`: `data/reviews/evp8_hard_e6_evidence_only_qwen_qwen3.7-max_full_summary.json`
    - `tracked_parsed_reviews`: `data/reviews/evp8_hard_e6_evidence_only_qwen_qwen3.7-max_full_reviews.jsonl`
- `audit_after_qwen_evidence_only`: `python scripts\audit_evp8_hard_e6_evidence_only_results.py --out data\protocols\evp8_hard_e6_evidence_only_result_audit_v0_1.json`
  - proceed if: audit status is passed or Qwen-only partial with complete Qwen coverage
  - outputs:
    - `tracked_result_audit`: `data/protocols/evp8_hard_e6_evidence_only_result_audit_v0_1.json`
- `deepseek_evidence_only_second`: `python scripts\run_evp8_hard_qwen_deepseek.py --execute --config configs\evp8_hard_e6_evidence_only.local.json --model-id deepseek/deepseek-v4-pro`
  - proceed if: Qwen evidence-only audit has complete Qwen coverage and user explicitly authorizes DeepSeek
  - outputs:
    - `ignored_raw_responses`: `outputs/evp8_hard_e6_evidence_only_full/deepseek_deepseek-v4-pro/raw_responses.jsonl`
    - `tracked_summary`: `data/reviews/evp8_hard_e6_evidence_only_deepseek_deepseek-v4-pro_full_summary.json`
    - `tracked_parsed_reviews`: `data/reviews/evp8_hard_e6_evidence_only_deepseek_deepseek-v4-pro_full_reviews.jsonl`

## Primary Opportunity Set

- Source: `data/reviews/evp8_hard_false_accept_case_analysis_v0_1.json`
- Repeated false accepts: `9`
- Rule: measure whether the nine repeated false accepts change from accept to reject/escalate

## Stop Gates

- User has not explicitly authorized EVP-8-HARD E6-evidence-only Qwen API.
- Ignored local config configs/evp8_hard_e6_evidence_only.local.json is missing.
- Tracked example config is used for --execute.
- Any expected evidence-only output already exists before execution.
- Existing E6-full Qwen/DeepSeek summaries would be overwritten.
- Rendered prompt text or raw model response would be written to tracked files.
- Parsed review JSONL contains raw_response_text, provider response object, rendered prompt, or prompt text.
- Evidence-only result is interpreted as automatic correctness verification instead of risk handling.

## Checks

- example_config_exists: `true`
- local_config_exists: `true`
- local_config_path_boundary: `true`
- example_config_not_authorized: `true`
- local_config_not_authorized: `true`
- local_config_packet_variant: `true`
- check_only_passed: `true`
- packet_variant_is_evidence_only: `true`
- candidate_count_47: `true`
- verdict_fields_removed: `true`
- check_only_no_api: `true`
- check_only_no_raw_outputs: `true`
- false_accept_analysis_ready: `true`
- expected_evidence_only_outputs_absent: `true`

## Claim Boundary

This packet prepares an evidence-only ablation. It is not an API authorization and not a model result.
