# Gemini repaired EVP-8 v0.3 run packet

Status: `failed`

## Boundary

- Authorized API model: `google/gemini-2.5-flash` through OpenRouter pinned routing.
- This packet covers the frozen 98-candidate EVP-8 E0-E6 packet set only.
- The paper-facing result is a three-model repaired Qwen + DeepSeek + Gemini descriptive result, not a broad-LLM conclusion.
- Raw responses remain in ignored `outputs/**`; tracked summaries exclude raw response text, rendered prompts, patch diffs, and API keys.

## Checks

| check | passed | detail |
| --- | --- | --- |
| preflight_strict_ready | true | `true` |
| smoke_check_only_passed | true | `"passed"` |
| full_check_only_passed | true | `"passed"` |
| smoke_api_passed | true | `{"smoke_gate": "passed", "parse_valid_count": 35, "review_count": 35}` |
| full_api_passed | true | `{"run_gate": "passed", "first_batch_full_gate": "passed", "parse_valid_count": 686, "review_count": 686}` |
| cost_gate_passed | true | `{"usage_cost_gate": "passed", "total_cost_usd": 0.63891037}` |
| tracked_summaries_exclude_raw_text | true | `{"smoke": false, "full": false}` |
| label_conditioned_gemini_e6_present | true | `{"level": "E6", "accept": 25, "reject": 73, "escalate": 0, "correct_accept": 20, "false_accept": 5, "accepted_precision": 0.8, "correct_recall": 0.952381, "false_accept_rate": 0.064935, "escalation_rate": 0.0}` |
| sanitized_false_accept_analysis_includes_gemini | false | `null` |
| apsec_three_model_audit_passed | true | `"passed"` |

## Execution Summary

| scope | records | parse-valid | cost | decisions |
| --- | ---: | ---: | ---: | --- |
| smoke | 35 | 35 | $0.034846500 | `{"accept": 17, "escalate": 14, "reject": 4}` |
| full | 686 | 686 | $0.638910370 | `{"accept": 101, "escalate": 291, "reject": 294}` |

## Gemini Label-Conditioned E6 Result

| accept | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 25 | 20 | 5 | 80.00% | 95.24% | 6.49% | 0.00% |

## Tracked Artifacts

- `config_example`: `configs/evp8_gemini_repaired_v0_3.example.json`
- `preflight`: `data/protocols/evp8_gemini_repaired_v0_3_preflight_summary.json`
- `smoke_check_only`: `data/protocols/evp8_gemini_repaired_v0_3_smoke_check_only.json`
- `full_check_only`: `data/protocols/evp8_gemini_repaired_v0_3_full_check_only.json`
- `smoke_summary`: `data/reviews/evp8_gemini_repaired_v0_3_prompt_v0_2_google_gemini-2.5-flash_smoke_summary.json`
- `full_summary`: `data/reviews/evp8_gemini_repaired_v0_3_prompt_v0_2_google_gemini-2.5-flash_full_summary.json`
- `label_conditioned_summary`: `data/reviews/evp8_gemini_repaired_v0_3_prompt_v0_2_label_conditioned_summary.json`
- `label_conditioned_md`: `docs/experiments/evp8_gemini_repaired_v0_3_prompt_v0_2_label_conditioned_summary.md`
- `false_accept_case_analysis`: `data/reviews/apsec_false_accept_case_analysis_v0_2.json`
- `apsec_manuscript`: `docs/paper/apsec_technical_track_rewrite_v0_1.md`
- `apsec_audit`: `data/reviews/apsec_manuscript_rewrite_audit_v0_1.json`

## Remaining Gaps

- The repaired main result is now three-model, but still not broad-model evidence.
- The APSEC package still requires IEEEtran/BibTeX/page-budget conversion before submission.
