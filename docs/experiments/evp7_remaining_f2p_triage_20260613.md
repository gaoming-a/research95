# EVP-7 Remaining F2P-Only Triage 2026-06-13

This batch covers the remaining readiness top lanes after the first parallel
F2P-only triage. It does not admit any task into `p2p_broad_main`.

## Scope

- `bugsinpy_ansible_1`: `python -m pytest test/units/galaxy/test_collection.py::test_verify_collections_no_version`
- `bugsinpy_luigi_1`: `python -m pytest test/server_test.py::MetricsHandlerTest::test_get`
- `bugsinpy_matplotlib_1`: `python -m pytest lib/matplotlib/tests/test_bbox_tight.py::test_noop_tight_bbox`

No dependency install, checkout edit, test edit, or fixture shim was performed.

## Results

| Task | Result | Probe status |
| --- | --- | --- |
| `bugsinpy_ansible_1` | checkout completed; with `PYTHONPATH=lib`, both versions fail before target test because `fcntl` is unavailable on Windows | `f2p_blocked_windows_posix_import` |
| `bugsinpy_luigi_1` | checkout completed; existing `inspect` runtime compatibility gets past Python 3.11 `ArgSpec`, but both versions then fail because `tornado` is absent | `f2p_blocked_dependency_environment` |
| `bugsinpy_matplotlib_1` | reused existing historical probe state; buggy checkout lacks the target test file and this task already has a native-extension import blocker | `f2p_blocked_existing_incomplete_native_probe` |

## Implication

Across the eight readiness lanes, only `bugsinpy_youtube-dl_2` produced a new
clean F2P signal under the current no-install/no-edit boundary. The next
meaningful expansion decision is whether to spend a bounded project-level
P2P-broad attempt on `youtube-dl_2` despite the known `youtube-dl_1` project
discovery timeout risk.

