# EVP-7 G5 Qualitative Decision Cases

This artifact selects representative EVP-7 decision cases from existing parse-valid review records. It writes only structured decision sequences, model-visible evidence categories, deterministic tool-only decisions, and separated evaluator-only interpretations. It does not include raw responses, prompt text, or reviewer-facing truth labels.

## Summary

- case count: 6
- case roles: `evidence_enabled_accept, tool_false_accept_recovered_by_llm, correct_patch_downgraded_by_llm, tool_summary_late_accept, no_op_rejected_after_evidence, partial_patch_rejected_after_evidence`
- raw-output-free check passed: true
- reviewer-facing truth labels separated: true

## Terminology Ledger

| Canonical term | Meaning in this report | Boundary |
|---|---|---|
| model-visible sequence | The E0/E2/E4/E6 decisions and structured evidence categories visible in the review record | Does not include evaluator-only labels |
| evaluator-only interpretation | The hidden label, patch source, and validation outcome used after review to interpret the case | Not part of the model-visible prompt |
| tool-only decision | Deterministic E4/E6 baseline decision from visible tests or visible tool summaries | Used for attribution, not as an oracle |

## Case Overview

| case | candidate | role | project | task | E0 | E2 | E4 | E6 | evaluator-only outcome |
|---|---|---|---|---|---|---|---|---|---|
| QC1 | `evp7_candidate_0007` | `evidence_enabled_accept` | PySnooper | `bugsinpy_PySnooper_3` | escalate | escalate | accept | accept | `correct_under_f2p_and_p2p_broad` |
| QC2 | `evp7_candidate_0078` | `tool_false_accept_recovered_by_llm` | youtube-dl | `bugsinpy_youtube-dl_20` | escalate | reject | escalate | reject | `incorrect_issue_not_fixed` |
| QC3 | `evp7_candidate_0001` | `correct_patch_downgraded_by_llm` | PySnooper | `bugsinpy_PySnooper_1` | escalate | escalate | escalate | escalate | `correct_under_f2p_and_p2p_broad` |
| QC4 | `evp7_candidate_0051` | `tool_summary_late_accept` | youtube-dl | `bugsinpy_youtube-dl_5` | reject | escalate | escalate | accept | `correct_under_f2p_and_p2p_broad` |
| QC5 | `evp7_candidate_0031` | `no_op_rejected_after_evidence` | httpie | `bugsinpy_httpie_5` | escalate | escalate | reject | reject | `incorrect_issue_not_fixed` |
| QC6 | `evp7_candidate_0005` | `partial_patch_rejected_after_evidence` | PySnooper | `bugsinpy_PySnooper_1` | escalate | escalate | reject | reject | `incorrect_issue_not_fixed` |

## Case Details

### QC1 - evidence_enabled_accept

- candidate: `evp7_candidate_0007`
- project/task: PySnooper / `bugsinpy_PySnooper_3`
- issue summary: snoop file output should append trace lines to the user-provided file path
- touched files: `pysnooper/pysnooper.py`
- patch size: `{'added_lines': 1, 'deleted_lines': 1, 'files_changed': 1}`
- visible tests count: 1

| level | LLM decision | confidence | human review | risk flags | evidence used | tool-only decision |
|---|---|---:|---|---|---|---|
| E0 | escalate | 0.40 | true | `insufficient_evidence` | `issue_summary, patch_diff` | -- |
| E2 | escalate | 0.60 | true | `insufficient_evidence` | `issue_summary, patch_diff, patch_applies` | -- |
| E4 | accept | 0.90 | false | `insufficient_evidence` | `patch_diff, issue_summary, test_results` | accept |
| E6 | accept | 0.95 | false | `` | `patch_diff, visible_test_evidence, visible_static_evidence` | accept |

Evaluator-only interpretation:

- patch source label: `correct_reference`
- outcome label: `correct_under_f2p_and_p2p_broad`
- failure type: `none`
- interpretation: Visible test evidence changed a cautious model-visible sequence into an accept decision. This case illustrates the intended value of evidence visibility when the evaluator-only label marks the patch as correct.

### QC2 - tool_false_accept_recovered_by_llm

- candidate: `evp7_candidate_0078`
- project/task: youtube-dl / `bugsinpy_youtube-dl_20`
- issue summary: get_elements_by_attribute should match HTML elements that contain valueless attributes before or after the target attribute.
- touched files: `youtube_dl/utils.py`
- patch size: `{'added_lines': 1, 'deleted_lines': 1, 'files_changed': 1}`
- visible tests count: 1

| level | LLM decision | confidence | human review | risk flags | evidence used | tool-only decision |
|---|---|---:|---|---|---|---|
| E0 | escalate | 0.10 | true | `insufficient_evidence` | `issue_summary, patch_diff` | -- |
| E2 | reject | 0.95 | false | `partial_fix, under_fix` | `issue_summary, patch_diff` | -- |
| E4 | escalate | 0.30 | true | `under_fix, insufficient_evidence` | `issue_summary, patch_diff, test_results` | accept |
| E6 | reject | 0.80 | false | `under_fix, test_overfitting` | `issue_summary, patch_diff, test_results` | accept |

Evaluator-only interpretation:

- patch source label: `partial_fix`
- outcome label: `incorrect_issue_not_fixed`
- failure type: `partial_fix`
- interpretation: The deterministic visible-test and visible-tool-summary baselines accepted this partial patch, whereas the LLM did not accept it at E4 or E6. This is one of the recovered tool-only false accepts.

### QC3 - correct_patch_downgraded_by_llm

