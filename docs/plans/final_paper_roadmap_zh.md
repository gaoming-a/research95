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
- 2026-06-09 起，研究主线明确不改为 patch generation。AI patch
  generation 是 candidate 来源和 failure taxonomy 的一部分，不是主实验要证明
  成功的对象。
- 主实验任务集必须按 validation stability 和 dataset balance 重构；每个 bug
  不要求都有 AI-generated correct patch，但每个纳入任务必须有可靠 ground
  truth 和可复现 validation。

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

边界：

- 本文研究问题是 **candidate patch verification**，不是 **patch
  generation**。
- AI-generated patches 可以是 correct、incorrect、partial、
  non-applicable 或 generation failure；它们都应被记录和分类。
- 不能把“某个 bug 没有生成出正确 AI patch”解释为课题失败。只有 ground
  truth 不稳定、reference patch 无法验证、环境不可复现时，任务才应从主实验
  排除。

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

长期目标比例应在数据集层面平衡，而不是要求每个 bug 都有完整正负样本。
每个 validation-stable bug 最好至少有一个 reference correct patch；AI-generated
correct patch 不是每个 bug 的硬性要求。

长期目标候选组成：

| Patch 类型 | 建议比例 |
| --- | ---: |
| reference correct patches | 20-30% |
| AI-generated correct patches | 10-25% |
| AI-generated incorrect / partial patches | 35-50% |
| constructed controls | 15-25% |
| non-applicable / syntactic-invalid patches | <= 10-15% |

真实 AI-generated patch 生成协议必须固定：

- Input: issue/bug description + allowed repository context；
- Forbidden: reference patch、hidden evaluator tests、post-fix code；
- Budget: 固定 token budget / attempts；
- Output: unified diff 或 strict agent edit-plan 后由本地 `git diff`
  materialize；
- Validation: 所有 patches 走同一 validation pipeline；
- Reporting: 必须报告 generator success rate，不只报告 verifier metrics。

每个生成 patch 必须记录：

- prompt；
- retrieved files；
- generated patch；
- temperature；
- token cost；
- whether patch applies；
- validation outcome；
- failure logs。

每个 task 必须记录 generator accounting：

- `environment_stable`: true / false；
- `reference_patch_valid`: true / false；
- `generator_attempts`；
- `num_ai_patches_generated`；
- `num_ai_patches_applicable`；
- `num_ai_patches_correct`；
- `num_ai_patches_incorrect`；
- `generation_status`: solved / partially_solved / unsolved /
  non_applicable_only；
- `main_experiment_included`: true / false；
- `exclusion_reason`。

这些字段用于区分 patch generation failure 与 patch verification
performance，避免因为删除 generator-unsolved tasks 造成 cherry-picking。

### 3.4 任务纳入、排除与 hard-generation case

任务纳入主实验的必要条件：

1. buggy version 能稳定复现目标 failure；
2. reference patch 能稳定通过 fail-to-pass check；
3. pass-to-pass regression checks 不 flaky；
4. patch apply / revert 可复现；
5. validation runtime 可控；
6. hidden evaluator label 可靠。

只有 validation 不稳定时才从主实验排除。排除理由应写成：

> Excluded because the task did not satisfy reproducible validation criteria.

不能写成：

> Excluded because the model failed to solve it.

`bugsinpy_httpie_5` 的当前角色：

- 若 reference patch 和 retained oracle 稳定，则保留为
  `hard_generation_case`；
- 不再要求它产出 AI-generated correct patch；
- 可保留 1 个 reference correct patch、2-3 个 AI-generated incorrect patches、
  1 个 constructed partial/control patch；
- 不围绕它继续做单任务 prompt 调参；
- 在论文或 appendix 中报告为 fixed generation budget 下的 failure/stress case。

如果后续发现 `httpie_5` 的环境、reference patch 或 oracle 不稳定，则从主实验
剔除，并进入 excluded tasks table。

### 3.5 Pass-to-pass scope

最终主实验采用双层 pass-to-pass：

- `P2P-core`：与修改区域、功能路径或相邻模块相关的非失败测试，用于快速
  smoke regression audit；
