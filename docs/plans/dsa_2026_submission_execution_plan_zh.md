# DSA 2026 论文、实验与投稿执行总计划

计划编号：DSA-2026-EVIDENCE-POLICY-20260710
制定日期：2026-07-10
当前状态：P2_SOURCE_FEASIBILITY_PASS / REGULAR_FROZEN /
P3_MECHANICAL_PASS_PENDING_AUTHOR_SIGNOFF / SHORT_INACTIVE /
V0_SUBMISSION_GATE_PENDING
唯一主目标：DSA 2026 Regular Paper
同会场降级：DSA 2026 Short Paper，仅可在任何模型调用前锁定
非活动备选：ACAI 2026；不得并行投稿，也不得在看到 DSA 实验结果后切换
用户优先级：科学与收录稳健性优先，其次才是时间
本轮边界：P3 机械冻结候选已完成；等待作者签核，不进入 P4/P5，不调用 API，不改论文结果

## 1. 权威性与目标覆盖

本文件从 2026-07-10 起成为项目唯一 active master plan，并覆盖：

- `docs/plans/apsec_ccfc_evidence_repair_plan_zh.md` 的 APSEC venue-specific
  路线；
- `docs/plans/final_paper_roadmap_zh.md` 中所有旧 current/next-step 状态；
- current-98、EVP-8-HARD、coverage-contestation、stress-31 和旧 v0.1--v0.3
  的确认性解释；
- 旧 prompt、旧 runner、旧 config 和旧 manuscript generator 的执行资格。

旧文件继续保留作 provenance，但不能覆盖本计划。`docs/plans/current_plan_zh.md`
只记录每轮 Inspect--Plan--Execute--Verify--Diagnose--Repair--Gate 日志。

后续每轮只激活一个阶段。阶段 Gate 未通过时，不得顺手进入下一阶段；no-API
轮次不得调用模型，standing authorization 也不得绕过 smoke/full 各自的 Gate。

2026-07-11 用户持续授权覆盖：在 P1--P5 全部 passed、模型/packet/analysis 和
exact hard maximum 已冻结后，smoke 与随后满足 Gate 的 full run 可使用现有 API key
自动执行，不再单独确认预算。该授权不覆盖提前调用、不允许突破 request/retry/token/
cost hard cap，也不覆盖因结果方向而重跑。GitHub 同步仍先尽力执行；private remote
连续失败时记录错误并继续本地闭环，但任何情况下都不得误推当前 public origin。

## 2. 第一性原理结论

### 2.1 唯一研究问题

> 在 task-disjoint 的受控补丁集合上，真实、累积的可执行证据从 C0 增至 C3 时，
> 多个固定 LLM 对正确补丁和隐蔽错误补丁的 accept/reject/escalate 分布如何变化？

该问题研究的是 evidence-conditioned decision policy，不是 autonomous verifier
correctness，也不是证明 LLM 优于确定性工具。

### 2.2 一句话论文论证

计划中的论证句是：

> 在受控 candidate-patch gating 问题中，我们使用 task-disjoint 候选对、冻结的
> visible/hidden oracle 和四级真实可执行证据，估计证据增加如何改变 LLM 的自动
> 接受、拒绝和升级策略，同时报告错误接受、正确接受与人工工作量之间的边界。

这是待验证 argument，不是已成立 claim。最终标题、摘要和结论只能由新实验结果
决定。

### 2.3 为什么不继续修旧实验

- 旧 prompt 直接规定 sparse evidence、failure 和 escalation/reject 路由；
- 旧 E4/E6 packet 含 verdict-like decision，E4/P2P 证据又未真实物化；
- 旧 cohort 被用于协议开发、prompt 修补和结果报告，不是 held-out confirmation；
- 旧统计把 correlated candidates 当作独立样本；
- 旧 stress-31 有重复 patch、全为 negatives，不能支持完整 utility claim。

因此所有旧数值只允许用于开发史、失败机制或计划依据，不能进入新论文主统计、
新置信区间或摘要。旧 98/31/47-case 数字、旧模型百分比、旧 candidate-level Wilson
区间、旧六表和旧结果图必须从 DSA title、abstract、contributions、results、
conclusion 和主图表删除；ID/hash 只保留在 quarantine/provenance 账本。

## 3. DSA 2026 投稿门 D0

官方页面：

- CFP：https://dsa26.techconf.org/
- 投稿：https://dsa26.techconf.org/submission
- Regular/Short：https://dsa26.techconf.org/track/regular
- Proceedings：https://dsa26.techconf.org/track/proceeding
- Registration：https://dsa26.techconf.org/registration

截至 2026-07-11 的官方信息：

- Regular/Short 截止：2026-09-01；页面未写明时区；
- 通知：2026-10-18；camera ready 与 author registration：2026-10-25；
- 会议：2026-11-14 至 2026-11-15，厦门；
- Regular 最多 12 页，Short 最多 10 页；Regular/Short track 页面明确 content and
  references 均计入页限；
- Proceedings 由 IEEE CPS 出版，并提交 IEEE Xplore、Ei Compendex、Scopus；
- 每篇论文至少一名作者付 full registration 并现场报告，否则不进入 IEEE
  digital library 和 EI indexing；
- early author registration 为 IEEE/REAJ/ORSC member USD 700，其他 USD 750。

“提交 EI”不是最终检索保证。以下六项是 DSA 投稿资格门 V0，不是内部实验有效性门：

