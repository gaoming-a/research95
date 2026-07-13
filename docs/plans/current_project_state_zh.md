# 当前项目状态与文件地图

日期：2026-07-13

## 2026-07-13 DSA development pilot standing authorization / unsigned

- v0.3 逐 aggregate 签核入口已被一次性 standing-execution proposal 取代；
- protocol SHA=`7ceb704a0d0310f60c86ee46356bacd0b4793fc772e3e1ac7b241ef68462d899`，
  当前首个派生候选仍为 v0.3 aggregate `90e1eebc…49d38`；
- scientific surface 锁定 pair、packets、prompt/schema、exact routes、72项调度、repeats、
  development exclusion 与 no-outcome-rerun；执行链修复必须逐版本通过 conformance；
- 作者只需签署 standing protocol 一次；以后合规的纯执行修复自动派生 authorization；
- 科学表面变化、已有有效输出重跑、leakage、完整性失败、公开发布或投稿仍暂停；
- 当前 unsigned，standing/v0.3 active authorization 均不存在，v0.3 API=0、output absent。

## 2026-07-13 DSA 72-call pilot v0.2 terminal / v0.3 unsigned repair freeze

- v0.2 canary 已发出8次 Qwen endpoint HTTP 请求，全部因字符串
  `max_tokens="omitted"` 在推理前返回400；有效模型输出=0、科学决策=0、retry=0；
- 剩余64次未启动；v0.2 authorization、request ledger 和8条 raw error hash 已由
  terminal audit 绑定，v0.2 禁止恢复或覆盖；
- v0.3 不改 pair、packets、prompt/schema、三条 routes、repeats 或 factorial，只删除
  request body 中的文档哨兵，并在第一条 non-valid terminal record 后立即停止；
- v0.3 使用新 request domain/output path；prepare/check、runner check-only、token 整数
  类型、route metadata、hidden separation 和无授权执行阻断均 PASS；
- aggregate SHA=`90e1eebc6ce182ccb5a5f8cf4efef1eca14ed2d9dc68ded55adf1efec3849d38`；
  v0.3 unsigned，v0.3 API requests=0、output absent；
- V2-P2 仍 attempted=62、qualified=0、order63 `started=false`。

## 2026-07-13 DSA 72-call pilot v0.2 OpenRouter refreeze / unsigned / no API

- v0.1 authorization 已在 model calls=0、output absent 时撤销，active 文件不存在；
- pair、packets、prompt/schema、Qwen/DeepSeek 和 72-request 结构未变；
- route3 改为 OpenRouter `google/gemini-3.5-flash`，canonical
  `google/gemini-3.5-flash-20260519`，只允许 `google-ai-studio/priority`，禁止 fallback；
- strict schema、minimal reasoning、router metadata 和 provider/model/attempt/pipeline
  runtime hard stops 已冻结并通过对抗性 fixtures；
- aggregate SHA=`2ee6c3f03e14f64723b5ddb52187c63ed83cb4f2d5bb2dfea5d16a7c2412ebc3`；
  v0.2 unsigned，API key reads/model calls=0，两个 pilot output 目录均不存在；
- V2-P2 仍 attempted=62、qualified=0、order63 `started=false`。

## 2026-07-13 DSA 72-call pilot signed / credential-blocked before network

- 作者签核与 authorization record 已绑定 aggregate `f8992839…cfebeb`；
- 签核前 freeze/check、runner check-only PASS；
- 首次 canary 在读取不到 `DASHSCOPE_API_KEY` 时 fail closed，未创建 output、未发出请求；
- `.env` 仅声明 `QWEN_API_KEY`、`DEEPSEEK_API_KEY`，没有 `DASHSCOPE_API_KEY`、
  `GEMINI_API_KEY`；Windows process/user/machine 也没有三个冻结变量；
- 当前仍为 model calls=0，order63 未启动；等待精确凭证注入，不修改冻结 surface。

## 2026-07-13 DSA 72-call development pilot frozen / unsigned / no API

- V2-P2 ledger v0.62：attempted=62、qualified=0、next order63
  `bugsinpy_ansible_9`、started=false、API=0；order63 暂停未启动；
- 旧证据中4个 eligible pairs 按冻结 pair-hash 规则机械选择 selection SHA
  `12174ce2…e8e6`，不是按模型预期表现人工挑选；
- positive/negative 在 digest-frozen、network-none 镜像中各通过2 basic + 1 F2P +
  3 P2P；8个匿名 C0--C3 packets 与72项三路线/三重复调度已冻结；
- prompt/schema 静态和对抗性 schema checks、hidden separation、LF byte-hash、runner
  check-only 与无签核 execute block 全部 PASS；
- aggregate SHA=`f8992839f6b47c507ab4bf8e0f49d2e63d6238998a2ff666d674b8eee4cfebeb`；
  当前 unsigned，API key read/model calls/network requests=0。

## 2026-07-12 Continuous V2-P2 authorization active

- 当前 ledger v0.2：attempted=2、qualified=0、next order3 `bugsinpy_black_4`、started=false；
- 作者已授权连续自动执行 V2-P2、普通 task failure 自动继续和本地 checkpoint commits；
- 30 pairs 后只在 V2-P3 hash-bound 作者签核暂停；签核前 model API=0；
- hard stop、冻结漂移、公开发布和投稿仍必须暂停；当前未启动 order3。
- order3 official archives 暴露13个相同 dangling docs symlinks；unsigned omission/manifest
  amendment 已生成，SHA=`6d072620…74847`。作者签核前不提取、不构建、不测试。

## 2026-07-12 V2-P2 order-2 terminal / STOP BEFORE ORDER3（已被上方覆盖）

- 当前状态：`V2_P2_ORDERS_1_2_ENVIRONMENT_TERMINAL / ORDER_3_NOT_STARTED /
  NO_API / V0_SUBMISSION_GATE_PENDING`；
- order2 FastAPI_11 environment build exit=1：pip20.1.1 无法 editable-install pyproject-only
  checkout，且 frozen requirements 的 Starlette0.12.8 与 FastAPI0.55.1 所需0.13.2冲突；
- 未修依赖、未重跑；image/container/test/oracle/candidate/API=0；
- terminal ledger v0.2 精确保留 order1 record 并追加 order2；next=`bugsinpy_black_4`、
  started=false；按用户要求不创建或执行 order3 Goal。

## 2026-07-12 V2-P2 order-2 preflight PASS（已被上方覆盖）

- 当前状态：`V2_P2_ORDER_1_TERMINAL / ORDER_2_REAL_PREFLIGHT_PASS /
  FASTAPI_11_NOT_STARTED / NO_API`；
- order2 runner 完整绑定 previous ledger、FastAPI_11 metadata、py383、tests scope、dual-fresh
  oracle、T1--T4 与独立 terminal draft；order1 文件不会被执行器覆盖；
- order2 failure logging 已在结果前改为把具体失败子命令输出到 outer build log；不改变
  dependency authority，也不授权修复或重跑；
- 当前 order2 checkout/environment/container/test/API=0；下一步只冻结 official source。
- official FastAPI_11 source/context 现已 write/check PASS，context tree=
  `d4072ff1925bb925d6367f253ad6a18fc5f5a14b8cc51c1c53cb20aadcc5b81b`；
  checkout=1，environment/container/test/API仍为0；下一步是唯一 no-cache image build。

## 2026-07-12 V2-P2 order-1 terminal / cursor continues（已被上方覆盖）

- 当前状态：`V2_P2_ORDER_1_MATERIALIZATION_FAILED_ENVIRONMENT /
  ORDER_2_READY_NOT_STARTED / NO_API / V0_SUBMISSION_GATE_PENDING`；
- pandas_161 official source/context 已冻结；唯一 no-cache py383 build 在 dependency-build
  aggregate exit=1，未生成 task image；没有 container/project-test/oracle/candidate outcome；
- order=1 terminal reason=`environment-build-failure`；未执行 setup、未修依赖、未重跑；
  checkout/build/container/test/API=1/1/0/0/0；
- exact failed subcommand 因子日志只存在于 discarded failed layer 而不可恢复；这是证据
  局限，不授权重跑；
- V2-P2 并未整体 hard stop。next cursor 是 order=2 `bugsinpy_fastapi_11`，started=false；
  当前 Goal 完成封存后，按作者自动授权另设 order-2 Goal 继续。

## 2026-07-12 V2-P2 order-1 real preflight PASS（已被上方覆盖）

- 作者高明已签核 SHA-bound V2-P1 清单并授权自动执行 V2-P1 至 V2-P2；test-scope
  amendment 状态为 `author_signed_immutable`；
- 当前状态：`V2_P2_ORDER_1_REAL_PREFLIGHT_PASS / PANDAS_161_NOT_STARTED /
  NO_API / V0_SUBMISSION_GATE_PENDING`；
