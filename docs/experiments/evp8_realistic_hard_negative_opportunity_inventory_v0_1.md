# EVP-8 Realistic Hard-Negative Opportunity Inventory v0.1

Date: 2026-06-30

This is a no-API planning audit. It records the user's broad API
authorization but does not use it, because the corrected realistic cohort
currently has no validated visible-pass/hidden-fail opportunity set.

## Boundary Checks

- api_call_not_attempted: passed (False)
- raw_model_outputs_not_read: passed (False)
- patch_text_not_written: passed (False)
- corrected_realistic_manifest_detected: passed (53)
- historical_hard_manifest_detected: passed (47)
- corrected_realistic_visible_pass_hidden_fail_absent: passed (0)
- historical_hard_calibration_opportunities_present: passed (9)
- new_verifier_api_not_ready_as_expected: passed (False)

## Corrected Realistic Cohort

- candidates: 53
- labels: `{'correct': 30, 'visible_test_failing_wrong': 23}`
- visible-tool decisions: `{'accept': 30, 'reject': 23}`
- visible-pass/hidden-fail candidates: 0
- visible-tool accepted wrong candidates: 0
- visible-tool fully separates merge labels: True

This corrected realistic cohort is externally useful for label-validity auditing, but it is not useful for measuring false-accept reduction because visible tests already separate the v0.3 merge labels.

## Historical Hard Cohort

- candidates: 47
- labels: `{'agent_plausible_wrong': 10, 'correct': 10, 'irrelevant_or_noop': 14, 'partial': 13}`
- visible-tool false accepts: 9
- false accepts by project: `{'httpie': 9}`
- false accepts by task: `{'bugsinpy_httpie_1': 4, 'bugsinpy_httpie_2': 2, 'bugsinpy_httpie_3': 2, 'bugsinpy_httpie_4': 1}`

The opportunity cases are real hard negatives, but they are historical and concentrated in httpie, so they should calibrate failure modes rather than serve as the main new realistic cohort.

Evidence-only opportunity summary:

- `deepseek/deepseek-v4-pro`: repeated accept 4, escalate 5, strict reject 0
- `qwen/qwen3.7-max`: repeated accept 7, escalate 2, strict reject 0

## Target Matrix

| target | status | next action |
| --- | --- | --- |
| `corrected_realistic_current_cohort` | `not_suitable_as_hard_negative_experiment` | Do not run more verifier API on this same evidence; use it as a label-validity audit case. |
| `historical_evp8_hard_httpie_luigi` | `usable_as_calibration_not_main_external_validity` | Use these cases to define failure modes and analysis metrics; do not count them as fresh realistic-cohort evidence. |
| `pending_or_unvalidated_realistic_sources` | `needs_validation_before_any_api` | If the pending files still exist locally, validate/relabel them under corrected project environments, then recompute visible-pass/hidden-fail counts. |
| `new_realistic_hard_negative_generation` | `recommended_next_research_step` | First write a no-API generation/validation packet that filters for visible-pass/hidden-fail after corrected oracle execution. Only then use the broad API authorization. |

## Readiness

- ready for verifier API: False
- API authorization recorded but not used: True
- block reason: No current corrected realistic visible-pass/hidden-fail cohort exists; calling verifier APIs now would mostly retest a visible-tool-separated dataset.
- next step: Build a no-API generation/validation packet for fresh realistic hard negatives, then run validation and visible-tool headroom before any verifier API.