| 门 | 必须得到的证据 | 未通过时 |
|---|---|---|
| D0.1 AI policy | DSA Secretariat 对现有 AI 参与、IEEE disclosure 位置和允许范围的书面回复 | 未回复前不得提交 DSA；venue-neutral 科学准备可继续 |
| D0.2 EI | 学校图书馆核验近三届 DSA proceedings 的 Compendex 记录；保存检索式、日期和截图/导出 | 不把 DSA 视为满足最低 EI |
| D0.3 publication | 核对 2026 IEEE conference ID、ISBN、CPS 和现场报告要求 | 信息不一致则停止 DSA 投稿 |
| D0.4 logistics | 用户已授权注册/差旅预算无需再次确认；作者仍须确认厦门现场报告人和可行性 | 无共同作者能现场报告则停止 |
| D0.5 authorship | P3 前确认科学责任；P12 前冻结姓名、单位、邮箱和顺序 | 无法承担或如实披露则不得 API/投稿 |
| D0.6 venue/template snapshot | 保存 CFP、submission、track、proceedings、registration 和官方 template ZIP 的快照/哈希；用 `IEEEconf.cls` clean-build 最小实名 skeleton，核验 Letter、作者/keyword、页限和引用计页规则 | 网页或模板不一致则暂停 |

DSA 页面尚未给出 venue-specific GenAI 细则。IEEE 通用政策要求披露 AI 生成的
文本、图、代码或其他内容，说明系统、涉及部分和使用程度；纯语法编辑通常不在
强制披露范围。不得把现有实质参与伪装成语法润色。

本计划本身由 AI 协助形成。作者必须在 D0.5 中逐条接受、修改或否决设计决定，
形成作者签核版本；本计划不能代替作者的方法学责任。

2026-07-11 Gate 解耦修订：V0 外部门与 P1--P5 科学门并行推进。V0 必须在 P12 初始
投稿前全部 pass，但不再阻塞 P1 quarantine、P2 source feasibility 或其他 no-API
科学准备。首次模型调用只由 P1--P5、冻结 hard cap 和 standing authorization 控制；
D0.5 的科学责任部分仍须在 P3 前完成。若 V0 最终失败，保留冻结实验作为
venue-neutral evidence，另选已核验 EI venue；不得为换会场重跑或挑选结果。

2026-07-11 P0 执行记录：官方页面、IEEE 通用 AI policy、三届 IEEE proceedings、
Secretariat 联系邮箱和模板 ZIP 已核验；`IEEEconf.cls` skeleton 已 clean-build 并通过
字体/渲染审计。询问信已完成但未发送，Engineering Village 核验、2026 CPS ID/ISBN、
现场报告人、作者责任和最终作者元数据仍待外部确认。权威状态见
`docs/submission/dsa_2026/p0_d0_record_zh.md`；V0 投稿 Gate 仍为 STOP，但按上述解耦
规则不再阻塞 P1。

### D0 时间门

- 最晚 2026-07-14：发出并保存 DSA AI/EI/publication 询问；
- 最晚 2026-07-18：D0.1--D0.6 全部 pass，或停止 DSA 2026 路线；
- ACAI 仅在 DSA 于任何实验前停止、ACAI 另行通过 scope/AI/EI 门后才能成为新计划；
- 禁止一稿多投。

## 4. Regular 与 Short 的不可逆选择

主线优先 Regular。Short 是独立的预注册 pilot protocol，不是“不好看的 Regular
结果”的包装。

| 冻结项 | Regular | Short |
|---|---:|---:|
| primary tasks | 30 | 20 |
| projects | 至少 8 | 至少 6 |
| 每项目上限 | 4 tasks | 4 tasks |
| source list | 30 primary + 10 reserve | 20 primary + 8 reserve |
| 全新 project 要求 | 至少 15 tasks / 4 projects | 至少 10 tasks / 3 projects |
| candidates | 60 | 40 |
| fixed models | 3 | 2 |
| repeats | 3 | 3 |
| 论文定位 | controlled confirmatory study | preregistered estimation/pilot study |

选择规则：

1. P2 no-API source feasibility 和 precision simulation 后选择一次；
2. 选择必须发生在任何 smoke/full model call 前；
3. Regular 不达标但 Short 达标时，只有用户明确签核才能切换；
4. 一旦发生任何模型调用，稿型、task 数、project 数、模型数和重复数永久冻结；
5. 结果弱、CI 宽、p 值不显著或 reviewer 意见都不能触发 Regular→Short；
6. Short 不能使用旧 task 补规模。

2026-07-11 P2 决策：Regular 已通过 source capacity、conditional precision 和最近邻
定位 Gate，冻结为唯一稿型；Short 仅保留为 pre-API simulation record 并设为 inactive，
不得在看到任何模型或 cohort 结果后重新激活。只有 P3 以及 D0.5 科学责任部分形成可审计
passed 记录后，Regular 才可进入 cohort materialization；V0 其余外部项在 P12 前并行
完成。稿型冻结不等于模型 API 授权。

API 前 precision simulation 只针对一个已锁定目标：冻结 tasks/models/providers/run
window 后，独立 stateless repeats 所诱导的 decision stochasticity。task/project 不是
从总体抽出的随机变量，模拟和最终区间都不得解释为跨项目总体 CI。

- 覆盖 C0/C3 within-task decision correlation = 0、0.3、0.6 和最坏 Bernoulli rate；
- Regular：conditional primary-rate interval 总宽目标不超过 0.35，conditional
  paired-effect interval 总宽不超过 0.30；
- Short：conditional paired-effect interval 总宽不超过 0.40；
- 同时模拟删去单项目后的 effect range，作为稳定性门，不称 confidence interval；
- 模拟不达标就停止相应稿型，不用 candidate/model/repeat 伪造更大的外部样本量。

## 5. 术语账本

