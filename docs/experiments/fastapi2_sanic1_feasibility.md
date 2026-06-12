# FastAPI 2 and Sanic 1 Feasibility Probe

## FastAPI 2

`bugsinpy_fastapi_2` checks out successfully and has a clear retained F2P
oracle:

- Buggy:
  `tests/test_ws_router.py::test_router_ws_depends_with_override` fails because
  the websocket receives `Socket Dependency` instead of `Override`.
- Fixed: the same test passes.

The task was not advanced to project-level P2P-broad construction. It shares
the same FastAPI official test root as `bugsinpy_fastapi_1`, whose full-repo
and official-root `tests/` P2P construction timed out without producing a
manifest. `bugsinpy_fastapi_2` is therefore retained as a clear-F2P but
shared-scope-risk case and does not enter `p2p_broad_main`.

## Sanic 1

`bugsinpy_sanic_1` checks out successfully and has a clear retained F2P oracle
after a Python 3.11 compatibility shim:

- Buggy:
  `tests/test_blueprints.py::test_bp_middleware_order` fails because response
  middleware executes as `[1, 2, 3, 6, 5, 4]` instead of
  `[1, 2, 3, 4, 5, 6]`.
- Fixed: the same test passes.

The Sanic isolated environment is under ignored `outputs/envs/sanic1_p2p_py311`.
It uses a minimal declared dependency subset and records the Python 3.11
compatibility boundary in
`data/p2p_scopes/bugsinpy_sanic_1_dependency_environment_audit.json`.

Project-level P2P-broad construction was attempted once and reached the 60
minute budget without producing `data/p2p_scopes/bugsinpy_sanic_1_p2p_broad.json`.
The task is recorded as `pending_blocked_project_level_scope_timeout` and does
not enter `p2p_broad_main`.
