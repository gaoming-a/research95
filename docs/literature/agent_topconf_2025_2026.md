# Agent Top-Conference Literature Review 2025-2026

Last updated: 2026-05-28

## Scope

This document tracks top-conference papers from roughly May 2025 to May 2026 related to LLM/AI agents.

Target venues include ICLR, ICML, NeurIPS, ACL, EMNLP, NAACL, ICSE, ASE, FSE, OSDI/SOSP, WWW, KDD, AAAI, IJCAI, and related top-tier venues when the paper is directly about agents.

Working definition of "agent": an LLM/AI system that plans, acts, uses tools, interacts with environments/users, coordinates multiple agents, maintains memory, or performs autonomous software-engineering/coding workflows. General LLM papers are included only when the agent component is central to the method or evaluation.

## Inclusion Criteria

- Published or accepted in the last year window.
- Directly studies LLM/AI agents, multi-agent systems, agent evaluation, tool use, planning, memory, software engineering agents, or safety/reliability of agents.
- Has enough accessible content to summarize method and findings.

## Exclusion Criteria

- Blog posts or benchmarks without peer-reviewed venue.
- General LLM papers with no meaningful agent component.
- Older papers outside the window unless needed as background.

## Selection Summary

This first pass prioritizes papers that are both venue-verified and methodologically useful for the cross-model code-review project. The selected set covers:

- Multi-agent orchestration and communication.
- Tool-use, retrieval, web, and operating-environment agents.
- Software/research/ML-engineering agents.
- Agent training, data generation, and automatic agent design.
- Safety, memory, and tool-related failure modes.

Because "near one year" is relative to 2026-05-28, the working window is May 2025 to May 2026. ICLR 2025 papers are retained because several were published in the 2025 proceedings and remain the most directly relevant peer-reviewed agent papers during the current research cycle; ICLR 2026, NeurIPS 2025, EMNLP 2025, ICML 2025, ACL/NAACL 2025, ASE 2025, and AAAI 2026 papers are included when venue status is explicit.

## Selected Papers