| 规范术语 | 定义 | 禁止替换为 |
|---|---|---|
| evidence-conditioned patch gating | 在指定模型可见证据下给出合入策略 | autonomous verification |
| model-visible evidence | 决策前真实可见且已物化的字段 | hidden evaluator |
| visible oracle | 预冻结、允许模型看到结果的测试或检查 | correctness oracle |
| hidden evaluator | 所有模型输出冻结后才连接的独立标签/测试 | visible test |
| oracle-positive | visible 与 hidden oracle 均稳定通过的候选 | universally correct patch |
| hard negative | visible checks 通过但独立 hidden oracle 稳定失败的候选 | arbitrary wrong patch |
| accept | 建议自动合入 | correct |
| reject | 建议不合入 | incorrect proof |
| escalate | 路由给人工或更多工具 | safe/correct |
| false accept | hard negative 被 accept | 所有非 reject |
| correct accept | oracle-positive 被 accept | deployment recall |
| task-level effect | 每个 task 内先汇总 candidate/model/repeat 后的效应 | request-level n |
| exploratory evidence | 旧协议开发结果 | confirmatory evidence |

全文、schema、表图和代码注释必须使用同一术语。任何新同义词先更新账本。

## 6. Claim 边界与待验证 evidence map

允许的 claim：

- 在冻结 controlled cohort 内，C0→C3 与三类决策分布的关联；
- oracle-positive 与 hard-negative 上的 task-level paired policy change；
- 固定模型、固定 provider、固定日期范围内的模型异质性和 repeat 稳定性；
- deterministic baselines 揭示的 automation/workload trade-off；
- 失败模式和可复现的 protocol-design lesson。

禁止的 claim：

- LLM 能自动验证补丁正确性；
- 通用安全、部署 prevalence 或总体 precision；
- 三个固定模型代表所有 LLM；
- C0→C3 bundled change 是某一个字段的单独因果效应；
- escalate 等于 reject、safe 或 correct；
- IEEE Xplore 自动等于 EI；
- 旧 current-98/stress 结果与新结果合并；
- 首次、唯一、SOTA 或 superiority，除非作者完成直接最近邻检索并有证据。

| 待验证 claim | 必需证据 | 当前状态 |
|---|---|---|
| 新协议无 verdict/label leakage | 递归 denylist、canonical packet diff、rendered-prompt audit | needs evidence |
| C0→C3 改变 hard-negative accept policy | 新 cohort 的 task-level `Delta-` 与区间 | needs evidence |
| C0→C3 改变 oracle-positive accept policy | 新 cohort 的 task-level `Delta+` 与区间 | needs evidence |
| 策略变化通过 accept/reject/escalate 哪条路径发生 | 冻结 transition matrix 与 secondary outcomes | needs evidence |
| 行为在固定模型间不同 | model-specific secondary analysis | needs evidence |
| 旧结果不进入新结论 | quarantine registry 与 analysis input denylist | partially supported |

## 7. 新实验协议

### 7.1 Cohort feasibility

每个 task 必须：

1. 与 current-98、EVP-8-HARD、coverage、stress-31、realistic-agent 和协议开发
   fixture task-disjoint；
2. 在两个干净环境中重现 reference baseline；
3. 在 candidate transform 前冻结并哈希：
   - visible F2P tests；
   - visible P2P/regression tests；
   - hidden behavior/regression oracle；
   - 命令、timeout、通过规则和环境锁；
4. 形成同源候选对：
   - oracle-positive：全部 visible/hidden oracle 在两环境稳定通过；
   - hard negative：C1--C3 visible checks 全部通过，但至少一个独立 hidden oracle
     在两环境稳定失败；
5. 按 P2 在 excluded development tasks 上形成、并由 P3 签核的 transform registry
   和优先序构造 negative，不人工挑选“效果更明显”的版本；
6. 任一 oracle 在 candidate materialization 后改变，task 作废；只可在模型调用前
   按冻结 reserve 顺序替换。

P2 只能在明确排除的 development tasks 上设计和机械验证 transform registry；这些
tasks 永不进入 primary/reserve。P2 对候选 source 只检查 baseline、oracle、environment
和 source-level 条件，禁止在 primary/reserve 选择前应用 transform 或查看其 hidden
结果。随后用冻结 seed 在项目数、每项目上限和新项目配额约束下选择 source list。
P3 由作者签核 transform registry；P4 才首次依序应用到冻结 primary/reserve。若 reserve
耗尽仍不足，不改 transform、不后验挑 task，直接停止相应稿型。任何旧实验 task、
prompt fixture 和已看过模型决策的 case 都进入 exclusion registry。

数量、项目数、环境稳定性或 visible/hidden separation 任一不满足，停止相应稿型。
不得用旧 current-98、hard 或 stress case 补齐。

### 7.2 四个模型可见条件

| 条件 | 累积模型可见内容 |
|---|---|
| C0 context | 中性 task 描述、normalized candidate diff、必要代码上下文 |
| C1 executable-basic | C0 + 实际 patch apply、syntax/import/static 命令与逐项结果 |
| C2 bug-focused | C1 + 预注册 visible F2P 名称、命令与逐项结果 |
| C3 regression-aware | C2 + 预注册 visible P2P/regression 名称、命令与逐项结果 |

硬约束：

- 所有证据真实运行并物化；
- 禁止空数组、`not_run`、`not_recorded` 和占位 summary；
- C0→C3 只增加字段，不能删除、改写或重排前级语义；
- 不加入 synthetic advisory cue、tool verdict、rule decision 或 source decision；
- hidden oracle、candidate type、positive/negative、reference provenance 不可见；
- project/task/source/commit/issue URL 替换为冻结中性代码；
- 执行顺序按冻结 seed 交错随机化，不能整块先跑低级或高级条件。

