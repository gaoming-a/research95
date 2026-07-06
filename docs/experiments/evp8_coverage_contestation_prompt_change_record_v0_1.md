# EVP-8 coverage-contestation prompt change record v0.1

Date: 2026-07-06

## Change

Added a new frozen prompt:

- `prompts/evp8_coverage_contestation_merge_gate_v0_1.md`
- SHA-256: `722608bd0b88ec8af3c31ce06fc756e39aa4c070f57292c9eea256a66e4c422a`

No existing prompt was modified.

## Existing prompts checked

| prompt | role | SHA-256 |
| --- | --- | --- |
| `prompts/evp8_visible_evidence_merge_gate_v0_2.md` | main evidence-conditioned merge-gate prompt | `3e64dbedf9b0155f3013f30a4044631dc18d4f8d22920620941e16bd0e7d09f0` |
| `prompts/evp8_tool_contestation_merge_gate_v0_1.md` | prior EVP-8-HARD no-verdict tool-contestation prompt | `dbb09a88a3c4370d82cc257f9d44561924fcf7ba9f8cd21934adeabf2eb51bbc` |

## Contradiction and repetition audit

The new prompt is not a replacement for the main prompt. It is an independent
prompt-sensitivity / coverage-contestation condition.

No contradiction with the main prompt was introduced:

- Both prompts prohibit hidden evaluator labels, hidden tests, hidden oracle
  outcomes, reference-patch provenance, and final merge labels.
- Both prompts require decisions from the same merge-gate action space:
  `accept`, `reject`, or `escalate`.
- The main prompt remains a general safety-oriented visible-evidence merge-gate
  condition.
- The new prompt adds coverage-specific fields and asks whether a
  visible-test-only accept premise should be challenged.

Overlap with the existing tool-contestation prompt is intentional but scoped:

- Both prompts remove final deterministic verdict following.
- Both prompts report coverage concern and visible-test-only challenge fields.
- The new prompt is formalized for the current robustness route and emphasizes
  coverage sufficiency, edge-case coverage, and regression-surface coverage.
- The existing EVP-8-HARD prompt remains a historical hard-cohort condition and
  is not silently reused as the current 98-cohort ablation prompt.

## Allowed use

- Use as a new ablation condition to test whether current results are sensitive
  to prompt policy.
- Use only after check-only packet and leakage gates pass.
- Report outputs separately from the main `evp8_visible_evidence_merge_gate_v0_2`
  results.

## Forbidden use

- Do not overwrite or rename the main prompt.
- Do not merge coverage-contestation results into the main E0-E6 table without
  labeling them as a separate prompt condition.
- Do not count escalation as strict semantic correction.
- Do not run hard-negative verifier API while the hard-negative cohort remains
  below 30 visible-pass/hidden-fail cases across 3 projects.
