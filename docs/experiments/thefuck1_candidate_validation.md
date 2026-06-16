# thefuck_1 Candidate Validation

Date: 2026-06-16

## Scope

This record documents formal admission of `bugsinpy_thefuck_1` into the
EVP-7 main cohort under an explicit bounded policy.

The P2P-broad manifest is:

```text
data/p2p_scopes/bugsinpy_thefuck_1_p2p_broad_rules_pip_policy.json
```

This is not full-project coverage. The admitted scope is
`project_level_official_test_root` with `tests/rules` as the collection root and
`thefuck_rules_root_pip_p2p_v1` as the policy. The policy keeps only collected
test source segments containing `pip`.

## P2P Construction

Full `thefuck` project-level P2P-broad construction exceeded the bounded budget
and produced no manifest. A collection-wide `pip` static-include attempt also
failed to avoid non-target collection work because the include filter runs
after collection.

The admitted policy therefore uses:

- scope type: `project_level_official_test_root`;
- scope root: `tests/rules`;
- static include token: `pip`;
- retained fail-to-pass oracle:
  `tests/rules/test_pip_unknown_command.py::test_get_new_command[pip un+install thefuck-un+install-uninstall-pip uninstall thefuck]`;
- no model API call.

Completed P2P scope counts:

```json
{
  "collected_tests": 1431,
  "collection_error_files": 0,
  "excluded_fail_to_pass_oracle": 1,
  "excluded_static_external_dependency": 1,
  "excluded_static_include_filter": 1425,
  "included_p2p_tests": 4
}
```

The retained P2P-broad tests are:

```text
tests/rules/test_fix_alt_space.py::test_match
tests/rules/test_pip_install.py::test_get_new_command
tests/rules/test_pip_unknown_command.py::test_get_new_command[pip instatl-instatl-install-pip install]
tests/rules/test_pip_unknown_command.py::test_match
```

## Retained Oracle

Tracked oracle:

```text
scripts/oracles/thefuck_1_pip_unknown_command.py
```

The oracle runs the parameterized `pip unknown command` test in the isolated
Python 3.11 environment. It fails on the buggy checkout and passes on the fixed
checkout.

## Candidate Slice

Builder:

```text
scripts/build_thefuck1_candidates.py
```

Generated ignored candidate file:

```text
outputs/thefuck1_candidate_validation_001/candidates.jsonl
```

The admission slice contains four candidates:

| candidate type | expected validation behavior |
| --- | --- |
| `correct_reference` | retained oracle passes and P2P-broad passes |
| `buggy_noop` | retained oracle fails |
| `partial_fix` | retained oracle fails |
| `regression_patch` | retained oracle passes but P2P-broad fails |

## Validation Results

P2P-broad validation:

```json
{
  "record_count": 4,
  "patch_applied_count": 4,
  "retained_oracle_passed_count": 2,
  "p2p_broad_test_count": 4,
  "label_with_p2p_broad_counts": {
    "correct_under_f2p_and_p2p_broad": 1,
    "incorrect_issue_not_fixed": 2,
    "incorrect_regression": 1
  }
}
```

## Admission Outcome

`bugsinpy_thefuck_1` is now included in `p2p_broad_main`.

Current tracked no-API artifact counts after rebuild:

- main tasks: 21;
- projects: 6;
- promoted candidates: 98;
- correct reference candidates: 21;
- issue-not-fixed candidates: 76;
- regression candidates: 1;
- E0/E2/E4/E6 evidence packets: 392;
- G5 prompt manifest records: 392.

The previous real DeepSeek official G5 full run remains scoped to the
20-task/94-candidate/376-packet cohort. The new 21-task/392-packet cohort has
passed structural no-API gates and prompt-boundary checks, but has not been
rerun with a real LLM verifier.