删除旧 APSEC 计划中的 C4/C5 synthetic-advisory 支线，是本次最短路径压缩；DSA
主论文只回答真实 evidence bundle 的问题。

### 7.3 Prompt 与 schema

只允许一个全新中性 prompt 和一个 schema，C0--C3 完全相同。作者先形成 prompt
草案并签核；只有 D0 允许后，Codex 才可做矛盾、重复、泄漏和格式的机械审计。

Prompt 只定义：

- accept：建议自动合入；
- reject：建议不合入；
- escalate：现有证据不能支持自动决定。

Prompt 禁止：

- sparse evidence 应 escalate；
- failed test 必须 reject；
- condition/evidence-level 含义；
- coverage-contestation 指令；
- accept/reject/escalate 示例；
- tool verdict、rule-following 或 expected behavior。

模型可见 packet 禁止：

- `condition`、`evidence_level`、`packet_variant`、protocol id；
- 任意 `decision`、`source_decision`、rule/human verdict；
- hidden label、oracle verdict、candidate type；
- 可反查 project/task/reference 的标识。

Schema 只保留：

- `decision`；
- `confidence`；
- `concise_rationale`；
- `evidence_used`；
- `uncertainty`。

Parser 不得把 invalid、缺字段或无法解析输出改写为 escalate。

### 7.4 No-API protocol Gate

必须同时通过：

- Regular 240/240 或 Short 160/160 model-visible packets schema-valid；
- 所有 rendered prompts 递归 denylist=0；
- canonical diff 证明：
  - C1−C0 仅 executable-basic group；
  - C2−C1 仅 F2P group；
  - C3−C2 仅 P2P/regression group；
- model-visible 顶层 metadata diff=0；
- evidence fields 非空、命令和结果成对、环境 hash 完整；
- hidden label 与 model-visible tree 完全分离；
- prompt/schema/config/model/packet/analysis hashes 已冻结；
- no fallback、retry、invalid、cost 和中断恢复语义可静态审计；
- static packet-only rule 不能从残留 verdict 字段复原预期 decision。

任一失败：不得 smoke，先 Diagnose；只修根因并重走全部 no-API Gate。

### 7.5 模型、重复与请求预算

通式：

`full unique = tasks × 2 candidates × 4 conditions × models × 3 repeats`

| 项目 | Regular | Short |
|---|---:|---:|
| full unique | `30×2×4×3×3 = 2160` | `20×2×4×2×3 = 960` |
| full retry budget | 108 | 48 |
| full hard maximum | 2268 attempts | 1008 attempts |
| smoke unique | 24 | 16 |
| smoke retry budget | 2 | 1 |
| smoke hard maximum | 26 attempts | 17 attempts |

三个 repeats 不是三个独立 task 样本；它们是估计固定 task/model 条件下 response
stochasticity 的 stateless draws。每个冻结 repeat block 覆盖该 task/candidate/model 的
四个条件，block 内顺序随机且不共享上下文；分析按同一 block index 形成 C3-C0 contrast。

冻结要求：

- exact model ID、provider、API endpoint、date window；
- temperature、reasoning control、token cap、JSON mode；
- no-fallback policy；
- request ordering seed；
- input/output price snapshot、token/cost ceiling；
- Regular 三条预注册模型路线；Short 使用同一预注册顺序的前两条，不能按旧结果
  挑模型。

Retry 仅限 transport、rate limit 或空响应；每个 request 最多一次。semantic/schema
invalid 不重试。价格或模型版本变化时停止，不静默替换。

### 7.6 Baselines

必须报告：

- always-accept；
- always-reject；
- always-escalate；
- 每模型 C0 作为 evidence-minimal observed condition。

因为 positive 和 hard negative 都按定义通过全部 visible checks，deterministic
visible-test policy 在该 cohort 上严格退化为 always-accept，只报告一次等价性证明，
不得伪装成第四个独立基线。基线与 LLM 使用相同 cohort 和 hidden-label join；不能
把 always-escalate 的零 false accept 写成实用 superiority。

### 7.7 统计计划

唯一科学分析单位是 task。candidate、condition、model、repeat 和 request 都嵌套于
task；Regular 的 pooled n 仍是 30，Short 仍是 20。主 estimand 是冻结 cohort、固定
models/providers/config 和冻结 run window 内，对独立 stateless response draws 取期望的
paired finite-cohort effect。repeats 只估计该条件下的模型调用随机性，不扩展 task
范围；所有结论都不能外推到所有项目、补丁或 LLM。

两个 primary estimands：

1. hard-negative false-accept effect：
   `Delta- = P(accept | C3, negative) - P(accept | C0, negative)`；
2. oracle-positive correct-accept effect：
   `Delta+ = P(accept | C3, positive) - P(accept | C0, positive)`。

分析顺序：

1. 每个 task/model/repeat block 形成 C3-C0 contrast，再在 task 内平均；
2. pooled primary 对冻结 models 等权、对 tasks 等权；
3. 两个 primary comparisons 报 familywise 95% Bonferroni conditional intervals；
   interval 只由各固定 task/model 内的 repeat blocks 重采样，算法、次数和 seed 在 P3
   冻结，不报告总体显著性；
4. Regular 报 task-macro effect、project-balanced reweighting 和
   leave-one-project-out effect range；后两者是稳定性分析，不称 confidence interval；
5. Short 同样以 finite-cohort effect 和 conditional interval 为主，不以显著性作为贡献；
6. model-specific 结果只作 secondary heterogeneity；
7. reject、escalate、non-escalation、transition matrix 和 disagreement 为
   secondary；
8. adjacent C0→C1→C2→C3 只作描述，不把 bundled change 归因于单字段；
9. accepted precision 因人工平衡 cohort 只作 cohort-conditional 描述；
10. 报告零效应、负效应、宽区间和模型分歧，不删异常方向。

