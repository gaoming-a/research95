# EVP-8 Prompt-Setting Audit v0.1

Date: 2026-07-06

This is a no-API, raw-output-free audit of whether the recent weak/limited
experimental results are caused by the experimental prompt.

## Bottom Line

The result is not best explained as a prompt implementation bug. The visible
evidence prompt passed boundary checks, does not expose hidden labels or hidden
oracles, and the three repaired model runs are parse-valid and matrix-complete.

It is, however, partly explained by the prompt/evidence setting if the expected
result was a semantic verifier beyond visible tools. The main prompt asks for a
visible-only merge-gate decision, and E6 explicitly adds a deterministic visible
merge-gate summary. Under that setting, models are expected to follow visible
test/tool evidence. That is a design boundary, not a JSON/schema prompt bug.

## Evidence Checked

- Main prompt: `prompts/evp8_visible_evidence_merge_gate_v0_2.md`
- Contestation prompt: `prompts/evp8_tool_contestation_merge_gate_v0_1.md`
- Prompt boundary audit:
  `data/protocols/evp8_prompt_boundary_audit_v0_3_qwen_first_prompt_v0_2.json`
- Three-model repaired summaries:
  - `data/reviews/evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.json`
  - `data/reviews/evp8_deepseek_repaired_v0_3_prompt_v0_2_label_conditioned_summary.json`
  - `data/reviews/evp8_gemini_repaired_v0_3_prompt_v0_2_label_conditioned_summary.json`
- E6 no-verdict ablation:
  `data/reviews/evp8_e6_no_verdict_ablation_comparison.json`
- Tool-contestation opportunity analysis:
  `docs/experiments/evp8_hard_tool_contestation_opportunity_analysis_v0_1.md`
- Realistic-agent no-verdict comparison:
  `docs/experiments/evp8_realistic_agent_qwen_merge_label_variant_comparison_v0_3.md`

## Main Prompt Boundary

The main prompt is internally consistent for the current bounded study:

- It explicitly says to use only visible evidence.
- It forbids hidden evaluator labels, hidden tests, hidden oracle outcomes,
  reference-patch provenance, and final merge labels.
- The boundary audit passed with no template or sampled render findings.
- The schema contract is complete and strict enough to avoid parse/schema drift.

Therefore, the current poor/limited results should not be attributed to hidden
label leakage, missing schema fields, invalid enum wording, or parser loss.

## Three-Model E6 Pattern

| model | accept | reject | escalate | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen | 24 | 74 | 0 | 20 | 4 | 83.33% | 95.24% | 5.19% | 0.00% |
| DeepSeek | 21 | 73 | 4 | 17 | 4 | 80.95% | 80.95% | 5.19% | 4.08% |
| Gemini | 25 | 73 | 0 | 20 | 5 | 80.00% | 95.24% | 6.49% | 0.00% |

This is a coherent visible-evidence merge-policy result: E6 recovers most
correct-reference accepts, but it still accepts a small set of partial or
regression patches that visible tests/tool summaries do not distinguish.

## Verdict-Anchoring Diagnosis

The E6 no-verdict ablation shows that verdict anchoring exists but is not the
whole explanation.

| condition | accept | reject | escalate | accepted precision | correct recall | false accept rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| rule-only | 25 | 73 | 0 | 80.00% | 95.24% | 6.49% |
| DeepSeek E6-full | 23 | 75 | 0 | 82.61% | 90.48% | 5.19% |
| DeepSeek E6-no-verdict | 11 | 73 | 14 | 100.00% | 52.38% | 0.00% |
| Qwen E6-full | 24 | 74 | 0 | 83.33% | 95.24% | 5.19% |
| Qwen E6-no-verdict | 23 | 74 | 1 | 82.61% | 90.48% | 5.19% |

Removing verdict-like fields made DeepSeek much more conservative and removed
false accepts by escalation, but Qwen remained close to the full condition.
That means the explicit verdict field is a model-dependent factor, not the sole
cause. Visible test/tool evidence itself is strong enough to anchor Qwen.

## Tool-Contestation Check

The separate tool-contestation prompt does what the main prompt does not try to
do: it asks the model to challenge visible-test-only accept premises and assess
coverage. On the nine hard false-accept opportunity cases, DeepSeek moved 9/9
to escalation and Qwen moved 8/9 to escalation.

That is useful risk-triage evidence, but it changes the task. It should not be
silently treated as a repair of the main E0-E6 prompt, because it optimizes a
different behavior: challenge/escalate rather than ordinary merge-gate
accept/reject under the predefined evidence ladder.

## Diagnosis

- Not supported: the weak result comes from a malformed prompt, schema bug,
  hidden-label leakage, or parse failure.
- Supported: the weak result is partly a consequence of the intended
  visible-only prompt setting if the hoped-for outcome was tool-independent
  semantic verification.
- Supported: the deterministic visible-tool baseline is already strong on this
  frozen cohort, leaving only a small 6/98 opportunity set for the model to
  improve.
- Supported: stronger coverage-contestation wording can reduce unsafe accepts
  mostly by escalation, but that is a separate experimental condition with a
  recall/automation tradeoff.

## Current Claim Boundary

The safe interpretation is:

> The repaired EVP-8 results measure evidence-conditioned merge-gate policy
> behavior under visible evidence. They do not show that the models are reliable
> autonomous patch-correctness verifiers, and the remaining false accepts are
> consistent with visible evidence that lacks hidden semantic coverage.

Do not replace the main prompt or rerun APIs without first deciding whether the
next question is still the E0-E6 evidence-visibility ladder, or a new
coverage-contestation / risk-triage condition.
