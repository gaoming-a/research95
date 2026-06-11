# Tqdm 9 Candidate Validation

Date: 2026-06-11

## Status

`bugsinpy_tqdm_9` is admitted to the `p2p_broad_main` cohort.

This is the fifth completed project-level P2P main task after
`bugsinpy_httpie_5`, `bugsinpy_cookiecutter_1`, `bugsinpy_cookiecutter_2`,
and `bugsinpy_cookiecutter_3`.

## Scope

Task:

```text
task_id: bugsinpy_tqdm_9
project: tqdm
bug behavior: SI-scaled meter totals should round at display precision
  boundaries, and manual tqdm instances should report total length
touched file: tqdm/_tqdm.py
fail-to-pass nodeids:
  tqdm/tests/tests_tqdm.py::test_si_format
  tqdm/tests/tests_tqdm.py::test_update
```

P2P-broad scope:

```text
manifest: data/p2p_scopes/bugsinpy_tqdm_9_p2p_broad.json
collected/common nodeids: 14
excluded fail-to-pass oracle: 2
excluded failed on buggy baseline: 0
included P2P-broad tests: 12
collection error files: 0
stability runs: 3 per version
```

## Oracle

Added oracle:

```text
scripts/oracles/tqdm_9_si_len.py
```

The oracle checks both retained bug behaviors without relying on pytest:

- `format_meter(1, 9999, 1, unit_scale=True)` must display `10.0K`;
- `len(tqdm(total=2))` must return `2`.

Direct oracle check:

```text
buggy checkout: fail
fixed checkout: pass
```

## Candidates

Generated candidate slice:

```text
output: outputs/tqdm9_candidate_validation_001/candidates.jsonl
candidate_count: 7
candidate_type_counts:
  correct_reference: 1
  buggy_noop: 1
  irrelevant_patch: 1
  partial_fix: 4
```

The first generic candidate pass produced 13 candidates, but six generated
`partial_fix` records still passed the retained oracle. Those records omitted
style-only changes or threshold-line variants that did not break either target
behavior. They were filtered out before final validation rather than relabeled
silently.

Final partial negatives:

```text
first_hunk_only
missing_change_1
missing_change_4
split_replace_1_3
```

## Validation

Retained oracle validation:

```text
output: outputs/tqdm9_candidate_validation_001/oracle_validation_summary.json
record_count: 7
patch_applied_count: 7
oracle_ran_count: 7
oracle_all_passed_count: 1
validation_status_counts:
  validated: 7
```

F2P plus P2P-broad validation:

```text
output: outputs/tqdm9_candidate_validation_001/p2p_validation_summary.json
record_count: 7
p2p_broad_test_count: 12
patch_applied_count: 7
retained_oracle_passed_count: 1
label_with_p2p_broad_counts:
  correct_under_f2p_and_p2p_broad: 1
  incorrect_issue_not_fixed: 6
```

## Conclusion

`bugsinpy_tqdm_9` is a valid project-level P2P main-cohort task:

```text
project_level_p2p_status: completed
p2p_broad_main_included: true
label_scope.main: project_level_p2p_broad
```

The task adds a compact real bug with two independent retained oracle behaviors.
It also records a candidate-curation rule: generic partial diffs must be
validated against the retained oracle before being used as negative labels.
