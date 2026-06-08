# 最终论文路线：Evidence Visibility for Candidate Patch Verification

本文档保存长期最终论文路线，并从 2026-06-08 起被指定为本项目后续目标的
规范入口。它不是当前必须立即执行的完整实验清单，也不替代
`docs/plans/current_plan_zh.md` 的轮次执行记录。当前 pilot、IEEE 草稿和中期
报告可以继续作为保底路线；后续研究推进应以本文件定义的 evidence visibility
实证路线为主线。

后续执行规则：

- 以本文件作为后续目标和任务拆解来源。
- 每轮具体执行仍必须先同步 `docs/plans/current_plan_zh.md`，记录本轮小目标、
  边界、验收条件和执行结果。
- 禁止直接跳到 80 bugs / 240 patches 的完整路线；必须先完成 Stage A/B，
  再根据 pipeline 稳定性进入 15-20 bugs 和 30-50 bugs 扩展。

## 1. 论文主线

当前课题应从：

> 比较 `LLM-only`、`evidence-first`、`tool-augmented` 三组结果差异。

升级为：

> 在候选补丁验证任务中，证据可见性如何系统性影响 LLM 的 false accept、
> correct recall、escalation 和 merge-gate 决策；LLM 相比 tool-only
> baseline 的真实贡献在哪里。

推荐英文题目：

> Evidence Visibility Matters: A Systematic Study of LLM-Based Verification
> for Candidate Patches

推荐中文题目：

> 证据可见性对大语言模型候选补丁验证的影响：一项系统性实证研究

如果后续真的构建了大量真实 AI-generated patches，可升级为：

> PatchEvidenceBench: Evaluating Evidence Visibility in LLM-Based Verification
> of AI-Generated and Real-Bug-Derived Patches

但在真实 AI-generated patches 未成为主体前，标题中应使用
`Candidate Patches`，不要过早写成 `AI-Generated Patches`。

## 2. 核心研究问题

### RQ1：LLM-only patch review 的误接收风险有多大？

目标不是证明 LLM 会犯错，而是量化：

- 在没有可执行证据时，LLM 是否会把 plausible but incorrect patches 判为
  `accept`；
- 哪些 failure types 最容易被误接收；
- false accept 是否集中在 partial fix、under-generalization、
  test-passing wrong patch 等类型上。

### RQ2：prompt-only evidence-first 是否真正解决问题？

当前 full run 已经显示：prompt-only evidence-first 降低 false accept 的同时
牺牲 correct recall。后续应将其表述为：

> Prompt-only evidence discipline may make the verifier conservative rather
> than reliably correct.

这是一条有价值的负结果，不应被改写为正向结论。

### RQ3：哪类 evidence 最能改变 LLM 的 patch acceptance decision？

这是最终论文的核心贡献。后续不应只比较三组条件，而应做 evidence
visibility ablation。

建议 evidence levels：

| Level | Verifier 可见信息 |
| --- | --- |
| E0 | issue summary + patch diff |
| E1 | E0 + modified files / changed functions |
| E2 | E1 + static/apply/syntax/import result |
| E3 | E2 + failing test names / runtime trace |
| E4 | E3 + visible fail-to-pass and pass-to-pass test results |
| E5 | E4 + generated targeted test results |
| E6 | E5 + realistic full tool evidence summary |
| E7 | oracle upper bound，单独报告，不作为真实可见设置 |

需要回答：

- 从 E0 到 E6，false accept 是否下降；
- correct recall 是否下降；
- escalation 是否增加；
- 哪一层 evidence 对决策影响最大；
- E6 是否真的优于 tool-only rule；
- E7 是否只是 oracle leakage upper bound。

### RQ4：LLM 相比 tool-only baseline 的真实贡献是什么？

必须正面回答审稿人最可能提出的问题：

> 如果工具结果已经很强，LLM 是否只是复述工具输出？

应比较：

| Baseline / Method | 作用 |
| --- | --- |
| accept-all | 天真下界，暴露最大 false accept 风险 |
| reject-all | 安全但不可用的下界 |
| escalate-all | 人工负担上界 |
| test-only rule | 只看测试是否通过 |
| tool-only rule | 只用规则化工具证据判断 |
| LLM-only | 只看 issue 和 diff |
| prompt-only evidence-first | 只靠 prompt discipline |
| LLM + visible evidence | 看不同层级 evidence |
| LLM + calibrated escalation | 允许不确定时升级人工 |

如果 tool-only 与 LLM+tool 接近，不是失败。论文可以写成：

