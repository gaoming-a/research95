# DeepSeek repaired EVP-8 v0.3 run packet

Status: `passed`

## Boundary

- Authorized API model: `deepseek/deepseek-v4-pro`.
- This packet covers the frozen 98-candidate EVP-8 E0-E6 packet set only.
- The paper-facing result is a two-model repaired Qwen + DeepSeek result, not a three-model or broad-LLM conclusion.
- Raw responses remain in ignored `outputs/**`; tracked summaries exclude raw response text, rendered prompts, patch diffs, and API keys.

## Checks

| check | passed | detail |
| --- | --- | --- |
| preflight_strict_ready | true | `true` |
| smoke_check_only_passed | true | `"passed"` |
| full_check_only_passed | true | `"passed"` |
| smoke_api_passed | true | `{"smoke_gate": "passed", "parse_valid_count": 35, "review_count": 35}` |
| full_api_passed | true | `{"run_gate": "passed", "first_batch_full_gate": "passed", "parse_valid_count": 686, "review_count": 686}` |
| cost_gate_passed | true | `{"usage_cost_gate": "passed", "total_cost_usd": 0.434221524}` |
| tracked_summaries_exclude_raw_text | true | `{"smoke": false, "full": false}` |
| label_conditioned_deepseek_e6_present | true | `{"level": "E6", "accept": 21, "reject": 73, "escalate": 4, "correct_accept": 17, "false_accept": 4, "accepted_precision": 0.809524, "correct_recall": 0.809524, "false_accept_rate": 0.051948, "escalation_rate": 0.040816}` |
| apsec_two_model_audit_passed | true | `"passed"` |

## Execution Summary

| scope | records | parse-valid | cost | decisions |
| --- | ---: | ---: | ---: | --- |
| smoke | 35 | 35 | $0.026675244 | `{"accept": 9, "escalate": 21, "reject": 5}` |
| full | 686 | 686 | $0.434221524 | `{"accept": 45, "escalate": 343, "reject": 298}` |

## DeepSeek Label-Conditioned E6 Result

| accept | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 21 | 17 | 4 | 80.95% | 80.95% | 5.19% | 4.08% |

## Tracked Artifacts

- `config_example`: `configs/evp8_deepseek_repaired_v0_3.example.json`
- `preflight`: `data/protocols/evp8_deepseek_repaired_v0_3_preflight_summary.json`
- `smoke_check_only`: `data/protocols/evp8_deepseek_repaired_v0_3_smoke_check_only.json`
- `full_check_only`: `data/protocols/evp8_deepseek_repaired_v0_3_full_check_only.json`
- `smoke_summary`: `data/reviews/evp8_deepseek_repaired_v0_3_prompt_v0_2_deepseek_deepseek-v4-pro_smoke_summary.json`
- `full_summary`: `data/reviews/evp8_deepseek_repaired_v0_3_prompt_v0_2_deepseek_deepseek-v4-pro_full_summary.json`
- `label_conditioned_summary`: `data/reviews/evp8_deepseek_repaired_v0_3_prompt_v0_2_label_conditioned_summary.json`
- `label_conditioned_md`: `docs/experiments/evp8_deepseek_repaired_v0_3_prompt_v0_2_label_conditioned_summary.md`
- `apsec_manuscript`: `docs/paper/apsec_technical_track_rewrite_v0_1.md`
- `apsec_audit`: `data/reviews/apsec_manuscript_rewrite_audit_v0_1.json`

## Remaining Gaps

- Add a third repaired E0-E6 model only with a new explicit authorization and preflight.
- Create a raw-output-free candidate-level decision export before writing concrete false-accept case tables.
