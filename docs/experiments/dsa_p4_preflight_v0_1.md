# DSA 2026 P4 pre-transform preflight v0.1

日期：2026-07-11
状态：`PASS / P4_MATERIALIZATION_CONTINUES / NO_API / P5_NOT_STARTED`

## 1. 边界

本检查只冻结 P4 的结构输入和 candidate-independent bootstrap 环境。它没有构造
candidate、没有运行 transformed outcome、没有读取旧 candidate/模型输出/论文指标、
没有生成 rendered prompt、没有进入 P5，也没有调用模型 API。

reference patch 的唯一权威来源是 official BugsInPy `bug_patch.txt`，应用基线是 P2
source frame 中声明的 buggy commit。official `run_test.sh` 必须与 P2 冻结的 F2P
命令逐项一致。路径组件为 `test/tests/testing` 或文件名匹配 `test_*`、`tests_*`、
`*_test.py`、`*_tests.py` 的 patch 文件不进入 candidate transform；测试修改不是
候选补丁的一部分。

## 2. 不可变输入复核

- P2 protocol/source order/transform/development exclusion 四个 raw SHA-256 全部不变；
- P3 Gate=`PASS`，16 个 authoritative files 的 canonical hashes、byte counts 和
  aggregate `f81ba7063297dc9264041256b99a7daa002bd730cbe1dbd9bfb105cd7aa71297`
  全部不变；
- official BugsInPy catalog 仍位于 commit
  `11c5f1eea954a42132cfd06bf257766a7963e0fd`；
- Regular 顺序仍为 30 primary + 10 reserve，40 个 official F2P 命令均与 catalog
  `run_test.sh` 一致，所有 reference patch/bug info/requirements/run-test/setup 输入
  均已哈希。

## 3. 结构适用性

在任何 transformed candidate outcome 前，只对 source-only reference diff 计算冻结
shape，并按 T1--T4 priority 选择第一个结构适用 transform：

| disposition | 数量 |
|---|---:|
| T1 omit secondary source file | 3 |
| T2 omit secondary hunk | 17 |
| T3 omit secondary edit block | 8 |
| T4 partial multiline reversion | 8 |
| no applicable transform | 4 |

四个 `NONE` 均为 primary：`bugsinpy_sanic_5`、`bugsinpy_pandas_54`、
`bugsinpy_spacy_10`、`bugsinpy_fastapi_10`。它们按冻结规则作结构性 discard，不能
改 transform 或用结果重新分类。40 个任务中最多 36 个可进入 candidate
materialization，因此 P4 仍结构上可达到 30 pairs，但只剩 6 个非结构性 discard
余量。

## 4. Bootstrap environment lock

Docker base tag 在构建前强制核验为 repo digest
`sha256:e4e42fb5e98a45ba82afd5f9d4cd2ad297bbfe912ca3954eb03f2d7b57c7fa98`。
六个 Python 版本均实际创建并导出 Conda `@EXPLICIT` locks；bootstrap 工具固定为
pip 20.1.1、setuptools 47.1.1、wheel 0.34.2、pytest 5.4.3、packaging 20.4。
所有 Conda URL 只使用启用证书校验的清华镜像，pip index 同样为 HTTPS 镜像。

构建后的 candidate-independent toolchain image ID 为
`sha256:97e089cee02d0908e374f7b784ee0ffbb2fe5a2d64f619335aa962dc3ab3d768`。
两个 `--network none` fresh containers 的 6 个 lock hashes 与 Python version 输出
逐字节一致。该镜像不含项目 source、candidate 或 outcome。

首次 sanic 环境 pilot 暴露了 `setuptools 75.1.0` 与复现清单固定的
`packaging 20.4` API 不兼容，导致 fixed F2P 在 import 前失败。使用上述冻结构建
工具后，从新容器完整重跑得到 buggy=`fail`、fixed=`pass`，fixed 输出明确为目标
node `1 passed`。该 pilot 只验证环境链路；由于 `bugsinpy_sanic_5` 没有适用
transform，它不构成 P4 pair，也不进入 cohort。

## 5. 下一 Gate

下一步只允许为 36 个结构适用任务依 frozen stream 构建 task-specific dependency
image，并在 transform 前冻结 reference-stable visible P2P/hidden nodes。每个正式
候选仍须在两个从同一 task-image digest 新建且无共享 writable volume 的 containers
中执行全部冻结 checks。P4 Gate 尚未形成，P5/API 继续禁止。

机器证据：`data/protocols/dsa_p4_preflight_v0_1.json`
生成/审计器：`scripts/dsa2026_p4_preflight.py`
