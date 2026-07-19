# 未来研究方向 v0.1：反事实证据一致性训练与风险可控补丁验证（历史候选）

日期：2026-07-18

状态：`SUPERSEDED_BY_2026-07-19_DIRECTION_AUDIT / HISTORICAL_ONLY /
DO_NOT_EXECUTE`

> **权威状态更正（2026-07-19）：** 后续近期创新边界、数据可得性、标签可识别性和
> 通信工程契合度审计已撤销本文件的 `DIRECTION_SELECTED` 结论。本文件只保存 2026-07-18
> 的候选设计与决策来历，不再是未来研究方向或执行权威。不得据此枚举/采集数据、读取
> 研究输入、选择模型或 prompt、运行训练/评估/API，或形成论文效果 claim。当前状态、
> 两个条件候选和下一项作者决策以 `docs/plans/current_plan_zh.md` 的 0.69 节为准；逐问
> 对齐与独立对抗审查完成前没有锁定题目。

## 1. 决策结论

结合作者的通信工程硕士学位、大模型研究方向、最低 EI 检索要求，以及
4 张 A6000 和 3 张 RTX 3090 的本地资源，后续研究主线选择为：

> 面向代码补丁验证的反事实证据一致性训练与风险可控决策。

小论文工作题目为：

> *Counterfactual Evidence-Consistent Training for Risk-Aware LLM Patch Verification*

毕业论文工作题目为：

> 面向大模型智能体的多源证据可靠性建模与成本感知主动获取方法研究。

二者是一条连续主线。小论文研究静态证据融合与选择性放行；毕业论文新增不确定性
风险控制、序贯证据获取、真实成本和跨场景验证。毕业论文不能仅把小论文增加样本或
模型后重复发表。

本文件选定问题域、候选方法边界和研究阶梯；准确的创新实现仍须通过 G0 系统性
novelty Gate，当前不得声称已经冻结或首次提出。本文不授权数据访问、训练、验证、
模型调用或论文效果结论。规范未来研究 manifest 继续保持空且 `not_started`。

## 2. 第一性原理问题定义

给定任务描述与候选补丁 `x`、一组模型可见证据
`E={e_1,...,e_k}`，以及只供训练或事后评价使用的隐藏二元正确性标签 `y`，模型输出
可校准的正确性概率 `p(y=correct|x,E)`。`accept / reject / escalate` 不是三个天然
真值类别，而是由 development split 上预先冻结的高、低两个概率阈值导出的决策动作。

每条证据至少具有五个相互区分的属性：

1. `direction`：支持、反驳或不确定；
2. `diagnosticity`：按预注册的行为覆盖/区分规则，预期能否区分正确补丁与
   plausible-but-incorrect 补丁，而不是由测试标签事后指定；
3. `reliability`：来源和生成过程是否可信；
4. `dependency`：是否与其他证据重复、相关或共享同一失败来源；
5. `cost`：运行时间、显存/计算、外部调用或人工成本。

“更多证据”不构成科学命题。独立且有诊断性的支持证据才应增加正确补丁的接受
概率；有效反证应降低接受概率；重复证据不应被机械累计；未被可靠证据消解的冲突或不足
通常应削弱置信度，但不能按类别直接指定 `escalate`。最终动作仍由校准概率和阈值导出。
主要目标是在固定自动放行覆盖率下最小化错误接受风险，而不是最大化接受率。

该形式化与通信工程的联系是多源含噪信息融合、可靠性估计、不确定性决策和资源约束，
不是把软件证据比喻成“信道”。补丁验证是第一个具有可执行隐藏标签的受控应用。若学院
或导师要求直接通信场景，毕业论文扩展阶段再增加网络配置变更验证、网络故障诊断或协议
行为验证；小论文不同时引入第二场景，以免无法归因。

## 3. 小论文科学问题与可证伪假设

### RQ1：证据数量偏差

在补丁、token 数量、证据顺序和解码配置受控时，基础模型能否区分独立诊断证据、
低诊断性证据、重复证据、噪声证据和冲突证据？

### RQ2：反事实一致性训练

相比相同 backbone、数据、token 和训练步数的普通 LoRA-SFT，反事实证据一致性训练
能否在固定自动放行覆盖率下降低错误接受风险？

### RQ3：项目外与时间外泛化

该改进能否保持在未见项目、未来时间窗口及第二个独立模型家族上？

### RQ4：增量机制

