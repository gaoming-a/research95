# 当前项目状态与文件地图

日期：2026-06-22

本文件是短入口，用来整理当前计划文档和项目文件。它不替代
`docs/plans/current_plan_zh.md` 的逐轮执行日志，也不替代
`docs/plans/final_paper_roadmap_zh.md` 的研究路线。

## 当前同步状态

- 分支：`main`
- 远端：`origin/main`
- 当前 Git 状态：以 `git status --short --branch` 和
  `git log -1 --oneline` 为准。不要只依赖本文件里记录的 hash 判断是否 ahead；
  本轮语义上要求远端至少包含 EVP-8 Qwen G6 result state、G7
  later-model completion packet、G7.1 later-model runner/preflight 和 G7.2
  OpenRouter strict preflight readiness；G7.3 scaffold 是否同步以最新
  `git status` 和远端 log 为准。
- 当前本地 ahead 状态：
  - 本轮 post-push inspection 显示 `git status --short --branch` 为
    `main...origin/main`；
  - 远端已包含 Kimi reasoning-disabled clean-rerun gate、429 resume boundary
    文档和 OpenRouter top-level error retry repair；精确 hash 以
    `git log -1 --oneline` 和远端 log 为准；
  - 当前 Kimi K2.6 reasoning-disabled clean rerun、Devstral 2 full run 和
    Gemini 2.5 Flash full run 均已通过 later-model gate；five-model synthesis
    已通过；`.env` 和 local config 仍 ignored；raw outputs 和 blocked attempts
    仍只在 ignored `outputs/`；最终仍以命令输出和 `git log -1 --oneline`
    为准。
- 当前远端已同步锚点：
  - `7308910 Add EVP-8 Kimi reasoning clean rerun gate`：远端已包含 Kimi
    reasoning-disabled routing policy、OpenRouter request controls、preflight/
    audit/check-only refresh 和 clean rerun gate 文档；
  - `eaecfeb Add EVP-8 later-model audit scaffold`：远端已包含 G7.3
    later-model post-run audit scaffold、five-model synthesis scaffold、G7
    completion packet guard refresh 和 no-API waiting-state artifacts；
  - `8ceeef2 Fix EVP-8 post-push state entry`：远端已包含上一轮
    post-push 状态修正；
  - `40ae224 Record EVP-8 OpenRouter strict preflight`：远端已包含 G7.2
    OpenRouter strict preflight passed、completion packet refresh、no-secret
    docs/state updates；
  - `b2729b9 Record EVP-8 G7.1 sync blocker`：远端已包含上一轮 GitHub
    sync blocker 记录；
  - `ddca89f Add EVP-8 later-model runner preflight`：远端已包含 G7.1
    later-model runner/preflight/check-only scaffold；
  - `79ff382 Prepare EVP-8 later-model packet`：远端已包含 G7 no-API
    later-model completion packet；
  - `6f3c8f0 Sync EVP-8 Qwen G6 result state`：远端已包含 DeepSeek/Qwen
    first-batch full-run passed state 的短状态修正；
  - `d59021e Record EVP-8 Qwen G6 full result`：远端已包含 Qwen 686-call
    first-batch full-run raw-output-free summary、first-batch passed audit/
    synthesis 和本轮计划/索引更新；
  - `d9a8391 Record EVP-8 DeepSeek G6 full result`：远端已包含 DeepSeek
    686-call first-batch full-run raw-output-free summary、post-full-run
    partial audit/synthesis 和本轮计划/索引更新；
  - `72f1fb5 Checkpoint EVP-8 full-run raw responses`：远端已包含 full-run
    raw-response incremental checkpointing and resume-prefix guard；
  - `d79cb1e Authorize EVP-8 DeepSeek G6 full run`：远端已包含 DeepSeek G6
    first-batch full-run 授权记录；
  - `95efbdc Record EVP-8 G6 authorization boundary`：远端已包含 G6 explicit
    authorization boundary re-check；
  - `422f956 Fix EVP-8 post-push state entry`：远端已包含 G5 packet 后的
    post-push 状态修正；
  - `930bc73 Prepare EVP-8 first batch full packet`：远端已包含 G5 no-API
    first-batch full-run packet、full check-only summary、post-full-run audit/
    synthesis scaffolds 和相关计划文档；
  - `1d235ee Sync EVP-8 smoke packet guards`：历史 smoke guard-sync 锚点。
