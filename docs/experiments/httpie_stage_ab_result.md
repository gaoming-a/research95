# Httpie Stage A/B Result

## Scope

Run id: `httpie_stage_ab_001`.

This is the first Stage A/B small closed loop from
`docs/plans/final_paper_roadmap_zh.md`. It uses the five user-confirmed
`httpie` tasks from the BugsInPy expansion screening registry:

- `bugsinpy_httpie_1`
- `bugsinpy_httpie_2`
- `bugsinpy_httpie_3`
- `bugsinpy_httpie_4`
- `bugsinpy_httpie_5`

This run does not call model APIs and does not test the final research
hypothesis. It validates whether these screened tasks can become a
patch-verification dataset slice with executable labels and prompt-boundary
checks.

## Commands

```powershell
python scripts\build_patch_verification_dataset.py `
  --run-id httpie_stage_ab_001 `
  --out-dir outputs\httpie_stage_ab_001 `
  --task-id bugsinpy_httpie_1 `
  --task-id bugsinpy_httpie_2 `
  --task-id bugsinpy_httpie_3 `
  --task-id bugsinpy_httpie_4 `
  --task-id bugsinpy_httpie_5

python scripts\validate_patch_candidates.py `
  --candidates outputs\httpie_stage_ab_001\candidates.jsonl `
  --out outputs\httpie_stage_ab_001\validation.jsonl `
  --summary-out outputs\httpie_stage_ab_001\validation_summary.json `
  --workdir-root outputs\httpie_stage_ab_001\workdirs

python scripts\run_patch_verification_api_pilot.py `
  --candidates outputs\httpie_stage_ab_001\candidates.jsonl `
  --evidence-packets outputs\httpie_stage_ab_001\evidence_packets.jsonl `
  --out-dir outputs\httpie_stage_ab_001\api_prompt_dry_run `
  --conditions llm_only evidence_first `
  --dry-run `
  --limit 0
```

## Dataset

| item | count |
|---|---:|
| tasks | 5 |
| candidates | 22 |
| correct reference | 5 |
| buggy no-op | 5 |
| irrelevant patch | 5 |
| partial fix | 7 |
| difficult negatives | 7 |
| difficult-negative ratio | 0.3182 |

Patch materialization:

| materialization | count |
|---|---:|
| buggy/fixed unified diff | 5 |
| empty diff against buggy checkout | 5 |
| local comment-only unified diff | 5 |
| first hunk of reference unified diff | 1 |
| reference diff with one change omitted | 6 |

## Validation

All 22 candidates validated.

| item | count |
|---|---:|
| patch applied | 22 |
| oracle ran | 22 |
| oracle all passed | 5 |
| validation status `validated` | 22 |

Interpretation: the five correct reference patches pass retained executable
oracles; the 17 negative candidates apply cleanly but fail retained oracle
checks as expected.

## Prompt Boundary

The dry run rendered 44 prompts:

| condition | prompts |
|---|---:|
| `llm_only` | 22 |
| `evidence_first` | 22 |

All 44 prompt-boundary checks passed. The prompt length range was 1074 to 2794
characters.

## Deterministic Baselines

| condition | accepted precision | false accept rate | correct recall | escalation rate |
|---|---:|---:|---:|---:|
| `accept_all` | 0.2273 | 1.0000 | 1.0000 | 0.0000 |
| `reject_all` | NA | 0.0000 | 0.0000 | 0.0000 |
| `oracle_upper_bound` | 1.0000 | 0.0000 | 1.0000 | 0.0000 |

Tool-only baselines:

| condition | accepted precision | false accept rate | correct recall | escalation rate |
|---|---:|---:|---:|---:|
| `tool_only_apply_only` | NA | 0.0000 | 0.0000 | 1.0000 |
| `tool_only_validation_summary` | 1.0000 | 0.0000 | 1.0000 | 0.0000 |

The `tool_only_validation_summary` result uses retained executable validation
summary and must remain separated from hidden-evaluator-free realistic
merge-gate claims.

## Conclusion

The five `httpie` screened tasks are no longer only registry entries: they now
form a validated Stage A/B dataset slice with 22 candidates, executable labels,
no-API metrics, tool-only baselines, and dry-run prompt boundary checks.

This is still preparation evidence, not model-review evidence. The next
expansion step should either repeat the same closed-loop process for another
project group or add AI-generated candidate patches under the final roadmap's
generation protocol.
