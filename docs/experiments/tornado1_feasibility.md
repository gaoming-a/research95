# Tornado 1 Feasibility Probe

Date: 2026-06-12

## Decision

`bugsinpy_tornado_1` is excluded from `p2p_broad_main` as
`pending_blocked_project_level_unittest_scope_timeout`.

## Scope

- Project: `tornado`
- Buggy commit: `6a5a0bfa370b6c0d3dbbf9589a560a98202d2baa`
- Fixed commit: `4677c54cc18bbfbdf0f4dadf11610fab6203fd63`
- F2P command:
  - `python -m unittest -q tornado.test.websocket_test.WebSocketTest.test_nodelay`

## F2P Result

The buggy and fixed checkouts were created successfully.

On Windows/Python 3.11, direct execution first failed before the oracle because
the default Proactor event loop does not implement `add_reader`. Using the
shared compatibility shim with `asyncio.WindowsSelectorEventLoopPolicy()` made
the local Tornado test server runnable without editing Tornado source or tests.

- Buggy checkout: `WebSocketHandler.set_nodelay` asserted on `self.stream`, and
  the test observed `None != "hello"`.
- Fixed checkout: the same test passed.

The retained F2P oracle is therefore clear under the documented Windows runtime
policy.

## Project-Level P2P Attempt

The project-level unittest P2P-broad attempt used `tornado/test` discovery with
`*_test.py`, excluded the retained F2P oracle, and used batch-first stability
runs.

The attempt reached the 40 minute execution budget before producing
`data/p2p_scopes/bugsinpy_tornado_1_p2p_broad.json`. The output directory
contained only the compatibility shim helper directory. The observed active
child test near cleanup was
`tornado.test.iostream_test.TestIOStreamSSLContext.test_future_interface`.

No residual Tornado Python process remained after cleanup.

## Boundary

This is not a label result and not a project-level P2P result. The task cannot
enter `p2p_broad_main` without a completed project-level P2P-broad manifest and
`p2p_broad_size >= 3`.

No Tornado source files, tests, or fixtures were edited. Local Tornado
socket/server tests are allowed; external network services are not. No task-file
P2P downgrade was used.