- 当前本地语义锚点以 `git log -1 --oneline` 和本轮提交为准；语义上已完成
  EVP-8 Phase 1 DeepSeek/Qwen smoke closure、G5 no-API first-batch full-run
  packet readiness、DeepSeek G6 full-run checkpointing repair，以及 DeepSeek
  / Qwen 686-call first-batch full-run passed audit and synthesis；G7 no-API
  later-model completion packet 已 ready；G7.1 later-model runner/preflight
  结构验证已通过；G7.2 strict preflight 已在 ignored `.env` 中确认
  `OPENROUTER_API_KEY` presence；G7.3 later-model post-run audit 和
  five-model synthesis scaffold 已通过 waiting-state check；用户已授权后续模型
  API，但首个 Kimi 686-record run 被 later-model gate 正确阻断，原因是
  Kimi 默认 reasoning 导致 79 条 invalid JSON output。OpenRouter top-level
  429 error retry repair 后，Kimi clean rerun 已通过：686/686 parse-valid、
  provider-reported cost 686/686、actual model/provider metadata 686/686。
  Devstral 2 full run 随后也已通过：686/686 parse-valid、
  provider-reported cost 686/686、actual model/provider metadata 686/686。
  Gemini 2.5 Flash full run 也已通过：686/686 parse-valid、
  provider-reported cost 686/686、actual model/provider metadata 686/686。
  当前 later-model audit 和 five-model synthesis 均为 `passed`；允许报告
  frozen EVP-8 v0.1 packet set 上的描述性五模型 per-level decision patterns，
  但仍不支持 LLM superiority over deterministic baseline 或最终
  evidence-level effectiveness claim。成本审计已生成：
  `data/reviews/evp8_cost_accounting_summary.json` 记录 passed-result USD
  excluding Qwen = `2.892118056`、passed Qwen CNY = `41.119548`、ignored Kimi
  blocked attempts USD = `7.27612053`，并设置 `api_freeze=true`。
- GitHub sync 边界：此前出现过 GitHub network-level connection failure；用户已允许
  在连续同步失败时跳过 GitHub 并继续本地计划执行。最近一次已确认
  `git push origin main` 成功；最终是否仍 ahead 仍以
  `git status --short --branch` 和远端 log 为准。
- `bugsinpy_cookiecutter_4` 已收束为 tracked blocker policy；完整 builder
  失败输出仍是本地诊断残留，不应提交。
- ignored 本地交付物：
  - `outputs/`
  - `artifacts/`
  - `.env`
  - `configs/*.local.json`

## 当前研究状态

- 当前主张边界：EVP-7 仍是 bounded four-anchor pilot；EVP-8 现在支持
  frozen v0.1 packet set 上的 descriptive five-model per-level decision
  patterns。当前仍不支持 LLM superiority over deterministic baselines、最终
  evidence-level effectiveness 或跨规模 generalization claim。
- 当前实验边界：
  - structural cohort：21 real-bug tasks；
  - structural candidate manifest：98 patch candidates；
  - no-API evidence packets：392 E0/E2/E4/E6 records；
  - real DeepSeek G5 verifier run：仍限定在旧 20-task / 94-candidate /
    376-packet cohort；
  - EVP-8 DeepSeek G6 first-batch full run：98 candidates x 7 evidence
    levels = 686 records，686/686 parse-valid，raw-output-free summary 已生成；
  - EVP-8 Qwen G6 first-batch full run：98 candidates x 7 evidence levels =
    686 records，686/686 parse-valid，raw-output-free summary 已生成；
  - EVP-8 G7/G7.1 later-model readiness：Kimi K2.6、Devstral 2、Gemini
    2.5 Flash 计划补跑 3 x 686 = 2058 records，OpenRouter public catalog
    audit 当前 `all_available = true`，packet `ready`，runner/preflight
    strict checks 和 full check-only 已通过；`OPENROUTER_API_KEY` presence
    已通过；G7.3 post-run audit/five-model synthesis 当前均为 `passed`；
    Kimi K2.6、Devstral 2 和 Gemini 2.5 Flash 均已 passed；
  - EVP-8 cost accounting：passed-result USD excluding Qwen = `2.892118056`，
    Qwen passed cost = CNY `41.119548`，ignored Kimi blocked attempts =
    USD `7.27612053`；当前 API freeze 为 true；
  - SQJ low-cost submission route：当前首选投稿目标为 Software Quality
    Journal，按 CCF C 类 / 学校 C 类口径作为 D 类及以上候选；投稿前必须先由
    学院/科研秘书确认发表当年 CCF 目录、高风险/预警名单状态和学校认定口径；
    当前成本路线为 non-OA / subscription route，不默认支付 APC；
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
  - `docs/artifact/sqj_submission_checklist.md`
  - `docs/artifact/sqj_final_freeze_readiness.md`
  - `docs/artifact/submission_handoff_20260618.md`
