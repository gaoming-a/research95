# DSA reviewer-agent 证据条件实验计划 v0.2

日期：2026-07-11
状态：`DESIGN_DRAFT / AUTHOR_SIGNOFF_REQUIRED / NO_API`

## 1. 一句话论点

在最终预注册前已完成行为资格验证、且与开发任务隔离的 patch cohort 上，估计真实累积
执行证据从 C0 增至 C3 时，固定 reviewer agent 对 oracle-positive 与 hard-negative
候选作出 `accept`、`reject`、`escalate` 决策的变化；结论只适用于冻结的 task、模型
route 和运行窗口，不证明自主验证、修复正确性或部署安全性。

## 2. 术语锁定

| 术语 | v0.2 定义 | 禁止混用 |
|---|---|---|
| reviewer agent | 固定模型 endpoint 执行同一个中性 prompt 和 JSON schema；无自主工具，只读取给定 evidence packet | autonomous repair agent、tool-using verifier |
| task | 一个真实缺陷来源及其一对合格候选；唯一科学分析单位 | request、candidate、repeat |
| oracle-positive | 在同一冻结环境中两次通过 basic、visible、hidden checks 的正确候选 | “绝对正确补丁” |
| hard-negative | 语法/basic/全部 visible 通过，但至少一个独立 hidden check 两次稳定失败的部分修复 | 语法错误、visible-fail patch |
| condition | 同一候选的一个累积可见证据包 C0--C3；名称不向 agent 暴露 | label、verdict |
| accept | 建议自动合并 | 正确标签 |
| reject | 建议不合并 | 错误标签 |
| escalate | 已给信息不足以自动决策 | 失败或缺失值 |

## 3. 保留的研究问题

- RQ1：对 hard-negative，C3 相比 C0 如何改变 `accept` 概率？主 estimand 为
  `Delta_minus=P(accept|C3,negative)-P(accept|C0,negative)`。
- RQ2：对 oracle-positive，C3 相比 C0 如何改变 `accept` 概率？主 estimand 为
  `Delta_plus=P(accept|C3,positive)-P(accept|C0,positive)`。
- RQ3：C0 到 C3 的 `accept/reject/escalate` 转移路径及三条模型 route 的差异如何？

两项主效果必须一起报告；不能只报告方向有利的一项。task 是分析单位，candidate、
condition、model、repeat 和 request 都是 task 内嵌套单位。

## 4. 为什么 v0.2 改变执行顺序

v0.1 在 clean environment 和候选行为资格验证前冻结 30 primary + 10 reserve，随后
出现结构不适用、官方环境腐化、缺失依赖和语法无效 negative。它们没有产生模型结果，
但证明“source metadata 可用”不等于“agent 实验材料合格”。

v0.2 只改变材料构造与最终冻结的先后顺序：先冻结通用构造规则，再机械构造候选池；
只有已经通过资格验证的前 30 个 task pairs 才进入最终确认性 cohort。模型回复永远不
参与材料选择。

## 5. 最短执行链

### V2-D0：关闭 v0.1（本轮）

- 保留全部 P2/P3/P4 v0.1 记录和 hashes；
- 状态记为 `TERMINATED_BEFORE_MODEL_OUTPUT`，不是 confirmatory result；
- 五个 v0.1 P4-active tasks 进入 v0.2 development exclusion；
- 不调用模型、不改 prompt、不改论文结果。

### V2-P1：冻结材料构造协议

在查看任何新 task qualification outcome 前，冻结并由作者签核：

1. source eligibility、development exclusion 和 hash-seeded task order；
2. project-level environment recipe policy；
3. deterministic ordered candidate generator；
4. positive、negative、visible、hidden 的资格规则；
5. source-frame exhaustion stop rule；
6. 全部失败记录与 no-task-specific-repair 规则。

本阶段只冻结规则，不运行新 task，不调用模型。

### V2-P2：预模型材料池构造

- 按冻结顺序逐 task 处理，不预先固定“必须保留”的 40 项；
- 每个 project 的环境 recipe 必须在该项目 task outcomes 前冻结，并对该项目所有尝试
  一致；可安装声明的 runtime/test dependencies 和 project 本身，但不得在某 task
  失败后添加 task-specific 修补；
