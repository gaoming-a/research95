# EVP-7 G5 376-Record Claim Traceability

This audit reads only tracked raw-output-free summaries and paper drafts. It maps current EVP-7 supported and unsupported claims to evidence files and paper coverage; it does not read or package raw model responses.

## Summary

- passed: yes
- raw-output-free check passed: yes

## Checks

| check | passed |
|---|---:|
| `summary_is_current_376_run` | true |
| `quality_status_bounded` | true |
| `statistics_raw_output_free` | true |
| `all_supported_claims_covered` | true |
| `all_unsupported_claims_covered` | true |
| `all_ieee_boundary_cues_present` | true |

## Supported Claims

| claim | generated tables | markdown draft | IEEE draft | evidence sources |
|---|---:|---:|---:|---|
| The current EVP-7 run produced raw-output-free tracked metrics from real DeepSeek verifier outputs. | true | true | true | `data/reviews/evp7_g5_llm_376_full_summary.json`, `data/reviews/evp7_g5_376_full_quality_audit.json`, `data/reviews/evp7_g5_376_statistical_analysis.json` |
| The run shows evidence-level metric variation in the tracked summary. | true | true | true | `data/reviews/evp7_g5_llm_376_full_summary.json`, `data/reviews/evp7_g5_376_full_quality_audit.json`, `data/reviews/evp7_g5_376_statistical_analysis.json` |
| E4/E6 preserved zero observed false accepts and accepted precision 1.0. | true | true | true | `data/reviews/evp7_g5_llm_376_full_summary.json`, `data/reviews/evp7_g5_376_full_quality_audit.json`, `data/reviews/evp7_g5_376_statistical_analysis.json` |
| E4/E6 improved correct recall over E0 and produced positive Evidence Gain versus E0. | true | true | true | `data/reviews/evp7_g5_llm_376_full_summary.json`, `data/reviews/evp7_g5_376_full_quality_audit.json`, `data/reviews/evp7_g5_376_statistical_analysis.json` |

## Unsupported Claims

| claim | generated tables | markdown draft | IEEE draft | evidence sources |
|---|---:|---:|---:|---|
| Scale-generalized paper claims beyond EVP-7. | true | true | true | `data/reviews/evp7_g5_llm_376_full_summary.json`, `data/reviews/evp7_g5_376_full_quality_audit.json`, `data/reviews/evp7_g5_376_statistical_analysis.json` |
| A claim that the LLM outperforms the deterministic visible-test tool-only baseline. | true | true | true | `data/reviews/evp7_g5_llm_376_full_summary.json`, `data/reviews/evp7_g5_376_full_quality_audit.json`, `data/reviews/evp7_g5_376_statistical_analysis.json` |
| A claim that E6 strictly improves over E4 in this run. | true | true | true | `data/reviews/evp7_g5_llm_376_full_summary.json`, `data/reviews/evp7_g5_376_full_quality_audit.json`, `data/reviews/evp7_g5_376_statistical_analysis.json` |
| A claim that runner-estimated cost is an external DeepSeek billing statement. | true | true | true | `data/reviews/evp7_g5_llm_376_full_summary.json`, `data/reviews/evp7_g5_376_full_quality_audit.json`, `data/reviews/evp7_g5_376_statistical_analysis.json` |

## IEEE Boundary Cues

| cue | passed | accepted cues |
|---|---:|---|
| `bounded_pilot` | true | `["bounded", "pilot"]` |
| `not_scale_generalized` | true | `["not scale-generalized", "does not establish cross-model generality"]` |
| `no_deterministic_superiority` | true | `["deterministic-baseline superiority", "LLM outperforms the deterministic"]` |
| `no_e6_strict_superiority` | true | `["E6 strict superiority over E4", "E6 strictly improves over E4"]` |
| `no_billing_equivalence` | true | `["not an external billing statement", "billing equivalence"]` |
