# APSEC/CCF-C 证据有效性修复与投稿总计划

计划编号：APSEC-CCFC-VALIDITY-20260710
制定日期：2026-07-10
当前状态：P1_LEGACY_PROMPT_RETIREMENT_COMPLETE；STOP_PENDING_G0_AND_COHORT_FEASIBILITY
默认目标：APSEC 2026 Technical Track，按用户指定的 CCF-C 目标评估
论文类型：受控实证方法研究
研究目标选择：A——研究可见证据如何改变 accept/reject/escalate policy，
不把实验定义为 verifier correctness 证明
本轮边界：按用户明确授权物理删除四个旧 EVP-8 prompt；不改论文、不生成
新 prompt、不运行实验、不调用 API

2026-07-10 执行修订：用户明确要求删除全部旧 EVP-8 prompt。该决定覆盖本计划
原先“保留且不修改旧 prompt”的安排。四个旧模板从活动工作树物理删除；其原始
字节仍由既有 Git 提交保存，删除前 SHA-256 和退休原因写入 prompt change log。
旧 protocol、manifest、run packet、result 和 audit 中的 prompt path/id/hash 作为
历史 provenance 保持原样，不得改写。任何旧 config/runner 都只允许用于历史
代码审计，不再是执行入口；不得把它们静默改指向未来 v0.4 prompt。

## 1. 本计划的权威性

本文件是后续论文修复和投稿工作的唯一主计划。docs/plans/current_plan_zh.md
只记录每一轮的执行日志；旧 roadmap、旧实验 packet、旧 claim map 和旧审计报告
只提供历史证据，不能覆盖本计划的门禁。

后续每轮必须按以下闭环执行：

1. Inspect：检查工作区、当前计划、上一轮产物和审计结果。
2. Plan：只激活本计划中的一个阶段，写清输入、边界和验收条件。
3. Execute：只做该阶段允许的动作。
4. Verify：每个关键动作后立即做最小验证。
5. Diagnose：失败时先区分执行链、实验设计、数据证据、论文 claim、API
   或投稿规则问题。
6. Repair：只修根因，不加兼容层，不用旧结果兜底。
7. Sync Docs：更新 current_plan_zh.md、current_project_state_zh.md、
   engineering_notes.md、INDEX.md 和 README。
8. Gate：阶段验收未通过时不得进入下一阶段。
9. Commit And Sync：只提交本阶段相关文件并检查敏感信息；只有 G0 确认的
   venue-compliant private/anonymized GitHub remote 才允许推送。

## 2. 第一性原理结论

当前论文的主要问题不是英文、页数或图表，而是中心 claim 不能由独立、无泄漏、
可复算的确认性证据支持。必须先修实验识别和统计单位，再写论文和排版。

本计划锁定五条原则：

- 旧 current-98、EVP-8-HARD、coverage-contestation 和 stress-31 结果全部降级为
  protocol-development / exploratory evidence，不进入新论文的确认性统计。
- 不在旧 v0.3 packet 上继续打补丁。新实验使用全新的 EVP-v0.4 命名空间、
  schema、prompt、cohort、分析和有效性审计。
- 不再把 verdict 当作证据阶梯的一部分。证据 bundle 和 synthetic advisory cue
  必须是两个正交变量。
- 不把 candidate、repeat 或 model 当作独立样本。task 是唯一主抽样单位，
  project 是上层聚类单位。
- 截止日期不能降低科学门槛。任一硬门未通过就停止 APSEC 2026 路线，由用户另行
  决定目标，不提交已知无效的版本。

## 3. 投稿规则快照与 G0 硬门

官方 Technical Track 页面：
https://conf.researchr.org/track/apsec-2026/apsec-2026-technical-track

截至 2026-07-10，官方页面写明：

- 可选摘要截止：2026-07-13；
- 全文截止：2026-07-20；
- 英文 PDF、A4、IEEE conference 格式、正文 10 pt；
- 参考文献计入最多 10 页；
- 双盲；
- 录用论文提交 IEEE Xplore；
- 生成式 AI 只允许轻微语言辅助；不得用于实质生成原创研究内容、科学 claim、
  实验结果、分析或论文文本。

官方页面没有承诺 EI Compendex 收录。因此“EI”只能在学校认可要求和正式检索
来源中单独核实，不能把 IEEE Xplore 等同于 EI。

### G0 必须由作者确认的五件事

| 决策 | 必须提供的确认 | 未通过时 |
|---|---|---|
| G0.1 目标 | APSEC 2026 Technical Track 是否仍是本轮唯一主目标 | 停止 venue-specific 执行 |
| G0.2 AI 原创性 | 作者能否如实证明研究思想、方法、结果解释、结论和投稿文本由作者形成；并盘点现有 AI 参与 | 无法满足官方政策时停止 APSEC 路线 |
| G0.3 政策澄清 | 若现有 AI 参与超过轻微语言辅助，作者须先获得 Program Chairs 的书面解释 | 未澄清前不得继续 APSEC 科学内容与正文工作 |
| G0.4 时间与成本 | 接受本计划的硬门、最晚节点和后续 API 成本审批机制 | 不以缩样、删验证或复用旧数据赶截止 |
| G0.5 匿名期与公开仓库 | 审计 2026-06-20 后身份关联公开 GitHub 更新；取得 Program Chairs 意见，并确定 private/anonymized GitHub 同步位置 | 未解决前禁止新的公开 push，且不得把 APSEC 路线标为合规 |

G0 的通过状态必须写入新的 venue/provenance decision record。没有作者确认，
后续只能做只读审计和无 API 的机械检查。

