# EVP-8 Realistic Agent-Patch Source Inventory v0.4

Date: 2026-06-30

This is a no-API Phase 0 inventory for the realistic/agent-patch
follow-up cohort. It scans candidate source files and writes aggregate
statistics only. It does not create a candidate manifest, store patch
diffs, render prompts, or read raw model responses.

## Boundary Checks

- api_call_not_attempted: passed (False)
- raw_model_outputs_not_read: passed (False)
- candidate_manifest_not_created: passed (False)
- prompt_text_not_stored: passed (False)
- patch_diff_not_stored_in_output: passed (False)
- candidate_source_files_scanned: passed (44)
- existing_evp8_controlled_manifest_detected: passed (data/patches/evp7_candidates.jsonl)
- existing_evp8_hard_manifest_detected: passed (data/patches/evp8_hard_evaluator_manifest_v0_1.jsonl)

## Aggregate Source Counts

- candidate source files scanned: 44
- candidate records scanned: 547
- usable records across all sources: 389
- agent-like records across all sources: 189
- non-trivial hard negatives across all sources: 324

Fresh sources exclude the existing EVP-8 controlled cohort and the current
EVP-8-HARD cohort.

- unique fresh usable candidates: 53
- unique fresh agent-like candidates: 53
- unique fresh non-trivial hard negatives: 53
- fresh projects: 3 (PySnooper, cookiecutter, tqdm)
- pending usable candidates: 13
- pending agent-like candidates: 13
- pending non-trivial hard negatives: 13

## Readiness

- ready for Phase 1 candidate curation: `True`
- ready for API: `False`
- API block reason: Phase 0 inventory cannot authorize model execution; visible-tool baseline gate has not been built.

Phase 1 count gate:

- `fresh_usable_candidates_at_least_50`: passed
- `fresh_agent_like_candidates_at_least_30`: passed
- `fresh_nontrivial_hard_negatives_at_least_25`: passed
- `fresh_projects_at_least_3`: passed

## Source Status Counts

- `already_curated_into_evp8_hard_source`: 8
- `already_promoted_to_evp8_controlled_source`: 22
- `existing_evp8_controlled_manifest`: 1
- `existing_evp8_hard_manifest`: 1
- `fresh_realistic_agent_source`: 3
- `legacy_pilot_or_duplicate_source`: 3
- `pending_unvalidated_source`: 6

## Source Category Counts

- `agent_like_generated`: 23
- `controlled_negative`: 280
- `human_reference`: 78
- `real_agent_generated`: 166

## Candidate Sources

