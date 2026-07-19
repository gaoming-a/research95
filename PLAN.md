# Plan: Same API, Changed Contract（C′）

_Locked via grill — by Codex + author_

## Goal

完成一篇以 benchmark/protocol/empirical study 为主的 EI 候选小论文，研究在工具名称与参数
schema 保持稳定、当前契约已明确呈现的条件下，LLM 工具智能体能否随单个可执行契约原子的
变化而正确改变动作，并在语义等价变化下保持稳定。小论文必须用自建有限状态工具环境、独立
机械 oracle、显式 pair lineage、闭环任务完成指标和独立现实版本迁移证据建立可信性；普通
SFT/LoRA、DPO、CounterComp/PairCFR 类目标只作基线。硕士论文只在小论文证实现有模型与
普通适应方法仍存在稳定 OOD 缺口后，扩展契约组合、持续更新或结构化适应方法。

本计划只锁定研究设计，不授权数据生成、外部数据获取、模型选择、API、训练或实验。进入每个
执行阶段前，仍需作者单独授权并由 canonical future-study manifest 明确记录。

## Approach

1. **冻结科学问题、claim 与评测单位。**

   - 暂定题名：**Same API, Changed Contract: Paired Executable Evaluation of LLM
     Tool-Agent Compliance**。
   - 固定任务、工具 identity、参数 schema、初始状态与除契约外的完整可见历史；每个
     `flip pair` 只允许一个语义级 executable contract atom 变化。
   - 固定同一规范化 witness action `a_w`；独立 checker 必须证明其标签在两侧
     `permitted ↔ prohibited`。
   - 同时生成 `equivalent pair`：仅改变同义措辞、字段顺序或无关条款，并证明 witness
     标签与可接受行为集合不变。
   - 只声称 observable contract-conditioned compliance，不声称模型内部因果机制、通用
     agent safety、真实生产可靠性或首次 counterfactual/pairwise training。
   - 在任何数据构造前完成硬 novelty Gate：用全文维度矩阵逐项比较 GuideBench、
     ContractBench、Skill Drift、ToolEVO、CounterComp、PairCFR、AgentAssay/Agent Behavioral
     Contracts 等，证明既有协议不能测量“稳定工具表面下，单契约原子变化导致实际动作合法性
     与完成轨迹变化”。同时预注册 paired design 相对独立实例 aggregate accuracy 新识别的量：
     pair-level contract sensitivity、equivalent-contract invariance 和 paired compliant
     completion。若只是把相邻组件拼接、没有新增可识别现象，数据构造前即停题。

2. **冻结两个互补评测层级。**

   - 诊断层：模型判断固定 witness 的合法性。主指标为 Flip Pair Accuracy，即一对两侧都
     判断正确才计 1；同时报告 required-flip rate、单侧 accuracy 和 equivalent-pair
     invariance。
   - 执行层：模型在有限状态环境中自行选择并调用工具。独立 simulator 分开记录 contract
     violation 与 task completion；query/escalate/no-op 可共同合法，但仅拒绝行动不能获得
     completion。主指标为 Paired Compliant Completion，即一对两侧都无违规且完成任务才计 1。
   - 每个执行对必须附带机械的 policy-separation certificate。先冻结 contract-erasure
     projection `E`：删除契约字段/token，只保留类型化任务、状态观测、稳定 event ID、过去动作
     和工具返回；两侧用 event ID 与 DSL transition ID 对齐 history。action normalizer 将表面调用
     映射为 DSL action ID 和规范化参数，只有该表示完全相同才属于同一动作等价类。
   - 在有限 horizon/cost 下，定义 `Π_i^ok` 为所有只读取 `E(history)`、映射到规范化动作类且能
     在第 i 侧无违规完成任务的确定性历史策略集合。证书要求 `Π_0^ok ∩ Π_1^ok = ∅`；独立求解
     后端必须给出交为空的证明，或给出一个共同成功策略作为反例。共同安全动作可以存在，但若
     always-query/always-escalate 或任何 contract-agnostic policy 仍能两侧完成，该 pair 只能
     留作安全 control，不能进入主要 contract-sensitivity 指标。
   - 生成执行层实例前冻结 goal、horizon、cost、fallback、动作规范化与等价关系。若不能
     冻结，执行层不生成，整个 C′ 方向停止而不是退化成纯文本二分类论文。