本总计划本身包含由 Codex 提出的实质实验设计建议，不能被直接视为“作者独立形成
的方法学”。若目标仍是 APSEC 2026，作者必须在 G0 中如实披露这一事实，独立
审查和形成自己的方法学决定，并在需要时取得 Program Chairs 的书面许可；否则
本计划只能用于选择其他允许该类辅助的目标，不能作为 APSEC 投稿流程。

当前 origin 是身份关联的公开仓库，且 APSEC 匿名期自全文截止前一个月开始。
这与项目“每次更新必须 GitHub 同步”的规则形成直接冲突。唯一可继续 APSEC
且同时保持 Git 同步的路径，是由用户先提供或批准 venue-compliant private/
anonymized GitHub remote；不得自行改变仓库可见性、创建外部仓库或继续向当前
公开 remote 推送 APSEC-facing 更新。

### APSEC 路线中的统一 AI fail-closed 边界

在 G0.2/G0.3 未取得书面澄清前，该边界覆盖 P0--P12，而不只覆盖正文：

- Codex 可以做仓库检查、确定性一致性检查、格式检查和计划记录；
- Codex 不得替作者完成文献综合、novelty 判断、prompt/schema/统计设计、
  candidate 选择、实质分析链选择、结果解释、scientific claim 或投稿正文；
- 不把本计划中的拟议表述直接复制到论文；
- “轻微语言辅助”只包括作者原句的拼写、语法和局部清晰度修正，不包括翻译、
  段落重构、claim 改写、摘要重写或相关工作综合；
- 模型作为研究对象的实验调用与生成式 AI 作为作者工具必须在记录中明确区分；
- P2、P3、P4、P5、P9、P10 的科学判断和实质实现由作者完成；若 Program
  Chairs 书面允许更广 AI 辅助，必须逐项记录允许范围；
- 最终科学论证和正文必须由作者亲自形成、核验并承担责任。

## 4. 目标论证与 claim 边界

### 4.1 暂定的一句话研究问题

在未参与协议开发、task-disjoint 且包含预注册 project-held-out 子集的受控补丁
集合上，逐步公开真实可执行证据 bundle 以及加入正交的 synthetic advisory cue，
会如何改变多个
LLM verifier 的
accept/reject/escalate policy，以及这种变化在错误接受、正确接受和
protocol-level non-escalation rate 之间形成什么权衡。

这只是实验设计目标，不是当前已经成立的论文结论。

### 4.2 允许形成的 claim 类型

- 受控 cohort 内的 task-level 描述性结果；
- balanced controlled cohort 内，同一 task/candidate/model 下 C0 对 C3 的
  bundled cumulative evidence-condition decision-distribution difference；
- 相同 C3 底层证据下 synthetic advisory cue 的配对条件差异；
- 模型间和重复运行间的异质性；
- deterministic visible-tool 与 always-escalate 等基线揭示的风险—覆盖权衡。

### 4.3 禁止预设的 claim

- autonomous patch correctness verification；
- 通用 verifier superiority；
- “首次”“唯一”或“现有研究通常忽略”，除非最近邻文献矩阵直接支持；
- deployment safety、真实部署 prevalence 或总体 precision；
- bundled C0→C3 effect 归因到某一个单独字段；
- synthetic cue effect 等同于真实工具影响或心理学意义的 anchoring；
- escalation 等同于 semantic rejection 或 correctness；
- IEEE Xplore 等同于 EI；
- 使用旧 exploratory 结果形成新确认性 CI、p 值或合并样本。

## 5. 术语账本

| 规范术语 | 唯一定义 | 禁止混用 |
|---|---|---|
| model-visible evidence | 模型作出决策前实际可见且已物化的字段 | hidden evaluator label |
| hidden evaluator | 所有模型输出冻结后才连接的 correctness oracle | model-visible test |
| evidence bundle | C0→C3 累积加入的预定义真实证据集合 | 单字段因果效应 |
| synthetic advisory cue | 与 C3 底层证据正交、明确标为合成且不可信的 NONE/ACCEPT/REJECT 字段 | 真实 tool verdict 或 hidden truth |
| accept | 模型建议自动接受候选补丁 | correctness |
| reject | 模型明确拒绝候选补丁 | escalate |
| escalate | 路由给人工或更多工具，不作语义判断 | safe/correct |
| false accept | hidden-negative candidate 被 accept | 所有非 reject |
| correct accept | hidden-positive candidate 被 accept | recall 的无条件泛化 |
| protocol-level non-escalation rate | 本协议内 accept 或 reject 的比例 | 部署 automation coverage |
| task-level inference | 每个 task 先汇总候选和重复，再进行推断 | candidate-level n |
| exploratory evidence | 用于设计、动机和故障说明的旧结果 | confirmatory evidence |

新 prompt、schema、分析、claim map 和论文必须复用这套术语。任何新增同义词都先
更新账本。

## 6. 锁定的确认性实验设计

### 6.1 Cohort

- 30 个确认性 held-out tasks。
- 至少 8 个 projects，每项目最多 4 个 tasks。
- task 不得与 current-98、EVP-8-HARD、coverage、stress-31、realistic-agent
  或任何旧 verifier 实验重叠。
- 至少 15 个 tasks 来自至少 4 个从未进入旧 verifier 实验的 projects。
- 在候选构造前冻结 40 个 task 的有序名单：前 30 个 primary，后 10 个 reserve。
- reserve 只能在任何 verifier 输出产生前，按冻结顺序替换环境或 oracle
  不稳定的 task；看到 verifier 输出后禁止替换或补样。