统计代码在任何模型调用前以 synthetic fixtures 自测，锁定 repeat-block resampling、
Bonferroni level、seed 和 hash。解封后不能改变 estimand、exclusion、interval 或图表
主结论规则。

## 8. Smoke、Full 与“绝不再重跑”规则

### 8.1 Smoke

Smoke 使用 held-out cohort 外的两个 development candidates：一个 positive、一个
hard negative；四条件、每模型一次。

Smoke 只验证：

- provider/model identity 与 no fallback；
- request serialization；
- schema 和 semantic parse；
- token/cost/retry telemetry；
- private raw 与 tracked sanitized 输出边界；
- 中断恢复不覆盖 valid response。

Smoke decision 内容无论好坏都不能用于调 prompt。smoke 后只允许一次不改变 rendered
request、schema、parser semantics、packet、model ID/decoding config、调度或分析语义的
纯 transport/telemetry repair，例如日志落盘或 byte-equivalent serialization；修复后
必须重走 P5 no-API Gate 并重新申请 smoke。任何 model-visible/semantic/config 改动都
违反 P3 freeze，当前 DSA 2026 路线立即停止；只能作为未来独立实验，不能与本版本
合并或在当前时间表内“修复后重跑”。

### 8.2 Full-run Gate

2026-07-11 standing authorization 只在 passed smoke audit、exact request maximum、
最大成本和全部冻结 hash 存在时激活。full 只能覆盖该冻结版本和 hard maximum；不再
追加预算确认。

Full 期间只允许查看完整性、成本、传输和 provider identity；不得查看 paper-facing
metrics 或连接 hidden labels。

以下任一发生立即停止：

- provider fallback 或 actual model ID 漂移；
- prompt/schema/config/packet hash 改变；
- 首个 semantic/schema invalid；
- leakage/canonical diff 审计失败；
- retry、token、费用或时间 hard cap 到达；
- hidden labels 提前连接或查看；
- valid response 被覆盖；
- 执行顺序偏离冻结 manifest；
- provider 不再提供冻结版本。

### 8.3 绝不重跑的原因

不得替换任何 valid response，尤其不能因为：

- decision 不符合预期；
- false accept 太高；
- correct accept 太低；
- 模型不一致；
- CI 太宽或 p 值不显著；
- reviewer 希望结果更强；
- 想降为 Short；
- 想换 prompt、模型或 candidate 获得更好结果。

hidden labels 一旦解封：

- 不增加 task，不使用 reserve；
- 不修改 oracle 或 transform；
- 不重跑模型；
- 不把新版本与原版本合并统计。

唯一允许完成的是：hidden labels 仍封存、全部 hash 不变时，按预注册 transport
policy 完成尚未成功写入的 request。若科学设计或执行语义必须改变，原版本停止并
完整保留；新版本是新的研究，不是“修复后补跑”，且不在 DSA 截止前自动启动。

## 9. 阶段化执行闭环

### P0：D0 venue、AI、EI、预算和 remote

输出：venue decision record、AI-use inventory、EI verification record、attendance/
budget sign-off、private remote decision、DSA 官方页面/template ZIP 快照及哈希、
可 clean-build 的最小 `IEEEconf.cls` skeleton PDF 与编译日志。
Gate：本地 source/template/remote 证据包完成；D0.1--D0.6 作为并行 V0 投稿门跟踪。
停止：V0 未全 pass 时不得进入 P12 初始投稿；不阻塞 P1--P5 科学准备。

### P1：旧证据 quarantine

动作：给所有旧 artifact 唯一分类；建立 analysis denylist；递归复现 verdict leakage；
禁止新 generator 读取旧 paper-facing metric。
输出：quarantine registry、superseding validity audit。
Gate：旧结果不能进入新 analysis/claim map。

2026-07-11 执行结果：PASS。机器 denylist、人工隔离注册表、superseding audit 和
task/project exclusion registry 已冻结；98/98 个结构等价 E6-no-verdict packet 复现
嵌套 `visible_tests_rule_decision`，两个旧 full config 各复现 686 个 packet 的
placeholder/空 P2P evidence；28 个旧 task 和 8 个旧 project 只供 P2 排除。
`scripts/audit_dsa_legacy_quarantine.py --check` 全部通过，且未读取 prompt/patch 正文、
raw response、API key，也未调用 API。此结果取代 2026-07-03 的旧 validity audit；
旧文件继续保留为 provenance。

### P2：source feasibility 与稿型冻结

动作：先在 exclusion registry 内的 development tasks 上设计、验证并哈希 transform
registry/优先序；候选 primary/reserve 只做 task/project、双环境 baseline、visible/hidden
oracle 和 source-level 盘点，禁止应用 transform 或查看 candidate hidden 结果；随后建立
source frame，以冻结 seed 选择 source/reserve，运行 conditional precision simulation，
并完成最近邻文献预检。
输出：Regular 或 Short 的唯一选择、development/exclusion registry、transform registry、
source frame、source/reserve list、simulation report、nearest-neighbor matrix 和检索日志。
Gate：开发任务与 source list 完全 disjoint；对应数量、项目分布和 conditional interval
width 门全部通过；研究问题仍有清楚且诚实的定位。
停止：Short 也不达标。

2026-07-11 执行结果：PASS / REGULAR_FROZEN。P2 在 P1 的 28-task/8-project 基础上，
将实际登记或 probe 过的开发 task 扩展排除到 59 个；官方 BugsInPy snapshot 与 SCAM
2023 improved Conda/Docker reproduction snapshot 均冻结 commit/hash。改进环境中仍有
304 个 buggy=fail/fixed=pass 的未接触 source，覆盖 9 个新 project；hash-seeded
Regular source list 为 30 primary + 10 reserve，每 project primary 不超过 4，且每个
primary project 都有 reserve。四类 transform 只在 excluded development tasks 上做
结构适用性验证并冻结优先级，未在 source 上应用。

