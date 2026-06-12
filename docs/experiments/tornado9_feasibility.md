# Tornado 9 Feasibility Probe

Date: 2026-06-12

## Decision

`bugsinpy_tornado_9` is excluded from `p2p_broad_main` as
`pending_blocked_shared_project_level_unittest_scope_timeout`.

## Scope

- Project: `tornado`
- Buggy commit: `c9d2a3fa573987629ad576e991c2f3b65f4daab4`
- Fixed commit: `86cc31f52992fb9d11f92de6fd5496842fea2265`
- F2P command:
  - `python -m unittest -q tornado.test.httputil_test.TestUrlConcat.test_url_concat_none_params`

## F2P Result

The first parallel same-task checkout attempt showed that BugsInPy checkouts for
the buggy and fixed versions of the same task must not run concurrently. The
checkout script uses the shared `projects/<project>/bugs/<id>/` directory as
temporary storage for test and changed files. The incomplete fixed checkout was
deleted and rebuilt serially.

Under the shared compatibility shim:

- Buggy checkout: `url_concat(..., None)` raised `TypeError`.
- Fixed checkout: the same test passed.

The retained F2P oracle is therefore clear.

## Project-Level P2P Attempt

The project-level unittest P2P-broad attempt used `tornado/test` discovery with
`*_test.py`, excluded the retained F2P oracle, and used per-test dynamic
stability runs rather than batch-first execution.

The attempt did not produce `data/p2p_scopes/bugsinpy_tornado_9_p2p_broad.json`.
Only the compatibility shim helper directory was written. The observed active
tests during the run included Tornado `gen_test` cases, and no residual Python
process remained after cleanup.

## Boundary

This is not a label result and not a project-level P2P result. The task cannot
enter `p2p_broad_main` without a completed project-level P2P-broad manifest and
`p2p_broad_size >= 3`.

No Tornado source files, tests, or fixtures were edited. No task-file P2P
downgrade was used.
