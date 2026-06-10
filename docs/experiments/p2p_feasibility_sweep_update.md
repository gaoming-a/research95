# P2P Feasibility Sweep Update

Date: 2026-06-10.

This note records the first bounded feasibility sweep after freezing Luigi as a
pending large-suite stress case.

## Inclusion Rule

The final main cohort remains:

```text
project_level_p2p_status == completed
and p2p_broad_main_included is true
```

Tasks that fail the bounded sweep are retained in task-level accounting as
`pending_blocked`; they are not silently removed.

## Current Sweep Table

| task | project | project-level P2P status | collected / nodeids | blocker | main cohort |
|---|---|---|---:|---|---|
| `bugsinpy_httpie_5` | httpie | completed | 17 / 17 | none after external-dependency exclusions | yes |
| `bugsinpy_luigi_3` | luigi | pending_blocked | 113 files / 904 nodeids | 44 collection errors; two bounded attempts timed out | no |
| `bugsinpy_luigi_4` | luigi | pending_blocked | shared Luigi project | shared large-suite blocker; project-level attempt not continued | no |
| `bugsinpy_httpie_1` | httpie | pending_blocked | 19 files / 0 nodeids | missing `pytest_httpbin` collection dependency | no |
| `bugsinpy_httpie_2` | httpie | pending_blocked | not completed | bounded project-level scope timeout | no |
| `bugsinpy_httpie_3` | httpie | pending_blocked | not completed | bounded project-level scope timeout | no |
| `bugsinpy_httpie_4` | httpie | pending_blocked | 15 files / 0 nodeids initially | legacy requests compatibility; later bounded scope timeout | no |
| `bugsinpy_tqdm_1` | tqdm | completed_insufficient_p2p_broad | 10 files / 1 nodeid | missing `nose`; P2P-broad size 1 < 3 | no |
| `bugsinpy_tqdm_2` | tqdm | completed_insufficient_p2p_broad | 6 files / 1 nodeid | missing `nose`; P2P-broad size 1 < 3 | no |
| `bugsinpy_black_1` | black | pending_blocked | unittest / 0 nodeids | missing `typed_ast`; unittest collection error | no |
| `bugsinpy_black_3` | black | pending_blocked | unittest / 0 nodeids | missing `typed_ast`; unittest collection error | no |
| `bugsinpy_cookiecutter_1` | cookiecutter | pending_blocked_after_override | 45 files / 0 nodeids | coverage addopts sanitized; then missing `poyo`, `binaryornot`, `freezegun` | no |
| `bugsinpy_cookiecutter_2` | cookiecutter | pending_blocked | not attempted | shared cookiecutter dependency blocker after addopts retry | no |
| `bugsinpy_cookiecutter_3` | cookiecutter | pending_blocked | not attempted | shared cookiecutter dependency blocker after addopts retry | no |

## Interpretation

The first replacement sweeps did not yet add new `p2p_broad_main` tasks beyond
`httpie_5`.

This is not a reason to lower the main standard. It shows that project-level
P2P-broad construction is a real feasibility constraint and must be reported
transparently.

## Next Selection Guidance

The next sweep should prioritize projects with:

- no mandatory network-service pytest fixtures;
- no bundled virtual environment inside the checkout;
- project-level collection within 5-8 minutes;
- collection errors <= 10, or errors clearly attributable to unavailable
  external dependencies;
- at least 3 P2P-broad tests over 3 stability runs.

Candidate projects from the existing screening registry should be evaluated
with this feasibility gate before any verifier API expansion.

## `tqdm` Notes

Both selected `tqdm` tasks completed bounded project-level scope construction,
but most test files failed collection because the current environment lacks the
legacy `nose` dependency. Each task retained only one stable project-level
P2P-broad test:

```text
tqdm/tests/tests_version.py::test_version
```

Because the predefined main threshold is `p2p_broad_size >= 3`, both tasks are
excluded from `p2p_broad_main`. Installing or emulating `nose` would be a
separate environment decision and was not done silently during this sweep.

## `black` Notes

The P2P scope builder now has a bounded `unittest` adapter. The adapter supports
standard-library unittest discovery and runner execution while preserving the
same project-level P2P-broad threshold.

Both selected `black` tasks were screened through the adapter:

- `bugsinpy_black_1`
- `bugsinpy_black_3`

Both tasks failed project-level unittest collection because importing
`tests/test_black.py` imports `black`, which requires the missing dependency
`typed_ast`. This dependency is present in the task requirements but was not
installed silently during the sweep.

Tracked manifests:

```text
data/p2p_scopes/bugsinpy_black_1_p2p_broad.json
data/p2p_scopes/bugsinpy_black_1_p2p_broad_collection_errors.json
data/p2p_scopes/bugsinpy_black_3_p2p_broad.json
data/p2p_scopes/bugsinpy_black_3_p2p_broad_collection_errors.json
```

The `black` tasks remain excluded from `p2p_broad_main` until the environment
dependency decision is handled explicitly and project-level P2P-broad can be
constructed with at least three stable tests.

### Isolated Dependency Attempt

After user approval, an isolated Python 3.11 virtual environment was created
under ignored `outputs/envs/` and used to try:

```text
pip install typed-ast==1.4.0
```

The installation failed because pip attempted to build the extension from source
and the machine lacks Microsoft Visual C++ 14.0+ Build Tools. The failed virtual
environment was removed.

This keeps the black tasks blocked pending an explicit environment decision:

- install system C++ build tools and retry the declared dependency;
- use an older Python interpreter compatible with available wheels;
- explicitly allow a newer `typed-ast` version and record the environment
  deviation;
- or continue with other tasks that do not require compiled legacy
  dependencies.

## `cookiecutter` Notes

After the `black` dependency blocker, `bugsinpy_cookiecutter_1` was screened as
the next non-compiled-dependency candidate. Its first project-level pytest
collection found 45 test files but collected 0 nodeids. Every file failed
collection because the retained checkout's `setup.cfg` injects:

```text
--cov-report --cov=cookiecutter
```

The current environment does not provide the pytest-cov plugin, so pytest exited
before test collection. After user confirmation, the scope builder was extended
with an audited coverage-only addopts sanitizer. For `cookiecutter_1`, it
recorded:

```text
original_addopts: -vvv --cov-report term-missing --cov=cookiecutter
removed_tokens: --cov-report, term-missing, --cov=cookiecutter
retained_tokens: -vvv
sanitized_addopts: -vvv
```

This successfully removed the coverage instrumentation blocker, but collection
still produced 0 common nodeids because it then exposed missing runtime/test
dependencies:

```text
poyo: 24 collection errors
binaryornot: 14 collection errors
freezegun: 2 collection errors
```

This produced the tracked manifests:

```text
data/p2p_scopes/bugsinpy_cookiecutter_1_p2p_broad.json
data/p2p_scopes/bugsinpy_cookiecutter_1_p2p_broad_collection_errors.json
data/p2p_scopes/bugsinpy_cookiecutter_1_p2p_broad_addopts_override_audit.json
```

`bugsinpy_cookiecutter_2` and `bugsinpy_cookiecutter_3` were not run after this
shared project-level dependency blocker was identified. They remain in the
cohort registry as `pending_blocked`, not silently removed.

The next decision is explicit: whether to build an isolated Cookiecutter
dependency environment containing its declared runtime/test dependencies. Until
that is confirmed and project-level P2P-broad succeeds, no `cookiecutter` task
enters `p2p_broad_main`.