- `P2P-broad`：当前实验环境下整个可运行且稳定通过的测试子集，用于最终主
  实验标签和 merge-gate 指标。

`P2P-broad` 定义为满足以下条件的最大测试集合：

1. 能在当前实验环境中被收集；
2. 不属于 retained fail-to-pass oracle；
3. 在 buggy baseline 上稳定通过；
4. 在 reference-fixed version 上稳定通过；
5. 不依赖外部网络、缺失服务、随机环境或本地私有配置；
6. 在设定 timeout 内稳定完成。

最终 label 规则：

```text
if patch does not apply:
    label = non_applicable
elif retained oracle fails:
    label = incorrect_issue_not_fixed
elif p2p_broad fails:
    label = incorrect_regression
else:
    label = correct_under_f2p_and_p2p_broad
```

最终主实验的 `P2P-broad` scope type 必须记录为
`project_level_p2p_broad`。任务相关测试文件内的 P2P scope 只能作为开发期
smoke audit 或 appendix 边界结果，不能用于声称 project-level regression
stability。

当前执行状态：

- `httpie_5` 已完成 project-level P2P-broad manifest：17 个 collected
  tests 中，排除 1 个 fail-to-pass oracle 和 13 个外部网络依赖测试，保留
  3 个稳定本地 P2P-broad tests。由于该项目当前只发现 1 个测试文件，
  project-level 与早期局部 scope 结果一致。
- `cookiecutter_1` / `cookiecutter_2` / `cookiecutter_3` 已完成独立的
  project-level P2P-broad manifest，并通过 retained oracle 与 P2P-broad
  candidate validation。
- `tqdm_9` 已完成 project-level P2P-broad manifest：14 个 collected tests
  中，排除 2 个 fail-to-pass oracle，保留 12 个稳定 P2P-broad tests。
  该任务也记录了 partial-candidate curation 规则：reference diff 中的
  style-only changes 不能自动构成错误负例。
- `luigi_3` / `luigi_4` 的早期 P2P-broad 是 task-file scope，不是最终主
  实验标准。Luigi project-level scope 当前需要单独解决全项目测试量、收集
  错误和长运行时间问题后才能进入最终主实验标签。

当前 cohort 决策：

- 主实验只使用 `p2p_broad_main` cohort：
  - `project_level_p2p_status == completed`；
  - `p2p_broad_main_included == true`。
- 当前进入 `p2p_broad_main` 的任务为：
  - `bugsinpy_httpie_5`；
  - `bugsinpy_cookiecutter_1`；
  - `bugsinpy_cookiecutter_2`；
  - `bugsinpy_cookiecutter_3`；
  - `bugsinpy_tqdm_9`。
- `bugsinpy_luigi_3` / `bugsinpy_luigi_4` 当前标记为
  `pending_blocked`，task-file P2P 结果只保留为 appendix/smoke evidence，
  不参与最终 regression-aware 主指标。
- `bugsinpy_httpie_1` 到 `bugsinpy_httpie_4` 已经过 bounded feasibility
  sweep，但当前未进入 `p2p_broad_main`：阻塞原因包括缺少真实
  `pytest_httpbin` 测试依赖、legacy compatibility 和 project-level scope
  timeout。
- `bugsinpy_tqdm_1` / `bugsinpy_tqdm_2` 已经过 bounded feasibility sweep；
  两者均只保留 1 个 stable P2P-broad test，低于 `p2p_broad_size >= 3`
  门槛，因此不进入主指标。
- `bugsinpy_tqdm_3` 到 `bugsinpy_tqdm_8` 已经过 follow-up screening；
  在不安装新依赖的情况下只收集到
  `tqdm/tests/tests_version.py::test_version`，行为相关测试文件仍受 legacy
  `nose` 路径阻塞，因此当前不进入主指标。
- `unittest` adapter 已加入 P2P scope builder，用于避免因测试框架限制
  排除任务；`bugsinpy_black_1` / `bugsinpy_black_3` 已通过该 adapter
  筛选，但当前因缺少真实 `typed_ast` 依赖而标记为 `pending_blocked`。