### 6.2 每个 task 的同源候选对

每个 task 恰好两个候选，共 60 个候选：

1. oracle-positive：以参考修复为源，在两个干净环境中通过 apply、静态检查、
   visible tests 和完整 hidden oracle。
2. hard negative：从同一参考修复按预注册的确定性变换顺序构造；通过全部
   model-visible checks，但至少一个独立 hidden behavior/regression oracle
   稳定失败。

候选变换顺序、选择规则和失败原因在任何 verifier 调用前冻结。不得人工选择
“更有论文效果”的候选。无法形成稳定候选对的 task 在冻结前按 reserve 顺序替换。

每个 task 必须先冻结并哈希 visible/hidden oracle split、命令和判定规则，再冻结
transform registry，最后才允许物化候选。候选物化后修改任一 oracle 的 task
立即作废，只能在任何 verifier 输出前按 reserve 顺序替换。

该集合明确称为 balanced controlled challenge cohort，不估计真实部署中的
正确/错误补丁比例。

### 6.3 四级真实证据

所有字段必须实际执行和物化；不允许空数组冒充证据，也不允许 not_run 或
not_recorded 进入 model-visible packet。

| 条件 | 新增的真实可见证据 |
|---|---|
| C0 context | issue/task 描述、candidate diff、必要的代码上下文 |
| C1 executable-basic | C0 + patch apply、syntax/import/static 命令与真实结果 |
| C2 bug-focused | C1 + 预注册 visible F2P 测试名称、命令和真实结果 |
| C3 regression-aware | C2 + 预注册 visible P2P/regression 测试名称、命令和真实结果 |

hidden oracle、hidden label、候选来源标签、构造类型和 reference-patch 标识均不得
出现在 model-visible packet 或 rendered prompt。project/task identifier 改为
冻结的中性代码；两个候选的 diff header、路径展示和格式规范完全相同。

公开 benchmark 的训练污染无法被证明为零。P3 必须冻结、P4 必须执行
reference-contamination audit：

- 删除 project、task、commit、issue URL 和可反查标识，只保留判断所需的中性
  代码上下文；
- 对 normalized diff 与公开 reference/history 做 exact/subsequence similarity
  inventory，并确认所有条件对同一 candidate 暴露完全相同的语义内容；
- 记录 positive 来自公开 reference、negative 为其确定性变体这一已知风险；
- primary estimand 只允许是同一 candidate 的 C0↔C3/C4/C5 条件差异，因为静态
  memorization signal 在配对条件间保持不变；C0 absolute accuracy 和
  positive-vs-negative 差异只能描述，不得证明 verifier correctness；
- 若任一条件包含额外 reference/source cue，或语义/来源信息在配对条件间不一致，
  立即停止；不得用 threats 文案掩盖可修复泄漏。

### 6.4 正交 synthetic advisory cue 干预

在 C3 的底层证据完全不变、prompt 完全相同的前提下增加两个条件：

- C4：synthetic_advisory_cue=ACCEPT；
- C5：synthetic_advisory_cue=REJECT。

C0--C3 使用同一 schema 的 synthetic_advisory_cue=NONE。C3/C4/C5 唯一允许的
差异是该字段值。prompt 明确说明该 cue 是合成、不可信且可能错误的实验字段；
它不伪装成 tool 或 hidden truth，不携带 reasons、counts、source_decision
或其他 verdict-like 字段。

这取代旧 E6-no-verdict 设计。coverage-contestation prompt 不进入确认性主实验，
只保留为旧 exploratory 证据。

### 6.5 模型、重复和调用数

- verifier models：Qwen、DeepSeek、Gemini 三条已使用路线，但在执行前必须冻结
  精确 model ID、provider、日期、temperature、reasoning control、token cap、
  retry 和 fallback policy。
- 每个 model × candidate × condition 独立运行 3 次；每次 stateless，不共享上下文。
- 六个条件按冻结的交错随机顺序执行，避免整块条件与服务时间漂移混淆。
- 确认性 planned unique requests：30 tasks × 2 candidates × 6 conditions
  × 3 models × 3 repeats = 3240。
- API smoke 只使用不属于确认性 cohort 的 development fixtures：
  2 fixtures × 6 conditions × 3 models = 36 planned unique requests。
- transport/empty-response 每条最多 retry 一次，且全局 retry budget 为 planned
  unique requests 的 5% 向上取整：smoke 最多 2 次 retry、hard maximum 38
  attempts；full 最多 162 次 retry、hard maximum 3402 attempts。
- 达到 global retry budget 立即停止；不得把理论 6480 attempts 当作隐含授权。
- smoke 和 full run 必须分别获得用户明确授权；本计划本身不构成 API 授权。

### 6.6 输出

唯一决策 schema：

- decision：accept、reject 或 escalate；
- concise rationale；
- evidence fields used；
- uncertainty/coverage concern；
- schema version、prompt hash、packet hash、model/provider metadata。

存储分为两个边界：

- private raw：raw response、带原始路径/标识的 patch、rendered prompt、
  credential 和 local config，只保存在 ignored outputs/evp_v0_4/private；
- anonymous scientific inputs：normalized candidate patches、model-visible
  packets、oracle commands、environment lock、sanitized decisions 和分析脚本，
  staging 在 artifacts/evp_v0_4_anonymous；只有完成 license、identity 和
  double-blind audit 后，才进入 G0.5 批准的 private/anonymized GitHub remote
  或匿名 archive。

当前 identity-linked public repository 已包含历史论文和部分 scientific
materials，必须在 G0.5 中完整盘点；G0.5 未通过前不新增任何公开 tracked
artifact 或 APSEC-facing commit。

