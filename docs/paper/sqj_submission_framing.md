# SQJ Submission Framing and Claim Boundary

Status: no-API SQJ framing packet, updated 2026-06-30.

This document fixes the paper-facing route for Software Quality Journal (SQJ).
It is not a final submission package and does not authorize new experiments.

## Target

- Target venue: Software Quality Journal.
- Publication route: traditional / subscription route, not Open Access, unless
  APC is explicitly approved later.
- Manuscript type: regular original research article, not survey or review.
- Next manuscript format: Springer Nature `sn-jnl` LaTeX.
- Current source draft: `docs/paper/patch_verification_draft.md`.
- Historical source draft only: `docs/paper/ieee_submission_draft.tex`.

## Working Title

Evidence Visibility in LLM-Based Patch Verification: A Software Quality
Perspective

## One-Sentence Claim

Evidence visibility is a first-order experimental variable in LLM-based patch
verification: on a frozen real-bug candidate set, five LLMs change their
merge-gate decisions across evidence levels, but the response is model-dependent
and non-monotonic.

## SQJ Fit

The paper should be framed as a software quality and reliability study rather
than a model-ranking paper. The central quality problem is whether an LLM
verifier can be trusted as a merge gate when the evidence visible to the model
is incomplete, structured differently, or augmented with tool-derived behavior.

The SQJ-facing contribution is therefore:

1. A controlled evidence-visibility protocol for candidate patch verification.
2. A hidden-evaluator workflow that separates model-visible evidence from
   evaluator-only labels.
3. A five-model empirical study over a frozen 98-candidate by 7-level EVP-8
   packet set.
4. A quality-risk analysis showing model-dependent, non-monotonic decision
   behavior instead of a simple "more evidence is always better" curve.
5. A cost and execution-risk accounting ledger for real multi-model verifier
   experiments.
6. A supplementary source-acquisition/gate-readiness analysis showing that a
   fresh realistic agent-patch branch produced a real two-project hard-negative
   opportunity set but failed a predeclared three-project verifier-readiness
   gate.

## Research Questions

RQ1. How does evidence visibility change LLM merge-gate decisions for candidate
patches?

RQ2. Are evidence-level effects stable across models, or are they
model-dependent?

RQ3. Do higher evidence levels produce a monotonic improvement in verifier
decisions?

RQ4. What software-quality risks appear when an LLM verifier saturates,
over-escalates, or reacts inconsistently to evidence?

RQ5. What cost-observability and execution controls are needed for reproducible
multi-model LLM verifier studies?

## Core Results to Report

The paper may report these results:

- EVP-8 five-model synthesis is `passed` for the frozen v0.1 packet set.
- Each selected model produced 686 valid reviews over 98 candidates and 7
  evidence levels.
- DeepSeek V4 Pro and Qwen3.7 Max show visible variation across evidence
  levels.
- Kimi K2.6 and Gemini 2.5 Flash show smaller but still observable level-specific
  differences.
- Devstral 2 saturates to all-escalate behavior, which is a verifier reliability
  finding rather than a failure to hide.
- Aggregated five-model decisions are non-monotonic across E0-E6.
- Blocked Kimi attempts are cost and engineering-risk evidence, not valid model
  results.
- The fresh realistic hard-negative branch may be reported only as a
  supplementary gate-readiness result: 94 generated candidates yielded 26
  validated visible-pass/hidden-fail cases across two projects, while third
  project attempts failed because generated patches were correct-like,
  visible-failing, or failed materialization before validation.

## Forbidden Claims

The SQJ manuscript must not claim:

- LLM verifiers outperform deterministic visible-tool or test-based baselines.
- E6 is strictly or generally better than E4.
- Evidence levels establish a final monotonic effectiveness ranking.
- The 98-candidate EVP-8 set supports broad scale generalization.
- Blocked Kimi attempts are valid model-result records.
- Runner-estimated or provider-reported costs are complete external billing
  statements.
- A guarantee of SQJ recognition before school or department confirmation.
- The fresh realistic hard-negative branch is a three-project verifier-ready
  main experiment.
- Qwen or DeepSeek verifier APIs should be run on the fresh realistic branch
  while `ready_for_verifier_api=false`.
- The full-file generation-interface repair validates the verifier system or
  demonstrates practical autonomous patch verification.

## Result Mapping

| Manuscript element | Source artifact |
|---|---|
| EVP-8 five-model decision pattern | `data/protocols/evp8_five_model_synthesis_v0_1.json` |
| Paper table source | `docs/paper/generated_tables.md` |
| LaTeX table source | `docs/paper/generated_tables.tex` |
| Cost accounting | `data/reviews/evp8_cost_accounting_summary.json` |
| Cost narrative | `docs/experiments/evp8_cost_accounting_summary.md` |
| Protocol plan | `docs/experiments/evp8_journal_scale_execution_plan_20260620.md` |
| Canonical route | `docs/plans/final_paper_roadmap_zh.md` |
| Historical EVP-7 motivation | `docs/paper/patch_verification_draft.md` |
| Fresh realistic branch boundary | `data/protocols/evp8_realistic_hardneg_paper_claim_decision_packet_v0_1.json` |
| Fresh realistic gate result | `data/protocols/evp8_realistic_hardneg_combined_generation_gate_with_full_file_v0_1.json` |

## Suggested SQJ Structure

1. Introduction
2. Background and Related Work
3. Evidence Visibility Protocol
4. Candidate Patch and Evidence Packet Construction
5. Multi-Model Verifier Study
6. Results
7. Software Quality Risks and Cost Observability
8. Threats to Validity
9. Artifact and Reproducibility
10. Conclusion

The fresh realistic hard-negative branch should appear in Results or Threats
as a gate-readiness/source-acquisition subsection, not as the main verifier
experiment. Suggested subsection title:

> Fresh Realistic Hard-Negative Acquisition: A Gate-Readiness Negative Result

## Submission Readiness Gates

Before submission:

1. Confirm with the department or research office that SQJ is recognized under
   the current CCF C / school C-class route and is not on a high-risk or warning
   list for the publication year.
2. Confirm author role and affiliation requirements.
3. Generate a Springer Nature `sn-jnl` LaTeX draft.
4. Rebuild figures and tables from tracked summaries.
5. Run claim-boundary and local quality gates.
6. Prepare an SQJ-specific artifact checklist.
7. Keep API freeze active unless a new budgeted experiment is explicitly
   approved.
