# EVP-8 Realistic Hard-Negative Source Probe Audit v0.1

- status: `passed`
- source kind: `curated_no_api_hard_negative_source_probe`
- candidates: 10
- project counts: `{'scrapy': 10}`
- candidate type counts: `{'buggy_noop': 1, 'correct_reference': 1, 'irrelevant_patch': 1, 'partial_fix': 7}`
- visible test outcomes: `{'failed': 4, 'passed': 6}`
- oracle passed: 1

This audit stores aggregate source-probe metadata only. It does not store
patch text, prompt text, raw model outputs, or rendered prompts.

## Checks

- api_call_not_attempted_by_source_probe: passed (False)
- raw_model_outputs_not_read: passed (False)
- patch_text_not_stored: passed (False)
- prompt_text_not_stored: passed (False)
- candidate_count_matches_summary: passed (10)
- evidence_count_matches_candidates: passed (10)
- evidence_ids_match_candidate_ids: passed (True)
- validation_all_validated: passed ({'validated': 10})
- visible_tests_completed: passed ({'completed': 10})

## Next Step

join validation with visible-test outcomes and refresh the combined hard-negative gate
