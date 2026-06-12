# EVP-7 Parallel F2P-Only Triage 2026-06-13

This batch is a controlled expansion triage artifact. It does not admit any
task into `p2p_broad_main`.

## Scope

- `bugsinpy_scrapy_2`: `python -m unittest -q tests.test_utils_datatypes.LocalCacheTest.test_cache_without_limit`
- `bugsinpy_tornado_1`: `python -m unittest -q tornado.test.websocket_test.WebSocketTest.test_nodelay`
- `bugsinpy_youtube-dl_2`: `python -m unittest -q test.test_InfoExtractor.TestInfoExtractor.test_parse_mpd_formats`

Each task kept buggy/fixed checkout serial within the task. Independent task
lanes were run in parallel where safe. No dependency install, checkout edit,
test edit, or fixture shim was performed.

## Results

| Task | Buggy | Fixed | Probe status |
| --- | --- | --- | --- |
| `bugsinpy_scrapy_2` | import error: missing `twisted` | import error: missing `twisted` | `f2p_blocked_dependency_environment` |
| `bugsinpy_tornado_1` | fails after Windows selector event loop policy | passes after Windows selector event loop policy | `f2p_established_existing_p2p_timeout` |
| `bugsinpy_youtube-dl_2` | fails target unittest | passes target unittest | `f2p_established_p2p_not_attempted` |

## Implication

`bugsinpy_youtube-dl_2` is the only new lane in this batch with clean F2P
signal under the current no-install boundary. It still requires an explicit
project-level P2P-broad construction attempt and candidate validation before it
can be considered for main-cohort admission.

`bugsinpy_tornado_1` reconfirms earlier F2P evidence, but it retains the
existing project-level P2P-broad timeout blocker.

`bugsinpy_scrapy_2` remains blocked by the current environment because Twisted
is absent.

