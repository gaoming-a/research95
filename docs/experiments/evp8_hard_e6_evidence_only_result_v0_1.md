# EVP-8-HARD E6 Evidence-Only Result v0.1

## Scope

- Cohort: `EVP-8-HARD`
- Packet variant: `e6_evidence_only_no_verdict`
- Candidate count: `47`
- Evidence level: `E6`
- Removed model-visible verdict fields:
  - `rule_based_visible_merge_gate_decision`
  - `rule_based_visible_merge_gate_reasons`
  - `source_decision`

Raw model outputs are stored only under ignored `outputs/`. The tracked
summaries and parsed reviews do not store raw response text or provider
response objects.

## Run Gates

| Model | Reviews | Parse valid | Run gate | Usage/cost gate | Cost |
|---|---:|---:|---|---|---:|
| qwen/qwen3.7-max | 47 | 47 | passed | passed | CNY 2.686008 |
| deepseek/deepseek-v4-pro | 47 | 47 | passed | passed | USD 0.034915072 |

## Whole-Cohort Decisions

| System | Accept | Reject | Escalate |
|---|---:|---:|---:|
| tool-only baseline | 17 | 30 | 0 |
| qwen/qwen3.7-max | 15 | 30 | 2 |
| deepseek/deepseek-v4-pro | 6 | 30 | 11 |

## Whole-Cohort Metrics

| System | Accepted precision | Correct recall | False accept rate | False reject rate | Escalation rate |
|---|---:|---:|---:|---:|---:|
| tool-only baseline | 47.06% | 80.00% | 24.32% | 20.00% | 0.00% |
| qwen/qwen3.7-max | 53.33% | 80.00% | 18.92% | 20.00% | 4.26% |
| deepseek/deepseek-v4-pro | 33.33% | 20.00% | 10.81% | 20.00% | 23.40% |

## Primary Opportunity Set

The primary opportunity set contains the nine candidates previously falsely
accepted by the tool baseline, Qwen E6-full, and DeepSeek E6-full.

| Model | Repeated accept | Escalate | Strict corrected to reject | Safe handled by reject/escalate | Non-empty risk flags |
|---|---:|---:|---:|---:|---:|
| qwen/qwen3.7-max | 7 | 2 | 0 | 2 | 2 |
| deepseek/deepseek-v4-pro | 4 | 5 | 0 | 5 | 5 |

## Interpretation

Removing verdict-like tool summary fields changed model behavior, so the
previous E6-full equality with the tool baseline was not inevitable model
invariance. It was at least partly caused by the visible verdict summary.

The improvement is risk handling, not correctness verification. Neither model
strictly corrected a known false accept to `reject`; both only moved some
known false accepts to `escalate`. Qwen was conservative on 2/9 opportunity
cases, while DeepSeek was more conservative on 5/9, but DeepSeek also escalated
6 correct patches in the whole cohort and reduced correct recall to 20%.

The result supports a narrower claim:

> Removing deterministic verdict fields can make LLM verifiers less likely to
> blindly accept visible-test-passing hidden failures, but the effect manifests
> mainly as escalation and remains model-dependent.

It does not support an automatic merge-gate claim. The remaining false accepts
are still dangerous: Qwen repeats 7/9 and DeepSeek repeats 4/9 known false
accepts.

## Evidence Files

- Audit: `data/protocols/evp8_hard_e6_evidence_only_result_audit_v0_1.json`
- Opportunity analysis:
  `data/reviews/evp8_hard_e6_evidence_only_opportunity_analysis_v0_1.json`
- Qwen summary:
  `data/reviews/evp8_hard_e6_evidence_only_qwen_qwen3.7-max_full_summary.json`
- Qwen parsed reviews:
  `data/reviews/evp8_hard_e6_evidence_only_qwen_qwen3.7-max_full_reviews.jsonl`
- DeepSeek summary:
  `data/reviews/evp8_hard_e6_evidence_only_deepseek_deepseek-v4-pro_full_summary.json`
- DeepSeek parsed reviews:
  `data/reviews/evp8_hard_e6_evidence_only_deepseek_deepseek-v4-pro_full_reviews.jsonl`
