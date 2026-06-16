# EVP-7 Expansion Readiness

This report is a planning artifact and registry summary. Main-cohort admission is controlled by `data/cohorts/task_cohort_registry.json`; this report does not admit tasks by itself.

## Current Cohort

- Main tasks: 21
- Main candidates from registry: 98
- Main projects: `{"PySnooper": 2, "cookiecutter": 3, "httpie": 1, "thefuck": 1, "tqdm": 1, "youtube-dl": 13}`
- Blocked or pending registry tasks: 27

## Candidate Pool

- Source: `outputs\candidate_pool_rescreen\parallel_latest.json`
- Total BugsInPy tasks: 501
- Already registered tasks: 47
- New candidate tasks: 454
- Metadata-promising candidates: 202
- Framework counts: `{"other": 1, "pytest": 351, "unittest": 102}`
- Metadata blocker counts: `{"external_service_dependency": 5, "heavy_ml_dependency": 45, "native_build_dependency": 179}`
- Fresh-project promising candidates: 0
- Controlled probe result source: `data\tasks\evp7_controlled_probe_results.json`
- Controlled probe recorded tasks: `["bugsinpy_ansible_1", "bugsinpy_fastapi_4", "bugsinpy_luigi_1", "bugsinpy_matplotlib_1", "bugsinpy_sanic_2", "bugsinpy_scrapy_2", "bugsinpy_thefuck_1", "bugsinpy_tornado_1", "bugsinpy_tornado_2", "bugsinpy_youtube-dl_10", "bugsinpy_youtube-dl_11", "bugsinpy_youtube-dl_13", "bugsinpy_youtube-dl_16", "bugsinpy_youtube-dl_17", "bugsinpy_youtube-dl_2", "bugsinpy_youtube-dl_20", "bugsinpy_youtube-dl_21", "bugsinpy_youtube-dl_23", "bugsinpy_youtube-dl_3", "bugsinpy_youtube-dl_37", "bugsinpy_youtube-dl_4", "bugsinpy_youtube-dl_43", "bugsinpy_youtube-dl_5", "bugsinpy_youtube-dl_6", "bugsinpy_youtube-dl_7"]`
- Controlled probe status counts: `{"admitted_p2p_broad_main": 14, "f2p_blocked_checkout_timeout": 1, "f2p_blocked_dependency_environment": 3, "f2p_blocked_existing_incomplete_native_probe": 1, "f2p_blocked_windows_posix_import": 1, "f2p_established_corrected_policy_p2p_timeout": 2, "f2p_established_existing_p2p_timeout": 1, "f2p_established_official_root_p2p_timeout": 1, "f2p_established_shared_tornado_p2p_timeout_risk": 1}`
- F2P-established P2P candidates: `[]`

## Probe Lanes

| Task | Project | Framework | Score | Known blocked tasks | Probe status |
| --- | --- | --- | ---: | ---: | --- |
| `bugsinpy_fastapi_4` | `fastapi` | `pytest` | 8 | 2 | `f2p_blocked_dependency_environment` |
| `bugsinpy_sanic_2` | `sanic` | `pytest` | 8 | 1 | `f2p_established_official_root_p2p_timeout` |
| `bugsinpy_thefuck_1` | `thefuck` | `pytest` | 8 | 0 | `admitted_p2p_broad_main` |
| `bugsinpy_scrapy_2` | `scrapy` | `unittest` | 7 | 1 | `f2p_blocked_dependency_environment` |
| `bugsinpy_tornado_2` | `tornado` | `unittest` | 7 | 2 | `f2p_established_shared_tornado_p2p_timeout_risk` |
| `bugsinpy_youtube-dl_3` | `youtube-dl` | `unittest` | 7 | 1 | `f2p_established_corrected_policy_p2p_timeout` |
| `bugsinpy_ansible_1` | `ansible` | `pytest` | 5 | 1 | `f2p_blocked_windows_posix_import` |
| `bugsinpy_luigi_1` | `luigi` | `pytest` | 5 | 2 | `f2p_blocked_dependency_environment` |

## Decision

EVP-7 passed pilot-level G5 signal; expansion should proceed as controlled project-diverse probes, not blind BugsInPy sweeping or bulk admission. The current metadata-promising pool has no fresh-project candidates outside already-main or already-risky projects.

## Execution Boundary

- Run at most one bounded checkout/F2P/P2P probe per risky project lane at a time.
- Parallelize across independent projects only; do not run buggy and fixed checkout for the same task concurrently.
- Do not admit a task to p2p_broad_main until F2P, project-level P2P-broad, candidate construction, and candidate revalidation all pass.
- Avoid repeating known blockers unless the probe explicitly tests a new bounded policy.
