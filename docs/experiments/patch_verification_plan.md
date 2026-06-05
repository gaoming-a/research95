# Patch Verification Experiment Plan

## Goal

Build a small but realistic pilot for AI-generated patch verification. The
first pilot should be no-API and label-focused. API reviewer/verifier calls only
begin after the candidate schema and oracle labels validate locally.

## Candidate Sources

Phase 1 sources:

- existing BugsInPy buggy/fixed pairs from the old real-bug expansion;
- executable oracles in `scripts/oracles/`;
- patch hunks from the real fix commits.

Phase 2 sources:

- model-generated patches for the same tasks;
- SWE-bench Lite / Verified style tasks if setup cost is controlled;
- manually constructed partial or overfitted patches only when the construction
  is documented and oracle-checkable.

## Candidate Types

- Correct patch: the reference fixed patch or equivalent behavior.
- Buggy/no-op patch: the original buggy version or a patch that leaves the
  defect unchanged.
- Partial patch: fixes one behavior but misses another documented behavior.
- Overfitted patch: passes the visible hint but fails a hidden or stronger
  oracle.
- Irrelevant patch: changes unrelated code and should be rejected.

## No-API Pilot

Required files:

- `outputs/patch_verification_pilot_001/candidates.jsonl`.
- `outputs/patch_verification_pilot_001/evidence_packets.jsonl`.
- `outputs/patch_verification_pilot_001/verifier_outputs.jsonl`.
- `outputs/patch_verification_pilot_001/dataset_summary.json`.
- `outputs/patch_verification_pilot_001/metrics.json`.

Required checks:

- every candidate has a patch id, source bug id, project, patch text or source
  excerpt, and expected outcome;
- every candidate has at least one oracle or evidence source;
- correct and incorrect candidates are both present;
- labels can be recomputed without API calls.

### Pilot 001 Status

Completed on 2026-06-05.

Generated records:

- 7 retained real-bug tasks;
- 30 patch candidates;
- 90 deterministic verifier outputs;
- projects: `httpie` and `luigi`;
- candidate types: `correct_reference`, `buggy_noop`,
  `irrelevant_patch`, `partial_fix`;
- patch materialization types: retained buggy/fixed unified diff, empty diff
  control, comment-only source diff control, first-hunk partial diff, omitted
  change-block partial diff, and line-reverted replace partial diff.
- executable validation: 30/30 candidates apply and match retained oracle
  labels.

No-API baseline results:

- `accept_all`: accepted precision 0.2333, false accept rate 1.0,
  correct-patch recall 1.0.
- `reject_all`: false accept rate 0.0, correct-patch recall 0.0,
  false reject rate 1.0.
- `oracle_upper_bound`: accepted precision 1.0, false accept rate 0.0,
  correct-patch recall 1.0.

Interpretation:

- This validates schema, metrics, and label separation.
- This validates candidate construction and executable labels for a small API
  pilot.
- This does not yet validate the research hypothesis; that requires model
  reviewer outputs under `llm_only` and `evidence_first`.

## API Pilot

Only run after the no-API pilot passes.

Conditions:

1. LLM-only patch review.
2. Prompt-only evidence-first verifier.
3. Tool-augmented evidence verifier, after the prompt-only failure mode is
   documented.
4. Majority review only after the first two prompt-only conditions are stable.
5. Agent-context review only if there is a concrete context-ablation question.

Metrics:

- false accept rate;
- false reject rate;
- accepted precision;
- correct patch recall;
- escalation rate;
- invalid-output rate;
- cost.

## First Stop Gate

After 20-30 patch candidates, stop and inspect:

- Are incorrect patches realistic?
- Are there any test-passing wrong or partial patches?
- Does evidence-first verification improve false accept rate without rejecting
  almost everything?
- Are failure modes explainable at claim level?

If these answers are negative, do not scale the dataset.

## Revised Tool-Augmented Stage

The first DeepSeek full run returned `stop_or_redesign` for prompt-only
evidence-first verification. A 5-candidate failure-case smoke showed that
`tool_augmented_evidence` can recover the expected decisions when patch-apply
status and executable behavior summaries are visible.

Next full run:

- build 30-candidate tool-augmented inputs from the existing validation records;
- run only `tool_augmented_evidence` in a new output directory;
- compare against the previous `llm_only` and prompt-only `evidence_first`
  groups;
- report results as conditional tool-assisted verification, not as prompt-only
  model ability.