- source freezer、py383 no-setup task image、dual-fresh oracle、project-root pool、T1--T4
  materializer、candidate runner 与 terminal ledger 均已 outcome 前实现；synthetic T1--T4
  10/10 patch/tree 可重放；
- real preflight 全项 PASS；checkout/environment/container/project-test/prompt/key/API
  在 pre-outcome 时均为0；现已冻结 order=1 official source/context，context tree=
  `fc25ef1325ecba7a346f576012d13349050e76709cc1f07fad7b05d81aee7108`，checkout=1，
  environment/container/test/API 仍为0；下一步构建唯一 py383 task image；
- 作者的 V2-P2 自动授权不授权 V2-P3、prompt/schema、论文结果或模型 API；到 V2-P3
  final freeze 或冻结 hard stop 必须暂停。

## 2026-07-12 V2-P2 首任务 pre-outcome amendment Gate（已被上方覆盖）

- 用户已授权真实处理 order=1 `bugsinpy_pandas_161`，但尚未发生 checkout、环境构建、
  container、项目测试或模型请求；
- Inspect 发现 V2-P1 文本引用 project recipe 中的 project test root，而签核 artifact
  的九个 recipe 均遗漏该字段；真实活动在 outcome 前暂停；
- 当前只生成基于299条冻结 `declared_test_file` 的九项目 test-scope/collection-adapter
  amendment proposal；不修改 V2-P1 hashes；
- 作者签核 amendment 后，本 Goal 才恢复首任务真实材料化；第二个 task、V2-P3、prompt、
  论文结果与模型 API 仍不授权。

## 2026-07-12 V2-P2 executor check-only 状态覆盖（已被上方覆盖）

- 当前状态：`V2_P2_EXECUTOR_CHECK_ONLY_PASS / REAL_MATERIALIZATION_NOT_AUTHORIZED /
  FIRST_TASK_NOT_STARTED / NO_API / V0_SUBMISSION_GATE_PENDING`；
- 纯状态机 executor 与 deterministic write/check auditor 已完成；它们只消费 synthetic
  metadata，没有 filesystem/process/network/container/test/prompt/API 执行能力；
- V2-P1 aggregate 与299-task source order 均未变化；首个 cursor task 仍为
  `bugsinpy_pandas_161`，只完成 identity selection，没有 checkout 或启动；
- 六条成功/失败/停止路径与五条协议漂移拒绝路径全部 PASS，真实 checkout、环境构建、
  container、项目测试、prompt render、API key read 和模型请求计数均为0；
- 下一 Goal 只有在用户明确授权后才可开始真实 V2-P2 materialization；该授权不自动
  扩展到 V2-P3、prompt、论文结果或模型 API。

## 2026-07-12 V2-P1 状态覆盖（已被上方覆盖）

- 当前状态：`V2_P1_PASS_AUTHOR_SIGNED / RULES_FROZEN /
  V2_P2_NOT_AUTHORIZED / NO_API / V0_SUBMISSION_GATE_PENDING`；
- 作者高明签核的8项原文已保存，SHA-256=
  `65328de6aa913bd8ee04dfdbfd172960745bc431ab7d2f7742c8aa7038dbe2ca`；
- V2-P1 冻结299 tasks/9 projects 的完整 project-round-robin source order；P2 development
  与 v0.1 五个 P4-active tasks 均排除；source-order SHA-256=
  `21be1d9fed719de44126be585fa7e9123fd8579588d9ce86eb396d4ab5c2dd11`；
- 六个 Python base locks、固定 bootstrap versions、project recipe template、T1--T4
  全候选枚举、pre-candidate regression split、dual-fresh qualification 和30-pair/source
  exhaustion stop rule 均已冻结；
- V2-P1 check-only Gate 全部 PASS；没有 task checkout、environment build、container、
  project test、candidate/model outcome、prompt render 或 API；
- V2-P2 尚未授权。下一 Goal 只可实现 executor 与 synthetic metadata dry-run；真实
  materialization 需要新的明确用户授权；
- V0 submission gates 继续 pending，不因 V2-P1 通过而自动满足。

## 2026-07-11 v0.2 路线覆盖（已被上方覆盖）

- 当前状态：`V0_1_TERMINATED_BEFORE_MODEL_OUTPUT / V0_2_DESIGN_DRAFT /
  V2_P1_AUTHOR_SIGNOFF_PENDING / NO_API / V0_SUBMISSION_GATE_PENDING`；
- P3/P4 v0.1 在模型 API=0、confirmatory outputs=0、P4 final Gate 未形成时终止；
  不是不利模型结果驱动，也不声称预注册 capacity stop 已触发；
- P2/P3 v0.1 immutable artifacts 保留不变，16-file aggregate 仍为
  `f81ba7063297dc9264041256b99a7daa002bd730cbe1dbd9bfb105cd7aa71297`；v0.1
  P4 记录只作 feasibility/provenance，不得进入 v0.2 效果量或模型结果；
- 唯一 active 实验计划为
  `docs/plans/dsa_agent_evidence_experiment_v0_2_zh.md`；核心仍是同一候选在
  C0--C3 累积真实证据下 reviewer agent 的 `accept/reject/escalate` 变化；
- v0.2 把通用材料构造规则冻结在 outcome 前，把 clean environment、positive/negative
  行为资格验证放到最终 cohort/P3 冻结前；只有机械顺序中前30个合格 task pairs 才
  进入确认性冻结；
- reviewer agent 是 frozen endpoint + neutral prompt + JSON schema，无自主工具；
  计划有效响应为 2160，task 仍是唯一科学分析单位；
- 当前 V2-P1 签核清单未签署，不授权 materialization、task/test/container、prompt
  修改或 API；下一步必须先由作者签核8项 construction rules；
- DSA 的 AI policy、学校 Compendex、2026 publication metadata、现场报告人与 authorship
  仍是独立 V0 submission gates，未因实验路线重构而通过。

## 2026-07-11 DSA P4 preflight 状态（v0.1 历史，已被上方覆盖）

- 当前状态：`P2_SOURCE_FEASIBILITY_PASS / REGULAR_FROZEN /
  P3_PASS_AUTHOR_SIGNED / P4_IN_PROGRESS / P5_NOT_STARTED /
  SHORT_INACTIVE / V0_SUBMISSION_GATE_PENDING / NO_API`；
- P0 的官方 source/template/private remote 本地证据包已完成。AI policy、学校
  Compendex 核验、2026 publication metadata、现场报告人和 authorship metadata
  作为并行 V0 外部门继续等待，V0 未通过时不得提交 DSA，但不否定已完成的 P2；
- P1 已建立机器 denylist、人工隔离注册表和 superseding validity audit。旧 APSEC/
  EVP-8/current-98/HARD/coverage/stress 结果只允许 provenance、失败复盘和任务排除，
  禁止进入 DSA 效果量、表图、claim map 或正文数字；
- 机械复现确认 E6-no-verdict 的嵌套 `visible_tests_rule_decision` 残留为 98/98；两个
  旧 full config 各有 686 个结构等价 packet，并复现未物化字段和空 P2P evidence；
- P2 将 development task exclusion 扩展到 59 tasks，P1 的整项目排除保持 8 projects；
  official/improved-reproduction snapshot 形成 304-task/9-project source frame；
- Regular 已冻结为 30 primary + 10 reserve/9 projects/60 planned candidates；每项目
  primary≤4 且都有 reserve。Short precision 虽通过但已 inactive，不是结果 fallback；
- transform registry 仅在 excluded development tasks 上验证；P2 没有对 source 应用
  transform、读取 candidate hidden result 或创建候选；
- Regular precision 最大 rate/effect width 为 0.1185/0.1704，低于 0.35/0.30；12 篇
  最近邻定位 Gate 通过，但禁止 first/unique/SOTA 或 autonomous correctness claim；
- 新 DSA 脚本必须采用 `scripts/dsa2026_*.py`，并在每次新增或修改后通过
  `python scripts/audit_dsa_legacy_quarantine.py --check`；
- P3 已形成预注册、evidence contract、三条 exact model route、一个全新 DSA
  prompt/schema、synthetic render/leakage audit 和 immutable hash manifest；作者
  高明已逐项签核 11 项并承担科学责任，机械/作者 Gate 均 PASS；
- 用户 standing API authorization 只在 P1--P5 全 pass 后激活；P3 已过但 P4 正在
  执行且 P5
  未过，因而仍禁止 smoke、full 和模型 API；
- private remote 已配置并为当前分支 push target；public `origin` 禁止作为 fallback。
  当前唯一 active goal 是 P4 dual-clean cohort materialization；P5 未创建、未进入。
- P4 preflight 已通过：P2/P3 immutable hashes、40-task/F2P metadata 和 catalog commit
  均无漂移；source-only transform scan 为 T1=3/T2=17/T3=8/T4=8/NONE=4。
  结构上最多 36 pairs，达到 30 pairs 仅余 6 个非结构性 exclusion 空间；