- 当前下一投稿格式：不再以 IEEEtran 作为下一主稿格式；SQJ 路线要求生成
  Springer Nature `sn-jnl` LaTeX draft，并补齐 data availability、competing
  interests、author contribution、funding/acknowledgement 等 submission
  elements。SQJ framing and claim-boundary packet 已写入
  `docs/paper/sqj_submission_framing.md`。首个 generated source draft 已写入
  `docs/paper/sqj_submission_draft.tex`，参考文献文件为
  `docs/paper/sqj_references.bib`；本地 MiKTeX 缺少 `sn-jnl.cls`，因此当前只做
  source-structure gate，不做 PDF compile gate。SQJ-specific source-package
  checklist 已写入 `docs/artifact/sqj_submission_checklist.md`，并由
  `scripts/audit_sqj_submission_checklist.py` 审计；该 checklist 不是 final
  submission freeze。SQJ final-freeze readiness packet 已写入
  `docs/artifact/sqj_final_freeze_readiness.md`，并由
  `scripts/audit_sqj_final_freeze_readiness.py` 审计；该 packet 记录学校认定、
  `sn-jnl.cls`/PDF compile、作者/基金/利益冲突、artifact rebuild 和最终用户授权
  缺口，不授权投稿。SQJ-specific figures 已写入 `docs/figures/sqj/`，当前
  `sqj_submission_draft.tex` 引用三张 EVP-8 主图：protocol、decision
  patterns 和 cost boundary。
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
   - 当前 EVP-8 post-smoke audit：
     `python scripts\audit_evp8_smoke_results.py --check` 已通过，当前状态为
     `passed`，不读取 raw outputs；
   - 当前 EVP-8 G4 smoke synthesis：
     `python scripts\summarize_evp8_smoke_synthesis.py --check` 已通过，当前
     状态为 `passed`，只读取 tracked audit/summary fields；
   - EVP-8 G0 one-command guard：
     `python scripts\check_evp8_deepseek_qwen_g0.py --check` 已通过；该 guard
     汇总 protocol audit、strict preflight、smoke check-only、execution packet、
     post-smoke audit self-test/check、expected-output absence 和 ignored
     boundary。注意：这是 smoke 执行前 guard；现在 smoke outputs 已存在，后续
     不应再用 G0 作为 post-smoke 验收；
   - EVP-8 DeepSeek/Qwen Phase 1 smoke 已执行：两个模型各 35 条 records，
     均为 35/35 parse-valid，post-smoke audit 和 G4 synthesis 均通过；
   - DeepSeek 使用 4096-token output budget 修复 1024-token truncation；
     Qwen official cost 以 CNY token-pricing estimate 记录，不写成 USD bill；
   - 历史 G5 no-API first-batch full-run packet 已 ready：
     `python scripts\write_evp8_first_batch_full_run_packet.py --check`；
   - full-run check-only 已通过，覆盖 98 candidates x 7 levels = 686 packets；
   - DeepSeek G6 first-batch full run 已执行并通过 audit：
     `data/reviews/evp8_deepseek_deepseek-v4-pro_full_summary.json` 记录
     686/686 parse-valid，estimated USD cost `0.788808816`，不含 prompt text
     或 raw response text；
  - Qwen G6 first-batch full run 已执行并通过 audit：
     `data/reviews/evp8_qwen_qwen3.7-max_full_summary.json` 记录 686/686
     parse-valid，estimated CNY cost `41.119548`，不含 prompt text 或 raw
     response text；
   - Kimi K2.6 later-model full run 已执行并通过 later-model audit：
     `data/reviews/evp8_moonshotai_kimi-k2.6_full_summary.json` 记录 686/686
     parse-valid，provider-reported USD cost `1.02450976`，actual model/provider
     metadata 686/686，不含 prompt text 或 raw response text；
   - Devstral 2 later-model full run 已执行并通过 later-model audit：
     `data/reviews/evp8_mistralai_devstral-2512_full_summary.json` 记录
     686/686 parse-valid，provider-reported USD cost `0.44937088`，actual
     model/provider metadata 686/686，不含 prompt text 或 raw response text；
   - Gemini 2.5 Flash later-model full run 已执行并通过 later-model audit：
     `data/reviews/evp8_google_gemini-2.5-flash_full_summary.json` 记录
     686/686 parse-valid，provider-reported USD cost `0.6294286`，actual
     model/provider metadata 686/686，不含 prompt text 或 raw response text；
   - first-batch full-run audit 当前为 `passed`，synthesis 当前为 `passed`，
     二者均不读取 raw outputs；
   - G7 later-model completion packet 已 ready：
     `python scripts\write_evp8_later_model_completion_packet.py --check`；
   - G7.1/G7.2 later-model local config/preflight/check-only 已 passed：
     `python scripts\preflight_evp8_later_models.py --config configs\evp8_later_models.local.json --allow-missing-credentials`；
     `python scripts\run_evp8_later_model_full.py --check-only --run-scope full --config configs\evp8_later_models.local.json --allow-missing-credentials`；
   - 当前 strict API ready 为 true：ignored `.env` 中
     `OPENROUTER_API_KEY` presence 已通过；本轮三 later-model API 已全部完成；
  - 当前 G7.3 post-run audit/synthesis 已通过 passed-state check：
     `python scripts\audit_evp8_later_model_full_results.py --check`；
     `python scripts\summarize_evp8_five_model_synthesis.py --check`；
   - 后续不应继续补模型或改协议；下一步是 paper/table/artifact freeze，
     且必须继续区分 descriptive five-model pattern 和 unsupported superiority/
     final-effectiveness claims；
   - 当前成本审计：
     `python scripts\summarize_evp8_cost_accounting.py --check` 已通过；
     blocked attempts 是成本/执行风险证据，不是 valid model-result records；
   - smoke 之后的后续顺序已经写入 canonical EVP-8 plan：
     two-model smoke synthesis -> 独立 no-API full-run packet -> DeepSeek
     686-call full run -> DeepSeek audit passed -> Qwen 686-call full run -> Qwen
     audit passed -> two-model first-batch synthesis passed -> later-model execution packet
     -> Kimi/Devstral/Gemini 补跑 -> five-model synthesis -> paper/artifact
     freeze；当前该链路已完成到 five-model synthesis passed，下一步已收敛为
     SQJ no-API paper route：claim-boundary audit -> SQJ framing ->
     Springer `sn-jnl` LaTeX draft -> figures/tables -> artifact freeze ->
     school-recognition confirmation -> submission；
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
  EVP-8 DeepSeek/Qwen post-smoke audit；当前已 `passed`，审计 tracked
  summaries、执行顺序、parse/cost gates、per-evidence-level decision/count
  aggregates 和 raw-output ignored boundary。