- `bugsinpy_black_2` 已经过 follow-up screening，也因相同 `typed_ast`
  import blocker 而标记为 `pending_blocked`。
- cohort registry 为 `data/cohorts/task_cohort_registry.json`。
- 2026-06-11 决策：下一阶段不优先修复 legacy `nose` blocker 或 Black
  `typed_ast`/MSVC blocker；这些任务保留为 blocked feasibility cases。
  主线转向引入更多 BugsInPy 项目作为新候选池，并继续使用相同
  project-level P2P-broad 纳入标准。

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
   benchmark-style dataset；AI-generated patches 不要求每个 task 都包含
   correct generated repair，但必须记录 generator attempts、failure modes 和
   validation outcomes。
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

当前状态：

- `httpie_stage_ab_001` 已完成首个 Stage A/B 小闭环：5 个 `httpie` tasks、
  22 个 candidates、22/22 executable validations、no-API baselines、
  tool-only baselines 和 44 条 prompt-boundary dry-run records。
- 已补充 AI patch generation diagnostics：direct diff 生成 apply failure 高；
  agent-style workflow 可稳定 materialize generated negative patches，但当前没有
  稳定产出 correct repairs。
- `bugsinpy_httpie_5` 当前不作为主成功案例；若 validation 继续稳定，则保留为
  hard-generation/stress case。

### Stage B：重构 schema 和 pipeline

目的：让扩展不是手工堆数据。

必须完成：

- TaskRecord；
- PatchRecord；
- EvidencePacket；
- ValidationOutcome；
- VerifierDecision。

当前状态：

- 已有长期 schema 文档和 leakage policy；
- 当前 builder 已支持按 `--task-id` 和 `--run-id` 生成独立 dataset slice；
- 仍需把 task-level generator accounting 接入同一 schema，区分
  validation-stable hard case、generator failure 和真正 excluded task。

### Stage C：扩 BugsInPy 到 30-50 bugs

筛选标准：

- 环境稳定；
- buggy version 有可复现 failing test；
- reference fix 可应用；
- 测试运行时间可控；
- 项目分布尽量均衡；
- bug 类型不单一。

### Stage D：生成真实 AI candidate patches

每个 task 用 2-3 种生成策略，每个 generator 最多保留 1-2 个 admitted
patch。生成预算固定，生成失败也必须记录。

Stage D 的目标不是证明 generator 能修好每个 bug，而是构造真实候选补丁分布：

- correct AI-generated patch；
- incorrect AI-generated patch；
- partial fix；
- non-applicable diff；
- syntactic/import failure；
- generation timeout / empty output / exact edit failure。

执行规则：

- 不删除 generator-unsolved task，除非 validation 本身不稳定。
- 不围绕单个 hard case 无限调 prompt。
- 每发现 1 个 generator-unsolved hard case，应补充 1-2 个
  validation-stable tasks 来维持数据集平衡。
- non-applicable patches 可以保留为 failure type，但主实验占比控制在
  10-15% 以内。
- `httpie_5` 当前归类为 hard-generation/stress case，而不是主成功案例。

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

处理：

- 不改变研究主线；patch generation failure 是 verification motivation 的一部分。
- 保留 validation-stable 的 generator-unsolved tasks，并报告 generator success
  rate。
- AI-generated patches 如果无法形成 balanced main source，则降级为
  generated-negative / partial-fix extension。
- 保留少量 non-applicable patch 作为 failure type，但控制在 10-15% 以内。
- 允许每个 generator 做一次 basic apply repair loop，但不能针对单个 bug 反复
  调参到过拟合。

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
2. 先重构主实验任务集规则：每个 task 先判断 validation stability，再决定
   included / hard-generation case / excluded；
3. 将 `httpie_5` 暂定为 hard-generation/stress case，限制其候选数量，并补充
   1-2 个 validation-stable replacement tasks 来维持数据平衡；
4. 再扩到 15-20 bugs，保证数据集层面有足够 reference correct、
   AI-generated incorrect、constructed partial/control 和少量 non-applicable
   patches；
5. 继续准备中期报告材料；
6. 最后根据环境稳定性决定是否进入 30-50 bugs 的硕士论文稳健版。

