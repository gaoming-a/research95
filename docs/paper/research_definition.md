# Research Definition

## Core Problem

Candidate patches for real software tasks can come from reference fixes,
constructed controls, AI generators, or agent workflows. A candidate patch is
not automatically safe to merge merely because it looks plausible or passes
some visible checks. Existing tests may be incomplete, and LLM reviewers can
accept plausible but incorrect changes or reject correct patches for
unsupported reasons.

This project studies patch acceptance as a verification problem:

> Given a real software task and a candidate patch, decide whether the patch
> should be accepted, rejected, or escalated based on executable or tool-backed
> evidence visible to the verifier.

## Why This Is Different From the Old Project

The old project asked whether LLM reviewers can find bugs in source excerpts.
That framing produced useful negative evidence: LLM-only review and majority
review over-reported fixed/reference controls.

The new project asks whether a candidate patch should be merged. That changes
the unit of analysis:

| Old Unit | New Unit |
| --- | --- |
| Source excerpt | Candidate patch |
| Bug found / not found | Accept / reject / escalate |
| False positive on fixed code | False accept or false reject |
| Reviewer explanation | Evidence-supported patch claim |
| Regression oracle as post-hoc label | Evidence source for verification |

## Revised Target Contribution

The target contribution is not a new foundation model or an immediate broad
benchmark. The target contribution is an empirically validated
evidence-visibility workflow for candidate patch verification:

1. Build paired real-task patch candidates.
2. Evaluate LLM-only patch review as a baseline.
3. Evaluate prompt-only evidence-first verification and report its negative or
   mixed result under the configured gate.
4. Vary visible evidence levels from task/patch context through realistic tool
   evidence summaries.
5. Compare the resulting false accepts, accepted precision, correct recall,
   escalation, utility, and claim boundaries.
6. Report tool-augmented verification separately when executable behavior
   summaries are visible, because that is an evidence-assisted workflow rather
   than prompt-only model ability.
7. Position the contribution against real-bug benchmarks, test-suite-based
   patch validation, LLM program repair, and agentic software-engineering
   systems: those lines motivate the setting, while this paper isolates the
   evidence visible to the verifier at merge-gate decision time.

## Revised Hypotheses

H1: LLM-only patch review is not a reliable merge gate because it can accept or
explain plausible but unsupported patch claims.

H2: Prompt-only evidence-first verification can reduce false accepts, but may
lose correct-patch recall when the visible evidence packet lacks executable or
tool-backed behavior evidence.

H3: Increasing evidence visibility changes merge-gate behavior: safety,
correct-patch recall, escalation, and utility should be reported together
rather than collapsed into a single accept/reject score.

Secondary hypotheses:

- H4: For clear executable outcomes, deterministic visible-tool evidence may
  dominate binary accept/reject decisions; any LLM contribution must be
  bounded and separated from tool-only baselines.
- H5: Escalation is necessary for patches whose correctness cannot be supported
  by available evidence.
- H6: The current EVP-7 result supports bounded pilot observations only; it does
  not establish scale generality, deterministic-baseline superiority, or strict
  E6-over-E4 superiority.
- H7: Evidence Gain is a descriptive pilot metric for the frozen EVP-7 protocol,
  not a proposed universal benchmark score.

## Non-Goals

- Do not claim that LLM-only review is deployment-ready.
- Do not treat a second LLM opinion as ground truth.
- Do not treat passing visible tests as full correctness.
- Do not rely on synthetic coding tasks as the primary evidence.
- Do not revive the old claim that cross-review is generally better.
- Do not present tool-augmented results as prompt-only model ability.
- Do not title or frame the current paper as primarily about AI-generated
  patches until generated patches become a dominant validated candidate source.
