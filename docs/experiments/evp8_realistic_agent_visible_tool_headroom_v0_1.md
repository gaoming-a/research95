# EVP-8 Realistic Agent Visible-Tool Headroom v0.1

Date: 2026-06-30

This analysis compares a deterministic visible-tool baseline against
evaluator-only labels for the realistic agent-patch cohort. The baseline
itself contains no labels; labels are used only in this headroom summary.

- candidates: 53
- labels: `{'correct': 1, 'test_passing_wrong': 52}`
- decisions: `{'accept': 30, 'reject': 23}`
- decision by label: `{'correct': {'accept': 1}, 'test_passing_wrong': {'accept': 29, 'reject': 23}}`

Metrics:

- accepted precision: `1/30` = `0.0333`
- correct recall: `1/1` = `1.0`
- false accept rate among wrong: `29/52` = `0.5577`
- wrong reject rate: `23/52` = `0.4423`
- escalation rate: `0/53` = `0.0`

Interpretation:

- Visible tests alone are not a sufficient merge gate on this cohort.
- The baseline accepts many test-passing wrong patches, so there is real
  headroom for an LLM verifier to reduce false accepts.
- Correct-patch recall is undermeasured because this separated realistic
  cohort currently contains only one correct patch.