- `data/protocols/evp8_deepseek_qwen_smoke_synthesis_v0_1.json`、
  `docs/experiments/evp8_deepseek_qwen_smoke_synthesis_v0_1.md`：
  EVP-8 DeepSeek/Qwen G4 smoke synthesis；当前已 `passed`，只从 tracked
  audit/summary fields 汇总 two-model per-level decision patterns。
- `data/protocols/evp8_deepseek_qwen_first_batch_full_check_only_v0_1.json`：
  EVP-8 DeepSeek/Qwen first-batch full-run check-only summary；当前已
  `passed`，覆盖 98 candidates x 7 levels = 686 prompts，不调用 API、不存
  rendered prompt text、不生成 raw outputs。
- `data/protocols/evp8_deepseek_qwen_first_batch_full_run_packet_v0_1.json`、
  `docs/experiments/evp8_deepseek_qwen_first_batch_full_run_packet_v0_1.md`：
  G5 no-API first-batch full-run packet；当前 `ready`，记录 DeepSeek/Qwen
  686-call exact commands、expected outputs、cost fields、post-full-run audit/
  synthesis commands 和非授权边界。
- `data/protocols/evp8_deepseek_qwen_first_batch_full_result_audit_v0_1.json`、
  `docs/experiments/evp8_deepseek_qwen_first_batch_full_result_audit_v0_1.md`：
  first-batch full-run post-result audit；当前 `passed`，不读取 raw outputs。
