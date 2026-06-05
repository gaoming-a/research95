# Agent 顶会文献调研 2025-2026 中文版

最后更新：2026-05-28

## 调研范围

本文档跟踪 2025 年 5 月至 2026 年 5 月左右与 LLM/AI agent 相关的顶会论文。

目标会议包括 ICLR、ICML、NeurIPS、ACL、EMNLP、NAACL、ICSE、ASE、FSE、OSDI/SOSP、WWW、KDD、AAAI、IJCAI，以及在主题上与 agent 直接相关的其他顶级会议。

本文中的 "agent" 指：能够规划、行动、调用工具、与环境或用户交互、进行多 agent 协作、维护记忆，或执行自动化软件工程/代码工作流的 LLM/AI 系统。一般 LLM 论文只有在 agent 组件是其方法或评估核心时才纳入。

## 纳入标准

- 发表或接收时间位于近一年窗口内。
- 直接研究 LLM/AI agent、多 agent 系统、agent 评估、工具使用、规划、记忆、软件工程 agent，或 agent 安全与可靠性。
- 有足够可访问内容，能够总结方法和实验发现。

## 排除标准

- 博客文章或没有同行评审 venue 的 benchmark。
- 没有实质 agent 组件的一般 LLM 论文。
- 超出时间窗口的旧论文，除非作为背景材料。

## 选择概述

第一轮调研优先选择同时满足两个条件的论文：venue 可验证，且对当前 cross-model code review 课题有方法启发。入选论文覆盖：

- 多 agent 编排与通信。
- 工具使用、检索、Web agent 与操作环境 agent。
- 软件工程、研究与机器学习工程 agent。
- agent 训练、数据生成与自动化 agent 设计。
- 安全、记忆与工具相关失效模式。

由于“近一年”以 2026-05-28 为参照，工作窗口设为 2025 年 5 月到 2026 年 5 月。部分 ICLR 2025 论文保留在内，因为它们在 2025 proceedings 中正式发表，且仍是当前研究周期内最直接相关的 peer-reviewed agent 论文。ICLR 2026、NeurIPS 2025、EMNLP 2025、ICML 2025、ACL/NAACL 2025、ASE 2025 和 AAAI 2026 论文则在 venue 状态明确时纳入。

## 入选论文

