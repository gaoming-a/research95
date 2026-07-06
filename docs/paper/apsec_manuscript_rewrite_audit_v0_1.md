# APSEC Manuscript Rewrite Audit v0.1

- audit id: `apsec_manuscript_rewrite_audit_v0_1`
- status: `passed`
- manuscript: `docs\paper\apsec_technical_track_rewrite_v0_1.md`
- boundary: no API call, no raw output read, no prompt text or patch text read.

## Checks

| check | passed | detail |
|---|---:|---|
| `manuscript_exists` | True | `docs\paper\apsec_technical_track_rewrite_v0_1.md` |
| `baseline_audit_passed` | True | `passed` |
| `apsec_status_present` | True | `` |
| `target_format_note_present` | True | `` |
| `required_sections_present` | True | `[]` |
| `title_scope_narrowed` | True | `` |
| `contribution_bullets_present` | True | `` |
| `evidence_visibility_protocol_present` | True | `` |
| `three_model_repaired_main_result_present` | True | `` |
| `dataset_composition_present` | True | `` |
| `evidence_ladder_humanized` | True | `` |
| `rq4_demoted_from_main_questions` | True | `` |
| `qwen_main_result_present` | True | `` |
| `deepseek_main_result_present` | True | `` |
| `gemini_main_result_present` | True | `` |
| `ablation_main_table_boundary_present` | True | `` |
| `rule_only_baseline_present` | True | `` |
| `rule_only_strength_acknowledged` | True | `` |
| `qwen_e0_not_deterministic` | True | `` |
| `majority_boundary_present` | True | `` |
| `ci_present` | True | `` |
| `false_accept_anatomy_present` | True | `` |
| `sanitized_false_accept_case_analysis_present` | True | `` |
| `tool_contestation_boundary_present` | True | `` |
| `coverage_contestation_boundary_present` | True | `` |
| `realistic_gate_boundary_present` | True | `` |
| `figures_referenced` | True | `` |
| `all_expected_citations_present` | True | `[]` |
| `reference_support_records_removed` | True | `` |
| `remaining_broad_model_gap_explicit` | True | `` |
| `forbidden_overclaims_absent` | True | `[]` |
| `api_call_attempted` | True | `False` |
| `raw_outputs_read_by_this_audit` | True | `False` |
| `prompt_or_patch_text_read_by_this_audit` | True | `False` |

## Verdict

- readiness: `markdown_rewrite_ready_for_ieeetran_package`

Remaining work:

- Do not broaden the three-model repaired result into a universal LLM-verifier claim.
- Report coverage-contestation as conservative prompt-sensitivity evidence, not as an improved verifier.
- Use the sanitized false-accept case analysis only as category-level failure anatomy, not as full rationale auditing.
- Compile and visually inspect the APSEC IEEEtran source package.
- Normalize BibTeX fields and check APSEC reference style.
- Check table widths, figure placement, page count, and double-blind wording in the compiled PDF.