- 6 个冻结 Python 版本已导出 Conda explicit locks。candidate-independent toolchain
  image ID 为 `sha256:97e089cee02d0908e374f7b784ee0ffbb2fe5a2d64f619335aa962dc3ab3d768`，
  两个无网络 fresh containers 的版本/lock 输出一致；正式 task-specific environment、
  oracle registry、candidate pair 和最终 P4 Gate 尚未完成。
- `bugsinpy_fastapi_12` 的 task environment 与 official F2P 已在两个 fresh containers
  一致通过；40-node regression pool 已在任何 pool outcome/transform 前冻结并哈希。
  随后的双环境逐节点验证为 40/40 stable pass，现已冻结 visible P2P=3、hidden=20；
  official positive 与唯一 T4 partial-reversion candidate 已在任何 candidate outcome
  前物化并哈希，materialization SHA-256 为
  `41bbfc2319f9f5aa336cb772e5db5f098211cf7d3253120df6b577648d0445bb`；
  candidate worker/runner 已独立实现并通过静态与 namespace audit。保留同一 T4 edit
  修复 CRLF patch bytes 后，四个正式 fresh containers 已完成：positive 26/26 pass；
  negative 的 syntax、F2P、3 P2P、20 held-out 均稳定 fail。negative 未通过 visible，
  因而 task Gate=`DISCARD_TASK`、model-visible records=0、leakage=0；非结构性 discard
  理论余量降为 5。P4 final Gate 未形成，下一 task 本轮未启动。
- replacement-cursor audit 已把 primary #1--#3 的 structural/terminal/structural
  discards 分配给 reserve #1--#3，但 reserve 只在 primary scan 完成后执行。唯一 next
  task 已冻结为 primary #4 `bugsinpy_tornado_10`，cursor SHA-256=
  `24f37f3f2eefe99c9346b4b141965cb137e8f7dfb87e6e11eaa0ac909b0fbf2e`；
  该审计未创建/运行新 task、candidate、container 或 API request。
- primary #4 `bugsinpy_tornado_10` 的 official source/context 先完成 hash freeze，
  但 task-specific image 构建在 official `setup.sh` 第1条 `pip install unittest`
  以 exit=1 失败。按 P3 no-redesign 规则，任务状态为
  `DISCARD_PRE_CANDIDATE_ENVIRONMENT_BUILD_FAILURE`；没有修改依赖，也没有执行 F2P、
  发现 regression pool、物化 T1 或调用模型。P4 仍在进行中，当前 bounded Goal 已结束；
  下一步须另设 Goal 重新计算 replacement cursor，不能直接启动下一 task。
- post-Tornado cursor replay 已把该 environment discard 作为第4个 realized slot，
  只分配 frozen reserve #4 `bugsinpy_tornado_7`，不执行 reserve。唯一 next task 已更新为
  primary #5 `bugsinpy_matplotlib_21`，transform=`T2_omit_secondary_hunk`，cursor
  SHA-256=`a212352973531adfc58b0e85978fcad1cf65adea100fb2584b66f03ebeb437fb`；
  maximum possible pairs=34、remaining nonstructural discard budget=4。该 cursor Goal
  未构建/运行 Matplotlib task、container、candidate、test 或模型请求。
- Matplotlib #21 的 official buggy/fixed codeload archives 与 task context 已完成
  write/check freeze；context record SHA-256=
  `b1e09a00c57d8adfcfb65a71f5c3028c873f988b56d4f9f573c52a797cfd6660`。
  该 checkpoint 尚未构建 task image、运行 reference F2P/pool、物化 T2 或调用模型。
- 随后的 clean `py381` image ID 为 `sha256:3632b1e6…bb6c5a7`；两个 fresh、
  network-none、mount-free reference F2P runs 均因 frozen environment 缺少 NumPy
  exit=4，且 output hash 完全一致。Gate=
  `DISCARD_PRE_CANDIDATE_REFERENCE_F2P_FAILURE`；未补依赖、未发现 pool、未物化 T2、
  API=0。当前 bounded Goal 结束，下一步须另设 replacement-cursor Goal。

### 2026-07-10 DSA 路线计划基线（已由上方 P2 状态覆盖）

- 当前唯一 active master plan 是
  `docs/plans/dsa_2026_submission_execution_plan_zh.md`。
- 唯一主目标为 DSA 2026 Regular；Short 只是在任何模型调用前、经 P2 feasibility
  和 precision gate 后由用户明确锁定的独立 protocol，不是结果不好时的降格。
  ACAI 当前 inactive，禁止并行投稿。
- 当前状态为 `DSA_2026_ROUTE_PLANNING_ONLY / REGULAR_NO_GO /
  SHORT_NO_GO / WAITING_FOR_D0_P1_P2_P3`。默认 Regular 不等于授权执行。
- 新研究只回答真实、累积 C0--C3 可执行证据如何改变固定 LLM 的
  accept/reject/escalate policy；旧 C4/C5 synthetic-advisory 支线已删除。
- current-98、EVP-8-HARD、coverage-contestation、stress-31 及旧论文全部是
  quarantined development/exploratory provenance，不进入 DSA 主统计、CI、摘要、
  结论或主图表。
- 当前没有新 prompt；没有 smoke/full/API 授权。下一轮严格只执行 P0/D0；P0 passed
  后另开一轮 P1，P1 passed 后才可另开 P2。
- DSA AI 参与许可、近三届 EI 检索、2026 CPS/出版信息、现场参会预算、作者签核、
  官方页面/template ZIP 快照与最小 skeleton 编译仍待完成；在这些门通过前不能把
  DSA 视为已满足最低 EI。
- 推荐独立 private GitHub repository，remote 名为 `private`。URL 尚未提供，当前
  只允许本地提交，禁止向身份关联的 public origin 推送本轮论文计划。
- 现有 APSEC Markdown/TeX/BibTeX/7 页 PDF 只是历史 baseline；DSA 新稿必须使用
  官方 `IEEEconf.cls` 的独立 namespace，按最终 PDF 12/10 页门重新构建。

## 2026-07-10 历史：证据有效性与旧 prompt 退休状态覆盖

- 当时的唯一 active master plan 已切换为
  docs/plans/apsec_ccfc_evidence_repair_plan_zh.md，状态为
  P1_LEGACY_PROMPT_RETIREMENT_COMPLETE /
  STOP_PENDING_G0_AND_COHORT_FEASIBILITY。
- 用户已选择研究目标 A：研究可见证据如何改变 accept/reject/escalate policy，
  不把实验定义为 verifier correctness 证明。
- 四个旧 EVP-8 prompt 模板已从活动工作树物理删除；删除前 SHA-256 和冲突/
  重复检查保存在 `prompts/prompt_change_log.md`。当前没有 EVP-v0.4 prompt。
- 下文或历史 artifact 中的 `current`、`main`、`ready`、`passed` 只表示当时状态；
  所有旧 EVP-8 config/runner 均为 historical/not executable，不得触发新的
  smoke、full run 或模型 API，也不得被静默改指向未来 v0.4 prompt。
- 当前 APSEC Markdown、LaTeX、BibTeX 和 7 页 PDF 只作为历史 draft baseline，
  不是 submission-ready package。
- 旧 final experiment-setting validity audit 和旧 manuscript audit 只证明其
  当时实现的内部一致性，已被 2026-07-10 根因审计超越；它们不能证明当前
  no-verdict、evidence ladder、统计单位或 confirmatory design 有效。
- current-98、EVP-8-HARD、coverage-contestation、stress-31 和所有旧
  v0.1--v0.3 paper-facing 数值全部降级为 development/exploratory evidence。
- 新主线是全新的 EVP-v0.4：30 held-out tasks、至少 8 projects、60 个配对候选、
  四级真实 evidence、正交 synthetic cue 干预、三模型三重复和 task-cluster
  统计。
- 既有 readiness 记录 fresh-project promising candidates=0，P1A 必须先证明
  40 个 source tasks/8 projects 可物化，否则 APSEC 2026 实验路线停止。
- 当前 origin 是身份关联的公开仓库，APSEC 匿名期内不得继续 public push。
  下一轮只能先做 G0 五项决策、P1 历史隔离和 P1A feasibility；在
  G0、P1、P1A、P2--P6 全部通过且用户另行授权前，不得调用 API。

本文件是短入口，用来整理当前计划文档和项目文件。它不替代
`docs/plans/current_plan_zh.md` 的逐轮执行日志，也不替代
`docs/plans/final_paper_roadmap_zh.md` 的研究路线。

当前权威性规则：

- 本文件顶部的 2026-07-10 状态覆盖优先于后文全部历史记录。
- 后文保留的旧分支、旧 hash、旧“下一步”只作为审计追溯，不得覆盖当前
  EVP-v0.4 evidence-validity repair 路线。