| No. | Paper | Venue | Main topic | Why it matters for this project |
| --- | --- | --- | --- | --- |
| 1 | [Graph-of-Agents: A Graph-based Framework for Multi-Agent LLM Collaboration](https://openreview.net/forum?id=34cANdsHKV) | ICLR 2026 | Multi-model agent graph | Directly supports cross-model reviewer/generator routing. |
| 2 | [Interact-RAG: Reason and Interact with the Corpus, Beyond Black-Box Retrieval](https://openreview.net/forum?id=yHUjWb6eMe) | ICLR 2026 | Agentic retrieval | Shows that agents need controllable intermediate actions, not only prompt-level calls. |
| 3 | [Go-Browse: Training Web Agents with Structured Exploration](https://openreview.net/forum?id=IpzRWE52yw) | ICLR 2026 | Web-agent data collection | Provides a recipe for scalable trajectory collection from environment exploration. |
| 4 | [Proactive Agent: Shifting LLM Agents from Reactive Responses to Active Assistance](https://proceedings.iclr.cc/paper_files/paper/2025/hash/75c37811e830bf029584b1c6fac17726-Abstract-Conference.html) | ICLR 2025 | Proactive assistance | Frames agent behavior as anticipatory decision-making with reward-model evaluation. |
| 5 | [AgentOccam: A Simple Yet Strong Baseline for LLM-Based Web Agents](https://proceedings.iclr.cc/paper_files/paper/2025/hash/f2c6e459b95694a24ac69c469a4ee746-Abstract-Conference.html) | ICLR 2025 | Web-agent baseline | Strong evidence that representation alignment can beat complex orchestration. |
| 6 | [Web Agents with World Models](https://proceedings.iclr.cc/paper_files/paper/2025/hash/a00548031e4647b13042c97c922fadf1-Abstract-Conference.html) | ICLR 2025 | World models | Relevant to predicting consequences of repair/review actions before execution. |
| 7 | [WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum RL](https://proceedings.iclr.cc/paper_files/paper/2025/hash/c66e1fcc9691aae706250638f36f681b-Abstract-Conference.html) | ICLR 2025 | RL for web agents | Shows how failed attempts can generate new curriculum tasks. |
| 8 | [SWE-Search: Enhancing Software Agents with MCTS and Iterative Refinement](https://proceedings.iclr.cc/paper_files/paper/2025/hash/a1e6783e4d739196cad3336f12d402bf-Abstract-Conference.html) | ICLR 2025 | Software agents | Directly relevant baseline for repository-level code repair agents. |
| 9 | [Cut the Crap: An Economical Communication Pipeline for LLM-based Multi-Agent Systems](https://proceedings.iclr.cc/paper_files/paper/2025/hash/bbc461518c59a2a8d64e70e2c38c4a0e-Abstract-Conference.html) | ICLR 2025 | Communication pruning | Important for controlling cost in cross-model review matrices. |
| 10 | [Scaling Large Language Model-based Multi-Agent Collaboration](https://proceedings.iclr.cc/paper_files/paper/2025/hash/66a026c0d17040889b50f0dfa650e5e0-Abstract-Conference.html) | ICLR 2025 | Agent scaling law | Useful but also warns that scaling agents alone may have diminishing returns. |
| 11 | [ToolGen: Unified Tool Retrieval and Calling via Generation](https://proceedings.iclr.cc/paper_files/paper/2025/hash/b646bdebeb87dfafe2c6f77a63b564e1-Abstract-Conference.html) | ICLR 2025 | Tool calling | Suggests tool access can be learned as generation instead of external retrieval. |
| 12 | [AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents](https://proceedings.iclr.cc/paper_files/paper/2025/hash/c493d23af93118975cdbc32cbe7323f5-Abstract-Conference.html) | ICLR 2025 | Agent safety | Shows agentic capability and safety must be evaluated jointly. |
| 13 | [MAS-GPT: Training LLMs to Build LLM-based Multi-Agent Systems](https://icml.cc/virtual/2025/poster/46543) | ICML 2025 | Automatic MAS construction | Relevant to whether reviewer-agent topology can be generated from task type. |
| 14 | [ResearchTown: Simulator of Human Research Community](https://icml.cc/virtual/2025/poster/46055) | ICML 2025 | Research-agent simulation | Relevant to simulating review, writing, and collaboration workflows. |
| 15 | [TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks](https://neurips.cc/virtual/2025/poster/121705) | NeurIPS 2025 | Digital-worker benchmark | A strong benchmark-design reference for realistic agent work. |
| 16 | [MLE-Dojo: Interactive Environments for Empowering LLM Agents in Machine Learning Engineering](https://proceedings.neurips.cc/paper_files/paper/2025/hash/0603c69125ad4b964bc9c4832f7b9f8f-Abstract-Datasets_and_Benchmarks_Track.html) | NeurIPS 2025 Datasets & Benchmarks | ML engineering agents | Closest to iterative coding/experiment agents. |
| 17 | [Attractive Metadata Attack: Inducing LLM Agents to Invoke Malicious Tools](https://neurips.cc/virtual/2025/poster/116046) | NeurIPS 2025 | Tool-use security | Shows tool metadata itself is an attack surface. |
| 18 | [Memory Injection Attacks on LLM Agents via Query-Only Interaction](https://neurips.cc/virtual/2025/poster/118152) | NeurIPS 2025 | Agent memory security | Relevant to persistent review-memory poisoning. |
| 19 | [WALL-E: World Alignment by NeuroSymbolic Learning improves World Model-based LLM Agents](https://neurips.cc/virtual/2025/poster/119191) | NeurIPS 2025 | World-model alignment | Supports executable symbolic constraints around agent actions. |
| 20 | [ContextAgent: Context-Aware Proactive LLM Agents with Open-world Sensory Perceptions](https://neurips.cc/virtual/2025/poster/115593) | NeurIPS 2025 | Proactive context-aware agent | Expands proactivity beyond desktop/web states into broader context sensing. |

## Detailed Reading Notes

### 1. Graph-of-Agents

- Problem: Multi-agent LLM systems often use fixed or overly broad agent pools; irrelevant agents increase cost and can add noise.
- Method: Select relevant agents using model-card information, build a directed graph from inter-response relevance, pass messages forward and backward, then pool the final responses.
- Experiments: Evaluated on general and domain-specific benchmarks including MMLU, MMLU-Pro, GPQA, MATH, HumanEval, and MedMCQA; the reported result is that using three selected agents can outperform baselines that use all six agents.
- Limitation: The method assumes model-card/task-specialization information is meaningful and that benchmark-level response aggregation transfers to long-horizon environments.
- Relevance: This is highly aligned with cross-model code review. Our reviewer matrix should not just test all pairs; it can learn or analyze which reviewer model is useful for which bug/source/task type.

### 2. Interact-RAG

- Problem: Agentic RAG is often still black-box retrieval: the agent only rewrites queries and consumes snippets.
- Method: Adds a corpus interaction engine with action primitives, then trains an autonomous agent with synthetic trajectories, SFT, and RL.
- Experiments: Reports gains across six information-seeking benchmarks.
- Limitation: The benefit depends on exposing useful low-level retrieval controls; ordinary API search may not provide this interface.
- Relevance: For code review, this argues for giving reviewer agents structured access to code, tests, traces, and diffs rather than dumping them into one prompt.

### 3. Go-Browse

- Problem: Web agents lack enough realistic task trajectories and often do not understand site structure.
- Method: Treats exploration as graph search, reuses discoveries across episodes, and collects successful trajectories at scale.
- Experiments: Collected 10K successful trajectories and 40K interaction steps over WebArena URLs; fine-tuning a 7B model reaches 21.7% WebArena success and beats GPT-4o mini in the reported setup.
- Limitation: WebArena trajectories may not generalize to arbitrary production websites.
- Relevance: For our bug-generation problem, this suggests using failed/passed trajectories as data, not just final solutions. Each review/repair attempt can become a training/evaluation trajectory.

### 4. Proactive Agent

- Problem: Most LLM agents respond after instructions; proactive assistance needs prediction of when and how to help.
- Method: Collects human activity events, labels proactive suggestions as accepted/rejected, trains a reward model, and builds ProactiveBench.
- Experiments: The fine-tuned model reaches 66.47% F1 in proactive assistance, outperforming evaluated open and closed models.
- Limitation: Proactivity depends heavily on human preference labels and privacy-sensitive context.
- Relevance: Code-review agents could proactively flag risky generated code before tests fail, but this requires clear timing and false-positive metrics.

### 5. AgentOccam

- Problem: Web-agent failure can come from observation/action mismatch rather than weak reasoning.
- Method: Simplifies the agent by aligning webpage observations and action representations with the language patterns LLMs handle well.
- Experiments: Improves WebArena and WebVoyager performance without in-context examples, new roles, online feedback, or search.
- Limitation: The approach is domain-representation specific.
- Relevance: This is a warning against over-building multi-agent scaffolds. For code review, prompt/input representation may matter more than adding extra reviewer roles.

### 6. Web Agents with World Models

- Problem: Web agents make irreversible errors because they lack a model of action consequences.
- Method: Trains/uses world models to predict state transitions through transition-focused observation abstraction, then augments policy selection.
- Experiments: On WebArena and Mind2Web, world-model augmentation improves policy selection and is more cost/time efficient than heavier tree-search agents.
- Limitation: Natural-language transition prediction may miss low-level state changes.
- Relevance: A repair agent should predict whether a patch might break hidden tests, not only whether the current bug is fixed.

### 7. WebRL

- Problem: Strong web agents often require proprietary APIs; open models struggle with sparse rewards and limited task data.
- Method: Uses self-evolving curriculum RL: unsuccessful attempts create new tasks, an outcome-supervised reward model supplies feedback, and adaptive RL handles policy drift.
- Experiments: Llama-3.1-8B improves from 4.8% to 42.4% success; Llama-3.1-70B reaches 47.3% on WebArena-Lite.
- Limitation: RL setup and reward-model quality are expensive and environment-specific.
- Relevance: Our natural-bug pipeline can use failed generations as curriculum cases for reviewers and repairers.

### 8. SWE-Search

- Problem: Software agents are often linear and cannot backtrack from poor early decisions.
- Method: Combines MCTS, self-improvement, a value agent, a SWE-agent explorer, and a discriminator/debate agent.
- Experiments: Reports a 23% relative improvement across five models on SWE-bench compared with standard open-source agents without MCTS.
- Limitation: Search increases inference cost and may be overkill for small coding tasks.
- Relevance: This is a central related-work paper for code repair. Our work should position cross-model review as a lower-cost alternative or complement to search-heavy software agents.

### 9. AgentPrune

- Problem: Multi-agent communication graphs waste tokens and can propagate malicious or redundant messages.
- Method: Defines communication redundancy and prunes the spatio-temporal message-passing graph in one shot.
- Experiments: Maintains comparable performance with much lower reported cost and reduces token use by 28.1%-72.8%; also improves robustness under two agent-based attack types.
- Limitation: Pruning quality depends on the redundancy estimator and task setting.
- Relevance: Cross-model review should track marginal utility per reviewer, not only absolute review accuracy.

### 10. Scaling LLM-based Multi-Agent Collaboration

- Problem: It is unclear whether adding more LLM agents scales like increasing model capacity.
- Method: Uses DAG-organized MacNet topologies to coordinate many agents and studies scaling behavior.
- Experiments: Reports collaboration among over one thousand agents, irregular topologies outperforming regular ones, and a logistic collaborative scaling law.
- Limitation: Large-agent settings may be unrealistic for cost-constrained code review.
- Relevance: Useful for framing why we need controlled reviewer selection and cost-aware evaluation.

### 11. ToolGen

- Problem: Tool use through long descriptions and external retrieval does not scale to large tool sets.
- Method: Represents each tool as a token and learns retrieval/calling as generation.
- Experiments: Evaluated with more than 47,000 tools and reports improvements in tool retrieval and autonomous task completion.
- Limitation: Requires model-side training and tool-token maintenance.
- Relevance: For coding agents, tool choice can be treated as a first-class learned action instead of ad hoc prompt routing.

### 12. AgentHarm

- Problem: Agent safety is not the same as chatbot safety because tools enable multi-step harmful execution.
- Method: Creates 110 malicious agent tasks, 440 with augmentations, across 11 harm categories; evaluates refusal and post-jailbreak task capability.
- Experiments: Finds that leading models can comply with harmful agent requests and that universal jailbreak strings can remain effective in agentic settings.
- Limitation: Safety benchmarks may lag real tool ecosystems.
- Relevance: Our paper should avoid evaluating only correctness. Agent review/repair can introduce new risks, especially when tools execute code.

### 13. MAS-GPT

- Problem: Manually designing multi-agent systems is expensive and brittle.
- Method: Reframes MAS construction as code generation from user query to executable MAS; trains a medium-sized model on consistent query-MAS pairs.
- Experiments: ICML page reports query-adaptive MAS generation in a single inference.
- Limitation: Generated systems require strong correctness and safety checks.
- Relevance: Future work: automatically generate reviewer-agent workflows based on task and bug type.

### 14. ResearchTown

- Problem: Scientific communities involve reading, writing, and reviewing interactions that are hard to study at scale.
- Method: Models a research community as an agent-data graph and uses TextGNN-style message passing over research activities.
- Experiments: Reports realistic simulation of collaborative research, robust multi-researcher/paper behavior, and interdisciplinary idea generation.
- Limitation: Simulated research quality is hard to validate against real scientific novelty.
- Relevance: Useful background for our goal of writing and reviewing a paper with agent assistance, and for modeling peer-review-like agent behavior.

### 15. TheAgentCompany

- Problem: Agent benchmarks often lack consequential real-world work tasks.
- Method: Builds a self-contained software-company environment where agents browse, write code, run programs, and communicate with coworkers.
- Experiments: The strongest baseline agent completes about 30% of tasks autonomously.
- Limitation: A benchmark company is still a controlled environment and may not cover production variance.
- Relevance: This is a strong benchmark-design reference: our experiments should include realistic workflows, not only isolated HumanEval-style functions.

### 16. MLE-Dojo

- Problem: ML-engineering agents need iterative experimentation, debugging, and feedback, but many benchmarks are static.
- Method: Provides a Gym-style environment over 200+ Kaggle-style challenges with executable feedback loops.
- Experiments: Evaluates eight frontier LLMs and finds they improve iteratively but remain weak on long-horizon solutions and complex error resolution.
- Limitation: Kaggle-like tasks emphasize ML pipelines more than general software maintenance.
- Relevance: Supports our choice to record execution feedback, hidden tests, and repair trajectories instead of only final patch accuracy.

### 17. Attractive Metadata Attack

- Problem: Tool metadata itself can steer agents toward malicious tools.
- Method: Constructs syntactically and semantically valid tool metadata through black-box iterative optimization.
- Experiments: Reports 81%-95% attack success across ten simulated tool-use scenarios, with privacy leakage and limited effect on primary-task completion.
- Limitation: Simulated tool ecosystems may simplify real tool governance.
- Relevance: Our agent framework should treat tool descriptions, model labels, and reviewer-role descriptions as part of the threat surface.

### 18. Memory Injection Attacks

- Problem: Agents with memory can be poisoned without direct memory access.
- Method: Uses query-only interactions to cause malicious records to be stored and later retrieved; bridging steps link victim queries to malicious reasoning.
- Experiments: Shows memory compromise across diverse agents.
- Limitation: Details depend on memory-write and retrieval policies.
- Relevance: If we maintain long-term review memory, it must separate trusted experiment records from model-generated rationales.

### 19. WALL-E

- Problem: LLM world models may not match environment dynamics.
- Method: Extracts symbolic action rules, knowledge graphs, and scene graphs from trajectories, encodes them as executable constraints, and uses an MPC-like planning loop.
- Experiments: Reports large gains in Mars/Minecraft-like and ALFWorld settings, including 98% ALFWorld success after four iterations.
- Limitation: Symbol extraction can be brittle; not all domains expose clean symbolic dynamics.
- Relevance: For code review, executable tests and static checks can play the role of symbolic environment constraints around LLM reasoning.

### 20. ContextAgent

- Problem: Proactive agents need richer context than closed UI states or hand-written notification rules.
- Method: Extracts multidimensional sensory context, uses historical persona information, predicts whether assistance is needed, and calls tools unobtrusively.
- Experiments: ContextAgentBench has 1,000 samples across nine scenarios and twenty tools; reported gains are up to 8.5% for proactive prediction and 6.0% for tool calling.
- Limitation: Privacy and sensor-noise issues are central.
- Relevance: For coding agents, context could include recent edits, failing tests, bug history, and developer intent; but false-positive interruption cost must be measured.

## Cross-Paper Synthesis

### Method Trends

1. Agent research is moving from prompt-only scaffolding to structured execution: graphs, search, world models, tool primitives, memory, and executable environments.
2. Multi-agent gains depend on topology and selection. More agents are not automatically better; relevance, communication pruning, and cost-aware routing matter.
3. Web and software agents increasingly rely on environment feedback loops. Static QA-style evaluation is insufficient for long-horizon agent behavior.
4. Training data is shifting from human-written demonstrations to trajectory mining, failed-attempt curricula, synthetic interaction data, and environment rollouts.
5. Safety failures are agent-specific. Tools, memory, and metadata create failure modes that do not appear in ordinary chatbot evaluation.

### Implications for Our Cross-Model Code Review Paper

The literature supports the core direction, but the paper should avoid claiming that "more models reviewing each other" is enough. A stronger framing is:

- Treat code generation, review, repair, execution, and hidden-test feedback as an agentic workflow.
- Study cross-model complementarity under cost constraints.
- Separate bug source types: interface/specification, logic/boundary, controlled mutation, false positive, and repair regression.
- Measure both correctness and failure side effects: false positives, unnecessary repairs, regressions, cost, and latency.
- Use execution feedback as a lightweight world model: reviewer judgments should be checked against tests and repair outcomes.

### Gaps We Can Exploit

- Many agent papers optimize task success, but fewer isolate reviewer reliability in code-generation pipelines.
- Multi-agent papers often report aggregate benchmark gains without analyzing bug categories and cross-model disagreement.
- Safety papers focus on malicious behavior; there is room to study benign but harmful reviewer actions, such as false-positive repairs that break passing code.
- Software-agent papers often emphasize final SWE-bench solve rate; our narrower setting can provide more interpretable causal evidence about where cross-model review helps or hurts.

## Reading Protocol

For each included paper, record:

- Venue and acceptance status.
- Paper link and source used for verification.
- Research problem.
- Core method.
- Experimental setup and main findings.
- Limitations or threats to validity.
- Relevance to cross-model code review, coding agents, or agent reliability.

Workshop, preprint, or withdrawn papers may be tracked as background candidates, but they are not counted toward the target set unless the user explicitly broadens the scope.
