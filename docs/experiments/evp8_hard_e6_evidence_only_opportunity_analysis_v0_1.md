# EVP-8-HARD E6 Evidence-Only Opportunity Analysis v0.1

- Status: `waiting_for_model_results`
- Opportunity set size: `9`
- API call attempted: `false`
- Raw model outputs read: `false`

## Purpose

This analysis focuses only on the nine candidates that the tool baseline,
Qwen E6-full, and DeepSeek E6-full all falsely accepted. It checks whether
the evidence-only ablation changes those accept decisions to reject or
escalate.

## Waiting State

No evidence-only parsed reviews exist yet. This is the expected
pre-authorization state.

Expected parsed review files:

- `data/reviews/evp8_hard_e6_evidence_only_qwen_qwen3.7-max_full_reviews.jsonl`
- `data/reviews/evp8_hard_e6_evidence_only_deepseek_deepseek-v4-pro_full_reviews.jsonl`

## Checks

- `api_call_not_attempted_by_analysis`: `true`
- `raw_model_outputs_not_read`: `true`
- `opportunity_set_size_is_9`: `true`
- `parsed_reviews_do_not_contain_raw_fields`: `true`
- `opportunity_coverage_complete_for_existing_models`: `true`