- 旧 manuscript claim map、正文 v0.3 和 CCF-C Fig. 1--3 均为历史资产；只有在
  新确认性证据和 claim gate 通过后才能决定是否复用其机械结构。
  配图后端按用户询问后的推荐路径选择 Python/matplotlib，图集位于
  `docs/figures/ccfc/`。Fig. 1--3 已插入
  `docs/paper/ccfc_manuscript_rewrite_v0_1.md` 的对应正文位置，并通过
  `scripts/audit_ccfc_figure_placement.py` 审计。
  附件评审意见触发的 v0.2 修订已把 Qwen v0.3 label-conditioned metrics、
  E6 rule-only/no-verdict baseline 和 E0-E6 evidence ladder 放入主文；未完成的
  majority 和完整 E0/no-tool baseline 仍不得写成已完成结果。
  2026-07-03 追加实验逻辑清理：当前论文包不再携带早期无效设置作为正文内容。
  2026-07-08 追加 APSEC figure/mainline consistency pass：APSEC Fig. 1 不再
  写成五模型 verifier，Fig. 2 已改为 Qwen/DeepSeek/Gemini 三模型 E0/E3/E6
  correct recall、false accept rate、escalation rate，对齐当前三模型主结果。
  2026-07-04 追加 PaperSpine 下一步产物：citation support bank 和 baseline
  feasibility audit 已完成；rule-only visible-tool 是当前已完成 deterministic
  baseline，always-escalate/always-reject/always-accept 以及
  uniform random three-way expected policy 只能作为 reference policies，
  majority vote 和单独 E0/no-tool deterministic verifier 仍不得写成已完成。
  2026-07-04 v0.3 正文已把 citation keys、reference support records、baseline
  policy boundary 和 Wilson 95% CI uncertainty summary 合入正文，并通过
  `scripts/audit_ccfc_manuscript_v0_3.py` reviewer-style audit。
  2026-07-04 五步补齐 pass 已完成：random expected reference、tool-contestation
  opportunity-set Wilson 95% CI、Methods/Results/Discussion/Threats 结构压缩和
  reviewer-aware audit 均已进入可复现生成链路；这不改变 majority/E0-no-tool
  未完成边界。
  2026-07-04 追加 no-API baseline feasibility 复查：tracked model summaries
  只有 aggregate per-level counts，没有 candidate-level aligned decisions；
  因此 majority-vote 不能在当前 no-raw-response 边界下计算。Qwen E0 只能作为
  observed model condition，不能写成 deterministic no-tool verifier。
  2026-07-05 追加 APSEC technical-track Markdown rewrite：
  `docs/paper/apsec_technical_track_rewrite_v0_1.md` 已生成并通过
  `scripts/audit_apsec_manuscript_rewrite.py` 审计。该稿保留当前 bounded claim，
  并已完成 APSEC reviewer-risk repair：标题收窄、candidate composition 表、
  humanized E0-E6 表、RQ4 降级、rule-only 强基线解释、E6 false-accept aggregate
  anatomy、Reference Support Records 删除。它适合作为匿名 IEEEtran / BibTeX /
  10-page APSEC formatting 的下一步输入，但还不是最终投稿 PDF。
  对 realistic hard-negative branch，在 `ready_for_verifier_api=false` 时仍不得
  运行 Qwen/DeepSeek verifier API。该限制不追溯否定 2026-07-05 用户明确授权
  并已完成的 DeepSeek repaired v0.3 E0-E6 main run，也不追溯否定 2026-07-06
  用户授权并已完成的 Gemini repaired v0.3 E0-E6 third-model run；后续
  Kimi/Devstral repaired run 仍需要新的明确授权和 preflight。

## 2026-07-06 快速状态增量

- 主线 A 已完成。coverage-contestation prompt robustness 路线保持主 prompt
  `evp8_visible_evidence_merge_gate_v0_2` 保持不动；新增独立 frozen prompt
  `prompts/evp8_coverage_contestation_merge_gate_v0_1.md`，用于测试模型是否能
  主动挑战 visible-test-only accept 和 coverage 不足。
- 新增 prompt 修改记录：
  `docs/experiments/evp8_coverage_contestation_prompt_change_record_v0_1.md`，
  明确新 prompt 是独立 ablation，不替换主 prompt，也不能把 escalation 当作
  strict correction。
- 当前 98 cohort coverage-contestation no-API check-only 已通过：
  `docs/experiments/evp8_coverage_contestation_current98_check_only_v0_1.md` 和
  `data/protocols/evp8_coverage_contestation_current98_check_only_v0_1.json`。
  它构造 98 个 E6 no-verdict packets；Qwen、DeepSeek、Gemini 已按该边界
  各完成 98 条 API review，合计 294 calls，三模型均为 98/98 parse-valid。
- 当前 98 cohort coverage-contestation 分析已通过：
  `docs/experiments/evp8_coverage_contestation_current98_analysis_v0_1.md` 和
  `data/reviews/evp8_coverage_contestation_current98_analysis_v0_1.json`。
  结果为三模型 repeated false accept 均为 0，但 correct recall 代价极大：
  DeepSeek/Gemini 为 0/21，Qwen 为 2/21。该结果只能写成
  prompt-sensitivity / conservative triage evidence，不能写成 autonomous
  semantic verification improvement。
- APSEC rewrite 已新增 Section 5.4 coverage-contestation 小节，明确它不替代
  repaired v0.3 三模型主结果，也不支持“LLM 显著优于 rule-only”的 claim。
- 新增 hard-negative stress-test packet：
  `docs/experiments/evp8_hardneg_stress_test_packet_v0_1.md` 和
  `data/protocols/evp8_hardneg_stress_test_packet_v0_1.json`。该 packet 中的
  26/30、2/3、Luigi 下一步已经是历史状态；2026-07-06 主线 B 已改用 Scrapy_1
  source probe 修复第三项目 gate。
- 主线 B hard-negative readiness gate 已通过：
  `docs/experiments/evp8_realistic_hardneg_combined_generation_gate_with_scrapy_source_probe_v0_1.md`
  和
  `data/protocols/evp8_realistic_hardneg_combined_generation_gate_with_scrapy_source_probe_v0_1.json`
  记录 104 candidates、31 visible-pass/hidden-fail cases、3 projects
  (`PySnooper`, `cookiecutter`, `scrapy`)，`ready_for_verifier_api=true`。
  其中 Scrapy 第三项目来自 curated no-API stress-source partial variants，不得
  写成纯 agent-generated realistic cohort。后续 verifier matrix 如继续运行，必须
  标注为 hard-negative stress-test 条件。
- 主线 B verifier 前置 cohort/headroom 已完成：
  `docs/experiments/evp8_realistic_hardneg_stress_cohort_v0_1.md` 和
  `data/protocols/evp8_realistic_hardneg_stress_cohort_v0_1.json` 记录 31 个
  separated hard-negative stress cases。rule-only visible-tool baseline 为
  31/31 accept，且 31/31 都是 hidden-fail false accepts，false accept rate
  `1.0`。这说明 stress-test verifier matrix 有明确 headroom；下一步可在
  ignored `outputs/evp8_realistic_hardneg_stress_cohort_v0_1/model_visible_packets.jsonl`
  上做 verifier preflight/API，但论文口径仍是 stress-test evidence。
- 主线 B 31-case verifier matrix no-API preflight 已完成：
  `docs/experiments/evp8_realistic_hardneg_stress_matrix_preflight_v0_1.md` 和
  `data/protocols/evp8_realistic_hardneg_stress_matrix_preflight_v0_1.json`。
  状态为 `passed_with_no_verdict_blocked`。有效 ready API 矩阵只包含
  `current_merge_gate` 与 `coverage_contestation` 两个 prompt 条件，覆盖
  Qwen / DeepSeek / Gemini，共 `186` calls。`e6_no_verdict` 在该 stress cohort
  上被阻断，因为 packets 中没有 verdict-like 字段可移除；不得写成已 ready 或
  已执行的独立 ablation。preflight 同时确认 tracked 输出不保存 patch diff、
  rendered prompt 或 raw responses。
- 主线 B 31-case verifier matrix API run 与分析已完成：
  `docs/experiments/evp8_realistic_hardneg_stress_matrix_analysis_v0_1.md` 和
  `data/reviews/evp8_realistic_hardneg_stress_matrix_analysis_v0_1.json`。
  6 个 model-condition runs 均通过，合计 186 parse-valid reviews；Gemini
  `current_merge_gate` 有 3 条 provider 空响应被 `--retry-invalid` 重试修复。
  `current_merge_gate` aggregate repeated false accept 为 62/93 (`66.67%`)，
  safe escalation 为 31/93 (`33.33%`)；`coverage_contestation` repeated false
  accept 降为 12/93 (`12.90%`)，safe escalation 升为 81/93 (`87.10%`)。
  两个条件 strict reject 均为 0，因此该结果支持 conservative triage /
  false-accept reduction，不支持 strict correction，也不定义 correct recall。
