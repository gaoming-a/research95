# Cookiecutter 3 Candidate Validation

Date: 2026-06-11

## Status

`bugsinpy_cookiecutter_3` is admitted to the `p2p_broad_main` cohort.

This is the fourth completed project-level P2P main task after
`bugsinpy_httpie_5`, `bugsinpy_cookiecutter_1`, and
`bugsinpy_cookiecutter_2`.

## Scope

Task:

```text
task_id: bugsinpy_cookiecutter_3
project: cookiecutter
bug behavior: Cookiecutter renders its own choice list, so click.prompt should not duplicate choices
touched file: cookiecutter/prompt.py
fail-to-pass nodeids:
  tests/test_read_user_choice.py::test_click_invocation[1-hello]
  tests/test_read_user_choice.py::test_click_invocation[2-world]
  tests/test_read_user_choice.py::test_click_invocation[3-foo]
  tests/test_read_user_choice.py::test_click_invocation[4-bar]
```

P2P-broad scope:

```text
manifest: data/p2p_scopes/bugsinpy_cookiecutter_3_p2p_broad.json
collected/common nodeids: 262
excluded fail-to-pass oracle: 4
excluded failed on buggy baseline: 3
included P2P-broad tests: 255
collection error files: 0
stability runs: 3 per version
```

The scope used the isolated Cookiecutter dependency environment with two
additional declared dependencies for this retained checkout:

```text
future==0.18.3
whichcraft==0.6.1
```

Tracked dependency audit:

```text
data/p2p_scopes/bugsinpy_cookiecutter_3_dependency_environment_audit.json
```

## Oracle

Added oracle:

```text
scripts/oracles/cookiecutter_3_prompt_show_choices.py
```

The oracle calls `read_user_choice` with mocked `click.prompt` and asserts that
the call includes `show_choices=False`. This validates the target behavior
without relying on pytest fixtures.

Direct oracle check:

```text
buggy checkout: fail
fixed checkout: pass
```

## Candidates

Generated candidate slice:

```text
output: outputs/cookiecutter3_candidate_validation_001/candidates.jsonl
candidate_count: 4
candidate_type_counts:
  correct_reference: 1
  buggy_noop: 1
  irrelevant_patch: 1
  partial_fix: 1
```

The task-specific negative changes the relevant `click.prompt` call to
`show_choices=True`. It touches the right argument but preserves the bug.

## Validation

Retained oracle validation:

```text
output: outputs/cookiecutter3_candidate_validation_001/oracle_validation_summary.json
record_count: 4
patch_applied_count: 4
oracle_ran_count: 4
oracle_all_passed_count: 1
validation_status_counts:
  validated: 4
```

F2P plus P2P-broad validation:

```text
output: outputs/cookiecutter3_candidate_validation_001/p2p_validation_summary.json
record_count: 4
p2p_broad_test_count: 255
patch_applied_count: 4
retained_oracle_passed_count: 1
label_with_p2p_broad_counts:
  correct_under_f2p_and_p2p_broad: 1
  incorrect_issue_not_fixed: 3
```

## Conclusion

`bugsinpy_cookiecutter_3` is a valid project-level P2P main-cohort task:

```text
project_level_p2p_status: completed
p2p_broad_main_included: true
label_scope.main: project_level_p2p_broad
```

The task adds another prompt/UI-behavior bug to the main cohort, but the overall
dataset remains below the 15-20 bug target for a strong interim report.
