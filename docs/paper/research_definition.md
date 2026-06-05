# Research Definition

## Core Problem

AI coding agents can generate patches for real software tasks, but a generated
patch is not automatically safe to merge. Existing tests may be incomplete, and
LLM reviewers can accept plausible but incorrect explanations or reject correct
patches for unsupported reasons.

This project studies patch acceptance as a verification problem:

> Given a real software task and a candidate patch, decide whether the patch
> should be accepted, rejected, or escalated based on executable or tool-backed
> evidence.

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

The target contribution is not a new foundation model or a broad benchmark. The
target contribution is an empirically validated patch-verification workflow:

1. Build paired real-task patch candidates.
2. Evaluate LLM-only patch review as a baseline.
3. Evaluate prompt-only evidence-first verification and report its failure
   modes.
4. Evaluate a tool-augmented verifier that can inspect patch-apply status and
   executable behavior summaries.
5. Analyze when unsupported patch plausibility causes false accepts and when
   evidence poverty causes false rejects or escalations.

## Revised Hypotheses

H1: LLM-only patch review is not a reliable merge gate because it can accept
plausible but partial patches.

H2: Prompt-only evidence-first verification can reduce false accepts, but may
lose correct-patch recall when the visible evidence packet lacks executable
behavior evidence.

H3: A tool-augmented verifier that sees patch-apply status and executable
behavior summaries can improve the safety/recall tradeoff relative to
prompt-only review on the same candidate set.

Secondary hypotheses:

- H4: Majority review does not reliably solve unsupported patch claims.
- H5: Escalation is necessary for patches whose correctness cannot be supported
  by available evidence.

## Non-Goals

- Do not claim that LLM-only review is deployment-ready.
- Do not treat a second LLM opinion as ground truth.
- Do not treat passing visible tests as full correctness.
- Do not rely on synthetic coding tasks as the primary evidence.
- Do not revive the old claim that cross-review is generally better.
- Do not present tool-augmented results as prompt-only model ability.
