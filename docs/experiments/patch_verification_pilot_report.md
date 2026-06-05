# Patch Verification Pilot Report

## Status

- no-API dataset gate: passed
- candidate count: 30
- verifier baseline output count: 90
- executable validation: passed
- API readiness flag: True
- real API calls: not run

## Reproduction Command

Run the complete local no-API chain with:

```powershell
python scripts\run_no_api_patch_pipeline.py --out-dir outputs\patch_verification_pilot_repro_001
```

This command rebuilds candidates, recomputes no-API metrics, validates patch
labels with executable oracles, renders API prompts in dry-run mode, and
regenerates a pilot report without calling a model API.

## Dataset Composition

| project | count |
|---|---:|
| `httpie` | 22 |
| `luigi` | 8 |

| candidate type | count |
|---|---:|
| `buggy_noop` | 7 |
| `correct_reference` | 7 |
| `irrelevant_patch` | 7 |
| `partial_fix` | 9 |

| expected outcome | count |
|---|---:|
| `correct` | 7 |
| `incorrect` | 7 |
| `irrelevant_or_noop` | 7 |
| `partial` | 9 |

| patch materialization | count |
|---|---:|
| `buggy_fixed_unified_diff` | 7 |
| `empty_diff_against_buggy_checkout` | 7 |
| `first_hunk_of_reference_unified_diff` | 1 |
| `local_comment_only_unified_diff` | 7 |
| `reference_diff_with_one_change_omitted` | 6 |
| `reference_replace_with_one_line_reverted` | 2 |

## Validation

- records: 30
- patch applied: 30
- oracle ran: 30
- oracle all passed: 7

| validation status | count |
|---|---:|
| `validated` | 30 |

## No-API Baselines

| condition | accepted precision | false accept rate | correct recall | false reject rate | escalation rate | invalid output rate |
|---|---:|---:|---:|---:|---:|---:|
| `no_api_accept_all::accept_all` | 0.2333 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| `no_api_oracle_upper_bound::oracle_upper_bound` | 1.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| `no_api_reject_all::reject_all` | NA | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 |

## Prompt Dry-Run

- rendered prompts: 60
- conditions: {'evidence_first': 30, 'llm_only': 30}
- label-leakage checks: {'passed': 60}
- prompt char range: 1074 to 2794

## Interpretation

The current state validates dataset construction, executable labels, metrics, and prompt boundaries. It does not yet test the research hypothesis because no model reviewer decisions have been collected.

Real DeepSeek API smoke and full runs have now been executed. The full-run
result is summarized in `docs/experiments/deepseek_full_run_result.md`; the gate
verdict is `stop_or_redesign`, so the result must be treated as mixed/negative
rather than a positive evidence-first claim.
