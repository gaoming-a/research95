# 当前项目状态与文件地图

日期：2026-06-20

本文件是短入口，用来整理当前计划文档和项目文件。它不替代
`docs/plans/current_plan_zh.md` 的逐轮执行日志，也不替代
`docs/plans/final_paper_roadmap_zh.md` 的研究路线。

## 当前同步状态

- 分支：`main`
- 远端：`origin/main`
- 当前 Git 状态：以 `git status --short --branch` 和
  `git log -1 --oneline` 为准。2026-06-20 最近检查为本地 `main` clean，
  且有未推送的 plan-only 提交。
- 当前远端已同步锚点：
  - `1d235ee Sync EVP-8 smoke packet guards`：远端已包含 G0 guard、G4
    synthesis scaffold 和 smoke execution packet guard-sync。
- 当前本地未推送语义锚点以 `git log -1 --oneline` 为准；语义上是
  `Plan EVP-8 staged follow-up gates`，写入 smoke 之后的 G5-G9 staged path，
  包括 first-batch full-run packet、DeepSeek/Qwen 686-call full run、
  later-model packet、five-model synthesis 和 paper/artifact freeze。
- GitHub sync 边界：此前出现过 GitHub network-level connection failure；用户已允许
  在连续同步失败时跳过 GitHub 并继续本地计划执行。最近针对
  `Plan EVP-8 staged follow-up gates` 的 push 两次失败在 network-level
  connection，因此该 ahead 状态不应解读为实验未完成或工作区脏状态。
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

1. EVP-8 期刊版 full-ladder protocol：
   - 当前用户意图：将现有 bounded EVP-7 pilot 升级为期刊版；
   - canonical 执行计划：
     `docs/experiments/evp8_journal_scale_execution_plan_20260620.md`；
   - 当前机器可审计协议：
     `data/protocols/evp8_protocol_v0_1.json`，由
     `python scripts\audit_evp8_protocol_spec.py --check` 检查；
   - 当前 Phase 0 smoke candidate set：
     `data/protocols/evp8_candidate_set_v0_1.json`，从 tracked EVP-7
     structural cohort 冻结为 21 tasks / 6 projects / 98 candidates；
   - 当前 EVP-8 prompt template：
     `prompts/evp8_visible_evidence_merge_gate_v0_1.md`，由
     `python scripts\build_evp8_prompt_manifest.py --check` 生成 manifest 和
     boundary audit；
   - 当前 packet/schema dry-run：
     `python scripts\build_evp8_packet_schema_dry_run.py --check` 已生成
     686 planned packet skeletons 和 686 schema-valid dry-run outputs 的
     tracked summaries；
   - 当前 cost/baseline dry-run：
     `python scripts\build_evp8_cost_baseline_dry_run.py --check` 已生成
     686 planned calls per model 的 cost-observability summary，以及 686 条
     schema-valid deterministic baseline placeholder decisions 的 summary；
   - 当前审计状态：protocol spec audit passed，所有 Phase 0 dry-run blocker 已
     移除，`phase0_api_readiness = ready_for_api_preflight`；这仍不是 API
     执行授权；
   - 当前 DeepSeek/Qwen local preflight：
     `python scripts\preflight_evp8_deepseek_qwen.py --config configs\evp8_deepseek_qwen.local.json --strict-api-ready`
     已通过；tracked summary 只记录 key presence，不包含 key value；
   - 当前 EVP-8 smoke runner check-only：
     `python scripts\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\evp8_deepseek_qwen.local.json`
     已通过，覆盖 project-frequency-stratified 5 candidates x 7 levels =
     35 packets，并包含主导项目 youtube-dl；
   - 当前 EVP-8 smoke execution packet：
     `python scripts\write_evp8_smoke_execution_packet.py --check` 已通过，
     packet status 为 `ready`，但 `execution_authorized_by_packet=false`；
   - 当前 EVP-8 post-smoke audit scaffold：
     `python scripts\audit_evp8_smoke_results.py --check` 已通过，当前状态为
     `waiting_for_execution`，不读取 raw outputs；
   - 当前 EVP-8 G4 smoke synthesis scaffold：
     `python scripts\summarize_evp8_smoke_synthesis.py --check` 已通过，当前
     状态为 `waiting_for_execution`，只读取 tracked audit/summary fields；
   - 当前 EVP-8 G0 one-command guard：
     `python scripts\check_evp8_deepseek_qwen_g0.py --check` 已通过；该 guard
     汇总 protocol audit、strict preflight、smoke check-only、execution packet、
     post-smoke audit self-test/check、expected-output absence 和 ignored
     boundary；
   - 当前 expected-output absence guard 已通过：DeepSeek/Qwen 预期
     raw-response paths 和 tracked-summary paths 均不存在，避免真实 API 执行前
     才发现 stale outputs；
   - 下一步不是自动 API，而是等待用户明确执行 EVP-8 DeepSeek/Qwen smoke；建议
     使用明确语句：`按当前计划执行 EVP-8 Phase 1 DeepSeek/Qwen smoke`；
   - 第一批模型只允许在 no-API gates 和 smoke gates 通过后执行
     DeepSeek V4 Pro + Qwen3.7 Max；
   - 后续补跑 Kimi K2.6、Devstral 2、Gemini 2.5 Flash 必须使用同一 frozen
     packets/prompts/schema，不能边跑边改协议；
   - smoke 之后的后续顺序已经写入 canonical EVP-8 plan：
     two-model smoke synthesis -> 独立 no-API full-run packet -> DeepSeek
     686-call full run -> DeepSeek audit -> Qwen 686-call full run -> Qwen
     audit -> two-model first-batch synthesis -> later-model execution packet
     -> Kimi/Devstral/Gemini 补跑 -> five-model synthesis -> paper/artifact
     freeze；
   - 边界：不把 EVP-7 的 E2/E4/E6 直接当作 EVP-8 full-ladder 中间层，不从
     DeepSeek+Qwen interim result 写成最终五模型结论。