> For clear executable outcomes, tool evidence dominates binary decisions; LLMs
> mainly add value in evidence synthesis, explanation, and calibrated
> escalation under uncertainty.

### RQ5：不同 patch 来源和 bug 类型是否影响 verifier 行为？

后续需要分析：

- reference fix；
- no-op patch；
- irrelevant patch；
- constructed partial fix；
- real LLM-generated patch；
- agent-generated patch；
- test-passing but wrong patch；
- regression-introducing patch；
- hallucinated API patch；
- over-broad patch；
- under-fix patch。

每条 candidate patch 至少应有两个标签：

- `patch_source_label`: reference / constructed / llm_generated /
  agent_generated；
- `failure_type_label`: partial_fix / regression / hallucinated_api /
  overfitting / non_applicable / syntactic_invalid 等。

## 3. 数据集扩展路线

### 3.1 数据源

建议分三层：

| 层级 | 数据来源 | 用途 |
| --- | --- | --- |
| 主数据源 | BugsInPy | Python 真实 bug，环境相对可控，适合主实验 |
| 扩展数据源 | SWE-bench Lite / Verified 子集 | 更贴近 GitHub issue / PR 场景 |
| 对照数据源 | 当前构造型 patches | 保留 no-op、irrelevant、partial fix 等 negative controls |

短期不要同时铺开所有来源。优先把 BugsInPy pipeline 跑顺，再考虑 SWE-bench。

### 3.2 目标规模分档

| 档位 | Bugs | Candidate patches | 用途 |
| --- | ---: | ---: | --- |
| 中期增强版 | 15-20 | 60-80 | 支撑中期报告和方向可行性 |
| 硕士论文稳健版 | 30-50 | 100-180 | 完整硕士论文主实验 |
| CCF C/B 冲刺版 | 60-80 | 180-240 | 较强实证研究 |
| Benchmark 版 | 100+ | 300+ | 更接近 benchmark/tool paper |

当前不应把 80 bugs / 240 patches 作为下一轮最低要求。它应作为长期目标。

### 3.3 Candidate patch 来源比例

长期目标比例：

| Patch 类型 | 建议比例 |
| --- | ---: |
| reference fix | 15-20% |
| constructed controls | 20-25% |
| real LLM-generated patches | 45-55% |
| real agent-generated patches | 10-20% |

真实 AI-generated patch 生成协议必须固定：

- Input: issue/bug description + allowed repository context；
- Forbidden: reference patch、hidden evaluator tests、post-fix code；
- Budget: 固定 token budget / attempts；
- Output: unified diff；
- Validation: 所有 patches 走同一 validation pipeline。

每个生成 patch 必须记录：

- prompt；
- retrieved files；
- generated patch；
- temperature；
- token cost；
- whether patch applies；
- validation outcome；
- failure logs。

## 4. Evidence 与 hidden evaluator 分离

这是论文科学性的底线。

### Visible evidence

Verifier 可以看到：

- issue description；
- candidate patch；
- patch apply result；
- syntax/import/lint result；
- visible failing test trace；
- visible pass-to-pass test result；
- generated targeted test result；
- coverage/static analysis summary。

### Hidden evaluator

Verifier 不能看到：

- hidden fail-to-pass tests；
- hidden regression tests；
- manual validation notes；
- reference patch diff；
- oracle behavior summary；
- final label。

如果 tool-augmented verifier 看到 hidden evaluator，结果只能作为
`oracle upper bound`，不能作为真实 merge-gate 能力。

## 5. Baseline 体系

必须 baseline：

1. Accept-all；
2. Reject-all；
3. Escalate-all；
4. Test-only rule；
5. Tool-only rule；
6. LLM-only；
7. Prompt-only evidence-first；
8. LLM + visible evidence；
9. LLM + generated tests；
10. LLM + full realistic tool evidence。

建议 tool-only rule：

```text
if patch does not apply:
    reject
elif syntax/import/lint fails:
    reject or escalate
elif visible fail-to-pass tests fail:
    reject
elif pass-to-pass regression tests fail:
    reject
elif generated targeted tests reveal defect:
    reject or escalate
elif all visible tests pass but evidence coverage is weak:
    escalate
else:
    accept
```

可选加分 baseline：

- self-consistency verifier；
- cross-model verifier；
- evidence-blind verifier；
- issue-blind verifier；
- explanation-constrained verifier；
- calibrated verifier。

## 6. 指标体系

### 安全指标

