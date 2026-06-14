# EVP-7 G5 Metric Scaffold

Date: 2026-06-14

## Purpose

This document records the no-API metric scaffold for the EVP-7 G5 gate.

G5 is the signal-existence gate: it asks whether E0/E2/E4/E6 evidence levels
change false accept rate, correct recall, escalation, or utility in an
explainable way.

The current artifact does not prove G5 for an LLM verifier. It proves that the
analysis path can consume schema-stable verifier records, join evaluator labels
only at aggregate-metric time, and compute the planned G5 metrics.

## Command

```powershell
python scripts\analyze_evp7_schema_dry_run_metrics.py --check
```

## Inputs

```text
data/reviews/evp7_merge_gate_schema_dry_run.jsonl
data/patches/evp7_candidates.jsonl
```

The dry-run review records remain label-free. Candidate labels are joined only
inside the aggregate metric calculation.

## Output

```text
data/reviews/evp7_schema_dry_run_metrics.json
```

## Current Status

- review records = 264;
- candidates = 66;
- E0/E2/E4/E6 record counts = 66 each;
- G5 metric scaffold = passed;
- G5 signal claim status = `requires_real_llm_verifier_outputs`.

## Dry-Run Metric Preview

| level | false accept rate | accepted precision | correct recall | escalation rate | Evidence Gain vs E0 |
| --- | ---: | ---: | ---: | ---: | ---: |
| E0 | 0.0 | n/a | 0.0 | 1.0 | 0.0 |
| E2 | 0.0 | n/a | 0.0 | 1.0 | 0.0 |
| E4 | 0.037736 | 0.857143 | 0.923077 | 0.0 | 17.5 |
| E6 | 0.037736 | 0.857143 | 0.923077 | 0.0 | 17.5 |

The variation above is produced by deterministic schema dry-run rules, not by
an LLM. It validates metric-path sensitivity only.

## Utility Formula

The scaffold uses a conservative merge-gate utility:

```text
accept_correct - 5*accept_wrong - 0.25*escalate - reject_correct
```

False accepts are penalized more strongly than escalation or false rejection,
matching the merge-gate risk model. These weights are a scaffold for consistent
comparison and require sensitivity analysis before paper claims.

## Boundary

This scaffold remains the no-API parser/metric path for the current
13-task/66-candidate/264-packet structural cohort. The latest G5 model-result
evidence is the separate 248-record DeepSeek run summarized in
`docs/experiments/evp7_g5_llm_full_run_result.md`.
