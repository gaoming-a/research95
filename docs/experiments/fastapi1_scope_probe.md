# FastAPI 1 Official Test-Root Scope Probe

## Summary

`bugsinpy_fastapi_1` has a clear retained fail-to-pass oracle, but it did not
produce a usable project-level P2P-broad manifest under the current bounded
pipeline.

## F2P Oracle

- Task: `bugsinpy_fastapi_1`
- Project: `fastapi`
- Oracle nodeid:
  `tests/test_jsonable_encoder.py::test_encode_model_with_default`
- Buggy checkout result: fails with
  `TypeError: jsonable_encoder() got an unexpected keyword argument
  'exclude_defaults'`
- Reference checkout result: passes

## Scope Attempts

- Full-repository project-level discovery was attempted twice and timed out
  without producing `data/p2p_scopes/bugsinpy_fastapi_1_p2p_broad.json`.
- The user approved the general official-test-root policy, not a FastAPI
  special case.
- Under that policy, FastAPI's selected official test root was `tests/`.
- The `tests/` official-root attempt also reached the 60 minute construction
  budget without producing a manifest.

## Decision

`bugsinpy_fastapi_1` is recorded as
`pending_blocked_official_test_root_timeout`.

It does not enter `p2p_broad_main`, because the official test-root scope did
not complete and no P2P-broad size or candidate revalidation evidence exists.

## Boundary

This is not a candidate-label result. No task-file-level scope was used, and no
FastAPI source or test-fixture shim was introduced.
