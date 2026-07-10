# DSA 2026 P0/D0 决策记录

记录日期：2026-07-11

当前状态：P0_IN_PROGRESS / D0.6_TEMPLATE_BUILD_PASS_AUTHOR_METADATA_PENDING /
D0.1--D0.3_AND_D0.5_PENDING / D0.4_BUDGET_AUTHORIZED_ATTENDANCE_PENDING

本文件只记录 P0/D0。它不授权 P1、source feasibility、candidate transform、prompt、
smoke、full run 或任何模型 API。

## 1. Gate 总表

| Gate | 当前状态 | 已完成证据 | 尚缺证据 |
|---|---|---|---|
| D0.1 AI policy | PENDING | IEEE 通用政策已核验；DSA 询问信已完成并找到 Secretariat 邮箱 | 发信、保存原始 sent copy、取得 DSA 书面回复 |
| D0.2 EI | PENDING | 2023--2025 IEEE Xplore proceeding ID、catalog、ISBN 已冻结 | 学校 Engineering Village/Compendex 三届 accession 记录 |
| D0.3 publication | PARTIAL | 官网确认 IEEE CPS，并写明 submitted for possible inclusion | 2026 IEEE conference ID、catalog、ISBN/CPS 最终状态书面确认 |
| D0.4 logistics | PARTIAL | 用户已授权 API/注册/差旅预算无需再次确认；费用按 Others USD 750 保守规划 | 共同作者现场参会人和注册日期可行性 |
| D0.5 authorship | PENDING | AI-use inventory 已建立；作者责任清单已列出 | 全体作者姓名/单位/邮箱和逐项人工签核 |
| D0.6 venue/template | PARTIAL (technical pass) | 官方页面/ZIP 哈希、页限、`IEEEconf.cls` clean build、字体/渲染/PDF hash 均通过 | 用最终作者元数据替换 skeleton placeholder，投稿前再次核验活页面 |

P0 总 Gate 仍为 STOP。D0.1--D0.5 全部 PASS 前不得激活 P1。

## 2. Venue Decision Record

- 唯一目标：DSA 2026 Regular Paper。
- DSA scope 与研究问题直接匹配：dependable software、verification/testing、program
  repair、empirical study 和 generative-AI dependability 均在官方主题内。
- Short 仍只是 P2 前可能冻结的独立协议；当前不是活动路线。
- ACAI inactive；禁止并行投稿。
- 官方 Regular 页限是 12 页，明确包括 content and references。
- 官方初稿实名，不是 double-blind：要求作者姓名、单位、摘要和最多 6 个关键词；
  每稿最多 5 位作者。
- proceedings 页面只承诺提交 IEEE Xplore/EI，不构成最终 EI 保证。用户的最低 EI
  要求尚未通过 D0.2。
- 官方页面未发现 DSA-specific GenAI author policy，因此 D0.1 不能凭 IEEE 通用政策
  自动标 PASS。

完整来源和哈希见 `official_source_snapshot_20260711.md`。

## 3. AI-Use Inventory

### 3.1 LLM 作为历史实验对象

旧 EVP artifacts 记录过以下固定模型标识：

- `deepseek/deepseek-v4-pro`；
- `qwen/qwen3.7-max`；
- `moonshotai/kimi-k2.6`；
- `mistralai/devstral-2512`；
- `google/gemini-2.5-flash`。

这些旧实验全部为 quarantined development/exploratory provenance，不进入 DSA 新
confirmatory 统计。新实验使用哪些模型必须到 P3 由作者冻结；P0 不选择模型。

### 3.2 AI 参与研究工程和科学设计

- OpenAI Codex 已实质参与仓库检查、实验根因审计、计划形成、代码/文档编辑、
  deterministic verification、Git 检查和 DSA P0 官方政策/模板核验。
- 2026-07-10 的 DSA 总计划含 AI 提出的研究问题压缩、实验数量、统计边界、
  no-rerun 规则、论文结构和投稿 Gate；作者尚未逐项签核为自己的科学决定。
- 2026-07-11 的 P0 输出，包括询问信、source snapshot、AI inventory、skeleton source
  和 build audit，由 Codex 协助生成并由确定性工具核验。
- 历史仓库没有为所有早期文件持续记录 AI system/build、输入范围和采纳程度。这是
  provenance gap，不能补写成“仅语法润色”。现有 Git、prompt change log、protocol
  和计划记录必须保留。

系统标识记录：OpenAI Codex，GPT-5-based；仓库未暴露每次服务端 build/version，
因此不能虚构更精确版本。

### 3.3 AI 参与论文文字、图表和引用

- 当前 APSEC Markdown/LaTeX/PDF 曾接受 AI 辅助审阅、改写、结构和版式工作；它们
  已降级为 historical baseline，不直接转投 DSA。
- DSA 新稿尚未开始。后续每段正文、图表和引用必须进入 provenance ledger，记录
  system/date/input/output/adoption/author verification/policy disposition。
