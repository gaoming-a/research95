# SQJ Claim Traceability Audit

This audit maps SQJ manuscript claims to tracked raw-output-free evidence. It does not call model APIs, read raw model responses, infer new results, compile the manuscript, or mark final freeze complete.

## Summary

- passed: yes
- raw-output-free check passed: yes
- API call attempted: no
- raw outputs read: no
- final freeze complete: no

## Checks

| check | passed | detail |
|---|---:|---|
| `synthesis_passed` | true | `"passed"` |
| `synthesis_no_api` | true | `false` |
| `synthesis_expected_models` | true | `["deepseek/deepseek-v4-pro", "qwen/qwen3.7-max", "moonshotai/kimi-k2.6", "mistralai/devstral-2512", "google/gemini-2.5-flash"]` |
| `synthesis_expected_levels` | true | `null` |
| `cost_passed` | true | `true` |
| `cost_api_freeze` | true | `true` |
| `blocked_attempts_not_model_results` | true | `null` |
| `fresh_gate_failed_as_expected` | true | `null` |
| `fresh_verifier_api_not_ready` | true | `null` |
| `fresh_decision_downgraded` | true | `"downgrade_to_two_project_fresh_hard_negative_supplement_or_source_acquisition_negative_result"` |
| `all_supported_claims_covered` | true | `null` |
| `all_forbidden_claims_absent` | true | `null` |

## Supported Claims

| id | framing | draft | evidence sources | claim |
|---|---:|---:|---|---|
| `evidence_visibility_variable` | true | true | `evp8_synthesis` | Evidence visibility is a first-order experimental variable for LLM-based patch verification. |
| `frozen_evp8_scope` | true | true | `evp8_synthesis` | The SQJ main result is a descriptive five-model EVP-8 study over 98 candidates and seven evidence levels. |
| `non_monotonic_model_dependent` | true | true | `evp8_synthesis` | The observed EVP-8 decision patterns are model-dependent and non-monotonic. |
| `devstral_saturation_risk` | true | true | `evp8_synthesis` | Devstral 2 saturation to escalation is a verifier reliability finding. |
| `blocked_kimi_cost_risk` | true | true | `evp8_cost` | Blocked Kimi attempts are cost and execution-risk evidence only, not valid model-result records. |
| `fresh_realistic_negative_result` | true | true | `fresh_decision`, `fresh_gate` | The fresh realistic branch is a two-project source-acquisition negative result, not a verifier-ready main experiment. |

## Forbidden Claims

| id | absent | hits | claim |
|---|---:|---|---|
| `llm_superiority` | true | `[]` | LLM verifiers outperform deterministic visible-tool or test-based baselines. |
| `e6_general_optimal` | true | `[]` | E6 is strictly or generally better than E4. |
| `monotonic_effectiveness_ranking` | true | `[]` | Evidence levels establish a final monotonic effectiveness ranking. |
| `scale_generalization` | true | `[]` | The 98-candidate EVP-8 set supports broad scale generalization. |
| `fresh_verifier_ready` | true | `[]` | The fresh realistic branch is a three-project verifier-ready main experiment. |
| `practical_autonomous_verifier` | true | `[]` | The full-file generation-interface repair validates practical autonomous patch verification. |
