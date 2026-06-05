# Model Selection Shortlist

Last updated: 2026-06-05

This document is a decision aid for Stage 3 of the AI execution plan. It does
not select the experiment model by itself and must not be treated as
`configs/model_selection.local.json`.

## Sources Checked

- LMArena leaderboard: `https://lmarena.ai/leaderboard/`
- OpenRouter model catalog API: `https://openrouter.ai/api/v1/models`

OpenRouter availability was checked through the public model catalog API on
2026-06-05. LMArena should be used as the capability-band source on the final
selection date; if the leaderboard changes, record the new date and source in
`configs/model_selection.local.json`.

Latest local catalog audit:

```text
outputs/model_selection/openrouter_catalog_audit.md
```

Current result: all six shortlist slugs are visible in the public OpenRouter
catalog.

## Selection Rule

For the first real API pilot, prefer a single concrete OpenRouter model slug:

- use one model for both `llm_only` and `evidence_first`;
- avoid `~...latest` aliases for reproducibility;
- avoid preview-only models unless there is a strong reason;
- record source date, provider, capability source, capability band, and known
  limitations;
- do not claim cross-model generality from the first single-model pilot.

## Candidate Slugs Observed on OpenRouter

The following slugs were visible in the OpenRouter catalog query. They are
candidate options only.

| priority | slug | provider | reason to consider | caveat |
|---:|---|---|---|---|
| 1 | `anthropic/claude-sonnet-4.6` | Anthropic | Strong general-purpose reviewer candidate; stable non-`latest` slug; large context. | Closed model; cost and provider routing must be recorded. |
| 2 | `openai/gpt-5.1-codex` | OpenAI | Coding-specialized model family; plausible reviewer for patch acceptance. | Coding specialization may make results less comparable with general chat models. |
| 3 | `openai/gpt-5.2` | OpenAI | Strong general-purpose candidate with explicit slug. | If using a very high-end model, paper must avoid comparing against weaker earlier runs. |
| 4 | `deepseek/deepseek-v3.2` | DeepSeek | Strong open-style family candidate; useful if cost or openness matters. | Need to verify current capability band on final selection date. |
| 5 | `qwen/qwen3-coder-next` | Qwen | Coding-oriented candidate; suitable if focusing on code-review behavior. | May bias the pilot toward coding-specialized behavior. |
| 6 | `z-ai/glm-5` | Z.ai | Alternative frontier-style non-US provider candidate. | Capability band must be documented carefully before use. |

## Recommended First Pilot Choice

For the first single-model pilot, the most conservative choice is:

```text
anthropic/claude-sonnet-4.6
```

Rationale:

- It is a concrete, non-`latest` OpenRouter slug.
- It avoids preview naming.
- It is likely strong enough that failure is less easily dismissed as purely
  weak-model behavior.
- Because the experiment compares two conditions within the same model, one
  strong model is sufficient for the first pilot claim.

This recommendation is not a command to run the API. The user must still
confirm the slug and selection rationale before creating local config.

## Local Config Command After Confirmation

After the user confirms the model, generate local model selection with:

```powershell
python scripts\create_model_selection_local.py `
  --model anthropic/claude-sonnet-4.6 `
  --provider Anthropic `
  --selection-source LMArena `
  --selection-source-url https://lmarena.ai/leaderboard/ `
  --capability-source "LMArena leaderboard checked on 2026-06-05 and OpenRouter catalog availability" `
  --capability-band "single-model-pilot/frontier-reviewer" `
  --reason "Single-model within-model comparison of llm_only versus evidence_first using a strong concrete OpenRouter-accessible reviewer." `
  --require-openrouter-catalog
```

Then generate API local config:

```powershell
python scripts\create_api_pilot_local_config.py `
  --model anthropic/claude-sonnet-4.6 `
  --out configs\api_pilot.local.json `
  --smoke-limit 2 `
  --require-openrouter-catalog
```

Both generated files are ignored local files and must not be committed.

Before generating local config, re-check the selected slug:

```powershell
python scripts\audit_openrouter_model_catalog.py `
  --model anthropic/claude-sonnet-4.6 `
  --out-json outputs\model_selection\selected_model_catalog_audit.json `
  --out-md outputs\model_selection\selected_model_catalog_audit.md
```

## Paper Wording

Acceptable:

> We selected one documented OpenRouter-accessible model for a within-model
> comparison of `llm_only` and `evidence_first`, controlling for base-model
> capability.

Not acceptable:

> The experiment proves that evidence-first verification is better across model
> families or across capability tiers.
