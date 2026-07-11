# DSA 2026 P2 Conditional Precision Simulation v0.1

日期：2026-07-11

## 结论

- Regular：最大 primary-rate interval width = 0.1185（门限 0.35）；最大 paired-effect width = 0.1704（门限 0.30）。
- Short：最大 paired-effect width = 0.2500（门限 0.40）。
- Gate：Regular=PASS；Short=PASS。

## 模拟边界

每个场景模拟 20000 个固定 run window，覆盖 C0/C3 marginal rate 0.1、0.25、0.5、0.75、0.9，
以及 requested within-block correlation 0、0.3、0.6；不可能的 Bernoulli correlation 按 Fréchet boundary 截断并记录实际值。

区间只量化固定 task/model 下三次 stateless repeat 的 decision stochasticity。task 和 project 不是总体随机样本，
因此这些宽度不得称为跨项目总体置信区间。leave-one-project-out effect range 只作为稳定性边界报告，不是 CI。

本模拟未调用模型、未读取任何模型输出、旧论文指标或 candidate hidden result。
