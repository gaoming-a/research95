# Agent 新课题反向新颖性筛选协议

- 日期：2026-07-25
- 状态：`round_1_complete_one_yellow_candidate_no_topic_lock`
- 范围：只做公开来源检索、主张拆解、先验碰撞审查和纸面实验设计
- 禁止：研究数据构造、模型/API 调用、训练、pilot 和论文实证结论

## 1. 目的

只向作者展示已经通过直接近邻反证的 Agent 课题。不得先给课题名称、再在实施后发现相同
方法已经被论文或公开代码实现。

## 2. 已关闭路线

- EviRepair：独立审计结论为 `NO_GO_ABANDON_EVIREPAIR`；
- CEC/RC 失败归因总体主效应；
- 单一会话上下文偏执；
- Same API, Changed Contract；
- 纯 benchmark、纯系统拼装和以阴性/边界结论为主要毕业贡献的路线；
- 通信领域。

上述路线不得通过改名、换 benchmark 或增加多个已知模块重新进入候选池。

## 3. 反向筛选顺序

每个候选必须按以下顺序处理：

1. **机制拆解**：用一句话写出输入、可学习或可控制变量、更新机制和输出；
2. **语义同构检索**：不用候选自定义名称，分别检索任务、机制、训练信号、路由/记忆/验证
   形式和评价目标的同义表达；
3. **邻域扩展**：检查 2024--2026 arXiv、ACL Anthology、PMLR、OpenReview、主要会议官网
   和作者代码；
4. **代码反证**：检查论文仓库、框架插件和 benchmark baseline 是否已实现同一核心箭头；
5. **组合反证**：即使没有单篇完全相同，也检查两篇直接近邻是否已经自然拼出候选方案；
6. **reviewer 攻击**：回答“为什么这不是已有方法换域、换标签、换模型或多加一个 Agent”；
7. **结果与时限审查**：只有具有独立 oracle、明确优化目标、可用强基线、短期正向改进空间
   和硕士扩展链的候选才可入围。

任一步发现同构机制，立即淘汰并记录碰撞来源，不进入最终推荐清单。

## 4. 入围必须提供的证据

每个最终候选必须同时给出：

- 最接近的三项工作及其公开代码状态；
- claim-to-prior-art 差分：已有工作、候选独有机制、不能声称的内容；
- 一个可独立消融的最小创新单元；
- 等预算最强基线，而不是弱 prompt baseline；
- 独立成功 oracle、样本单位、主指标和错误改进保护指标；
- 7--10 天内可完成的低成本 pilot；
- 明确 Go/No-Go 阈值；
- EI 小论文核心和硕士论文扩展之间的工作量映射；
- 2026-08-31 前形成论文的时间风险。

## 5. 当前验收

- 优先生成较大的机制候选池，不承诺所有候选存活；
- 最终目标是形成不少于 5 个经过两轮反证的候选；若不足 5 个，必须明确报告实际幸存数量，
  不得降低新颖性标准补足数量；
- 不调用模型/API，不训练，不运行实验；
- 完成后更新当前计划、文档索引和经验记录，并同步 GitHub。

## 6. 第一轮候选池与淘汰结果

第一轮没有得到 5 个可直接推荐的候选。以下方向均已在公开论文、代码或产品工作流中发现
核心箭头碰撞，不能通过换名或增加 Agent 重新进入：

| 候选机制 | 结论 | 主要碰撞或结构性原因 |
|---|---|---|
| Spreadsheet 目标区域发现后再做公式修复 | 淘汰 | Spreadsheet-RL 的任务输入已直接给出目标工作表和范围，原设想的主要困难并不存在 |
| 从需求自动生成测试并回写规格歧义 | 淘汰 | ClarifyGPT、TiCoder、测试驱动开发 Agent 与 TDFlow 已覆盖澄清、测试生成和闭环修订 |
| 规格决策账本与需求到代码/测试追踪 | 淘汰 | Kiro/spec-driven development 与 TraceDev 已把持久规格和 traceability 做成公开系统 |
| PPT 来源归因、局部更新和版本传播 | 淘汰 | DynaSlide、SlideAgent、Adobe attribution、LayerProof 及公开 deck-update 工作流已占据核心链 |
| 通用失败类型路由与验证修复 | 淘汰 | AgentDebugX 等近期工作已覆盖失败归因、证据采集、类型路由、定向修复和重跑 |
| PR 测试覆盖感知修复 | 淘汰 | coverage-guided prompting、TestAgent 及 2026 年覆盖感知 coding-agent 工作已直接进入该问题 |
| PDB 精确修复训练 | 淘汰 | PDB 暴露的低 precision 缺口已由 QiMeng-PRepair 的 edit-aware GRPO 直接处理并报告正向结果 |
| 用约定 hard negatives 做普通 SFT/DPO | 淘汰 | AP2O-Coder 已按错误类型渐进做 preference optimization；InferFix、CodeUltraFeedback 等已覆盖 bug-type/执行反馈训练。仅换成科学代码约定不是新方法 |

