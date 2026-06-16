# EVP-7 Controlled Probe: sanic_2 F2P

This is a controlled expansion probe, not a main-cohort admission record.

## Scope

- Task: `bugsinpy_sanic_2`
- Project: `sanic`
- Command: `python -m pytest tests/test_app.py::test_asyncio_server_start_serving`
- Boundary: F2P feasibility, followed by one bounded Sanic official tests-root
  P2P construction attempt after the F2P gate passed.

## Initial No-Install Result

- Buggy checkout: completed.
- Fixed checkout: completed.
- Buggy target test: import failed before reaching the target test.
- Fixed target test: import failed before reaching the target test.
- Decision: `do_not_admit_environment_blocked`.

Both checkouts failed while loading `tests/conftest.py` because the current
environment lacks the Sanic runtime dependency `aiofiles`. No dependency
install, source edit, test edit, or fixture shim was performed.

## Isolated Dependency Recheck

A later explicit dependency-isolation decision authorized a fresh ignored env:
`outputs/envs/sanic2_f2p_py311`.

Key installed versions:

- `aiofiles==0.5.0`
- `websockets==8.1`
- `multidict==4.7.6`
- `httpx==0.9.3`
- `httpcore==0.3.0`
- `pytest==9.1.0`
- `pytest-sanic==1.6.2`

The run reused the already documented Python 3.11 asyncio compatibility shim
from `outputs/sanic1_f2p_probe/compat_shim/sitecustomize.py`. It did not edit
the Sanic checkout.

F2P result:

- Buggy target test: failed with
  `AttributeError: 'AsyncioServer' object has no attribute 'start_serving'`.
- Fixed target test: passed, with one resource warning.

## P2P Result

`bugsinpy_sanic_2` then attempted a bounded project-level official test root
P2P construction over `tests/`, excluding the F2P nodeid. The run exceeded the
15 minute outer budget, left no manifest, and was stopped after a residual
pytest process was observed on
`tests/test_custom_request.py::test_custom_request`.

## Implication

`bugsinpy_sanic_2` now has a clear F2P oracle, but it still cannot enter
`p2p_broad_main` because no P2P-broad manifest with at least three stable
pass-to-pass tests exists. It remains a non-main controlled-probe task unless a
future explicit P2P policy redesign succeeds without falling back to a task-file
only scope.