- False Accept Rate；
- Accepted Precision；
- Critical False Accept；
- Regression Accept Rate。

其中 False Accept Rate 是主指标，因为 merge gate 最怕错误 patch 被接收。

### 可用性指标

- Correct Recall；
- Escalation Rate；
- False Reject Rate。

需要强调：全 reject 很安全，但无工程价值。

### 解释质量指标

人工抽样标注：

- Evidence-supported explanation rate；
- Unsupported claim rate；
- Contradiction rate；
- Actionability score。

### 成本指标

- Token cost per decision；
- Runtime cost per decision；
- Cost per false accept avoided；
- Human escalation workload。

### 统计分析

至少需要：

- Wilson confidence interval；
- bootstrap confidence interval；
- per-project breakdown；
- per-patch-source breakdown；
- per-evidence-level comparison；
- McNemar test 或 bootstrap paired comparison；
- effect size，不只报告 p-value。

## 7. Failure taxonomy

长期 taxonomy：

| Failure type | 说明 |
| --- | --- |
| partial_fix | 只修一部分 bug |
| overfitting_patch | 通过已有测试但未真正修复 |
| regression_introducing | 修当前 bug 但破坏已有行为 |
| hallucinated_api | 使用不存在或不兼容 API |
| irrelevant_edit | 改无关代码 |
| no_op_patch | 几乎没有有效行为改变 |
| brittle_hardcoding | 针对测试硬编码 |
| under_generalization | 只处理特例 |
| over_generalization | 改动过宽，引入副作用 |
| environment_specific | 依赖特定环境或版本 |
| non_applicable | patch 无法应用或冲突 |
| syntactic_invalid | 语法或导入错误 |

分析目标：

- LLM-only 最容易误接收哪类 patch；
- generated tests 最容易发现哪类错误；
- tool-only 对哪类 patch 已足够；
- LLM 对哪类 ambiguous case 有帮助。

## 8. Generated tests 路线

Generated targeted tests 是冲 90+ 的增强项，但不能过早进入主线。

推荐最小 Python 版本：

1. 从 issue 和 modified function 中抽取目标行为；
2. 生成 3-5 个 targeted tests；
3. 在 buggy、patched、reference fixed 版本上运行；
4. 只把 visible generated test outcomes 给 verifier；
5. hidden evaluator 仍然保留；
6. 人工抽检 generated tests，避免错误测试污染结论。

关键边界：

- generated tests 不能由 reference patch 泄漏；
- test generation 和 verifier decision 要分离；
- generated tests 失败不必自动 reject，可以作为 evidence；
- generated tests 对论文的作用应是 evidence level，而不是 hidden label。

## 9. 多模型设计

长期 verifier 至少包含：

- 当前主模型；
- 另一个不同厂商/架构的强模型；
- 一个开源或较小模型。

patch generator 至少包含：

- simple prompting；
- retrieval-augmented patch generation；
- agent-style patch generation。

论文重点不是模型排行榜，而是：

> evidence visibility trend 是否跨模型稳定。

## 10. Artifact 目标结构

长期 artifact 目标：

```text
PatchEvidenceBench/
  data/
    tasks/task_metadata.jsonl
    patches/candidate_patches.jsonl
    patches/patch_files/
    evidence/visible_evidence/
    evidence/hidden_evaluator/
    labels/patch_labels.jsonl
  prompts/
    verifier_prompts/
    generator_prompts/
    test_generation_prompts/
  scripts/
    build_tasks.py
    generate_patches.py
    validate_patches.py
    build_evidence_packets.py
    run_verifiers.py
    compute_metrics.py
    bootstrap_ci.py
    make_tables.py
    make_figures.py
  docker/
    Dockerfile
    environment.yml
  results/
    raw_verdicts/
    metrics/
    figures/
    failure_cases/
  docs/
    schema.md
    reproduction.md
    threat_model.md
    leakage_policy.md
```

必须有 `leakage_policy.md`，写清楚：

- verifier 不能看到 reference patch；
- verifier 不能看到 hidden evaluator；
- oracle upper bound 单独报告；
- generated tests 和 hidden tests 分离；
- prompt 中不包含 label；
- patch source 是否可见应作为 ablation 控制。

## 11. 论文 contributions

最终 contributions 建议：

1. **任务定义**：将 candidate patch verification 定义为
   accept/reject/escalate merge-gate decision problem under varying evidence
   visibility。
2. **数据集**：构建 real-bug-derived 与 AI-generated candidate patches 的
   benchmark-style dataset。