3. **建立可审计的语义根与数据谱系。**

   - 首篇只保留两个核心契约族：幂等/重复副作用；原子提交/部分提交与补偿。freshness 仅作
     迁移轴，不作主创新。
   - 每个 root specification 使用版本化有限状态 DSL 表达状态、动作、guard、transition、
     side effect、goal 和契约 atom；自然语言只是该语义根的一个 rendering。
   - 每个根记录 `root_id`、父变换、contract atom、工具族、状态图哈希、renderer 版本、随机
     seed、source/provenance 和 split。现实项额外记录 `source_change_event_id`；同一 changelog
     事件、端点版本变化或共同上游变更的所有 roots 共享该事件 ID。所有改名、同义改写、字段
     重排、随机实例及组合派生继承同一 `root_id`。
   - 在任何表面文本生成前按 root/tool family/contract composition 分配 split；派生项永不
     跨 split。生成后重新执行 lineage-closure 审计。
   - 初始规模目标为至少 240 个独立 roots、8--12 个工具族；最终数量由不进入 confirmatory
     test 的 pilot 所估计的 root-cluster 方差决定，使每个预注册模型 PCC 的 95% 区间半宽
     不超过 5 个百分点。派生文本行不增加统计样本量。

4. **用五层 Gate 保证自生成数据可靠性。**

   **Gate R1 — 构造有效性。**

   - DSL 必须通过类型、可达性、终止性和状态不变量检查；每个 episode 的目标必须可达。
   - `flip pair` 的语义 AST diff 必须严格为 1，非契约输入的规范化哈希必须完全一致；
     `equivalent pair` 的可达转移和可接受动作集合必须等价。
   - 执行层必须按冻结的 `E`、history alignment、action normalizer 与 `Π_i^ok` 机械验证
     policy-separation certificate，并保存可复算的空交证明或共同策略反例；不能只因为 witness
     标签翻转就假定闭环策略必然不同。
   - 上述结构不变量要求 100% 通过；一个失败即阻止数据发布和后续模型运行。

   **Gate R2 — 标签独立性。**

   - 先冻结一份不含实现代码的参考语义规范和人工逐步推导的极小 gold suite，覆盖每个 contract
     atom、flip 方向、等价控制、部分提交和共同安全动作；gold suite 由两名审阅者核对。
   - generator 只按声明式变换产生语义实例和 transformation certificate，不输出、缓存或参与
     最终 legality/completion 标签；evaluation checker 通过独立状态枚举重新计算。
   - 再使用第二种独立求解后端（例如显式枚举与独立 SMT/模型检查编码）交叉验证 checker；
     两个后端可以共享序列化 schema/parser，但不得共享 guard、transition、goal 或许可判定代码。
   - gold suite、两个求解后端必须在全部适用实例上 100% 一致；任何分歧先诊断 generator、
     checker 或 DSL semantics，修复并全量重验，不能投票或人工挑选结果。
   - 为 checker 注入预定义的 guard inversion、wrong-scope、wrong-expiry、partial-commit、
     duplicate-effect 和 stale-contract mutants；验证套件必须杀死全部声明内 mutants。
   - LLM 或人工意见不得成为最终 legality/completion 标签源。

   **Gate R3 — 自然语言忠实性。**

   - 自然语言 renderer 必须从已验证 AST 生成，禁止先写文本再让 LLM 猜 DSL。
   - 两名互不沟通的审阅者盲审全部现实迁移 roots，并分层抽查至少 10% 且不少于 100 个合成
     roots，分别判断文本是否忠实、是否泄露标签、是否只改变目标 contract atom。
   - 合成审计 Cohen's kappa 必须不低于 0.80；所有实质分歧须裁决并修订根模板。现实迁移项
     必须 100% 通过双人来源核对，否则删除，不以 kappa 平均掩盖来源错误。

   **Gate R4 — 泄漏与 shortcut。**

   - 保持 pair 两侧长度、字段位置、工具名、动作位置和标签比例可比较；设置关键词、长度、
     位置、工具名、旧契约 prior 以及 bag-of-words/浅层分类器基线。
   - 必须在 root-closed、tool-family OOD、wording OOD 和 unseen two-clause composition 上报告；
     任何根或其派生不得跨训练/开发/测试。
   - 若关键词、位置、工具名、长度或 bag-of-words 等不含契约语义的浅层基线在严格 OOD 上
     达到 95% Paired Compliant Completion，判定存在 shortcut，修复或停题。
   - deterministic NL parser + exact FSM planner 是正式可行解而非“作弊”。它若在严格 OOD 上
     达到 95% 或与 gold DSL oracle 相差不超过 2 个百分点，只否决“必须参数训练”的论点；
     benchmark 仍可比较 LLM 与显式解析方案的正确性、成本和覆盖边界，但不得故意增加语言噪声
     以压低 parser。

   **Gate R5 — 外部有效性。**

   - 经单独 acquisition/data-use 授权后，只从具有可核验版本号/日期的官方 API 文档、SDK
     release notes、公开规范仓库或 changelog 建立现实迁移候选；记录 URL、版本、访问日期、
     许可证、内容哈希和最小证据摘录/释义。
   - 两名审阅者独立确认：规范化 tool signature hash 在比较边界内稳定；变化属于执行语义而
     非名称/参数变化；可以映射为一个声明内 contract atom。每个 root 必须保存旧版证据、
     新版证据和官方迁移/变更声明三方 provenance。映射后仍由机械 checker 产生动作标签。
   - 在许可、安全且可离线复现时，只有供应方版本化 SDK contract tests、官方规范测试或与
     本研究独立存档的可执行 artifact 才能验证旧/新行为并升级为行为证据。自建 mock/replay
     只能检查 DSL/renderer 内部一致性；无法获得独立可执行证据的项只能支持“真实文档语义
     变化迁移”，不得写成真实 API 执行有效性或生产可靠性。
   - 外部集最低 Gate：不少于 30 个独立 `source_change_event_id`、至少 5 个工具族、覆盖两个
     核心契约族，任何单一工具族不超过 30%。同一事件派生的多个 roots 只算一个最高依赖事件
     簇。达不到则不能主张现实版本迁移；因该证据是 C′ 的核心区分项，需重新过选题 Gate，
     而不是用多个自建包装代替现实性。