20,000-run-window conditional simulation 覆盖 marginal rate 0.1--0.9 和 C0/C3
correlation 0/0.3/0.6；Regular 最大 primary-rate width=0.1185、paired-effect
width=0.1704，均通过 0.35/0.30 门。2018--2026 最近邻预检核对 12 篇 official/
publisher/arXiv source，未发现 exact design match，但冻结定位不得使用 first/unique/
SOTA。总审计 18 项 PASS。SCAM reproduction 只证明 source-level feasibility；P4 对
最终 candidates 的两次全新 clean-environment 复跑仍是强制 Gate。

### P3：作者预注册与 prompt/schema 冻结

动作：作者签核 RQ、estimands、C0--C3、P2 transform registry、模型顺序、统计、
exclusion、prompt 和 schema；Codex 只在允许范围做机械冲突/泄漏检查。
输出：preregistration、prompt change record、hash manifest。
Gate：所有设计项在模型输出前不可变。

2026-07-11 执行状态：MECHANICAL_PASS / PENDING_AUTHOR_SIGNOFF。已形成 RQ1--RQ3、
两个 task-level primary estimand、C0--C3 contract、20,000-draw paired repeat-block
Bonferroni conditional interval、secondary/stability outcomes、exclusion/stop/no-rerun，
并冻结 `qwen3.7-plus-2026-05-26`、`deepseek-v4-flash`、`gemini-3.5-flash` 三条
provider route、参数、顺序、window 和 hard caps。全新 DSA prompt/schema 从空文件
建立；未恢复或读取已删除 prompt。synthetic cumulative/rendered-prompt、递归 leakage、
冲突/重复、retired-hash inequality 和 manifest 机械审计均通过。作者科学责任尚未
签核，因此 P3 不是 PASS，P4/P5/API 仍未授权。

### P4：held-out cohort materialization

动作：按冻结顺序构造候选对，双环境复跑，生成 model-visible/hidden 分离 manifest。
输出：cohort、environment lock、oracle hashes、candidate hashes。
Gate：全部 candidates 满足标签和证据物化规则。
停止：冻结 reserve 耗尽仍不足时停止 DSA；不得据此改 transform、补 task 或
Regular→Short。

### P5：新执行链与 no-API preflight

动作：新 namespace 实现 packet builder、runner、parser、retry、telemetry、sanitized
export 和 analysis self-test；不得修补旧 runner。
输出：240/160 packets、canonical diff、leakage audit、cost packet。
Gate：7.4 全 pass。

### G1/P6：Smoke 授权与执行

动作：P5 passed 后按 standing authorization 执行 24/16 unique smoke；执行后立即
审计 identity、parse、cost 和输出边界。
Gate：全部 smoke records valid、无 fallback、无泄漏、成本在 cap 内。
停止：只允许一次上述纯 transport/telemetry repair；再次失败或任何语义改动停止 DSA。

### G2/P7：Full 授权与一次冻结执行

动作：smoke Gate passed 后按 standing authorization 和 frozen manifest 完成；不得
突破 hard maximum。
输出：private raw responses、tracked sanitized decisions、run audit。
Gate：全部 unique requests 完成、hash 一致、invalid=0、成本/attempts 合规。

### P8：解封、统计和独立复算

动作：冻结输出后一次性连接 hidden labels；两套独立实现复算 primary effects、
Bonferroni conditional intervals、model heterogeneity、transition 和
leave-one-project-out effect range。
输出：candidate/task matrix、analysis report、table/figure source data。
Gate：两套实现核心结果一致；旧数据未进入；零/负结果未隐藏。

### P9：claim freeze

动作：建立逐句 claim-to-evidence map；按证据决定 title/abstract/conclusion；删除
unsupported novelty、safety、correctness、superiority wording。
Gate：每个主 claim 有新 artifact ID；不存在“计划中的结果”。

### P10：作者主导的论文重建

按 evidence-first 顺序：

1. Results；
2. Introduction 与 Conclusion；
3. Title；
4. Discussion；
5. Methods/Experimental Setup；
6. Related Work 与引用核验；
7. Abstract 最后写。

新 canonical Markdown/TeX 必须使用 DSA namespace；不从旧 APSEC generator 机械
复制科学内容。作者逐段形成和签核正文，AI 使用按 D0 书面边界记录。

### P11：引用、图表、artifact 与初始投稿封装

动作：主来源核验、图表生成、artifact sanitize、官方 DSA template 转换、页数与
PDF 视觉审计；对每条引用标记 direct/partial/background/limiting/metadata-only，
metadata-only 不得进入正文；保护 BibTeX 中 `{Defects4J}`、`{BugsInPy}`、
`{QuixBugs}`、`{SWE-bench}`、`{LLM}` 等专名大小写。
Gate：claim-to-citation map 完整，missing/unused/duplicate/warning 均为 0；图表可读、
artifact 可复算、PDF 符合 12/10 页和 DSA template。

### P12：独立预审与初始提交

动作：至少一轮独立 scientific review、独立统计复算、AI disclosure、作者/单位、
关键词、页限、PDF hash、SoftConf 首次上传与回执审计。
Gate：critical/major issue=0，作者最终签核后于内部日期上传；上传 hash 与审阅件一致。
停止：任一硬门失败不上传。

### P13：录用后 CPS/camera-ready

