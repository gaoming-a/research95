# thefuck_5 Feasibility Probe

Date: 2026-06-16

## Decision

`bugsinpy_thefuck_5` has a clear F2P oracle, but it is not admitted to
`p2p_broad_main`. The task failed the P2P-broad gate:

- rules-root `git push` policy produced only two pass-to-pass tests;
- broader rules-root `git` policy timed out without a manifest.

No candidate construction was allowed.

## Scope

- Project: `thefuck`
- Buggy commit: `7c858fadb3458be829d3d43666ccb46c3ed5b8a0`
- Fixed commit: `c205683a8df8a57e2db1e9816a5a7ce3255b08fc`
- F2P command:
  - `pytest tests/rules/test_git_push.py::test_match_bitbucket`
- Patch target:
  - `thefuck/rules/git_push.py`

The checkout was reconstructed from the retained local `thefuck` Git clone with
the BugsInPy reset/copy-test-file/copy-fixed-file flow. The buggy checkout
contains only the injected fixed test file. The fixed checkout contains the
injected test file and the fixed `thefuck/rules/git_push.py`.

## Environment

The task requires an older pytest boundary than `thefuck_1`. A fresh ignored
environment was created at `outputs/envs/thefuck5_f2p_py311` with:

- `pytest==3.10.1`
- `pluggy==0.13.1`
- `py==1.11.0`
- `pyte==0.8.0`
- `win-unicode-console==0.5`

`pytest==3.10.1` keeps the legacy `request.node.get_marker` API used by this
checkout's `tests/conftest.py`. On Python 3.11 it must be run with
`--assert=plain` to avoid legacy assertion-rewrite AST incompatibility.

## F2P Result

- Buggy checkout: failed with `AssertionError` because
  `match(Command('git push origin', bitbucket output))` returned true.
- Fixed checkout: passed.

The retained F2P oracle is clear.

## P2P Result

Two bounded rules-root policies were attempted:

1. `thefuck_rules_root_git_push_p2p_v1`
   - root: `tests/rules`
   - static include token: `git push`
   - result: only two P2P-broad tests after excluding the F2P oracle.

2. `thefuck_rules_root_git_p2p_v1`
   - root: `tests/rules`
   - static include token: `git`
   - result: 15 minute outer timeout without a manifest; observed active test:
     `tests/rules/test_git_merge.py::test_match`.

The generated large insufficient 2-test manifest and P2P output directories
were removed. The retained tracked record is the concise blocker summary:

```text
data/p2p_scopes/bugsinpy_thefuck_5_p2p_blocked_rules_git_policy.json
```

The ignored local checkout/env process directories were also removed after the
tracked record was written:

```text
outputs/thefuck5_p2p_workspace
outputs/envs/thefuck5_f2p_py311
```

## Implication

`bugsinpy_thefuck_5` is useful F2P evidence for the expansion audit, but it does
not satisfy the admission gate:

- F2P: established
- P2P-broad >= 3: not established
- candidate validation: not allowed
- main-cohort admission: no
