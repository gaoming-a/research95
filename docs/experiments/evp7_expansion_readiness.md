# EVP-7 Expansion Readiness

This report is a planning artifact. It does not admit new bugs into the main cohort.

## Current Cohort

- Main tasks: 7
- Main projects: `{"PySnooper": 2, "cookiecutter": 3, "httpie": 1, "tqdm": 1}`
- Blocked or pending registry tasks: 27

## Candidate Pool

- Source: `outputs\candidate_pool_rescreen\parallel_latest.json`
- Total BugsInPy tasks: 501
- Already registered tasks: 30
- New candidate tasks: 471
- Metadata-promising candidates: 187
- Framework counts: `{"other": 1, "pytest": 353, "unittest": 117}`
- Metadata blocker counts: `{"external_service_dependency": 5, "heavy_ml_dependency": 45, "native_build_dependency": 179, "network_reference_in_metadata": 102}`
- Fresh-project promising candidates: 0
- Controlled probe result source: `data\tasks\evp7_controlled_probe_results.json`
- Controlled probe recorded tasks: `["bugsinpy_ansible_1", "bugsinpy_fastapi_4", "bugsinpy_luigi_1", "bugsinpy_matplotlib_1", "bugsinpy_sanic_2", "bugsinpy_scrapy_2", "bugsinpy_tornado_1", "bugsinpy_youtube-dl_11", "bugsinpy_youtube-dl_2", "bugsinpy_youtube-dl_3", "bugsinpy_youtube-dl_4", "bugsinpy_youtube-dl_5", "bugsinpy_youtube-dl_6", "bugsinpy_youtube-dl_7"]`
- Controlled probe status counts: `{"f2p_blocked_dependency_environment": 4, "f2p_blocked_existing_incomplete_native_probe": 1, "f2p_blocked_windows_posix_import": 1, "f2p_established_existing_p2p_timeout": 1, "f2p_established_p2p_not_attempted": 7}`
- F2P-established P2P candidates: `["bugsinpy_youtube-dl_11", "bugsinpy_youtube-dl_2", "bugsinpy_youtube-dl_3", "bugsinpy_youtube-dl_4", "bugsinpy_youtube-dl_5", "bugsinpy_youtube-dl_6", "bugsinpy_youtube-dl_7"]`

## Probe Lanes

| Task | Project | Framework | Score | Known blocked tasks | Probe status |
| --- | --- | --- | ---: | ---: | --- |
| `bugsinpy_fastapi_4` | `fastapi` | `pytest` | 8 | 2 | `f2p_blocked_dependency_environment` |
| `bugsinpy_sanic_2` | `sanic` | `pytest` | 8 | 1 | `f2p_blocked_dependency_environment` |
| `bugsinpy_scrapy_2` | `scrapy` | `unittest` | 7 | 1 | `f2p_blocked_dependency_environment` |
| `bugsinpy_tornado_1` | `tornado` | `unittest` | 7 | 2 | `f2p_established_existing_p2p_timeout` |
| `bugsinpy_youtube-dl_2` | `youtube-dl` | `unittest` | 7 | 1 | `f2p_established_p2p_not_attempted` |
| `bugsinpy_ansible_1` | `ansible` | `pytest` | 5 | 1 | `f2p_blocked_windows_posix_import` |
| `bugsinpy_luigi_1` | `luigi` | `pytest` | 5 | 2 | `f2p_blocked_dependency_environment` |
| `bugsinpy_matplotlib_1` | `matplotlib` | `pytest` | 5 | 1 | `f2p_blocked_existing_incomplete_native_probe` |

## Decision

EVP-7 passed pilot-level G5 signal; expansion should proceed as controlled project-diverse probes, not blind BugsInPy sweeping or bulk admission. The current metadata-promising pool has no fresh-project candidates outside already-main or already-risky projects.

## Execution Boundary

- Run at most one bounded checkout/F2P/P2P probe per risky project lane at a time.
- Parallelize across independent projects only; do not run buggy and fixed checkout for the same task concurrently.
- Do not admit a task to p2p_broad_main until F2P, project-level P2P-broad, candidate construction, and candidate revalidation all pass.
- Avoid repeating known blockers unless the probe explicitly tests a new bounded policy.
