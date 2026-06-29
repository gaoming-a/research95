# EVP-8 Realistic Agent Generation Dry-Run Audit v0.3

Date: 2026-06-29

This audit summarizes the no-API generation dry-run. It stores prompt
hash/count metadata only, not prompt text, patch diffs, raw responses, or
provider response objects.

## Summary

- audit status: `passed`
- run id: `evp8_realistic_agent_generation_dryrun_supplement_002`
- model: `qwen3.7-max`
- provider: `qwen_official`
- prompt version: `agent_edit_plan_v1`
- prompt count: 5
- candidate count: 0

Task prompt counts:

- `bugsinpy_PySnooper_3`: 1
- `bugsinpy_cookiecutter_1`: 1
- `bugsinpy_cookiecutter_2`: 1
- `bugsinpy_cookiecutter_3`: 1
- `bugsinpy_tqdm_9`: 1

## Checks

- target_matrix_passed: passed (passed)
- dry_run_summary_declares_dry_run: passed (True)
- api_call_not_attempted: passed (False)
- patch_generation_not_attempted: passed (0)
- prompt_count_matches_target: passed ({'actual': 5, 'expected': 5})
- summary_prompt_count_matches_manifest: passed (5)
- target_task_coverage_complete: passed (['bugsinpy_PySnooper_3', 'bugsinpy_cookiecutter_1', 'bugsinpy_cookiecutter_2', 'bugsinpy_cookiecutter_3', 'bugsinpy_tqdm_9'])
- per_task_variant_counts_match: passed ({'bugsinpy_PySnooper_3': 1, 'bugsinpy_cookiecutter_1': 1, 'bugsinpy_cookiecutter_2': 1, 'bugsinpy_cookiecutter_3': 1, 'bugsinpy_tqdm_9': 1})
- variant_pairs_unique: passed (5)
- label_leakage_checks_passed: passed ({'passed': 5})
- prompt_hash_present_for_all: passed (0)
- prompt_char_count_present_for_all: passed (0)
- forbidden_prompt_manifest_keys_absent: passed ([])
- raw_response_dir_absent: passed (outputs\evp8_realistic_agent_generation_dryrun_supplement_002\raw)
- candidates_pending_absent_or_empty: passed (outputs\evp8_realistic_agent_generation_dryrun_supplement_002\candidates.pending.jsonl)
- evidence_packets_pending_absent_or_empty: passed (outputs\evp8_realistic_agent_generation_dryrun_supplement_002\evidence_packets.pending.jsonl)

## Next Gate

Explicit generation API authorization is required before replacing --dry-run with --execute. Generated candidates must then be validated and relabeled before any realistic verifier cohort is built.
