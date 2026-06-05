# Prompt Change Log

This log starts fresh for the patch-verification project.

Do not copy old real-bug review prompts into this file unless they are actively
adapted for patch verification. Every new prompt entry must record:

- prompt id;
- purpose;
- previous version, if any;
- contradiction check;
- label-leakage check;
- expected experimental impact;
- runs that used it.

## `patch_verify_llm_only_v1`

- Purpose: baseline patch review using only task context and patch text.
- Previous version: none.
- Contradiction check: consistent with the current plan because it is a
  baseline, not the proposed evidence-first method.
- Label-leakage check: prompt template does not include evaluator `patch_id`,
  `candidate_type`, `expected_outcome`, `patch_materialization`, hidden oracle
  path, oracle result, or construction notes.
- Expected experimental impact: estimates unsupported accept/reject behavior.
- Runs that used it: none yet.

## `patch_verify_evidence_first_v1`

- Purpose: evidence-constrained patch verification requiring explicit visible
  evidence for accept/reject decisions.
- Previous version: none.
- Contradiction check: does not expose hidden oracle labels; it compares
  evidence discipline rather than oracle-gated upper bound behavior.
- Label-leakage check: prompt template uses only model-visible evidence packet
  fields.
- Expected experimental impact: should reduce unsupported accepts, possibly by
  increasing escalation when visible evidence is insufficient.
- Runs that used it: none yet.

See `docs/prompts/api_pilot_prompts.md` for the full prompt templates.

## `patch_verify_tool_augmented_evidence_v1`

- Date: 2026-06-05
- Purpose: failure-case redesign smoke after the DeepSeek full run produced a
  `stop_or_redesign` gate.
- Relationship to earlier prompts: this is not a replacement for
  `patch_verify_evidence_first_v1`; it is a separate tool-augmented condition.
- Added evidence: patch-apply status and retained oracle execution summaries.
- Boundary: because the model sees tool execution outcomes, results from this
  condition must be reported separately from prompt-only review conditions.
- Label-leakage rule: evaluator fields such as `expected_outcome`,
  `candidate_type`, `patch_materialization`, `hidden_oracles`,
  `oracle_command`, `oracle_workdir`, construction notes, and label confidence
  remain excluded from rendered prompts.
- Runs that used it: `outputs/patch_verification_redesign_smoke_001`, a
  5-candidate DeepSeek official API redesign smoke.
