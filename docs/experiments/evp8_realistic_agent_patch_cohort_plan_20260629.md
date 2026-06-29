# EVP-8 Realistic Agent-Patch Cohort Plan

Date: 2026-06-29

This is a no-API execution plan. It does not authorize model calls, prompt
changes, or mutation of the existing EVP-8 / EVP-8-HARD cohorts.

## Plain-Language Summary

The current result is meaningful but still too narrow. EVP-8-HARD shows that
when verdict-like tool summaries are visible, Qwen and DeepSeek simply follow
the tool-only baseline. After those verdict fields are removed, both models
change behavior, but mainly by escalating some risky cases instead of strictly
rejecting them.

In simple terms:

> The current system can show that evidence presentation changes LLM decisions,
> but it cannot yet prove that LLMs reliably verify real AI-generated patches.

The next step is to build a separate realistic or agent-like patch cohort. The
goal is not to make the model look better. The goal is to create enough
realistic tool failure cases to test whether an LLM adds anything beyond the
visible tools.

## Why This Is The Next Step

The main weakness is no longer "we need another model." The current two-model
evidence-only result already shows model dependence:

- Qwen preserves correct-patch recall but still accepts most known false
  accepts.
- DeepSeek escalates more false accepts but also escalates many correct
  patches.

Adding another same-prompt model would mostly repeat this pattern unless the
candidate distribution changes. The scientific problem is candidate strength:
the current hard-case opportunity set has only nine repeated false accepts, all
concentrated in `httpie`.

To make a stronger paper, the next cohort must contain realistic mistakes that
visible tools can plausibly miss:

- test-passing but semantically wrong agent patches;
- partial fixes that cover the obvious failing path but miss edge cases;
- regressions introduced by plausible edits;
- overfitted special-case patches;
- correct reference or independently validated patches as recall controls.

## Research Question

### RQ-R1: Do evidence-only LLM verifiers add value beyond visible tools on realistic agent-style patches?

Compare three systems on the same hidden-label-separated cohort:

| System | Purpose |
|---|---|
| tool-only baseline | Measures what visible tools alone would decide. |
| Qwen evidence-only | Tests high-recall LLM triage behavior. |
| DeepSeek evidence-only | Tests more conservative LLM triage behavior. |

The important quantity is opportunity-set behavior, not only full-cohort
accuracy:

- tool false accepts changed to LLM reject;
- tool false accepts changed to LLM escalate;
- tool false rejects changed to LLM accept;
- cost in additional false rejects or escalations on correct patches.

## Scope

Target cohort:

- 50-100 candidate patches;
- at least 30 realistic agent-generated or agent-like candidates;
- at least 25 non-trivial hard negatives;
- at least 15 visible-test-passing hidden-failing candidates if available;
- at least 10 correct or independently validated patches as recall controls;
- at least 3 projects represented, unless source availability blocks this.

This cohort must remain separate from:

- the old 98-candidate controlled EVP-8 cohort;
- the current 47-candidate EVP-8-HARD cohort;
- any historical raw agent logs that cannot be validated without leaking hidden
  labels.

## Candidate Admission Rules

Each candidate must have:

- stable `candidate_id`;
- stable `task_id` and project name;
- candidate source category:
  - `real_agent_generated`;
  - `agent_like_generated`;
  - `human_reference`;
  - `controlled_negative`;
- patch application status;
- model-visible patch evidence;
- visible tool evidence;
- evaluator-only hidden label;
- evaluator-only hidden oracle or validation rationale.

Allowed labels:

- `correct`;
- `partial`;
- `regression`;
- `overfitted`;
- `test_passing_wrong`;
- `irrelevant_or_noop`;
- `environment_invalid`.

Only non-`environment_invalid` candidates can enter the model-call cohort.

## Evidence Boundary

Model-visible records may contain:

- task summary;
- issue or failure symptom summary if available;
- touched files and safe code context;
- patch diff;
- visible test command names;
- visible test outcomes;
- static-analysis or runtime summaries that a realistic verifier could see.

Model-visible records must not contain:

- final correctness label;
- hidden oracle name or result;
- reference-patch provenance;
- source file path that reveals the label;
- deterministic accept/reject verdict;
- `rule_based_visible_merge_gate_decision`;
- `rule_based_visible_merge_gate_reasons`;
- `source_decision`;
- raw model response text.

## Phase 0: Source Inventory

Goal: determine whether enough realistic patch material already exists.

Actions:

1. Inventory tracked candidate manifests, prior agent-patch logs, and
   validation summaries.
2. Count candidates by project, source category, label, application status, and
   visible/hidden evidence availability.
