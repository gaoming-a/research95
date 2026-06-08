# Tool-Only Baseline Result

This report summarizes deterministic tool-only baselines on the current
30-candidate pilot. No model API was called.

## Inputs

- candidates: `outputs/patch_verification_pilot_001/candidates.jsonl`
- validation records: `outputs/patch_verification_pilot_001/validation.jsonl`
- output records: `outputs/tool_only_baseline/tool_only_verifier_outputs.jsonl`
- metrics: `outputs/tool_only_baseline/tool_only_metrics.json`

The output files under `outputs/` are ignored local artifacts. Reproduce them
with:

```powershell
python scripts\run_tool_only_baseline.py `
  --candidates outputs\patch_verification_pilot_001\candidates.jsonl `
  --validation outputs\patch_verification_pilot_001\validation.jsonl `
  --out outputs\tool_only_baseline\tool_only_verifier_outputs.jsonl `
  --summary-out outputs\tool_only_baseline\tool_only_summary.json
python scripts\analyze_patch_verification.py `
  --candidates outputs\patch_verification_pilot_001\candidates.jsonl `
  --verifier-outputs outputs\tool_only_baseline\tool_only_verifier_outputs.jsonl `
  --out outputs\tool_only_baseline\tool_only_metrics.json
```

## Conditions

| Condition | Evidence Used | Boundary |
| --- | --- | --- |
| `no_api_tool_only_apply_only` | patch apply status only | realistic but weak visible-tool baseline; clean application alone cannot justify accept |
| `no_api_tool_only_validation_summary` | retained executable validation summary | current-pilot tool-summary/oracle-style baseline; not a final hidden-evaluator-free realistic merge gate |

## Current Metrics

| Condition | False Accept Rate | Correct Recall | Accepted Precision | Escalation Rate | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| `tool_only_apply_only` | 0.0 | 0.0 | n/a | 1.0 | safe but unusable; applies evidence alone forces escalation |
| `tool_only_validation_summary` | 0.0 | 1.0 | 1.0 | 0.0 | perfect on the current pilot because it uses retained executable validation summary |

## Interpretation

The result supports two narrow points:

1. patch-apply evidence alone is insufficient for a usable merge gate;
2. executable validation summary can dominate binary accept/reject decisions on
   the current pilot.

It does not yet prove that LLMs add value beyond a realistic hidden-evaluator-
free tool-only baseline. That question requires visible tests and hidden
evaluator tests to be separated in the expanded dataset.
