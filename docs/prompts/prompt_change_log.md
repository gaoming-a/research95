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
  5-candidate DeepSeek official API redesign smoke;
  `outputs/patch_verification_tool_augmented_full_001`, a 30-candidate
  DeepSeek official API tool-augmented full run.

## `patch_verify_evidence_visibility_merge_gate_v1`

- Date: 2026-06-13
- Purpose: EVP-7 G5 evidence-visibility merge-gate verifier prompt for
  E0/E2/E4/E6 packet-level ablation.
- Previous version: none for EVP-7. This is not a replacement for
  `patch_verify_evidence_first_v1` and does not reuse
  `patch_verify_tool_augmented_evidence_v1`.
- Contradiction check: consistent with the EVP-7 protocol because it uses only
  model-visible evidence packets, the fixed accept/reject/escalate schema, and
  no retained-oracle or hidden P2P outcome. It also preserves the earlier
  `patch_verify_evidence_first_v1` stop/redesign boundary by treating this as a
  new evidence-visibility protocol prompt rather than a scale-up of the failed
  prompt-only condition.
- Label-leakage check: prompt manifest generation produced 184 current records with
  zero boundary findings. Candidate-specific evaluator fields such as
  `label_with_p2p_broad`, `candidate_type`, `expected_outcome`,
  `failure_type_label`, retained-oracle outcome, hidden P2P outcome, and
  reference provenance remain excluded. Generic schema enum values such as
  `partial_fix` are allowed only as possible verifier output categories, not as
  candidate labels.
- Expected experimental impact: enables the real G5 test of whether increasing
  evidence visibility changes false accept rate, correct recall, escalation,
  FACR, or Evidence Gain in genuine LLM verifier outputs.
- Runs that used it: DeepSeek official full run now covers the current
  8-task/46-candidate/184-record cohort after `youtube-dl_7` admission. The
  run used `deepseek-v4-pro`, concurrency 6, produced 183/184 parse-valid
  outputs, and preserved zero false accepts at E4/E6 in the aggregate metrics.
  Current prompt manifest/readiness artifacts:
  `data/reviews/evp7_g5_llm_prompt_manifest.jsonl` and
  `data/reviews/evp7_g5_llm_run_readiness.json`. Raw responses remain only in
  ignored `outputs/evp7_g5_llm_002/`.