本路线的最终定位：

> LLM patch verification 的可靠性不是模型单独决定的，而是由 evidence
> visibility 决定的。diff-only 条件下模型容易误接收 plausible wrong
> patches；prompt-only evidence discipline 会牺牲 recall；runtime evidence、
> generated tests 和 tool-visible summaries 能改变 safety/recall/escalation
> tradeoff；但 tool-only baseline 已能解决一部分明确案例，LLM 的主要价值在于
> 证据综合、解释和不确定场景下的升级判断。

## 17. 当前 Stage B/C 执行状态（2026-06-11）

当前 `p2p_broad_main` 已扩展到 8 个完成 project-level P2P-broad 的真实任务：

- `bugsinpy_httpie_5`
- `bugsinpy_cookiecutter_1`
- `bugsinpy_cookiecutter_2`
- `bugsinpy_cookiecutter_3`
- `bugsinpy_tqdm_9`
- `bugsinpy_PySnooper_1`
- `bugsinpy_PySnooper_3`
- `bugsinpy_youtube-dl_6`
- `bugsinpy_youtube-dl_7`

最新加入的 `bugsinpy_PySnooper_1` 使用独立 UTF-8 snoop-log oracle，包含 24 个
稳定 P2P-broad 测试和 6 个已验证 candidate patches。它确认了当前路线的关键
执行规则：新增任务可以来自 broader BugsInPy pool，但必须经过同一套
project-level P2P-broad 构造、retained oracle validation、F2P + P2P-broad
candidate revalidation 后才能进入主 cohort。

`bugsinpy_PySnooper_2` 被标记为 blocked feasibility case，因为它需要
compatibility/test-fixture shim 才能继续，当前阶段不允许这类 shim 进入主实验。
`bugsinpy_PySnooper_3` 则在只安装声明依赖、不引入 fixture shim 的情况下完成
project-level P2P-broad，包含 4 个稳定 P2P-broad 测试和 4 个已验证 candidate
patches。

下一阶段仍然不是修复 legacy `nose` 或 Black `typed_ast` / MSVC blocker，而是继续
筛选更多低摩擦 BugsInPy 项目，将主 cohort 扩展到 15-20 个 validation-stable
真实 bugs。

2026-06-13 更新：`bugsinpy_youtube-dl_7` 已在 retained oracle、4 个候选、
retained-oracle validation 和 108-test project-level P2P-broad validation
通过后正式纳入主 cohort。当时 EVP-7 tracked artifacts 为 8 tasks / 5 projects /
46 candidates / 184 E0-E6 packets。随后已完成 fresh DeepSeek V4 full run，
覆盖当前 184 packets；旧 168-packet run 只保留为 admission 前历史记录。

2026-06-13 后续更新：`bugsinpy_youtube-dl_6` 已按同一 admission gate 纳入，
包含 retained DFXP time oracle、4 个候选、retained-oracle validation 和
110-test project-level P2P-broad validation。当前 no-API tracked artifacts
已提升为 9 tasks / 5 projects / 50 candidates / 200 E0-E6 packets。此前
fresh DeepSeek V4 full run 只覆盖 8-task / 184-packet cohort；随后已完成
fresh 200-packet DeepSeek V4 G5 run，覆盖当前 9-task / 50-candidate /
200-packet cohort。该 run 支持 pilot evidence-visibility signal，但不支持
scale-generalized result 或 LLM 优于 deterministic tool-only baseline。

2026-06-13 再后续更新：`bugsinpy_youtube-dl_5` 已按同一 admission gate
纳入，包含 retained unified-timestamp oracle、4 个候选、retained-oracle
validation 和 128-test project-level P2P-broad validation。当前 no-API
tracked artifacts 已提升为 10 tasks / 5 projects / 54 candidates / 216
E0-E6 packets。随后已完成 fresh 216-packet DeepSeek V4 G5 run，覆盖当前
10-task / 54-candidate / 216-packet cohort。该 run 通过质量审计但仍有限制：
支持 bounded pilot observations，不支持规模泛化、不支持 LLM 优于
deterministic tool-only baseline、不支持已知真实计费成本。

