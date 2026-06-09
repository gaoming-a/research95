# Httpie 5 Task Stability and Generation Accounting

## Scope

Task: `bugsinpy_httpie_5`.

This audit executes the roadmap decision that `httpie_5` should no longer be
treated as a required generator-success task. The goal is to decide whether it
can remain in the verification study as a hard-generation / stress case.

No model API calls were made.

## Validation Stability

A single-task dataset slice was generated:

```text
outputs/httpie5_stability_audit_001/candidates.jsonl
```

It contains 6 candidates:

| candidate type | count |
|---|---:|
| correct reference | 1 |
| buggy no-op | 1 |
| irrelevant patch | 1 |
| partial fix | 3 |

The validation was run twice:

```text
outputs/httpie5_stability_audit_001/validation_run1.jsonl
outputs/httpie5_stability_audit_001/validation_run2.jsonl
```

Both runs produced the same summary:

| metric | value |
|---|---:|
| candidates | 6 |
| patch applied | 6 |
| oracle ran | 6 |
| oracle passed | 1 |
| validated labels | 6 |

The reference patch passed the retained oracle. The no-op, irrelevant, and
partial candidates failed the retained oracle as expected.

## Generation Accounting

Task-level accounting output:

```text
outputs/task_generation_accounting/httpie5_task_accounting.jsonl
outputs/task_generation_accounting/httpie5_task_accounting_summary.json
```

Current accounting:

| field | value |
|---|---:|
| generator attempts | 7 |
| AI patches admitted | 3 |
| AI patches applicable | 1 |
| AI patches correct | 0 |
| AI patches incorrect | 1 |
| AI patches environment-invalid | 2 |

The task-level role is:

```text
task_role = hard_generation_case
generation_status = unsolved
main_experiment_included = true
```

## Interpretation

`httpie_5` is not a good main success case for patch generation. Across the
fixed attempts recorded so far, no AI-generated correct patch was admitted.

However, the task is useful for patch verification:

- the reference patch is valid;
- negative/control candidates are reproducibly rejected by the retained oracle;
- one Qwen 3.7 Plus generated patch is applicable but incorrect;
- generator failure is precisely the kind of situation where a verifier should
  reject or escalate rather than assume the patch is correct.

## Original Boundary

The current audit validates retained oracle behavior and candidate-label
stability. It does not separately run a broad pass-to-pass regression suite.
The task accounting therefore records:

```text
pass_to_pass_stable = null
pass_to_pass_stability_note = not_measured_by_current_patch_verification_oracle
```

Before claiming full production-grade task stability, the project still needs a
defined pass-to-pass check set. Until then, `httpie_5` should be described as a
validation-stable hard-generation case under the retained oracle, not as a fully
audited regression-stability task.

## P2P Follow-Up

The pass-to-pass follow-up is now tracked separately in:

```text
docs/experiments/httpie5_pass_to_pass_scope.md
```

That follow-up defines a local P2P-broad stable subset with 3 tests and updates
task accounting to:

```text
p2p_status = completed
label_scope_current = f2p_plus_p2p_broad
regression_scope_current = p2p_broad_stable_subset
```

## Decision

Keep `httpie_5` in the study as a capped hard-generation / stress case.

Recommended cap:

- 1 reference correct patch;
- 2-3 AI-generated incorrect patches when available;
- 1 constructed partial/control patch;
- no further single-task prompt tuning unless the generation protocol changes
  globally.
