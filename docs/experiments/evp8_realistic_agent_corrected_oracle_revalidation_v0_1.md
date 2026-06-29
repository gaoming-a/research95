# EVP-8 Realistic Agent Corrected Oracle Revalidation v0.1

Date: 2026-06-30

This evaluator-side run revalidates hidden oracles with task-specific
Python environments after false-accept inspection found dependency
errors in the original validation tails.

- candidates: 53
- previous labels: `{'correct': 1, 'test_passing_wrong': 52}`
- corrected labels: `{'correct': 40, 'test_passing_wrong': 13}`
- label changes: 39
- dependency errors: 0
- patch applied: 53
- oracle ran: 53
- oracle passed: 40
- ready for recomputed metrics: `True`

Label changes by task:

- `bugsinpy_PySnooper_3`: 10
- `bugsinpy_cookiecutter_1`: 10
- `bugsinpy_cookiecutter_2`: 10
- `bugsinpy_cookiecutter_3`: 9
