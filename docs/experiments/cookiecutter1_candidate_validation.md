# Cookiecutter 1 Candidate Validation

Date: 2026-06-10

## Status

`bugsinpy_cookiecutter_1` is now admitted to the `p2p_broad_main` cohort.

This admission is narrow: it means the task has a completed project-level
P2P-broad scope and candidate labels under F2P plus P2P-broad. It does not mean
the overall dataset is large enough for the final paper.

## Scope

Task:

```text
task_id: bugsinpy_cookiecutter_1
project: cookiecutter
bug behavior: JSON context files containing non-ASCII characters should be decoded as UTF-8
source fix: cookiecutter/generate.py open(context_file) -> open(context_file, encoding='utf-8')
```

P2P-broad scope:

```text
manifest: data/p2p_scopes/bugsinpy_cookiecutter_1_p2p_broad.json
collected/common nodeids: 296
excluded fail-to-pass oracle: 1
excluded failed on buggy baseline: 5
included P2P-broad tests: 290
stability runs: 3 per version
```

The P2P construction used the tracked isolated dependency environment audit:

```text
data/p2p_scopes/bugsinpy_cookiecutter_1_dependency_environment_audit.json
```

It also used the audited coverage-only pytest addopts sanitizer:

```text
data/p2p_scopes/bugsinpy_cookiecutter_1_p2p_broad_addopts_override_audit.json
original_addopts: -vvv --cov-report term-missing --cov=cookiecutter
sanitized_addopts: -vvv
```

## Oracle

Added oracle:

```text
scripts/oracles/cookiecutter_1_utf8_context.py
```

The oracle creates a temporary UTF-8 JSON context file containing non-ASCII
characters and calls `cookiecutter.generate.generate_context`. It asserts that
the decoded context preserves the exact Unicode string.

Direct oracle check:

```text
buggy checkout: fail
fixed checkout: pass
```

The oracle intentionally does not depend on the original test fixture
`tests/test-generate-context/non_ascii.json`, because that fixture is absent in
the retained buggy checkout and present in the fixed checkout. The oracle tests
the behavior directly instead of mixing source behavior with fixture presence.

## Candidates

Generated candidate slice:

```text
output: outputs/cookiecutter1_candidate_validation_001/candidates.jsonl
candidate_count: 4
candidate_type_counts:
  correct_reference: 1
  buggy_noop: 1
  irrelevant_patch: 1
  partial_fix: 1
```

Candidate materialization:

```text
buggy_fixed_unified_diff: 1
empty_diff_against_buggy_checkout: 1
local_comment_only_unified_diff: 1
task_specific_wrong_encoding_diff: 1
```

The task-specific wrong-encoding negative changes the buggy open call to use
`encoding='ascii'`. This is a behavior-relevant negative for this single-line
UTF-8 bug, not a generic multi-hunk partial fix.

## Validation

Retained oracle validation:

```text
output: outputs/cookiecutter1_candidate_validation_001/oracle_validation_summary.json
record_count: 4
patch_applied_count: 4
oracle_ran_count: 4
oracle_all_passed_count: 1
validation_status_counts:
  validated: 4
```

F2P plus P2P-broad validation:

```text
output: outputs/cookiecutter1_candidate_validation_001/p2p_validation_summary.json
record_count: 4
p2p_broad_test_count: 290
patch_applied_count: 4
retained_oracle_passed_count: 1
label_with_p2p_broad_counts:
  correct_under_f2p_and_p2p_broad: 1
  incorrect_issue_not_fixed: 3
```

## Execution Notes

Two implementation details were required for reproducible validation on this
Windows environment:

1. The retained Cookiecutter checkout contains `docs/*.md` reparse
   point/junction entries. Candidate validation now skips symlink/reparse-point
   entries when copying a checkout, because those documentation links are not
   semantic inputs to this oracle, patch, or P2P scope.
2. Candidate-level P2P validation must reuse the scope manifest's audited
   `pytest_addopts_override.sanitized_addopts`. Without this, pytest reads
   `setup.cfg` coverage options and fails in the isolated venv where
   `pytest-cov` is intentionally absent.

## Conclusion

`bugsinpy_cookiecutter_1` is a valid project-level P2P main-cohort task under
the current evidence rules:

```text
project_level_p2p_status: completed
p2p_broad_main_included: true
label_scope.main: project_level_p2p_broad
```

The task strengthens the main cohort by adding a second completed
project-level P2P task after `bugsinpy_httpie_5`. The overall research still
needs more completed tasks before final-paper claims can be made.