## 7. 预注册统计分析

### 7.1 推断单位

- 唯一主抽样单位：task。
- 两个 candidates、三个 repeats、六个 conditions 和三个 models 都嵌套在 task 内。
- 每模型单独报告 n=30 tasks。
- 三模型汇总仍重采样同一批 30 tasks，禁止写成 n=90。
- 三次 repeat 用来估计 task/model/condition 的决策概率和 disagreement，
  禁止当作三个独立样本。

### 7.2 主要指标

- hard-negative false-accept probability；
- oracle-positive correct-accept probability；
- escalation probability；
- strict-reject probability；
- protocol-level non-escalation rate，即 accept+reject；
- repeat disagreement rate。

cohort-conditional accepted precision 只能是次要描述指标。

### 7.3 主要比较

1. Evidence-bundle family：hard negative 的 accept probability 差异
   C3−C0，以及 positive 的 accept probability 差异 C3−C0；二者是同一
   Holm family。
2. Synthetic-cue family：分别对 hard negative 和 positive 计算
   C4−C3、C5−C3 的 accept probability 差异，共四个冻结标量，组成第二个
   Holm family。
3. reject、escalate 和 protocol-level non-escalation rate 的分布变化是
   secondary outcomes。
4. Adjacent C0→C1→C2→C3 只作 bundle 梯度的次要描述，不归因到单个字段，
   不做确认性显著性声明。

### 7.4 区间与检验

- estimand：对冻结 cohort 中 30 个 task 等权的 within-cohort condition
  difference；
  不外推为项目总体或部署总体效应。
- 点估计：task macro-average；同时报告 project-level task means，但不把
  projects 等权替代主 estimand。
- 主要 95% CI：以 project 为 cluster 的 wild-cluster bootstrap-t，Rademacher
  weights，固定 9,999 次；每个 project 的 cluster contribution 固定为
  g_j=(n_j/30)×mean_task(d_ij)，保证 contributions 之和等于 task-macro
  effect；studentized statistic 固定为 T=effect/SE_CR2。
- 主要双侧检验：对上述 task-count-weighted project cluster contributions 做
  sign-flip；project 数不超过 15 时枚举全部 2^J 个符号组合，否则固定
  10,000 次。project→task hierarchical bootstrap 只作敏感性分析。
- 上述两个冻结 family 分别采用 Holm correction。
- 报告 leave-one-project-out 方向稳定性。
- 在任何 verifier API 前，对 J≥8、n=30 和 ICC=0.05/0.15/0.30 做冻结的
  precision simulation；若预期 CI 宽度不能达到下述门限，停止 APSEC 路线，
  不先花 API 成本再决定样本量。
- primary rate 的 95% CI 总宽度大于 0.35，或 paired effect CI 总宽度大于
  0.30 时，结论标记为 inconclusive；不得看结果后追加样本直到显著。
- 不设置“结果必须正向”的通过门。零效应或负结果仍可报告，但必须按预注册边界解释。

### 7.5 基线

所有基线在同一 30-task cohort 上计算：

- always-accept；
- always-reject；
- always-escalate；
- visible-test threshold；
- deterministic visible-tool rule。

基线与 LLM 使用相同 hidden-label join 和 task-level分母。风险—路由曲线必须同时
显示 false accept、correct accept 和 protocol-level non-escalation rate。

## 8. 阶段计划

### P0：G0 venue、AI provenance 与时间可行性

输入：

- 官方 Technical Track 规则；
- 当前论文和生成链的形成历史；
- 当前 identity-linked public GitHub remote 和 2026-06-20 后公开提交历史；
- 用户的目标、AI 使用和学校检索要求。

动作：

- 保存带日期的官方规则快照和链接；
- 建立 AI provenance inventory，区分作者工作、模型作为实验对象、Codex
  工程辅助、语言辅助和可能的实质生成；
- 由作者决定是否需要向 Program Chairs 书面询问；
- 审计匿名期内 public repository/preprint 暴露，并由作者决定 private/anonymized
  GitHub 同步位置；在此之前不 public push；
- 核对 EasyChair 的精确关闭时刻和时区；若仍未明确，内部提交截止固定为
  2026-07-19 23:59 UTC+8；
- 用当前冻结内容在 ignored tmp 做一次 A4 compatibility dry-run，只记录页数、
  float、表图字号和末页风险，不改科学文本、不形成最终 PDF；
- 确认 APSEC 2026 是否继续。

输出：

- venue/provenance decision record；
- public-exposure/anonymity decision；
- A4 compatibility report；
- G0.1–G0.5 明确 pass/stop。

通过门：

- 五项均明确通过，作者可以遵守 AI/originality/anonymity 规则，且存在
  venue-compliant GitHub 同步位置。

停止门：

- 任一项不明确或无法满足。停止 APSEC venue-specific 执行。

### P1：历史证据隔离与根因审计

输入：

- current-98、v0.1/v0.2/v0.3、E6-no-verdict、coverage、EVP-8-HARD、
  stress-31、旧 claim map 和旧有效性审计。

动作：

- 建立 paper-evidence registry；
- 将所有旧结果标为 development/exploratory/not-confirmatory；
- 删除活动工作树中的四个旧 EVP-8 prompt 模板，并在 prompt change log 中记录
  文件名、删除前 SHA-256、退休原因和历史引用边界；
- 递归重建和扫描旧 no-verdict packets，记录嵌套
  visible_tests_rule_decision 残留；