- IEEE 的 grammar-only exception 不适用于本项目的整体 AI 参与程度。
- AI 不能列为作者，也不能承担科学责任。

## 4. D0.2 Engineering Village 核验单

请通过学校图书馆的 Engineering Village 选择 Compendex，分别检索：

1. 2025 12th International Conference on Dependable Systems and Their
   Applications；ISBN `978-1-6654-7769-7`；IEEE catalog `CFP25M61-ART`；
2. 2024 11th International Conference on Dependable Systems and Their
   Applications；ISBN `979-8-3315-3239-0`；IEEE catalog `CFP24M61-ART`；
3. 2023 10th International Conference on Dependable Systems and Their
   Applications；ISBN `979-8-3503-0477-0`；IEEE catalog `CFP23M61-ART`。

每届必须保存：检索式、数据库、检索日期、会议记录/论文记录、Compendex accession
number、截图或导出。仅找到 IEEE Xplore、DBLP、Scopus 或 Google Scholar 不算 D0.2
PASS。

## 5. D0.4 Logistics Sign-Off

当前签核状态：

- [ ] 至少一位共同作者能于 2026-11-14--15 到厦门现场报告；
- [ ] 现场报告人是论文共同作者，不是 guest presenter；
- [x] 不再询问会员预算；当前按 Others USD 750 保守规划，若有会员资格只降低费用；
- [x] 用户已授权每稿 early/author full registration USD 700 或 USD 750，无需再次询问预算；
- [x] 用户已授权差旅、住宿和不可退预算无需再次询问；
- [ ] 能在 2026-10-25 前完成 author registration；
- [ ] 已指定差旅/报告应急联系人。

任一项不能确认，D0.4 FAIL，停止 DSA 路线。

## 6. D0.5 Authorship Sign-Off

- [ ] 所有作者均为人类，人数不超过 5；
- [ ] 已冻结作者顺序、姓名、单位、城市/国家、邮箱和 corresponding author；
- [ ] 每位作者实际理解并能解释研究问题、cohort、oracle、prompt、统计和结论边界；
- [ ] 每位作者能审查代码、原始/清洗数据、分析和最终 PDF；
- [ ] 每位作者接受对准确性、原创性、引用、AI disclosure 和研究诚信的最终责任；
- [ ] 已披露相关 prior publication/public repository/preprint；
- [ ] 已逐项接受、修改或否决 DSA 总计划中的 AI-originated scientific decisions；
- [ ] 最终 AI disclosure 与本 inventory 和 Git/provenance 记录一致。

未逐项签核前，D0.5 保持 PENDING。

## 7. Private Remote Decision

GitHub connector 的只读核验结果：

- `gaoming-a/research95` 存在且为 public，是当前 `origin`；
- `gaoming-a/cross-model-code-review` 和 `gaoming-a/review` 存在且为 private，
  但保存旧研究阶段和旧执行链，不适合作为新的 DSA clean development remote；
- 初始检查未发现独立的 DSA private repository。

执行决定：已新建 `gaoming-a/research95-dsa-private`，visibility=`PRIVATE`，并配置
本地 remote 名为 `private`。它不是 fork，未覆盖两个旧 private repos。提交前仍须执行
staged sensitive scan；只向 `private` push，不向 public `origin` push。

用户已指示：GitHub 同步频繁失败时记录失败并继续执行计划。因此后续每轮仍先尝试
同步 private remote；若同一同步条件连续失败，不得因此改推 public origin，也不阻断
已通过科学 Gate 的本地工作。

审稿 artifact 与 private development repo 不是同一对象。artifact 必须从 clean
staging 生成，无 `.git`、作者本机路径、credentials、raw responses、受限 benchmark
或历史 exploratory outputs；是否提交 URL 等 Secretariat 回复。

## 8. P0 完成前所需外部动作

1. 用户从自己的邮箱发送 `dsa_secretariat_inquiry_en.md`，保存 sent copy 和回复；
2. 学校图书馆完成三届 Compendex 核验；
3. 用户/全体作者完成 D0.4 与 D0.5 签核并提供作者元数据；
在三项完成前，本轮只能提交 P0 文档和 template skeleton，不能进入 P1。

## 9. API Standing Authorization

2026-07-11 用户明确授权后续实验使用现有 API key，且无需再次确认预算。执行边界：

- 本授权只在 D0、P1--P5 全部 passed 后激活；P0 当前不得调用模型；
- P5 必须先冻结 exact model IDs、requests、retries、token/cost hard cap、no-fallback、
  hashes 和中断恢复语义；
- G1 smoke passed 后可自动进入满足 Gate 的 G2 full，不再请求预算确认；
- 不能超过 hard cap，不能因结果弱/方向不利而重跑，不能读取结果后改稿型、prompt、
  task、oracle、模型或重复数；
- API key 继续只从 ignored local configuration/environment 读取，不能写入 tracked
  文件、日志或提交。
