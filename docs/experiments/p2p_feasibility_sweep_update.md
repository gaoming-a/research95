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
| `bugsinpy_cookiecutter_1` | cookiecutter | completed | 45 files / 296 nodeids | none after oracle/candidate validation | yes |
| `bugsinpy_cookiecutter_2` | cookiecutter | completed | 45 files / 286 nodeids | none after oracle/candidate validation | yes |
| `bugsinpy_cookiecutter_3` | cookiecutter | completed | 45 files / 262 nodeids | none after declared dependency installs and oracle/candidate validation | yes |

## Interpretation

The first replacement sweeps initially did not add new `p2p_broad_main` tasks
beyond `httpie_5`, but the later Cookiecutter follow-ups admitted
`cookiecutter_1`, `cookiecutter_2`, and `cookiecutter_3`.

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

This successfully removed the coverage instrumentation blocker. The immediate
retry then exposed missing runtime/test dependencies:

```text
poyo: 24 collection errors
binaryornot: 14 collection errors
freezegun: 2 collection errors
```

After user approval, an isolated Python 3.11 venv was created under ignored
`outputs/envs/cookiecutter_p2p_py311` and populated with Cookiecutter runtime
dependencies plus test dependencies needed for P2P, excluding pytest-cov because
coverage instrumentation is handled by the audited addopts sanitizer. With the
venv Python passed explicitly as both runner and test interpreter,
`bugsinpy_cookiecutter_1` completed project-level P2P-broad construction:

```text
collected/common nodeids: 296
excluded fail-to-pass oracle: 1
excluded failed on buggy baseline: 5
included P2P-broad tests: 290
stability runs: 3 per version
```

This produced the tracked manifests:

```text
data/p2p_scopes/bugsinpy_cookiecutter_1_p2p_broad.json
data/p2p_scopes/bugsinpy_cookiecutter_1_p2p_broad_collection_errors.json
data/p2p_scopes/bugsinpy_cookiecutter_1_p2p_broad_addopts_override_audit.json
data/p2p_scopes/bugsinpy_cookiecutter_1_dependency_environment_audit.json
```

`bugsinpy_cookiecutter_2` and `bugsinpy_cookiecutter_3` were initially deferred
after `cookiecutter_1` established the required environment and scope-builder
path. Later follow-ups migrated their oracles and candidate validations, so they
no longer remain `pending_blocked`.

The follow-up oracle and candidate validation have now been completed for
`bugsinpy_cookiecutter_1`. A migrated UTF-8 context oracle distinguishes the
buggy and fixed checkouts, and four candidates were validated under F2P plus
P2P-broad:

```text
correct_under_f2p_and_p2p_broad: 1
incorrect_issue_not_fixed: 3
```

The tracked follow-up report is:

```text
docs/experiments/cookiecutter1_candidate_validation.md
```

`bugsinpy_cookiecutter_1` now enters `p2p_broad_main`. This is a task-level
cohort admission, not a claim that the full final-paper dataset is complete.

### `cookiecutter_2` Follow-up

`bugsinpy_cookiecutter_2` was then migrated using the same isolated dependency
environment and audited addopts sanitizer, but with a separate project-level
P2P-broad manifest:

```text
data/p2p_scopes/bugsinpy_cookiecutter_2_p2p_broad.json
```

The retained fail-to-pass behavior is multiple hook execution:

```text
tests/test_hooks.py::TestExternalHooks::test_run_hook
```

The P2P-broad scope retained 278 stable tests after excluding the F2P oracle and
seven tests that already fail on the buggy baseline. Candidate validation
produced:

```text
correct_under_f2p_and_p2p_broad: 1
incorrect_issue_not_fixed: 10
```

The tracked follow-up report is:

```text
docs/experiments/cookiecutter2_candidate_validation.md
```

`bugsinpy_cookiecutter_2` now enters `p2p_broad_main` as the third completed
project-level main task.

### `cookiecutter_3` Follow-up

`bugsinpy_cookiecutter_3` was migrated next. Its retained metadata points to:

```text
tests/test_read_user_choice.py::test_click_invocation
```

The target behavior is that Cookiecutter's custom choice prompt already renders
the available choices, so the call to `click.prompt` must use
`show_choices=False` to avoid duplicated Click-rendered choices.

Two additional declared dependencies were needed in the isolated Cookiecutter
venv:

```text
future==0.18.3
whichcraft==0.6.1
```

After installing these declared dependencies, project-level collection errors
dropped to zero. The final P2P-broad scope retained 255 stable tests after
excluding four parameterized F2P nodeids and three tests that already fail on
the buggy baseline.

Candidate validation produced:

```text
correct_under_f2p_and_p2p_broad: 1
incorrect_issue_not_fixed: 3
```

The tracked follow-up report is:

```text
docs/experiments/cookiecutter3_candidate_validation.md
```

`bugsinpy_cookiecutter_3` now enters `p2p_broad_main` as the fourth completed
project-level main task.

### `tqdm_9` Follow-up

After the `tqdm_1` and `tqdm_2` insufficient-scope result, `bugsinpy_tqdm_9`
was selected from the retained BugsInPy workspace because its compact test file
does not trigger the earlier `nose` collection blocker.

The retained fail-to-pass behavior is:

```text
tqdm/tests/tests_tqdm.py::test_si_format
tqdm/tests/tests_tqdm.py::test_update
```

The project-level P2P-broad scope collected 14 common nodeids, excluded the two
F2P oracle nodeids, and retained 12 stable P2P tests with zero collection
errors:

```text
data/p2p_scopes/bugsinpy_tqdm_9_p2p_broad.json
```

Candidate validation produced:

```text
correct_under_f2p_and_p2p_broad: 1
incorrect_issue_not_fixed: 6
```

The tracked follow-up report is:

```text
docs/experiments/tqdm9_candidate_validation.md
```

`bugsinpy_tqdm_9` now enters `p2p_broad_main` as the fifth completed
project-level main task. Its candidate-construction audit also records that
generic partial diffs can be label-invalid when the reference patch contains
style-only changes.

### Sixth-Task Screening Boundary

After admitting `bugsinpy_tqdm_9`, the remaining retained selected candidates
were screened for a sixth project-level P2P task:

```text
bugsinpy_black_2
bugsinpy_tqdm_3
bugsinpy_tqdm_4
bugsinpy_tqdm_5
bugsinpy_tqdm_6
bugsinpy_tqdm_7
bugsinpy_tqdm_8
```

`bugsinpy_black_2` shares the same real dependency blocker as the earlier Black
tasks: importing `black` fails because `typed_ast` is absent, while the previous
isolated `typed-ast==1.4.0` install attempt on Python 3.11 required local MSVC
build tools.

For `bugsinpy_tqdm_3` through `bugsinpy_tqdm_8`, per-file pytest collection
without installing new dependencies collected only:

```text
tqdm/tests/tests_version.py::test_version
```

The behavior-relevant files still fail collection through the legacy `nose`
dependency path. These tasks are therefore recorded as `pending_blocked` rather
than silently admitted with an insufficient P2P-broad scope.

The next expansion decision is now explicit: either approve a controlled legacy
dependency environment for `nose`/Black's `typed_ast`, or bring in additional
BugsInPy projects instead of continuing to mine this exhausted retained subset.
