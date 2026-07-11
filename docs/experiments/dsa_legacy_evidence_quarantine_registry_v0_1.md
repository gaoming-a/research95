# DSA 2026 旧证据隔离注册表 v0.1

日期：2026-07-11
状态：ACTIVE / PROVENANCE_ONLY

## 1. 目的

本注册表把既有实验完整保留为研究来历，但禁止其进入 DSA 2026 的候选选择、效果量、
图表、claim map 或正文数字。隔离是数据用途限制，不是删除原始证据，也不把失败结果
改写成新结果。

机器可读规则见 `data/protocols/dsa_legacy_analysis_denylist_v0_1.json`；机械复核由
`scripts/audit_dsa_legacy_quarantine.py` 完成。

## 2. 隔离族

| 旧证据族 | 允许用途 | DSA 中禁止用途 | 原因 |
|---|---|---|---|
| current-98、repaired v0.1--v0.3、five-model | provenance、失败复盘 | 主分析、模型选择、正文数字 | 同一旧候选与分析链反复复用 |
| E0--E6、E6 rule-only、E6-no-verdict | 泄漏与证据物化审计 | evidence ladder 效果估计 | no-verdict 仍含嵌套 rule decision，且多个层级字段未实际物化 |
| coverage-contestation、tool-contestation、evidence-only | 方法失败分类 | 正向结论或补强 prompt-only 结论 | tool-augmented verifier 与 prompt-only 条件不是同一干预 |
| EVP-8-HARD、stress-31 | 旧任务排除、provenance | DSA 候选或压力测试结果 | cohort/task reuse 会破坏新评估独立性 |
| realistic-agent/source acquisition | 旧任务排除、来源追溯 | DSA source selection 或效果估计 | 来源链已参与旧设计选择 |
| APSEC claim maps、tables、manuscript generators | 历史写作追溯 | DSA claim map、表格、正文生成 | 可能把旧 paper-facing metrics 重新带入新稿 |

## 3. 强制边界

1. 新 DSA 分析和写作生成器必须使用 `scripts/dsa2026_*.py` 命名空间。
2. 该命名空间不得读取 denylist 中的旧输入 glob、导入旧 manuscript generator，或
   出现已冻结的旧 cohort 标识。
3. P1 审计器是唯一例外：它只能读取列明的 metadata/config/runner，以复现失效机制、
   形成 task/project 排除表；不得读取 raw API outputs、API key、prompt 正文或 patch 正文。
4. 旧任务与旧项目并集只用于 P2 排除，不能被解释为新候选池。
5. 2026-07-03 的 `final_experiment_setting_validity_audit_v0_1` 被本轮审计取代；旧文件
   保留但不再是 DSA 有效性依据。

## 4. 解除条件

本隔离不通过“修补旧脚本”解除。DSA 新实验必须在新命名空间、独立任务来源、冻结协议
和预注册分析下重新建立证据。任何例外都必须先修改计划和 denylist，并重新通过 P1 Gate。
