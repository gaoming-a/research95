# EVP-8 Realistic Hard-Negative Stress Cohort v0.1

- status: `passed`
- candidates: 31
- projects: `{'PySnooper': 9, 'cookiecutter': 17, 'scrapy': 5}`
- source kinds: `{'curated_no_api_stress_source': 5, 'model_generated_source': 26}`
- visible-tool decisions: `{'accept': 31}`
- visible-tool false accepts: 31
- visible-tool false accept rate: `1.0`
- headroom exists: `True`

Boundary: this is a hard-negative stress-test cohort, not a pure
agent-generated realistic cohort. Patch-bearing packets are written only
under ignored `outputs/**`; this tracked report stores hashes and
aggregate/case metadata only.

## Tasks

- `bugsinpy_PySnooper_3`: 9
- `bugsinpy_cookiecutter_2`: 9
- `bugsinpy_cookiecutter_3`: 8
- `bugsinpy_scrapy_1`: 5

## Checks

- api_call_not_attempted: passed (False)
- case_count_minimum_met: passed (31)
- project_minimum_met: passed (['PySnooper', 'cookiecutter', 'scrapy'])
- all_cases_are_visible_pass_hidden_fail: passed (True)
- model_visible_count_matches_evaluator: passed (31)
- baseline_count_matches_evaluator: passed (31)
- visible_tool_baseline_all_accepts: passed ({'accept': 31})
- visible_tool_false_accepts_all_cases: passed (31)
- model_visible_forbidden_fields_absent: passed ([])

## Next Step

Run verifier preflight/matrix only as hard-negative stress-test evidence.
