# Leakage Policy

This policy defines what a verifier may see in the patch-verification study.
It is the boundary that prevents tool-augmented results from becoming hidden
oracle leakage.

## Core Rule

Verifier inputs may include only the evidence assigned to their evidence level.
They must not include final labels, reference-patch provenance, hidden evaluator
results, or manually assigned failure taxonomy labels.

## Evaluator-Only Fields

These fields are never shown to LLM verifiers:

- `expected_outcome`;
- `candidate_type`;
- `failure_type_label`;
- `patch_materialization`;
- evaluator-facing `patch_id` when it encodes construction type;
- `construction_notes`;
- reference patch diff unless the condition is explicitly marked as an oracle
  upper bound;
- hidden oracle paths;
- hidden oracle stdout/stderr;
- hidden fail-to-pass results;
- hidden regression results;
- manual validation notes;
- final merge label.

## Model-Visible Fields

These fields may be shown when allowed by the evidence condition:

- anonymous `model_candidate_id`;
- issue summary or task summary;
- candidate patch diff;
- touched files or changed functions;
- patch apply status;
- syntax/import/lint status;
- visible test names;
- visible test outcomes;
- visible runtime traces;
- generated targeted test outcomes;
- summarized tool evidence that is explicitly marked visible.

## Evidence Conditions

| Condition | May See | Must Not See |
| --- | --- | --- |
| LLM-only / E0 | issue summary, patch diff | test outcomes, oracle results, labels |
| Prompt evidence-first | issue summary, patch diff, evidence discipline instruction | hidden labels, oracle result |
| Static evidence / E2 | E0 + patch apply/static checks | visible/hidden test outcomes unless configured |
| Runtime / E3 | E2 + runtime trace | hidden evaluator result |
| Visible tests / E4 | E3 + visible test outcomes | hidden tests and final label |
| Generated tests / E5 | E4 + generated targeted test outcomes | reference patch and hidden evaluator |
| Full realistic tool evidence / E6 | all realistic visible tool evidence | final ground truth and hidden evaluator |
| Oracle upper bound / E7 | hidden evaluator summary | cannot support realistic merge-gate claims |

## Current Pilot Boundary

The current `tool_augmented_evidence` full run and the new
`tool_only_validation_summary` baseline use retained executable validation
summaries from the 30-candidate pilot. These are useful as a tool-summary
diagnostic and an upper-bound-style comparison, but they are not yet a final
hidden-evaluator-free realistic setting.

Paper wording must therefore distinguish:

- prompt-only `evidence_first`: negative/mixed result;
- `tool_augmented_evidence`: conditional tool-assisted verifier result on the
  current pilot;
- `tool_only_validation_summary`: deterministic tool-summary comparison, not
  standalone proof that LLMs add value beyond realistic visible tests.

## Acceptance Gate For Future Expanded Runs

Before a future expanded run can support the final evidence-visibility claim:

1. visible tests and hidden evaluator tests must be stored separately;
2. evidence packets must be generated from visible evidence only;
3. oracle-upper-bound conditions must be reported in a separate table;
4. prompts must pass automated leakage scans;
5. qualitative examples must be manually checked for accidental label leakage.