- oracle-positive 必须在两个 fresh isolated runs 中通过全部 basic/visible/hidden；
- partial-fix candidates 按冻结顺序生成，取第一个两次稳定满足“basic+visible 全过、
  至少一个 independent hidden 失败”的候选；
- 无合格 negative 时记录 materialization failure，继续冻结 task order，不手工修补；
- 首次累计 30 个完整 task pairs 后停止材料构造；source frame 先耗尽则在 API 前停止。

这一阶段会运行代码和测试，但它仍是 stimulus construction，不产生 agent 回复。

### V2-P3：确认性冻结和作者签核

对已经合格的 30 pairs 冻结：candidate/environment/evidence hashes、C0--C3 contract、
prompt/schema、三条模型 route、三次 stateless repeats、请求顺序、重试/成本/token/时间窗、
统计 seed 和分析程序。作者逐项签核前，API 始终禁止。

### V2-P4：全量 render/check-only

离线生成 30 tasks × 2 candidates × 4 conditions = 240 个匿名 packets，验证：

- C0--C3 只能累加冻结的下一 evidence group；
- 同一 candidate 的已有字段逐字节不变；
- 不暴露 condition、task/project、candidate role、oracle、label 或 verdict；
- 所有 command/result、environment hashes、schema、token 和调度检查通过。

### V2-P5：reviewer-agent 模型实验

只有 V2-P1--P4 全部 PASS、V2-P3 作者签核且 exact routes 重新核验后，独立 Goal 才可
先做 bounded smoke，再运行冻结 full experiment。

计划有效响应数：

`30 tasks × 2 candidates × 4 conditions × 3 models × 3 repeats = 2160`。

### V2-P6：分析与论文

模型输出及 hashes 冻结后才连接 hidden role/tree，计算 `Delta_minus`、`Delta_plus`、
决策转移矩阵、模型异质性、repeat disagreement、project-balanced 和 leave-one-project-out
稳定性。随后按真实结果修改论文，不允许因不利结果重跑。

## 6. C0--C3 evidence contract

| 条件 | 累积可见内容 |
|---|---|
| C0 | neutral change request、candidate diff、必要 code context |
| C1 | C0 + patch apply 与 syntax/import/static 的真实命令和结果 |
| C2 | C1 + 预注册 visible fail-to-pass 命令和结果 |
| C3 | C2 + 预注册 visible pass-to-pass/regression 命令和结果 |

所有非 C0 evidence group 必须非空、command/result 成对、绑定完整环境 hashes；禁止
placeholder、not-run、tool verdict 或 hidden oracle。

## 7. 统计与停止边界

- 保留 v0.1 的 task-macro paired `Delta_minus`/`Delta_plus` 结构；最终 seed、interval
  和 executable analysis 在 V2-P3 重新冻结；
- 不把 2160 requests 当作 2160 个独立样本；
- 不用 pooled p-value，不声称总体项目/模型置信区间；
- 材料阶段 source frame 耗尽但不足 30 pairs：API 前停止并报告 feasibility failure；
- 模型阶段 valid response 永不覆盖；只允许冻结协议定义的 transport/429/empty retry；
- null、negative、heterogeneous、wide interval 或 reviewer 偏好不能触发重跑。

## 8. Claim--evidence map

| Claim | 所需证据 | 当前状态 |
|---|---|---|
| v0.1 在模型前因协议路线偏移终止 | v0.1 Gate、P3 hash、API=0 | supported |
| v0.2 材料构造不使用模型 outcome | V2-P1 rules + V2-P2 audit | needs execution |
| C3 改变 hard-negative accept policy | 新输出上的 `Delta_minus` | needs V2-P5/P6 |
| C3 改变 oracle-positive accept policy | 新输出上的 `Delta_plus` | needs V2-P5/P6 |
| agent 能自主验证或修复补丁 | 本设计不提供该证据 | forbidden claim |

## 9. 当前边界与下一 Gate

本文件是设计草案，不是新的预注册签核，也不授权 task materialization、prompt 修改、
API 或论文结果修改。下一 Goal 只能在作者签核 V2-P1 的构造规则后，建立 source order、
project recipe policy、candidate generator 和 check-only preflight；不得顺手进入 V2-P2。

机器设计：`data/protocols/dsa_v0_1_termination_and_v0_2_redesign_v0_1.json`。
机械审计：`scripts/dsa2026_audit_v0_2_redesign.py`。
