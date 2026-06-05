# Verifiable Review of AI-Generated Patches in Real Software Projects

Draft status: pre-API methods draft, 2026-06-05.

This draft intentionally does not report model-review results. The current
evidence supports dataset construction, executable label validation, no-API
baselines, prompt-boundary checks, deterministic no-API reproducibility, and
model-selection boundary documentation. The main hypothesis requires the
pending API pilot.

## Abstract

AI coding agents increasingly produce patches for real software tasks, but a
patch that looks plausible is not necessarily safe to merge. This paper studies
patch acceptance as a verification problem: given a real task and a candidate
patch, decide whether the patch should be accepted, rejected, or escalated based
on evidence. We construct a pilot patch-verification dataset from retained
real-bug pairs, materialize source-level patch candidates, validate labels with
executable oracles, and prepare two review conditions: LLM-only patch review and
evidence-first verification. The current artifact contains 30 validated patch
candidates from 7 real-bug tasks across 2 projects, including 9 partial-fix
candidates. No-API baselines show the expected merge-gate tradeoff:
accept-everything has perfect correct-patch recall but false-accept rate 1.0,
while reject-everything has false-accept rate 0.0 but correct-patch recall 0.0.
The pending API pilot will test whether evidence-first verification reduces
false accepts without collapsing correct-patch recall.

## 1. Introduction

AI coding agents are increasingly used to generate patches for real codebases.
The standard question, "does the patch pass tests?", is insufficient when tests
are incomplete or when generated changes are plausible but partial. Software
teams need a merge-gate decision: accept, reject, or escalate.

This work treats patch review as a verification problem rather than a generic
bug-finding problem. The reviewer is asked to judge a candidate patch against a
task summary and visible patch context. The evaluator uses executable or
tool-backed evidence to determine whether the decision is correct.

The motivating failure mode comes from earlier experiments in this project:
LLM-only review produced useful signals but also over-reported defects on
fixed/reference controls. That makes prompt-only review unsuitable as a merge
gate without stronger evidence discipline.

## 2. Research Questions

RQ1. How reliable is LLM-only review when deciding whether candidate patches
should be accepted?

RQ2. Can evidence-first verification reduce false accepts compared with
LLM-only review?

RQ3. Does evidence-first verification preserve useful correct-patch recall, or
does it only reduce false accepts by rejecting or escalating too aggressively?

RQ4. Which patch types expose the most useful failure modes: empty/no-op
controls, unrelated changes, or partial fixes?

## 3. Dataset Construction

The pilot dataset is built from retained BugsInPy-derived real-bug assets. Each
source task has a buggy checkout, a fixed checkout, a task summary, touched
files, visible test hints, and retained executable oracles.

Each candidate record contains evaluator-facing fields, including `patch_id`,
`candidate_type`, `expected_outcome`, and oracle metadata. Model-visible inputs
use an anonymous `candidate_id` and omit evaluator labels, oracle paths, oracle
results, and construction notes.

The current pilot contains:

| item | value |
|---|---:|
| real-bug tasks | 7 |
| projects | 2 |
| patch candidates | 30 |
| correct reference patches | 7 |
| empty/no-op controls | 7 |
| unrelated controls | 7 |
| partial-fix candidates | 9 |

Patch materialization uses retained source artifacts:

- `buggy_fixed_unified_diff`: reference diff between buggy and fixed checkouts.
- `empty_diff_against_buggy_checkout`: no-op control.
- `local_comment_only_unified_diff`: applicable unrelated source change.
- `first_hunk_of_reference_unified_diff`: partial candidate from a multi-hunk fix.
- `reference_diff_with_one_change_omitted`: partial candidate omitting one change block.
- `reference_replace_with_one_line_reverted`: partial candidate reverting one line inside a replace block.

## 4. Executable Label Validation

Candidate labels are validated by applying each candidate patch to a copied
buggy checkout and running retained executable oracles. This guards against
purely prompt-based or manually asserted labels.

Current validation status:

| validation item | value |
|---|---:|
| candidates validated | 30 |
| patches applied | 30 |
| oracle runs | 30 |
| validation failures | 0 |

Correct patches are expected to pass all retained oracles. Negative candidates
(`incorrect`, `irrelevant_or_noop`, and `partial`) are expected to fail at least
one retained oracle.

## 5. Review Conditions

### LLM-Only Review

The reviewer sees the task summary, visible context, and candidate patch. It
must output one JSON object with decision, confidence, claims, rationale, and
uncertainty. It does not see hidden oracle paths or oracle results.

### Evidence-First Verification

The reviewer sees the same task and patch context plus model-visible evidence
source metadata and visible test hints. It must tie every accept/reject decision
to concrete visible evidence. If the visible evidence is insufficient, it should
escalate.

### Oracle Upper Bound

The evaluator can use hidden labels and oracle outcomes to produce an upper
bound. This is not model capability and must be reported separately.

