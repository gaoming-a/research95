# 当前项目状态与文件地图

日期：2026-06-18

本文件是短入口，用来整理当前计划文档和项目文件。它不替代
`docs/plans/current_plan_zh.md` 的逐轮执行日志，也不替代
`docs/plans/final_paper_roadmap_zh.md` 的研究路线。

## 当前同步状态

- 分支：`main`
- 远端：`origin/main`
- 当前 Git 状态：以 `git status --short --branch` 为准。2026-06-18 最近几轮
  检查均为本地 `main` clean 且 ahead `origin/main`；精确 ahead 数会随本地
  文档维护提交增加，不应写成长期 truth。
- 最近本地 no-API 维护提交包括
  `6423ecf Record no-API submission maintenance` 和
  `1766932 Refresh short project state`；前者记录 paper/package rebuild、
  readiness、artifact 和 local quality 验证，后者刷新短状态入口。
- GitHub sync 边界：此前 push 频繁失败，用户已允许在同步失败时跳过 GitHub
  并继续本地计划执行；因此本地 `main` ahead `origin/main` 是已知同步状态，
  不应解读为未完成实验或未提交工作。
- `bugsinpy_cookiecutter_4` 已收束为 tracked blocker policy；完整 builder
  失败输出仍是本地诊断残留，不应提交。
- ignored 本地交付物：
  - `outputs/`
  - `artifacts/`
  - `.env`
  - `configs/*.local.json`

## 当前研究状态

- 当前主张：bounded EVP-7 evidence-visibility pilot claim。
- 当前实验边界：
  - structural cohort：21 real-bug tasks；
  - structural candidate manifest：98 patch candidates；
  - no-API evidence packets：392 E0/E2/E4/E6 records；
  - real DeepSeek G5 verifier run：仍限定在旧 20-task / 94-candidate /
    376-packet cohort；
  - raw-output-free tracked summaries and audits。
- 当前 evidence-level 边界：EVP-7 是 E0/E2/E4/E6 four-anchor pilot，不是
  完整 E0-E6 adjacent-difference ladder；E1/E3/E5 不应补插进当前 artifacts，
  只能在未来 EVP-8 / EVP-7-v2 新协议中整体重做。
- 当前 paper-facing 结果：
  - `docs/paper/ieee_submission_draft.tex`
  - `docs/paper/patch_verification_draft.md`
  - `docs/paper/generated_tables.md`
  - `docs/paper/generated_tables.tex`
  - `docs/artifact/submission_checklist.md`
  - `docs/artifact/submission_handoff_20260618.md`
- 当前 known non-blocker：
  - old prompt-only evidence-first gate remains `stop_or_redesign`；
  - this blocks prompt-only positive claims, not the current bounded EVP-7 claim。

## 继续实验前的决策门

如果继续实验，不应直接扩量或直接调用 API。必须先选择一个目标：

当前 no-API 下一步决策包：

- `docs/experiments/evp7_next_decision_packet_20260618.md`

1. 论文工作量呈现强化：
   - 默认优先，无 API；
   - 目标：把 cohort construction、candidate construction、F2P/P2P
     validation、evidence packets、LLM verifier、tool-only baseline、
     qualitative cases、claim traceability 和 artifact audit 写成清晰的论文
     工作量闭环；
   - 边界：不补 E1/E3/E5，不扩 bug，不改当前 four-anchor claim。
2. 第二模型关键锚点复现：
   - 条件执行，必须先确认 provider、model、预算、scope 和停止条件；
   - 默认只覆盖 `E0`、`E4`、`E6`，用于检查 DeepSeek G5 趋势是否跨模型
     稳定；
   - 边界：不补 E1/E3/E5，不证明第二模型优于 tool-only baseline，不替代
     当前 376-record DeepSeek G5 主结果。
3. 扩 EVP-7 cohort：
   - 当前状态：本轮已完成 `bugsinpy_thefuck_1` admission；后续
     `bugsinpy_cookiecutter_4` P2P 构造被记录为 dependency/command/timeout
     blocker，未 admission；
   - 当前结果：21 tasks / 98 candidates / 392 no-API evidence packets；
   - 当前 gate：`docs/experiments/evp7_expansion_readiness.md` 已刷新为
     21 tasks / 98 candidates；
   - `bugsinpy_thefuck_1` 的 admission scope 是
     `thefuck_rules_root_pip_p2p_v1`：`tests/rules` + `pip` source-token
     filter，不能写成 full-project coverage；
   - 当前 metadata-promising pool 没有 fresh-project candidates outside
     already-main or already-risky projects；
   - 下一步不是继续盲目扩 cohort，而是决定是否做新的 30-50 bug 边界、
     跨模型复现实验，或论文结果同步。
4. 新 verifier design：
   - 目标：重新设计旧 prompt-only evidence-first 失败路线；
   - 下一步：先做 redesign dry-run 和 prompt-boundary check；
   - 禁止按旧 `patch_verify_evidence_first_v1` prompt 继续扩量。

## 计划文档分工

- `docs/plans/current_project_state_zh.md`：
  当前短入口和文件地图。
- `docs/plans/current_plan_zh.md`：
  严格逐轮执行日志。任何实验、API、数据、论文、Git 同步动作前都要更新。
