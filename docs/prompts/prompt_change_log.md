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
