# EVP-8 Hard-Case Source Inventory v0.1

Date: 2026-06-29

This is a no-API source inventory for Phase B. It does not create an
`EVP-8-HARD` candidate manifest and does not store patch diffs, prompt text,
or raw model responses.

## Boundary Checks

- api_call_not_attempted: passed (False)
- raw_model_outputs_not_read: passed (False)
- old_evp8_cohort_not_mutated: passed (False)
- hard_candidate_manifest_not_created: passed (False)
- prompt_text_not_stored: passed (False)
- source_files_scanned: passed (34)
- evp7_controlled_cohort_detected: passed (98)

## Existing Controlled Cohort

- source: `data/patches/evp7_candidates.jsonl`
- status: `already_used_in_evp8_controlled_cohort`
- candidates: 98
- tasks: 21
- hard negatives already inside controlled cohort: 41
- rule-only E6 opportunity cases: 6 (5 false accepts, 1 false rejects)

Interpretation: this cohort can be used as prior evidence and source-pattern
context, but it must not be counted as new hard-case extension data.

## Local Source Summary

- candidate source files scanned: 34
- candidate records scanned: 260
- non-promoted candidate records: 68 (unique: 49)
- non-promoted eligible hard negatives: 48 (unique: 20)
- AI/agent candidate records: 38 (unique: 19)
- AI/agent eligible hard negatives: 23 (unique: 13)

Source status counts:

- `already_promoted_to_evp7_controlled`: 22
- `legacy_pilot_or_duplicate_output`: 3
- `not_promoted_to_evp7_controlled`: 9

## Candidate Sources

| source | status | kind | candidates | eligible new hard negatives | validation joins |
| --- | --- | --- | ---: | ---: | ---: |
| `outputs/build_default_check/candidates.jsonl` | `legacy_pilot_or_duplicate_output` | `constructed_or_reference` | 30 | 0 | 0 |
| `outputs/cookiecutter1_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/cookiecutter2_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 11 | 0 | 11 |
| `outputs/cookiecutter3_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/httpie5_stability_audit_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 6 | 0 | 0 |
| `outputs/httpie_agent_patch_qwen37_httpie5_strict_001/candidates.pending.jsonl` | `not_promoted_to_evp7_controlled` | `ai_or_agent_generated` | 1 | 1 | 1 |
| `outputs/httpie_agent_patch_qwen37_httpie5_strict_001/candidates.relabeled.jsonl` | `not_promoted_to_evp7_controlled` | `ai_or_agent_generated` | 1 | 1 | 1 |
| `outputs/httpie_agent_patch_stage_ab_001/candidates.pending.jsonl` | `not_promoted_to_evp7_controlled` | `ai_or_agent_generated` | 8 | 8 | 8 |
| `outputs/httpie_agent_patch_stage_ab_001/candidates.relabeled.jsonl` | `not_promoted_to_evp7_controlled` | `ai_or_agent_generated` | 8 | 8 | 8 |
| `outputs/httpie_ai_patch_stage_ab_001/candidates.jsonl` | `not_promoted_to_evp7_controlled` | `ai_or_agent_generated` | 10 | 1 | 10 |
| `outputs/httpie_ai_patch_stage_ab_001/candidates.pending.jsonl` | `not_promoted_to_evp7_controlled` | `ai_or_agent_generated` | 10 | 4 | 10 |
| `outputs/httpie_stage_ab_001/candidates.jsonl` | `not_promoted_to_evp7_controlled` | `constructed_or_reference` | 22 | 7 | 22 |
| `outputs/luigi3_stability_audit_001/candidates.jsonl` | `not_promoted_to_evp7_controlled` | `constructed_or_reference` | 5 | 0 | 0 |
| `outputs/luigi4_stability_audit_001/candidates.jsonl` | `not_promoted_to_evp7_controlled` | `constructed_or_reference` | 3 | 0 | 0 |
| `outputs/patch_verification_pilot_001/candidates.jsonl` | `legacy_pilot_or_duplicate_output` | `constructed_or_reference` | 30 | 9 | 30 |
| `outputs/patch_verification_pilot_repro_001/candidates.jsonl` | `legacy_pilot_or_duplicate_output` | `constructed_or_reference` | 30 | 9 | 30 |
| `outputs/pysnooper1_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 6 | 0 | 6 |
| `outputs/pysnooper3_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/thefuck1_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/tqdm9_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 7 | 0 | 7 |
| `outputs/youtubedl11_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/youtubedl16_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/youtubedl17_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/youtubedl20_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/youtubedl21_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/youtubedl23_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/youtubedl2_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/youtubedl37_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/youtubedl43_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/youtubedl4_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/youtubedl5_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/youtubedl5_candidate_validation_001/candidates_after_format_check.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/youtubedl6_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |
| `outputs/youtubedl7_candidate_validation_001/candidates.jsonl` | `already_promoted_to_evp7_controlled` | `constructed_or_reference` | 4 | 0 | 4 |

## Phase B Readiness

- ready for hard-case manifest: `False`
- reason: The local inventory finds reusable sources and reaches the minimum 20 unique non-promoted eligible hard negatives, but these have not yet been curated into a separate manifest and no hard-case tool-only opportunity baseline has been built.
- next gate: Construct a separate no-API EVP-8-HARD candidate draft only after adding or validating enough non-promoted hard negatives; then build a tool-only baseline and stop before API if opportunity cases remain below 10.

Plain-language conclusion: the project has enough historical material to
explain why hard cases matter, and it has some validated AI/agent patch
sources. It does not yet have enough fresh non-promoted hard negatives or a
new hard-case tool-only opportunity baseline to justify another model API run.