改进是否来自反事实训练，而不是普通微调、post-hoc calibration、更长输入或更高
`escalate` 比例？

预期假设只有在以下条件同时满足时才被支持：

- 诊断证据产生的标签一致 logit 更新显著大于等 token 的重复/无关证据；
- 所提方法在预注册覆盖率上的错误接受风险低于普通 SFT；
- 对重复和无关证据的错误置信漂移更小；
- 结果在预注册的项目外测试与第二 backbone 复现中成立。

若只能通过几乎全部 `escalate` 降低风险、只改善总体 accuracy/F1、或最简单规则/校准
基线取得相同结果，则核心方法假设失败。

## 4. 小论文最短方法

小论文只引入一个候选训练创新变量：反事实证据排序约束。训练目标为：

```text
L = L_correctness + lambda * L_counterfactual_ranking
```

- `L_correctness`：使用训练集隐藏二元标签 `y` 的正确/错误概率损失；
- `L_counterfactual_ranking`：只使用预注册且具有明确期望关系的同补丁证据对。诊断
  证据状态应比等 token 的低诊断性/无关状态给真实类别更高的对数概率；精确重复和
  语义冗余对施加近似不变约束。不能把所有冲突证据笼统标为 `escalate`。

选择性阈值与 calibration 只在 development split 冻结：高于上阈值为 `accept`，低于
下阈值为 `reject`，中间为 `escalate`；主比较固定预注册的 `accept coverage`（自动
放行率），并另报总自动决策覆盖率、拒绝率和升级率，不能把升级动作当作监督真值。
不额外堆叠图神经网络、多专家、完整贝叶斯网络、多智能体、DPO/RLHF 或在线强化学习。
主动工具规划和新测试生成明确留到毕业论文扩展。

## 5. 全新数据与证据干预

数据单位是独立的 `issue--candidate-patch` 组，不是证据变体、模型调用或随机重复。每组
需要正确候选和至少一个 plausible-but-incorrect 候选，并在模型不可见的 evaluator-only
边界下建立正确性标签。

每个任务至少形成以下配对证据状态：

1. 独立且有诊断性的真实证据；
2. 真实但低诊断性的证据，包括覆盖不足但执行结果真实的检查；
3. 精确重复或语义冗余证据；
4. 自然工具失败、结果损坏、过期输出等不可靠证据；
5. 有效但相互冲突或不足的证据。

人工构造只用于控制干预，不能成为唯一噪声来源。四个构念必须分开：真实性/可靠性由
来源与执行完整性定义；支持/反驳方向由工具实际结果定义；诊断性由预注册的行为覆盖与
区分规则定义；最终类别方向才由训练集隐藏二元标签 `y` 监督。不得根据模型最终答案
反推任何证据属性，也不得用测试集 `y` 构造测试证据属性。所有条件 token-matched；
有/无工具最终 verdict 必须作为独立消融，防止标签线索泄漏。

数据必须来自隔离注册表之外的全新项目和任务。训练、开发和测试按项目与时间双重隔离；
同一 issue、补丁谱系、派生证据及生成代理风格不得跨 split。标签不能仅由“通过原测试”
或“与开发者补丁相同”决定，应结合完整回归、定向/差分测试及对无法自动判定项的独立
复核。

## 6. 样本量确定规则

本计划不拍脑袋指定任务数，也不继承旧研究的效果量、项目数或停止规则。样本量按以下
顺序确定：

1. 先完成只定义来源范围、允许字段、纳入/排除规则和验收条件的 source-feasibility
   协议设计；此步不枚举、下载或读取项目/任务内容；
2. 在任何新来源访问前，另行实现并审计一个 fail-closed 的
   `source_acquisition_authorization` 机制。它不同于规范 scientific-use manifest；作者
   签核的授权必须绑定确定性来源/查询/时间窗、允许字段、隔离 staging namespace、记录/
   字节上限和旧内容碰撞检查，并且只允许纯机械采集。当前仓库尚无已激活的该授权；
3. 只有第2步通过后，采集器才可按预声明规则自动枚举、机械下载并哈希到隔离的
   future-study staging。该阶段不得输出语义内容，不得人工筛选，不得建立 source frame，
   也不得做环境/标签试验、进入 loader、选模、分析或训练；
4. 使用 staging 中已经存在的精确文件创建当前 validator 可接受的非空、hash-bound
   development-feasibility 规范 manifest，再由作者二次签核并验证。只有该 Gate 通过后，
   才允许读取内容、建立 source frame 和开展 feasibility 科学使用；
