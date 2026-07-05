# APSEC False-Accept Case Analysis v0.2

- status: `passed`
- boundary: reads local raw responses to extract decisions, writes only sanitized raw-output-free case fields

## Per-Model Anatomy

| model | false accepts | partial fixes | regression patches |
| --- | ---: | ---: | ---: |
| qwen/qwen3.7-max | 4 | 3 | 1 |
| deepseek/deepseek-v4-pro | 4 | 3 | 1 |
| google/gemini-2.5-flash | 5 | 4 | 1 |

## Sanitized Case Rows

| model | candidate | project | task | type | E6 | no-verdict | rationale category | risk category |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen/qwen3.7-max | evp8_smoke_candidate_0039 | thefuck | bugsinpy_thefuck_1 | regression_patch | accept | accept | accepted_without_specific_tool_reason_category | accepted_without_reported_risk_flags |
| qwen/qwen3.7-max | evp8_smoke_candidate_0053 | youtube-dl | bugsinpy_youtube-dl_16 | partial_fix | accept | accept | accepted_without_specific_tool_reason_category | accepted_without_reported_risk_flags |
| qwen/qwen3.7-max | evp8_smoke_candidate_0066 | youtube-dl | bugsinpy_youtube-dl_20 | partial_fix | accept | accept | accepted_due_to_visible_test_success | accepted_without_reported_risk_flags |
| qwen/qwen3.7-max | evp8_smoke_candidate_0093 | youtube-dl | bugsinpy_youtube-dl_6 | partial_fix | accept | accept | accepted_without_specific_tool_reason_category | accepted_without_reported_risk_flags |
| deepseek/deepseek-v4-pro | evp8_smoke_candidate_0039 | thefuck | bugsinpy_thefuck_1 | regression_patch | accept | escalate | accepted_due_to_visible_test_success | accepted_without_reported_risk_flags |
| deepseek/deepseek-v4-pro | evp8_smoke_candidate_0049 | youtube-dl | bugsinpy_youtube-dl_11 | partial_fix | accept | escalate | accepted_due_to_visible_test_success | accepted_without_reported_risk_flags |
| deepseek/deepseek-v4-pro | evp8_smoke_candidate_0053 | youtube-dl | bugsinpy_youtube-dl_16 | partial_fix | accept | escalate | accepted_due_to_visible_test_success | accepted_without_reported_risk_flags |
| deepseek/deepseek-v4-pro | evp8_smoke_candidate_0066 | youtube-dl | bugsinpy_youtube-dl_20 | partial_fix | accept | escalate | accepted_due_to_visible_test_success | accepted_without_reported_risk_flags |
| google/gemini-2.5-flash | evp8_smoke_candidate_0039 | thefuck | bugsinpy_thefuck_1 | regression_patch | accept | n/a | accepted_due_to_visible_tests_and_merge_gate_summary | accepted_without_reported_risk_flags |
| google/gemini-2.5-flash | evp8_smoke_candidate_0049 | youtube-dl | bugsinpy_youtube-dl_11 | partial_fix | accept | n/a | accepted_due_to_visible_tests_and_merge_gate_summary | accepted_without_reported_risk_flags |
| google/gemini-2.5-flash | evp8_smoke_candidate_0053 | youtube-dl | bugsinpy_youtube-dl_16 | partial_fix | accept | n/a | accepted_due_to_visible_tests_and_merge_gate_summary | accepted_without_reported_risk_flags |
| google/gemini-2.5-flash | evp8_smoke_candidate_0066 | youtube-dl | bugsinpy_youtube-dl_20 | partial_fix | accept | n/a | accepted_due_to_visible_tests_and_merge_gate_summary | accepted_without_reported_risk_flags |
| google/gemini-2.5-flash | evp8_smoke_candidate_0093 | youtube-dl | bugsinpy_youtube-dl_6 | partial_fix | accept | n/a | accepted_due_to_visible_tests_and_merge_gate_summary | accepted_without_reported_risk_flags |

## Checks

| check | passed | detail |
| --- | ---: | --- |
| `raw_sources_exist` | True | `{'qwen/qwen3.7-max': 'outputs/evp8_main_v0_3_qwen_first_prompt_v0_2_json_mode_full/qwen_qwen3.7-max/raw_responses.jsonl', 'deepseek/deepseek-v4-pro': 'outputs/evp8_deepseek_repaired_v0_3_prompt_v0_2_json_mode_full/deepseek_deepseek-v4-pro/raw_responses.jsonl', 'google/gemini-2.5-flash': 'outputs/evp8_gemini_repaired_v0_3_prompt_v0_2_openrouter_full/google_gemini-2.5-flash/raw_responses.jsonl'}` |
| `false_accept_rows_present` | True | `13` |
| `qwen_false_accept_count` | True | `{'false_accept': 4, 'partial_fix': 3, 'regression_patch': 1}` |
| `deepseek_false_accept_count` | True | `{'false_accept': 4, 'partial_fix': 3, 'regression_patch': 1}` |
| `gemini_false_accept_count` | True | `{'false_accept': 5, 'partial_fix': 4, 'regression_patch': 1}` |
| `raw_response_text_not_stored` | True | `True` |
| `rendered_prompt_or_patch_diff_not_stored` | True | `True` |
