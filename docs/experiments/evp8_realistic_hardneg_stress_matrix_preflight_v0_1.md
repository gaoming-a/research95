# EVP-8 hard-negative stress matrix preflight v0.1

Status: `passed_with_no_verdict_blocked`

## Boundary

- No verifier API call was attempted.
- Raw model outputs were not generated.
- Rendered prompt text was not stored.
- Patch-bearing packets remain in ignored `outputs/**`; tracked files contain only counts, hashes, and boundary checks.
- The matrix is hard-negative stress-test evidence, not a pure agent-generated realistic cohort.

## Scope

- candidates: `31`
- models: `qwen/qwen3.7-max`, `deepseek/deepseek-v4-pro`, `google/gemini-2.5-flash`
- requested conditions: `current_merge_gate`, `e6_no_verdict`, `coverage_contestation`
- ready conditions: `current_merge_gate`, `coverage_contestation`
- requested calls if all conditions were ready: `279`
- effective ready calls: `186`

## Condition Gates

| condition | ready | reason | prompt |
| --- | --- | --- | --- |
| `current_merge_gate` | true | `ready` | `prompts/evp8_visible_evidence_merge_gate_v0_2.md` |
| `e6_no_verdict` | false | `blocked_no_verdict_transform_is_degenerate_for_stress_packets` | `prompts/evp8_visible_evidence_merge_gate_v0_2.md` |
| `coverage_contestation` | true | `ready` | `prompts/evp8_coverage_contestation_merge_gate_v0_1.md` |

## Composition

- project counts: `{"PySnooper": 9, "cookiecutter": 17, "scrapy": 5}`
- source kind counts: `{"curated_no_api_stress_source": 5, "model_generated_source": 26}`

## Checks

| check | passed | detail |
| --- | --- | --- |
| `api_call_not_attempted` | true | `false` |
| `raw_outputs_not_generated` | true | `false` |
| `rendered_prompt_text_not_stored` | true | `false` |
| `stress_cohort_summary_exists` | true | `"data/protocols/evp8_realistic_hardneg_stress_cohort_v0_1.json"` |
| `model_visible_packets_exists` | true | `"outputs/evp8_realistic_hardneg_stress_cohort_v0_1/model_visible_packets.jsonl"` |
| `candidate_count_is_31` | true | `31` |
| `candidate_ids_unique` | true | `31` |
| `tracked_summary_candidate_count_matches_packets` | true | `{"packets": 31, "summary": 31}` |
| `visible_pass_all_packets` | true | `31` |
| `forbidden_label_keys_absent_from_packets` | true | `{}` |
| `sanitizer_removed_hidden_metadata` | true | `{"max": 3, "min": 3}` |
| `ready_conditions_are_nonempty` | true | `["current_merge_gate", "coverage_contestation"]` |
| `no_verdict_degenerate_condition_blocked` | true | `[{"boundary_findings": [], "condition_id": "e6_no_verdict", "metadata_fields_removed_total": 93, "packet_count": 31, "packet_transform": "sanitized_stress_packet_minus_verdict_fields", "prompt_template": "prompts/evp8_visible_evidence_merge_gate_v0_2.md", "prompt_template_sha256": "3e64dbedf9b0155f3013f30a4044631dc18d4f8d22920620941e16bd0e7d09f0", "readiness_reason": "blocked_no_verdict_transform_is_degenerate_for_stress_packets", "ready_for_api": false, "rendered_prompt_chars_max": 5884, "rendered_prompt_chars_min": 4965, "rendered_prompt_hashes_unique_count": 31, "rendered_prompt_text_stored": false, "verdict_fields_removed_total": 0}]` |
| `effective_call_count_matches_ready_conditions` | true | `186` |

## Next Step

Run only the ready current_merge_gate and coverage_contestation conditions for Qwen, DeepSeek, and Gemini unless a separate verdict-field packet variant is built and preflighted for no-verdict.