2. 论文工作量呈现强化：
   - 默认优先，无 API；
   - 目标：把 cohort construction、candidate construction、F2P/P2P
     validation、evidence packets、LLM verifier、tool-only baseline、
     qualitative cases、claim traceability 和 artifact audit 写成清晰的论文
     工作量闭环；
   - 边界：不补 E1/E3/E5，不扩 bug，不改当前 four-anchor claim。
3. 第二模型关键层级/关键锚点复现：
   - 条件执行，必须先确认 provider、model、预算、scope 和停止条件；
   - “关键层级”只指当前 four-anchor pilot 中的 `E0`、`E4`、`E6`
     key anchors，用于检查 DeepSeek G5 趋势是否跨模型稳定；
   - 边界：不补 E1/E3/E5，不证明第二模型优于 tool-only baseline，不替代
     当前 376-record DeepSeek G5 主结果。
4. 扩 EVP-7 cohort：
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
5. 新 verifier design：
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
- `data/protocols/evp8_protocol_v0_1.json`：
  EVP-8 v0.1 七层 evidence ladder 的 tracked machine spec。
- `data/protocols/evp8_protocol_v0_1_audit_summary.json`：
  EVP-8 protocol spec 的 no-API 审计摘要；当前进入
  `ready_for_api_preflight`，但仍不授权真实 API 执行。
- `data/protocols/evp8_candidate_set_v0_1.json`、
  `data/protocols/evp8_candidate_set_v0_1_summary.json`：
  EVP-8 Phase 0 smoke/protocol-validation candidate set；当前为 21 tasks /
  6 projects / 98 candidates，不是最终期刊规模 full-run cohort。
- `prompts/evp8_visible_evidence_merge_gate_v0_1.md`、
  `data/protocols/evp8_prompt_manifest_v0_1.json`、
  `data/protocols/evp8_prompt_boundary_audit_v0_1.json`：
  EVP-8 prompt template、manifest 和 boundary audit；只冻结模板，不包含真实
  rendered packet prompts。
- `data/protocols/evp8_evidence_packet_dry_run_summary_v0_1.json`、
  `data/protocols/evp8_schema_dry_run_summary_v0_1.json`：
  EVP-8 packet/schema dry-run summaries；验证 686 planned skeletons 和 schema
  outputs，不生成完整 evidence packet JSONL。
- `data/protocols/evp8_cost_observability_dry_run_v0_1.json`、
  `data/protocols/evp8_deterministic_tool_baseline_dry_run_v0_1.json`：
  EVP-8 cost-observability 和 deterministic-baseline dry-run summaries；验证
  planned call accounting 和 schema，不读取 local config、不调用 API。
- `configs/evp8_deepseek_qwen.example.json`：
  EVP-8 DeepSeek/Qwen local preflight 的 tracked no-secret example config。
- `data/protocols/evp8_deepseek_qwen_local_config_plan_v0_1.json`、
  `data/protocols/evp8_deepseek_qwen_preflight_summary_v0_1.json`：
  EVP-8 DeepSeek/Qwen local config plan 和 preflight summary；只记录 local config
  boundary、key presence、planned call counts 和 no-API 状态。