- 记录 E4/E5 空证据、同 cohort 调 prompt、candidate-level Wilson CI、
  缺完整决策矩阵等根因；
- 给论文生成器增加 fail-closed 输入边界：新主结果不得读取旧统计文件。

输出：

- evidence quarantine report；
- superseding validity audit note；
- legacy prompt retirement record；
- 新旧 artifact 边界清单。

最小验证：

- 每个旧 artifact 恰好一个分类；
- 四个旧 prompt 的活动路径均不存在，删除前哈希可从退休记录复核，且没有生成
  任何替代 prompt；
- 旧数值不能进入新的 confirmatory analysis 输入；
- 递归扫描可以抓到任意深度 verdict-like key。

停止门：

- 仍有旧结果被 active claim map 当作确认性证据。

### P1A：held-out source feasibility gate

当前已知状态是 fresh-project promising candidates=0，且既有 readiness 中
F2P-established P2P candidate 列表为空。因此 30-task/8-project cohort 目前不是
ready artifact，必须先证明来源可执行，不能直接进入预注册或候选物化。

动作：

- 无 API 地盘点全部未使用 task/project、依赖、平台、visible/hidden oracle
  availability 和双环境可复跑性；
- 在不构造 candidate、不看 verifier 输出的前提下，形成至少 40 个有序 task
  sources；
- 对每个 source 证明 reference baseline、预先存在的 visible/hidden split 和
  两个干净环境可运行；
- 记录失败 task 的依赖、超时、平台或 oracle 原因，不把旧 task 作为兜底。

通过门：

- 至少 40 个可物化 source tasks、至少 8 projects、每项目最多 5 个；
- 其中至少 20 个 tasks 来自至少 4 个未进入历史 verifier 实验的 projects；
- visible/hidden oracle scope 在 candidate transform 前可冻结；
- 双环境 reference baseline 稳定。

停止门：

- 任一数量、项目分布或 oracle/environment 条件未满足。立即停止 APSEC 2026
  实验路线，不进入 P2/P3/P4，不用旧 current-98 补齐。

### P2：最近邻文献与 novelty 门

该阶段的检索、阅读、相关性判断和 novelty 决策由作者完成。只有 G0/Program
Chairs 明确允许时，Codex 才能对作者已核验的 primary sources 做机械元数据整理；
不得让生成式 AI 代替作者形成文献判断或 novelty claim。

优先检索四类：

1. LLM patch correctness assessment、patch verifier、critic/ranker；
2. APR/agent 的 visible/hidden test、oracle separation 和 overfitting；
3. selective prediction、reject option、human escalation；
4. LLM-as-judge、tool/advisory influence 和 prompt sensitivity。

动作：

- 优先核验 2024 至投稿截止日的最近邻工作；
- 保存可复核检索日志：数据库、精确 query、检索日期、时间范围、纳排标准、
  backward/forward snowballing 和 limiting/contradictory evidence；
- 建立比较矩阵：任务、可见证据、隐藏标签、输出类别、消融、hard negative、
  baseline、统计单位和实际 claim；
- 更新逐句 claim-to-citation map；
- 核验正式元数据、DOI/URL 和 BibTeX 专名。

输出：

- nearest-neighbor matrix；
- reproducible search log；
- claim-to-citation map v0.2；
- verified bibliography inventory。

通过门：

- 每个 novelty 差异都有直接来源和对应实验；
- “首次”“尚无”“现有研究通常”等领域覆盖判断必须由完整检索日志和
  direct/strong evidence 支持；partial support 只能用于明确缩窄的局部句子；
- 不存在 metadata-only 引用；
- 若最近邻已有等同设计，停止并由作者重新决定研究贡献，不自行改 claim。

### P3：EVP-v0.4 预注册冻结

动作：

- 作者独立复核本计划提出的设计，写出自己的设计理由并签核；不得把 AI 生成的
  计划文本直接当作作者方法学；
- 若 Program Chairs 未书面允许更广 AI 辅助，prompt、schema、oracle split、
  transform registry、统计 estimand 和分析规则均由作者亲自形成；
- 对 P1A 的每个 task，先冻结并哈希 visible/hidden oracle split、命令和判定，
  再冻结 transform registry；顺序不得倒置；
- 冻结一句话研究问题、RQ、C0–C5、模型数、重复数、主要指标、统计代码接口、
  cohort 标准、排除规则和随机化种子；
- 使用旧 prompt 的 Git 历史、删除前哈希和审计记录逐条检查矛盾和重复；不得
  恢复已退休模板；
- 由作者在 G0/政策边界允许后另行形成全新的单一 v0.4 prompt，并单独记录
  prompt change record；Codex 本轮不生成该 prompt；
- 冻结 semantic parse-valid=100% 的处理规则；invalid 不作为第四决策、不从
  denominator 删除，任一 semantic invalid 使受影响 run 无效；
- 冻结两个 primary statistical families、project-cluster inference、
  precision simulation、surface-provenance audit 和 contamination checks；
- 冻结 schema、prompt hash、config hash 和分析计划 hash。

输出：

- EVP-v0.4 preregistration；
- prompt、schema、change record；
- protocol audit。

最小验证：

- C0–C3 只累积规定证据；
- C3/C4/C5 只有 synthetic_advisory_cue 值不同；
- prompt 不把 sparse evidence 预设为 escalate，也不把 synthetic cue 预设为真；
- prompt/schema/config hash 可重复计算。

停止门：

- 任一主设计项仍可能在看到 verifier 输出后改变。

### P4：held-out task pool 与候选对物化

动作：

