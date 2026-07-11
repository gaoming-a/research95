# DSA v0.2 材料构造协议作者签核清单

日期：2026-07-11
状态：`UNSIGNED / V2-P1_NOT_AUTHORIZED / NO_API`

该签核只授权后续 Goal 冻结 V2-P1 的材料构造协议，不授权运行 task/test/container，
不授权进入 V2-P2，不授权修改 prompt，不授权模型 API。

作者需独立核验并明确接受以下 8 项：

1. `central_question`：核心实验是 C0--C3 如何改变固定 reviewer agent 的
   `accept/reject/escalate` 回复，而不是完整复现 BugsInPy。
2. `agent_boundary`：reviewer agent 是固定 endpoint + 中性 prompt + JSON schema，
   无自主工具；tool-using agent 是另一项研究。
3. `preconfirmatory_materialization`：候选环境与行为资格验证发生在最终 cohort/P3
   冻结前，但必须遵守 outcome 前已冻结的通用构造规则。
4. `source_and_exclusion`：task order 用 hash 机械确定；v0.1 五个 P4-active tasks
   只作 development evidence，不进入 v0.2 确认性 cohort。
5. `environment_policy`：使用 outcome 前冻结的 project-level recipe，不强制复制腐化
   official setup；不得在单个 task 失败后作 task-specific 依赖或兼容修补。
6. `candidate_qualification`：positive 全 checks 两次通过；negative 必须 basic/visible
   两次通过且 independent hidden 至少一项两次失败；不能用语法错误或 visible-fail。
7. `cohort_and_stop`：只冻结机械顺序中前 30 个完整 pairs；source frame 先耗尽则在
   任何模型调用前停止。
8. `freeze_and_responsibility`：最终 cohort、prompt、模型 route、统计和运行规则仍需
   V2-P3 的独立作者签核；作者核验所有结果、遵守最终 AI 政策并承担科学责任。

建议作者后续使用的完整签核文本：

> 我作为作者【高明】签核 DSA v0.2 V2-P1 材料构造协议的全部 8 项；我已审查核心问题、
> reviewer-agent 边界、pre-confirmatory materialization、source/exclusion、project-level
> environment policy、candidate qualification、30-pair/stop rule 和后续独立冻结责任。
> 我理解该签核只授权后续 Goal 冻结 V2-P1 规则，不授权运行 task/test/container，
> 不授权进入 V2-P2，不授权修改 prompt 或调用模型 API。
