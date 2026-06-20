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
