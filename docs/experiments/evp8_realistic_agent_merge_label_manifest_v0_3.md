# EVP-8 Realistic Agent Merge Label Manifest v0.3

Date: 2026-06-30

This evaluator-side manifest defines merge-correct labels. A candidate
is `correct` only when it applies, passes declared visible tests, and
passes the hidden oracle.

- candidates: 53
- labels: `{'correct': 30, 'visible_test_failing_wrong': 23}`
- transitions: `{'correct->correct': 30, 'correct->visible_test_failing_wrong': 10, 'test_passing_wrong->visible_test_failing_wrong': 13}`
- visible passed: 30
- oracle passed: 40
- merge correct: 30
- environment invalid: 0

Policy: correct iff patch applies, declared visible tests pass, and hidden oracle passes.
