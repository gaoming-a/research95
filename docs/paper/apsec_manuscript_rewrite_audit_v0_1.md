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
| `contribution_bullets_present` | True | `` |
| `evidence_visibility_protocol_present` | True | `` |
| `qwen_main_result_present` | True | `` |
| `rule_only_baseline_present` | True | `` |
| `qwen_e0_not_deterministic` | True | `` |
| `majority_boundary_present` | True | `` |
| `ci_present` | True | `` |
| `tool_contestation_boundary_present` | True | `` |
| `realistic_gate_boundary_present` | True | `` |
| `figures_referenced` | True | `` |
| `all_expected_citations_present` | True | `[]` |
| `forbidden_overclaims_absent` | True | `[]` |
| `api_call_attempted` | True | `False` |
| `raw_outputs_read_by_this_audit` | True | `False` |
| `prompt_or_patch_text_read_by_this_audit` | True | `False` |

## Verdict

- readiness: `markdown_rewrite_ready_for_latex_conversion`

Remaining work:

- Convert citation keys to BibTeX.
- Convert Markdown to anonymous IEEEtran conference LaTeX.
- Check page budget, table widths, figure placement, and double-blind wording.
