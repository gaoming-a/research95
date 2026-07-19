# 大模型原生候选方向审计 v0.1

日期：2026-07-19

状态：`CANDIDATE_AUDIT_ONLY / TOPIC_NOT_LOCKED / DATA_NOT_AUTHORIZED /
NO_MODEL_OR_EXPERIMENT`

## 1. 本轮纠正与边界

通信工程是作者的培养专业，不是后续课题必须使用的应用场景。作者实际研究方向是大
模型，且没有系统学习通信领域内容。因此本轮从通用大模型和大模型智能体出发重新筛选，
不再把网络故障、ns-3、3GPP 或其他通信知识作为前提。

本文件只记录候选问题、近期直接近邻、机械标签方案、最简单基线和停止条件。它不代表：

- 已经确定论文题目；
- 已经证明创新；
- 已经授权读取、生成或下载研究数据；
- 已经选择模型、训练方法、超参数或样本量；
- 已经授权模型/API、训练、容器、工具环境或真实实验。

规范 future manifest 仍必须为空、`not_started` 且
`data_use_authorized=false`。只有作者完成逐问确认、锁定版计划通过独立对抗审查并另行
签核数据边界后，才能进入 feasibility。

## 2. 第一性原理筛选标准

一个候选只有同时满足以下条件才值得进入下一轮：

1. **实际问题不是常识重述。** 不能只是“信息更多通常更准”“训练更多通常更好”或
   “加入验证通常更可靠”；必须存在相反结果也合理的可证伪比较。
2. **研究对象是大模型。** 场景可以是工具调用、代码或形式任务，但贡献必须研究模型的
   规划、泛化、适应或可验证行为，而不是只实现传统业务系统。
3. **主标签可机械获得。** 优先使用执行、状态机、求解器、模型检查器或形式约束；不能
   让 LLM-as-a-judge 或作者逐条主观判断定义主要结果。
4. **最简单方法不能提前解决。** 固定规则、模板、Schema diff、经典规划器、检索和
   确定性报告器必须作为前置 Gate，而不是论文结束后才补的弱基线。
5. **小论文和硕士论文共享一条科学主轴。** 硕士论文要增加新的不确定性、决策范围或
   验证边界，不能只增加模型、样本和 GPU。
6. **近期直接近邻后仍有剩余空间。** 宽泛的工具恢复、动态工具适应、结构化输出、
   多约束自修正、RAG 冲突、普通代码测试和 LoRA 遗忘均不能直接作为题目。

## 3. 条件首选：动作后结果不确定性下的安全恢复

### 3.1 实际问题

工具返回超时、连接中断或响应丢失时，外部操作可能已经生效，也可能没有生效。对于
付款、发邮件、创建订单、修改文件或提交任务等有副作用的工具，模型若把“没有收到成功
响应”理解为“操作没有发生”并直接重试，可能造成重复扣款、重复发送或重复写入；若直接
宣布成功，也可能掩盖未完成操作。

该问题与原研究中“证据越多是否越好”不同。这里同一可见错误对应多个仍可能的世界
状态，新增的错误消息并不自动消除不确定性，额外动作还可能造成不可逆伤害。可证伪问题是：

> 当一次有副作用的工具调用产生歧义结果时，大模型智能体能否依据工具契约和当前可能
> 世界集合，选择对所有仍可能状态都安全且能够推进任务的核对、带幂等键重试、补偿、
> 终止或升级动作？

### 3.2 最小形式化

令 `S` 为有限世界状态，`B_t ⊆ S` 为智能体根据当前历史仍不能排除的状态集合。工具
动作 `a` 具有前置条件、可能状态转移、可见观测、副作用类型、幂等性与补偿属性。歧义
响应后，标签器不得使用智能体不可见的真实状态直接给答案，而应在整个 `B_t` 上判断：

- **安全性**：动作在每个 `s ∈ B_t` 中都不违反冻结不变量；
- **信息推进**：只读核对动作能否把 `B_t` 分成会改变后续安全选择的子集；
- **可靠终止**：只有 `B_t` 中全部状态均满足目标时才能报告成功；
- **可恢复性**：在允许的公平故障假设下，条件策略是否能够到达目标或正确升级。

小论文只要求判断当前下一步或短恢复片段；硕士论文才扩展为从观测历史到动作的条件
策略图，并用模型检查器穷举允许分支。

### 3.3 为什么仍可能有创新空间

近期近邻已经很强，因此允许的 claim 必须很窄：

