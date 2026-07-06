# EVP-8 Realistic Agent Generation Dry-Run Audit v0.2

Date: 2026-06-29

This audit summarizes the no-API generation dry-run. It stores prompt
hash/count metadata only, not prompt text, patch diffs, raw responses, or
provider response objects.

## Summary

- audit status: `passed`
- run id: `evp8_realistic_hardneg_scrapy_full_file_qwen_002`
- model: `qwen3.7-max`
- provider: `qwen_official`
- prompt version: `agent_full_file_v1`
- prompt count: 8
- candidate count: 0

Task prompt counts:

- `bugsinpy_scrapy_1`: 8

## Checks

- target_matrix_passed: passed (passed)
- dry_run_summary_declares_dry_run: passed (True)
- api_call_not_attempted: passed (False)
- patch_generation_not_attempted: passed (0)
- prompt_count_matches_target: passed ({'actual': 8, 'expected': 8})
- summary_prompt_count_matches_manifest: passed (8)
- target_task_coverage_complete: passed (['bugsinpy_scrapy_1'])
- per_task_variant_counts_match: passed ({'bugsinpy_scrapy_1': 8})
- variant_pairs_unique: passed (8)
- label_leakage_checks_passed: passed ({'passed': 8})
- prompt_hash_present_for_all: passed (0)
- prompt_char_count_present_for_all: passed (0)
- forbidden_prompt_manifest_keys_absent: passed ([])
- raw_response_dir_absent: passed (outputs\evp8_realistic_hardneg_scrapy_full_file_qwen_002\raw)
- candidates_pending_absent_or_empty: passed (outputs\evp8_realistic_hardneg_scrapy_full_file_qwen_002\candidates.pending.jsonl)
- evidence_packets_pending_absent_or_empty: passed (outputs\evp8_realistic_hardneg_scrapy_full_file_qwen_002\evidence_packets.pending.jsonl)

## Next Gate

Explicit generation API authorization is required before replacing --dry-run with --execute. Generated candidates must then be validated and relabeled before any realistic verifier cohort is built.
