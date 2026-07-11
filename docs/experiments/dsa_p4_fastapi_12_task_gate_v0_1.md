# DSA 2026 P4 `bugsinpy_fastapi_12` task Gate v0.1

日期：2026-07-11
状态：`DISCARD_TASK / P4_CONTINUES_LATER / NO_API / P5_NOT_STARTED`

## 1. 冻结边界

该任务是冻结 Regular primary 顺序中的第 2 项。official reference F2P、3 个 visible
P2P、20 个 held-out regression nodes、task image、T4 transform 和 selected edit 均在
candidate outcome 前冻结。T4 selected edit SHA-256 保持为
`0a13deab2ab6aa6b37e4b54dff36d547532f7762ec12135e452548d0c22da2bf`。

首次四容器启动在任何 F2P/P2P/held-out outcome 前被 patch-apply integrity check
阻断：Docker task source 保留 CRLF，而候选 patch 被错误序列化为 LF。该执行链路问题
只通过保留 official raw newline bytes 和同一 selected edit 修复；没有更换 transform、
edit、oracle 或任务。修复后的 materialization SHA-256 为
`2cd71a77407a96169fb8988fb914666dab372ab6e4663452d148ae670b67bbb3`。

## 2. Fresh-container evidence

两候选各运行两个 distinct containers；四个 containers 均使用 image
`sha256:11fb7ffa940afd56884299fdb26a5775bf1b09ed87a5fb8c1c9213c04ad22da3`，
`network=none`、`mounts=0`、container exit=0，candidate patch/tree 和 worker hashes
均一致。

| role | run A container | run B container | basic | F2P | visible P2P | held-out | disposition |
|---|---|---|---:|---:|---:|---:|---|
| official positive | `85ed18c50fb8…` | `26eadd691063…` | 2/2 pass | 1/1 pass | 3/3 pass | 20/20 pass | `positive_valid` |
| T4 negative | `7e588bf36b1c…` | `0fff2361e5fa…` | 1/2 pass | 0/1 pass | 0/3 pass | 0/20 pass | `discard_visible_check_failure` |

T4 negative 的 patch-apply check 通过，但 `py_compile` 在两环境中均以
`IndentationError` 失败；F2P、3 个 visible P2P 和 20 个 held-out nodes 随后均稳定
失败。虽然它稳定失败 20 个 held-out checks，但 hard negative 必须先通过全部 visible
checks，因此不能 admission，也不能因为 hidden failure 明显而保留。

## 3. Task Gate

- positive：`positive_valid`；
- negative：`discard_visible_check_failure`；
- task Gate：`DISCARD_TASK`；
- admitted model-visible candidates：0；
- hidden/model-visible leakage：0；
- candidate results SHA-256：
  `cdfbd008a2585c93d0d7150682f9897f9e38314db2eb515f58b410859d6eacc2`；
- P4 final Gate：未形成；P5/API：未进入/0 calls。

该任务消耗 1 个非结构性 discard 余量，理论剩余余量从 6 降为 5。完整 P4 后续只能
按冻结规则在继续处理时使用 next frozen reserve；本 task-level Goal 在这里停止，不顺手
处理下一个任务。

机器证据：

- `data/hidden/dsa_p4_candidate_registry_v0_1.json`；
- `data/hidden/dsa_p4_candidate_results_v0_1.json`；
- `data/hidden/dsa_p4_task_gate_v0_1.json`；
- `data/cohorts/dsa_p4_model_visible_candidates_v0_1.json`；
- `data/protocols/dsa_p4_separation_audit_v0_1.json`；
- `data/protocols/dsa_p4_candidate_hash_manifest_v0_1.json`。