3. **证据可见性消融**：系统改变 evidence visibility，衡量 false accept、
   correct recall、escalation 和 explanation reliability。
4. **LLM vs tool-only**：比较 LLM-based verification 与 rule-based
   tool-only baselines，隔离 LLM 的真实增益。
5. **failure taxonomy**：总结 false accepts 和 false rejects 的主要失败模式。

## 12. 推荐论文结构

1. Introduction；
2. Background and Related Work；
3. Problem Definition；
4. Dataset Construction；
5. Experimental Design；
6. Results；
7. Discussion；
8. Threats to Validity；
9. Artifact and Reproducibility；
10. Conclusion。

## 13. 实际推进阶段

### Stage A：当前 pilot 保底

目的：支撑中期和保底论文雏形。

产物：

- pilot metrics；
- failure cases；
- tool-only baseline；
- 中期报告材料。

### Stage B：重构 schema 和 pipeline

目的：让扩展不是手工堆数据。

必须完成：

- TaskRecord；
- PatchRecord；
- EvidencePacket；
- ValidationOutcome；
- VerifierDecision。

### Stage C：扩 BugsInPy 到 30-50 bugs

筛选标准：

- 环境稳定；
- buggy version 有可复现 failing test；
- reference fix 可应用；
- 测试运行时间可控；
- 项目分布尽量均衡；
- bug 类型不单一。

### Stage D：生成真实 AI candidate patches

每个 task 用 2-3 种生成策略，每个 generator 最多保留 1-2 个 patch。

### Stage E：构建 evidence visibility ablation

至少完成：

- diff-only；
- prompt-only evidence-first；
- static/apply evidence；
- runtime trace；
- visible tests；
- full realistic tool evidence；
- oracle upper bound，单独报告。

### Stage F：加入 tool-only 和多 verifier

核心问题：

- LLM 是否优于 tool-only；
- LLM 在哪里有帮助；
- LLM 在哪里有害；
- evidence visibility trend 是否跨模型稳定。

### Stage G：generated tests 与人工审计

只在 Stage A-F 稳定后进入。

## 14. 风险与处理

### 风险 1：扩数据后环境崩溃

处理：先做 task stability screening。宁可 50 个高质量任务，不要 150 个半坏任务。

### 风险 2：AI-generated patches 质量太差

处理：保留 non-applicable patch 作为 failure type，但控制比例。允许每个 generator
做一次 basic apply repair loop。

### 风险 3：tool evidence 泄漏 hidden label

处理：visible evidence 和 hidden evaluator 分开存储；oracle upper bound 单独报告。

### 风险 4：LLM 没有超过 tool-only

处理：不强行改结论。将结论改为 LLM 的价值主要在 evidence synthesis、
explanation 和 calibrated escalation。

### 风险 5：贡献被已有 patch correctness assessment 工作覆盖

处理：强调四个差异：

- accept/reject/escalate merge-gate decision；
- evidence visibility ablation；
- tool-only vs LLM contribution isolation；
- AI-generated candidate patch distribution。

## 15. 执行策略

采用双轨策略：

### 轨道 A：短期保底

维护当前 pilot，补：

- tool-only baseline；
- qualitative failure cases；
- confidence intervals；
- 中期报告材料；
- claim 边界。

### 轨道 B：长期最终论文

启动：

- data schema；
- task expansion；
- AI patch generation；
- evidence ablation；
- multi-model verifier；
- generated tests；
- artifact。

如果轨道 B 因环境或数据问题受阻，轨道 A 仍可支撑中期报告和保底论文。

## 16. 当前建议

下一步不应直接启动 80 bugs / 240 patches 的完整路线。更稳妥的路线是：

1. 保存本文件作为最终论文路线；
2. 继续准备中期报告材料；
3. 在当前 pilot 上补 tool-only baseline 和 qualitative cases；
4. 再扩到 15-20 bugs；
5. 最后根据环境稳定性决定是否进入 30-50 bugs 的硕士论文稳健版。

本路线的最终定位：

> LLM patch verification 的可靠性不是模型单独决定的，而是由 evidence
> visibility 决定的。diff-only 条件下模型容易误接收 plausible wrong
> patches；prompt-only evidence discipline 会牺牲 recall；runtime evidence、
> generated tests 和 tool-visible summaries 能改变 safety/recall/escalation
> tradeoff；但 tool-only baseline 已能解决一部分明确案例，LLM 的主要价值在于
> 证据综合、解释和不确定场景下的升级判断。