- candidate: `evp7_candidate_0001`
- project/task: PySnooper / `bugsinpy_PySnooper_1`
- issue summary: Snooper log files and decoded source lines should preserve non-ASCII text as UTF-8
- touched files: `pysnooper/tracer.py, pysnooper/pycompat.py`
- patch size: `{'added_lines': 6, 'deleted_lines': 2, 'files_changed': 2}`
- visible tests count: 1

| level | LLM decision | confidence | human review | risk flags | evidence used | tool-only decision |
|---|---|---:|---|---|---|---|
| E0 | escalate | 0.20 | true | `insufficient_evidence` | `issue_summary, patch_diff` | -- |
| E2 | escalate | 0.30 | true | `insufficient_evidence` | `issue_summary, patch_diff, visible_static_evidence` | -- |
| E4 | escalate | 0.60 | true | `insufficient_evidence, regression_risk` | `test_results, patch_diff, visible_static_evidence` | accept |
| E6 | escalate | 0.40 | true | `insufficient_evidence, regression_risk` | `visible_test_evidence, patch_diff, issue_summary` | accept |

Evaluator-only interpretation:

- patch source label: `correct_reference`
- outcome label: `correct_under_f2p_and_p2p_broad`
- failure type: `none`
- interpretation: The tool-only baselines accepted this correct reference patch at E4 and E6, but the LLM kept escalating. This case shows the recall cost behind the safety-oriented interpretation.

### QC4 - tool_summary_late_accept

- candidate: `evp7_candidate_0051`
- project/task: youtube-dl / `bugsinpy_youtube-dl_5`
- issue summary: unified_timestamp should correctly add PM offsets for both strptime parsed timestamps and email parsedate_tz fallback timestamps.
- touched files: `youtube_dl/utils.py`
- patch size: `{'added_lines': 3, 'deleted_lines': 3, 'files_changed': 1}`
- visible tests count: 1

| level | LLM decision | confidence | human review | risk flags | evidence used | tool-only decision |
|---|---|---:|---|---|---|---|
| E0 | reject | 0.95 | false | `under_fix, regression_risk` | `issue_summary, patch_diff` | -- |
| E2 | escalate | 0.70 | true | `under_fix, regression_risk, insufficient_evidence` | `issue_summary, patch_diff, patch_applies` | -- |
| E4 | escalate | 0.70 | true | `insufficient_evidence` | `patch_diff, issue_summary, visible_test_evidence, visible_static_evidence` | accept |
| E6 | accept | 0.85 | false | `` | `issue_summary, patch_diff, test_results` | accept |

Evaluator-only interpretation:

- patch source label: `correct_reference`
- outcome label: `correct_under_f2p_and_p2p_broad`
- failure type: `none`
- interpretation: The model rejected or escalated before the full visible tool summary, then accepted at E6. This case illustrates that the strongest evidence level can recover some correct-patch recall.

### QC5 - no_op_rejected_after_evidence

- candidate: `evp7_candidate_0031`
- project/task: httpie / `bugsinpy_httpie_5`
- issue summary: escaped long separators should be parsed as part of the key
- touched files: `httpie/cli.py`
- patch size: `{'added_lines': 0, 'deleted_lines': 0, 'files_changed': 0}`
- visible tests count: 1

| level | LLM decision | confidence | human review | risk flags | evidence used | tool-only decision |
|---|---|---:|---|---|---|---|
| E0 | escalate | 0.00 | true | `insufficient_evidence` | `issue_summary, patch_diff` | -- |
| E2 | escalate | 0.10 | true | `insufficient_evidence` | `patch_diff, patch_applies` | -- |
| E4 | reject | 0.95 | false | `under_fix` | `issue_summary, test_results` | reject |
| E6 | reject | 0.95 | false | `under_fix, regression_risk` | `issue_summary, visible_test_evidence, test_results` | reject |

Evaluator-only interpretation:

- patch source label: `buggy_noop`
- outcome label: `incorrect_issue_not_fixed`
- failure type: `no_op_patch`
- interpretation: A no-op control moved from escalation to rejection once visible test evidence was available. This supports the paper's merge-gate framing for non-fixing patches.

### QC6 - partial_patch_rejected_after_evidence

- candidate: `evp7_candidate_0005`
- project/task: PySnooper / `bugsinpy_PySnooper_1`
- issue summary: Snooper log files and decoded source lines should preserve non-ASCII text as UTF-8
- touched files: `pysnooper/tracer.py, pysnooper/pycompat.py`
- patch size: `{'added_lines': 4, 'deleted_lines': 1, 'files_changed': 1}`
- visible tests count: 1

| level | LLM decision | confidence | human review | risk flags | evidence used | tool-only decision |
|---|---|---:|---|---|---|---|
| E0 | escalate | 0.10 | true | `insufficient_evidence, partial_fix` | `issue_summary, patch_diff, touched_files` | -- |
| E2 | escalate | 0.60 | true | `under_fix, insufficient_evidence` | `issue_summary, patch_diff, patch_applies` | -- |
| E4 | reject | 0.95 | false | `regression_risk` | `visible_test_evidence` | reject |
| E6 | reject | 0.95 | false | `regression_risk` | `patch_diff, visible_test_evidence` | reject |

Evaluator-only interpretation:

- patch source label: `partial_fix`
- outcome label: `incorrect_issue_not_fixed`
- failure type: `partial_fix`
- interpretation: A partial patch remained non-accepted after visible evidence was added. This case represents the common E4/E6 reject path rather than the smaller set of tool-only false accepts.

## Paper-Use Boundary

- Use these cases to explain decision mechanics, not to make scale-generalized claims.
- Keep the model-visible decision sequence separate from evaluator-only labels in prose.
- The cases support the bounded interpretation that evidence visibility changes merge-gate behavior while preserving a safety/recall tradeoff.
