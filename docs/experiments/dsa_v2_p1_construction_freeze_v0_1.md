# DSA v0.2 V2-P1 材料构造协议冻结记录

日期：2026-07-12
状态：`PASS / AUTHOR_SIGNED / RULES_FROZEN / V2-P2_NOT_AUTHORIZED / NO_API`

## 1. 结果

作者高明签核的8项声明已保存、哈希绑定并与机器协议逐项对应。V2-P1 只冻结
材料构造规则和完整 source order；没有 checkout、环境构建、container、project test、
candidate outcome、prompt render 或模型请求。

- author declaration SHA-256：`65328de6aa913bd8ee04dfdbfd172960745bc431ab7d2f7742c8aa7038dbe2ca`；
- eligible tasks：299；
- projects：9；
- frozen source-order SHA-256：`21be1d9fed719de44126be585fa7e9123fd8579588d9ce86eb396d4ab5c2dd11`；
- target：机械顺序中前30个完整 oracle-positive/hard-negative pairs；
- source 耗尽不足30 pairs：在 V2-P3/API 前停止。

## 2. Source order 前12项

| order | round | project | task | framework |
|---:|---:|---|---|---|
| 1 | 1 | pandas | `bugsinpy_pandas_161` | pytest |
| 2 | 1 | fastapi | `bugsinpy_fastapi_11` | pytest |
| 3 | 1 | black | `bugsinpy_black_4` | unittest |
| 4 | 1 | keras | `bugsinpy_keras_40` | pytest |
| 5 | 1 | ansible | `bugsinpy_ansible_8` | pytest |
| 6 | 1 | tornado | `bugsinpy_tornado_3` | unittest |
| 7 | 1 | matplotlib | `bugsinpy_matplotlib_4` | pytest |
| 8 | 1 | spacy | `bugsinpy_spacy_8` | pytest |
| 9 | 1 | sanic | `bugsinpy_sanic_4` | pytest |
| 10 | 2 | pandas | `bugsinpy_pandas_167` | pytest |
| 11 | 2 | fastapi | `bugsinpy_fastapi_5` | pytest |
| 12 | 2 | black | `bugsinpy_black_5` | unittest |

完整299项及所有 official metadata hashes 位于
`data/protocols/dsa_v2_p1_source_order_v0_1.json`。顺序使用 domain-separated
SHA-256 project/task keys 做 project round-robin，不读取 candidate 或 model outcome。

## 3. 冻结构造规则

- 环境：每个 project 在首个 outcome 前实例化同一 recipe template；使用 task
  requirements、project package metadata、六个 hash-bound Python explicit locks
  和 pip20.1.1/setuptools47.1.1/wheel0.34.2/pytest5.4.3/packaging20.4；
  不执行腐化 `setup.sh`；
  task 失败后禁止定向补依赖或兼容修补。
- regression oracle：fixed tree 上先冻结最多40个相关 nodes；双 fresh positive
  稳定通过后，前3个作 visible P2P、随后最多20个作 hidden，至少需3+1。
- candidate：按 T1 file、T2 hunk、T3 edit block、T4 changed line 的固定优先级
  枚举；类内按 descriptor hash；选择第一个 visible 全过且 hidden 稳定失败者。
- positive/negative 均需两个 distinct fresh、network-none、mount-free containers；
  语法/basic 或任何 visible failure 都不能成为 hard negative。

## 4. Gate checks

- `author_declaration_exact`: PASS
- `author_declaration_sha256`: PASS
- `author_signed_all_eight_items`: PASS
- `signoff_document_bound`: PASS
- `p3_v0_1_manifest_intact`: PASS
- `official_catalog_commit_match`: PASS
- `eligible_count_is_299`: PASS
- `eligible_projects_are_nine`: PASS
- `p2_development_tasks_absent`: PASS
- `p2_excluded_projects_absent`: PASS
- `v0_1_active_tasks_absent`: PASS
- `all_f2p_commands_match_catalog`: PASS
- `source_order_contiguous_unique`: PASS
- `source_order_is_pre_outcome`: PASS
- `project_recipes_cover_all_projects`: PASS
- `base_python_locks_complete_and_hash_matched`: PASS
- `official_setup_is_not_executable_authority`: PASS
- `candidate_order_has_four_frozen_classes`: PASS
- `qualification_requires_dual_visible_pass_hidden_fail`: PASS
- `target_and_source_exhaustion_stop_frozen`: PASS
- `no_v2_p2_or_api_authorization`: PASS

## 5. 当前边界

V2-P1 完成不等于 V2-P2 授权。下一 Goal 最多可实现 executor 和 synthetic
check-only dry-run；真实 task checkout、environment、container/test 和 model API
仍需新的明确授权。prompt/schema 保持 v0.1 冻结文件不变且当前不执行。

机器协议：`data/protocols/dsa_v2_p1_construction_protocol_v0_1.json`。
机器审计：`data/protocols/dsa_v2_p1_gate_audit_v0_1.json`。
冻结 manifest：`data/protocols/dsa_v2_p1_hash_manifest_v0_1.json`。
