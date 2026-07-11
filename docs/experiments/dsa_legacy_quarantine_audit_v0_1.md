# DSA 2026 旧证据隔离审计 v0.1

日期：2026-07-11
状态：PASSED / SUPERSEDING_AUDIT

## 1. 结论

旧实验只能作为 provenance、失败复盘和新任务排除依据，不能进入 DSA 的效果量、
图表、claim map 或正文数字。本审计取代 2026-07-03 的 bounded-claim validity audit。

## 2. 机械复现

- E6-no-verdict 合成等结构 packet：98 个。
- 顶层已删除 verdict 字段残留：0。
- 嵌套 `visible_tests_rule_decision` 残留：98 / 98。
- 两个旧 full config 均重建 686 个结构等价 packet，并再次出现 `not_run`、
  `not_separately_materialized`、`not_recorded` 和空 P2P evidence。
- 复现只使用空 patch/test 合成输入；未读取 prompt、patch 正文、raw response、API key，
  且没有 API 调用。

## 3. 排除注册表

冻结旧任务 28 个、旧项目 8 个。
该集合只供 P2 做 source/task disjointness 排除，不是候选池。机器记录见
`data/protocols/dsa_legacy_task_exclusion_registry_v0_1.json`。

## 4. Gate

- `nested_verdict_failure_reproduced`: PASS
- `legacy_evidence_incompleteness_reproduced`: PASS
- `retired_prompts_absent_and_hashes_recorded`: PASS
- `task_project_registry_frozen`: PASS
- `dsa_namespace_guard_passed`: PASS

P1 只有在全部检查 PASS 时完成。新增或修改任何 `scripts/dsa2026_*.py` 后必须重跑
`python scripts/audit_dsa_legacy_quarantine.py --check`。