5. 在该受限科学使用授权下建立与确认性测试隔离的 feasibility cohort，估计环境复现率、
   候选产出率、配对 discordance 和项目内相关性；
6. 根据可接受的错误放行上限和最低自动覆盖率定义最小有意义效应，不从 feasibility
   结果挑选容易显著的阈值；
7. 以项目为 cluster 做 Monte Carlo power simulation，固定 `alpha=0.05`、power 不低于
   `0.80`，并根据资格率反推原始任务需求量；
8. 在训练前重新冻结训练/确认性 RQ、数据、split、模型与样本量绑定，生成对应的规范
   manifest 和新的作者签核；
9. 若预声明来源不足以满足功效要求，只能在训练前按协议扩展来源并重新签核；不得在
   查看测试结果后追加样本。

训练集使用冻结窗口内全部合格训练任务，并报告预注册的 learning curve。测试任务数而非
证据变体数或模型调用数是独立样本量。

## 7. 模型、资源与对照

小论文使用两个不同家族的开放权重 7B--8B 代码模型：第一 backbone 用于方法开发，协议
冻结后在第二 backbone 上复现；每个主配置至少三个随机种子。具体模型只能依据许可、
logits 可用性、LoRA 支持、上下文要求、发布日期与预训练数据边界等预注册条件机械选择，
不能在看见任务结果后挑模型。

- 4 张 A6000：LoRA/bf16 主训练、批量推理和主要消融；若预注册的显存 dry-run 失败，
  才能按预先规定条件改用 QLoRA；
- 3 张 RTX 3090：数据验证、容器测试、基线推理和独立评价；
- 不把 A6000 与 3090 强行组成一个异构同步训练任务；
- 14B/32B 只作为毕业论文扩展，不从零预训练、不做 70B 全参数训练。

最小对照为：

1. tool-only 与证据计数/规则融合；
2. 冻结基础模型 zero/few-shot；
3. 相同数据与预算的普通 LoRA-SFT；
4. 普通 SFT + post-hoc calibration；
5. 所提反事实排序 LoRA。其 `lambda=0` 配置就是第3项普通 LoRA-SFT，不重复伪列为
   另一项消融。

所有学习方法共享 backbone、训练数据、训练 token/step、解码和测试预算。不能用更多训练
数据、更长上下文或更多人工审核替代方法贡献。

## 8. 指标与统计

主指标：

- 预注册固定 `accept coverage`（自动放行率）下的错误接受风险；
- selective risk 与 risk--coverage curve / AURC；
- accepted precision、correct recall 和人工审核比例；
- paired counterfactual evidence sensitivity；
- 重复/无关证据导致的 confidence drift；
- 工具基线错误 opportunity set 上的严格纠错率。

次指标包括 Brier score、log-loss、ECE、MCC、balanced accuracy、AUROC，以及跨项目和
跨时间性能下降。统计单位是任务；配对比较按任务完成，并用项目级聚类/层次 bootstrap
反映同项目相关性。不得把多模型、多证据状态或多随机种子视为独立任务扩大样本量。

## 9. 最近邻工作与创新边界