动作：通知后读取正式 CPS Author Kit、conference ID/ISBN、reviewer comments 与最终
instructions；完成 IEEE copyright、camera-ready、PDF QA 和每稿 full registration。
Gate：2026-10-25 前 camera-ready 与 registration 均有回执，最终 hash 与审阅件一致。

### P14：现场报告

动作：锁定共同作者中的现场报告人、差旅和应急联系人；议程发布后制作 slides，
至少两次计时彩排，并准备本地 PDF/PPTX 双备份。
Gate：共同作者本人于 2026-11-14--15 在厦门完成报告；不得以非作者 guest 代讲。

## 10. 论文结构计划

### 10.1 结果成立前的中性标题

`A Controlled Study of Evidence-Conditioned LLM Patch-Gating Decisions`

只有结果直接支持时，才可改为 finding-led title；禁止预先写 “improves safety”、
“reliable verification” 或 “reduces false accepts”。

### 10.2 论证链

`patch-gating risk -> evidence boundary 未被控制 -> task-disjoint hidden-evaluator
protocol -> paired C0/C3 effects -> accept/escalate trade-off -> controlled-cohort boundary`

### 10.3 建议章节与 Regular 页预算

| 章节 | 主要工作 | 目标页数 |
|---|---|---:|
| Abstract | context-gap-approach-result-implication-boundary；最后写 | 0.25 |
| 1 Introduction | software dependability stake、gap、RQ、贡献 | 0.90 |
| 2 Related Work | APR overfitting、LLM review/repair、judge sensitivity、reject option | 0.90 |
| 3 Study Design | task/candidates、C0--C3、prompt、hidden evaluator、estimands | 2.25 |
| 4 Experimental Setup | models、repeats、baselines、randomization、statistics | 0.90 |
| 5 Results | protocol validation、primary effects、transitions、heterogeneity/failures | 2.25 |
| 6 Discussion and Threats | meaning、rival explanations、limits、use boundary | 1.35 |
| 7 Conclusion | contribution-evidence-implication-boundary | 0.25 |
| References | 直接、已核验来源 | 1.95 |

Regular 正文内部目标合计 11.0 页，为 12 页硬上限保留约 1 页的 title/author、float
和引用增长缓冲。Short 内部目标不超过 9.0 页；只有 P2 已锁定 Short 时才使用对应
两模型/20-task protocol。不能在结果后靠删 limitations 或 references 硬压。

### 10.4 计划主图表

- Fig. 1：model-visible evidence 与 hidden evaluator 分离的协议图；
- Fig. 2：C0→C3 paired decision transitions 和两个 primary effects；
- Table 1：cohort、candidate pair 与 C0--C3 定义；
- Table 2：pooled primary effects、conditional intervals 与基线；
- Table 3：model-specific heterogeneity 与 repeat disagreement；
- Table 4：leave-one-project-out 和主要 failure modes；空间不足时进入 artifact。

每张图表只服务一个 claim。caption 必须写清 n 是 task，不把 request 数当样本数。

### 10.5 Related Work 主题簇

1. test adequacy、APR overfitting 和 plausible-vs-correct patch；
2. LLM code review、repair、critic/ranker 和 patch assessment；
3. LLM-as-judge、prompt sensitivity、tool/advisory influence；
4. selective prediction、reject option、human escalation 和 automation reliance。

作者必须实际阅读 primary sources，保存检索式、日期、纳排与 limiting evidence。
以稳定 claim ID 维护 nearest-neighbor comparison matrix；每条引用标为 direct、
partial、background、limiting 或 metadata-only。metadata-only 不进入正文，不以综述
代替原始来源，不生成虚构引用。所有“首次”“尚无”“通常忽略”在作者全文核验前
删除。

### 10.6 Results 与 Discussion 分工

Results 只报告观察、条件、effect、conditional interval 和 failure；Discussion 才解释可能机制、替代
解释和边界。工具服从、保守升级或模型分歧都不能在 Results 中写成因果机制。

### 10.7 DSA 排版与 PDF Gate

当前 7 页 PDF 仅作历史视觉 baseline：它由 `IEEEtran` 生成，六张旧表使用
`\scriptsize`，旧 Fig. 2 依赖颜色且低值不易区分，TeX 还比 PDF 更新；不能改名后
直接投稿。新稿必须使用独立 DSA namespace 和官方 ZIP 中的 `IEEEconf.cls`，从 clean
build 重建。

初始投稿逐项验证：

- US Letter、双栏、无页码、不手调 margin；
- 实名作者和单位，作者数不超过 5；abstract、title 符合模板限制，keywords 不超过
  6 个；
- 阿拉伯数字章节号；图注在图下、表题在表上，图表在首次引用后出现；
- 图中文字按模板达到 10 pt，表格不靠约 7 pt `\scriptsize` 塞页；参考文献 9 pt；
- Regular 最终 PDF 不超过 12 页，Short 不超过 10 页；在书面澄清前参考文献计入；
- `pdfinfo`、`pdffonts`、`pdfimages`、编译日志和 220--300 dpi 逐页渲染均通过；
  字体嵌入、无裁切/重叠/缺字，末页两栏平衡；
- Markdown、TeX、BibTeX、图源和 PDF SHA-256 对齐，上传文件 hash 与审阅件一致。

## 11. Artifact、AI provenance 与 Git

### 11.1 私有开发仓库

2026-07-11 已新建独立 private GitHub repository
`gaoming-a/research95-dsa-private`，remote 名为 `private`；现有 public `origin`
保留但禁止 DSA development push。该 private repo 不是 public fork，也不等于
anonymized artifact。

private repo 保存：

- 计划、代码、prompt/schema/config hashes；
- normalized candidate manifests；
- model-visible packets；
- sanitized decisions、分析脚本和表图 source data；
- AI-use provenance ledger 和作者签核。

