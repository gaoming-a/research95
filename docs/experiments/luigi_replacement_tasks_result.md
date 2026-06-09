# Luigi Replacement Task Validation and P2P Result

## Scope

Tasks:

- `bugsinpy_luigi_3`
- `bugsinpy_luigi_4`

These tasks were selected as validation-stable replacement tasks after
`httpie_5` was classified as a hard-generation case.

No model API calls were made.

## Candidate Slices

| task | candidates | correct reference | negative/control |
|---|---:|---:|---:|
| `bugsinpy_luigi_3` | 5 | 1 | 4 |
| `bugsinpy_luigi_4` | 3 | 1 | 2 |

Retained-oracle validation was run twice for each task.

| task | run | patch applied | oracle ran | oracle passed | validated |
|---|---:|---:|---:|---:|---:|
| `bugsinpy_luigi_3` | 1 | 5/5 | 5/5 | 1/5 | 5/5 |
| `bugsinpy_luigi_3` | 2 | 5/5 | 5/5 | 1/5 | 5/5 |
| `bugsinpy_luigi_4` | 1 | 3/3 | 3/3 | 1/3 | 3/3 |
| `bugsinpy_luigi_4` | 2 | 3/3 | 3/3 | 1/3 | 3/3 |

## P2P Scope

P2P-broad was constructed within each task's relevant test file:

| task | test path | collected | excluded F2P oracle | other exclusions | P2P-broad |
|---|---|---:|---:|---:|---:|
| `bugsinpy_luigi_3` | `test/parameter_test.py` | 137 | 1 | 1 static external dependency | 135 |
| `bugsinpy_luigi_4` | `test/contrib/redshift_test.py` | 14 | 1 | 0 | 13 |

The current scope is a per-task-file stable runnable subset, not the whole
Luigi project test suite.

## Candidate Labels With P2P

| task | `correct_under_f2p_p2p` | `incorrect_issue_not_fixed` | `incorrect_regression` |
|---|---:|---:|---:|
| `bugsinpy_luigi_3` | 1 | 4 | 0 |
| `bugsinpy_luigi_4` | 1 | 2 | 0 |

## Task Accounting

Output:

```text
outputs/task_generation_accounting/luigi_replacement_task_accounting.jsonl
outputs/task_generation_accounting/luigi_replacement_task_accounting_summary.json
```

Both tasks are classified as:

```text
task_role = main_balanced_task
generation_status = not_attempted
main_experiment_included = true
p2p_status = completed
label_scope_current = f2p_plus_p2p_broad
```

## Boundary

The P2P scope for this run is intentionally limited to the task-specific test
file associated with the retained oracle. This is stronger than retained-oracle
only validation, but it is not a project-wide Luigi regression suite.

Before a final large-scale paper claim, the project should either:

- apply the same per-task-file P2P rule consistently across all BugsInPy tasks;
  or
- define a broader project-level stable test discovery process and report the
  additional exclusions and runtime costs.

## Decision

`bugsinpy_luigi_3` and `bugsinpy_luigi_4` are suitable replacement tasks for the
main experiment set. They help balance `httpie_5`, which remains a
hard-generation/stress case.