- 汇总所有历史 task/project ID；
- 构造 40-task frozen ordered pool；
- 按 P3 已冻结的 hash 验证 visible/hidden oracle split；任何变更使 task 作废；
- 在 oracle split 冻结后才按冻结 transform registry 构造候选；
- 在干净环境中物化 reference positive 和 deterministic hard negative；
- 运行实际 apply/static/F2P/P2P/hidden oracle；
- 在第二个干净环境复跑标签；
- 冻结 30 个 primary task pairs 和 reserve 使用记录。
- 对 task/project identifier、diff header/path/format 做匿名化和规范化；
- 运行 surface-only provenance audit：仅使用行数、hunk、路径、格式和 token
  统计，在 leave-one-project-out 下预测 positive/negative；balanced accuracy
  高于预注册的 0.65 即停止并重新设计，不进入 API。

输出：

- task pool manifest；
- candidate provenance manifest；
- visible/hidden oracle manifest；
- surface-provenance audit；
- 60-candidate frozen cohort summary。

最小验证：

- historical task overlap=0；
- 30 tasks、至少 8 projects、每项目不超过 4；
- 每 task 恰好一正一负；
- positive 全部通过；negative 全部 visible-pass/hidden-fail；
- 环境错误、依赖错误和非确定性失败为 0；
- 两环境标签一致。
- neutral task IDs、diff normalization 和 surface-provenance gate 通过。

停止门：

- 30 个稳定 task pairs 或项目分布未达到标准。不得用旧任务补齐。

### P5：实现新的单一执行链

实现范围：

- packet builder；
- recursive leakage/schema checker；
- no-API preflight；
- API runner；
- sanitized decision exporter；
- task-cluster analyzer；
- validity auditor。

AI/originality 边界：

- 未取得 Program Chairs 的书面许可时，P5 的算法、parser semantics、统计实现
  和 scientific defaults 必须由作者亲自编写；Codex 只能运行作者提供的代码和
  作者指定的确定性机械检查。作者逐行审查是额外验证，不能替代作者形成实现；
- 作者必须保留实现审查记录，证明代码与 P3 preregistration 一致。

工程规则：

- 新代码使用 evp_v0_4 命名空间，不在旧 runner 中添加兼容分支；
- packet 采用显式 allowlist；
- recursive denylist 检查 label、correctness、oracle verdict、source decision
  和所有 verdict-like nested keys；
- API 与 check-only 路径严格分离；
- provider fallback 默认禁止；
- retry 只处理 transport/empty-response，并受 5% global cap；semantic
  parse-invalid 不重试，直接触发受影响 run 无效；
- 临时测试 fixture 放 ignored tmp，验证后删除；不保留一次性 test 文件。

输出：

- 可复用脚本和最小文档；
- synthetic fixture validation report。

停止门：

- check-only 会触发 API；
- packet/prompt 有隐藏泄漏；
- 分析器不能从 sanitized matrix 独立复算；
- runner 会静默 fallback 或覆盖旧输出。

### P6：全链路 no-API preflight

动作：

- 构造全部 360 个唯一 packets；
- 对所有条件做 canonical JSON diff；
- 扫描 packet、rendered prompt、call manifest 和 tracked outputs；
- 运行 parser fixture、统计 fixture 和双实现复算；
- 计算 smoke 36 unique/38 hard-maximum attempts 与 full
  3240 unique/3402 hard-maximum attempts 的 token/cost/time 预算。

通过门：

- 360/360 packet schema-valid；
- hidden leakage=0；
- C0–C3 累积字段完全符合预注册；
- C3/C4/C5 非 synthetic_advisory_cue 字段 diff=0；
- check-only API calls=0；
- prompt/model/config hash 冻结；
- 成本包和 run manifest 完整。

停止门：

- 任一差异或成本不明确。不得调用 API。

### G1：API 授权

必须向用户展示：

- 精确模型和 provider；
- smoke 36 planned unique requests、2 retry budget、38 hard maximum attempts；
- full 3240 planned unique requests、162 retry budget、3402 hard maximum attempts；
- 按 hard maximum 计算的最大 token 和估算费用；
- raw/tracked 数据边界；
- 停止条件。

只有用户明确授权对应阶段后才能执行。smoke 授权不自动包含 full run。

### P7：development-only API smoke

动作：

- 只用 2 个不属于 held-out cohort 的 development fixtures；
- 三模型、六条件各跑一次，共 36 unique requests；transport retry 最多 2 次，
  hard maximum 38 attempts；
- 检查 provider/model identity、schema、parser、telemetry 和 retry。

通过门：

- 36/36 unique records 最终完整，attempts 不超过 38；
- provider/model 无 fallback；
- schema-valid 率 100%；
- tracked 输出无 raw response、prompt、patch、credential；
- 不因 smoke 决策修改 prompt、RQ 或统计计划；
- 只有不改变 model-visible request、model config、parser semantics 或分析语义的
  transport/observability 修复，才可回到 P5/P6 后申请新 smoke 授权；
- 任一 request serialization、prompt/schema、token/reasoning control、
  decision parsing 或分析语义变化，都必须 version bump 并回到 P3，随后重走
  P4--P7。

### P8：确认性 full run

动作：

- 按冻结交错顺序执行 3240 planned unique requests；全局 retry 最多 162，
  hard maximum 3402 attempts；
- 每条调用 stateless；
- raw 写 ignored outputs；
- 每批次即时检查完整性，但不连接 hidden labels、不看 paper-facing metric；
- provider/transport failure 按预注册 retry 一次。

通过门：

