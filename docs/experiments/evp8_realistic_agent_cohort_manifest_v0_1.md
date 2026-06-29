# EVP-8 Realistic Agent Cohort Manifest v0.1

Date: 2026-06-30

- status: `passed`
- cohort id: `EVP-8-REALISTIC-AGENT`
- candidate count: 53
- non-trivial hard negatives: 52
- baseline decisions: `{'escalate': 53}`
- headroom gate ready: `False`
- headroom block reason: Visible tests have not been executed for the realistic cohort yet.

## Outputs

- evaluator_manifest: `data/patches/evp8_realistic_agent_evaluator_manifest_v0_1.jsonl`
- model_visible_seed: `data/evidence/evp8_realistic_agent_model_visible_seed_v0_1.jsonl`
- rule_only_baseline: `data/baselines/evp8_realistic_agent_rule_only_baseline_v0_1.jsonl`

## Label Counts

- `correct`: 1
- `test_passing_wrong`: 52

## Project Counts

- `PySnooper`: 11
- `cookiecutter`: 30
- `tqdm`: 12

## Checks

- source_inventory_v0_4_phase1_ready: passed (True)
- candidate_count_at_least_50: passed (53)
- model_visible_count_matches_evaluator: passed (53)
- baseline_count_matches_evaluator: passed (53)
- model_visible_forbidden_fields_absent: passed ([])
- all_candidates_patch_applied: passed (True)
- rule_only_baseline_all_escalate_until_visible_tests_run: passed ({'escalate': 53})

## Next Step

run declared visible tests for the realistic cohort and build the visible-tool headroom baseline
