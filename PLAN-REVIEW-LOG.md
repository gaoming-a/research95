# Plan Review Log: Same API, Changed Contract（C′）

Act 1 (grill) complete — plan locked with the user. MAX_ROUNDS=5.

The author accepted the benchmark-first contribution shape on 2026-07-19. This
sign-off locks the research design for adversarial review; it does not authorize
data acquisition/generation, model selection, APIs, training, or experiments.

## Reviewer transport note

The bundled Codex CLI entry at the WindowsApps path could be discovered but could
not be started from the workspace process (`Access denied`) even for
`codex --version`. No review was claimed from that failed call. The fallback is a
dedicated independent Codex agent context instructed to perform read-only review of
`PLAN.md`; all revisions will be re-submitted to the same reviewer context for at
most five rounds. This preserves independent context, read-only intent, continuity,
and the bounded loop, but it is not the CLI transport described by the skill.

## Round 1 — independent Codex reviewer

1. **Generator–oracle 仍存在共同错误风险**：两者虽然不复用判定函数，却共同依赖同一 DSL
   语义和 transformation certificate，100% 一致无法排除共同误解。修复：冻结独立规范语义，
   加入人工推导的极小 gold suite，并用第二种独立求解后端交叉验证 checker；generator 不得
   输出或参与最终标签。
2. **“现实版本迁移”目前只是现实文档到自建 DSL 的人工映射**，机械 checker 只能证明映射
   后的模型，不能证明原 API 的真实语义，容易过度声称外部有效性。修复：每个 root 必须保存
   旧版、新版和迁移声明三方证据，并优先用版本化 SDK 测试/规范测试重放；无法执行验证时将
   claim 降为“真实文档语义变化迁移”。
3. **现实 roots 的独立性定义不足**：同一 changelog 事件、同一端点或同一模板派生的多个
   root 不能视为独立样本。修复：增加 `source_change_event_id`，按事件—工具族分层封闭，并
   以最高依赖事件簇作为外部集统计单位。
4. **统计单位写成“root cluster 或 tool family”不唯一，且 8–12 个工具族不足以直接支撑
   5 个百分点的常规功效声明**；推理随机性也未冻结。修复：预先固定主要 estimand 和最高层
   cluster，依据 pilot 的配对 discordance 与簇内相关重算样本量，并规定确定性解码或重复推理
   及其嵌套分析方式。
5. **benchmark-first 的创新仍可能被 GuideBench＋ContractBench＋Skill Drift 的组合解释为
   增量拼接**。修复：在数据构造前增加硬 novelty Gate，要求全文维度表证明相邻工作不能测量
   “稳定表面、单契约原子变化导致实际动作合法性翻转”，并预注册该 paired design 相对独立
   样本评测新增的可识别现象；不能证明即停题。
6. **确定性 parser+planner 近饱和不必然说明 benchmark 无价值**，它也可能是该问题的有效
   解决方案；当前停止逻辑混淆了 benchmark 难度与训练必要性。修复：明确 gold-DSL planner
   只作 ceiling，NL parser 是正式基线；只有无语义浅层基线在严格 OOD 饱和才判 shortcut，
   parser 饱和仅否决训练扩展而不自动否决评测贡献。
7. **小论文到硕士论文仍缺少“训练改进真实迁移”的必要条件**：现实集上只证明基础现象存在，
   不足以支持后续结构化适应方法。修复：把 held-out 现实 semantic-delta 集上的显著改进和
   能力保持列为硕士方法扩展的硬 Gate。
8. **权威状态尚未闭合**：`current_plan_zh.md` 与 `current_project_state_zh.md` 仍写“C 待作者
   确认/训练候选”，而 `PLAN.md` 已锁定 benchmark-first；虽然 manifest 仍正确保持未授权空
   状态，但执行入口存在冲突。修复：进入任何数据阶段前统一权威文档、索引和审查日志，并
   继续保持 manifest 未授权直至作者单独放行。

VERDICT: REVISE

### Codex's response