这一结果不等于“所有 Agent 课题都已完成”，只说明上述主张形式在本项目的时间和创新要求下
不再值得下注。

## 7. Imaging-101 公开基准完整性复核

初始检索命中了不完整的旧仓库 `AI4ImagingLab/imaging-101-release`，其中看不到逐任务测试。
继续追溯 README 后确认正式公开仓库是
[`starpacker/inverse-101`](https://github.com/starpacker/inverse-101)，不能再依据旧仓库误判
数据不可用。

对正式仓库 `main@fb263c4` 做只读 sparse checkout 后得到：

- 57 个任务目录；
- 56 个任务含测试，唯一无测试任务为 `shack-hartmann`；
- 245 个 `test_*.py`；
- 314 个 `src/` Python 文件；
- 41 个文件精确命名为 `generate_fixtures.py`；
- 公开 GitHub 当前只有 `main` 分支，无公开 issue；
- 仓库代码检索未发现 convention-repair、residual-diagnosis 或 adapter-synthesis 实现。

人工复核 `conventional_ptychography`、`electron_ptychography` 和 `mri_sense`，确认真实代码中
存在 centered FFT、`fftshift/ifftshift`、`norm="ortho"`、复共轭和 adjoint 等约定敏感
操作，不是只靠论文中的一个 MRI 个案构造候选。

论文
[`Imaging-101`](https://arxiv.org/html/2607.10789)
报告 57 个任务、严格数值 fixtures 和明显的总体 headroom；其失败分析把 42.1% 的失败
`(task, model)` 对归为 numerical-convention drift，并明确列出 sign、scale、axis ordering
和 normalization。论文建议 verified skills，但没有实现从数值偏差诊断约定并自动修复的
系统。

## 8. 数值约定修复候选的三层碰撞审查

### 8.1 已有问题与基准

- Imaging-101 已定义并实证了 numerical-convention drift；
- AInsteinBench、petscagent-bench、Chain of Unit-Physics、Agentic Diagrammatica 等已说明
  科学代码中的物理约束、库约定和验证问题；
- 因此不能声称首次发现科学 coding agent 的约定错误，也不能把增加一个 verifier 当作创新。

### 8.2 已有机制与代码

- [`FACC`](https://github.com/FourierACceleratorCompiler/FACC) 已从 I/O 样例合成 FFT
  drop-in adapters。其公开 DSL 直接含 `FSBitReversal`、`FSNormalize`、
  `FSHalfNormalize`、`FSDenormalize` 和 `FSHalfDenormalize`。因此“枚举 FFT 约定并让
  输出匹配”已经被实现，不能作为本课题创新；
- [`LearnSy`](https://doi.org/10.1145/3586055) 已研究 OGIS/CEGIS 中如何选取高效的
  distinguishing question；主动选择诊断输入或以信息增益减少查询本身不是新算法；
- [`Oracle-Free Repair Synthesis for Floating-Point Programs`](https://doi.org/10.1145/3563322)
  已根据浮点误差 micro-structure 做全自动修复；高浮点误差修复不是本候选可占据的主张；
- [`AutoMR`](https://doi.org/10.1109/ICSME.2019.00035) 已自动发现 numerical
  metamorphic relations；数值关系发现也不能单独作为贡献；
- Google 的公开张量程序合成专利已经从 I/O 例子枚举 transpose、slice、norm 等算子。
  “对张量输出搜索一个变换”不是尚未实现的空白；
- 通用 APR 的模板、动态上下文、执行反馈、最小补丁、过拟合检测和信息增益排序均有直接
  先验工作。

### 8.3 现有预防系统

[`get-physics-done`](https://github.com/psi-oss/get-physics-done) 的公开代码含 18 字段
convention lock、`convention_set/check/diff`、`ASSERT_CONVENTION` 和 subfield defaults。
它是声明式、预防式一致性锁：不从数值残差推断约定，不定位 agent 生成代码中的约定漂移，
也不自动生成修复。它不是直接同构实现，但必须成为强基线。

SciLink 已提供可插拔科学 skills、失败后 updater 和可持久化的 skill distillation。因而
“给 Agent 增加科学技能库”也不能成为候选的最小创新单元。

## 9. 当前唯一幸存候选：黄色，不锁题

暂用描述名：

> 面向科学 coding agent 的残差结构约束数值约定诊断与最小边界修复。

它只有在下述最小箭头保持完整时才可能与近邻区分：

> failing numerical fixture + agent code → residual-structure signature →
> typed convention-equivalence class and ambiguity margin → convention-specific
> code boundary localization → one minimal boundary edit → unseen-fixture
> validation or abstention.

必须同时具备：

1. **残差结构诊断**：不是穷举每个 adapter 后看谁通过，而是由比例场、频谱位移、轴对应、
   相位/共轭关系等 residual signature 先形成可审计的失败归因；
2. **代码边界定位**：输出一个与约定操作对应的具体边界位置，不能只在最终输出后包一层
   万能 adapter；
3. **歧义拒绝**：多个约定假设无法由当前证据区分时必须 abstain，不能返回第一个过可见
   fixture 的补丁；
4. **独立验证**：诊断 fixture 与新 seed/新实例验证必须隔离，避免测试过拟合；
5. **Agent 增量**：在相同执行和 token 预算下，证明该工具给 coding agent 带来的额外
   修复成功，而不是只证明一个确定性枚举器能修人为 mutation。

即使满足这些条件，可声称的也只是“约定特定的可解释诊断与受约束修复”，不能声称首次
adapter synthesis、首次 CEGIS、首次主动 question selection、首次 numerical APR、首次
科学 Agent 验证或首次最小补丁。

### 当前评级

- 基准与公开资产：绿色；
- 可执行 oracle 与正向 headroom：绿色；
- 未发现端到端直接实现：暂时绿色；
- 机制独立于已有组成件：黄色；
- 2026-08-31 前完成：黄色；
- 最终结论：**条件候选，不锁题，不进入实验**。

FACC 加 LearnSy/通用 APR 已能自然拼出候选的大部分步骤。若后续纸面机制仍可被描述为
“FACC 换成 Python 科学代码，再接一个 coding agent”，该候选必须淘汰。

## 10. 若后续获准实验，预先冻结的最短证据链

当前没有实验授权；本节只定义未来 Gate，不能解释为已经选样或获得正向结果。

- 先按代码/测试结构冻结 10--12 个任务，不按模型运行结果选题；
- 自然 agent failures 与受控 convention mutations 分开报告；
- 诊断使用一个公开/训练 fixture，最终验证使用 reference generator 产生的隐藏新 seed，
  且 reference body 不向待测 agent 暴露；
- 最强基线至少含 Imaging-101 原始反思、通用 APR、静态 skill、GPD-style convention lock、
  FACC-style exhaustive adapter synthesis 和普通 OGIS question selection；
- 主指标为自然约定失败上的 held-out repair success；同时报告 full-task success、错误修改率、
  abstention precision、编辑大小、oracle/test 调用数和 token；
- 受控 mutation 只用于识别覆盖率和机制消融，不得替代自然失败主结果。

若允许 7 天 no-API feasibility pilot，Go 条件至少应包括：

- 预冻结任务中能机械表示至少 4 类约定且不是全部退化为最终输出 adapter；
- 相对 FACC-style exhaustive baseline 明显减少查询或错误编辑，并在隐藏 seed 上不降低
  patch validity；
- 至少 5 个自然约定失败可复现，且不是只靠一个 MRI root；
- 若仅 controlled mutations 有效、自然失败不足，或强基线达到近饱和，立即 No-Go。

## 11. 第一轮结论与下一步

截至 2026-07-25 的公开证据闭包中，第一轮实际幸存数量是 **1 个黄色候选、0 个绿色候选**。
这比给出五个未经反证的题目更符合作者“不要实施后才发现已做过”的要求。

下一轮仍只做公开来源筛选：

1. 不再继续包装普通约定枚举、普通主动查询或普通 DPO；
2. 从 2026 年新发布、低基线且有完整 executable oracle 的 Agent benchmark 重新扩候选池；
3. 每个新候选先查 paper、code、issue/branch、产品工作流和两篇近邻组合；
4. 只有机制级反证通过后，才与本节黄色候选比较并请求作者锁题。
