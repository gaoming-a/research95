# DSA 2026 P4 replacement cursor audit v0.1

日期：2026-07-11
状态：`PASSED_UNIQUE_NEXT_TASK / NO_NEW_EXPERIMENT / NO_API / P5_NOT_STARTED`

## 1. 顺序解释

冻结执行游标按 primary order 先扫描；遇到 structural/terminal discard 时，
只把该 slot 分配给 frozen reserve prefix，reserve 在 primary scan 完成后按顺序执行。
这一解释沿用 outcome 前的实际轨迹：primary #1 `bugsinpy_sanic_5` 结构 discard 后，
P4 已直接进入 primary #2 `bugsinpy_fastapi_12`，未先执行 reserve #1。

## 2. 已实现游标

| primary order | task | disposition | replacement |
|---:|---|---|---|
| 1 | `bugsinpy_sanic_5` | `discard_structural_no_applicable_transform` | reserve #1 `bugsinpy_sanic_4` |
| 2 | `bugsinpy_fastapi_12` | `discard_terminal_task_gate` | reserve #2 `bugsinpy_fastapi_6` |
| 3 | `bugsinpy_pandas_54` | `discard_structural_no_applicable_transform` | reserve #3 `bugsinpy_pandas_90` |

唯一 next task：

- primary order：4；
- task：`bugsinpy_tornado_10`；
- transform：`T1_omit_secondary_source_file`；
- cursor SHA-256：`24f37f3f2eefe99c9346b4b141965cb137e8f7dfb87e6e11eaa0ac909b0fbf2e`。

## 3. Capacity

- target pairs：30；
- known structural primary discards：4；
- terminal nonstructural discards：1；
- maximum possible pairs after known discards：35；
- remaining nonstructural discard budget：5；
- realized replacement slots：3；
- unallocated reserves：7。

## 4. Gate

全部 P2/P3/P4 input hashes、30+10 order、contiguous cursor、reserve-prefix replacement、
terminal task Gate、capacity 和 no-API/no-P5 boundary 均通过。下一 Goal 才允许针对
`bugsinpy_tornado_10` 建立 task environment 和 pre-outcome oracle；本审计未运行新实验。

机器证据：`data/protocols/dsa_p4_replacement_cursor_v0_1.json`。
生成/审计器：`scripts/dsa2026_p4_replacement_cursor_audit.py`。
