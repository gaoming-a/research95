# EVP-8 Realistic Agent Qwen Merge-Label Result Analysis v0.3

Date: 2026-06-30

- model: `qwen/qwen3.7-max`
- packet variant: `e6_full_with_verdict`
- evaluator source: `data/patches/evp8_realistic_agent_evaluator_manifest_v0_3.jsonl`
- corrected label set: `True`
- merge label set: `True`
- reviews: `53`
- parse valid: `53`
- run gate: `passed`
- labels: `{'correct': 30, 'visible_test_failing_wrong': 23}`
- visible-tool decisions: `{'accept': 30, 'reject': 23}`
- Qwen decisions: `{'accept': 30, 'reject': 23}`
- baseline to Qwen transitions: `{'accept->accept': 30, 'reject->reject': 23}`

Metric comparison:

- visible-tool accepted precision: `30/30` = `1.0`
- Qwen accepted precision: `30/30` = `1.0`
- visible-tool false accept rate among wrong: `0/23` = `0.0`
- Qwen false accept rate among wrong: `0/23` = `0.0`
- false accepts avoided by Qwen: `0`
- new false accepts introduced by Qwen: `0`
- correct patch accepted by Qwen: `30/30`
- correct patch rejected by Qwen: `0/30`

Interpretation:

- Qwen exactly matched the deterministic visible-tool baseline on all 53 candidates.
- It did not reduce false accepts in this evidence setting.
- The result supports a negative finding: with a visible merge-gate summary present, Qwen behaves like a policy follower rather than adding independent semantic verification value.
- Claim boundary: Merge labels require patch apply, declared visible-test pass, and hidden-oracle pass; this v0.3 analysis supersedes v0.1 false-accept and v0.2 hidden-oracle-only labels.
