# Paper Outline: Verifiable Review of AI-Generated Patches

## Working Title

Verifiable Review of AI-Generated Patches in Real Software Projects

## One-Sentence Contribution

We study whether LLM-based reviewers can safely serve as merge gates for
AI-generated patches, and evaluate an evidence-first verification protocol that
accepts only claims supported by executable or tool-backed evidence.

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

RQ3. Does evidence-first verification reduce false accepts compared with
LLM-only review, majority review, or agent-context review?

RQ4. What evidence sources are most useful for patch acceptance decisions:
existing tests, targeted tests, static checks, differential execution, or
claim-level evidence packets?

## Expected Contributions

1. A paired patch-verification benchmark constructed from real bug/fix pairs.
2. An empirical study of LLM-only patch review reliability.
3. A taxonomy of patch-review failure modes.
4. An evidence-first verification protocol and baseline implementation.
5. A reproducible artifact with no-API validation, deterministic output
   comparison, documented model-selection boundaries, and optional API reruns.

## Non-Claims

- Do not claim that cross-review is generally better.
- Do not claim that LLM-only adjudication is reliable.
- Do not present oracle-gated results as pure model ability.
- Do not claim deployment readiness unless evidence sources are available
  before acceptance.
- Do not claim cross-model generality from the first single-model pilot.
