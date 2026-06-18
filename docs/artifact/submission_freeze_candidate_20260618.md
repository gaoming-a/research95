# Submission Freeze Candidate: Four-Anchor EVP-7 Package

Date: 2026-06-18

This packet records the current no-API freeze candidate for the paper and
anonymous artifact package. It is not a final freeze decision and does not
authorize model calls, cohort expansion, or evidence-level changes.

## Candidate State

- Paper route: bounded EVP-7 four-anchor evidence-visibility pilot.
- Evidence levels: E0/E2/E4/E6 only.
- Structural/no-API pipeline: 21 tasks, 6 projects, 98 candidates, and 392
  E0/E2/E4/E6 evidence packets.
- Paper-facing real verifier run: 20 tasks, 94 candidates, and 376 DeepSeek G5
  review records.
- Current IEEE draft target: `docs/paper/ieee_submission_draft.tex`.
- Current compiled PDF target: `outputs/paper_compile/ieee_submission_draft.pdf`
  local ignored build.
- Current anonymous artifact target:
  `artifacts/research95_anonymous_artifact.zip` local ignored build.
- Latest artifact readiness boundary: 303 packaged tracked files, audit
  `safe: true`, and required advisor workload packet included.

## What This Candidate Supports

- A bounded single-model EVP-7 observation that evidence visibility changes
  merge-gate decisions in the current cohort.
- A workload presentation that separates the 21/98/392 structural pipeline from
  the 20/94/376 real DeepSeek G5 paper-facing run.
- A submission package that includes the advisor-facing workload response,
  no-API submission handoff, final checklist, paper figures, and anonymous
  artifact gates.

## What This Candidate Does Not Decide

- It does not choose a target venue or final formatting constraint.
- It does not freeze the current 7-page IEEE PDF as the final submission draft.
- It does not approve second-model replication.
- It does not approve 30-50 bug expansion.
- It does not insert E1/E3/E5 into the current EVP-7 artifacts.
- It does not claim that the LLM beats the deterministic tool-only baseline.
- It does not turn the old prompt-only `stop_or_redesign` result into a positive
  claim.

## Required User Confirmations

Before this candidate becomes the final submission package, confirm:

1. Target venue and formatting constraints.
2. Whether the current 7-page IEEE PDF should be frozen as the submission draft.
3. Whether to keep the current no-API/no-expansion boundary for submission.
4. Whether GitHub sync should be retried later or local-only work should
   continue until the network failure boundary clears.

## Default Next Action

If no new decision is given, continue only no-API paper-submission maintenance:

- regenerate tracked paper tables and the IEEE draft;
- compile and inspect the ignored PDF;
- rebuild and audit the ignored anonymous artifact;
- rerun paper readiness and local quality gates;
- update handoff/checklist notes.