3. Exclude raw provider outputs, unvalidated patches, and candidates whose
   hidden label is only inferable from leaked metadata.

Pass condition:

- at least 50 candidate sources are available for curation; or
- at least 30 are available and there is a clear, no-API path to generate more
  agent-like candidates later.

Stop condition:

- fewer than 25 usable non-control candidates exist and no validation path is
  available.

## Phase 1: Candidate Curation Without API

Goal: create a draft manifest with hidden labels separated from model-visible
evidence.

Outputs:

- evaluator-only manifest;
- model-visible seed manifest;
- source-inventory summary;
- leakage audit summary.

Pass condition:

- 50-100 non-environment-invalid candidates;
- at least 25 non-trivial hard negatives;
- no evaluator-only label appears in model-visible records;
- no hidden oracle result appears in model-visible records;
- project/source distribution is reported explicitly.

Stop condition:

- hard negatives are too few;
- candidates are dominated by one project without a clear limitation note;
- model-visible records require hidden oracle information to be meaningful.

## Phase 2: Visible Tool Baseline Gate

Goal: test whether the cohort has enough headroom for LLM-added value.

Run only visible tools and deterministic policy. Do not call model APIs.

Required metrics:

- accept/reject/escalate counts;
- false accepts against evaluator-only labels;
- false rejects against evaluator-only labels;
- opportunity-set size;
- visible-test-passing hidden-failing count;
- per-project and per-source opportunity counts.

Pass condition:

- at least 10 tool opportunity cases; and
- opportunity-set rate at least 15%; and
- at least 5 visible-test-passing hidden-failing false accepts.

Stop condition:

- the tool baseline has almost no mistakes;
- all mistakes are environment artifacts;
- opportunity cases are concentrated in one trivial source type.

If this gate fails, do not run LLM APIs. Report that the cohort is too
tool-solved or too weak for the intended question.

## Phase 3: Packet Dry-Run And Prompt Boundary

Goal: ensure that evidence-only packets are structurally valid before any API
execution.

Required checks:

- rendered prompt hashes only, not rendered prompt text;
- output schema dry-run;
- hidden-label leakage scan;
- no verdict-like field scan;
- expected output absence check;
- cost and credential presence check without printing key values.

Pass condition:

- all packets pass schema checks;
- leakage findings = 0;
- verdict-like visible fields = 0;
- API call attempted = false.

## Phase 4: Qwen-First Model Execution

This phase requires separate explicit user authorization after Phases 0-3 pass.

Execution order:

1. Qwen evidence-only run;
2. raw-output-free coverage and leakage audit;
3. opportunity-set analysis;
4. decision whether DeepSeek replication is still useful;
5. DeepSeek evidence-only run only if authorized after Qwen audit.

Stop condition:

- parsed reviews are incomplete;
- raw response text appears in tracked files;
- prompt boundary changes from the dry-run packet;
- Qwen result already shows no useful signal and DeepSeek would not answer a
  distinct question.

## Phase 5: Analysis And Paper Use

Required reports:

- whole-cohort metrics with Wilson 95% confidence intervals;
- opportunity-set transition table;
- accepted precision and correct recall;
- false accept rate and false reject rate;
- escalation workload;
- paired bootstrap intervals for Qwen vs tool-only and DeepSeek vs tool-only;
- per-project and per-source breakdown;
- 5-10 false-accept case studies without patch diff disclosure if needed.

Supported claim only if the data supports it:

> Evidence-only LLM verifiers can change visible-tool decisions on realistic
> agent-style patch failures, mostly by escalating risky cases rather than by
> reliably proving correctness.

Unsupported unless the data is much stronger:

- LLM verifier is a reliable automated merge gate;
- LLM verifier generally outperforms visible tools;
- escalation is equivalent to correctness verification;
- one model is generally better across projects and patch sources.

## Immediate Next Actions

1. Implement a no-API inventory script for realistic/agent patch sources.
2. Produce a source inventory JSON and Markdown report.
3. Decide whether existing local sources can reach 50-100 candidates.
4. If not, write a separate candidate-generation plan before generating new
   patches.
5. Do not run any model API until the visible tool baseline gate passes.

## Practical Meaning

This plan turns the current work from "LLM copied or partially escaped the
tool baseline" into a stronger engineering question:

> In realistic AI patch review, where tools sometimes miss plausible wrong
> patches, can an LLM identify enough risk to justify human escalation without
> destroying recall?

That is a practical paper claim because it matches how merge review is used:
reduce dangerous auto-accepts, identify cases needing human review, and measure
the cost of that safety in extra escalations.
