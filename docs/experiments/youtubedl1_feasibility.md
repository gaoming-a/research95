# youtube-dl 1 Feasibility Probe

Date: 2026-06-12

## Decision

`bugsinpy_youtube-dl_1` is excluded from `p2p_broad_main` as
`pending_blocked_project_level_unittest_discovery_timeout`.

## Scope

- Project: `youtube-dl`
- Buggy commit: `99036a1298089068dcf80c0985bfcc3f8c24f281`
- Fixed commit: `1cc47c667419e0eadc0a6989256ab7b276852adf`
- F2P command:
  - `python -m unittest -q test.test_utils.TestUtil.test_match_str`

## F2P Result

The buggy and fixed checkouts were created successfully.

- Buggy checkout: `test.test_utils.TestUtil.test_match_str` failed because
  `match_str('is_live', {'is_live': False})` returned `True`.
- Fixed checkout: the same test passed.

The retained F2P oracle is therefore clear.

## Project-Level P2P Attempt

The project-level unittest P2P-broad attempt used `test/` discovery with
`test_*.py`, excluded the retained F2P oracle, and statically excluded obvious
network/external execution tokens before dynamic stability runs.

The attempt reached the 30 minute execution budget before producing
`data/p2p_scopes/bugsinpy_youtube-dl_1_p2p_broad.json`. The output directory
contained only the compatibility shim helper directory, which indicates the run
did not reach a usable manifest or test-record stage.

No residual youtube-dl Python process remained after cleanup.

## Boundary

This is not a label result and not a project-level P2P result. The task cannot
enter `p2p_broad_main` without a completed project-level P2P-broad manifest and
`p2p_broad_size >= 3`.

No youtube-dl source files, tests, or fixtures were edited. No network tests or
external services were admitted as main evidence. No task-file P2P downgrade was
used.