5. **先执行完全无模型的 feasibility Gate。**

   - 只在作者另行授权数据构造、manifest 变更且隔离审计通过后，先生成小规模 root-level
     feasibility set；不调用模型或 API。
   - 验证 R1--R5 中当阶段可检查的项目、root lineage、标签平衡、pair 可达性、执行任务非
     平凡性和现实来源数量。
   - 运行 majority/old-contract prior、关键词/位置/工具名、bag-of-words、contract retrieval、
     deterministic parser+exact planner 和 gold DSL oracle。
   - 任一结构标签错误、lineage 泄漏、现实集不足或 shortcut 近饱和，先停止并修设计；不得
     顺手进入模型 pilot。

6. **通过新授权后执行最小模型 pilot。**

   - 模型选择在执行前依据当时可获得、许可和可复现的开放权重模型重新核验；目标覆盖至少
     两个模型家族、7B/14B 两个能力档，不因现有 GPU 资源固定过时型号。
   - 先做 prompt-only、显式契约重读、相关条款检索再决策和结构化输出；只有 pilot 显示非
     平凡 headroom 才进入训练基线。
   - 若所有强模型 prompt-only 已在主要 OOD 达到 95% 以上，benchmark 缺少研究张力，停止
     训练扩展；若接近随机且错误来自 renderer 歧义，先修数据，不把失败归因于模型。

7. **把训练严格限定为适应基线。**

   - 比较等样本、等 token、等 backbone、等 adapter rank、等更新步数、等随机种子数和等
     调参预算的 ordinary SFT、standard DPO、true-pair/shuffled-pair SFT/DPO、PairCFR 式
     `PairCAD/ShuffCAD × CE/CE+InfoNCE` 与 CounterComp 风格 triplet。
   - 至少三个随机种子；训练、开发和测试按 root lineage 固定，不因结果调整 split。
   - 训练只有在相对全部强基线取得预注册的最小实际增量时，才可被描述为本 benchmark 上的
     empirical improvement，仍不得称新 pairwise/contrastive 方法。
   - 同时报告标准 tool-calling 保持率；合规提升若显著损害 completion 或基础工具能力，判定
     方法失败。

