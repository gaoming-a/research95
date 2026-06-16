# Tornado 2 Feasibility Probe

Date: 2026-06-16

## Decision

`bugsinpy_tornado_2` has a clear F2P oracle, but it is not admitted to
`p2p_broad_main`. No P2P-broad manifest exists, and the task inherits the
Tornado project-level unittest timeout risk already observed for
`bugsinpy_tornado_1` and `bugsinpy_tornado_9`.

## Scope

- Project: `tornado`
- Buggy commit: `2ca8821d006f6693f920a4b183a3a7c985a5c8ad`
- Fixed commit: `4f486a4aec746e9d66441600ee3b0743228b061c`
- F2P command:
  - `python -m unittest -q tornado.test.httpclient_test.HTTPClientCommonTestCase.test_redirect_put_without_body`
- Patch target:
  - `tornado/http1connection.py`

## Checkout

The checkout was reconstructed from the retained local Tornado Git clone using
the BugsInPy reset/copy-test-file/copy-fixed-file flow. The buggy checkout
contains only the injected fixed test file. The fixed checkout contains the
injected test file and the fixed `tornado/http1connection.py`.

Marker files were verified in both checkouts:

- `bugsinpy_bug.info`
- `bugsinpy_requirements.txt`
- `bugsinpy_run_test.sh`
- `bugsinpy_setup.sh`

## F2P Result

The test was run with the documented Windows runtime policy:
`asyncio.WindowsSelectorEventLoopPolicy()`. This is the same local-server
compatibility boundary recorded for Tornado 1 and does not edit Tornado source
or tests.

- Buggy checkout: failed with `HTTPStreamClosedError`, then
  `TimeoutError: Operation timed out after 5 seconds`.
- Fixed checkout: passed.

The retained F2P oracle is therefore clear.

## P2P Boundary

A dry-run of the project-level unittest P2P builder passed with:

- start dir: `tornado/test`
- pattern: `*_test.py`
- top-level dir: `.`
- runs: 3
- per-test timeout: 8 seconds
- batch timeout: 120 seconds
- batch size: 20
- batch-first: enabled

No real P2P construction was started in this turn. Tornado 1 and Tornado 9
already produced project-level unittest P2P timeout evidence, so a third long
Tornado sweep is not allowed without a new explicit bounded policy. No
task-file-only downgrade was used.

## Implication

`bugsinpy_tornado_2` is useful F2P evidence for the expansion audit, but it
does not satisfy the admission gate:

- F2P: established
- P2P-broad >= 3: not established
- candidate validation: not allowed
- main-cohort admission: no
