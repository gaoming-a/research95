# Model Selection Protocol

The first API pilot is a within-model condition comparison:

- `llm_only`
- `evidence_first`

The model choice must therefore be documented, but the first claim should not
depend on cross-model ranking. If the study later expands to multiple models,
the selected models must be from a documented, similar capability band.

Before creating the ignored local selection file, consult:

```text
docs/experiments/model_selection_shortlist.md
```

The shortlist is only a decision aid. The user must still confirm the concrete
OpenRouter slug and rationale before `configs/model_selection.local.json` is
created.

## Required Record

Create an untracked real selection file from:

```powershell
configs\model_selection.example.json
```

Prefer generating it with:

```powershell
python scripts\create_model_selection_local.py `
  --model <concrete-openrouter-model-slug> `
  --provider <provider> `
  --selection-source <source-name> `
  --selection-source-url <source-url> `
  --capability-source <ranking-or-catalog-name> `
  --capability-band <single-model-pilot-or-near-peer-band> `
  --reason <selection-rationale> `
  --require-openrouter-catalog
```

`--require-openrouter-catalog` checks the public OpenRouter catalog before
writing. If the network is unavailable, run `scripts/audit_openrouter_model_catalog.py`
manually when connectivity returns and do not execute the API pilot until the
slug is verified.

The real file should be named:

```text
configs/model_selection.local.json
```

It must record:

- selection date;
- source name and URL;
- concrete OpenRouter slug;
- provider;
- capability score or capability band;
- reason for selection;
- known limitations.

## Validation

Template validation:

```powershell
python scripts\validate_model_selection.py `
  --selection configs\model_selection.example.json `
  --allow-placeholders
```

Real validation:

```powershell
python scripts\validate_model_selection.py `
  --selection configs\model_selection.local.json `
  --api-config configs\api_pilot.local.json `
  --out outputs\model_selection\latest.json
```

The real validation must pass before a real API smoke run. If the API config is
provided, the selected `primary_pilot_model.openrouter_slug` must match
`configs/api_pilot.local.json`.

## Paper Boundary

For a single-model pilot, the paper may say:

> We used one documented OpenRouter-accessible model to compare review
> conditions within the same model, controlling for base model capability.

It must not say:

> The selected model set proves model-family-level or capability-rank-level
> generality.