- `data/protocols/evp8_deepseek_qwen_first_batch_full_synthesis_v0_1.json`、
  `docs/experiments/evp8_deepseek_qwen_first_batch_full_synthesis_v0_1.md`：
  first-batch full-run two-model synthesis；当前 `passed`，从两个
  raw-output-free first-batch summaries 汇总 tracked per-level decision counts。
- `data/protocols/evp8_later_model_openrouter_catalog_audit_v0_1.json`、
  `docs/experiments/evp8_later_model_openrouter_catalog_audit_v0_1.md`：
  G7 later-model OpenRouter public catalog audit；当前 `all_available = true`，
  只检查 pinned model IDs，不使用 API key、不调用模型。
- `data/protocols/evp8_later_model_completion_packet_v0_1.json`、
  `docs/experiments/evp8_later_model_completion_packet_v0_1.md`：
  G7 no-API later-model completion packet；当前 `ready`，记录 Kimi/Devstral/
  Gemini exact model IDs、expected outputs、cost ceiling、guard commands、stop
  gates 和非授权边界。
- `configs/evp8_later_models.example.json`：
  tracked no-secret later-model OpenRouter config template；local copy 是
  ignored `configs/evp8_later_models.local.json`。
- `data/protocols/evp8_later_model_local_config_plan_v0_1.json`：
  G7.1 later-model local config plan；记录 ignored local config target、planned
  model IDs、call counts 和 no-key boundary。
- `data/protocols/evp8_later_model_preflight_summary_v0_1.json`：
  G7.1 later-model preflight summary；当前 `structural_ready=true`、
  `credential_presence_ready=false`，不打印 key value、不调用 API。
- `data/protocols/evp8_later_model_full_check_only_v0_1.json`：
  G7.1 later-model full check-only summary；当前 `passed`，验证 686 prompts
  per model / 2058 planned later-model calls，不生成 raw outputs。
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
  guarded EVP-8 DeepSeek/Qwen smoke/full runner；check-only 不调用 API，真实
  执行必须使用 ignored local config、strict preflight、显式 `--execute`、
  `--run-scope smoke|full` 和单个 configured `--model-id`；executed summary
  必须保留 raw-output-free per-level review/parse/decision aggregates。
- `scripts/write_evp8_smoke_execution_packet.py`：
  从 tracked protocol/preflight/check-only summaries 生成 no-API smoke
  execution packet；`--check` 要求 packet ready 且仍不授权 API。
- `scripts/audit_evp8_smoke_results.py`：
  不读取 raw outputs 的 post-smoke summary audit；无真实 smoke summaries
  时输出 `waiting_for_execution`，当前 smoke 后输出 `passed`；会检查每个
  `E0-E6` 的 per-level aggregate 是否完整，避免 G4 synthesis 读取 ignored
  raw responses。
- `scripts/summarize_evp8_smoke_synthesis.py`：
  不读取 raw outputs 的 G4 synthesis scaffold；无真实 smoke summaries 时输出
  `waiting_for_execution`，DeepSeek-only pass 时输出
  `partial_waiting_for_qwen`，当前双模型均通过后只报告 tracked per-level
  decision counts 和严格 claim boundary。
- `scripts/write_evp8_first_batch_full_run_packet.py`：
  生成 G5 no-API first-batch full-run packet；不授权 API。
- `scripts/audit_evp8_first_batch_full_results.py`：
  不读取 raw outputs 的 first-batch full-run summary audit；当前 DeepSeek 和
  Qwen full summaries 均通过后输出 `passed`。
- `scripts/summarize_evp8_first_batch_full_synthesis.py`：
  不读取 raw outputs 的 first-batch full-run synthesis scaffold；当前 DeepSeek
  和 Qwen full summaries 均通过后输出 `passed`。
- `scripts/write_evp8_later_model_completion_packet.py`：
  生成 G7 no-API later-model completion packet；要求 catalog audit、first-batch
  audit/synthesis、full check-only 和 expected-output absence 均通过。它只写
  handoff packet，不调用 Kimi/Devstral/Gemini API。
- `scripts/create_evp8_later_model_local_config.py`：
  创建 ignored later-model local config，tracked summary 不含 API key。
- `scripts/preflight_evp8_later_models.py`：
  later-model OpenRouter local config preflight；`--allow-missing-credentials`
  允许 structural check-only，`--strict-api-ready` 才要求
  `OPENROUTER_API_KEY` present。