2026-06-13 再后续更新：`bugsinpy_youtube-dl_2` 已按同一 admission gate
纳入，包含 retained MPD parser oracle、4 个候选、retained-oracle validation
和 147-test project-level P2P-broad validation。当前 no-API tracked artifacts
已提升为 11 tasks / 5 projects / 58 candidates / 232 E0-E6 packets。随后已完成
fresh 232-packet DeepSeek V4 G5 run，覆盖当前 11-task / 58-candidate /
232-packet cohort。该 run 在同 prompt/config/model 下重试 2 条空响应后得到
232/232 parse-valid 结果，G5 signal status =
`real_llm_verifier_signal_observed_on_evp7`，并通过 raw-output-free quality
audit，但仍只支持 bounded pilot observations，不支持规模泛化、LLM 优于
deterministic tool-only baseline 或已知真实计费成本。

## 18. 2026-06-12 外部建议提取后的增量修订

本节只记录相对既有路线图的增量约束。以下内容不得重复替代前文已经定义的
E0-E7 evidence levels、visible/hidden 分离、tool-only baseline、Candidate
Patches 标题和规模分档。

### 18.1 先修正文档一致性，再继续扩量

后续论文草稿、README、计划和 cohort registry 必须统一为当前主线：

- 研究对象是 `candidate patch verification under evidence visibility`；
- 当前主 cohort 是完成 `project_level_p2p_broad` 的任务集合，不再使用旧的
  “7 tasks / 2 projects” 表述；
- Luigi 的 task-file P2P 结果只能作为 appendix/smoke evidence，不能写入最终
  project-level 主指标；
- 当前 retained validation summary / oracle-style summary 只能作为诊断或上界
  风格证据，不能冒充 hidden-evaluator-free 的真实 merge-gate 设置。

在这些口径统一前，不应继续把旧 IEEE 草稿当作当前论文结论来源。

### 18.2 Evidence Visibility Curve 作为核心图形

最终论文应把 E0-E6 的主结果组织为一条
`Evidence Visibility Curve`，而不是只报告若干条件表格。核心曲线至少包含：

- false accept rate；
- correct recall；
- accepted precision；
- escalation rate；
- safety/utility trade-off。

E7 只作为 oracle upper bound 单独报告，不进入真实可见证据曲线。曲线的结论不
要求单调变好；如果证据增加带来 recall 下降或 escalation 上升，应解释为
safety/utility trade-off，而不是强行写成正向改进。

### 18.3 新指标只能作为校准指标，不能替代主指标

可以在主指标之外引入两个论文友好的派生指标，但必须做敏感性说明，不能用任意
权重制造结论。

`False-Accept Controlled Recall (FACR)`：

> 在 false accept rate 不超过预设安全阈值时，系统还能接受多少正确 patch。

`Evidence Gain (EG)`：

> `EG(Ek) = Utility(Ek) - Utility(E0)`。

Utility 可以采用如下保守形式：

```text
Utility = AcceptCorrect - lambda * AcceptWrong - mu * Escalate - nu * RejectCorrect
```

其中 `lambda` 必须显著高于 `mu` 和 `nu`，因为 merge gate 中错误接受 wrong
patch 的代价高于升级人工和错误拒绝正确 patch。正式论文中必须报告参数选择
理由，并至少做一组敏感性分析。

### 18.4 分阶段消融，避免一次性全因子爆炸

如果成本或数据规模不足，优先采用分阶段设计：

1. 全量任务先跑核心 evidence levels：`E0`、`E2`、`E4`、`E6`；
2. 只有当核心曲线稳定后，再补齐 `E1`、`E3`、`E5`；
3. 多模型稳健性优先跑关键层级：`E0`、`E4`、`E6`；
4. generated tests 仍是增强项，不能在 Stage A-F 未稳定前成为主线依赖。

这样可以保留 evidence-visibility 研究问题，同时避免把实验推进变成无法复现的
全量矩阵。

### 18.5 LLM 增量价值的判定边界

最终论文必须正面回答 LLM 是否超过 realistic tool-only baseline。允许出现三种
结论：

