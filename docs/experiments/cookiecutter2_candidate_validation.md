# Cookiecutter 2 Candidate Validation

Date: 2026-06-10

## Status

`bugsinpy_cookiecutter_2` is admitted to the `p2p_broad_main` cohort.

This is the third completed project-level P2P main task after
`bugsinpy_httpie_5` and `bugsinpy_cookiecutter_1`.

## Scope

Task:

```text
task_id: bugsinpy_cookiecutter_2
project: cookiecutter
bug behavior: all matching pre- or post-generation hook scripts should be executed
touched file: cookiecutter/hooks.py
fail-to-pass nodeid: tests/test_hooks.py::TestExternalHooks::test_run_hook
```

P2P-broad scope:

```text
manifest: data/p2p_scopes/bugsinpy_cookiecutter_2_p2p_broad.json
collected/common nodeids: 286
excluded fail-to-pass oracle: 1
excluded failed on buggy baseline: 7
included P2P-broad tests: 278
stability runs: 3 per version
```

The scope used the same isolated Cookiecutter dependency environment as
`cookiecutter_1` and the tracked coverage-only pytest addopts sanitizer:

```text
data/p2p_scopes/bugsinpy_cookiecutter_2_p2p_broad_addopts_override_audit.json
sanitized_addopts: -vvv
```

## Oracle

Added oracle:

```text
scripts/oracles/cookiecutter_2_multiple_hooks.py
```

The oracle creates a temporary template repository with two matching
`pre_gen_project` hooks. It calls `cookiecutter.hooks.run_hook` and asserts that
both marker files are created.

Direct oracle check:

```text
buggy checkout: fail
fixed checkout: pass
```

The original `TestFindHooks::test_find_hook` node was not used as the retained
oracle because the retained checkout already contains `tests/test-hooks`, which
causes fixture setup errors unrelated to the target bug. The retained oracle
therefore validates the multiple-hook behavior directly.

## Candidates

Generated candidate slice:

```text
output: outputs/cookiecutter2_candidate_validation_001/candidates.jsonl
candidate_count: 11
candidate_type_counts:
  correct_reference: 1
  buggy_noop: 1
  irrelevant_patch: 1
  partial_fix: 8
```

Candidate materialization:

```text
buggy_fixed_unified_diff: 1
empty_diff_against_buggy_checkout: 1
local_comment_only_unified_diff: 1
first_hunk_of_reference_unified_diff: 1
reference_diff_with_one_change_omitted: 5
reference_replace_with_one_line_reverted: 2
```

## Validation

Retained oracle validation:

```text
output: outputs/cookiecutter2_candidate_validation_001/oracle_validation_summary.json
record_count: 11
patch_applied_count: 11
oracle_ran_count: 11
oracle_all_passed_count: 1
validation_status_counts:
  validated: 11
```

F2P plus P2P-broad validation:

```text
output: outputs/cookiecutter2_candidate_validation_001/p2p_validation_summary.json
record_count: 11
p2p_broad_test_count: 278
patch_applied_count: 11
retained_oracle_passed_count: 1
label_with_p2p_broad_counts:
  correct_under_f2p_and_p2p_broad: 1
  incorrect_issue_not_fixed: 10
```

## Conclusion

`bugsinpy_cookiecutter_2` is a valid project-level P2P main-cohort task:

```text
project_level_p2p_status: completed
p2p_broad_main_included: true
label_scope.main: project_level_p2p_broad
```

The task improves candidate balance because it contributes eight constructed
partial fixes in addition to reference, no-op, and irrelevant controls.
