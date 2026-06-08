# Httpie AI Patch Generation Attempt

## Scope

Run id: `httpie_ai_patch_stage_ab_001`.

This run used DeepSeek official API with `deepseek-v4-pro` to generate two AI
candidate patches for each of the five validated `httpie` Stage A/B tasks.

This run generated patches only. It did not call reviewer/verifier APIs.

## Generation Protocol

Model-visible input included:

- task id;
- project name;
- issue summary;
- touched file names;
- visible test hint;
- buggy source from the retained buggy checkout.

Model-visible input excluded:

- reference patch;
- fixed checkout;
- hidden oracle paths;
- oracle results;
- expected outcome;
- candidate type labels.

## Execution Notes

The first execution stopped at `bugsinpy_httpie_5__ai_patch_01` because the
model response consumed all generation budget in reasoning tokens and returned
empty final content.

The generator was then changed to:

- write prompt manifest and pending candidates incrementally;
- reuse already saved raw responses;
- keep failed raw attempts instead of overwriting them;
- allow retry attempts to be written as separate raw files.

A later retry with `max_tokens=8192` still returned empty final content for
`bugsinpy_httpie_5__ai_patch_01`. A shorter source context completed the full
10-patch generation.

## Validation Result

Validation was run with `validate_patch_candidates.py` over
`outputs/httpie_ai_patch_stage_ab_001/candidates.pending.jsonl`.

| item | count |
|---|---:|
| generated candidates | 10 |
| patch applied | 4 |
| oracle ran | 4 |
| oracle passed | 3 |
| patch apply failed | 6 |

Relabeled outcomes after validation:

| expected outcome | count |
|---|---:|
| `correct` | 3 |
| `incorrect` | 1 |
| `environment_invalid` | 6 |

Per-candidate validation:

| patch id | validation status | patch applied | oracle passed |
|---|---|---:|---:|
| `bugsinpy_httpie_1__ai_patch_01` | `patch_apply_failed` | false | false |
| `bugsinpy_httpie_1__ai_patch_02` | `validated` | true | false |
| `bugsinpy_httpie_2__ai_patch_01` | `patch_apply_failed` | false | false |
| `bugsinpy_httpie_2__ai_patch_02` | `label_mismatch` | true | true |
| `bugsinpy_httpie_3__ai_patch_01` | `label_mismatch` | true | true |
| `bugsinpy_httpie_3__ai_patch_02` | `patch_apply_failed` | false | false |
| `bugsinpy_httpie_4__ai_patch_01` | `patch_apply_failed` | false | false |
| `bugsinpy_httpie_4__ai_patch_02` | `label_mismatch` | true | true |
| `bugsinpy_httpie_5__ai_patch_01` | `patch_apply_failed` | false | false |
| `bugsinpy_httpie_5__ai_patch_02` | `patch_apply_failed` | false | false |

## Interpretation

The run proves that the project can call a generator model, store raw responses
safely, convert generated diffs into candidate records, and validate them with
retained executable oracles.

It does not yet provide a clean AI-generated patch dataset slice for verifier
experiments because 6/10 generated patches fail to apply. This is too high to
use as-is.

The next decision must be explicit:

- retry generation with a stricter diff-only prompt and possibly lower source
  context;
- keep only the 4 applicable patches as a diagnostic sample;
- switch to a coding-agent-style patch generation workflow that edits a copied
  checkout and emits a verified `git diff`.
