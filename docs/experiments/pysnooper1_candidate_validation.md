# PySnooper 1 Candidate Validation

Date: 2026-06-11

## Status

`bugsinpy_PySnooper_1` is admitted to the `p2p_broad_main` cohort.

This is the sixth completed project-level P2P main task after
`bugsinpy_httpie_5`, `bugsinpy_cookiecutter_1`, `bugsinpy_cookiecutter_2`,
`bugsinpy_cookiecutter_3`, and `bugsinpy_tqdm_9`.

## Scope

Task:

```text
task_id: bugsinpy_PySnooper_1
project: PySnooper
bug behavior: snooper log files and decoded source lines should preserve
  non-ASCII text as UTF-8
touched files:
  pysnooper/tracer.py
  pysnooper/pycompat.py
fail-to-pass nodeid:
  tests/test_chinese.py::test_chinese
```

P2P-broad scope:

```text
manifest: data/p2p_scopes/bugsinpy_PySnooper_1_p2p_broad.json
collected/common nodeids: 29
excluded fail-to-pass oracle: 1
excluded failed on buggy baseline: 4
included P2P-broad tests: 24
collection error files: 0
stability runs: 3 per version
```

The scope builder first tried the full project-level batch. The batch exposed
four tests that fail on both buggy and reference checkouts under the retained
Python 3.11 environment; those tests are excluded as buggy-baseline failures
rather than treated as regressions.

## Environment Boundary

Direct F2P execution under system Python 3.11 first hit the historical
`collections.Mapping` import boundary. The P2P builder's existing
`collections.abc` compatibility shim is sufficient for this class of Python
3.11 compatibility issue.

After that shim, PySnooper required `python-toolbox`, which is declared in
`setup.py` under `extras_require['tests']`. The dependency was installed only
into the ignored isolated venv:

```text
outputs/envs/pysnooper_p2p_py311
```

Tracked audit:

```text
data/p2p_scopes/bugsinpy_PySnooper_1_dependency_environment_audit.json
```

No global dependency installation was performed.

## Oracle

Added oracle:

```text
scripts/oracles/pysnooper_1_utf8_log.py
```

The oracle creates a temporary snoop log, traces a function containing Chinese
text, reads the resulting log as UTF-8, and asserts that the non-ASCII text is
preserved.

Direct oracle check:

```text
buggy checkout: fail with UnicodeDecodeError while reading the log as UTF-8
fixed checkout: pass
```

## Candidates

Generated candidate slice:

```text
output: outputs/pysnooper1_candidate_validation_001/candidates.jsonl
candidate_count: 6
candidate_type_counts:
  correct_reference: 1
  buggy_noop: 1
  irrelevant_patch: 1
  partial_fix: 3
```

Initial generic partial generation produced a `missing_change_1` candidate that
still passed the retained oracle in the Python 3.11 environment. That candidate
kept the UTF-8 source decode and UTF-8 log write behavior while omitting only
the Python 2 compatibility hunk, so it is not a valid negative label for the
current environment. It was excluded from the PySnooper task-level partial
allowlist before final validation.

Final partial negatives:

```text
first_hunk_only
missing_change_2
missing_change_3
```

## Validation

Retained oracle validation:

```text
output: outputs/pysnooper1_candidate_validation_001/oracle_validation_summary.json
record_count: 6
patch_applied_count: 6
oracle_ran_count: 6
oracle_all_passed_count: 1
validation_status_counts:
  validated: 6
```

F2P plus P2P-broad validation:

```text
output: outputs/pysnooper1_candidate_validation_001/p2p_validation_summary.json
record_count: 6
p2p_broad_test_count: 24
patch_applied_count: 6
retained_oracle_passed_count: 1
label_with_p2p_broad_counts:
  correct_under_f2p_and_p2p_broad: 1
  incorrect_issue_not_fixed: 5
```

## Conclusion

`bugsinpy_PySnooper_1` is a valid project-level P2P main-cohort task:

```text
project_level_p2p_status: completed
p2p_broad_main_included: true
label_scope.main: project_level_p2p_broad
```

The task expands the main cohort to six completed project-level P2P tasks. It
also adds a second candidate-curation rule: partial negatives must be validated
under the retained environment, because omitting compatibility-only hunks can
leave the target Python-version behavior fully fixed.
