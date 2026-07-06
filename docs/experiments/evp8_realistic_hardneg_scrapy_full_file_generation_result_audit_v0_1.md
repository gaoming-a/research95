# EVP-8 Realistic Agent Generation Result Audit v0.1

- status: `passed`
- run dir: `outputs/evp8_realistic_hardneg_scrapy_full_file_qwen_003`
- raw output content stored in this audit: `false`
- patch text stored in this audit: `false`
- prompt text stored in this audit: `false`

## Summary

- model/provider: `qwen3.7-max` / `qwen_official`
- prompt version: `agent_full_file_v1`
- prompts/candidates/evidence packets: 8 / 8 / 8
- unique patch ids: 8
- unique patch-text hashes: 4
- raw response files: 8
- extra raw files from failed attempts: 0

## Task Counts

- `bugsinpy_scrapy_1`: 8

## Project Counts

- `scrapy`: 8

## Boundary

- pending candidates contain evaluator-only fields: `true`
- pending candidates are model-visible inputs: `false`
- prompt manifest unexpected fields: `[]`
- evidence packet forbidden fields present: `[]`

## Checks

- generation_error_absent: passed (False)
- summary_run_id_expected: passed (evp8_realistic_hardneg_scrapy_full_file_qwen_003)
- summary_model_expected: passed (qwen3.7-max)
- summary_provider_expected: passed (qwen_official)
- summary_not_dry_run: passed (False)
- summary_prompt_count_matches_expected: passed (8)
- summary_candidate_count_matches_expected: passed (8)
- prompt_manifest_count_matches_expected: passed (8)
- candidate_count_matches_expected: passed (8)
- evidence_packet_count_matches_expected: passed (8)
- unique_patch_ids_match_expected: passed (8)
- unique_model_candidate_ids_match_expected: passed (8)
- evidence_candidate_ids_match_model_candidate_ids: passed (True)
- candidate_task_counts_match_plan: passed ({'bugsinpy_scrapy_1': 8})
- prompt_task_counts_match_plan: passed ({'bugsinpy_scrapy_1': 8})
- all_labels_pending_validation: passed ({'pending_validation': 8})
- raw_response_files_at_least_candidates: passed (8)
- candidate_raw_hashes_present: passed (8)
- prompt_manifest_has_no_payload_fields: passed ([])
- evidence_packets_hide_evaluator_fields: passed ([])

## Next Step

validate generated candidates and relabel with evaluator-only outcomes before cohort construction
