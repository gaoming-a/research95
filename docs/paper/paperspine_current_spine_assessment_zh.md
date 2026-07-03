# PaperSpine-style 当前论文脉络与后续方向整理

日期：2026-07-03

## 0. 使用边界

本文档借用 PaperSpine 的三个核心关卡思想：贡献为先、结果即验证、面向审稿人。
参考源为 PaperSpine 项目说明：
`https://github.com/WUBING2023/PaperSpine`。本轮没有安装或运行外部
PaperSpine workflow，也没有调用模型 API。

本整理只使用当前仓库中的 tracked aggregate artifacts：

- `docs/paper/ccfc_manuscript_rewrite_v0_1.md`
- `docs/paper/final_manuscript_claim_map_v0_1.md`
- `data/reviews/final_manuscript_claim_map_v0_1.json`
- `data/reviews/final_experiment_setting_validity_audit_v0_1.json`
- `docs/figures/ccfc/`
- `docs/paper/ccfc_revision_response_v0_2.md`

明确不使用：

- ignored raw outputs；
- rendered prompt text；
- patch diff 原文；
- 新 API 调用；
- 早期无效设置作为论文-facing 证据。

## 1. Confirmed Contribution

当前最稳的唯一贡献是：

> EVP-8 是一个 hidden-evaluator evidence-visibility protocol，用于测量
> LLM candidate patch verifier 在不同可见证据条件下的 merge-gate risk
> behavior；当前结果显示 evidence visibility 会改变 acceptance、false
> acceptance、escalation 和 tool-summary dependence，但不证明 LLM 能可靠自动
> 判断补丁正确性。

这个贡献有三个组成部分：

1. 协议贡献：EVP-8 将 model-visible evidence 与 evaluator-only labels 隔离。
2. 测量贡献：用 post-decision label join 计算 accepted precision、correct
   recall、false accept rate、false reject rate 和 escalation rate。
3. 风险行为贡献：用 Qwen v0.3、E6 ablation 和 tool-contestation 显示模型更像
   evidence-conditioned risk controller，而不是 semantic correctness verifier。

不应该写成的贡献：

- 新的自动程序修复算法；
- LLM 比传统 verifier 更强；
- 更多 evidence 单调提升 correctness；
- escalation 等同于 strict correction；
- fresh realistic branch 已经支持三项目真实 verifier 实验。

## 2. Confirmed Motivation

当前论文的动机应该这样收束：

候选补丁可能看起来合理，但是否可以 merge 取决于审查时可见的证据。LLM 可以读
代码、测试和工具摘要，但如果评估不控制 evidence visibility，就无法区分模型能力、
证据呈现、工具摘要锚定和 prompt-induced caution。软件质量场景需要的不是泛化地
宣布 LLM 会不会修补丁，而是测量在不同证据条件下，LLM 如何选择 accept、reject 或
escalate。

这个 motivation 与当前实验结果匹配；它不需要把早期无效设置写进正文，也不需要
继续追求“LLM 自动验证补丁正确性”的强叙事。

## 3. Result-to-Claim Matrix

| result unit | current evidence | claim it validates | status | boundary |
| --- | --- | --- | --- | --- |
| EVP-8 protocol | 98 candidate patches, E0-E6 evidence ladder, hidden evaluator join | 可以定义并审计 model-visible / evaluator-only evidence boundary | strong for protocol | 不是模型有效性证明 |
| Qwen v0.3 label-conditioned metrics | E0-E2 correct recall 0.00%；E3 80.95%；E4-E5 85.71%；E6 95.24%；E6 accepted precision 83.33%，4/77 false accepts | repaired evidence 会打开 correct-patch acceptance，同时带来 bounded false-accept risk | main result, Qwen-only | 不支持五模型泛化或 evidence-level ranking |
| E6 rule-only / full / no-verdict | rule-only、DeepSeek/Qwen E6-full、DeepSeek/Qwen E6-no-verdict 对比 | verdict-like tool summaries 会影响风险策略，且模型间差异明显 | useful ablation | 不是 semantic understanding proof |
| EVP-8-HARD tool-contestation | DeepSeek 9/9 false accepts 转 escalation；Qwen 8/9 转 escalation，0 strict reject | contestation 主要提升 safe handling / triage，不是 strict correction | strong boundary evidence | 不可把 escalation 写成 correction |
| realistic hard-negative branch | 26/30 cases，2/3 projects，gate failed | realistic source acquisition 仍是边界，不能作为 main verifier experiment | negative boundary | 不可支撑三项目真实场景主实验 |
| final setting-validity audit | `passed_with_bounded_claims` | 当前结果是真实 bounded evidence，而非当前论文主线中的设置假象 | necessary gate | 仍需承认 cohort / prompt / external validity 风险 |

PaperSpine-style 结论：当前每个主要结果都能绑定到一个贡献承诺；最弱的是
external validity 和 baseline breadth，不是主线逻辑。

## 4. Current Paper Spine

当前最顺的论文 spine 是：

1. 软件补丁审查需要在可见证据边界下做 merge-gate decision。
2. 现有 LLM patch-review 评估如果不控制 evidence visibility，容易混淆模型能力与
   evidence presentation。
3. EVP-8 提供 hidden-evaluator evidence-visibility protocol。
4. Qwen v0.3 repaired evidence 显示：visible executable/tool evidence 能打开
   correct acceptance，但带来 false-accept tradeoff。