- `docs/plans/final_paper_roadmap_zh.md`：
  canonical final-paper route 和研究路线。继续实验前应先检查这里的约束。
- `docs/plans/current_plan.md`：
  英文 companion handoff，不是主要执行日志。
- `docs/plans/agent_execution_plan_zh.md`、
  `docs/plans/ai_agent_experiment_execution_plan_zh.md`：
  历史执行计划，只保留溯源，不应覆盖当前路线。

## 项目文件地图

- `README.md`：
  项目总入口、当前状态、常用命令。
- `docs/INDEX.md`：
  全项目文档和脚本索引。
- `docs/protocol/evidence_visibility_protocol.md`：
  当前 EVP-7 protocol 和 evidence visibility boundary。
- `docs/experiments/evp7_protocol_pilot.md`：
  当前 protocol pilot 报告；真实 G5 结果仍是 20-task / 94-candidate /
  376-packet，structural no-API cohort 已扩到 21 / 98 / 392。
- `docs/experiments/thefuck1_candidate_validation.md`：
  `bugsinpy_thefuck_1` rules-root pip-family P2P policy、candidate validation
  和 admission 记录。
- `docs/experiments/evp7_g5_llm_376_full_result.md`：
  376-record real G5 run result。
- `docs/experiments/evp7_g5_376_full_quality_audit.md`：
  G5 quality audit and limitations。
- `docs/experiments/evp7_g5_376_claim_traceability.md`：
  paper claim traceability audit。
- `docs/experiments/evp7_g5_376_tool_attribution.md`：
  deterministic tool-only attribution boundary。
- `docs/experiments/evp7_g5_376_qualitative_cases.md`：
  qualitative decision-case interpretation。
- `docs/paper/research_definition.md`：
  problem definition、hypotheses、non-goals。
- `docs/paper/patch_verification_outline.md`：
  current paper outline。
- `docs/paper/patch_verification_draft.md`：
  Markdown paper draft；当前包含 `Workload at a Glance`，把
  21/98/392 structural pipeline 与 20/94/376 real G5 run 分开呈现。
- `docs/paper/generated_tables.md`、`docs/paper/generated_tables.tex`：
  script-generated paper tables；当前包含 EVP-7 workload ledger。
- `docs/paper/ieee_submission_draft.tex`：
  current IEEEtran submission draft；当前包含 `Workload at a Glance` 章节和
  `tab:evp7-workload-ledger`。
- `docs/paper/advisor_workload_response_zh.md`：
  中文导师/答辩工作量说明；集中回答当前工作量、bounded claim、不能写的
  overclaim，以及为什么当前论文不是单纯 prompt comparison。
- `docs/artifact/submission_freeze_candidate_20260618.md`：
  no-API freeze-candidate packet；记录当前 paper/artifact candidate 状态和
  仍需用户确认的 target venue、format、final freeze、Git sync 边界。
- `docs/figures/`：
  reproducible PDF/SVG/PNG paper figures。当前 draft 使用 fig1-fig7。
- `docs/artifact/anonymous_artifact.md`：
  anonymous artifact inclusion/exclusion policy。
- `docs/artifact/submission_checklist.md`：
  final submission checklist and package readiness criteria。
- `docs/experience/engineering_notes.md`：
  bug/repair经验记录，后续遇到同类问题先查这里。

## 脚本入口地图

- `scripts/audit_paper_readiness.py`：
  paper framing、protocol state、EVP-7 bounded-claim readiness。
- `scripts/audit_submission_freeze_candidate.py`：
  no-API freeze-candidate semantic boundary audit；防止 candidate packet 漂移为
  final freeze、API 授权、扩量授权或 E1/E3/E5 插入。
- `scripts/audit_paper_claim_boundary.py`：
  supported/unsupported claim traceability。
- `scripts/write_paper_tables.py`：
  paper-ready Markdown/LaTeX tables；当前也生成 EVP-7 workload ledger。
- `scripts/write_ieee_latex_draft.py`：
  IEEEtran draft generator；当前把 workload ledger 作为论文前段 reader bridge。
- `scripts/generate_paper_figures.py`：
  reproducible figure generation。
- `scripts/prepare_anonymous_artifact.py`：
  ignored anonymous ZIP builder。
- `scripts/audit_anonymous_artifact.py`：
  ZIP structure and exclusion audit。
- `scripts/write_git_sync_packet.py`：
  Git sync handoff packet with ahead/behind visibility。
- `scripts/audit_git_sync_packet.py`：
  Git sync packet safety audit。
- `scripts/write_pre_api_handoff.py`：
  one-command local handoff refresh。
- `scripts/run_local_quality_gate.py`：
  local no-API quality gate。

## 禁止误用

- 不提交 `outputs/`、`artifacts/`、`.env`、`configs/*.local.json`、benchmark
  checkouts 或 raw model responses。
- 不把 dry-run/mock/schema records 当成 real LLM verifier result。
- 不把 old prompt-only gate 的失败路线写成正向 claim。
- 不把 `tool_augmented_evidence` 用来修补 prompt-only evidence-first 结论。
- 不在没有新实验目标和 preflight 的情况下继续 API 扩量。