- response coverage=100%；
- semantic parse-valid=100%；任一 semantic invalid 使受影响 model-condition
  run 无效，不进入 P9；
- model/provider/prompt/packet hash 全程不变；
- 不选择性重跑某种 decision；
- sanitized candidate-level matrix 完整。

停止门：

- fallback、模型漂移、prompt/packet 改动、输出覆盖不足或 invalid 超门。
  整个受影响 run 无效，不形成论文结果。

### P9：hidden-label join、统计与有效性审计

动作：

- 在 APSEC AI policy 未获更广书面许可时，由作者亲自运行、核验和解释统计；
  Codex 不选择分析、不解释结果、不生成 human-readable scientific narrative；
- 所有模型输出冻结后一次性连接 hidden labels；
- 运行 task-level、project-cluster、repeat-stability 和 baseline 分析；
- 用第二条独立实现复算核心 counts/denominators；
- 执行 leave-one-project-out；
- 生成新的 setting-validity audit v0.2；
- 构建匿名 replication artifact staging：model-visible packets、normalized
  candidate patches、visible/hidden oracle commands、environment lock、prompt/
  config hashes、sanitized decisions 和 analysis scripts；不包含 credentials、
  raw responses、本机路径或身份信息。

输出：

- sanitized decision matrix；
- machine-readable analysis；
- human-readable analysis；
- validity audit；
- confirmatory claim decision table；
- anonymous artifact manifest 和 rebuild audit。

通过门：

- 两套实现核心计数一致；
- 所有分母都是 task-level；
- exploratory 和 confirmatory 完全分开；
- 精确 model/provider/date/hash 可追溯；
- 不隐藏零效应、负效应或模型异质性；
- artifact 可从 scientific inputs 重跑实验并从 sanitized decisions 复算表格；
  发布位置必须服从 G0 匿名期决定。

停止门：

- 任何主 claim 不能从 tracked sanitized artifacts 复算；
- unblinding 后改变主要分析；
- 旧结果进入合并统计。

### P10：作者主导的论文重建与引用同步

受 APSEC AI policy 约束，该阶段的科学论证、结果解释和正文由作者完成。Codex
只在 G0 允许的范围内做作者原句的拼写、语法、局部清晰度和格式修正；不得翻译、
重构段落、改写 claim、综合文献或起草摘要。

重写顺序：

1. Methods：cohort、候选构造、证据条件、hidden evaluator、执行和统计；
2. Results：只写 P9 已冻结的数字和预注册比较；
3. Discussion/Threats：construct、selection、serving variability、contamination、
   controlled-cohort prevalence 和 AI policy；
4. Related Work：按 P2 最近邻矩阵重建；
5. Introduction：问题、gap、方法和有边界的贡献；
6. Conclusion；
7. Abstract；
8. Title。

生成链规则：

- 作者认可的 canonical content 是唯一内容源；
- 修改生成器或 canonical source，不手改会被覆盖的 TeX/PDF；
- claim map、Markdown、LaTeX、BibTeX、表图数据同一版本；
- 摘要最后写，不能比 Results/Discussion 更强；
- 旧 98/31 数值只在确有必要的开发史或 threats 中出现，不进入主结果；
- 正文冻结后，由作者逐句重新认证 final claim-to-citation map：support grade、
  direct/indirect、边界、nearest-neighbor matrix row 和最终 BibTeX key；
- 投稿前按最终检索日期更新 search log，作者签核 final map。

通过门：

- 每个主 claim 都有 P9 artifact ID；
- 每个外部事实都有作者签核的 final claim-to-citation mapping；
- final map 的 metadata-only=0；所有 novelty/gap 句继续满足 P2 的完整检索日志
  与 direct/strong gate；
- P10 新增或实质更新的任一来源必须重新进入 P2 检索、核验和比较矩阵流程；
- 无 unsupported novelty、causal、safety 或 superiority wording；
- exact models/provider/date/repeats 全部披露；
- candidate construction、task clustering、基线和完整限制可复查。

### P11：APSEC A4/10-page 双盲封装

只有 P10 科学内容冻结后执行最终排版。

动作：

- 使用 IEEEtran 10pt conference A4；
- clean regenerate Markdown→TeX→BibTeX→PDF；
- 表格正文目标至少 8 pt，图中文字目标约 9–10 pt；
- 图形不只依赖颜色；
- 修复 BibTeX 专名、末页平衡、孤立标题和 source/PDF 漂移；
- 扫描正文、元数据、书签、图、Bib、自引、致谢、artifact 链接和仓库身份；
- 记录输入与最终 PDF SHA-256。

通过门：

- PDF MediaBox/CropBox 为 A4；
- 10 页以内且参考文献计入；
- 无 margin/font/negative-vspace 压页；
- source 早于且对应最终 PDF，generator check 无漂移；
- citation/reference warning=0，overfull=0；
- 字体嵌入、无裁切/重叠/空页；
- 双盲无泄漏；
- 末页两栏合理平衡；
- 最终逐页人工视觉检查通过。

### P12：独立审计、提交决策与冻结

动作：

- 至少一轮独立人工 scientific review；
- 独立复算核心表；
- venue、AI originality、双盲、artifact、页数和 PDF hash 最终签核；
- 核对 G1 smoke/full 两份明确授权记录和 attempts/cost 未超 hard maximum；
- 提交前重新检查官方规则和截止时间；
- 单独核实学校的 CCF/EI 认可口径。
- 若 EasyChair 精确关闭时刻仍不明确，作者须在内部截止前完成首次上传，保存
  回执，并复核平台文件 hash 与冻结 PDF 一致。

最终提交门：