5. E6 ablation 显示：verdict-like tool summaries 会影响模型风险策略。
6. Tool-contestation 显示：模型主要把风险转向 escalation，不是 strict semantic
   correction。
7. Realistic hard-negative branch 未过 gate，因此真实场景推广必须保守。
8. 论文结论：EVP-8 支撑 evidence-conditioned risk behavior measurement，不支撑
   reliable autonomous patch correctness verification。

这条 spine 是自洽的。它的优势是保守、可审计、claim 边界清楚；劣势是贡献力度偏
方法测量，实证规模和 baseline 仍偏弱。

## 5. CCF-C Readiness Audit

### 当前可投性判断

当前状态不是 final submission ready，但已经具备 CCF-C 可冲底稿基础。我的判断是：

- 直接投稿：borderline，偏高风险；
- 补最小 baseline 和 verified citations 后投稿：有现实 CCF-C 机会；
- 若想冲更稳或更高档次：需要扩外部有效性或补第三项目 realistic gate，但这会明显
  增加时间和不确定性。

### 主要强项

- 问题定位现在清楚：不是 LLM patch correctness，而是 evidence-conditioned risk
  behavior。
- EVP-8 的 hidden-evaluator boundary 是可复现的方法贡献。
- Qwen v0.3 主表有明确指标和数值，不再是审计日志式叙述。
- E6 ablation 与 tool-contestation 能支撑机制/风险解释。
- final validity audit 已把 leakage、raw-output-free、post-decision label join 和
  forbidden claims 收束。

### 主要拒稿风险

1. Baseline 不足。
   目前 tracked artifact 中只有 rule-only 和 no-verdict/with-verdict 对比；always
   escalate、random、majority、完整 E0/no-tool baseline 仍未作为完成结果。

2. 主正向结果 Qwen-only。
   五模型 synthesis 可作为协议覆盖背景，但当前最强 label-conditioned 主结果来自
   Qwen v0.3。审稿人可能认为模型泛化不足。

3. Related work 仍薄。
   需要 verified citations 支撑 APR plausible patch、test adequacy、LLM-as-reviewer、
   selective prediction/abstention、LLM-as-judge/tool anchoring。

4. Realistic branch 未过 gate。
   这不是致命问题，但必须严格写成 source-acquisition boundary。如果正文试图把它
   用来增强真实场景结论，会被抓住。

5. 统计呈现仍偏描述性。
   Phase A confidence intervals 已 tracked，但正文没有系统展开。CCF-C 未必强制更
   复杂统计，但最好补一个 concise uncertainty paragraph 或 appendix table。

## 6. Next Direction Priority

### P0：不再做的事

- 不把早期无效设置放回正文；
- 不继续无目标堆模型；
- 不在 `ready_for_verifier_api=false` 时运行 verifier API；
- 不把 realistic branch 未过 gate 解释成主实验证据；
- 不把 escalation 写成 correction。

### P1：最短稳妥 CCF-C 路线

1. 补 verified related work citations。
   优先级最高，因为当前 related work 是 CCF-C 审稿人最容易指出的写作缺口。

2. 补最小 baseline 表或明确 baseline boundary。
   最稳做法是优先补不需要 API 的 deterministic baselines：always-escalate、
   always-reject、majority/rule variants。如果当前 artifact 已能从 aggregate labels
   计算，应走 no-API 脚本；如果不能，先写 baseline feasibility audit。

3. 加一段 uncertainty / confidence interval summary。
   使用已 tracked Phase A confidence intervals，不新增实验。

4. 调整正文结构为 CCF-C conference style。
   把审计性文字压缩到 Methods / Threats，把 Results 写成
   claim-first + metric support + boundary。

### P2：增强但有风险的路线

1. 扩 Qwen 以外的 label-conditioned repaired analysis。
   价值：提升外部有效性。风险：需要更多 API/执行链路，可能引入新不确定性。

2. 修 realistic third-project gate。
   价值：增强真实场景可信度。风险：时间和失败概率高，不适合“稳妥写完”优先目标。

3. 扩更多项目/任务。
   价值：更强经验研究。风险：容易变成新课题，不适合当前 CCF-C 稳投路径。

## 7. Immediate Action Plan

当前建议按下面顺序推进：

1. 先做 citation support bank：为 introduction、related work、discussion 和 threats
   准备 verified references。
2. 做 deterministic baseline feasibility audit：确认能否从现有 aggregate labels 直接
   计算 always-escalate / always-reject / majority/rule baseline。
3. 如果可无 API 计算，生成 baseline table 并更新正文；如果不可计算，正文明确
   baseline limitation，不伪造结果。
4. 将 Phase A confidence intervals 以简短段落或 appendix table 接入正文。
5. 再进行一次 reviewer-aware audit，判断是否进入投稿格式整理。

## 8. Final Assessment

基于 PaperSpine-style spine audit，当前论文已经有一个可成立的 CCF-C 方向：

> A bounded empirical methods paper on evidence visibility and risk behavior in
> LLM-based candidate patch verification.

它当前最像一篇 CCF-C 边界内的软件工程实证/方法测量论文，而不是模型能力论文。
如果目标是“稳妥写完”，下一步不应该扩实验，而应该补引用、补最小 baseline、
压实结构和投稿格式。

当前结论：可以继续按 CCF-C 稳妥投稿路线推进，但还不应宣布 final submission
ready。
