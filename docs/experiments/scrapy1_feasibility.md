# Scrapy 1 Feasibility Probe

Date: 2026-06-12

## Decision

`bugsinpy_scrapy_1` is excluded from `p2p_broad_main` as
`blocked_dependency_native_build`.

## Scope

- Project: `scrapy`
- Buggy commit: `c57512fa669e6f6b1b766a7639206a380f0d10ce`
- Fixed commit: `9d9dea0d69709ef0f7aef67ddba1bd7bda25d273`
- F2P commands:
  - `python -m unittest -q tests.test_spidermiddleware_offsite.TestOffsiteMiddleware4._get_spiderargs`
  - `python -m unittest -q tests.test_spidermiddleware_offsite.TestOffsiteMiddleware4.test_process_spider_output`

## Probe Result

The buggy and fixed checkouts were created successfully. The initial F2P probe
failed on both checkouts because Scrapy imports Twisted and the environment did
not have `twisted` installed.

An isolated ignored environment was created at `outputs/envs/scrapy1_p2p_py311`.
The probe then attempted a declared dependency subset needed for the target
tests, including `Twisted==20.3.0`. That install failed while building
Twisted's native `twisted.test.raiser` extension because the local environment
does not provide Microsoft Visual C++ 14.0 or greater build tools.

## Boundary

This is not a label result and not a project-level P2P result. The retained F2P
oracle cannot be established under the declared dependency set in the current
Windows/Python 3.11 environment without either installing external native build
tools or substituting dependencies.

No Scrapy source files, tests, or fixtures were edited. No Twisted version
substitution or stub was introduced. No task-file P2P downgrade was used.

## Next Step

Skip Scrapy-family candidates for the next bounded sweep and move to a
non-FastAPI, non-Sanic, non-Scrapy candidate with lower dependency risk, such as
the utility-style `youtube-dl` unittest tasks.
