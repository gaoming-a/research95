# PySnooper 3 Candidate Validation

Date: 2026-06-12

## Status

`bugsinpy_PySnooper_3` is admitted to the `p2p_broad_main` cohort.

This is the seventh completed project-level P2P main task after
`bugsinpy_httpie_5`, `bugsinpy_cookiecutter_1`, `bugsinpy_cookiecutter_2`,
`bugsinpy_cookiecutter_3`, `bugsinpy_tqdm_9`, and
`bugsinpy_PySnooper_1`.

## Boundary

`bugsinpy_PySnooper_2` is separately blocked because it would require a
compatibility/test-fixture shim with unclear experimental boundaries.
`bugsinpy_PySnooper_3` does not use such a shim.

Allowed setup for this task:

```text
ignored venv: outputs/envs/pysnooper3_p2p_py311
dependency source:
  requirements.txt
  test_requirements.txt
```

No source-tree compatibility shim, missing fixture copy, or test semantic
modification was introduced.

## Scope

Task:

```text
task_id: bugsinpy_PySnooper_3
project: PySnooper
bug behavior: snoop file output should append trace lines to the user-provided
  file path
touched file: pysnooper/pysnooper.py
fail-to-pass nodeid:
  tests/test_pysnooper.py::test_file_output
```

P2P-broad scope:

```text
manifest: data/p2p_scopes/bugsinpy_PySnooper_3_p2p_broad.json
collected/common nodeids: 5
excluded fail-to-pass oracle: 1
excluded failed on buggy baseline: 0
included P2P-broad tests: 4
collection error files: 0
stability runs: 3 per version
```

## Oracle

Added oracle:

```text
scripts/oracles/pysnooper_3_file_output.py
```

The oracle creates a temporary output file, decorates a small function with
`@pysnooper.snoop(str(path))`, executes it, and asserts that the trace file is
created and contains expected local-variable trace content.

Direct oracle check:

```text
buggy checkout: fail with NameError: output_path is not defined
fixed checkout: pass
```

## Candidates

Generated candidate slice:

```text
output: outputs/pysnooper3_candidate_validation_001/candidates.jsonl
candidate_count: 4
candidate_type_counts:
  correct_reference: 1
  buggy_noop: 1
  irrelevant_patch: 1
  partial_fix: 1
```

The reference patch is a single-line fix. The default generic candidate
generation produced only no-op and irrelevant negatives, so a task-specific
difficult negative was added:

```text
wrong_mode_keeps_undefined_path
```

This negative touches the relevant `open(...)` call but keeps the undefined
`output_path` variable, so it remains issue-not-fixed under the retained oracle.

## Validation

Retained oracle validation:

```text
output: outputs/pysnooper3_candidate_validation_001/oracle_validation_summary.json
record_count: 4
patch_applied_count: 4
oracle_ran_count: 4
oracle_all_passed_count: 1
validation_status_counts:
  validated: 4
```

F2P plus P2P-broad validation:

```text
output: outputs/pysnooper3_candidate_validation_001/p2p_validation_summary.json
record_count: 4
p2p_broad_test_count: 4
patch_applied_count: 4
retained_oracle_passed_count: 1
label_with_p2p_broad_counts:
  correct_under_f2p_and_p2p_broad: 1
  incorrect_issue_not_fixed: 3
```

## Conclusion

`bugsinpy_PySnooper_3` is a valid project-level P2P main-cohort task:

```text
project_level_p2p_status: completed
p2p_broad_main_included: true
label_scope.main: project_level_p2p_broad
```

The task expands the main cohort to seven completed project-level P2P tasks.
It also records a boundary distinction: declared dependency installation in an
ignored venv is acceptable when audited, while compatibility/test-fixture shims
remain disallowed for main-cohort admission at this stage.