8. **预注册统计分析与报告边界。**

   - 合成主分析对每个预注册 evaluation model 分别估计其在目标 root population 上的 Paired
     Compliant Completion；`root_id` 是实验单位，也是 root-cluster 的唯一成员键。一个 cluster
     包含该 root 的所有 contract 两侧、paraphrase、随机派生与重复推理；先在 cluster 内聚合，
     再计算模型级 PCC 和 root-cluster 区间。tool family 是预定义分层与 OOD 分组；家族数少于
     20 时只报告逐家族和 leave-one-family-out 区间，不作“泛化到所有工具族”的总体显著性
     外推。所有方法差异只保留为校正后的次要分析。
   - 现实迁移分析以 `source_change_event_id` 为最高依赖 cluster、tool family 为分层；同一事件
     的多个 endpoints/roots 先在事件内聚合，再进入区间估计。
   - benchmark 论文不预设新方法。唯一主要 estimand 是：对每个在 confirmatory run 前冻结的
     evaluation model，估计其在预注册目标 root population 上的 Paired Compliant Completion；
     Flip Pair Accuracy 是预注册诊断指标。模型面板、版本和模板在查看 confirmatory 结果前冻结。
   - primary inference 使用 temperature 0/greedy decoding 并冻结模型、推理框架、模板和版本；
     对不可保证确定性的服务或随机策略，每个 root 至少重复 5 次，先在 root 内聚合，再按上述
     cluster 分析。训练方法另以至少 3 个训练 seeds 嵌套于 root-level 结果，不能把推理重复当
     独立 roots。
   - 使用不进入最终 confirmatory test 的 pilot roots 估计簇内相关和推理方差，再冻结最终
     样本量；每个冻结模型的主要 PCC 目标是 root-cluster 95% 区间半宽不超过 5 个百分点，
     而不是为一个尚不存在的新方法预设功效。若现有 8--12 个工具族不足以支持目标外推，则
     收缩 estimand 或增加独立家族，不用派生行伪造精度。prompt/training/baseline 的方法间差异
     全部是 Holm 校正的次要分析并报告绝对差值与区间。
   - 未来若进入硕士方法论文，必须在独立 preregistration 中指定唯一主要方法对比、最小实际
     效应、配对 discordance/ICC 假设和至少 80% power；不得从本 benchmark 的多重比较中事后
     选择“主方法”。
   - 预先报告按契约族、工具族、flip 方向、OOD 类型和失败类别的结果；不得只挑有利子集。
   - 发布可重建脚本、schema、root manifest、split manifest、hashes、checker 测试和审计
     报告；受许可限制的现实文本只发布允许的最小证据与可重建索引。

9. **形成 EI 小论文最短证据链。**

   - RQ1：当前模型在稳定 API 表面下能否服从单原子 contract delta？
   - RQ2：现象能否排除关键词、位置、工具名、旧契约 prior、lineage leakage 和纯 parser
     shortcuts？
   - RQ3：prompt、检索、ordinary SFT/DPO 与既有 pairwise 方法能改善多少，是否在 OOD 与
     capability retention 上成立？
   - RQ4：结论能否迁移到独立真实版本 semantic deltas？
   - 论文贡献只写 generator/protocol/oracle/paired metrics/empirical findings；投稿前重新核验
     目标会议或期刊当年的 EI/Compendex 状态、版面、费用和学校认定，不提前保证录用。

10. **只在小论文 Gate 通过后扩展硕士论文。**

    - 必要条件：模型存在重复可复现缺口；parser/planner 未近饱和；普通 SFT/DPO 和既有
      pairwise 基线仍留下显著 OOD 缺口；候选适应方法在 held-out 现实
      `source_change_event_id` 上也取得预注册的显著/实际改进；能力保持可接受。
    - 允许扩展：多 contract atom 组合、版本序列、continual adaptation、契约结构表示，以及
      parameter adaptation 与 runtime enforcement 的比较。
    - 若必要条件不成立，小论文可作为独立 benchmark 结果收尾，但不得强行制造训练创新；
      硕士方向必须重新过全文创新 Gate。