- [ComPass](https://arxiv.org/abs/2602.07561) 已用代码变换、对比学习和二分类器进行
  APCA；本研究不能把“一般对比学习补丁分类”称为创新。
- [RePaCA](https://arxiv.org/abs/2507.22580) 已用 GRPO 微调推理模型做静态 APCA；本研究
  不能把“训练推理模型判断补丁”称为创新。
- [Fine-grained calibration for automated code revision](https://arxiv.org/abs/2604.06723)
  已研究代码修订置信度校准；本研究不能把 post-hoc calibration 或 abstention 单独称为
  创新。
- [Abstain and Validate](https://conf.researchr.org/details/icse-2026/icse-2026-software-engineering-in-practice/9/Abstain-and-Validate-A-Dual-LLM-Policy-for-Reducing-Noise-in-Agentic-Program-Repair)
  已研究 agentic repair 的 abstention 与 patch validation；本研究必须证明证据结构训练的
  增量机制。
- [UTBoost](https://arxiv.org/abs/2506.09289) 与
  [PatchDiff study](https://arxiv.org/abs/2503.15223) 表明测试通过仍可能放过错误补丁，
  支撑可靠证据选择的应用需求，但不证明本方法有效。
- 通用 noisy/conflicting RAG 已有
  [Why So Gullible?](https://aclanthology.org/2024.findings-naacl.159/)、
  [CARE-RAG](https://arxiv.org/abs/2507.01281) 等工作；因此本研究不以“通用噪声 RAG
  融合”作为新颖性声明。

当前候选创新点严格限定为：在同一补丁、等 token 的反事实证据干预下，学习对证据边际
诊断价值的方向一致更新，并在固定自动覆盖率上控制错误放行风险。这里仍是初步新颖性
边界，不得在完成系统性检索和逐项对照前声称“首次”。

## 10. 投稿与毕业论文阶梯

小论文以可归档、当届确认进入 EI Compendex 的国际会议论文为最低目标，优先选择软件
测试、验证、软件可靠性或可信大模型方向。IEEE ICST 类会议是主题适配参考，不代表未来
某届已保证 EI；具体会议和 track 只依据当届官方 CFP、页数、归档与检索状态选择，不能
为了截止日期改动已看到结果后的科学设计。

毕业论文形成以下递进：

1. 问题建模与全新证据干预协议；
2. 小论文：反事实证据一致性训练与项目外风险评价；
3. 区分模型不确定性和证据不足，引入预注册的风险控制方法；
4. 学习下一项证据的预期风险下降/真实成本，形成成本感知主动获取与停止策略；
5. 扩展到更多语言、工具失败、分布漂移及必要的通信网络验证场景；
6. 综合系统评价、适用边界与失败条件。

主动阶段先比较全部工具、固定流水线、随机、最便宜优先、手工启发式、LLM 直接规划与
贪心价值/成本策略；只有贪心策略确实不足且存在可复验的序贯依赖时，才考虑 contextual
bandit 或 offline RL。

## 11. 执行 Gate 与停止条件

1. `G0 novelty`：完成系统性近期文献检索和逐项 novelty matrix，专门核对证据层
   反事实训练、等 token 配对、重复不变性和固定覆盖率风险目标是否已被最近邻组合覆盖；
   未通过时修改候选方法，不接触研究数据。
2. `G1 feasibility protocol`：只设计来源、允许字段、纳入/排除、环境/标签验收和停止
   规则，不枚举、下载或读取项目/任务内容。
3. `G2 acquisition bootstrap`：在单独审计的变更中实现上述 acquisition-only 授权机制；
   作者签核后，只允许采集器按确定性规则枚举、机械下载、哈希和旧内容碰撞检查到隔离
   staging，禁止语义输出、人工筛选和任何科学使用。该 Gate 未实现并通过前不得访问来源。
4. `G3 feasibility authorization`：由 G2 staging 的既存文件生成非空、hash-bound 规范
   manifest，作者二次签核且当前 validator 通过后，才允许建立 source frame 和运行无
   研究模型的环境/标签可行性检查。
5. `G4 experiment preregistration`：根据 feasibility 冻结 RQ、estimand、splits、证据
   规则、模型选择规则、样本量、baseline、统计和停止条件，生成训练/确认性 manifest
   和新的作者签核。
6. `G5 training dry-run`：只验证数据加载、loss、checkpoint、恢复和指标计算；不得使用
   confirmatory test outcomes 调参。
7. `G6 development`：只在 train/dev 开发并冻结最终方法。
8. `G7 confirmation`：一次性运行锁定的项目外/时间外测试并按预注册结论报告。

任一阶段发现旧任务/项目/内容碰撞、标签泄漏、同谱系跨 split、source frame 功效不足、
隐藏标签不可信、最简单 baseline 已无可测 headroom，或方法只能靠增加人工审核获益，均
必须停止并诊断；不得通过 prompt、阈值、模型或追加样本的结果后调整修补正向结论。

## 12. 当前未授权事项

- 未创建未来研究数据；
- 未选择具体项目、任务、backbone 或超参数；
- 未读取训练凭证；
- 未运行训练、模型推理、容器或 API；
- 未确定确认性样本量或效果量；
- 未产生任何论文结果或效果 claim。

下一步仅允许执行 `G0 novelty` 的系统性检索和 `G1 feasibility protocol` 的纯协议
设计。G2 acquisition-only 机制尚未实现或签核，因此当前不得枚举、下载或读取任何未来
项目/任务内容；即使未来 G2 只完成机械 staging，在 G3 规范 manifest 非空、hash-bound、
二次签核且通过 validator 前，仍不得读取语义内容或开展任何科学使用。
