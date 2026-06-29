# EVP-8 Realistic Agent Qwen Merge-Label Variant Comparison v0.3

Date: 2026-06-30

- candidates: 53
- corrected label set: `True`
- merge label set: `True`
- full decisions: `{'accept': 30, 'reject': 23}`
- no-verdict decisions: `{'accept': 30, 'reject': 23}`
- visible-tool decisions: `{'accept': 30, 'reject': 23}`
- full to no-verdict transitions: `{'accept->accept': 30, 'reject->reject': 23}`
- full vs no-verdict changes: `0`
- no-verdict vs visible-tool changes: `0`
- no-verdict false accepts among wrong: `0/23`

Interpretation:

- Removing the explicit merge-gate verdict did not change Qwen decisions; Qwen still follows visible test pass/fail outcomes on this cohort.
