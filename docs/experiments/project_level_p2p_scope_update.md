# Project-level P2P Scope Update

Date: 2026-06-10.

This note records the transition from task-file P2P scopes to the final
project-level P2P-broad standard.

## Final Scope Rule

The final main experiment should use `project_level_p2p_broad` manifests.

A task-file P2P scope may be used for smoke audits or appendix analysis, but it
must not be used to claim project-level regression stability.

Candidate labels use:

```text
if patch does not apply:
    label = non_applicable
elif fail-to-pass oracle fails:
    label = incorrect_issue_not_fixed
elif P2P-broad fails:
    label = incorrect_regression
else:
    label = correct_under_f2p_and_p2p_broad
```

## Script Changes

`scripts/build_pass_to_pass_scope.py` now supports:

- `project_level_p2p_broad` and `task_file_p2p_broad` scope types;
- explicit project-level test-file discovery for legacy projects whose pytest
  defaults do not collect files such as `tests.py`;
- checkout-independent nodeid normalization across buggy and reference-fixed
  versions;
- manifest output via `--manifest-out`;
- Windows-safe batch chunking;
- optional batch grouping by test file.

`scripts/validate_candidates_with_p2p.py` now emits
`correct_under_f2p_and_p2p_broad` for candidates that pass both the retained
fail-to-pass oracle and P2P-broad.

## `bugsinpy_httpie_5`

Project-level P2P-broad construction completed.

Manifest:

```text
data/p2p_scopes/bugsinpy_httpie_5_p2p_broad.json
```

Scope summary:

| field | value |
|---|---:|
| collected tests | 17 |
| common collected tests | 17 |
| excluded fail-to-pass oracle | 1 |
| excluded external dependency | 13 |
| included P2P-broad tests | 3 |
| stability runs per version | 3 |

The project-level result matches the earlier local P2P result because the
current `httpie_5` checkout exposes only one test file under the project-level
test discovery rule.

Candidate validation summary:

| label | count |
|---|---:|
| `correct_under_f2p_and_p2p_broad` | 1 |
| `incorrect_issue_not_fixed` | 5 |

## `bugsinpy_luigi_3`

Project-level P2P-broad construction is currently blocked by runtime and
environment complexity.

Diagnostic observations:

| field | value |
|---|---:|
| discovered test files | 113 |
| collected nodeids | 904 |
| collection errors | 44 |
| first construction attempt | timed out after 15 minutes |
| second construction attempt | timed out after 20 minutes |

The collection errors are concentrated in contrib and external-service test
areas. The second construction attempt added file-grouped batch validation but
still did not complete within the local execution limit.

This means the existing Luigi task-file P2P results remain useful as smoke or
appendix evidence, but they should not be treated as final project-level P2P
labels until a separate Luigi project-level scope construction strategy is
approved.

## Decision

Luigi is frozen as a pending large-suite stress case for the current main
experiment phase.

`bugsinpy_luigi_3` and `bugsinpy_luigi_4` are not included in the
`p2p_broad_main` cohort. Their task-file P2P results are retained only as
appendix/smoke evidence.

The tracked cohort registry records this status:

```text
data/cohorts/task_cohort_registry.json
```

Main metrics must include only tasks satisfying:

```text
project_level_p2p_status == completed
and p2p_broad_main_included is true
```

For the current registry, `bugsinpy_httpie_5` is in `p2p_broad_main`; Luigi
tasks are in `blocked_or_pending` and `p2p_local_smoke`.

## Next Task Selection Rule

The next replacement tasks should be selected through a bounded P2P feasibility
sweep rather than by repeatedly debugging Luigi. Initial screening thresholds:

| criterion | threshold |
|---|---:|
| collection time | <= 5-8 minutes |
| collection errors | <= 10, or clearly attributable to unavailable external dependencies |
| P2P-broad size | >= 3 |
| stability runs | 3 |

Tasks that exceed the budget should be marked `pending_blocked` and retained in
blocked-task accounting rather than silently removed.