- LLM 明显优于 tool-only：报告其真实增量；
- LLM 与 tool-only 接近：写成 executable evidence dominates binary decisions；
- LLM 不如 tool-only：写成 LLM 不适合作为自动 merge gate，只适合 explanation
  或 calibrated escalation。

不能因为结果不漂亮而弱化 tool-only baseline。本文的创新在于隔离 evidence
visibility 对 merge-gate 决策的影响，而不是保证 LLM 总能超过工具规则。

### 18.6 扩量边界更新

30-50 bugs / 100-180 patches 是硕士论文稳健版目标，不是无条件硬门槛。若继续
BugsInPy 扩量，必须先解决当前候选池边界：

- 继续找低摩擦 BugsInPy 项目；
- 明确允许 isolated native/editable build；
- 引入 BugsInPy 之外的新 benchmark/source；
- 或接受较小但 visible/hidden、baseline 和统计设计更干净的数据规模。

这些选择会改变实验边界，不能由执行代理私自决定。

## 19. 2026-06-12 EVP-7 protocol pilot 决策

已确认选择 Option A：

- 冻结当时 BugsInPy low-friction cohort：7 bugs / 4 projects；
- 停止继续以“第 8 个 bug”为目标盲扫 BugsInPy；
- 立即转入 `EVP-7 Protocol Pilot`，先验证现有 7 个样本能否在最终
  evidence-visibility protocol 下产生论文级信号。

2026-06-13 更新：这条决策禁止的是盲目追第 8 个 bug，不禁止已经完成
project-level P2P-broad、retained oracle 和 candidate revalidation 的受控
admission。`bugsinpy_youtube-dl_7` 和 `bugsinpy_youtube-dl_6` 已按该标准
纳入，当前主 cohort 为 9 bugs / 5 projects。

当前不批准：

- 将 native/editable build 作为主扩量路线；
- 为凑主实验数量降级到 task-file P2P；
- 在 protocol 未冻结前直接迁移到外部 benchmark/source。

新增 tracked protocol 入口：

- `docs/protocol/evidence_visibility_protocol.md`；
- `docs/experiments/evp7_protocol_pilot.md`；
- `data/tasks/evp7_tasks.jsonl`；
- `data/patches/evp7_candidates.jsonl`；
- `data/patches/evp7_candidate_summary.json`；
- `data/evidence/evp7_evidence_packets.jsonl`；
- `data/evidence/evp7_evidence_packet_summary.json`；
- `data/reviews/evp7_merge_gate_schema_dry_run.jsonl`；
- `data/reviews/evp7_merge_gate_schema_dry_run_summary.json`；
- `data/reviews/evp7_schema_dry_run_metrics.json`；
- `data/reviews/evp7_g5_llm_prompt_manifest.jsonl`；
- `data/reviews/evp7_g5_llm_run_readiness.json`；
- `data/reviews/evp7_g5_llm_preflight_example.json`；
- `data/reviews/evp7_g5_llm_preflight_strict_example.json`；
- `data/reviews/evp7_g5_workflow_check_only_example.json`；
- `data/reviews/evp7_g5_workflow_mock_reviews.jsonl`；
- `data/reviews/evp7_g5_workflow_mock_metrics.json`；
- `data/reviews/evp7_g5_workflow_mock_summary.json`；
- `data/reviews/evp7_g5_local_config_dry_run.json`；
- `docs/experiments/evp7_g5_metric_scaffold.md`；
- `docs/experiments/evp7_g5_llm_run_readiness.md`；
- `docs/experiments/evp7_g5_execution_confirmation_packet.md`；
- `data/exclusions/blocked_bugsinpy_projects.jsonl`；
- `scripts/build_evp7_protocol_manifests.py`；
- `scripts/build_evp7_candidate_manifest.py`；
- `scripts/build_evp7_evidence_packets.py`。

Phase A 已补齐 EVP-7 candidate-level schema：

1. 已从已有 validated candidate outputs 生成
   `data/patches/evp7_candidates.jsonl`，共 46 条候选；