不提交：`.env`、local configs、credentials、raw responses、rendered prompts、
benchmark checkout、带身份/本机路径的日志、artifact ZIP。

每轮只向 `private` 尽力同步，不向当前 public origin 推送。private sync 连续失败时按
用户指令记录并继续本地闭环；若 DSA 书面确认允许身份关联公开仓库且用户明确批准，
public release 时点再单独决定。

### 11.2 审稿/发布 artifact

从已审 staging 生成无 `.git` 的 clean artifact；包含 protocol、sanitized packets、
environment lock、analysis 和 rebuild instructions。现场/发布前扫描作者、邮箱、
绝对路径、secret、raw prompt/response 和第三方受限内容。

DSA 当前公开页面未给出 artifact track 或 supplementary-material 规则，因此论文必须
自包含，关键方法和主证据不能外包给链接。是否在 SoftConf 提交 artifact URL 必须由
Secretariat 书面确认；未确认时只冻结私有 staging，录用后再按正式 instructions 发布。

### 11.3 AI provenance

私有 ledger 至少记录：日期、系统/模型、任务、输入范围、输出文件、采纳程度、作者
验证、是否进入科学设计/代码/统计/正文、论文影响、venue-policy disposition 和是否
需披露。必须分别记录“LLM 作为实验对象”“AI 参与研究/编码/统计”“AI 参与写作”。
最终 disclosure 必须与事实一致；不能用“作者审查”替代真实复现，也不能删除不利
的 AI 参与记录。

## 12. 硬时间表

| 最晚日期 | 必须完成 |
|---|---|
| 2026-07-14 | DSA AI/EI/publication 询问发出；private remote 方案和 template skeleton 确定 |
| 2026-07-18 | D0 全通过；P1 quarantine 完成 |
| 2026-07-21 | P2 feasibility、precision simulation、Regular/Short 一次性冻结 |
| 2026-07-24 | P3 preregistration、作者 prompt/schema 和分析 hash 冻结 |
| 2026-08-03 | P4 cohort 双环境 materialization 完成 |
| 2026-08-06 | P5 no-API preflight 全通过；exact cost packet 完成 |
| 2026-08-08 | G1 smoke 执行与 audit 通过 |
| 2026-08-09 | smoke Gate passed 后 standing authorization 激活 full |
| 2026-08-12 | 一次 frozen full run 完成 |
| 2026-08-15 | P8 双实现分析、claim freeze 完成 |
| 2026-08-22 | 作者完成 DSA full draft |
| 2026-08-26 | 引用、图表、artifact、初始投稿 package 完成 |
| 2026-08-28 | 独立 scientific/statistical/PDF review 完成 |
| 2026-08-30 | 内部冻结并完成首次上传；保存回执和 hash |
| 2026-08-31 | 只处理平台/文件级问题，不改科学内容 |
| 2026-09-01 | 官方日期门；不得把首次上传拖到当天 |
| 2026-10-18 | 官方通知后立即获取 CPS Author Kit 和最终 instructions |
| 2026-10-23 | 内部 camera-ready、copyright、registration 与 PDF QA 冻结 |
| 2026-10-25 | 官方 camera-ready/author-registration 日期门 |
| 2026-11-07 | slides、现场报告人、差旅与双备份锁定；完成两次彩排 |
| 2026-11-14--15 | 共同作者本人在厦门完成现场报告 |

页面未注明截止时区，因此内部首次上传固定为 2026-08-30，不依赖最后时刻解释。

若 2026-07-21 没有合格 Short source frame，停止；若 2026-08-09 尚未通过 smoke，不启动
full；若 2026-08-15 没有完整有效结果，不用旧结果替代。

## 13. 最终完成定义

### 科学

- 稿型在任何 API 前冻结；
- task-disjoint cohort、真实 C0--C3、无 verdict leakage；
- hidden-label post-decision join；
- finite-cohort task-level effect、conditional repeat interval 和 project-deletion 稳定性；
- 预定义 decision-policy 基线、repeat 稳定性和失败模式完整；
- 零/负结果也可发表，不通过重跑改变。

### 可复现

- cohort、oracle、environment、prompt、schema、model、packet、analysis hashes 完整；
- sanitized task-level matrix 可重算全部主表；
- 两套实现复算一致；
- exact provider/model/date/retry/cost 可审计。

### 论文

- Results 先写，Abstract 最后写；
- 每个主 claim 有新实验 artifact；
- Related Work 使用作者核验的 primary sources；
- 术语、Markdown、TeX、BibTeX、表图数字一致；
- 无 autonomous correctness、safety、superiority 或 EI overclaim。

### 投稿

- DSA AI、EI、CPS、现场报告和费用门有书面证据；
- 官方 template、页数、字体、图表、引用、PDF hash 和回执通过；
- AI disclosure 与 provenance 一致；
- 至少一轮独立 reviewer-style audit 无 critical/major issue；
- 作者最终签核。

## 14. 下一轮唯一入口

P3 机械冻结候选已经通过，下一步只执行作者签核与 immutable manifest 重生成；V0
外部材料继续并行等待：

1. 作者逐项签核候选冻结稿中的 RQ、estimands、C0--C3、P2 transform registry、
   finite-cohort/conditional interval、models、统计、exclusion、prompt/schema 和
   no-rerun；
2. 作者确认能独立审查并承担全部科学/作者责任；
3. 记录作者名/时间，重生成 immutable hash manifest，重新运行 P3 Gate；
4. P3 passed 后立即停止，不得顺手进入 P4/P5 或调用模型 API。

在 P1、P2、P3、P4、P5 全部通过前，不调用任何模型；全部通过后按 2026-07-11
standing authorization 执行，不再单独确认预算。
