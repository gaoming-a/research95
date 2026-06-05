# Paper Outline: Verifiable Review of AI-Generated Patches

## Working Title

Verifiable Review of AI-Generated Patches in Real Software Projects

## One-Sentence Contribution

We show that prompt-only LLM patch review has a safety/recall tradeoff on
real-bug patch candidates, then evaluate whether a tool-augmented verifier can
use executable evidence summaries to make safer accept/reject decisions.

## Motivation

AI coding agents increasingly generate patches for real issues. Existing
benchmarks often ask whether an agent can produce a passing patch, but software
teams also need to know whether a patch should be trusted. Previous experiments
in this project found that LLM-only code review has persistent false positives
on fixed/reference controls. That makes LLM-only review a weak merge gate.

## Research Questions

RQ1. How reliable are LLM-only reviewers when deciding whether AI-generated
patches should be accepted?

RQ2. What failure modes cause false accepts and false rejects in patch review?

RQ3. Why does prompt-only evidence-first verification fail to preserve
correct-patch recall in the first full pilot?

RQ4. Does a tool-augmented verifier improve the safety/recall tradeoff when it
sees patch-apply status and executable behavior summaries?

## Expected Contributions

1. A paired patch-verification benchmark constructed from real bug/fix pairs.
2. An empirical study of LLM-only patch review reliability.
3. A taxonomy of patch-review failure modes.
4. A negative result for prompt-only evidence-first verification under the
   configured gate.
5. A tool-augmented verification protocol and baseline implementation.
6. A reproducible artifact with no-API validation, deterministic output
   comparison, documented model-selection boundaries, and optional API reruns.

## Non-Claims

- Do not claim that cross-review is generally better.
- Do not claim that LLM-only adjudication is reliable.
- Do not present oracle-gated results as pure model ability.
- Do not present tool-augmented results as proof that prompt-only evidence-first
  succeeded.
- Do not claim deployment readiness unless evidence sources are available
  before acceptance.
- Do not claim cross-model generality from the first single-model pilot.
