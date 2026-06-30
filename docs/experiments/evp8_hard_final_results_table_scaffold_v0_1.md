# EVP-8-HARD Final Results Table Scaffold v0.1

Generated from tracked aggregate audits only. This is a table scaffold for paper writing, not a new experiment.

## Table 1. Whole-Cohort Decisions and Metrics

| system | variant | model | accept | reject | escalate | true accept | false accept | accepted precision | correct recall | false accept rate | escalation rate | claim use |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `tool_only_baseline` | `tool_only_baseline` | `deterministic` | 17 | 30 | 0 | 8 | 9 | 47.06% | 80.00% | 24.32% | 0.00% | baseline risk and opportunity-set definition |
| `deepseek/deepseek-v4-pro::with_verdict` | `with_verdict` | `deepseek/deepseek-v4-pro` | 17 | 30 | 0 | 8 | 9 | 47.06% | 80.00% | 24.32% | 0.00% | tool-verdict dominance |
| `qwen/qwen3.7-max::with_verdict` | `with_verdict` | `qwen/qwen3.7-max` | 17 | 30 | 0 | 8 | 9 | 47.06% | 80.00% | 24.32% | 0.00% | tool-verdict dominance |
| `deepseek/deepseek-v4-pro::evidence_only` | `evidence_only` | `deepseek/deepseek-v4-pro` | 6 | 30 | 11 | 2 | 4 | 33.33% | 20.00% | 10.81% | 23.40% | verdict removal ablation |
| `qwen/qwen3.7-max::evidence_only` | `evidence_only` | `qwen/qwen3.7-max` | 15 | 30 | 2 | 8 | 7 | 53.33% | 80.00% | 18.92% | 4.26% | verdict removal ablation |
| `deepseek/deepseek-v4-pro::tool_contestation` | `tool_contestation` | `deepseek/deepseek-v4-pro` | 0 | 29 | 18 | 0 | 0 | n/a | 0.00% | 0.00% | 38.30% | risk triage under explicit contestation |
| `qwen/qwen3.7-max::tool_contestation` | `tool_contestation` | `qwen/qwen3.7-max` | 1 | 30 | 16 | 0 | 1 | 0.00% | 0.00% | 2.70% | 34.04% | risk triage under explicit contestation |

## Table 2. Nine-Case Tool False-Accept Opportunity Set

| system | variant | repeated accept | escalate | strict reject | safe handled | interpretation |
|---|---|---:|---:|---:|---:|---|
| `tool_only_baseline` | `tool_only_baseline` | 9 | 0 | 0 | 0 | defines the nine-case false-accept opportunity set |
| `qwen_with_verdict` | `with_verdict` | 9 | 0 | 0 | 0 | repeats tool-only false accepts |
| `deepseek_with_verdict` | `with_verdict` | 9 | 0 | 0 | 0 | repeats tool-only false accepts |
| `qwen_evidence_only` | `evidence_only` | 7 | 2 | 0 | 2 | safe handling is escalation-driven |
| `deepseek_evidence_only` | `evidence_only` | 4 | 5 | 0 | 5 | safe handling is escalation-driven |
| `qwen_tool_contestation` | `tool_contestation` | 1 | 8 | 0 | 8 | safe handling is escalation-driven |
| `deepseek_tool_contestation` | `tool_contestation` | 0 | 9 | 0 | 9 | safe handling is escalation-driven |

## Table 3. Policy Utility Scenario Winners

| scenario | best system | best score | false accept penalty | false reject penalty | escalation cost | claim use |
|---|---|---:|---:|---:|---:|---|
| `merge_gate_strict` | `deepseek_tool_contestation` | -6.500 | 20.00 | 1.00 | 0.25 | conditional policy ranking, not correctness proof |
| `balanced_triage` | `deepseek_tool_contestation` | -6.500 | 5.00 | 1.00 | 0.25 | conditional policy ranking, not correctness proof |
| `review_cost_sensitive` | `deepseek_tool_contestation` | -20.000 | 5.00 | 1.00 | 1.00 | conditional policy ranking, not correctness proof |
| `automation_recall` | `deepseek_tool_contestation` | -13.000 | 5.00 | 2.00 | 0.50 | conditional policy ranking, not correctness proof |

## Sensitivity Winner Counts

| winner | grid cells |
|---|---:|
| `deepseek_tool_contestation` | 16 |
| `qwen_evidence_only` | 3 |
| `qwen_evidence_only + tool_only_baseline` | 1 |

## Table Notes

- Use with-verdict rows for tool-verdict dominance, not LLM-added-value claims.
- Use tool-contestation rows for risk-triage claims, not semantic correctness claims.
- Report accepted precision as n/a when accepted_total is zero.
