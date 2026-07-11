# DSA P4 `bugsinpy_matplotlib_21` Reference F2P Gate v0.1

Date: 2026-07-11

## Outcome

`DISCARD_PRE_CANDIDATE_REFERENCE_F2P_FAILURE`

The official reference patch and fixed declared test were prepared identically
in two fresh, mount-free, network-disabled containers. Both exact official F2P
commands failed before test collection because the frozen clean environment did
not contain NumPy.

The signed no-redesign rule forbids adding an undeclared dependency after this
outcome. The task is therefore discarded before regression-pool discovery and
before T2 candidate materialization.

## Frozen inputs

- selecting cursor SHA-256:
  `a212352973531adfc58b0e85978fcad1cf65adea100fb2584b66f03ebeb437fb`;
- source/context record SHA-256:
  `b1e09a00c57d8adfcfb65a71f5c3028c873f988b56d4f9f573c52a797cfd6660`;
- executor commit: `b6d0cc69a86a0f542efd543d5c40156b241c3481`;
- task image ID:
  `sha256:3632b1e6573f98531116b876d8bd25d00accac9ff3aca80b3e51095b3bb6c5a7`;
- Python environment: `py381` / Python 3.8.1;
- Conda explicit lock SHA-256:
  `df1e425eedcb0d3806b5bf10c55e369648621d93f46f5754cdc85f8435cf21f8`;
- reference patch SHA-256:
  `2874ffe8cac4b57f37eb9cc5b63d761736f5ebbf50568975bb4cce9e9ae9ece6`;
- prepared reference tree SHA-256:
  `371b33a1f7695bf6bf011663f4ff03c370d181a252300d289789dc8886786a66`.

## Dual-fresh evidence

| run | container | network | mounts | command exit | output SHA-256 |
|---|---|---|---:|---:|---|
| A | `5a6f036a024dcd092adbd69ae80fa56a7a415ce8465fc1705c5707ae2082f64f` | `none` | 0 | 4 | `966307f535435b2f4d646c7871debb59fcb1b4c72497199ca5c7d67c75b14ff5` |
| B | `8c634dc6e2049b5e38f5e36922734f085db7c5c5cc5a3e64dfdba5e1903ba87c` | `none` | 0 | 4 | `966307f535435b2f4d646c7871debb59fcb1b4c72497199ca5c7d67c75b14ff5` |

Both runs reported the same import chain and terminal error:

`ModuleNotFoundError: No module named 'numpy'`

Image labels, environment build-artifact hashes, reference preparation, command
identity, exit/timeout/outcome, and normalized output hashes all agreed. This is
an isolated frozen-environment F2P failure, not a network or run-disagreement
failure.

The earlier improved-reproduction logs contain NumPy, while that framework keys
shared Conda environments only by Python version plus requirements content.
Those historical logs remain source-frame provenance; they do not authorize
copying shared-environment packages into this clean P4 image.

## Boundary audit

- task image created: yes;
- official reference F2P executed: exactly two fresh runs;
- official reference F2P passed: no;
- regression pool discovered/frozen: no;
- transformed T2 candidate materialized or run: no;
- Matplotlib record in oracle/candidate/task-Gate registries: no;
- dependency, oracle, transform, or task repair: none;
- model API calls: 0;
- P5/rendered prompt/paper-result change: none.

Machine result SHA-256:
`2b20ec02f840ed8738d7a0fe29e3e9ce70adf4be892be3075b8fc050087a8c5c`.
Pre-candidate discard record SHA-256:
`9b36980b50a50d64c2a9692980cad6b328684b1f497dc3c5c180f255dd5fe7d9`.

Machine evidence is stored in
`data/hidden/dsa_p4_reference_f2p_results_v0_1.json` and
`data/hidden/dsa_p4_pre_candidate_discard_v0_1.json`. This bounded Goal stops
here and does not select or start the next task.
