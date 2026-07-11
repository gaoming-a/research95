# DSA P4 v0.1 终止记录

日期：2026-07-11
状态：`TERMINATED_BEFORE_MODEL_OUTPUT / PROTOCOL_REDESIGN / NO_API`

## 决定

P3/P4 v0.1 在任何模型调用前终止。该决定不是把不利模型结果删除，也不是声称已触发
“reserve 耗尽、少于 30 pairs”的预注册 capacity stop rule；该规则未触发，当前没有
模型结果，也没有确认性效果量。
终止原因是确认性 cohort 在 clean environment 和候选行为资格验证之前已冻结，导致 P4
的实际工作主要变成旧 benchmark 环境与材料复现，而不是 C0--C3 下 reviewer agent
决策变化实验。

P3 v0.1 的 16-file immutable manifest aggregate 仍为
`f81ba7063297dc9264041256b99a7daa002bd730cbe1dbd9bfb105cd7aa71297`，本终止记录不修改
任何 P2/P3 v0.1 冻结文件。

## 证据边界

- primary #1 `bugsinpy_sanic_5`：无适用 transform，结构性 discard；
- primary #2 `bugsinpy_fastapi_12`：T4 negative 语法/visible Gate 失败，task discard；
- primary #3 `bugsinpy_pandas_54`：无适用 transform，结构性 discard；
- primary #4 `bugsinpy_tornado_10`：官方 setup 含不可安装的 `unittest` distribution；
- primary #5 `bugsinpy_matplotlib_21`：clean F2P 因冻结环境缺少 NumPy 失败；
- P4 final Gate 未形成，P5 未开始，模型 API calls=0，确认性模型输出=0。

这些记录只能用于协议可行性、工程复盘和 v0.2 development exclusion，不得进入 v0.2
效果量、模型结果表或有效性 claim。上述五个已在 P4 活动中被检查的 task 不能进入
v0.2 确认性 cohort。

## 诊断

v0.1 的研究问题没有被当前失败否定。问题出在执行顺序：source-level improved
reproduction 不能替代 clean qualification；结构适用 transform 不能保证语法/visible
有效；同项目 reserve 也不能对冲项目级环境失败。

因此 v0.2 把候选物化和资格验证明确放在最终 cohort/P3 冻结之前。模型输出仍完全不参与
候选构造或选择。

机器记录：`data/protocols/dsa_v0_1_termination_and_v0_2_redesign_v0_1.json`。
