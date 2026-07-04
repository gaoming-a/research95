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
| `dataset_composition_present` | True | `` |
| `evidence_ladder_humanized` | True | `` |
| `rq4_demoted_from_main_questions` | True | `` |
| `qwen_main_result_present` | True | `` |
| `rule_only_baseline_present` | True | `` |
| `rule_only_strength_acknowledged` | True | `` |
| `qwen_e0_not_deterministic` | True | `` |
| `majority_boundary_present` | True | `` |
| `ci_present` | True | `` |
| `false_accept_anatomy_present` | True | `` |
| `tool_contestation_boundary_present` | True | `` |
| `realistic_gate_boundary_present` | True | `` |
| `figures_referenced` | True | `` |
| `all_expected_citations_present` | True | `[]` |
| `reference_support_records_removed` | True | `` |
| `multi_model_repaired_gap_explicit` | True | `` |
| `forbidden_overclaims_absent` | True | `[]` |
| `api_call_attempted` | True | `False` |
| `raw_outputs_read_by_this_audit` | True | `False` |
| `prompt_or_patch_text_read_by_this_audit` | True | `False` |

## Verdict

- readiness: `markdown_rewrite_ready_for_latex_conversion`

Remaining work:

- If APSEC competitiveness is prioritized, add repaired E0-E6 main tables for at least one more model and preferably two more models.
- Add a raw-output-free case-level false-accept analysis for the four Qwen E6 false accepts.
- Convert citation keys to BibTeX.
- Convert Markdown to anonymous IEEEtran conference LaTeX.
- Check page budget, table widths, figure placement, and double-blind wording.
