# Pilot Dataset Construction

## Goal

Create a no-API pilot dataset that can test the patch-verification framing
before spending API calls.

Target for the first pilot:

- 5-8 source bugs;
- 20-30 candidate patches;
- at least 40 percent negative candidates;
- at least 2 projects;
- all candidates have an executable or tool-backed label.

## Starting Sources

Use the retained BugsInPy oracles as the first source because they already
provide paired buggy/fixed behavior and executable checks.

Candidate projects:

- `httpie`;
- `luigi`;
- `tqdm`;
- `black`;
- additional projects only after setup is reproducible.

## Candidate Construction

For each source bug, build up to four candidate patches:

1. `correct_reference`
   - the known fix;
   - expected outcome: `correct`.
2. `buggy_noop`
   - no change or original buggy hunk;
   - expected outcome: `irrelevant_or_noop` or `incorrect`.
3. `partial_fix`
   - only if the oracle or behavior has multiple checkable requirements;
   - expected outcome: `partial`.
4. `irrelevant_patch`
   - small unrelated change in a nearby file;
   - expected outcome: `irrelevant_or_noop`.

Do not construct `overfitted_fix` unless a visible/hidden evidence split exists.

## No-API Validation

Before API review:

- validate JSONL schema;
- ensure each candidate has expected outcome;
- ensure each candidate has at least one evidence source;
- run available oracle commands where local checkouts exist;
- generate a summary with candidate-type counts and project counts.

## API Pilot Readiness Gate

The API pilot can start only when:

- at least 20 candidates validate;
- correct and incorrect candidates are both present;
- no candidate exposes `expected_outcome` in model-visible context;
- evidence-first packets can be generated without hidden label leakage;
- metrics can be recomputed from JSONL records.
- model-visible `patch_text` contains realistic diff or source hunk evidence,
  not only neutral placeholders;
- at least 30 percent of candidates are realistic difficult negatives, such as
  `partial`, `overfitted`, or `test_passing_wrong`.

## Pilot 001 Result

The first generated pilot meets the schema and no-API metric gates:

- 7 retained BugsInPy-derived tasks;
- 30 candidates;
- 23 negative controls;
- 2 projects;
- 90 no-API verifier outputs;
- 7 reference diffs materialized from retained buggy/fixed checkouts;
- 7 comment-only source diffs used as applicable unrelated negative controls;
- 9 `partial_fix` candidates generated from multi-change or multi-line
  reference diffs;
- 30/30 candidates validated by apply + retained executable oracles;
- label-leakage check passed for model-visible evidence packets.

The current generated pilot meets the no-API API-readiness gate for a small
pilot: `api_readiness.ready = true` and `validation_summary.all_validated =
true`. The next step is prompt/run preparation for `llm_only` and
`evidence_first`; do not expand to majority or multi-model experiments yet.

## First API Conditions

Run only the minimum useful set:

1. one LLM-only reviewer;
2. one evidence-first verifier;
3. optional second reviewer only if cost is acceptable.

Do not run majority-review experiments until LLM-only and evidence-first
baselines are working.