- APSEC technical-track Markdown rewrite 已纳入 stress matrix 结果：
  `docs/paper/apsec_technical_track_rewrite_v0_1.md` 的 abstract、contribution、
  experiment design、Results 5.5、Discussion、Threats 和 Conclusion 均已更新。
  旧的 “realistic hard-negative branch 未过 readiness gate” 叙述已移除；新稿把
  31-case stress matrix 写成 bounded stress-test supplement，并明确 scrapy cases
  来自 curated no-API stress-source partial variants。APSEC audit 已通过：
  `docs/paper/apsec_manuscript_rewrite_audit_v0_1.md` /
  `data/reviews/apsec_manuscript_rewrite_audit_v0_1.json`。
- APSEC IEEEtran/BibTeX/page-budget/PDF 包已同步到最新 Markdown 主稿：
  `scripts/write_apsec_ieeetran_package.py --compile` 会重新生成
  `docs/paper/apsec_ieeetran_draft.tex`、`docs/paper/apsec_references.bib`、
  page-budget audit，并执行 pdflatex/bibtex/pdflatex/pdflatex。本地编译 PDF 为
  7 页，仍低于 APSEC technical track 10 页边界；latest log 无 undefined
  references，记录 0 个 overfull hbox 和 11 个 underfull hbox。新增
  `scripts/audit_apsec_pdf_layout.py`、`docs/paper/apsec_pdf_layout_audit_v0_1.md`
  和 `data/reviews/apsec_pdf_layout_audit_v0_1.json`，确认 7 页 PDF 均可渲染、
  页面非空、author block 匿名、旧 APSEC gate-failed 文案未残留。当前包仍是
  draft package，不是 final submission PDF。
- CCF-C manuscript generation chain 已同步 stress matrix 结果：
  `scripts/write_final_manuscript_claim_map.py` 现在读取
  `data/reviews/evp8_realistic_hardneg_stress_matrix_analysis_v0_1.json`，
  并重新生成 `docs/paper/ccfc_manuscript_rewrite_v0_1.md`、
  `docs/paper/final_manuscript_claim_map_v0_1.md` 和
  `data/reviews/final_manuscript_claim_map_v0_1.json`。CCF-C Fig. 2--3 已重画，
  不再出现旧的 “realistic gate is source acquisition / three-project realistic
  verifier readiness” 文案。`scripts/audit_ccfc_manuscript_v0_3.py` 已把旧
  gate-failed 当前结论列为 forbidden wording，并通过 reviewer-style audit。
- 新增 Gemini repaired EVP-8 v0.3 E0-E6 third-model run：
  strict preflight、smoke/full check-only、smoke API、full API 和
  label-conditioned analysis 均通过。full API 为 686/686 parse-valid，估算成本
  USD `0.638910370`；Gemini E6 为 25 accepts、20 correct accepts、
  5 false accepts、accepted precision `80.00%`、correct recall `95.24%`、
  false accept rate `6.49%`、escalation rate `0.00%`。
- APSEC/CCF-C 正文现在使用 Qwen + DeepSeek + Gemini three-model repaired
  v0.3 主结果。当前结论是 bounded evidence-conditioned risk behavior，不是
  broad-LLM superiority，也不是 autonomous correctness verifier。
- 新增 EVP-8 prompt-setting audit：
  `docs/experiments/evp8_prompt_setting_audit_v0_1.md` 和
  `data/reviews/evp8_prompt_setting_audit_v0_1.json`。结论是：当前结果不佳不能
  归因为 prompt 实现 bug、schema 错误或 hidden-label leakage；如果目标是工具外
  语义 verifier，则 visible-only merge-gate prompt 和 E6 deterministic visible
  summary 本身会把结果限制为 evidence-conditioned policy behavior。
- 新增 Gemini run packet：
  `docs/experiments/evp8_gemini_repaired_v0_3_run_packet.md` 和
  `data/protocols/evp8_gemini_repaired_v0_3_run_packet.json`，状态为 `passed`。
- 新增 sanitized false-accept case analysis：
  `docs/paper/apsec_false_accept_case_analysis_v0_2.md` 和
  `data/reviews/apsec_false_accept_case_analysis_v0_2.json`。它记录 Qwen、
  DeepSeek、Gemini 的 E6 false accepts candidate-level category 信息，但不保存
  raw response text、rendered prompts、patch diffs、full rationale text 或凭证。
- APSEC IEEEtran/BibTeX/page-budget 草案包：
  `docs/paper/apsec_ieeetran_draft.tex`、
  `docs/paper/apsec_references.bib`、
  `docs/paper/apsec_page_budget_audit_v0_1.md` 和
  `data/reviews/apsec_page_budget_audit_v0_1.json`。2026-07-07
  camera-facing cleanup 已把主文表格从 14 张压缩到 6 张，删除机械表题、重复图题、
  conclusion 内部 package note 和原始长浮点数，并把 false-accept analysis 改为
  正文 case-group 表。后续 APSEC reference/method-detail pass 已把 references
  从 11 条扩到 24 条结构化 BibTeX，简化 Table II，新增 Implementation and
  Artifact 小节，统一 RQ3，删除 APSEC 主文 Figure 3。2026-07-08 后续一致性
  pass 又补充 BugsInPy 正式引用，将 references 提升到 25 条，删除 main text
  中具体 cost 数值，弱化 E4/E5 主文 claim，并把 Figure 2 改为三模型主线图。
  页数估算 7.05 页，状态 `passed`；实际 IEEEtran/BibTeX 编译 PDF 为 7 页，
  latest log 无 undefined references、0 个 overfull hbox、11 个 underfull hbox。
  当前仍不是最终投稿 PDF；下一步需要 final human bibliographic review 和最终
  venue-format polish。
- 当前剩余 APSEC 风险已经从“主结果单模型/两模型不足”转为：
  cohort 小、三模型仍非 broad-model、rule-only baseline 很强、false accepts
  仍集中在 partial/regression negatives、以及最终 double-blind、reference 和
  BibTeX 字段需要人工级格式检查。

## 2026-07-05 快速状态增量

- 新增 APSEC technical-track Markdown rewrite：
  `docs/paper/apsec_technical_track_rewrite_v0_1.md`。它把当前 CCF-C 稳定稿
  重写为 APSEC-style technical research paper 结构，包含 Abstract、
  Introduction、Background、Protocol、Experimental Design、Results、
  Discussion、Threats 和 Conclusion。
- 新增 APSEC rewrite generator：
  `scripts/write_apsec_manuscript_rewrite.py`。它只读取 tracked claim map，
  不调用 API、不读取 raw model responses、不把 majority-vote 或单独
  E0/no-tool deterministic verifier 写成完成结果。
- 新增 APSEC rewrite audit：
  `docs/paper/apsec_manuscript_rewrite_audit_v0_1.md` 和
  `data/reviews/apsec_manuscript_rewrite_audit_v0_1.json`，状态为 `passed`。
- 当前下一步不是扩实验，而是 final formatting：APSEC IEEEtran/BibTeX/page
  budget 草案包已经生成，仍需 PDF 编译、图表宽度、双盲措辞和 reference style
  的人工级检查。
- 2026-07-05 APSEC reviewer-risk repair 是历史阶段：当时稿件明确承认
  paper-facing main result remains single-model/two-model，并将 realistic
  hard-negative branch 作为 source-acquisition boundary。该阶段提出的第三个
  repaired E0-E6 主模型和 raw-output-free case-level analysis 已在 2026-07-06
  完成。
- 当前 Git 同步状态：2026-07-05 继续执行后 GitHub push 已恢复成功，远端包含
  APSEC reviewer-risk repair。
- 新增 APSEC false-accept case-analysis feasibility audit，状态为
  `blocked_missing_candidate_level_decision_export`：当前 no-raw summaries 只支持
  4 个 E6 false accepts 的 aggregate anatomy（3 partial fixes + 1 regression
  patch），不支持具体 candidate-level case table。
- 新增 DeepSeek repaired EVP-8 v0.3 run：strict preflight、smoke/full
  check-only、smoke API、full API 和 label-conditioned analysis 均通过。full API
  为 686/686 parse-valid，估算成本 USD `0.434221524`；DeepSeek E6 为
  21 accepts、17 correct accepts、4 false accepts、accepted precision `80.95%`、
  correct recall `80.95%`、false accept rate `5.19%`、escalation rate `4.08%`。
- 2026-07-05 阶段 APSEC rewrite 使用 Qwen + DeepSeek two-model repaired main
  result，并在正文中显式区分 repaired v0.3 E0-E6 主表和独立 E6 verdict-field
  ablation package，避免 DeepSeek E6 数字来源混淆。当前 2026-07-06 版本已升级
  为 Qwen + DeepSeek + Gemini three-model repaired main result。
- 新增 DeepSeek run packet：
  `docs/experiments/evp8_deepseek_repaired_v0_3_run_packet.md` 和
  `data/protocols/evp8_deepseek_repaired_v0_3_run_packet.json`，状态为
  `passed`。
