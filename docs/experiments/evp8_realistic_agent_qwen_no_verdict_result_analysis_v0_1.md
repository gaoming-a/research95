# EVP-8 Realistic Agent Qwen No-Verdict Result Analysis v0.1

Date: 2026-06-30

- model: `qwen/qwen3.7-max`
- packet variant: `e6_no_verdict`
- reviews: `53`
- parse valid: `53`
- run gate: `passed`
- labels: `{'correct': 1, 'test_passing_wrong': 52}`
- visible-tool decisions: `{'accept': 30, 'reject': 23}`
- Qwen decisions: `{'accept': 30, 'reject': 23}`
- baseline to Qwen transitions: `{'accept->accept': 30, 'reject->reject': 23}`

Metric comparison:

- visible-tool accepted precision: `1/30` = `0.0333`
- Qwen accepted precision: `1/30` = `0.0333`
- visible-tool false accept rate among wrong: `29/52` = `0.5577`
- Qwen false accept rate among wrong: `29/52` = `0.5577`
- false accepts avoided by Qwen: `0`
- new false accepts introduced by Qwen: `0`
- correct patch outcomes: `[{'candidate_id': 'evp8_realistic_agent_candidate_0001', 'visible_tool_decision': 'accept', 'qwen_decision': 'accept', 'qwen_primary_reason': 'The patch applies cleanly and passes the visible fail-to-pass test (test_chinese) which directly validates the UTF-8 encoding fix for non-ASCII text, with no visible contradictions in the merge-gate summary.'}]`

Interpretation:

- Qwen exactly matched the deterministic visible-tool baseline on all 53 candidates.
- It did not reduce false accepts in this evidence setting.
- The result supports a negative finding: with a visible merge-gate summary present, Qwen behaves like a policy follower rather than adding independent semantic verification value.
- Claim boundary: This run measures whether Qwen reduces visible-tool false accepts on realistic agent patches; it cannot support a strong correct-recall claim because the cohort has one correct patch.
