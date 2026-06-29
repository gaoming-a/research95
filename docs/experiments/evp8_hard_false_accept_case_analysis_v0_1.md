# EVP-8-HARD False Accept Case Analysis v0.1

## Scope

- Cohort: `EVP-8-HARD`
- Candidate count: 47
- Repeated false accepts: 9
- Models: `qwen/qwen3.7-max`, `deepseek/deepseek-v4-pro`
- API call attempted by this analysis: `false`
- Raw model outputs read: `false`
- Patch diffs stored in this analysis: `false`

This analysis joins evaluator-only labels with model-visible evidence and
parsed review schema fields after execution. It is not model-visible
input and is not a new API run.

## Main Finding

All nine tool false accepts were repeated by both Qwen and DeepSeek. They
share the same surface pattern: the candidate applies, the visible test
passes, and the hidden evaluator oracle fails. This is exactly the
failure mode a practical merge gate must control.

## Aggregate Breakdown

| Dimension | Breakdown |
|---|---|
| Labels | `{"agent_plausible_wrong": 5, "partial": 4}` |
| Tasks | `{"bugsinpy_httpie_1": 4, "bugsinpy_httpie_2": 2, "bugsinpy_httpie_3": 2, "bugsinpy_httpie_4": 1}` |
| Themes | `{"agent_plausible_wrong_httpie_2": 2, "agent_plausible_wrong_httpie_3": 2, "agent_plausible_wrong_httpie_4": 1, "partial_httpie1_errno_fallback_blind_spot": 3, "partial_httpie1_unique_filename_blind_spot": 1}` |
| Patch source kinds | `{"ai_or_agent_generated": 5, "constructed_or_reference": 4}` |
| Visible outcomes | `{"passed": 9}` |
| Non-empty Qwen risk flags | 0/9 |
| Non-empty DeepSeek risk flags | 0/9 |

## Case Table

| Candidate | Task | Hidden label | Theme | Visible evidence | Hidden failure signal | Model behavior |
|---|---|---|---|---|---|---|
| evp8_hard_candidate_0001 | bugsinpy_httpie_1 | partial | partial_httpie1_errno_fallback_blind_spot | completed; passed; tests/test_downloads.py::TestDownloadUtils::test_unique_filename | hidden oracle passed=False; httpie_1_unique_filename.py, httpie_1_errno_fallback.py | tool/qwen/deepseek all accepted |
| evp8_hard_candidate_0002 | bugsinpy_httpie_1 | partial | partial_httpie1_errno_fallback_blind_spot | completed; passed; tests/test_downloads.py::TestDownloadUtils::test_unique_filename | hidden oracle passed=False; httpie_1_unique_filename.py, httpie_1_errno_fallback.py | tool/qwen/deepseek all accepted |
| evp8_hard_candidate_0003 | bugsinpy_httpie_1 | partial | partial_httpie1_errno_fallback_blind_spot | completed; passed; tests/test_downloads.py::TestDownloadUtils::test_unique_filename | hidden oracle passed=False; httpie_1_unique_filename.py, httpie_1_errno_fallback.py | tool/qwen/deepseek all accepted |
| evp8_hard_candidate_0008 | bugsinpy_httpie_2 | agent_plausible_wrong | agent_plausible_wrong_httpie_2 | completed; passed; tests/test_redirects.py::TestRedirects::test_max_redirects | hidden oracle passed=False; httpie_2_max_redirects.py | tool/qwen/deepseek all accepted |
| evp8_hard_candidate_0009 | bugsinpy_httpie_2 | agent_plausible_wrong | agent_plausible_wrong_httpie_2 | completed; passed; tests/test_redirects.py::TestRedirects::test_max_redirects | hidden oracle passed=False; httpie_2_max_redirects.py | tool/qwen/deepseek all accepted |
| evp8_hard_candidate_0010 | bugsinpy_httpie_3 | agent_plausible_wrong | agent_plausible_wrong_httpie_3 | completed; passed; tests/test_sessions.py::TestSession::test_download_in_session | hidden oracle passed=False; httpie_3_session_headers.py | tool/qwen/deepseek all accepted |
| evp8_hard_candidate_0011 | bugsinpy_httpie_3 | agent_plausible_wrong | agent_plausible_wrong_httpie_3 | completed; passed; tests/test_sessions.py::TestSession::test_download_in_session | hidden oracle passed=False; httpie_3_session_headers.py | tool/qwen/deepseek all accepted |
| evp8_hard_candidate_0012 | bugsinpy_httpie_4 | agent_plausible_wrong | agent_plausible_wrong_httpie_4 | completed; passed; tests/test_regressions.py::test_Host_header_overwrite | hidden oracle passed=False; httpie_4_host_header.py | tool/qwen/deepseek all accepted |
| evp8_hard_candidate_0022 | bugsinpy_httpie_1 | partial | partial_httpie1_unique_filename_blind_spot | completed; passed; tests/test_downloads.py::TestDownloadUtils::test_unique_filename | hidden oracle passed=False; httpie_1_unique_filename.py, httpie_1_errno_fallback.py | tool/qwen/deepseek all accepted |

## What The Cases Show

- The false accepts are concentrated in `httpie`: four partial fixes for
  `httpie_1` and five agent-plausible wrong patches for `httpie_2` to
  `httpie_4`.
- Every repeated false accept has visible outcome `passed`, so the
  visible test is not discriminative enough for hidden correctness.
- Both models produced zero non-empty risk flags on these nine cases,
  which means the current E6 prompt/evidence setup did not surface the
  hidden risk as uncertainty or escalation.
- Qwen sometimes adds semantic-sounding acceptance reasons, while
  DeepSeek mostly states that visible tests passed. In both cases, the
  decision boundary remains identical to the tool baseline.

## Implication For The Next Experiment

The next ablation should not add another same-prompt model. It should
remove verdict-like tool-summary fields and test whether the model can
detect or escalate these same nine cases from lower-level evidence.
If the decisions still match the tool baseline, the paper claim should
move further toward tool-verdict dominance rather than LLM-added
verification value.

## Checks

- `tool_false_accepts_repeated_by_both_models`: `true`
- `raw_model_outputs_not_read`: `true`
- `patch_text_not_stored_in_analysis`: `true`
- `all_repeated_false_accepts_have_visible_pass`: `true`
- `all_repeated_false_accepts_have_hidden_failure`: `true`
