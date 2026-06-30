# EVP-8-HARD Tool-Contestation Result v0.1

## Scope

- Cohort: `EVP-8-HARD`
- Candidate count: `47`
- Packet variant: `e6_tool_contestation_no_verdict`
- Models:
  - `qwen/qwen3.7-max`
  - `deepseek/deepseek-v4-pro`
- Removed model-visible verdict fields:
  - `rule_based_visible_merge_gate_decision`
  - `rule_based_visible_merge_gate_reasons`
  - `source_decision`

The prompt explicitly asks the model to judge whether visible tests are
sufficient for accept and whether a visible-test-only accept premise should be
challenged. It does not expose hidden evaluator labels, hidden oracle outcomes,
reference provenance, or final merge labels.

Raw model outputs are stored only under ignored `outputs/`. The tracked
summaries and parsed reviews do not store raw response text or provider
response objects.

## Run Gates

| Model | Reviews | Parse valid | Run gate | Usage/cost gate | Cost |
|---|---:|---:|---|---|---:|
| qwen/qwen3.7-max | 47 | 47 | passed | passed | CNY 3.479676 |
| deepseek/deepseek-v4-pro | 47 | 47 | passed | passed | USD 0.0386889 |

## Whole-Cohort Decisions

| System | Accept | Reject | Escalate |
|---|---:|---:|---:|
| tool-only baseline | 17 | 30 | 0 |
| Qwen tool-contestation | 1 | 30 | 16 |
| DeepSeek tool-contestation | 0 | 29 | 18 |

## Whole-Cohort Metrics

| System | Accepted precision | Correct recall | False accept rate | False reject rate | Escalation rate |
|---|---:|---:|---:|---:|---:|
| tool-only baseline | 47.06% | 80.00% | 24.32% | 20.00% | 0.00% |
| Qwen tool-contestation | 0.00% | 0.00% | 2.70% | 20.00% | 34.04% |
| DeepSeek tool-contestation | n/a | 0.00% | 0.00% | 20.00% | 38.30% |

Wilson 95% intervals remain wide on this 47-candidate hard-case cohort. For
whole-cohort false accept rate, the tool-only baseline is 0.243
[0.134, 0.401], Qwen is 0.027 [0.005, 0.138], and DeepSeek is 0.000
[0.000, 0.094].

## Tool-Contestation Signals

| Model | `would_challenge_visible_test_only_accept=true` | high coverage concern | insufficient-for-accept |
|---|---:|---:|---:|
| Qwen tool-contestation | 16/47 | 28/47 | 16/47 |
| DeepSeek tool-contestation | 46/47 | 46/47 | 18/47 |

DeepSeek contests almost every visible-test-only accept premise and is therefore
much more conservative. Qwen is more selective: it contests a smaller subset,
but still contests most known false-accept opportunities.

## Primary Opportunity Set

The primary opportunity set contains the nine candidates previously falsely
accepted by the tool baseline, Qwen E6-full, and DeepSeek E6-full.

| Model | Repeated accept | Escalate | Strict reject | Safe handled | Challenge true | Visible tests insufficient |
|---|---:|---:|---:|---:|---:|---:|
| Qwen tool-contestation | 1 | 8 | 0 | 8 | 8 | 8 |
| DeepSeek tool-contestation | 0 | 9 | 0 | 9 | 9 | 9 |

On the nine-case opportunity set, Qwen safe handling is 0.889 [0.565, 0.980]
and DeepSeek safe handling is 1.000 [0.701, 1.000] by Wilson 95% interval.
The same intervals apply to the challenge rate because the safe handling is
entirely driven by escalation, not strict rejection.

## Interpretation

This result directly addresses the earlier E6-full threat. When the prompt
receives a verdict-like deterministic merge-gate decision, Qwen and DeepSeek
repeat the tool-only baseline exactly. When that verdict is removed and the
model is asked to contest the visible-test-only accept premise, both models
become much more willing to mark visible evidence as insufficient.

The result is not an automatic correctness-verification success. Neither model
strictly rejects the nine known false accepts. The improvement is
`accept -> escalate`, not `accept -> reject`. Qwen still accepts one known
false accept, and both models reduce correct recall to zero because they
escalate all correct patches that the tool baseline accepted.

The defensible claim is:

> Explicit tool-contestation prompts can make LLM verifiers challenge
> visible-test-only accept premises and route known false accepts to escalation,
> but this works as risk triage rather than autonomous patch correctness
> verification.

## Evidence Files

- Check-only:
  `data/protocols/evp8_hard_tool_contestation_check_only_v0_1.json`
- Combined audit:
  `data/protocols/evp8_hard_tool_contestation_result_audit_v0_1.json`
- Opportunity analysis:
  `data/reviews/evp8_hard_tool_contestation_opportunity_analysis_v0_1.json`
- Opportunity Markdown:
  `docs/experiments/evp8_hard_tool_contestation_opportunity_analysis_v0_1.md`
- Qwen summary:
  `data/reviews/evp8_hard_tool_contestation_qwen_qwen3.7-max_full_summary.json`
- Qwen parsed reviews:
  `data/reviews/evp8_hard_tool_contestation_qwen_qwen3.7-max_full_reviews.jsonl`
- DeepSeek summary:
  `data/reviews/evp8_hard_tool_contestation_deepseek_deepseek-v4-pro_full_summary.json`
- DeepSeek parsed reviews:
  `data/reviews/evp8_hard_tool_contestation_deepseek_deepseek-v4-pro_full_reviews.jsonl`