| source | status | candidates | usable | agent-like | hard negatives | fresh usable | fresh agent-like | fresh hard negatives | pending usable |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `data/patches/evp7_candidates.jsonl` | `existing_evp8_controlled_manifest` | 98 | 98 | 0 | 42 | 0 | 0 | 0 | 0 |
| `data/patches/evp8_hard_evaluator_manifest_v0_1.jsonl` | `existing_evp8_hard_manifest` | 47 | 0 | 13 | 23 | 0 | 0 | 0 | 0 |
| `data/patches/evp8_hard_extra_httpie1_errno_partials/candidates.jsonl` | `already_curated_into_evp8_hard_source` | 3 | 3 | 0 | 3 | 0 | 0 | 0 | 0 |
| `data/patches/evp8_hard_extra_luigi4_partial/candidates.jsonl` | `already_curated_into_evp8_hard_source` | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| `outputs/build_default_check/candidates.jsonl` | `legacy_pilot_or_duplicate_source` | 30 | 0 | 0 | 9 | 0 | 0 | 0 | 0 |
| `outputs/cookiecutter1_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 1 | 0 | 0 | 0 | 0 |
| `outputs/cookiecutter2_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 11 | 11 | 0 | 8 | 0 | 0 | 0 | 0 |
| `outputs/cookiecutter3_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 1 | 0 | 0 | 0 | 0 |
| `outputs/evp8_realistic_agent_generation_qwen_primary_001/candidates.pending.jsonl` | `pending_unvalidated_source` | 54 | 0 | 54 | 54 | 0 | 0 | 0 | 0 |
| `outputs/evp8_realistic_agent_generation_qwen_supplement_001/candidates.pending.jsonl` | `pending_unvalidated_source` | 10 | 0 | 10 | 10 | 0 | 0 | 0 | 0 |
| `outputs/evp8_realistic_agent_generation_qwen_supplement_002/candidates.pending.jsonl` | `pending_unvalidated_source` | 5 | 0 | 5 | 5 | 0 | 0 | 0 | 0 |
| `outputs/evp8_realistic_agent_validation_qwen_primary_001/candidates.relabeled.jsonl` | `fresh_realistic_agent_source` | 54 | 54 | 54 | 54 | 46 | 46 | 46 | 0 |
| `outputs/evp8_realistic_agent_validation_qwen_supplement_001/candidates.relabeled.jsonl` | `fresh_realistic_agent_source` | 10 | 10 | 10 | 10 | 2 | 2 | 2 | 0 |
| `outputs/evp8_realistic_agent_validation_qwen_supplement_002/candidates.relabeled.jsonl` | `fresh_realistic_agent_source` | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 0 |
| `outputs/httpie5_stability_audit_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 6 | 6 | 0 | 3 | 0 | 0 | 0 | 0 |
| `outputs/httpie_agent_patch_qwen37_httpie5_strict_001/candidates.pending.jsonl` | `pending_unvalidated_source` | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 1 |
| `outputs/httpie_agent_patch_qwen37_httpie5_strict_001/candidates.relabeled.jsonl` | `already_curated_into_evp8_hard_source` | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
| `outputs/httpie_agent_patch_stage_ab_001/candidates.pending.jsonl` | `pending_unvalidated_source` | 8 | 8 | 8 | 8 | 0 | 0 | 0 | 8 |
| `outputs/httpie_agent_patch_stage_ab_001/candidates.relabeled.jsonl` | `already_curated_into_evp8_hard_source` | 8 | 8 | 8 | 8 | 0 | 0 | 0 | 0 |
| `outputs/httpie_ai_patch_stage_ab_001/candidates.jsonl` | `already_curated_into_evp8_hard_source` | 10 | 4 | 10 | 10 | 0 | 0 | 0 | 0 |
| `outputs/httpie_ai_patch_stage_ab_001/candidates.pending.jsonl` | `pending_unvalidated_source` | 10 | 4 | 10 | 10 | 0 | 0 | 0 | 4 |
| `outputs/httpie_stage_ab_001/candidates.jsonl` | `already_curated_into_evp8_hard_source` | 22 | 22 | 0 | 7 | 0 | 0 | 0 | 0 |
| `outputs/luigi3_stability_audit_001/candidates.jsonl` | `already_curated_into_evp8_hard_source` | 5 | 5 | 0 | 2 | 0 | 0 | 0 | 0 |
| `outputs/luigi4_stability_audit_001/candidates.jsonl` | `already_curated_into_evp8_hard_source` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| `outputs/patch_verification_pilot_001/candidates.jsonl` | `legacy_pilot_or_duplicate_source` | 30 | 30 | 0 | 9 | 0 | 0 | 0 | 0 |
| `outputs/patch_verification_pilot_repro_001/candidates.jsonl` | `legacy_pilot_or_duplicate_source` | 30 | 30 | 0 | 9 | 0 | 0 | 0 | 0 |
| `outputs/pysnooper1_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 6 | 6 | 0 | 3 | 0 | 0 | 0 | 0 |
| `outputs/pysnooper3_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 1 | 0 | 0 | 0 | 0 |
| `outputs/thefuck1_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 2 | 0 | 0 | 0 | 0 |
| `outputs/tqdm9_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 7 | 7 | 0 | 4 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl11_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 1 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl16_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 2 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl17_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 2 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl20_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 2 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl21_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 2 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl23_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 2 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl2_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 1 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl37_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 2 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl43_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 1 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl4_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 1 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl5_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 1 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl5_candidate_validation_001/candidates_after_format_check.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 1 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl6_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 1 | 0 | 0 | 0 | 0 |
| `outputs/youtubedl7_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp8_controlled_source` | 4 | 4 | 0 | 1 | 0 | 0 | 0 | 0 |

## Interpretation

The inventory is a source-readiness gate, not an experiment result. Existing
EVP-8 and EVP-8-HARD candidates remain useful as historical evidence and
failure-mode examples, but they are not counted as fresh realistic/agent
cohort material. Model APIs remain blocked until a separate curated cohort
and visible-tool headroom baseline exist.

Next step: If Phase 1 count gate passes, curate a separate evaluator/model-visible manifest without API. If it fails, add new realistic agent-like candidates or validate pending sources before any LLM run.
