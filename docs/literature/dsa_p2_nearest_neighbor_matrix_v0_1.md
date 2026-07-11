# DSA 2026 P2 Nearest-Neighbor Literature Matrix v0.1

检索日期：2026-07-11；时间窗：2018--2026。

## 定位结论

没有发现同时满足以下全部条件的直接设计：同一真实补丁、C0--C3 累积真实可执行证据、固定 LLM、
accept/reject/escalate 三分类、task-level paired effect。最接近的是 LLM4PatchCorrect、PatchZero、
SWE-PRBench、CodeJudgeBench 和 requirement-conformance review；它们必须在 Related Work 中正面区分。

允许的定位是 `controlled finite-cohort evidence-conditioned patch-gating study`。禁止写 first、unique、SOTA、
autonomous correctness verification 或 LLM superiority。

## 最近邻矩阵

| 工作 | 任务 | 输入/证据 | 输出 | 重叠 | 支撑等级 | 与本研究的关键差异 |
|---|---|---|---|---|---|---|
| [Annotation reliability](https://doi.org/10.1109/icse.2019.00064) | compare independent-test and author correctness labels | professional-developer gold labels and independent test suites | label reliability | foundation | strong support | supports the hidden-evaluator boundary but does not evaluate LLM review |
| [BugsInPy](https://doi.org/10.1145/3368089.3417943) | Python real-bug benchmark | buggy/fixed commits and bug-revealing tests | controlled testing/debugging dataset | foundation | strong support | dataset source, not a patch-review method |
| [RGT at scale](https://doi.org/10.1007/s10664-020-09920-w) | assess overfitting patches with generated tests | random tests derived from the human patch as oracle | overfitting assessment | foundation | background support | establishes independent-test labeling rather than LLM evidence-conditioned decisions |
| [Shibboleth](https://doi.org/10.1145/3533767.3534368) | static/dynamic APCA ranking and classification | production-code similarity and passing-test coverage impact | ranking and binary correctness class | medium | partial support | not an LLM evidence-visibility intervention and not a triage policy study |
| [PatchZero](https://arxiv.org/abs/2303.00202) | zero-shot APCA for unseen repair tools | code-model representation plus semantically similar labeled patches | binary correctness prediction | high | partial support | static transfer/classification setting rather than within-patch executable-evidence intervention |
| [BugsInPy reproduction](https://doi.org/10.1109/scam59687.2023.00036) | reproduce and repair benchmark environments | original virtualenv and improved Conda/Docker executions | reproducibility results and improved framework | foundation | strong support | directly constrains source feasibility but not the LLM research question |
| [FixCheck](https://doi.org/10.1109/icst60714.2024.00036) | generate fault-revealing tests for suspected incorrect patches | random testing plus LLM-generated tests | new tests exposing patch faults | medium | partial support | uses LLMs to create oracles rather than measuring a fixed reviewer's response to accumulated evidence |
| [LLM4PatchCorrect](https://doi.org/10.1109/tse.2024.3452252) | binary APCA for patches from unseen repair tools | bug description, execution trace, failing tests, coverage, and labeled similar patches | correct/incorrect prediction | high | partial support | does not isolate cumulative real evidence on the same patch and does not study accept/reject/escalate policy |
| [LLM code-review evaluation](https://arxiv.org/abs/2505.20206) | classify and improve HumanEval-style code | code with or without problem descriptions | correct/incorrect classification and suggested repair | medium | partial support | problem-description ablation on function tasks, not real patches or executable evidence levels |
| [Requirement-conformance review](https://doi.org/10.1007/s10515-026-00638-5) | LLM judgment of code against natural-language requirements | prompt variants and executable counterfactual verification filter | binary conformance judgment and overcorrection analysis | high | partial support | tests prompt complexity and a fix-guided filter, not a cumulative executable evidence ladder on real patches |
| [CodeJudgeBench](https://doi.org/10.18653/v1/2026.acl-long.888) | robustness of LLM judges for generation, repair, and unit tests | candidate responses and code-specific perturbations | comparative judgment robustness | high | partial support | judge robustness benchmark without real executable C0-C3 evidence accumulation or merge triage |
| [SWE-PRBench](https://arxiv.org/abs/2603.26130) | detect issues matching human pull-request feedback | diff, file content, or full structured context | issue-detection quality | high | partial support | context-volume ablation without a pass/fail test oracle or accept/reject/escalate patch gate |

## Gate

- exact design match found: `false`
- positioning gate passed: `true`
- 每篇均已检查官方摘要或全文页面；Crossref 只用于元数据，不单独作为内容支撑。
- 三个 arXiv DOI 的 Crossref 404 已从 arXiv 官方页面恢复，并保留在 search log。