2. 其中 9 条为 `correct_reference`，41 条为 issue-not-fixed negatives；
3. registry 中候选计数仍只能作为 44 条的下界，因为 `httpie_5` 缺少
   candidate count 字段；
4. 已生成 leakage-audited E0/E2/E4/E6 evidence packet records，共 200 条；
5. 已新增 independent visible-test outcome source 和 deterministic visible
   tool summary source；E4/E6 当前均为 50/50 complete；
6. G1 packet completeness 和 G2 leakage audit 当前均通过；3 条 visible
   `error` outcome 是 candidate-induced import failure，不是缺失证据；
7. G3 tool-only baseline readiness 当前通过：apply-only、visible-tests、
   visible-tool-summary 三组 baseline 共生成 150 条 schema-valid decisions；
8. G4 merge-gate schema stability 当前通过：200 条 E0/E2/E4/E6 dry-run
   outputs 全部可解析为 accept/reject/escalate JSON schema，invalid parse
   count = 0，leakage findings = 0；
9. 这些 G4 records 是 no-API parser/schema dry-run，不是 LLM verifier
   结果，不能支持模型效果结论；
10. G5 metric scaffold 当前通过：FAR、accepted precision、correct recall、
   escalation、FACR 和 Evidence Gain 的计算链路可复现；schema dry-run 和
   mock workflow 仍标记为 `requires_real_llm_verifier_outputs`；
11. 真实 LLM verifier 的 G5 prompt manifest 和 readiness summary 当前通过
   no-API 检查：232 条 prompts、四层各 58 条、leakage failed count = 0、
   prompt text 不写入 tracked manifest；
12. G5 API example config 和 preflight 当前通过结构检查；tracked example
   仍保持 strict API readiness false，只允许 ignored local config 执行真实
   API；
13. G5 guarded workflow 当前支持 check-only、mock validation 和 bounded
   concurrency；mock records 只验证 parser/metrics pipeline；
14. 用户确认 DeepSeek V4 后，已完成 fresh 232-packet 真实 DeepSeek official
    G5 full run：232 条 E0/E2/E4/E6 review，concurrency = 6；
15. full run 质量审计：初次 full run 有 2 条空响应；按同一
    prompt/config/model 重试后，repaired output 为 232/232 parse-valid，
    invalid-output rate = 0.0；原始响应保留在 ignored `outputs/`，tracked
    summary 不包含 raw model responses；
16. EVP-7 pilot-level metric variation 已观察到；metrics scaffold 记录
    `g5_signal_claim_status = real_llm_verifier_signal_observed_on_evp7`。E4/E6
    相对 E0 的 Evidence Gain 分别为 10.0 和 7.25，false accept rate 均为 0，
    accepted precision 均为 1.0，E4 correct recall = 0.272727，E6 correct
    recall = 0.090909；
17. 该结果支持 11-task / 58-candidate / 232-packet EVP-7 bounded pilot
    observations，不支持直接 scale-generalized paper claims；下一步应继续
    controlled expansion，同时保留成本字段缺失和 LLM 不优于 deterministic
    visible-test tool-only baseline 的质量边界。
18. 已完成 232-run quality audit：
    `docs/experiments/evp7_g5_full_run_quality_audit.md` 和
    `data/reviews/evp7_g5_full_run_quality_audit.json`；结论是
   `passed_with_limitations`，明确不支持“LLM 超过 deterministic
   visible-test tool-only baseline”、不支持已知
   DeepSeek 真实计费成本、不支持规模泛化；
19. 已生成 controlled expansion readiness summary：
    `docs/experiments/evp7_expansion_readiness.md` 和
    `data/tasks/evp7_expansion_readiness.json`；下一步应按 project-diverse
    bounded probe 推进，不做盲目 BugsInPy 批量扩展。
20. `bugsinpy_youtube-dl_5` admission 后的 10-task / 54-candidate /
    216-packet DeepSeek G5 run 现在是历史结果。
21. `bugsinpy_youtube-dl_2` admission 后，当前 structural/no-API artifacts
    和真实 DeepSeek G5 结果均已覆盖 11 tasks / 58 candidates / 232 packets。
