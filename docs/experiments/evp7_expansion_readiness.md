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

## Probe Lanes

| Task | Project | Framework | Score | Known blocked tasks | Probe status |
| --- | --- | --- | ---: | ---: | --- |
| `bugsinpy_fastapi_4` | `fastapi` | `pytest` | 8 | 2 | `metadata_only_not_admitted` |
| `bugsinpy_sanic_2` | `sanic` | `pytest` | 8 | 1 | `metadata_only_not_admitted` |
| `bugsinpy_scrapy_2` | `scrapy` | `unittest` | 7 | 1 | `metadata_only_not_admitted` |
| `bugsinpy_tornado_1` | `tornado` | `unittest` | 7 | 2 | `metadata_only_not_admitted` |
| `bugsinpy_youtube-dl_2` | `youtube-dl` | `unittest` | 7 | 1 | `metadata_only_not_admitted` |
| `bugsinpy_ansible_1` | `ansible` | `pytest` | 5 | 1 | `metadata_only_not_admitted` |
| `bugsinpy_luigi_1` | `luigi` | `pytest` | 5 | 2 | `metadata_only_not_admitted` |
| `bugsinpy_matplotlib_1` | `matplotlib` | `pytest` | 5 | 1 | `metadata_only_not_admitted` |

## Decision

EVP-7 passed pilot-level G5 signal; expansion should proceed as controlled project-diverse probes, not blind BugsInPy sweeping or bulk admission.

## Execution Boundary

- Run at most one bounded checkout/F2P/P2P probe per risky project lane at a time.
- Parallelize across independent projects only; do not run buggy and fixed checkout for the same task concurrently.
- Do not admit a task to p2p_broad_main until F2P, project-level P2P-broad, candidate construction, and candidate revalidation all pass.
- Avoid repeating known blockers unless the probe explicitly tests a new bounded policy.