- 当前剩余 APSEC 实验缺口中的第三个 repaired E0-E6 主模型和 raw-output-free
  candidate-level false-accept case export 已在 2026-07-06 完成。后续如再扩模型，
  仍必须另起计划和 preflight。
- 当前 Git 同步状态：本地 commit `Add DeepSeek repaired EVP-8 results` 已完成；
  GitHub push 连续三次失败，原因是 HTTPS/GitHub 443 连接 reset/timeout；当前
  分支相对 `origin/evp8-v03-qwen-main-exp` 为 `[ahead 1]`。

## 2026-07-04 快速状态增量

- 新增 CCF-C citation support bank：
  `docs/paper/ccfc_citation_support_bank_v0_1.md`。它按 claim segment 组织
  introduction、related work、method、discussion 和 threats 的引用支撑，并明确
  引用不能支撑 autonomous correctness verification 或 LLM superiority over
  deterministic baselines。
- 新增 CCF-C baseline feasibility audit：
  `docs/paper/ccfc_baseline_feasibility_audit_v0_1.md` 和
  `data/reviews/ccfc_baseline_feasibility_audit_v0_1.json`，由
  `scripts/audit_ccfc_baseline_feasibility.py` 生成。
- 当前可写入论文的 baseline 边界：
  - deterministic reference policies：always-escalate、always-reject、
    always-accept；
  - expected reference policy：uniform random three-way expected policy，
    只按 aggregate label totals 计算期望值，不是随机模拟或完成 verifier；
  - observed model condition：Qwen E0 no-tool/no-executable-evidence behavior；
  - completed deterministic baseline：rule-only visible-tool；
  - completed E6 model conditions：Qwen E6-full 和 DeepSeek E6-full；
  - 不可写成已完成：majority-vote across models、单独 E0/no-tool deterministic
    verifier。majority-vote 需要 candidate-level raw-output-free decision
    export/audit；当前 tracked summaries 不足以计算。
- 已完成 v0.3 正文集成：
  `docs/paper/ccfc_manuscript_rewrite_v0_1.md` 现在包含 citation-keyed related
  work、baseline policy boundary、Phase A Wilson 95% CI summary、
  tool-contestation opportunity-set Wilson 95% CI、Methods/Results/Discussion/
  Threats 结构压缩和 reference support records。
- 新增 reviewer-style manuscript audit：
  `docs/paper/ccfc_manuscript_v0_3_reviewer_audit.md` 和
  `data/reviews/ccfc_manuscript_v0_3_reviewer_audit.json`，状态为 `passed`。
- 下一步论文工作应转向 final formatting：把 citation keys 转成目标会议模板的
  BibTeX/LaTeX 引用，并检查图表编号、表格宽度和最终模板格式。

## 2026-07-03 快速状态增量

- 用户目标已明确：稳定写完，目标 CCF-C；核心不是继续冲更高档次，而是确认
  实验设置没有污染现有结果。
- 新增 final experiment-setting validity audit：
  `docs/experiments/final_experiment_setting_validity_audit_v0_1.md` 和
  `data/reviews/final_experiment_setting_validity_audit_v0_1.json`。
- 审计状态：`passed_with_bounded_claims`。
- 允许的结论：当前结果可作为真实 bounded evidence，支撑
  evidence-conditioned risk behavior。
- 禁止的结论：LLM 是 reliable autonomous patch correctness verifier，或
  escalation 等同于 strict correction。
- 新增 final manuscript claim map：
  `docs/paper/final_manuscript_claim_map_v0_1.md` 和
  `data/reviews/final_manuscript_claim_map_v0_1.json`。其状态为 `passed`，
  将 supported claims、forbidden claims、terminology ledger 和 figure plan
  绑定到最终 validity boundary。
- 新增稳定 CCF-C 正文重写稿：
  `docs/paper/ccfc_manuscript_rewrite_v0_1.md`。该稿把结果写成
  evidence-conditioned risk behavior，而不是 autonomous correctness
  verification。
- 新增 CCF-C 专用 Python 图集：
  `docs/figures/ccfc/ccfc_fig1_protocol.*`、
  `docs/figures/ccfc/ccfc_fig2_decision_patterns.*`、
  `docs/figures/ccfc/ccfc_fig3_claim_boundary.*`，每张图均输出 PDF/SVG/PNG。
- 新增 CCF-C figure placement audit：
  `docs/paper/ccfc_figure_placement_audit_v0_1.md` 和
  `data/reviews/ccfc_figure_placement_audit_v0_1.json`，状态为 `passed`。
- 新增附件评审响应文档：
  `docs/paper/ccfc_revision_response_v0_2.md`。它逐项记录“审计报告化”、
  早期无效设置不应作为论文内容、accept-aware 结果应成为主证据、baseline 缺口、
  related-work 缺口和 realistic branch 边界等问题的处理状态。
- 已完成实验逻辑二次清理：当前论文包不再把早期无效设置作为 RQ、主结果或
  解释性段落；当前主证据链从 repaired accept-aware label-conditioned metrics
  开始，并已升级为 Qwen/DeepSeek/Gemini 三模型主结果，再通过 E6
  rule-only/no-verdict ablation 与 tool-contestation 继续收束。
- 当前本轮写作/配图/正文插图目标已完成；若继续投稿准备，下一步应优先补 verified
  related-work citations 和缺失 baseline，或在目标模板确定后整合到 LaTeX/Word
  投稿格式，而不是继续无边界实验或 API。

## 2026-07-02 快速状态增量

- 根目录研究课题评估后的论文定位：当前结果适合写成 evidence visibility /
  risk behavior / software quality empirical study，不适合写成 reliable
  autonomous patch correctness verifier。
- 若要明显提升论文档次，下一步不是继续堆模型或 prompt 调参，而是补
  realistic hard-negative verifier-readiness gate：
  - 至少 30 个 validated visible-pass/hidden-fail cases；
  - 至少 3 个 projects；
  - 每个 case 必须满足 visible tests pass、hidden evaluator fail；
  - gate 未通过前不得运行 Qwen/DeepSeek verifier API。
- 若 gate 通过，后续只允许另行计划最小 Qwen/DeepSeek 对照实验，比较
  tool-only、with-verdict、evidence-only 和 tool-contestation，并分开报告
  strict correction、safe handling、correct recall 和 escalation rate。
- 若 gate 仍失败，fresh realistic branch 继续作为 two-project
  source-acquisition / gate-readiness negative result，不升级为主实验。
- 本地已新增 no-API uplift packet：
  `docs/experiments/evp8_realistic_hardneg_uplift_packet_v0_1.md` 和
  `data/protocols/evp8_realistic_hardneg_uplift_packet_v0_1.json`。它记录当前
  gate 状态为 `blocked_needs_more_cases_and_third_project`：26/30
  visible-pass/hidden-fail cases，2/3 projects，`ready_for_verifier_api=false`。
- 本地已新增 no-API third-project source-selection packet：
  `docs/experiments/evp8_realistic_hardneg_third_project_source_selection_packet_v0_1.md`
  和
  `data/protocols/evp8_realistic_hardneg_third_project_source_selection_packet_v0_1.json`。
  packet 选择 `luigi`，任务为 `bugsinpy_luigi_3` 和
  `bugsinpy_luigi_4`；它不授权 generation API 或 verifier API，只把下一步
  收敛为 no-API Luigi source-acquisition/materialization protocol。
- GitHub 同步已完成：远端分支 `evp8-v03-qwen-main-exp` 至少包含
  `f3c6238 Record paper uplift sync completion`，当前
  `git status --short --branch` 显示本地相对
  `origin/evp8-v03-qwen-main-exp` 无 ahead/behind。

## 2026-06-30 快速状态增量

- 当前分支仍为 `evp8-v03-qwen-main-exp`，精确同步状态以
  `git status --short --branch` 为准。
- `EVP-8-HARD tool-contestation` 已完成 Qwen 和 DeepSeek：
  - cohort: 47 candidates；
  - prompt: `prompts/evp8_tool_contestation_merge_gate_v0_1.md`；
  - runner: `scripts/run_evp8_hard_tool_contestation.py`；
  - result report:
    `docs/experiments/evp8_hard_tool_contestation_result_v0_1.md`；
  - combined audit:
    `data/protocols/evp8_hard_tool_contestation_result_audit_v0_1.json`。
- 核心结果：Qwen 在 9 个 repeated false accepts 中 8 个转为
  escalation、1 个仍 accept；DeepSeek 9/9 转为 escalation；两者 strict reject
  均为 0。
- 论文解释边界：该结果支持 tool-evidence reliability / risk-triage claim，
  不支持 autonomous merge gate 或 LLM strict correctness verification。
- 注意：新增 `data/` 结果受 `.gitignore` 默认规则影响，提交时必须只对本轮
  需要追踪的 JSON/JSONL 结果使用精确 `git add -f`。

