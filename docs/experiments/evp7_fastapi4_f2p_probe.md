# EVP-7 Controlled Probe: fastapi_4 F2P

This is a controlled expansion probe, not a main-cohort admission record.

## Scope

- Task: `bugsinpy_fastapi_4`
- Project: `fastapi`
- Command: `python -m pytest tests/test_param_in_path_and_dependency.py::test_reused_param`
- Boundary: F2P feasibility only; no project-level P2P-broad construction.

## Result

- Buggy checkout: completed.
- Fixed checkout: completed.
- Buggy target test: collection failed before reaching the target assertion.
- Fixed target test: collection failed before reaching the target assertion.
- Decision: `do_not_admit_environment_blocked`.

Both checkouts failed with the same current-environment import error:
`pydantic.errors.PydanticUserError` from the legacy FastAPI OpenAPI model code
under the current Pydantic v2 installation. No dependency install, source edit,
test edit, or fixture shim was performed.

## Implication

`bugsinpy_fastapi_4` remains useful as a dependency-environment diagnostic, but
it cannot enter `p2p_broad_main` unless a later explicit dependency isolation
decision establishes F2P and then project-level P2P-broad evidence.

