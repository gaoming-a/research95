# DSA v0.2 V2-P2 Executor Synthetic Check-Only

日期：2026-07-12
状态：`PASS / SYNTHETIC_ONLY / FIRST_TASK_NOT_STARTED / NO_API`

## 1. 结果

V2-P2 executor 已实现为纯状态机。它只能消费审计器传入的 synthetic metadata，
没有 filesystem/process/network/container/test/prompt/API 能力。V2-P1 manifest、
299-task source order、六个 locks、project recipe、T1--T4、3-visible/20-hidden、
dual-fresh 和30-pair/source-exhaustion规则全部绑定。

- V2-P1 aggregate：`ed7c927129c47027b57374625a2d76667503bbb1d8d37e04d4460e42b2ae8b40`；
- source-order：`21be1d9fed719de44126be585fa7e9123fd8579588d9ce86eb396d4ab5c2dd11`；
- 唯一 next task：`bugsinpy_pandas_161`；
- next task started：false；
- real checkout/environment/container/project-test/model API：全部0。

## 2. Synthetic paths

| path | terminal cursor | result |
|---|---|---|
| `pair_success` | `pending` | `first-frozen-order-hard-negative-qualified` |
| `environment_failure` | `pending` | `environment-failure-or-dual-disagreement` |
| `oracle_positive_failure` | `pending` | `oracle-positive-failure-or-dual-disagreement` |
| `no_qualifying_hard_negative` | `pending` | `no-qualifying-hard-negative` |
| `source_exhaustion` | `source-exhausted` | `eligible-source-order-exhausted-before-30-pairs` |
| `target_30_reached` | `cohort-qualified` | `target-pairs-reached` |

## 3. Protocol drift rejection

- `out_of_order_task_rejected`: REJECTED (`observation does not match unique frozen next task`)
- `tampered_candidate_order_hash_rejected`: REJECTED (`candidate order SHA-256 drift`)
- `noncontiguous_ledger_rejected`: REJECTED (`ledger does not follow contiguous frozen source order`)
- `execution_after_target_rejected`: REJECTED (`cannot execute from terminal cursor: cohort-qualified`)
- `execution_after_source_exhaustion_rejected`: REJECTED (`cannot execute from terminal cursor: source-exhausted`)

## 4. Preflight checks

- `v2_p1_manifest_aggregate_unchanged`: PASS
- `v2_p1_manifest_files_unchanged`: PASS
- `source_order_count_is_299`: PASS
- `source_order_sha256_unchanged`: PASS
- `cursor_selects_only_frozen_first_task`: PASS
- `cursor_does_not_start_task`: PASS
- `six_base_locks_match`: PASS
- `project_recipe_count_is_nine`: PASS
- `project_recipe_boundaries_match_v2_p1`: PASS
- `candidate_class_order_matches_v2_p1`: PASS
- `oracle_split_matches_v2_p1`: PASS
- `dual_fresh_matches_v2_p1`: PASS
- `cursor_stop_rules_match_v2_p1`: PASS
- `executor_has_no_external_execution_capability`: PASS
- `v2_p2_real_materialization_not_authorized`: PASS
- `model_api_not_authorized`: PASS

## 5. Synthetic checks

- `success_selects_first_qualifying_candidate`: PASS
- `environment_failure_is_terminal`: PASS
- `oracle_positive_failure_is_terminal`: PASS
- `no_qualifying_negative_is_terminal`: PASS
- `source_exhaustion_stops_before_30`: PASS
- `target_30_stops_without_source_exhaustion`: PASS
- `all_cases_keep_real_activity_zero`: PASS
- `all_cases_refuse_to_start_selected_task`: PASS
- `all_protocol_drift_attempts_rejected`: PASS

## 6. Boundary

本记录不授权真实 V2-P2。`bugsinpy_pandas_161` 只作为 cursor identity 被读取，
未 checkout、未构建、未启动、未测试。真实材料化必须由新的明确授权 Goal 开始。
prompt/schema、论文结果和模型 API 均未触碰。