## 当前同步状态

当前状态：

- 分支：`evp8-v03-qwen-main-exp`
- 远端：`origin/evp8-v03-qwen-main-exp`
- 最新本地语义锚点：以 `git log -1 --oneline` 为准，语义应为
  `Complete CCF-C manuscript audit pass`。
- 当前远端同步状态：`git status --short --branch` 显示本地相对
  `origin/evp8-v03-qwen-main-exp` 为 `[ahead 2]`；本轮 `git push` 因
  GitHub HTTPS 连接 reset 未完成。远端已包含上一提交 `595702c Add CCF-C
  citation and baseline support`，但尚未包含 v0.3 正文集成提交和五步补齐提交。
- 同步判断：以 `git status --short --branch`、`git log -1 --oneline` 和
  `origin/evp8-v03-qwen-main-exp` 为准；不得再用旧 `origin/main` 段落判断
  当前分支是否同步。
- 当前执行入口：CCF-C 稿件包后续审稿/格式整合。Manuscript claim map /
  threats-to-validity 收束、正文 v0.3、Fig. 1--3、正文内配图放置、
  `docs/paper/ccfc_revision_response_v0_2.md` 和
  `docs/paper/ccfc_manuscript_v0_3_reviewer_audit.md` 均已完成。当前实验逻辑以
  Qwen v0.3 accept-aware label-conditioned metrics 为主证据起点，且正文已包含
  citation-keyed related work、baseline policy boundary、Phase A Wilson 95% CI
  summary、tool-contestation opportunity-set CI 和 Methods/Results/Discussion/
  Threats 结构。
  Luigi
  source-acquisition/materialization protocol 已降级为可选未来工作，不再是稳妥
  CCF-C 路线的当前 blocker。

以下历史同步锚点只保留为旧 EVP-8 主线审计记录，不再代表当前分支状态：

- 分支：当前工作分支为 `evp8-v03-qwen-main-exp`；上一诊断分支为
  `evp8-accept-aware-retest`；历史主线为 `main`
- 历史远端：`origin/main`
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
- 本轮新增 accept-aware EVP-8 v0.2 DeepSeek/Qwen retest：
  - v0.1 的 `0 accept` 与实验设置有关：full-run 可见测试/工具 evidence
    多为 placeholder/not-run，且 E6 deterministic gate 缺少 accept 分支；
  - v0.2 使用既有 sanitized EVP-7 visible test/tool artifacts，E6 deterministic
    branch 在 no-API check-only 中为 `accept:25, reject:73`；
  - DeepSeek V4 Pro json-mode full rerun 通过：686/686 parse-valid，总
    decision counts 为 `accept:80, escalate:287, reject:319`，E6 为
    `accept:23, reject:75`；
  - Qwen3.7 Max json-mode full rerun 通过：686/686 parse-valid，总 decision
    counts 为 `accept:82, escalate:238, reject:366`，E6 为
    `accept:24, reject:74`；
  - 该结果只支持 two-model accept-aware retest 的描述性结论，不覆盖或替代
    frozen EVP-8 v0.1 five-model synthesis。
- 本轮新增 EVP-8 v0.3 Qwen-first main-experiment batch：
  - v0.3 复用冻结 prompt v0.2 文本和 accept-aware visible evidence
    construction，但作为 Qwen-first 主实验第一批结果重新冻结 protocol/config/
    packet；
  - Qwen-only strict preflight passed，仅验证 `QWEN_API_KEY` presence；
  - smoke check-only 和 full check-only 均 passed，full check-only 为
    686 packets、0 boundary/schema errors，E6 deterministic branch 为
    `accept:25, reject:73`；
  - Qwen smoke passed：35/35 parse-valid，decision counts 为
    `accept:16, escalate:15, reject:4`，estimated cost CNY `2.130804`；
  - Qwen full passed：686/686 parse-valid，actual model id
    `qwen3.7-max=686`，decision counts 为
    `accept:86, escalate:230, reject:370`，estimated cost CNY `40.88994`；
  - per-level full counts:
    E0 `escalate:74, reject:24`；E1 `escalate:74, reject:24`；
    E2 `escalate:73, reject:25`；E3 `accept:20, escalate:4, reject:74`；
    E4 `accept:21, escalate:2, reject:75`；
    E5 `accept:21, escalate:3, reject:74`；E6 `accept:24, reject:74`；
  - raw-output-free result audit and synthesis 均为 `passed`；
  - 该结果只支持 v0.3 Qwen-first 描述性 decision-pattern reporting，不支持
    五模型最终主实验结论、DeepSeek/Qwen 对比、LLM superiority 或最终
    evidence-level effectiveness claim。
- 本轮新增 EVP-8 v0.3 Qwen label-conditioned analysis：
  - 分析脚本为 `scripts/analyze_evp8_qwen_first_label_conditioned.py`；
  - raw-output-free JSON/Markdown 汇总为
    `data/reviews/evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.json`
    和
    `docs/experiments/evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.md`；
  - hidden evaluator labels 只在执行后 join，不进入 prompt 或 model-visible
    packet；决策只解析 `raw_response_text` 的最终 JSON，不使用
    `reasoning_content`；
  - correct-patch recall：E0/E1/E2 为 0，E3 为 17/21，E4/E5 为
    18/21，E6 为 20/21；
  - false accept：E3/E4/E5 为 3/77，E6 为 4/77；E6 accepted precision 为
    20/24；
  - 因此可以说 v0.3 Qwen 随证据量增加更能 accept 正确补丁，但不能忽略
    E3-E6 同时出现的 partial/regression false accepts。
- 本轮新增 EVP-8 LLM-vs-tool headroom / E6 ablation 计划：
  - 计划文档为
    `docs/experiments/evp8_llm_tool_headroom_ablation_plan_20260629.md`；
  - 下一步不直接跑模型，而是先做 no-API headroom audit，判断 deterministic
    tool-only baseline 是否有足够错误可供 LLM 改正；
  - 后续 ablation 的核心比较是 `rule-only`、当前 `E6-full` 和未来
    `E6-no-verdict`；
  - 该计划不授权 API 调用、不修改 prompt、不修改 candidate set。
- 本轮执行 EVP-8 Qwen/DeepSeek `E6-no-verdict` ablation：
  - Phase 0 headroom audit 已通过：
    `data/protocols/evp8_tool_headroom_audit_v0_1.json` 和
    `docs/experiments/evp8_tool_headroom_audit_v0_1.md`；
  - rule-only baseline 为 `accept=25, reject=73`，包含 5 个 false accepts
    和 1 个 false reject，opportunity-set size = 6；
  - no-verdict packet/check-only gate 已通过：
    `data/protocols/evp8_e6_no_verdict_ablation_smoke_check_only_v0_1.json`
    和
    `data/protocols/evp8_e6_no_verdict_ablation_full_check_only_v0_1.json`；
  - Qwen `E6-no-verdict` full run 通过：98/98 parse-valid，decision counts 为
    `accept=23, reject=74, escalate=1`，estimated cost CNY `5.778804`；
  - DeepSeek `E6-no-verdict` full run 通过：98/98 parse-valid，decision counts
    为 `accept=11, reject=73, escalate=14`，estimated cost USD
    `0.079322105`；
  - comparison summary 为
    `data/reviews/evp8_e6_no_verdict_ablation_comparison.json` 和
    `docs/experiments/evp8_e6_no_verdict_ablation_comparison.md`；
  - 主要结论：Qwen 去掉 verdict 后几乎保持 E6-full 模式，仍有 4/77
    false accepts；DeepSeek 去掉 verdict 后 false accept 降为 0，但 correct
    recall 降至 11/21，并产生 14 个 escalations；
  - 该结果支持 model-dependent risk-control / triage 解释，不支持自动 merge
    gate claim。
- 本轮新增 EVP-8 hard-case extension 计划：
  - 计划文档为
    `docs/experiments/evp8_hard_case_extension_plan_20260629.md`；
  - 目标是提升外部有效性和 opportunity-set 数量，而不是继续堆模型；
  - immediate next step 是 no-API confidence intervals、6-case opportunity
    analysis 和 utility/risk-policy table；
  - 后续才构建单独的 `EVP-8-HARD` 30-50 candidate hard-case cohort；
  - 任何 hard-case Qwen/DeepSeek API run 都需要先通过 no-API gates 和用户
    再授权。
- 本轮已完成 hard-case extension Phase A：
  - 脚本为 `scripts/analyze_evp8_phase_a_paper_ready.py`；
  - 输出为 `data/reviews/evp8_phase_a_paper_ready_analysis.json` 和
    `docs/experiments/evp8_phase_a_paper_ready_analysis.md`；
  - Wilson CI 显示 opportunity-set rates 的区间很宽，原因是当前只有 6 个
    opportunity cases；
  - case table 明确 5 个 false accepts 的 missing visible evidence 主要是
    regression/P2P/edge-case 覆盖不足；
  - utility table 显示 DeepSeek `E6-no-verdict` 只有在 false accept 成本显著
    高于 escalation 成本时最有吸引力。
