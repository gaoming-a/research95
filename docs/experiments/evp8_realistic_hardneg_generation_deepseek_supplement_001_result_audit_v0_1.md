# EVP-8 Realistic Agent Generation Result Audit v0.1

- status: `passed`
- run dir: `outputs/evp8_realistic_hardneg_generation_deepseek_supplement_001`
- raw output content stored in this audit: `false`
- patch text stored in this audit: `false`
- prompt text stored in this audit: `false`

## Summary

- model/provider: `deepseek-v4-pro` / `deepseek_official`
- prompt version: `agent_edit_plan_v1`
- prompts/candidates/evidence packets: 12 / 12 / 12
- unique patch ids: 12
- unique patch-text hashes: 6
- raw response files: 12
- extra raw files from failed attempts: 0

## Task Counts

- `bugsinpy_httpie_1`: 3
- `bugsinpy_httpie_2`: 3
- `bugsinpy_httpie_3`: 3
- `bugsinpy_httpie_4`: 3

## Project Counts

- `httpie`: 12

## Boundary

- pending candidates contain evaluator-only fields: `true`
- pending candidates are model-visible inputs: `false`
- prompt manifest unexpected fields: `[]`
- evidence packet forbidden fields present: `[]`

## Checks

- generation_error_absent: passed (False)
- summary_run_id_expected: passed (evp8_realistic_hardneg_generation_deepseek_supplement_001)
- summary_model_expected: passed (deepseek-v4-pro)
- summary_provider_expected: passed (deepseek_official)
- summary_not_dry_run: passed (False)
- summary_prompt_count_matches_expected: passed (12)
- summary_candidate_count_matches_expected: passed (12)
- prompt_manifest_count_matches_expected: passed (12)
- candidate_count_matches_expected: passed (12)
- evidence_packet_count_matches_expected: passed (12)
- unique_patch_ids_match_expected: passed (12)
- unique_model_candidate_ids_match_expected: passed (12)
- evidence_candidate_ids_match_model_candidate_ids: passed (True)
- candidate_task_counts_match_plan: passed ({'bugsinpy_httpie_1': 3, 'bugsinpy_httpie_2': 3, 'bugsinpy_httpie_3': 3, 'bugsinpy_httpie_4': 3})
- prompt_task_counts_match_plan: passed ({'bugsinpy_httpie_1': 3, 'bugsinpy_httpie_2': 3, 'bugsinpy_httpie_3': 3, 'bugsinpy_httpie_4': 3})
- all_labels_pending_validation: passed ({'pending_validation': 12})
- raw_response_files_at_least_candidates: passed (12)
- candidate_raw_hashes_present: passed (12)
- prompt_manifest_has_no_payload_fields: passed ([])
- evidence_packets_hide_evaluator_fields: passed ([])

## Next Step

validate generated candidates and relabel with evaluator-only outcomes before cohort construction