| 序号 | 论文 | Venue | 主题 | 与本项目的关系 |
| --- | --- | --- | --- | --- |
| 1 | [Graph-of-Agents: A Graph-based Framework for Multi-Agent LLM Collaboration](https://openreview.net/forum?id=34cANdsHKV) | ICLR 2026 | 多模型 agent 图 | 直接支持 cross-model reviewer/generator routing 的研究动机。 |
| 2 | [Interact-RAG: Reason and Interact with the Corpus, Beyond Black-Box Retrieval](https://openreview.net/forum?id=yHUjWb6eMe) | ICLR 2026 | agentic retrieval | 说明 agent 需要可控中间动作，而不只是一次性 prompt。 |
| 3 | [Go-Browse: Training Web Agents with Structured Exploration](https://openreview.net/forum?id=IpzRWE52yw) | ICLR 2026 | Web agent 数据收集 | 提供从环境探索中规模化收集 trajectory 的思路。 |
| 4 | [Proactive Agent: Shifting LLM Agents from Reactive Responses to Active Assistance](https://proceedings.iclr.cc/paper_files/paper/2025/hash/75c37811e830bf029584b1c6fac17726-Abstract-Conference.html) | ICLR 2025 | 主动式辅助 | 将 agent 行为建模为预测何时帮助、如何帮助的决策问题。 |
| 5 | [AgentOccam: A Simple Yet Strong Baseline for LLM-Based Web Agents](https://proceedings.iclr.cc/paper_files/paper/2025/hash/f2c6e459b95694a24ac69c469a4ee746-Abstract-Conference.html) | ICLR 2025 | Web agent baseline | 说明表示对齐可能比复杂 orchestration 更关键。 |
| 6 | [Web Agents with World Models](https://proceedings.iclr.cc/paper_files/paper/2025/hash/a00548031e4647b13042c97c922fadf1-Abstract-Conference.html) | ICLR 2025 | world model | 启发我们预测 review/repair 行为后果。 |
| 7 | [WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum RL](https://proceedings.iclr.cc/paper_files/paper/2025/hash/c66e1fcc9691aae706250638f36f681b-Abstract-Conference.html) | ICLR 2025 | Web agent 强化学习 | 说明失败尝试可以转化为新 curriculum。 |
| 8 | [SWE-Search: Enhancing Software Agents with MCTS and Iterative Refinement](https://proceedings.iclr.cc/paper_files/paper/2025/hash/a1e6783e4d739196cad3336f12d402bf-Abstract-Conference.html) | ICLR 2025 | 软件工程 agent | 是 repository-level code repair agent 的重要相关工作。 |
| 9 | [Cut the Crap: An Economical Communication Pipeline for LLM-based Multi-Agent Systems](https://proceedings.iclr.cc/paper_files/paper/2025/hash/bbc461518c59a2a8d64e70e2c38c4a0e-Abstract-Conference.html) | ICLR 2025 | 通信剪枝 | 对控制 cross-model review 矩阵成本非常重要。 |
| 10 | [Scaling Large Language Model-based Multi-Agent Collaboration](https://proceedings.iclr.cc/paper_files/paper/2025/hash/66a026c0d17040889b50f0dfa650e5e0-Abstract-Conference.html) | ICLR 2025 | agent scaling law | 提醒我们 agent 数量增加不一定线性带来收益。 |
| 11 | [ToolGen: Unified Tool Retrieval and Calling via Generation](https://proceedings.iclr.cc/paper_files/paper/2025/hash/b646bdebeb87dfafe2c6f77a63b564e1-Abstract-Conference.html) | ICLR 2025 | 工具调用 | 说明工具选择可以被建模为生成动作，而不只是外部检索。 |
| 12 | [AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents](https://proceedings.iclr.cc/paper_files/paper/2025/hash/c493d23af93118975cdbc32cbe7323f5-Abstract-Conference.html) | ICLR 2025 | agent 安全 | 说明 agent 能力与安全必须联合评估。 |
| 13 | [MAS-GPT: Training LLMs to Build LLM-based Multi-Agent Systems](https://icml.cc/virtual/2025/poster/46543) | ICML 2025 | 自动构建多 agent 系统 | 启发未来自动生成 reviewer-agent workflow。 |
| 14 | [ResearchTown: Simulator of Human Research Community](https://icml.cc/virtual/2025/poster/46055) | ICML 2025 | 研究社区 agent 仿真 | 与 review、writing、collaboration workflow 建模相关。 |
| 15 | [TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks](https://neurips.cc/virtual/2025/poster/121705) | NeurIPS 2025 | 数字员工 benchmark | 是真实 agent 工作流 benchmark 设计的重要参考。 |
| 16 | [MLE-Dojo: Interactive Environments for Empowering LLM Agents in Machine Learning Engineering](https://proceedings.neurips.cc/paper_files/paper/2025/hash/0603c69125ad4b964bc9c4832f7b9f8f-Abstract-Datasets_and_Benchmarks_Track.html) | NeurIPS 2025 Datasets & Benchmarks | 机器学习工程 agent | 最接近 iterative coding/experiment agent 的环境。 |
| 17 | [Attractive Metadata Attack: Inducing LLM Agents to Invoke Malicious Tools](https://neurips.cc/virtual/2025/poster/116046) | NeurIPS 2025 | 工具安全 | 说明 tool metadata 本身就是攻击面。 |
| 18 | [Memory Injection Attacks on LLM Agents via Query-Only Interaction](https://neurips.cc/virtual/2025/poster/118152) | NeurIPS 2025 | agent 记忆安全 | 与持久 review memory 的污染风险相关。 |
| 19 | [WALL-E: World Alignment by NeuroSymbolic Learning improves World Model-based LLM Agents](https://neurips.cc/virtual/2025/poster/119191) | NeurIPS 2025 | world model 对齐 | 支持用可执行符号约束限制 agent 行动。 |
| 20 | [ContextAgent: Context-Aware Proactive LLM Agents with Open-world Sensory Perceptions](https://neurips.cc/virtual/2025/poster/115593) | NeurIPS 2025 | 上下文感知主动 agent | 将 proactivity 扩展到更丰富的上下文感知。 |

## 详细阅读笔记

### 1. Graph-of-Agents

- 问题：多 agent LLM 系统常使用固定或过大的 agent 池，无关 agent 会增加成本并引入噪声。
- 方法：利用 model card 选择相关 agent，根据 response relevance 构建有向图，进行前向和后向消息传递，最后聚合响应。
- 实验：在 MMLU、MMLU-Pro、GPQA、MATH、HumanEval、MedMCQA 等 benchmark 上评估；报告结果显示，选择 3 个相关 agent 可以优于使用全部 6 个 agent 的 baseline。
- 局限：依赖 model card/task specialization 信息的有效性，benchmark 级聚合是否能迁移到长程环境仍需验证。
- 与本项目关系：高度相关。我们的 reviewer matrix 不应只测试所有组合，还应分析哪类 reviewer 对哪类 bug/source/task 更有用。

### 2. Interact-RAG

- 问题：很多 agentic RAG 仍然是黑盒检索，agent 只是改写 query 并消费片段。
- 方法：加入 corpus interaction engine 和 action primitives，并用 synthetic trajectories、SFT、RL 训练 autonomous agent。
- 实验：在 6 个 information-seeking benchmark 上报告提升。
- 局限：效果依赖是否能暴露有用的低层检索控制；普通 API search 未必支持这种接口。
- 与本项目关系：代码审查 agent 应获得结构化的代码、测试、trace、diff，而不是把所有内容堆进一个 prompt。

### 3. Go-Browse

- 问题：Web agents 缺少足够真实的任务轨迹，也常不理解网站结构。
- 方法：把探索视为 graph search，跨 episode 复用发现，并规模化收集成功 trajectory。
- 实验：在 WebArena URL 上收集 10K 成功轨迹和 40K interaction steps；微调 7B 模型后在 WebArena 达到 21.7% success，并在其设置下超过 GPT-4o mini。
- 局限：WebArena 轨迹未必能泛化到任意生产网站。
- 与本项目关系：bug generation/review/repair 不应只记录最终代码，失败和成功轨迹本身也可以成为评估数据。

### 4. Proactive Agent

- 问题：多数 LLM agent 是被动响应，主动帮助需要判断何时帮助以及如何帮助。
- 方法：收集人类活动事件，将主动建议标注为接受/拒绝，训练 reward model，并构建 ProactiveBench。
- 实验：微调模型在主动辅助中达到 66.47% F1，优于所评估的开放和闭源模型。
- 局限：主动性高度依赖人类偏好标签和隐私敏感上下文。
- 与本项目关系：code-review agent 可以在测试失败前主动提示风险，但必须严肃评估误报和打扰成本。

### 5. AgentOccam

- 问题：Web agent 失败可能来自 observation/action 表示不匹配，而不只是推理能力弱。
- 方法：简化 agent，使网页观察和动作表示更贴近 LLM 擅长处理的语言模式。
- 实验：在 WebArena 和 WebVoyager 上提升表现，且不依赖 in-context examples、新角色、在线反馈或搜索。
- 局限：方法依赖具体领域的表示设计。
- 与本项目关系：警惕过度构造复杂多 agent 框架。对代码审查来说，输入表示可能比增加 reviewer 角色更重要。

### 6. Web Agents with World Models

- 问题：Web agent 缺少行动后果模型，容易犯不可逆错误。
- 方法：通过 transition-focused observation abstraction 训练/使用 world model 预测状态转移，并辅助 policy selection。
- 实验：在 WebArena 和 Mind2Web 上，world-model augmentation 提升策略选择效果，并比重型 tree-search agent 更节省成本和时间。
- 局限：自然语言状态转移预测可能遗漏低层状态变化。
- 与本项目关系：repair agent 不应只判断当前 bug 是否被修复，还应预测 patch 是否可能破坏 hidden tests。

### 7. WebRL

- 问题：强 Web agent 往往依赖闭源 API；开放模型在稀疏奖励和有限任务数据下表现弱。
- 方法：使用 self-evolving curriculum RL：失败尝试产生新任务，outcome-supervised reward model 提供反馈，adaptive RL 处理 policy drift。
- 实验：Llama-3.1-8B 从 4.8% 提升到 42.4% success；Llama-3.1-70B 在 WebArena-Lite 达到 47.3%。
- 局限：RL 设置和 reward model 质量代价高，且依赖环境。
- 与本项目关系：自然 bug pipeline 可以把失败 generation 作为 reviewer/repairer 的 curriculum cases。

### 8. SWE-Search

- 问题：软件 agent 常是线性流程，难以从早期错误决策中回退。
- 方法：结合 MCTS、self-improvement、value agent、SWE-agent explorer 和 discriminator/debate agent。
- 实验：在 SWE-bench 上跨 5 个模型相对标准开源 agent 报告 23% 相对提升。
- 局限：search 增加推理成本，对小代码任务可能过重。
- 与本项目关系：这是 code repair 相关工作的核心论文。我们的工作可以定位为 search-heavy software agent 的低成本补充或替代。

### 9. AgentPrune

- 问题：多 agent 通信图浪费 token，并可能传播恶意或冗余消息。
- 方法：定义通信冗余，一次性剪枝 spatio-temporal message-passing graph。
- 实验：在保持相近性能的同时显著降低成本，报告 token 减少 28.1%-72.8%，并提升对两类 agent-based attack 的鲁棒性。
- 局限：剪枝质量依赖 redundancy estimator 和任务设置。
- 与本项目关系：cross-model review 需要跟踪每个 reviewer 的边际收益，而不只是绝对准确率。

### 10. Scaling LLM-based Multi-Agent Collaboration

- 问题：增加 LLM agent 数量是否像增加模型能力一样带来可预测收益并不清楚。
- 方法：用 DAG 组织的 MacNet 拓扑协调大量 agent，并研究 scaling 行为。
- 实验：报告超过 1000 个 agent 的协作，非规则拓扑优于规则拓扑，并提出 logistic collaborative scaling law。
- 局限：超大规模 agent 在成本受限的代码审查中不现实。
- 与本项目关系：可用于论证为什么需要 reviewer selection 和 cost-aware evaluation。

### 11. ToolGen

- 问题：通过长工具描述和外部检索进行工具调用，在大规模工具集下不可扩展。
- 方法：将每个工具表示成 token，把工具检索/调用学习为生成过程。
- 实验：在超过 47,000 个工具上评估，报告工具检索和 autonomous task completion 的提升。
- 局限：需要模型侧训练和 tool-token 维护。
- 与本项目关系：对 coding agent 来说，工具选择可被视为一类可学习动作，而不是临时 prompt routing。

### 12. AgentHarm

- 问题：agent 安全不同于 chatbot 安全，因为工具使多步有害执行成为可能。
- 方法：构建 110 个恶意 agent 任务，增强后 440 个，覆盖 11 类 harm；评估拒绝能力和 jailbreak 后任务能力。
- 实验：发现领先模型仍可能遵从有害 agent 请求，通用 jailbreak 字符串在 agentic setting 下仍有效。
- 局限：安全 benchmark 可能滞后于真实工具生态。
- 与本项目关系：论文不能只评估 correctness。agent review/repair 会引入新风险，尤其当工具执行代码时。

### 13. MAS-GPT

- 问题：手动设计多 agent 系统昂贵且脆弱。
- 方法：把 MAS 构建重写为从用户 query 生成可执行 MAS code，并用一致的 query-MAS pairs 训练中等规模模型。
- 实验：ICML 页面报告其能在单次 inference 中生成 query-adaptive MAS。
- 局限：生成的系统需要强 correctness 和 safety checks。
- 与本项目关系：未来可以根据 task 和 bug type 自动生成 reviewer-agent workflow。

### 14. ResearchTown

- 问题：科研社区包含阅读、写作和 review 交互，很难规模化研究。
- 方法：把研究社区建模为 agent-data graph，并使用 TextGNN-style message passing 表示研究活动。
- 实验：报告能够模拟 collaborative research、多研究者/论文行为和跨学科 idea generation。
- 局限：模拟研究质量很难用真实科学新颖性验证。
- 与本项目关系：有助于理解用 agent 辅助写作、审稿、协作，以及建模 peer-review-like 行为。

### 15. TheAgentCompany

- 问题：agent benchmark 常缺少 consequential real-world work tasks。
- 方法：构建一个自包含的软件公司环境，让 agent 浏览、写代码、运行程序并与同事交流。
- 实验：最强 baseline agent 能自主完成约 30% 的任务。
- 局限：benchmark company 仍是控制环境，可能无法覆盖生产环境变化。
- 与本项目关系：是 realistic agent workflow benchmark 设计的重要参考。我们的实验也应逐步加入真实 workflow，而不只停留在 HumanEval 函数。

### 16. MLE-Dojo

- 问题：ML engineering agent 需要迭代实验、debug 和反馈，但许多 benchmark 是静态的。
- 方法：基于 200+ Kaggle-style challenges 提供 Gym-style 可交互环境和执行反馈循环。
- 实验：评估 8 个 frontier LLM，发现它们能在迭代中进步，但在长程方案和复杂错误解决上仍弱。
- 局限：Kaggle-like 任务更强调 ML pipeline，而非一般软件维护。
- 与本项目关系：支持我们记录 execution feedback、hidden tests 和 repair trajectory，而不是只看 final patch accuracy。

### 17. Attractive Metadata Attack

- 问题：工具 metadata 本身可能诱导 agent 调用恶意工具。
- 方法：通过黑盒迭代优化构造语法和语义上有效的工具 metadata。
- 实验：在 10 个模拟 tool-use 场景中报告 81%-95% attack success，并产生 privacy leakage，同时对 primary task completion 影响有限。
- 局限：模拟工具生态可能简化真实工具治理。
- 与本项目关系：tool descriptions、model labels、reviewer role descriptions 都应视为潜在风险面。

### 18. Memory Injection Attacks

- 问题：带 memory 的 agent 即使没有直接 memory access，也可能被 query-only interaction 污染。
- 方法：通过交互诱导恶意记录被写入并在后续检索；使用 bridging steps 将受害 query 与恶意 reasoning 连接。
- 实验：展示了跨多种 agent 的 memory compromise。
- 局限：具体效果依赖 memory write 和 retrieval policy。
- 与本项目关系：如果维护长期 review memory，必须区分可信实验记录和模型生成的 rationale。

### 19. WALL-E

- 问题：LLM world model 可能不符合真实环境 dynamics。
- 方法：从 trajectory 中抽取 symbolic action rules、knowledge graphs 和 scene graphs，编码为可执行约束，并使用类似 MPC 的 planning loop。
- 实验：在 Mars/Minecraft-like 和 ALFWorld 设置中报告显著提升，包括 4 次迭代后 ALFWorld 98% success。
- 局限：符号抽取可能脆弱，并非所有领域都有清晰 symbolic dynamics。
- 与本项目关系：对 code review 来说，可执行测试和静态检查可作为 LLM reasoning 外部的 symbolic constraints。

### 20. ContextAgent

- 问题：主动 agent 需要比封闭 UI 状态或手写通知规则更丰富的上下文。
- 方法：抽取多维 sensory context，使用历史 persona 信息，预测是否需要帮助，并低干扰地调用工具。
- 实验：ContextAgentBench 包含 9 个场景和 20 个工具的 1,000 个样本；报告 proactive prediction 最多提升 8.5%，tool calling 最多提升 6.0%。
- 局限：隐私和 sensor noise 是核心问题。
- 与本项目关系：coding agent 的上下文可以包括近期编辑、失败测试、bug history 和开发意图，但必须测量 false-positive interruption cost。

## 跨论文综合

### 方法趋势

1. Agent 研究正在从 prompt-only scaffolding 转向结构化执行：graph、search、world model、tool primitives、memory 和 executable environment。
2. 多 agent 收益取决于 topology 和 selection。更多 agent 不自动更好；relevance、communication pruning 和 cost-aware routing 很关键。
3. Web 和 software agent 越来越依赖 environment feedback loop。静态 QA 式评估不足以刻画长程 agent 行为。
4. 训练数据正从人工 demonstration 转向 trajectory mining、failed-attempt curriculum、synthetic interaction data 和 environment rollout。
5. Safety failure 具有 agent-specific 特征。工具、memory 和 metadata 会产生普通 chatbot evaluation 中不存在的失效模式。

### 对 Cross-Model Code Review 论文的启示

文献支持本项目方向，但论文不应声称“更多模型互相审查就足够”。更稳的 framing 是：

- 把 code generation、review、repair、execution 和 hidden-test feedback 看作一个 agentic workflow。
- 在成本约束下研究 cross-model complementarity。
- 区分 bug source：interface/specification、logic/boundary、controlled mutation、false positive 和 repair regression。
- 同时测量 correctness 与副作用：false positives、unnecessary repairs、regressions、cost 和 latency。
- 将 execution feedback 作为轻量 world model：reviewer judgment 应接受 tests 和 repair outcomes 的校验。

### 可利用的研究空白

- 许多 agent 论文优化 task success，但较少在 code-generation pipeline 中独立分析 reviewer reliability。
- 多 agent 论文常报告 aggregate benchmark gains，但缺少 bug category 和 cross-model disagreement 分析。
- Safety 论文多关注恶意行为；还有空间研究 benign but harmful reviewer action，例如 false-positive repair 把 passing code 改坏。
- Software-agent 论文常强调最终 SWE-bench solve rate；我们更窄的设置可以提供更可解释的因果证据，说明 cross-model review 在哪里有用、哪里有害。

## 阅读记录协议

每篇纳入论文记录：

- Venue 和接收状态。
- 论文链接和验证来源。
- 研究问题。
- 核心方法。
- 实验设置与主要发现。
- 局限或 validity threats。
- 与 cross-model code review、coding agents 或 agent reliability 的关系。

Workshop、preprint 或 withdrawn papers 可以作为背景候选记录，但除非用户明确拓宽范围，否则不计入目标论文集。
