# 导师/答辩工作量说明：EVP-7 当前论文包

日期：2026-06-18

本文档用于向导师、答辩老师或后续接手的 AI 说明：当前论文不是只跑了几组
prompt，而是完成了一个 bounded four-anchor candidate patch verification
pipeline。本文档不新增实验结论，不替代 `docs/plans/final_paper_roadmap_zh.md`
和 `docs/paper/ieee_submission_draft.tex`。

## 当前可以主张什么

当前论文可以写成：

> 在 20 个真实 bug task、94 个 candidate patch、376 条 E0/E2/E4/E6 真实
> DeepSeek G5 verifier 记录上，证据可见性会改变 LLM 的 merge-gate 决策；
> E4/E6 在本 pilot 中保持 observed false accept rate = 0.0 和 accepted
> precision = 1.0，E6 相比 E0 有更高 correct recall 和 Evidence Gain。

这只能是 bounded EVP-7 pilot claim。它不能写成规模泛化结论，也不能写成 LLM
明确优于 deterministic tool-only baseline。

## 为什么不是“只跑 prompt”

当前工作量包含完整的候选补丁验证闭环：

1. 任务 admission：structural/no-API pipeline 已达到 21 real-bug tasks、
   6 projects。
2. candidate construction：98 candidate patches，包含 21 个 correct
   references、76 个 issue-not-fixed negatives、1 个 regression negative。
3. retained oracle validation：每个 candidate 先经过 F2P retained oracle
   验证，不靠 LLM opinion 当 ground truth。
4. P2P/regression policy：主线任务需要 project-level P2P-broad 或清楚记录的
   bounded policy；`bugsinpy_cookiecutter_4` 这类 blocker 没有被硬塞进主结果。
5. evidence packet construction：生成 392 条 E0/E2/E4/E6 leakage-audited
   evidence packets，四层边界明确。
6. visible/hidden separation：LLM 只看 model-visible evidence；hidden evaluator
   labels、oracle 路径、expected outcome 在评估后才 join。
7. tool-only baselines：294 条 deterministic tool-only decisions，用来判断 LLM
   与工具证据的关系。
8. real LLM verifier run：paper-facing 真实 DeepSeek G5 run 覆盖 20 tasks /
   94 candidates / 376 evidence packets，且 376/376 parse-valid non-mock records。
9. statistics and utility：包含 Wilson intervals、candidate-level bootstrap、
   Evidence Gain、utility sensitivity。
10. qualitative cases：6 个 raw-output-free qualitative cases，用于解释
    evidence visibility 如何改变 accept/reject/escalate。
11. claim-boundary audit：明确支持/不支持的 claim，避免把 pilot 写成过度结论。
12. artifact readiness：IEEE draft、figures、tables、anonymous artifact、handoff
    和 local quality gate 都有可复现脚本与审计。

因此，论文贡献应表述为 hidden-evaluator-free 的 candidate patch verification
实验管线和 evidence visibility pilot，而不是单纯 prompt comparison。

## 当前不能主张什么

以下结论当前不成立，不能写进论文主结论：

- scale-generalized paper claim beyond EVP-7；
- LLM 明确优于 deterministic visible-test 或 visible-tool-summary baseline；
- E6 严格优于 E4；
- runner-estimated cost 等于外部 DeepSeek billing statement；
- 当前四层 E0/E2/E4/E6 是完整 adjacent-difference E0-E6 ladder；
- 可以直接补 E1/E3/E5 到现有 artifacts 中。

如果未来要研究 E1/E3/E5，必须新开 EVP-8 或 EVP-7-v2，从 E0 开始重新定义
每一层新增证据，重新生成 packets、prompts、baselines、LLM runs、statistics
和 figures。

## 回应“工作量不够”的短答

可以这样回应：

> 当前结果规模不是大 benchmark，但工作量不是单纯模型调用。我们完成了真实
> bug task admission、candidate patch 构造、retained oracle validation、
> P2P/regression policy、visible/hidden 分离、392 条 leakage-audited evidence
> packets、294 条 deterministic baselines、376 条真实 LLM verifier records、
> 统计区间、utility sensitivity、qualitative cases、claim-boundary audit 和
> anonymous artifact packaging。当前论文应按 bounded empirical pilot 投稿；
> 如果要增强稳健性，下一步应做用户确认的第二模型 E0/E4/E6 key-anchor
> replication，而不是临时插入 E1/E3/E5 或盲目扩 bug。

## 下一步选择

默认无新决策时，继续 Option A：

- polish 当前 four-anchor paper package；
- 保持 bounded claim；
- 重建 PDF / artifact / audits；
- 准备投稿或给导师复核。

如果导师明确要求更多实验，优先选择：

1. second-model E0/E4/E6 key-anchor replication，先确认 provider/model/预算；
2. 新 30-50 bug boundary，先确认是否允许外部 benchmark 或 native/editable build；
3. 新 verifier design，先确认是否修 prompt-only negative result。

这些都不能从普通 `continue` 自动推断。