## 6. Metrics

Primary metrics are patch-level:

- false accept rate: incorrect, partial, or unrelated patches accepted;
- false reject rate: correct patches rejected;
- accepted precision: accepted patches that are actually correct;
- correct-patch recall: correct patches accepted;
- escalation rate: patches sent to human/tool verification;
- invalid-output rate and cost.

Escalation is neither accept nor reject. It should be reported separately
because reducing false accepts by escalating everything is not a useful merge
gate.

## 7. Current No-API Results

The current no-API baselines validate the metric implementation and expected
tradeoffs.

| baseline | accepted precision | false accept rate | correct recall | false reject rate |
|---|---:|---:|---:|---:|
| accept-all | 0.2333 | 1.0000 | 1.0000 | 0.0000 |
| reject-all | NA | 0.0000 | 0.0000 | 1.0000 |
| oracle upper bound | 1.0000 | 0.0000 | 1.0000 | 0.0000 |

Interpretation: the dataset and metrics expose the intended merge-gate tension.
The no-API results do not test the research hypothesis because no real model
reviewer decisions have been collected.

## 8. API Pilot Plan

The first API pilot should run only two conditions on the validated 30
candidates:

1. `llm_only`
2. `evidence_first`

Before running API calls, the executor must:

- create an untracked local API config from `configs/api_pilot.example.json`;
- set a real OpenRouter model slug;
- provide `.env` with `OPENROUTER_API_KEY`;
- run `scripts/preflight_api_pilot.py`;
- run a two-candidate smoke pilot before the full 30-candidate run.

The API runner writes `reviews.jsonl`, `metrics.json`, raw responses, and
`run_summary.md`.

## 9. Reproducibility and Handoff Controls

The pre-API artifact includes deterministic reproduction checks for the local
dataset construction pipeline. The original no-API pilot and a reproduced run
are compared by hashing deterministic output files:

- `candidates.jsonl`
- `evidence_packets.jsonl`
- `verifier_outputs.jsonl`
- `dataset_summary.json`
- `metrics.json`
- `validation_summary.json`
- `pilot_report.md`

The current comparison checks 7 deterministic files and reports no missing or
mismatched files. Runtime work directories, raw API responses, external
checkouts, and environment-dependent files are not treated as deterministic
reproducibility evidence.

Generated paper tables for the current pre-API state are available in
`docs/paper/generated_tables.md` and `docs/paper/generated_tables.tex`. These
tables are generated from JSON outputs rather than manually copied values.

The execution plan also separates local pre-API checks from model experiments.
The current handoff packet refreshes readiness, paper readiness, plan progress,
human-required inputs, Git-sync state, OpenRouter catalog visibility, and
deterministic reproducibility. This is an engineering control: it prevents
dry-run, mock, or local validation outputs from being mistaken for model
results.

## 10. Model Selection Boundary

The first real API pilot is a within-model comparison. The same model must be
used for `llm_only` and `evidence_first`, so the first claim controls for base
model capability but does not establish cross-model generality.

Before any local model config is created, the executor must document:

- concrete OpenRouter slug;
- provider;
- selection source and date;
- capability source or capability band;
- reason for selection;
- known limitations.

The current shortlist recommends `anthropic/claude-sonnet-4.6` as a
conservative first pilot candidate because it is a concrete, non-`latest`,
non-preview OpenRouter slug and is visible in the public model catalog. That is
not an experiment decision by itself. The user must still confirm the slug and
rationale before `configs/model_selection.local.json` and
`configs/api_pilot.local.json` are generated.

The local config helpers support a public OpenRouter catalog check before
writing local config. This only verifies slug visibility; it does not prove API
key access, pricing, provider routing, model quality, or paper suitability.

## 11. Threats to Validity

Dataset size is small. The current pilot is designed to validate the method and
failure surfaces, not to make broad claims about all AI-generated patches.

The partial-fix candidates are source-backed and oracle-checkable, but they are
constructed from retained reference diffs rather than generated by live coding
agents. A later stage should add model-generated patches or SWE-bench-style
tasks.

Visible test hints may not represent the evidence actually available in all
engineering workflows. The protocol should distinguish visible context,
evidence packets, and hidden evaluator oracles.

Model behavior can drift over time and across providers. Every API run must
record model slug, provider, date, prompt version, decoding settings, cost, raw
response path, and invalid-output status.

The first pilot uses a single model by design. This is appropriate for testing
whether evidence-first prompting changes acceptance behavior within one model,
but it cannot support claims about all frontier models or all coding agents.

## 12. Current Conclusion

The current artifact establishes a validated patch-verification pilot and a
ready-to-run API protocol. It does not yet establish that evidence-first
verification improves over LLM-only review. That claim depends on the pending
API pilot and must be evaluated using false accept rate, accepted precision,
correct-patch recall, escalation rate, and invalid-output rate.
