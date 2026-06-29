# EVP-8 Realistic Agent Qwen No-Verdict Corrected-Label Result Analysis v0.2

Date: 2026-06-30

- model: `qwen/qwen3.7-max`
- packet variant: `e6_no_verdict`
- evaluator source: `data/patches/evp8_realistic_agent_evaluator_manifest_v0_2.jsonl`
- corrected label set: `True`
- reviews: `53`
- parse valid: `53`
- run gate: `passed`
- labels: `{'correct': 40, 'test_passing_wrong': 13}`
- visible-tool decisions: `{'accept': 30, 'reject': 23}`
- Qwen decisions: `{'accept': 30, 'reject': 23}`
- baseline to Qwen transitions: `{'accept->accept': 30, 'reject->reject': 23}`

Metric comparison:

- visible-tool accepted precision: `30/30` = `1.0`
- Qwen accepted precision: `30/30` = `1.0`
- visible-tool false accept rate among wrong: `0/13` = `0.0`
- Qwen false accept rate among wrong: `0/13` = `0.0`
- false accepts avoided by Qwen: `0`
- new false accepts introduced by Qwen: `0`
- correct patch accepted by Qwen: `30/40`
- correct patch rejected by Qwen: `10/40`

Interpretation:

- Qwen exactly matched the deterministic visible-tool baseline on all 53 candidates.
- It did not reduce false accepts in this evidence setting.
- The result supports a negative finding: with a visible merge-gate summary present, Qwen behaves like a policy follower rather than adding independent semantic verification value.
- Claim boundary: Corrected oracle revalidation changed the cohort to 40 correct and 13 test-passing-wrong candidates; this analysis supersedes the original v0.1 label-conditioned false-accept claim.
