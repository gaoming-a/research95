# DSA v0.2 V2-P1 Project Test-Scope Amendment Sign-off

日期：2026-07-12
状态：`AUTHOR_SIGNOFF_REQUIRED / NO_REAL_ACTIVITY / NO_API`

## 缺口

已签核 V2-P1 要求 regression pool 使用 project recipe 声明的 project test root，
但九个 recipe 均遗漏该字段。以下范围完全由冻结的299条 declared_test_file 在任何
task outcome 前机械推导，不使用 pandas_161 或其他任务的运行结果。

## 提议冻结值

| project | framework | project test root | collection adapter |
|---|---|---|---|
| `ansible` | `pytest` | `test/units` | `python -m pytest --collect-only -q test/units` |
| `black` | `unittest` | `tests` | `python -m unittest-discover --start-dir tests --pattern test*.py --top-level-dir .` |
| `fastapi` | `pytest` | `tests` | `python -m pytest --collect-only -q tests` |
| `keras` | `pytest` | `tests` | `python -m pytest --collect-only -q tests` |
| `matplotlib` | `pytest` | `lib/matplotlib/tests` | `python -m pytest --collect-only -q lib/matplotlib/tests` |
| `pandas` | `pytest` | `pandas/tests` | `python -m pytest --collect-only -q pandas/tests` |
| `sanic` | `pytest` | `tests` | `python -m pytest --collect-only -q tests` |
| `spacy` | `pytest` | `spacy/tests` | `python -m pytest --collect-only -q spacy/tests` |
| `tornado` | `unittest` | `tornado/test` | `python -m unittest-discover --start-dir tornado/test --pattern *_test.py --top-level-dir .` |

amendments SHA-256：`b5778a7c95042d5475d333842c5b8a486a2798a7586d74a20a84e30487ddef94`。

## 作者签核（未签）

作者需明确确认：接受上述机械 derivation rule、九个 project test roots、两个
unittest patterns 与 collection adapters；该签核只补齐 V2-P1 project recipe
的缺失 test-scope 字段并授权恢复已批准的首任务 Goal，不授权修改其他 V2-P1
规则，不授权第二个 task、V2-P3、prompt、论文结果或模型 API。

当前真实 checkout/environment/container/test/API activity 全部为0。
