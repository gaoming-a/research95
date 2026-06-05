# Previous Findings Summary

This document is the only retained summary of the previous LLM code-review
direction. The full old plans, run logs, prompt histories, and paper drafts were
not migrated because they can pull the new project back into the failed
cross-review framing.

## What Failed

- The original strong hypothesis was that cross-review, majority voting, or
  agent-style context would make LLM code review generally more reliable.
- The experiments did not support that hypothesis.
- Majority voting continued to over-report fixed/reference controls.
- Patch-hunk context removed whole-file truncation artifacts but did not remove
  false positives.
- Evidence-constrained prompting reduced some false positives but harmed recall.
- Agent-style context changed behavior but did not reliably control false
  positives.
- LLM-only adjudication accepted unsupported claims and should not be used as
  ground truth.

## What Remains Useful

- Paired buggy/fixed controls are valuable because they expose false positives.
- Executable oracles are valuable because they separate model opinion from
  behavioral evidence.
- Claim-level evidence is valuable because candidate-level detection can hide
  wrong or unsupported explanations.
- The old results motivate the new question: whether AI-generated patches can be
  accepted safely only when review claims are evidence-backed.

## Carry-Forward Rule

Use these findings only as motivation for patch verification. Do not revive the
old claim that cross-review or majority voting is itself the solution.
