# Paper Tables: Pre-API Patch Verification

These tables are generated from current no-API outputs. They do not include real model-review results.

## Dataset By Project

| project | count |
|---|---:|
| `httpie` | 22 |
| `luigi` | 8 |

## Candidate Types

| candidate type | count |
|---|---:|
| `buggy_noop` | 7 |
| `correct_reference` | 7 |
| `irrelevant_patch` | 7 |
| `partial_fix` | 9 |

## Expected Outcomes

| expected outcome | count |
|---|---:|
| `correct` | 7 |
| `incorrect` | 7 |
| `irrelevant_or_noop` | 7 |
| `partial` | 9 |

## Patch Materialization

| materialization | count |
|---|---:|
| `buggy_fixed_unified_diff` | 7 |
| `empty_diff_against_buggy_checkout` | 7 |
| `first_hunk_of_reference_unified_diff` | 1 |
| `local_comment_only_unified_diff` | 7 |
| `reference_diff_with_one_change_omitted` | 6 |
| `reference_replace_with_one_line_reverted` | 2 |

## Executable Validation

| item | value |
|---|---:|
| records | 30 |
| patch applied | 30 |
| oracle ran | 30 |
| oracle all passed | 7 |
| all validated | True |

## No-API Baselines

| baseline | accepted precision | false accept rate | correct recall | false reject rate | escalation rate | invalid output rate |
|---|---:|---:|---:|---:|---:|---:|
| accept-all | 0.2333 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| oracle upper bound | 1.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| reject-all | NA | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 |

## Deterministic Reproducibility

| item | value |
|---|---:|
| matched | True |
| checked deterministic files | 7 |
| mismatches | 0 |
| missing | 0 |