11. **执行闭环与授权。**

    - 每一阶段执行 Inspect--Plan--Execute--Verify--Diagnose--Repair--Sync Docs--Gate--Commit
      And Sync；验证失败先分类，不继续后续实验。
    - 所有新研究输入只能经 canonical manifest 和 sanctioned loader；历史七条研究 lineage、
      旧数据、旧结果、旧 prompt 与旧选择证据继续隔离。
    - 每次代码或文档更新同步 README、当前计划、经验文档和索引；只提交本轮相关文件，扫描
      敏感信息后同步私有 GitHub。不得向公共仓库推送未来研究计划或未授权 artifact。
    - 在进入任何数据构造前，必须先使 `current_plan_zh.md`、`current_project_state_zh.md`、
      candidate audit、README、`docs/INDEX.md` 和本审查日志一致指向 C′ benchmark-first；权威
      文档冲突时 fail closed。随后仍需作者单独放行 data-use manifest，不能用本 PLAN 代替。

## Key decisions & tradeoffs

- **Benchmark-first，而非 method-first。** 牺牲“新损失函数”叙事，换取可识别、可机械反驳的
  科学问题。训练资源用于强基线和后续扩展，不构成创新理由。
- **合成主集＋现实外部集。** 合成 FSM 提供精确干预和无噪声标签；现实版本变化提供外部
  有效性。二者承担不同证据角色，不能用合成领域包装替代现实迁移。
- **机械标签＋人工来源核对。** 机械 checker 保证形式化后的动作标签；双人核对保证现实文档
  到 DSL 的映射忠实。机械 oracle 不能证明原始文档解释正确，人工一致性也不能替代执行标签。
- **诊断＋闭环执行。** witness 判断提供干净的 pair-level 定位；闭环 episode 防止任务退化为
  文本二分类或 always-abstain。
- **严格 lineage 优先于数据量。** 大量 paraphrase 不增加有效样本量；统计与 split 均以 root
  和 tool family 为单位。
- **当前不限制通信场景。** 工具族按契约语义和可验证性选择，不因学位专业名称引入不熟悉的
  通信任务。

## Risks / open questions

- 稳定 identity/schema 但执行语义发生单原子变化的真实案例可能不足 30 个或集中于少数工具；
  这是外部有效性生死 Gate，必须在模型实验前解决。
- GuideBench、ContractBench、Skill Drift 等相邻工作的组合可能在投稿前出现更直接的新工作；
  每个里程碑和投稿前重新做全文 novelty audit，直接重合即停止或改题。
- 自然语言 rendering 可能泄露标签或产生歧义；R3 双盲审计、hard negatives 与 shortcut 基线
  用于发现，不允许通过删除困难样本美化结果。
- 确定性 parser+planner 可能近饱和。若发生，说明核心问题是规范解析/规划而不是需要训练的
  LLM 适应；按 Gate 停止训练 claim。
- 闭环任务可能奖励保守拒绝或因 horizon/cost 设计产生伪差异；必须分别报告违规与完成，并在
  生成前冻结目标和预算，同时用 policy-separation certificate 排除共同策略伪装成契约服从。
- 具体开放权重模型、软件版本和 EI 投稿 venue 会变化；选择规则已经冻结，但具体名称必须在
  获得执行/投稿授权时用官方来源重新核验。

## Out of scope

- 当前不生成或下载任何研究数据，不读取旧研究输入，不运行模型/API/训练/容器或真实实验。
- 不声称新 counterfactual/pairwise/contrastive/DPO 方法，不以 LoRA 本身作为创新。
- 不研究自动发现外部 contract drift、skill 文档维护或通用 API schema evolution；当前契约被
  视为已经提供给 agent。
- 不证明模型内部真正使用契约，不作机制因果识别。
- 不声称覆盖所有工具、安全故障或生产系统可靠性；形式结论只在声明的有限状态 DSL 和契约
  atom 范围内成立。
- 小论文不扩展多智能体、通信协议、无限状态环境、隐式契约推断或在线 RL。
