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

## Target Contribution

The target contribution is not a new foundation model or a broad benchmark. The
target contribution is an empirically validated verification protocol:

1. Build paired real-task patch candidates.
2. Evaluate LLM-only patch review as a baseline.
3. Evaluate majority and agent-context review as weaker baselines.
4. Evaluate evidence-first verification as a controlled workflow.
5. Analyze when unsupported claims cause false accepts or false rejects.

## Main Hypothesis

H1: Evidence-first patch verification reduces false accepts compared with
LLM-only review, while preserving a useful rate of correct patch acceptance.

Secondary hypotheses:

- H2: LLM-only review makes both false accept and false reject errors on
  real-task patches.
- H3: Majority review does not reliably solve unsupported patch claims.
- H4: Escalation is necessary for patches whose correctness cannot be supported
  by available evidence.

## Non-Goals

- Do not claim that LLM-only review is deployment-ready.
- Do not treat a second LLM opinion as ground truth.
- Do not treat passing visible tests as full correctness.
- Do not rely on synthetic coding tasks as the primary evidence.
- Do not revive the old claim that cross-review is generally better.