- 本轮已完成 hard-case extension Phase B source inventory：
  - 脚本为 `scripts/inventory_evp8_hard_case_sources.py`；
  - 输出为 `data/protocols/evp8_hard_case_source_inventory_v0_1.json` 和
    `docs/experiments/evp8_hard_case_source_inventory_v0_1.md`；
  - 盘点 34 个非 raw 本地 candidate source files，检测到旧 98-candidate
    controlled cohort 已有 6 个 rule-only E6 opportunity cases；
  - 非 promoted 候选记录为 68 条，去重后 49 条；其中 eligible hard negatives
    为 48 条，去重后 20 条；
  - AI/agent candidate records 为 38 条，去重后 19 条；其中 eligible hard
    negatives 为 23 条，去重后 13 条；
  - 该 inventory 不生成 `EVP-8-HARD` manifest，不授权 API；下一步必须先做
    no-API candidate curation 和 hard-case tool-only baseline。
- 本轮已完成 `EVP-8-HARD` no-API candidate draft 和 baseline gate：
  - 脚本为 `scripts/build_evp8_hard_candidate_draft.py`；
  - 输出为 `data/patches/evp8_hard_evaluator_manifest_v0_1.jsonl`、
    `data/evidence/evp8_hard_model_visible_seed_v0_1.jsonl`、
    `data/baselines/evp8_hard_tool_only_baseline_v0_1.jsonl`、
    `data/protocols/evp8_hard_candidate_draft_v0_1.json` 和
    `docs/experiments/evp8_hard_candidate_draft_v0_1.md`；
  - draft 包含 35 条 applied candidates、5 个 tasks、1 个 project；
  - candidate labels 为 correct=8、agent_plausible_wrong=10、partial=7、
    irrelevant_or_noop=10；
  - model-visible seed 已通过 evaluator-label leakage 检查；
  - 第一版 draft gate 的 API readiness 为 `blocked`，原因是 nontrivial hard
    negatives 只有 17 条、visible test outcomes 为 0、actionable
    false-accept/false-reject headroom 为 0；
  - 该第一版 baseline 因只有 visible test hints 而没有 visible outcome，对
    35 条全部 `escalate`；随后已由 visible-test runner 更新。
- 本轮已运行 `EVP-8-HARD` no-API visible-test runner：
  - 脚本为 `scripts/run_evp8_hard_visible_tests.py`；
  - 输出为 `data/evidence/evp8_hard_visible_test_outcomes_v0_1.jsonl`、
    `data/protocols/evp8_hard_visible_test_outcome_summary_v0_1.json` 和
    `docs/experiments/evp8_hard_visible_test_outcomes_v0_1.md`；
  - dry-run 显示 9 条 planned、26 条 blocked；真实 run 后 9 条为 error、
    26 条仍 blocked；
  - error 主要来自 HTTPie 测试环境/collection 问题，例如缺少
    `pytest_httpbin` 或当前 `requests.compat` 不含旧版兼容符号；
  - 重建 hard-case baseline 后 decision counts 为 `reject=9, escalate=26`；
  - false accepts = 0、false rejects = 0、actionable false-accept/false-reject
    headroom = 0；API readiness 仍为 `blocked`。
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
  - EVP-8 accept-aware v0.2 retest：DeepSeek 和 Qwen 各 98 candidates x 7
    evidence levels = 686 records，均为 686/686 parse-valid；该 retest 只报告
    accept-aware two-model patterns，不是新五模型最终结果；
  - EVP-8 v0.3 Qwen-first main-experiment batch：Qwen3.7 Max 覆盖
    98 candidates x 7 evidence levels = 686 records，686/686 parse-valid；
    该结果只报告 Qwen-first patterns，后续 DeepSeek/Kimi/Devstral/Gemini
    需要另行授权；
  - EVP-8 v0.3 Qwen label-conditioned analysis：正确补丁 21、非正确补丁
    77；E6 correct recall = 95.24%，accepted precision = 83.33%，false
    accept rate = 5.19%；该分析只支持 Qwen v0.3 frozen batch 的描述性
    label-conditioned 结论；
  - EVP-8 LLM-vs-tool headroom / E6 ablation：Phase 0、Qwen/DeepSeek
    `E6-no-verdict` full run 和 rule-only / E6-full / E6-no-verdict comparison
    均已完成；当前结果显示 Qwen 不明显改正工具 false accepts，DeepSeek 用
    escalation 消除 false accepts 但显著牺牲 correct recall；
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

- `docs/experiments/evp8_hard_case_extension_plan_20260629.md`

当前默认下一步：

1. 基于
   `docs/experiments/evp8_phase_a_paper_ready_analysis.md` 和
   `docs/experiments/evp8_hard_case_source_inventory_v0_1.md`、
   `docs/experiments/evp8_hard_candidate_draft_v0_1.md` 写论文结果/局限段；
2. 不运行 API；先补 hard-case cohort：
   - 至少再增加 3 条 validated non-control hard negatives；
   - 修复或重建 hard-case visible-test execution coverage，使 visible tests
     能产生 passed/failed 而不是 environment/collection error；
   - 重新生成 tool-only baseline；
3. 若重新生成后 actionable false-accept/false-reject headroom 少于 10，则继续
   停止 API 并报告 headroom 不足；
4. 明确 claim boundary：Qwen 结果显示 verdict removal 对其影响小，但不修复
   4 个工具 false accepts；DeepSeek 结果显示更强风险控制，但代价是 correct
   recall 大幅下降；
5. 后续若要证明实用价值，必须新增 hard-case / real agent patch cohort 或做人类
   review 成本/风险函数，不应继续在同一 easy cohort 上堆模型；
6. 任何新增模型、重复 API 或 candidate-set 扩展都需要新的计划和用户授权。

以下条目保留为历史/备用路线，不再覆盖当前默认下一步：

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
   - 后续不应继续补模型或改协议；旧路线曾收敛为 paper/table/artifact freeze，
     但 2026-06-29 起该路线暂停为备用，当前优先 headroom audit / E6
     ablation；
   - 当前成本审计：
     `python scripts\summarize_evp8_cost_accounting.py --check` 已通过；
     blocked attempts 是成本/执行风险证据，不是 valid model-result records；
   - smoke 之后的后续顺序已经写入 canonical EVP-8 plan：
     two-model smoke synthesis -> 独立 no-API full-run packet -> DeepSeek
     686-call full run -> DeepSeek audit passed -> Qwen 686-call full run -> Qwen
     audit passed -> two-model first-batch synthesis passed -> later-model execution packet
     -> Kimi/Devstral/Gemini 补跑 -> five-model synthesis -> paper/artifact
     freeze；当前该链路已完成到 five-model synthesis passed。旧 SQJ no-API
     paper route 保留为备用，当前默认下一步已切换为 LLM-vs-tool headroom
     audit；
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
- `data/protocols/evp8_protocol_v0_2.json`、
  `prompts/evp8_visible_evidence_merge_gate_v0_2.md`、
  `configs/evp8_deepseek_qwen_accept_v0_2.example.json`：
  accept-aware retest 的 protocol/prompt/config；使用 existing sanitized
  EVP-7 visible artifacts、JSON mode request controls 和 DeepSeek
  thinking-disabled request control，不覆盖 v0.1。
- `data/protocols/evp8_deepseek_qwen_accept_v0_2_prompt_v0_2_full_check_only.json`、
  `data/protocols/evp8_deepseek_qwen_accept_v0_2_prompt_v0_2_full_run_packet.json`：
  accept-aware retest 的 no-API check-only 与 full-run packet；check-only
  `passed`，E6 deterministic branch 为 `accept:25, reject:73`。
- `data/protocols/evp8_deepseek_qwen_accept_v0_2_prompt_v0_2_full_result_audit.json`、
  `data/protocols/evp8_deepseek_qwen_accept_v0_2_prompt_v0_2_full_synthesis.json`：
  accept-aware retest 的 raw-output-free result audit 和 two-model synthesis；
  当前均为 `passed`，只支持 DeepSeek/Qwen v0.2 描述性结果。
- `data/reviews/evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.json`、
  `docs/experiments/evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.md`：
  EVP-8 v0.3 Qwen-first full run 的 label-conditioned raw-output-free 分析；
  报告 correct recall、accepted precision、false accept rate、false reject
  rate、escalation rate 和 E0-to-level paired accept transitions。
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
- `scripts/analyze_evp8_qwen_first_label_conditioned.py`：
  EVP-8 v0.3 Qwen-first label-conditioned 统计脚本；只解析 ignored Qwen
  raw responses 中的最终 JSON decision，执行后 join evaluator-only labels，
  输出 raw-output-free JSON/Markdown 汇总。
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