Accepted all eight findings. `PLAN.md` now adds a pre-data novelty Gate, an
implementation-independent semantic gold suite plus two solver backends, explicit
old/new/migration provenance and optional SDK/spec replay with a downgraded claim
when replay is impossible, `source_change_event_id`, fixed estimands and nested
randomness, the corrected interpretation of an NL parser solution, a real-transfer
improvement Gate for thesis methods, and fail-closed authority-document
synchronization. It also adds a ninth repair identified by the primary agent:
closed-loop pairs require a mechanically checked policy-separation certificate so a
contract-agnostic shared strategy cannot earn the primary paired score.

## Round 2 — independent Codex reviewer

1. **policy-separation certificate 仍缺少可执行定义**：“忽略 contract delta 的同一规范化
   策略”没有规定如何擦除契约文本、对齐两侧 observation history、动作等价类及策略记忆，
   因此当前无法机械复算。修复：冻结 contract-erasure projection 与两侧 history/action 对齐
   关系，并将证书明确定义为投影后两侧成功策略语言交集为空，再由独立后端给出空交证明或
   反例策略。
2. **本地 mock replay 不能提升现实有效性**：若 mock 仍由本研究依据文档构造，它只重复验证
   DSL 映射，不能证明真实旧/新 API 行为。修复：只有供应方版本化 SDK 测试、官方规范测试或
   独立存档的可执行 artifact 才可升级为行为证据；自建 mock 一律仍归类为“真实文档语义
   变化迁移”。
3. **主要统计 estimand 仍未指定唯一 confirmatory contrast**：当前写“方法间平均配对差”，
   但没有冻结哪两个方法是主要比较，5 个百分点功效目标因此不可计算且容易事后选择。修复：
   在 pilot 前指定唯一主要方法对比；若 benchmark 论文不主张新方法，则改为预注册模型级
   PCC/Flip Accuracy 的估计精度目标，把所有方法间差异降为校正后的次要分析。

VERDICT: REVISE

### Codex's response

Accepted all three findings. `PLAN.md` now defines a concrete contract-erasure
projection, history/event alignment, action normalization, finite deterministic
history-policy sets, and the empty-intersection certificate with proof or common
policy counterexample. Self-authored mocks cannot upgrade external-validity claims;
only independent provider/versioned executable evidence can. The benchmark's sole
primary estimand is now each preregistered model's PCC with a cluster-interval
precision target; all method contrasts are corrected secondary analyses. Any later
method paper must separately preregister one primary contrast and its power.

## Round 3 — independent Codex reviewer

1. **统计主目标仍有内部冲突**：第 3 节仍写样本量由“power analysis”决定，第 8 节首条仍把
   “方法间 PCC 平均配对差”定义为合成主 estimand，但后文又声明唯一主要 estimand 是每个冻结
   模型的 PCC 与区间精度；这会重新引入事后方法比较空间。修复：删除前两处旧表述，统一为
   “每个预注册模型的 PCC＋root-cluster 95% 区间半宽目标”，并明确 root-cluster 的构成和
   相应样本量计算；所有方法差异只保留为校正后的次要分析。

VERDICT: REVISE

### Codex's response

Accepted. The remaining power-analysis wording and method-difference primary
estimand were removed. A root cluster is now explicitly one `root_id` plus both
contract sides, all renderings/derivatives, and inference repeats; each
preregistered model receives its own PCC estimate and root-cluster 95% interval,
while all method differences remain corrected secondary analyses.

## Round 4 — independent Codex reviewer

首轮至第三轮的实质问题均已关闭；当前计划在 oracle 独立性、policy-separation 可复算性、
现实证据等级、统计单位与主 estimand、创新停止条件、授权隔离以及论文递进方面已形成自洽且
可执行的闭环。未发现新的实质阻断项。

VERDICT: APPROVED

### Resolution

Converged after four review rounds. No data, model, API, training, or experiment
authorization was inferred from approval. The next action remains author sign-off
on whether to implement the no-model planning/validation scaffold and, separately,
whether to authorize any future research-input construction.
