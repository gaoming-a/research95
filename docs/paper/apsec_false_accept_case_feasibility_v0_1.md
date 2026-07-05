# APSEC False-Accept Case-Analysis Feasibility v0.1

- audit id: `apsec_false_accept_case_feasibility_v0_1`
- status: `blocked_missing_candidate_level_decision_export`
- boundary: no API call, no raw response read, no patch diff read, no rendered prompt read.
- case-level table allowed now: `False`

## Aggregate Anatomy Currently Supported

| item | count |
|---|---:|
| `e6_false_accept_total` | 4 |
| `partial_fix_false_accepts` | 3 |
| `regression_patch_false_accepts` | 1 |

## Checks

| check | passed | detail |
|---|---:|---|
| `qwen_label_summary_exists` | True | `data\reviews\evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.json` |
| `candidate_set_summary_exists` | True | `data\protocols\evp8_candidate_set_v0_1_summary.json` |
| `candidate_set_metadata_exists` | True | `data\protocols\evp8_candidate_set_v0_1.json` |
| `apsec_audit_passed` | True | `passed` |
| `e6_false_accept_total_is_four` | True | `4` |
| `aggregate_partial_false_accepts_available` | True | `3` |
| `aggregate_regression_false_accepts_available` | True | `1` |
| `candidate_set_has_metadata_but_not_labels_or_decisions` | True | `['candidate_set_id', 'evp8_candidate_id', 'has_issue_summary', 'has_patch_text_source', 'label_fields_in_record', 'model_visible_record', 'patch_file_count', 'patch_sha256', 'project', 'selection_role', 'source_candidate_id', 'source_cohort_id', 'source_manifest', 'task_id', 'touched_file_count', 'touched_files']` |
| `qwen_summary_has_candidate_level_false_accept_records` | False | `No candidate-level false-accept records are present in the tracked aggregate summary.` |
| `api_call_attempted_by_this_audit` | True | `False` |
| `raw_response_read_by_this_audit` | True | `False` |
| `patch_diff_read_by_this_audit` | True | `False` |
| `rendered_prompt_read_by_this_audit` | True | `False` |

## Blocked Reason

Tracked paper-facing summaries expose aggregate false-accept counts but not the candidate IDs behind the four Qwen E6 false accepts.

## Minimum Next Artifact

- name: `raw_output_free_qwen_e6_false_accept_decision_export`
- required fields:
  - candidate_id
  - project
  - task_id
  - candidate_type
  - hidden_label
  - E6 decision
  - E6 no-verdict decision
  - tool-contestation linkage
  - rationale category without raw response text
- forbidden fields:
  - raw_response_text
  - full model rationale text
  - rendered prompt text
  - patch diff
  - API credentials
- construction note: Generate from existing local execution artifacts only if explicitly authorized to read the needed raw decision source; store only sanitized decision/category fields.
