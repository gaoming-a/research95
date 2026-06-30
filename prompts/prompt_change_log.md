# Prompt Change Log

This log records prompt changes for the patch-verification study. It is scoped
to experiment prompts, not agent system prompts.

## 2026-06-20 EVP-8 Visible Evidence Merge-Gate v0.1

- Prompt id: `evp8_visible_evidence_merge_gate_v0_1`
- Prompt file: `prompts/evp8_visible_evidence_merge_gate_v0_1.md`
- Protocol spec: `data/protocols/evp8_protocol_v0_1.json`
- Change type: new EVP-8 prompt template.
- Replaces: nothing. EVP-7 prompt `patch_verify_evidence_visibility_merge_gate_v1`
  remains the historical four-anchor pilot prompt.

Conflict and duplication check:

- The EVP-7 prompt is a merge-gate verifier prompt for `E0/E2/E4/E6`.
- The EVP-8 prompt keeps the same visible-only merge-gate boundary but targets
  the new adjacent-difference `E0-E6` protocol.
- The EVP-8 output schema removes evaluator-taxonomy-style fields and matches
  the protocol-defined keys:
  `decision`, `confidence`, `primary_reason`, `evidence_used`,
  `visible_contradictions`, `risk_flags`, and `human_review_needed`.
- The prompt does not expose per-candidate evaluator labels, hidden oracle
  outcomes, reference provenance, or final merge labels.
- The prompt is frozen for no-API Phase 0 auditing only. It does not authorize
  model calls or evidence-packet generation.

Verification:

- Run `python scripts\build_evp8_prompt_manifest.py --check`.
- Run `python scripts\audit_evp8_protocol_spec.py --check`.

## 2026-06-26 EVP-8 Visible Evidence Merge-Gate v0.2

- Prompt id: `evp8_visible_evidence_merge_gate_v0_2`
- Prompt file: `prompts/evp8_visible_evidence_merge_gate_v0_2.md`
- Protocol spec: `data/protocols/evp8_protocol_v0_2.json`
- Change type: JSON/schema-discipline repair for the accept-aware DeepSeek/Qwen
  retest.
- Replaces: no historical result. EVP-8 v0.1 remains the frozen five-model
  packet-set prompt; v0.2 is a separate accept-aware retest prompt.

Conflict and duplication check:

- v0.2 keeps the v0.1 visible-only merge-gate boundary and the same decision
  values: `accept`, `reject`, and `escalate`.
- v0.2 does not add hidden evaluator labels, hidden tests, reference-patch
  provenance, candidate types, or final merge labels.
- v0.2 does not change the substantive decision policy. It only makes the
  output contract stricter by requiring exact JSON, exact risk-flag enum
  values, and `human_review_needed=false` for supported accept/reject decisions.
- The change is not duplicated with EVP-7 because EVP-7 used the historical
  four-anchor prompt; this prompt targets the EVP-8 E0-E6 adjacent ladder.

Verification:

- Run
  `python scripts\build_evp8_prompt_manifest.py --spec-in data\protocols\evp8_protocol_v0_2.json --template-in prompts\evp8_visible_evidence_merge_gate_v0_2.md --manifest-out data\protocols\evp8_prompt_manifest_v0_2.json --boundary-audit-out data\protocols\evp8_prompt_boundary_audit_v0_2.json --check`.
- Run
  `python scripts\audit_evp8_protocol_spec.py --spec-in data\protocols\evp8_protocol_v0_2.json --summary-out data\protocols\evp8_protocol_v0_2_audit_summary.json --check`.

## 2026-06-30 EVP-8-HARD Tool-Contestation Merge-Gate v0.1

- Prompt id: `evp8_tool_contestation_merge_gate_v0_1`
- Prompt file: `prompts/evp8_tool_contestation_merge_gate_v0_1.md`
- Runner/config:
  `scripts/run_evp8_hard_tool_contestation.py` and
  `configs/evp8_hard_tool_contestation.example.json`
- Change type: new EVP-8-HARD ablation prompt for tool-evidence reliability
  and visible-test-only accept-premise contestation.
- Replaces: nothing. EVP-8 v0.2 remains the main visible-evidence merge-gate
  prompt; this prompt is a separate hard-case ablation.

Conflict and duplication check:

- The prompt keeps the v0.2 visible-only boundary: it does not expose hidden
  evaluator labels, hidden tests, hidden oracle outcomes, reference-patch
  provenance, or final merge labels.
- The prompt intentionally does not expose final deterministic tool verdict
  fields. The runner removes `rule_based_visible_merge_gate_decision`,
  `rule_based_visible_merge_gate_reasons`, and `source_decision` before prompt
  rendering.
- The prompt adds tool-contestation output fields:
  `coverage_concern`, `visible_tests_sufficient`,
  `tool_evidence_reliability`, `would_challenge_visible_test_only_accept`, and
  `challenge_reason`.
- The prompt is not a compatibility patch for v0.2. It answers a narrower
  causal question: whether models can challenge a visible-test-only accept
  premise when verdict-like tool summaries are absent.
- The result must be interpreted as risk triage when decisions move from
  `accept` to `escalate`; it does not establish automatic patch correctness
  verification.

Verification:

- Run
  `python -m py_compile scripts\run_evp8_hard_tool_contestation.py scripts\audit_evp8_hard_tool_contestation_results.py scripts\analyze_evp8_hard_tool_contestation_opportunity.py`.
- Run
  `python scripts\run_evp8_hard_tool_contestation.py --config configs\evp8_hard_tool_contestation.local.json --check-only`.
- Run
  `python scripts\audit_evp8_hard_tool_contestation_results.py --out data\protocols\evp8_hard_tool_contestation_result_audit_v0_1.json --check`.
- Run
  `python scripts\analyze_evp8_hard_tool_contestation_opportunity.py --out-json data\reviews\evp8_hard_tool_contestation_opportunity_analysis_v0_1.json --out-md docs\experiments\evp8_hard_tool_contestation_opportunity_analysis_v0_1.md --check`.