- [Atomix](https://arxiv.org/abs/2602.14849) 和
  [Cordon](https://arxiv.org/abs/2606.17573) 通过事务运行时、暂存、提交与补偿约束
  副作用；本候选不能再声称首次研究“可靠副作用工具”，而只研究事务或幂等能力不完整时，
  模型面对**动作后隐藏状态歧义**的恢复决策。
- [ToolGate](https://aclanthology.org/2026.findings-acl.470/) 用前置/后置条件验证调用和
  状态提交；本候选必须评价歧义观测后对整个 belief set 正确的核对与条件恢复，而不是
  再做一次调用 Gate。
- [Fission-GRPO](https://aclanthology.org/2026.acl-long.1880/) 从已经观察到的执行错误
  学习纠错；本候选的关键输入是无法判断操作是否发生的结果，而不是已知失败及其诊断消息。
- [Near-Miss](https://aclanthology.org/2026.gem-main.30/) 检测已完成轨迹是否跳过必要
  检查；本候选必须在执行前后生成或评价对全部允许结果都安全的恢复决策。
- [CAR-bench](https://arxiv.org/abs/2601.22027) 与
  [ClarifyBench](https://aclanthology.org/2026.findings-acl.2028/) 主要处理动作前的用户
  意图、缺参或可行性不确定；本候选只保留动作后的外部系统状态不确定。
- [Mnemosyne](https://arxiv.org/abs/2607.00269) 对工作流提案和修复做确定性准入；本
  候选不得把“有验证器的工作流修复”当创新，剩余问题只能是模型如何根据不可区分状态
  选择信息动作及生成分支恢复策略。
- [EvoC2F](https://openreview.net/forum?id=ZSGB91kMOG) 已在计划中显式编码副作用、重试
  策略和幂等要求，并通过编译与验证提供容错。若全文复核表明其已覆盖歧义执行结果下的
  belief-state 恢复或全分支策略验证，本候选立即 No-Go。

因此当前只能写为“创新窗口待全文复核”，不能写成“尚无人研究”。

### 3.4 数据与机械 oracle

本候选不需要使用现成研究样本。未来若获授权，可从作者自建、版本化的有限状态工具 DSL
生成：

- 任务目标与初始状态；
- 工具前置条件、状态效果、返回观测与副作用；
- 成功但响应丢失、执行前失败、部分效果、重复请求、查询延迟等故障分支；
- 幂等、带幂等键、可查询、可补偿、不可逆和必须人工升级等契约组合；
- 每个 belief state 下的安全动作集合与条件策略。

机械 oracle 由经典 belief-state 搜索和模型检查组成。自然语言任务与工具说明只能由
自有模板/语法生成，并与形式源记录一一绑定；主要标签不能由文本模型产生。将来可自行
决定代码和数据许可，但本轮不创建数据，也不预先声明发布许可。

划分必须按以下派生闭包分组，禁止随机拆句子：

- 同一状态机拓扑；
- 同一工具族与副作用机制；
- 同一故障组合；
- 同一自然语言语法族；
- 同一基础任务的全部改写、观测和反事实状态。

至少需要“未见工具族”“未见拓扑”“未见故障组合”三类 OOD 测试，才能说明模型学到
契约与恢复关系，而不是记住模板。

### 3.5 小论文最短路径

暂定问题名而非论文题目：**动作后歧义结果下的核对优先恢复**。

小论文只研究一次关键决策，构造可见错误相同但契约不同的匹配组：

1. 工具天然幂等，直接重试安全；
2. 工具非幂等但有状态查询，应先核对；
3. 工具非幂等但支持稳定幂等键，可携原键重试；
4. 已产生部分效果且可补偿，应按依赖执行补偿或继续；
5. 无可靠查询、补偿或幂等机制，应停止并升级，不能猜测成功或失败。

主要指标：

- belief-safe next-action accuracy；
- 重复副作用率；
- 不确定状态下的无依据成功报告率；
- 可恢复任务的稳健完成率；
- 多余核对、调用数和恢复成本。

如果无训练评测已经构成清晰发现，小论文不必加入微调。只有模型在严格 OOD 中存在稳定
缺口，且简单基线没有解决任务时，才考虑用求解器生成的策略/反例做 3B/7B LoRA；GPU
数量不是启动训练的理由。

### 3.6 硕士论文递进

小论文 Gate 全部通过后，硕士论文才增加新的科学变量：

1. 从单步安全动作扩展为条件恢复策略 DSL/图；
2. 从观测到的单一故障扩展为部分可观测、多故障和部分效果；
3. 从轨迹成功扩展为 safety、可靠终止和目标可达性的全分支模型检查；
4. 加入验证器反例驱动的策略修订；
5. 若训练 Gate 通过，再比较 SFT、LoRA 或可验证奖励训练在未见工具族上的泛化；
6. 最后才研究成本、失败概率或人工升级预算，不在首篇同时引入。

### 3.7 必须先打败的基线

无模型 Gate 至少包括：

1. 总是重试、总是假定成功、总是终止、总是先查询；
2. 按 `idempotent / queryable / compensatable` 字段写成的固定规则；
3. 给定形式 DSL 的强/强循环 contingent planner（oracle 上界）；
4. 确定性自然语言解析器加 planner；
5. 关键词、长度、工具名和故障码分类器；
6. ReAct 与显式契约 prompting；
7. LLM 生成候选动作后由模型检查器返回一个反例再修订。

planner 是标签 oracle，不是要被 LLM 在形式输入上击败的对象。LLM 可能有价值的部分只能
是从自然语言任务/契约中形成能跨工具族泛化的恢复判断或策略；如果确定性解析器能稳定
完成该映射，课题不成立。

### 3.8 硬性 No-Go

以下任一项成立就停止，不通过换模型或微调包装：

- 数据实际退化为“超时后总是查询一次”；
- 没有同一可见观测对应不同隐藏状态的动作后歧义；
- 正确动作依据标签器知道的真实状态，而不是智能体可见的 `B_t`；
- 固定契约规则或确定性解析器在严格 OOD 上达到近饱和；
- 事务、幂等键或运行时准入机制已经无条件消除了全部研究状态；
- 自然语言只是少量固定模板，工具名或故障码即可预测答案；
- 只测抽样 rollout 成功率，不验证条件策略的全部允许分支；
- 不能构造至少三类本质不同的副作用、三类故障机制和非平凡恢复分支；
- 近期全文复核发现直接工作已研究动作后歧义结果、belief-state 信息获取与模型检查策略；
- 经典规划/形式化部分成为全部贡献，大模型只负责把固定字段改写成另一种格式；
- 预注册的两个开放模型家族没有稳定失败空间，因而不存在训练或方法改进问题。

## 4. 条件后备一：可认证的组合式工具契约迁移

问题是：旧工具接口发生多个相关变化后，模型能否在新接口下保持原用户意图和最终环境
状态，而不是只生成 Schema 合法但语义过时的调用。潜在标签可由带证书的契约变换、
Schema 验证、执行和最终状态等价共同生成。

该方向数据与标签清晰，但创新风险高于首选：

- [ToolEVO](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d8d1d325f822e07d16866780cc23deb2-Abstract-Conference.html)
  已研究名称、参数和返回格式等 API 演化；
- [RoTBench](https://aclanthology.org/2024.emnlp-main.19/) 已覆盖工具和参数扰动；
- 动态文档适应、版本化代码生成和工具 schema 鲁棒性在 2025--2026 已有大量近邻；
- 确定性 Schema diff/AST 迁移器可能直接解决生成变换。

只有“显式新旧契约 + 组合依赖变化 + 变换证书 + 最终状态等价 + 未见变化组合”这一窄
交集仍可能存活。若最强确定性适配器在分组 OOD 上达到近饱和，立即 No-Go。它当前只作
后备，不授权读取 NESTFUL 或任何其他数据。

## 5. 条件后备二：部分执行后的最终报告忠实性

问题是：多步工具执行出现成功、失败、补偿和未确认状态时，模型最终是否完整、准确地
报告真正发生的效果。可用不可变事件账本和最终状态机械检查 `committed / failed /
compensated / unverified / not-attempted` 声明，不使用 LLM judge。

它容易形成 EI 评测论文，但当前不作为主线：确定性模板报告器很可能成为完整解法；若
模型只负责自然语言润色，科学问题太弱。它更适合作为首选方向中的“可靠终止/报告”指标，
而不是另一条毕业论文主轴。

## 6. 已淘汰的宽方向

截至本轮近期一手文献审计，以下宽题目不再进入候选池：

- 普通 JSON/结构化输出遵循；
- 一般性的多约束 instruction following、自我修正或动态约束追踪；
- 泛化工具报错恢复、工具选择和何时调用工具；
- 工具输出压缩、序列化格式或表格格式敏感性；
- 一般 RAG 可信性、冲突、引用与拒答；
- 通用代码测试生成、隐藏测试、API 版本迁移和仓库级修复；
- 泛化 LoRA 遗忘、adapter 组合和 instruction data selection；
- 一般异构 GPU 推理调度、量化或模型路由；
- 长上下文中的普通状态覆盖/撤销；
- 单纯将上述问题换到通信、医疗或其他行业场景。

这些方向不一定没有研究价值，但对当前“创新清楚、机械可验证、可扩展成硕士论文”的
要求而言，直接近邻过密或简单基线风险过高。

## 7. 数据边界事件与处置

本轮检索许可元数据时，公开 `AgentAbstain` 数据集卡自动渲染了少量样例行。审计者没有
主动下载、运行、复述或使用这些内容，但这仍属于未计划的研究输入暴露。处置如下：

1. 立即停止访问该数据页；
2. `AgentAbstain` 不得成为本候选的数据、许可依据、设计证据或后续样本来源；
3. 不将任何自动渲染内容写入仓库；
4. 首选候选改为完全自建的形式 DSL 与自有模板，不依赖该来源；
5. future manifest 保持空，不把该事件误写成数据已启动。

这次处置不能证明研究数据已经合格，只证明该偶发来源未被继续使用。

## 8. 当前条件排序与下一道作者 Gate

当前排序为：

1. **动作后结果不确定性下的安全恢复**：条件首选，实际问题和科学差异最清楚；
2. **可认证的组合式工具契约迁移**：数据容易机械化，但与近期工作更近；
3. **部分执行后的报告忠实性**：容易验证，但独立主线和硕士扩展偏弱。

第一项仍不是锁题。下一道作者 Gate 只确认研究载体：作者是否接受把“通用工具型大模型
智能体 + 自建有限状态工具环境”作为实验对象。若不接受，应撤销本排序并重新筛选纯文本、
训练机制或模型系统方向；若接受，下一轮才逐问确认贡献偏好，并对首选做全文级 novelty
复核、无模型生成器协议和 feasibility Gate。`PLAN.md` 在这些问题解决前不得创建。

## 9. 研究载体接受后的全文边界与贡献形态审计

作者已经接受“通用工具型大模型智能体 + 自建有限状态工具环境”作为研究载体。第8节的
载体确认 Gate 因此已经通过，但这不等于题目已经锁定。新一轮审计进一步缩小了可发表
边界。

### 9.1 直接碰撞与不能再使用的创新表述

- [`ReliabilityBench`](https://arxiv.org/abs/2601.06112) 已覆盖 timeout、rate limit、
  partial response、schema drift、故障恢复统计和确定性最终状态 oracle；
- [`FAILING TOOLS`](https://openreview.net/pdf?id=j7YsSnA64D) 已覆盖状态化多域工具中的
  运行时故障、确认调用、retry/fallback、postcondition verification、禁止调用和残余
  不确定性报告；
- [`Atomix`](https://arxiv.org/html/2602.14849) 已直接定义 post-effect/pre-return 故障、
  timeout、duplicate delivery 与 ambiguous retry，并用事务运行时做去重、补偿和
  irreversible-effect gating；
- [`Cordon`](https://arxiv.org/html/2606.17573) 已用 semantic transaction、shadow state、
  effect outbox、idempotency key 和 recovery manifest 延迟或协调外部效果；
- [`ACRFence`](https://arxiv.org/abs/2603.20625) 已处理 checkpoint restore 后重新合成请求
  导致的重复副作用，并提出 replay-or-fork；
- [`ToolGate`](https://aclanthology.org/2026.findings-acl.470/) 已用 Hoare 风格契约验证
  单一 trusted symbolic state 上的工具前置/后置条件；
- [`Fission-GRPO`](https://aclanthology.org/2026.acl-long.1880/) 已训练模型从执行错误中恢复；
- [`Agent-BRACE`](https://arxiv.org/abs/2605.11436) 已做显式 belief 表示与 policy 联合训练；
- [`Tactile`](https://arxiv.org/abs/2607.14443) 已提出 observe--ground--act--verify，并承认
  缺乏可靠反馈时动作可能处于 succeeded/failed/pending 不可确认状态；
- [`Strong planning under partial observability`](https://www.sciencedirect.com/science/article/pii/S0004370206000075)、
  contingent policy graph 和 strong/strong-cyclic model checking 是经典规划问题，
  不是本候选的新算法。

`FAILING TOOLS` 与 `EvoC2F` 的 OpenReview 普通页面受 challenge 限制；本轮边界依据公开
可检索 PDF 正文片段与官方论文元数据，未访问数据页或样例。因而锁题前仍要复核其后续
版本，但该访问限制不恢复已被其他一手工作直接覆盖的宽泛创新表述。

因此不得再声称：首次研究超时后操作可能已生效、首次提出先核对再重试、首次提出
retry/compensate/escalate 动作空间、首次让 LLM 生成恢复方案，或首次使用 belief state
与全分支检查。

### 9.2 最小存活主张

当前只允许保留以下组合主张：

> 对已经外部化、不能被运行时预先暂存或可靠回滚的副作用，响应丢失会形成可见历史相同
> 但 applied/unapplied 隐藏状态不同的 belief set。研究 LLM 能否从自然语言目标、声明
> 工具契约和执行历史提出恢复动作，并用一个免训练 guard 只放行在所有相容世界上保持
> 安全不变量且仍属于获胜策略的动作。

该主张与近邻的边界是：`FAILING TOOLS` 测量一般恢复行为，本候选评价集合世界上的动作
安全；`ToolGate` 维护单一可信状态，本候选在不可信或缺失结果后保留多个可能状态；
`Atomix/Cordon` 通过事务边界尽量在提交前消除风险，本候选只研究已越过该边界或第三方
服务不能纳入事务层的情形；`Agent-BRACE` 学习近似 belief，本候选使用精确有限 belief
提供硬约束。规划与模型检查只作为经典基础，不作为 novelty。

### 9.3 贡献形态决定

| 形态 | 当前判断 | 原因 |
|---|---|---|
| 仅 benchmark/measurement | 偏 No-Go | 与近期通用故障恢复 benchmark 太近，且容易退化为窄 timeout 子集 |
| benchmark + 免训练 verifier/guard | **默认条件 Go** | 同时形成新评价单元、机械真值、可部署安全层和安全—完成权衡 |
| benchmark + 普通 LoRA/SFT | 当前 No-Go | oracle 可精确计算安全动作，普通训练既无保证也没有独立创新 |
| method-first training/RL | No-Go | benchmark 与现象未冻结前先优化方法，且直接近邻过密 |

默认小论文不是“纯 benchmark”，而是 benchmark 提供测量基础，training-free guard 提供主
方法贡献。训练只有在 guard 已经通过、存在多个安全动作、符号成本规则不能选出最优动作、
且两个基础模型在严格 OOD 上留下稳定次优残差时，才可能成为硕士论文扩展；训练模型永远
不得绕过 guard。

### 9.4 最小机械协议

核心环境只需三个接口：`submit(request_id, operation, arguments)`、
`inspect(request_id | resource)`、`finish()`。一次调用可以产生：

- `OK`：动作提交且明确返回；
- `UNKNOWN_BEFORE`：动作未执行但返回 `UNKNOWN`；
- `UNKNOWN_AFTER`：动作已执行但同样返回 `UNKNOWN`。

后两者必须对模型完全同观测。在线 belief 更新只使用可见历史和公开契约。机械 oracle
输出集合标签，而不是唯一轨迹：`unsafe`、`safe_losing`、`winning`、`optimal`。核心只
纳入存在有界 strong policy 的实例；strong-cyclic 依赖弱公平性，必须单列为扩展。
可靠终止要求 belief 中所有可能状态及 pending-effect 闭包都满足安全不变量和目标。

为阻止 `always-inspect`，核心 episode 必须让有限诊断预算在至少两个模糊点之间竞争：
一个动作可用同键重试或后续收敛安全解决，另一个必须保留查询预算。至少30%的决策点应
具有相同最后观测与局部契约、但因历史 belief、未来目标或剩余预算而需要不同最优动作。

### 9.5 第一生死 Gate 与停止条件

任何模型调用前，先验证固定规则：

```text
有可靠 status query -> reconcile
否则操作幂等或有有效同键去重 -> retry_same_key
否则已确认生效且补偿安全 -> compensate
否则 -> escalate
```

以下任一情况成立即 No-Go：

1. 上述固定规则已经 sound and complete；
2. `always-inspect`、`always-retry` 或 `always-escalate` 位于同一安全—完成 Pareto 前沿；
3. 手写 parser + belief planner 在词汇/组合 OOD 上达到95%以上且成本接近 oracle；
4. 在线 guard 需要读取隐藏提交状态、注入器字段或完整离线 oracle 信息；
5. 所有副作用都能被 Atomix/Cordon 风格预提交暂存消除；
6. 同键重试即可解决全部实例；
7. 工具名、描述长度、预算或 `UNKNOWN` 次数等浅层特征可预测动作；
8. 同一状态图、反事实配对、模板改写或轨迹前缀被拆到不同 split；
9. 穷举重放出现任一安全违规或不可终止分支；
10. 新近工作直接覆盖“模糊完成 + belief set + 全世界安全恢复”。

当前研究问题因此是**条件 Go**，不是无条件锁题。下一道作者 Gate 只确认是否接受
“benchmark 作为测量基础 + training-free guard 作为小论文主贡献；训练仅作通过残差
Gate 后的硕士扩展”。确认前不得创建锁定 `PLAN.md`，不得生成 DSL 实例、读取研究样本、
运行模型/API/训练或开展真实实验。

## 10. guard 冗余反证与 B′ 贡献重构

本节由 9.2--9.5 之后的独立只读反证审计触发，并在贡献形态上取代第9节的默认推荐。

### 10.1 新近邻与结构性 No-Go

- [`AgentSpec`](https://arxiv.org/abs/2503.18666) 已提供 LLM agent 的 DSL 与免训练运行时
  约束执行；
- [`VIGIL`](https://arxiv.org/abs/2606.26524) 已把自然语言 skill specification 编译为
  有限 typed trace 上的策略，并用 SMT reference monitor 阻断违规调用；
- [`ToolGate`](https://aclanthology.org/2026.findings-acl.470/) 已做工具契约 pre/post 条件
  与运行时 gate；
- 经典的[`部分可观测 strong planning`](https://doi.org/10.1016/j.artint.2006.01.004)、
  [`runtime shield synthesis`](https://chaowang-vt.github.io/pubDOC/BloemKKW15.pdf) 和
  [`partial-observation shielding`](https://doi.org/10.1609/aaai.v37i12.26723) 已经覆盖
  belief/support 到安全或获胜动作集合的核心机械问题。

若 guard 获得完整 `M,G,B` 与 winning region，它能直接合成安全 contingent controller；
LLM 不再提供保证所需的信息。因此“benchmark + winning-action belief guard”作为新方法
为 No-Go，不得再作为作者确认项，也不得以“LLM 外挂 verifier”的措辞恢复这一 claim。

### 10.2 B′ 的非冗余信息边界

| 组件 | 可见信息 | 禁止信息与输出 |
|---|---|---|
| 环境 | 真实隐藏状态、故障分支、完整 DSL | 只向外返回定义好的观测 |
| LLM | 自然语言目标/工具说明、动作 schema、可见历史 | 不见 gold DSL、精确 belief、oracle 标签或安全动作集 |
| online monitor | 安全契约投影、安全不变量、公开 trace、候选动作 | 不见目标、成本、winning region、隐藏状态；只 allow/block，不推荐动作 |
| offline oracle/evaluator | 完整 `M,G,Φ,c` 与观测关系 | 只离线评分，不向 LLM/monitor 反馈 |

必须设计目标反事实配对：monitor 的安全投影与公开历史完全相同，只有 LLM 可见的自然
语言目标不同，且多个安全动作中任务正确动作互斥。若目标也形式化后交给 monitor，经典
planner 仍可完整求解，LLM 科学问题再次消失。

### 10.3 最小存活贡献与保证范围

主贡献改为**动作后确认丢失的副作用契约语义及其编译器**：明确 ack/commit、幂等键
作用域/有效期、查询新鲜度/完备性、部分提交和补偿前提，并编译成 safety-only、最大许可
的 epistemic monitor。相较 VIGIL 对一个已观测 finite trace 的约束，本候选必须研究一个
可见 history 同时代表多个可能 effect traces/worlds 时的全称安全判定；该差异仍只是待
全文检索验证的条件创新边界，不是已确认的“首次”。

形式 soundness 只相对于忠实、正确且完备的契约和安全不变量成立。monitor 不知道任务
目标，因而不能保证任务完成；LLM 的进展、完成、升级率与成本只能作为经验结果。benchmark
是语义与测量载体，不是独立创新；belief planning、model checking 和 shielding 是经典
实现基础，不得作算法 claim。

### 10.4 小论文、硕士论文与发表路线

- 小论文：契约语义、编译器与 soundness 边界、目标反事实配对、集合型 oracle、独立
  枚举器/符号检查器交叉验证、固定规则与 parser+planner 基线、安全—完成—升级—成本—
  开销评测；不承诺训练；
- 硕士论文：不完备或不确定契约、多个相互依赖外部副作用、组合抽象、反例引导契约修订
  与独立现实语义案例；只有通过残差 Gate 后才研究安全动作集内的策略学习；
- 小论文现实路线是未来一届 IEEE AITest regular，QRS regular 为备选；投稿当年必须按
  官方 CFP 重新核验 EI/Compendex 状态。STVR 类期刊留给具有新组合方法和现实验证的硕士
  扩展，不能把当前合成 wrapper 直接包装成期刊稿。

### 10.5 修订后的硬停止条件与作者 Gate

在第9节停止条件之外，以下任一项成立即 No-Go：

1. online monitor 获得完整 `M,G,B`、winning set/controller 或等价信息；
2. 不存在只对 LLM 可见、会改变多个安全动作间任务选择的自然语言目标；
3. 确定性 parser + planner 在严格 graph/contract/template OOD 上近饱和；
4. safety-only monitor 只能通过接近 `always-escalate` 的拒绝率取得零违规；
5. 环境、标签与 monitor 只由同一 DSL/实现自证，独立枚举器与符号检查器不能交叉一致；
6. 找不到至少两个与正式 API 文档语义相符、又不能被标准事务或同键重试平凡消除的案例族；
7. 新近工作直接覆盖动作后歧义世界集合上的副作用契约编译和最大许可 monitor。

修订后的唯一作者 Gate 是：是否接受“小论文以歧义副作用契约语义与编译器为主贡献，
benchmark 为评测载体，online monitor 只保安全，训练只作通过残差 Gate 后的硕士扩展”。
建议在目标为 EI 最低线时接受；若要求小论文必须训练，应停止本候选并重开选题。作者确认
前不得创建 `PLAN.md`、生成实例、访问研究数据、运行模型/API/训练或开展实验。

## 11. B′ 精确重合反证与 B″ 契约派生变形测试（取代第10节当前判断）

第10节完成后，三路独立只读审查继续检查 runtime verification、部分观测监督控制、
distributed idempotence 与 LLM-agent testing。结论一致：**B′ 作为“新歧义契约语义＋
最大许可 monitor 编译器”的方法论文 No-Go；只保留 B″ 测试路线作为尚未锁定的条件
候选。** 本节取代第10节的当前贡献判断，但保留其信息隔离分析作为审计来历。

### 11.1 为什么 B′ 不是新形式方法

令 `K(h)={s | s 与可见历史 h 相容}`。一步安全许可条件
`Allow(K,a) ⇔ ∀s∈K,∀s′∈Post(s,a):s′∉Bad`，持续安全则在 belief/support 空间求最大
安全不动点。它等价于不确定 trace concretization、部分观测 observer construction 与
permissive supervisor/shield synthesis，不能因使用 `epistemic`、`UNKNOWN_AFTER` 或
LLM 工具术语而变成新方法。

最直接的已有基础包括：Taleb 2024 multi-trace runtime verification、Abstract TeSSLa、
Assumption-Based Runtime Verification、Yin--Lafortune 与 Goorden--Reniers 的部分观测
最大许可监督、POMDP permissive shielding；分布式系统侧的 Fault Tolerance via
Idempotence、Flux、Rainmaker、FoundationDB `commit_unknown_result`、RIFL、Saga/LRA
已经覆盖响应丢失、重复执行、幂等键期限、完成记录、补偿与恢复；Atomix 又把
`post-effect/pre-return` 明确带入 LLM agent。因而 contract compiler 与 monitor 只能是
oracle、生成器或经典基线，不能作为 novelty。

### 11.2 B″ 的科学问题与真正的 metamorphic relations

B″ 不研究“怎样再发明一个 planner/guard”，而研究：

> 能否从有副作用工具的形式契约机械合成 metamorphic relations，以检测 LLM agent 在
> 回包丢失后对幂等保证、查询证据、补偿前提、目标变化与语义保持改写是否作出符合
> world-uniform safety 的关系型反应？

不可见的 applied/unapplied 两世界对 agent 输入完全相同时，只构成集合型 oracle，不构成
MR。有效 MR 必须改变可见输入并给出可证的动作集关系：belief 扩大时安全集不增；可靠证据
缩小 belief 时安全集不减；加入/删除有效同键幂等保证时同键重试的安全性按方向改变；加入
sound/complete/fresh readback 时可恢复集合扩展；语义保持改写与图同构保持规范化动作类；
仅改变用户目标时安全集不变、任务最优集改变。

### 11.3 最小定理、artifact 与对照

最低论文包必须同时包含：

1. 集合型 oracle soundness，以及每类 MR 的 equality/inclusion soundness；
2. 对预先定义的一阶契约缺陷类，MR suite 的 mutation adequacy/completeness；
3. 自建 DSL/解释器、观测等价世界与 MR 生成器、F2 fault injector、独立显式枚举器和
   独立符号 checker；
4. 覆盖 unknown-as-failure、key expiry、wrong key、stale/incomplete query、unconditional
   compensation、false success report 的 mutant library；
5. 在全部有界可达历史上验证 oracle/MR 零假阳性，并比较单实例 oracle、随机配对、普通
   trace check 的 mutation score；
6. cascade rule、确定性 parser+planner、结构化契约+exact shield、always-escalate/query/
   retry 基线；后续经单独授权才可加入多模型 paired evaluation。

主要指标是 world-uniform violation、safe completion、escalation、unnecessary block、
tool cost、MR consistency 与 mutation score。monitor 可作为防护对照，但“拦截后形式违规
归零”是定义结果，不是论文创新。

### 11.4 小论文到硕士论文

小论文按未来 AITest/QRS regular 所需的测试方法完整度设计，主贡献限定为契约派生 MR、
变异充分性边界、机械 oracle 和可复现工具。不能预先保证未来届次 EI 检索，投稿时必须
核验官方出版与索引状态。硕士论文再扩展多副作用组合、不完备契约、反例引导生成与测试
优先级；只有严格语义 OOD 下仍有不能由确定性 parser/cascade/exact planner 消除的稳定
残差，训练才有科学必要性。

### 11.5 外部全文 Gate 与硬停止条件

[AITest 2026 官方录用页](https://cisose.fit.ac.jp/aitest/index.php/accepted-papers-2/) 已列出
三篇标题级高危近邻：

- *Metamorphic testing of multi-agent LLM systems: A trace-based behavioral oracle framework*；
- *Deterministic behavioral contract testing for AI features at the browser layer*；
- *Formal trajectory analysis for testing agentic AI in stateful environments*。

[官方日程](https://cisose.fit.ac.jp/aitest/wp-content/uploads/2026/07/AITest_tentative_program17_07_2026.pdf)
确认它们在 2026-07-27--28 报告；本审计日期为 2026-07-19，尚未检索到全文。因此这只是
标题级碰撞风险，不能推断其具体方法，也不能宣称 B″ 的全文创新边界已经完成。全文公开后
若直接覆盖本节的状态型 agent、自动契约 MR、world-uniform oracle 与 mutation adequacy，
立即换题。

其他 No-Go：cascade/parser+planner 近似 oracle；MR 不比单实例/随机/trace check 多杀
mutant；MR 没有可见变换与非平凡输出关系；always-escalate 无安全进展 headroom；找不到
至少三类现实契约族；两套 oracle 不一致；错误仅是一轮 NL→DSL 解析；或 compiler/monitor
主张重新出现。

当前作者 Gate 是是否接受 B″ 及其“近邻全文直接重合即换题”条件。确认前不锁题、不创建
`PLAN.md`/`PLAN-REVIEW-LOG.md`，不生成研究实例，不访问研究输入，不运行模型、API、训练、
容器或真实实验。

## 12. B″ No-Go 与 B‴ 契约语义义务覆盖（取代第11节当前候选判断）

第11节之后的全文审计发现三组决定性的组件级碰撞，故 B″ 不再是条件候选：

1. [Rainmaker](https://www.usenix.org/conference/nsdi23/presentation/chen-yinfang) 的
   P1/P2/P4 已在请求生效后延迟/抑制响应使客户端超时，并以 bug taxonomy、四种 injection
   policies 和 call-site metrics 覆盖重试、重复副作用与 state divergence；它仅处理单个
   REST interaction 及 SDK retries，不编码恢复契约或 world-uniform oracle；
2. 未经同行评审的技术报告 [AgentAssay](https://arxiv.org/html/2603.02601) 已提出统一
   agent behavioral contracts、state/boundary coverage、agent mutation score/adequacy 与
   四类 agent MRs；其 coupling/adequacy 效力仍须独立复现；
3. [SGVEF-LOOP](https://aclanthology.org/2026.acl-long.1224/) 已对 MCP agents 自动合成
   静态知识约束的同意图/预期轨迹语义改写 pairs 并做 coverage-guided topology exploration；
   其公开贡献未定义副作用歧义、恢复契约或 mutation adequacy。

ReliabilityBench、StateGen/StateEval、Executable MRs、ARMeta 与 MR-Coupler 又分别覆盖
Action MRs + fault injection、FSM 顺序 API 测试 + 状态 oracle、specification-to-MR、
OpenAPI-to-MR 与 MR mutation validation。因而“动作后歧义 MR 生成、agent mutation
adequacy 或 response-loss coverage”都不能作为主创新。

这些是组件级重合，不代表单篇先例完整实现 B″；B″ 的否决还依赖下一段的内部 oracle/MR
冗余，不能把组合碰撞夸写为精确全文重合。

更关键的是，若每个输入已有精确 `Safe(K)` oracle，单个动作成员检查通常已能发现安全
错误；两个安全集合之间的 inclusion 不自动约束两个单选 agent 输出。若 MR 不比两个单例
oracle 多检出或多定位问题，它只是在重复 oracle。因此 B″ 判 No-Go，MR 降为可选诊断工具。

### 12.1 B‴ 的可证伪科学问题

B‴ 暂定为“契约派生的 atomic ambiguity-obligation coverage + sampled world-uniform
policy checking”。它问：现有 call-site、transition、final-state 与 Action-MR criteria
即使达到各自的高 coverage，是否仍会漏掉“同一观测对应不同隐藏副作用、不同世界诱导
冲突恢复动作”的缺陷；若会，一个契约语义 criterion 能否在等预算下稳定增加检出率？

生成前冻结有限 contract/state/action 与可达深度 `B`；独立 defect universe `D` 另行冻结，
在全部有界可见历史上规范化动作分布相同的 defects 视为等价并删除。`D` 与 generator
必须分开实现。对 `W_C(h)` 中所有观测等价世界，定义 `A_all=∩ Safe(w)`；再对具体动作 `a` 选择
`w_safe,w_unsafe`，使 `a` 在前者安全而在后者不安全。原子 obligation 为：

`<前缀ρ, 可见历史h, 动作a, w_safe, w_unsafe, capabilityγ>`。

`covers(t,o)` 要求 `t` 精确实例化 `ρ/h/γ` 与两个世界，并以显式 candidate-action probe
将 `a` 交给独立 oracle 验证安全/不安全分裂；每个 `(t,a)` 是原子 probe，一个动作不能替
其他动作增加 coverage。`AO-Cov(T)` 是与 defects 无关的有限 `Ω(C,B)` 中已覆盖 obligations
比例；目标模型质量与 `D` 的 kill 另算。

capability profile 必须区分 key 的 identity/scope/expiry、readback 的
sound/complete/fresh/correlated，以及 compensation 前置条件。主 universe 每个 obligation
必须有 `A_all≠∅` 且至少一个经独立进展 oracle 证明的非 escalation 安全推进动作；只能升级
的类单独报告，不进入主 coverage/kill 分母。安全、进展与成本保持三个 oracle。

随机 LLM 从固定前缀独立重启，只估计该前缀违规率；轨迹违规率必须用完整连贯 rollout
估计，不能拼接各前缀样本。二者均报告 95% 区间，采样量由预注册效应与错误上限决定。
因此方法是 sampled multi-step policy checking，不是完整 policy verification。

### 12.2 最低定理、artifact 与实验增量

最低方法包是：有限 scenario/oracle label soundness；定义 defect 等价并给出非循环的
相对 adequacy——obligation/covers 不含 `d`，另证每个 `d` 会在某个已覆盖 `h` 选择对应
不安全动作并被实际运行杀死；证明
Rainmaker `P1--P4 × call-site` 与普通 transition coverage 不蕴含 B‴ coverage 的严格
counterexample；contract/interpreter、场景生成器、coverage calculator、独立枚举 oracle、
独立符号 checker、fault injector 与 policy mutants。

主实验必须在相同 agent executions 与归一化 token 上限下比较 Rainmaker-style policies、
ReliabilityBench Action MRs、AgentAssay-style prioritization（不宣称其经验 state score 存在
固定满覆盖分母）、SGVEF/StateGen transition coverage、单世界/终态 oracle、随机语义对和
确定性 recovery cascade；oracle/world replay 成本另报。主 Gate 是相对最强基线新增至少
一个独立 defect class、kill 绝对提升至少10个百分点，且 contract/defect-cluster paired
bootstrap 95% 区间下界大于0。无模型 power analysis 若不能识别该阈值，先停题。实际模型
的前缀/轨迹违规率、safe completion、escalation、false positive 与成本均单独报告。

### 12.3 小论文、硕士扩展与停止条件

小论文只做 criterion、边界定理、可复现工具与跨至少三类现实契约的增量验证。硕士论文
扩展多个同时未决效果、契约不完整、组合 coverage、partial-order reduction 与 test
selection。只有无模型 cascade/parser/exact planner 后仍有稳定模型语义残差，才允许用
coverage witnesses 做 curriculum、LoRA 或 verifier-guided preference training。

No-Go 包括：退化为 response-timeout/call-site 注入；相同预算无新增 kill；只测试 oracle/
compiler；相关多调用没有新缺陷；现实契约不足三类；找不到足量原子 safe/unsafe split；
`Ω_progress` 不能保证非 escalation 安全推进；双 oracle 不一致；或共享实现循环自证。

AITest 2026 三篇高风险近邻已由官方录用页和日程确认为 Full Papers，但截至 2026-07-19
仍没有可核验全文/摘要/DOI。NetAgentBench 是 Twabi--Ding--Kondo 团队独立的 ICCCN 论文，
可证明 FSM/stateful trajectory/idempotent replay 已被占据，却不能替代 AITest 全文。
全文若覆盖 B‴ 的 observation-equivalent effect-world obligations、sampled world-uniform policy
checking 与相对 coverage 增量，立即换题。

当前 Gate 只问作者是否接受“B″ No-Go / B‴ 条件候选 / 严格增量失败或全文重合即换题”。
确认前不锁题、不创建计划终稿、不生成研究实例、不访问研究输入、不运行模型或实验。

## 13. B‴ 方法 No-Go 与候选 C 契约合法性翻转训练（取代第12节当前候选判断）

作者接受第12节的停止条件后，继续完成了经典测试理论、分布式故障恢复和近期 agent
evaluation 的三路只读反证。结论是：**B‴ 不能作为新的通用 coverage/adequacy 方法。**

### 13.1 B‴ 的条件性归约与适用边界

[Complete Requirements-based Testing with Finite State Machines](https://arxiv.org/abs/2105.11786)
在确定性 FSM 中把原子需求表示为参考状态、输入和允许输出集合；[n-Complete Test Suites for IOCO](https://link.springer.com/article/10.1007/s11219-018-9422-x)
在实现状态数有界、公平执行等条件下，对含 I/O、quiescence 与 compatible states 的
suspension automata 给出 n-complete ioco test suites；[Timed Testing under Partial Observability](https://vbn.aau.dk/da/publications/timed-testing-under-partial-observability/)
在其 test-purpose/conformance 设定中使用隐藏状态集合和 observation-based strategies；
[Require, Test, and Trace IT](https://link.springer.com/article/10.1007/s10009-016-0444-z)
从需求契约生成 mutants，并只对能导致可控 forbidden behavior 的可区分 modeled faults
寻找 witness。它也会遇到 equivalent/unproductive mutants，保证受确定性 SUT 与冻结
fault model 限定，不能外推为一般缺陷缺失。

这些文献本身没有无条件证明 B‴ 被完整包含。它们给出结构最接近、必须比较的形式基线：
只有另证 belief/information-state 的忠实有限编译并满足各自假设，B‴ 的结构部分才可视为
“信息状态、输入、允许输出”的领域实例；`A_all=∩Safe(w)` 也只能先视为有直接部分可观测
基线的候选 oracle。故 B‴ 不能把该结构、有限 fault model 或 mutant kill 本身声明为新一般
理论，但 No-Go 不是“既有文献已经严格 subsume 随机 LLM policy”的无条件定理。

动作后歧义本身也有直接先例。[Rainmaker](https://www.usenix.org/system/files/nsdi23-chen-yinfang.pdf)
注入请求生效后响应延迟至客户端 timeout；[RIFL](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/126-lee-online.pdf)
用唯一 RPC identity、持久 completion record 与 lease/GC 处理 lost reply 和 retry dedup；
这为 request identity 与 completion-record lifetime 提供具体先例，但不等同于一般 API
idempotency-key 的全部 scope/expiry 契约。Chain Replication、FATE/DESTINI、
Filibuster、Flux 与 ExoFlow 已覆盖 readback-before-retry、恢复规范、多 RPC 相关故障、幂等
与补偿。[Near-Miss](https://aclanthology.org/2026.gem-main.30/) 又已识别 mutating trajectory
中“最终结果正确但未做必要检查”的 latent policy failure。

即使没有这些外部碰撞，B‴ 仍有内部 No-Go：只要 `A_all(h)` 可精确计算，单历史成员检查
就能判定 agent 动作；safe/unsafe world pair 可能增加解释，却不增加检测。故第12节要求的
“相对单实例 oracle 严格新增 kill”没有方法层先验支撑；上述 formal testing 是在各自有限/
状态有界假设下必须面对的归约目标。B‴ 只剩一个窄的 acknowledgement-loss empirical
benchmark 空隙，不能
再称新 coverage theory。本审计按已接受停止规则结束 B‴ 的首选资格。

### 13.2 候选 C 的可识别最小科学问题

候选 C 暂名 **Same Tool, Changed Contract: Counterfactual Pair Training for
Contract-Conditioned LLM Tool Agents**。它不再研究隐藏世界覆盖，而研究一个直接可观察、
可训练和可证伪的行为问题：当前工具契约已改变时，模型是否仍输出只符合旧契约的判断。
工具身份与 schema 保持稳定，契约字段是唯一受控变化；契约 token 必然变化，因此输出差异
只能证明 observable contract-conditioned compliance，不能识别模型内部是否“真正依赖”
某个因素或给出因果机制结论。

决定性最小 pair 改为：

`(x,c0,a_w,L0)` 与 `(x,c1,a_w,L1)`，且 `L0≠L1`。

`x` 固定任务、工具身份、参数 schema、环境状态和完整可见历史；`c0/c1` 只改变一个明确
呈现给模型的契约原子；`a_w` 是冻结规范化动作类中的同一 witness action；
`L∈{permitted,prohibited}` 只表示它在冻结的一步决策边界内是否被可执行契约许可。独立
checker 必须证明标签翻转。这不把 `a_w` 称为唯一最优动作，也不排除 query、escalate、no-op
在两边共同合法。若以后评价完整 policy，必须先另行冻结目标、时域、进度/成本、fallback
规则和动作等价关系。等价 controls 只改变同义措辞、字段顺序或无关条款，并要求同一规范化
动作的合法性判断稳定，而非原始文本行为完全相同。研究问题是训练能否提高这种决定性更新
与等价变化稳定性，并进入 tool-family 与 contract-composition OOD。

### 13.3 已占据边界与待反证的领域创新假设

- [GuideBench](https://aclanthology.org/2025.acl-long.557/) 已评测频繁更新的领域 guidelines；
- [RoTBench](https://aclanthology.org/2024.emnlp-main.19/) 与 ToolEVO 已覆盖工具名、参数、
  response format、弃用和噪声下的工具适应；
- [Analyzing and Internalizing Complex Policy Documents for LLM Agents](https://aclanthology.org/2026.acl-long.767/)
  已提供可控 policy 环境生成、合成数据与 policy continued pretraining；
- [ToolAnchor](https://arxiv.org/abs/2607.14145) 已用 counterfactual anchor contexts 和
  post-training 缓解扩展工具集时的 behavioral inertia；
- [TicToc](https://arxiv.org/abs/2510.23853) 已测并训练时间新鲜度下的调用决策；
- Guidelines as Environments、Contract2Tool 与 ContractBench 分别占据因果规则世界规划、
  契约学习和 observation-contract 检查；
- [CounterComp](https://aclanthology.org/2023.acl-long.834/) 已把 counterfactual compositional
  contrast、metric learning 和 unseen-domain/composition OOD 结合；
  [PairCFR](https://aclanthology.org/2024.acl-long.646/) 已用成对最小标签翻转数据和 contrastive
  learning 提高 OOD；[Inverse IFEval](https://openreview.net/forum?id=sTwMHXReLc) 已直接测量
  模型克服训练惯性、服从与既有模式冲突的当前指令。

因此“tool drift benchmark”“规则更新”“counterfactual data”“普通 SFT/DPO”、pair flip、
invariance/contrastive objective 与 compositional OOD 均不能单独作创新。C 目前只剩待全文
反证的工具契约领域假设：**稳定工具身份/schema 与历史，单一可执行契约原子干预，同一
规范化 witness action 的机械合法性翻转，以及向独立真实版本化契约变化的迁移。** 若它
相对上述方法、GuideBench 和 AgentAssay/TSCG/PA-Tool 等 agent 近邻没有工具契约特有增量，
就只是既有反事实训练的领域实例。

### 13.4 数据、机械标签、基线与递进

当前只设计协议，不授权生成。题目确认本身也不授权任何生成或数据使用。未来只有作者另行
签署 acquisition/data-use 授权且 canonical manifest 明确改为 authorized 后，数据才可由
完全自建有限状态 contract DSL 产生；现实 API 文档只可在许可与 manifest 单独批准后用作
mutation taxonomy 和外部迁移来源，不替代机械标签。

首篇只保留两类主干：

1. idempotency：结果不明后可同 key 重试，或必须先 query/reconcile；
2. atomicity/partial commit：可整体重试，或必须核对已提交部分并补偿。

freshness 只作迁移轴。建议 8--12 个工具族；按基础语义模板、工具族和契约组合封闭划分，
所有改名、措辞、排序和随机派生留在同一 split。生成器与枚举/符号 checker 独立实现。
测试必须含 unseen tool family、unseen wording 和 unseen two-clause composition；多个自建
领域包装不能充当现实性证据，还必须预注册一个与合成模板 lineage 独立的真实、版本化契约
变化迁移集，其获取另需授权。

强基线为 prompt-only、契约显式重读、关键词/位置规则、deterministic parser+exact planner、
等样本等 token ordinary SFT、standard DPO、CounterComp/PairCFR 类目标、shuffled-pair
SFT/DPO、oracle 上界，以及标准 tool-calling 保持集。主要指标先限定为 witness-legality
flip accuracy、equivalent-contract judgment consistency、两类 OOD 和基础能力保持率；完整
agent 动作指标要等目标/时域/成本被另行冻结。

EI 小论文若 Gate 通过，暂定贡献只能是可执行工具契约干预生成器、固定动作合法性机械
oracle、pair-level protocol 与真实版本变化迁移证据。训练目标只有在相对 CounterComp、
PairCFR、普通 SFT/DPO 和 shuffled pairs 的严格增量成立后才能成为方法贡献。LoRA 只是
实现手段。硕士论文再做契约代数、多条款组合、隐式漂移检测、持续/在线适应及参数训练与
runtime enforcement 的比较。

### 13.5 C 的硬停止条件与当前 Gate

以下任一项成立即 No-Go：同一 witness action 的合法性不能由契约机械翻转；关键词/动作
位置或规则 parser 在严格 OOD 上近饱和且训练无额外组合泛化；候选方法不优于等预算
ordinary SFT/DPO、CounterComp/PairCFR 类目标或 shuffled pairs；收益只在 IID；只有
freshness 产生效果；标准工具能力明显下降；不能在独立真实版本化契约变化上迁移；与
GuideBench、Inverse IFEval、AgentAssay/TSCG/PA-Tool 等全文重合；或方法只是已有反事实
训练的工具契约包装。

当前唯一作者 Gate 是是否接受“B‴ 方法路线正式退出，C 仅以稳定工具身份/schema、单条款、
固定 witness 动作合法性机械翻转 + 可观察服从/OOD 作为待反证候选”。本次题目确认也不构成
数据或生成授权。确认前不锁题、不创建 `PLAN.md` 或 `PLAN-REVIEW-LOG.md`，不生成实例，
不访问研究输入，不选择模型，不运行 API、训练或实验。
