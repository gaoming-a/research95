# EVP-8-HARD E6 Evidence-Only Ablation Plan v0.1

## Purpose

The Qwen and DeepSeek hard-case runs exactly reproduced the deterministic
tool-only baseline. The false-accept case analysis then showed that all nine
repeated false accepts share the same visible pattern: the candidate applies,
the visible test passes, and the hidden evaluator oracle fails.

This ablation tests the next scientific question:

> Are Qwen and DeepSeek following the verdict-like tool summary, or can they
> make a different decision from lower-level visible evidence alone?

## Boundary

- Cohort: `EVP-8-HARD`
- Candidate count: 47
- Evidence level: E6-derived packet variant
- New packet variant: `e6_evidence_only_no_verdict`
- API status: not executed
- Raw outputs generated: false
- Prompt text stored: false

Removed model-visible fields:

- `rule_based_visible_merge_gate_decision`
- `rule_based_visible_merge_gate_reasons`
- `source_decision`

Retained model-visible evidence:

- issue and patch seed
- patch surface map
- patch application and static status
- visible fail-to-pass test evidence
- visible pass-to-pass/regression evidence slots
- broader visible tool diagnostics
- visible tool summary counts and visible contradictions

This keeps the visible evidence, but removes the explicit deterministic verdict.

## Check-Only Result

Tracked summary:

- `data/protocols/evp8_hard_e6_evidence_only_check_only_v0_1.json`

Check-only status: `passed`

Key facts:

- candidate count: 47
- packet count per model: 47
- evidence levels: E6 only
- prompt boundary findings: none
- schema output errors: none
- `rule_based_visible_merge_gate_decision` present: false
- `rule_based_visible_merge_gate_reasons` present: false
- `source_decision` present: false
- API call attempted: false
- raw outputs generated: false
- prompt text stored: false

The schema dry-run produces 47 escalations because the deterministic verdict is
removed. That is expected; it is a parser/schema preview, not a model result.

## Execute Command After Explicit Authorization

This plan does not authorize API calls. If the user explicitly authorizes the
ablation, use the existing guarded runner with the evidence-only config:

```powershell
python scripts\run_evp8_hard_qwen_deepseek.py `
  --execute `
  --config configs\evp8_hard_e6_evidence_only.local.json `
  --model-id qwen/qwen3.7-max
```

and, only after the Qwen run is audited:

```powershell
python scripts\run_evp8_hard_qwen_deepseek.py `
  --execute `
  --config configs\evp8_hard_e6_evidence_only.local.json `
  --model-id deepseek/deepseek-v4-pro
```

The ignored local config should be created from
`configs/evp8_hard_e6_evidence_only.example.json`. Do not execute the tracked
example config directly.

Default evidence-only output names are separate from the previous E6-full run:

- `data/reviews/evp8_hard_e6_evidence_only_qwen_qwen3.7-max_full_summary.json`
- `data/reviews/evp8_hard_e6_evidence_only_qwen_qwen3.7-max_full_reviews.jsonl`
- `data/reviews/evp8_hard_e6_evidence_only_deepseek_deepseek-v4-pro_full_summary.json`
- `data/reviews/evp8_hard_e6_evidence_only_deepseek_deepseek-v4-pro_full_reviews.jsonl`

## Stop Gates

- Do not run API without explicit user authorization.
- Do not overwrite the existing E6-full Qwen or DeepSeek summaries.
- Do not store rendered prompts or raw model responses in tracked files.
- Do not treat check-only schema outputs as model evidence.
- If evidence-only results still match the tool baseline on the nine repeated
  false accepts, reduce the claim toward tool-summary dominance.

## Expected Analysis

The primary opportunity set is the same nine repeated false accepts from
`evp8_hard_false_accept_case_analysis_v0_1`.

Paper-relevant outcomes:

- If a model rejects or escalates these cases, it suggests verdict removal can
  change risk handling.
- If a model still accepts these cases, the failure is not only verdict-field
  imitation; the remaining evidence/prompt is still insufficient for semantic
  hidden-risk detection.
- If the model escalates broadly, report it as triage/risk control, not as
  automatic correctness verification.