- `scripts/run_evp8_later_model_full.py`：
  later-model guarded full runner；`--check-only` 不调用 API，`--execute`
  需要 ignored local config、strict preflight、单个 configured model id 和
  explicit flag。
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
- `docs/experiments/evp8_later_model_completion_packet_v0_1.md`：
  G7 later-model no-API handoff；当前状态 ready，runner/preflight/check-only
  已 structural checked，但后续执行仍要求 `OPENROUTER_API_KEY` strict
  preflight 和逐模型显式授权。
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
  script-generated paper tables；当前包含 EVP-7 workload ledger、EVP-8
  five-model decision patterns 和 EVP-8 cost accounting。
- `docs/paper/sqj_submission_framing.md`：
  SQJ no-API submission framing and claim-boundary packet；当前 `sn-jnl`
  草稿应从这里和 Markdown draft 读取论文逻辑。
- `docs/paper/sqj_submission_draft.tex`：
  first generated Springer Nature `sn-jnl` SQJ source draft；当前引用
  `docs/figures/sqj/` 的三张 SQJ figures，但未本地编译。
- `docs/paper/sqj_references.bib`：
  generated BibTeX references for the SQJ source draft。
- `docs/artifact/sqj_submission_checklist.md`：
  SQJ source-package checklist；记录 non-OA route、学校认定确认门、source
  draft/BibTeX/table/figure package、allowed/forbidden claims、no-API boundary
  和 not-final-freeze 边界。
- `docs/artifact/sqj_final_freeze_readiness.md`：
  SQJ final-freeze readiness and blocker packet；记录当前 source package 已
  准备内容，以及学校认定、`sn-jnl.cls`/PDF compile、作者/基金/利益冲突、artifact
  rebuild 和最终用户授权缺口；该文件不授权投稿。
- `docs/paper/ieee_submission_draft.tex`：
  historical/source IEEEtran draft；当前包含 `Workload at a Glance` 章节和
  `tab:evp7-workload-ledger`，但 SQJ 路线下不再作为下一投稿主格式。
- `docs/paper/advisor_workload_response_zh.md`：
  中文导师/答辩工作量说明；集中回答当前工作量、bounded claim、不能写的
  overclaim，以及为什么当前论文不是单纯 prompt comparison。
- `docs/artifact/submission_freeze_candidate_20260618.md`：
  no-API freeze-candidate packet；记录当前 paper/artifact candidate 状态和
  仍需用户确认的 target venue、format、final freeze、Git sync 边界。
- `docs/figures/`：
  reproducible PDF/SVG/PNG paper figures。`docs/figures/fig1` through `fig7`
  是旧 IEEE/EVP-7 可复现图集；`docs/figures/sqj/` 是当前 SQJ/EVP-8 主图集。
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
  paper-ready Markdown/LaTeX tables；当前也生成 EVP-7 workload ledger、
  EVP-8 five-model decision patterns 和 EVP-8 cost accounting。
- `scripts/summarize_evp8_cost_accounting.py`：
  EVP-8 no-API cost accounting summary builder；读取 raw-output-free passed
  summaries 和 ignored blocked-attempt summaries，不读取 raw responses。
- `scripts/write_ieee_latex_draft.py`：
  IEEEtran historical/source draft generator；SQJ 路线下不再作为下一投稿主格式，
  只作为内容来源和回归检查。
- `scripts/write_sqj_latex_draft.py`：
  SQJ Springer Nature `sn-jnl` source draft generator；`--check` 生成
  `docs/paper/sqj_submission_draft.tex` 和 `docs/paper/sqj_references.bib`，
  并验证 source structure 和 SQJ figure references，不调用 API、不编译 PDF。
- `scripts/generate_sqj_figures.py`：
  SQJ-specific EVP-8 publication figure generator；生成 `docs/figures/sqj/`
  下的 protocol、decision-pattern 和 cost-boundary 三张 PDF/SVG/PNG 主图。
- `scripts/audit_sqj_submission_checklist.py`：
  SQJ source-package checklist audit；验证 source draft、BibTeX、tables、
  figure set、five-model synthesis、cost accounting/API freeze 和 not-final-freeze
  边界，不调用 API、不编译 PDF。
- `scripts/audit_sqj_final_freeze_readiness.py`：
  SQJ final-freeze readiness packet audit；验证 readiness 文档和外部 blocker
  边界，不调用 API、不编译 PDF、不授权投稿。
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