- G0、P1、P1A、P2–P11 和 G1 全部通过；
- 没有未解决的 critical/major validity issue；
- 上传文件 hash 与已审 PDF 一致；
- EasyChair 上传成功且回执已保存；
- 作者明确批准提交。

任一项失败：不上传。

## 9. 最晚时间门

这些日期是最晚通过时间，不是压缩验收标准的理由。

| 日期 | 必须完成的门 |
|---|---|
| 2026-07-10 | 本计划本地冻结；public push 因 G0.5 暂停 |
| 2026-07-11 | G0 五项决定、A4 dry-run、P1 与 P1A feasibility gate |
| 2026-07-12 | 仅在 P1A 通过后完成 P2 novelty 门与 P3 preregistration |
| 2026-07-13 | 作者自行决定是否提交可选摘要；P4 task pool 已冻结 |
| 2026-07-14 | 30-task/60-candidate cohort 和双环境标签全部通过 |
| 2026-07-15 | P5/P6 通过；成本包完成；G1 smoke/full 分级授权 |
| 2026-07-16 | 36 unique/最多 38 attempts 的 smoke 通过；full run 启动 |
| 2026-07-17 | 3240 unique/最多 3402 attempts 的 full run 和 P9 完成 |
| 2026-07-18 12:00 UTC+8 | 作者冻结全部科学文本与 final citation map |
| 2026-07-18 | P11 最终 A4 封装完成 |
| 2026-07-19 23:59 UTC+8 | P12 通过；作者完成上传、回执确认和平台文件 hash 复核，作为保守内部提交截止 |
| 2026-07-20 | 官方日期门；不得把首次上传拖到该日，除非 P0 已确认更精确且更晚的关闭时刻 |

若 2026-07-14 仍没有合格 cohort，或 2026-07-17 没有完整确认性结果，APSEC
2026 Technical Track 路线停止；不得用旧 current-98 或 stress-31 替代。

## 10. 每阶段的文档与 Git 规则

每完成一个阶段：

- 在 docs/plans/current_plan_zh.md 记录本阶段 Inspect、Plan、Execute、Verify、
  Diagnose、Repair 和 Gate；
- 更新 docs/plans/current_project_state_zh.md 顶部状态；
- 把新故障、原因和修复写入 docs/experience/engineering_notes.md；
- 新入口加入 docs/INDEX.md 和 README.md；
- prompt 变化必须更新独立 prompt change record；
- 删除已完成且不再需要的临时计划和一次性 test fixture；
- 只暂存本阶段相关文件；
- 检查 git diff、敏感信息、绝对本机路径、credential、raw output、patch-bearing
  ignored artifacts；
- 创建本地提交；
- 只有 G0.5 通过后，推送到用户确认的 private/anonymized GitHub remote；
  当前 identity-linked public origin 在匿名期内不得接收新的 APSEC-facing push。

禁止提交：

- .env 和 local config；
- API key、账户信息或 billing response；
- raw model response、rendered prompt；
- 带原始标识/路径的 private patch packets；
- benchmark checkout；
- artifact ZIP 到 Git；匿名 ZIP 只在 release/archive 阶段从已审 staging 生成；
- 包含本机用户名的编译日志。

允许进入 G0.5 批准的 private/anonymized remote、但禁止进入当前 public origin：

- 通过 license/identity/double-blind audit 的 normalized candidate patches；
- model-visible packets、oracle commands、environment lock、sanitized decisions；
- anonymous artifact manifest 和可复算分析脚本。

## 11. 完成定义

只有同时满足以下条件，目标才算完成：

### 科学

- 新 task-disjoint cohort 和预注册 project-held-out 子集完整；
- 证据与 advisory 正交；
- hidden-label post-decision join；
- task/project-cluster 统计；
- 强基线与三重复；
- 旧结果完全隔离；
- 结论可为零效应或负效应，但不越界。

### 可复现

- packet/prompt/config/model hashes 完整；
- sanitized candidate-level matrix 可重算全部主表；
- 匿名 artifact 含 normalized patches、model-visible packets、oracle commands、
  environment lock 和 analysis scripts，可复现实验输入与标签；
- exact provider/model/date/retry 披露；
- 新 validity audit 通过。

### 写作与引用

- 作者形成并确认科学文本；
- nearest-neighbor matrix、reproducible search log 和作者签核的 final 逐句
  claim map 完整；
- Markdown/LaTeX/BibTeX 引用集合一致；
- 0 missing、0 unused、0 duplicate、0 citation warning；
- 摘要、标题和结论不强于证据。

### 投稿

- APSEC AI/originality policy 可如实满足；
- 匿名期 public-repository 暴露已获 Program Chairs/作者明确处理，active Git
  remote 符合 G0.5；
- A4、10 pt、最多 10 页、双盲；
- 表图可读；
- source→PDF→hash 闭环；
- 官方规则提交前复核；
- 作者最终签核。

## 12. 下一轮执行入口

下一轮收到“开始执行计划”后，只执行 P0/G0、P1 和 P1A 的 no-API 部分：

1. 重新 Inspect 当前工作区和本计划；
2. 请作者确认 G0.1–G0.5；
3. 建立 venue/provenance decision record；
4. 建立旧证据 quarantine registry；
5. 递归复现 nested verdict leakage；
6. 运行 A4 compatibility dry-run 和 held-out source feasibility audit；
7. 运行最小验证并更新本地提交；只有 G0.5 通过后才推送合规 remote。

在 G0、P1、P1A、P2、P3、P4、P5、P6 全部通过且用户另行授权前，不调用任何
API。