- `data/protocols/evp8_deepseek_qwen_smoke_check_only_v0_1.json`：
  EVP-8 DeepSeek/Qwen smoke runner check-only summary；记录 35-packet smoke
  gate、prompt hash counts、schema status 和 no-API/no-raw-output 状态。
- `data/protocols/evp8_deepseek_qwen_smoke_execution_packet_v0_1.json`、
  `docs/experiments/evp8_deepseek_qwen_smoke_execution_packet_v0_1.md`：
  EVP-8 DeepSeek/Qwen smoke no-API execution packet；记录 guard commands、
  future execute commands、expected output paths、stop gates 和非授权边界。当前
  guard commands 已包含 G0 one-command guard、execution packet self-check、
  post-smoke audit check 和 G4 synthesis self-test/check。
- `data/protocols/evp8_deepseek_qwen_smoke_result_audit_v0_1.json`、
  `docs/experiments/evp8_deepseek_qwen_smoke_result_audit_v0_1.md`：
  EVP-8 DeepSeek/Qwen post-smoke audit scaffold；当前等待真实执行，未来审计
  tracked summaries、执行顺序、parse/cost gates、per-evidence-level
  decision/count aggregates 和 raw-output ignored boundary。
- `data/protocols/evp8_deepseek_qwen_smoke_synthesis_v0_1.json`、
  `docs/experiments/evp8_deepseek_qwen_smoke_synthesis_v0_1.md`：
  EVP-8 DeepSeek/Qwen G4 smoke synthesis scaffold；当前等待真实执行，未来只从
  tracked audit/summary fields 汇总 two-model per-level decision patterns。
- `scripts/audit_evp8_protocol_spec.py`：
  检查 EVP-8 相邻差分、visible/hidden 字段边界、模型批次、routing policy、
  cost observability 和 stop gates。
- `scripts/build_evp8_candidate_set_manifest.py`：
  从 tracked EVP-7 structural cohort 生成 EVP-8 Phase 0 candidate-set
  manifest，并检查 per-candidate records 不含 evaluator labels。
- `scripts/build_evp8_prompt_manifest.py`：
  审计 frozen EVP-8 prompt template，生成 no-API prompt manifest 和 boundary
  audit。
- `scripts/build_evp8_packet_schema_dry_run.py`：
  在内存验证 EVP-8 planned packet skeletons 和 output schema，生成 summary-only
  dry-run artifacts。
- `scripts/build_evp8_cost_baseline_dry_run.py`：
  在内存验证 EVP-8 planned usage/cost accounting 和 deterministic baseline
  output schema，生成 summary-only dry-run artifacts。
- `scripts/create_evp8_deepseek_qwen_local_config.py`、
  `scripts/preflight_evp8_deepseek_qwen.py`：
  创建 ignored EVP-8 DeepSeek/Qwen local config，并执行 no-API strict preflight。
- `scripts/run_evp8_deepseek_qwen_smoke.py`：
  guarded EVP-8 DeepSeek/Qwen smoke runner；check-only 不调用 API，真实执行必须
  使用 ignored local config、strict preflight、显式 `--execute` 和单个
  configured `--model-id`；executed tracked summary 必须保留 raw-output-free
  per-level review/parse/decision aggregates，供 G4 synthesis 使用。
- `scripts/write_evp8_smoke_execution_packet.py`：
  从 tracked protocol/preflight/check-only summaries 生成 no-API smoke
  execution packet；`--check` 要求 packet ready 且仍不授权 API。
- `scripts/audit_evp8_smoke_results.py`：
  不读取 raw outputs 的 post-smoke summary audit；当前无真实 smoke summaries
  时输出 `waiting_for_execution`；未来会检查每个 `E0-E6` 的 per-level
  aggregate 是否完整，避免 G4 synthesis 读取 ignored raw responses。
- `scripts/summarize_evp8_smoke_synthesis.py`：
  不读取 raw outputs 的 G4 synthesis scaffold；当前无真实 smoke summaries 时
  输出 `waiting_for_execution`，DeepSeek-only pass 时输出
  `partial_waiting_for_qwen`，双模型均通过后只报告 tracked per-level decision
  counts 和严格 claim boundary。
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
- `docs/experiments/evp8_journal_scale_execution_plan_20260620.md`：
  EVP-8 期刊版后续执行计划；记录 no-API 协议冻结、七层 evidence ladder、
  DeepSeek/Qwen 第一批执行和 Kimi/Devstral/Gemini 后续补跑边界。
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
