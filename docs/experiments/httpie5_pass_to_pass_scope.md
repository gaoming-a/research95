# Httpie 5 Pass-to-Pass Scope

## Scope

Task: `bugsinpy_httpie_5`.

This report defines a pass-to-pass scope for the current local environment. It
implements the final-paper rule that P2P-broad should be the maximal stable
runnable subset, not a hand-picked related-test set and not a blind full-suite
run.

No model API calls were made.

## Collection

Output files:

```text
outputs/httpie5_p2p_scope_001/p2p_scope.json
outputs/httpie5_p2p_scope_001/p2p_scope.md
outputs/httpie5_p2p_scope_001/candidate_p2p_validation.jsonl
outputs/httpie5_p2p_scope_001/candidate_p2p_validation_summary.json
```

The script collected 17 tests from `tests/tests.py` in both buggy and
reference-fixed checkouts.

Exclusions:

| reason | count |
|---|---:|
| retained fail-to-pass oracle | 1 |
| static external dependency | 13 |

The external-dependency exclusion is based on test-method source containing
network-oriented tokens such as `httpbin`, `http://`, or `https://`. These tests
are not part of the stable local P2P subset because they require external
network resources.

## P2P-Broad

The current P2P-broad stable subset has 3 tests:

```text
tests/tests.py::TestItemParsing::test_escape
tests/tests.py::TestItemParsing::test_invalid_items
tests/tests.py::TestItemParsing::test_valid_items
```

For this task, P2P-core is the same 3-test set because the stable runnable tests
all belong to `TestItemParsing`.

## Candidate Validation With P2P

The 6 existing `httpie_5` candidates were validated with retained oracle plus
P2P-broad:

| label with P2P-broad | count |
|---|---:|
| `correct_under_f2p_and_p2p_broad` | 1 |
| `incorrect_issue_not_fixed` | 5 |

No candidate currently falls into `incorrect_regression`: the only candidate
that passes the retained oracle is the reference patch, and it also passes all
3 P2P-broad tests.

## Accounting Update

Task-level accounting now records:

```text
p2p_status = completed
label_scope_current = f2p_plus_p2p_broad
regression_scope_current = p2p_broad_stable_subset
p2p_scope_size = 3
p2p_core_size = 3
```

## Boundary

This P2P-broad scope is the maximal stable runnable subset in the current local
environment after excluding the retained fail-to-pass oracle and unavailable
external-network tests. It is stronger than the earlier retained-oracle-only
audit, but it remains environment-specific and should be regenerated for each
expanded task.
