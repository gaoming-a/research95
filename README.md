# Research95: Evidence Visibility for Candidate Patch Verification

This workspace is a clean continuation of the previous LLM code-review project.
It keeps only the assets that are useful for a stronger research direction:
studying how evidence visibility affects whether candidate patches should be
accepted, rejected, or escalated in real software projects.

## Current Thesis

LLM-only code review is not a reliable merge gate. The previous paired real-bug
experiments showed that LLM reviewers can produce useful bug-detection signals,
but they also report many plausible defects on fixed/reference code. The new
research direction treats that failure as motivation:

> Candidate patches can look plausible or pass some visible checks while still
> being unsafe to merge. We study how different levels of visible engineering
> evidence affect false accepts, correct-patch recall, and escalation decisions.

## Primary Research Direction

**Evidence visibility for candidate patch verification.**

The main experimental unit is no longer "does a reviewer find a bug in a source
excerpt?" The main unit is:

- an issue or real bug;
- a candidate patch from a reference fix, constructed control, AI generator, or
  agent workflow;
- executable evidence for whether the patch is correct, partial, overfitted, or
  wrong;
- a reviewer/verifier decision: accept, reject, or escalate.

The final roadmap keeps AI-generated patches as one candidate source and
failure-taxonomy input, not as the claim that every task must have a correct
AI-generated repair.

## Reused Assets

This workspace intentionally reuses:

- `src/cross_review/`: API, JSONL, parsing, metrics, and execution utilities.
- `scripts/oracles/`: narrow executable oracles for real BugsInPy samples.
- `scripts/validate_real_bug_dataset.py`: reference validation logic for
  buggy/fixed controls.
- `scripts/build_real_bug_review_dataset.py`: source-context construction logic
  that can be adapted for patch-verification candidates.
- `scripts/build_claim_*` and `scripts/claim_label_worksheet.py`: claim-level
  evidence packet and worksheet workflow.
- `docs/background/`: compact summaries of old results that explain why
  LLM-only review and majority review are insufficient.

## Excluded From This Clean Workspace

The following were intentionally not copied:

- `.env` and local API keys;
- local model configs such as `configs/models.local.json`;
- raw `data/`, `outputs/`, `tmp/`, and benchmark checkouts;
- old IEEE drafts and generated-code paper drafts;
- anonymous artifact ZIPs from the old direction;
- broad historical experiment logs that are not needed for patch verification.

## Current Execution Target

Use the current short status entry first:

- `docs/plans/current_project_state_zh.md`

The final-paper route is:

- `docs/plans/final_paper_roadmap_zh.md`

Treat that file as the single source for the next research target. It upgrades
the current pilot into an evidence-visibility empirical study with expanded
real-bug tasks, hidden-evaluator separation, tool-only baselines, four-anchor
E0/E2/E4/E6 evidence ablation, an Evidence Visibility Curve, calibrated
secondary metrics such as FACR/Evidence Gain, and an anonymous artifact. A
complete adjacent-difference E0-E6 ladder is future EVP-8 / EVP-7-v2 work, not
an insertion into the current EVP-7 artifacts. The non-conflicting current
reinforcement options are workload presentation first, and a user-confirmed
second-model replication over key anchors E0/E4/E6 only. As of 2026-06-20, the
user-selected journal-upgrade route is recorded in
`docs/experiments/evp8_journal_scale_execution_plan_20260620.md`: freeze a new
EVP-8 full-ladder protocol first, then run DeepSeek V4 Pro and Qwen3.7 Max as
the first model batch, with Kimi K2.6, Devstral 2, and Gemini 2.5 Flash added
later on the same frozen packets and prompts. As of 2026-06-22, the
DeepSeek/Qwen first batch has passed on 686 records per model, and the
later-model OpenRouter runner/preflight are strict-ready with
`OPENROUTER_API_KEY` present in the ignored local environment. The first Kimi
K2.6 execution attempt wrote 686 ignored raw records but was correctly blocked
by the later-model gate because Kimi returned reasoning-heavy responses with
79 invalid JSON outputs. The tracked protocol now records a Kimi clean-rerun
policy with `reasoning.enabled=false` and `include_reasoning=false`. The
reasoning-disabled clean rerun now passes for Kimi K2.6 on 686/686 records
after the OpenRouter top-level error retry repair, with provider-reported cost
for every record and actual model/provider metadata present. Devstral 2 also
passes the same later-model gate on 686/686 records, with provider-reported
cost for every record and actual model/provider metadata present. Gemini 2.5
Flash also passes on 686/686 records, with complete provider-reported cost and
actual model/provider metadata. The later-model audit and five-model synthesis
are now `passed` for the frozen EVP-8 v0.1 packet set. This permits
descriptive five-model per-level decision-pattern reporting, but it still does
not prove LLM superiority over deterministic baselines or final
evidence-level effectiveness. The cost overrun is now separately tracked at
`data/reviews/evp8_cost_accounting_summary.json`: passed-result USD excluding
Qwen is `2.892118056`, passed Qwen cost is CNY `41.119548`, and blocked Kimi
attempts add USD `7.27612053`. API execution is frozen; the next EVP-8 work is
paper tables, figures, claim-boundary audit, and artifact freeze. The current
low-cash-cost submission route is Software Quality Journal (SQJ): treat it as
the preferred CCF C / school D-or-above candidate only after school/department
recognition confirmation, use the non-OA subscription route unless APC is
explicitly approved, and convert the next main draft to Springer Nature
`sn-jnl` LaTeX rather than continuing IEEEtran as the submission format. The
SQJ framing and claim boundary packet is
`docs/paper/sqj_submission_framing.md`. The first generated Springer source
draft is `docs/paper/sqj_submission_draft.tex`, produced by
`scripts/write_sqj_latex_draft.py`; local PDF compilation is intentionally not
part of the current gate because `sn-jnl.cls` is not bundled in this MiKTeX
environment. The SQJ-specific source-package checklist is
`docs/artifact/sqj_submission_checklist.md`, audited by
`scripts/audit_sqj_submission_checklist.py`; it is a source/checklist gate, not
a final submission freeze. The SQJ final-freeze readiness packet is
`docs/artifact/sqj_final_freeze_readiness.md`, audited by
`scripts/audit_sqj_final_freeze_readiness.py`; it records remaining external
blockers without authorizing submission. The SQJ-specific figure set is
generated by `scripts/generate_sqj_figures.py` under `docs/figures/sqj/` and is
now the manuscript-facing figure set for the SQJ draft.
As of 2026-06-26, the accept-aware EVP-8 v0.2 DeepSeek/Qwen retest has passed
without overwriting v0.1. The v0.2 runner reuses existing sanitized EVP-7
visible test/tool artifacts, adds an E6 deterministic accept branch, and uses
JSON-mode provider requests (`thinking` disabled for DeepSeek). Both DeepSeek
V4 Pro and Qwen3.7 Max pass 686/686 parse-valid full runs. DeepSeek records 80
accepts overall and 23 E6 accepts; Qwen records 82 accepts overall and 24 E6
accepts. This supports the diagnosis that the earlier v0.1 `0 accept` result
was materially affected by experimental evidence construction, not a
provider-independent inability to accept patches. It remains a two-model
accept-aware retest, not a new five-model final claim.
The first tracked EVP-8 machine spec is
`data/protocols/evp8_protocol_v0_1.json`, checked by
`python scripts\audit_evp8_protocol_spec.py --check`. That audit currently
passes the protocol-structure boundary and reports
`phase0_api_readiness=ready_for_api_preflight`; this still does not authorize
real model execution. The DeepSeek/Qwen ignored local preflight is tracked at
`data/protocols/evp8_deepseek_qwen_preflight_summary_v0_1.json`; it passed
structural and credential-presence checks without printing key values or
calling APIs. The guarded smoke runner check-only summary is tracked at
`data/protocols/evp8_deepseek_qwen_smoke_check_only_v0_1.json`; it validates
35 project-frequency-stratified smoke packets and prompt/schema gates without
API calls or raw outputs. The final no-API smoke handoff packet is
`data/protocols/evp8_deepseek_qwen_smoke_execution_packet_v0_1.json`, with a
Markdown companion at
`docs/experiments/evp8_deepseek_qwen_smoke_execution_packet_v0_1.md`. It records
the exact guard commands and DeepSeek-then-Qwen execute commands, but explicitly
does not authorize model calls by itself. The post-smoke audit scaffold is
`data/protocols/evp8_deepseek_qwen_smoke_result_audit_v0_1.json`, with
Markdown at `docs/experiments/evp8_deepseek_qwen_smoke_result_audit_v0_1.md`;
before execution it is expected to report `waiting_for_execution`.
The Phase 0 smoke/protocol-validation candidate set is frozen at
`data/protocols/evp8_candidate_set_v0_1.json`: 21 tasks, 6 projects, and 98
candidates from the tracked EVP-7 structural cohort. This is not the final
journal-scale full-run cohort. The EVP-8 prompt template is frozen at
`prompts/evp8_visible_evidence_merge_gate_v0_1.md`, with no-API prompt
manifest and boundary audit outputs under `data/protocols/`.

Every concrete continuation round must first update:

- `docs/plans/current_plan_zh.md`

Historical execution plans are retained for traceability only:

- `docs/plans/ai_agent_experiment_execution_plan_zh.md`
- `docs/plans/agent_execution_plan_zh.md`

They should not override `final_paper_roadmap_zh.md`.

## Current Status

- Use `git status --short --branch` as the source of truth for Git sync. Recent
  2026-06-18 GitHub pushes hit network failures, so local `main` may be ahead of
  `origin/main`; when that repeats, continue the no-API paper/package work
  locally and sync later.
- The short project/file map is `docs/plans/current_project_state_zh.md`.
- The current submission handoff is
  `docs/artifact/submission_handoff_20260618.md`; it records the latest
  PDF/artifact rebuild, readiness audits, and the default no-API continuation
  boundary. Its boundary is checked by
  `scripts/audit_submission_handoff.py`,
  `scripts/audit_submission_freeze_candidate.py`, and the local quality gate.
- The current journal-upgrade execution plan is
  `docs/experiments/evp8_journal_scale_execution_plan_20260620.md`. It is a
  no-API plan: it does not authorize model calls until the EVP-8 protocol,
  packets, prompts, candidate-set policy, metrics, stop gates, and model routing
  policy are frozen and explicitly approved for execution.
- The first EVP-8 protocol-spec audit is tracked at
  `data/protocols/evp8_protocol_v0_1_audit_summary.json`. It confirms the
  `E0-E6` adjacent-difference ladder and evaluator-only `E7` boundary, while
  keeping API execution blocked unless ignored local preflight and an explicit
  execution command later pass. The
  candidate set blocker is removed by
  `data/protocols/evp8_candidate_set_v0_1_summary.json`; the prompt text
  blocker is removed by `data/protocols/evp8_prompt_manifest_v0_1.json` and
  `data/protocols/evp8_prompt_boundary_audit_v0_1.json`. Packet/schema
  dry-run, cost-observability dry-run, and deterministic-baseline dry-run
  summaries are now tracked under `data/protocols/`. DeepSeek/Qwen smoke and
  first-batch full runs have passed, and the G7 later-model packet plus
  later-model strict preflight/check-only plus post-run audit/five-model
  synthesis scaffolds have passed without API calls. Kimi, Devstral, and
  Gemini have since passed their later-model full runs, and the tracked
  five-model synthesis is now passed for descriptive per-level decision
  patterns on the frozen EVP-8 packet set. The cost accounting summary now
  records the Kimi blocked-attempt overrun and sets `api_freeze=true`. The next
  EVP-8 gate is paper/table/artifact freeze, not another model run.
- The prompt-only DeepSeek full run completed and produced a mixed/negative
  `stop_or_redesign` result. It is not a positive paper claim.
- The later tool-augmented full run passed its dedicated gate, but only supports
  a conditional claim about tool-visible evidence.
- The first Stage A/B expansion slice, `httpie_stage_ab_001`, has completed
  without model API calls: five `httpie` tasks, 22 candidates, 22/22 executable
  validations, and 44 prompt-boundary dry-run checks.
- The first DeepSeek AI patch generation attempt produced 10 patches, but only
  4 applied cleanly; it is diagnostic generator-pipeline evidence, not a clean
  verifier dataset slice.
- The latest Qwen 3.7 Plus strict agent retry on `bugsinpy_httpie_5` produced
  one applicable, oracle-validated negative generated patch; the second
  candidate timed out at the provider call and was not admitted.
- The earlier 8 DeepSeek agent-style candidates all applied and ran oracles, but
  all 8 failed the retained oracles. AI-generated patches should therefore be
  treated as a generated-negative extension for now, not the main balanced
  dataset source.
- The final roadmap now keeps the research line unchanged: candidate patch
  verification under evidence visibility. The main experiment task set should
  be rebuilt around validation-stable real bugs; `httpie_5` is a
  hard-generation/stress case if its reference validation remains stable, not a
  required generator-success task.
- The `httpie_5` stability/accounting audit confirms retained-oracle label
  stability and classifies the task as `hard_generation_case`; project-level
  pass-to-pass regression stability is now tracked by
  `data/p2p_scopes/bugsinpy_httpie_5_p2p_broad.json`, which retains 3 stable
  P2P-broad tests after excluding the retained fail-to-pass oracle and
  external-network tests.
- Luigi 3 and Luigi 4 now serve as replacement `main_balanced_task` examples:
  both have retained-oracle validation, task-file P2P-broad scopes, and
  `f2p_plus_p2p_broad` labels. Their current P2P scope is task-file based, not a
  project-wide Luigi regression suite; they are not final project-level P2P
  main-label evidence until the Luigi project-level scope blocker is resolved.
- Main regression-aware metrics are now cohort-gated by
  `data/cohorts/task_cohort_registry.json`. The current `p2p_broad_main` cohort
  includes `bugsinpy_httpie_5`, `bugsinpy_cookiecutter_1`,
  `bugsinpy_cookiecutter_2`, `bugsinpy_cookiecutter_3`, and
  `bugsinpy_tqdm_9`, `bugsinpy_PySnooper_1`, and `bugsinpy_PySnooper_3`;
  Luigi tasks are
  `pending_blocked` and retained only as appendix/smoke evidence.
- A bounded replacement sweep tried `bugsinpy_httpie_1` through
  `bugsinpy_httpie_4`; none entered `p2p_broad_main` under the current
  project-level P2P budget because of missing `pytest_httpbin`, legacy
  compatibility, or scope timeout blockers. These are recorded in the cohort
  registry instead of being silently discarded.
- The next bounded sweep tried `bugsinpy_tqdm_1` and `bugsinpy_tqdm_2`. Both
  completed project-level scope construction but retained only one stable
  P2P-broad test because most test files require the legacy `nose` dependency;
  they are recorded as `completed_insufficient_p2p_broad`, not main tasks.
- A follow-up sixth-task screening checked `bugsinpy_tqdm_3` through
  `bugsinpy_tqdm_8`. Without a new dependency decision, each collected only
  `tqdm/tests/tests_version.py::test_version`; behavior-relevant test files
  remain blocked by the legacy `nose` path, so they are recorded as
  `pending_blocked`.
- The scope builder now has a bounded `unittest` adapter. `bugsinpy_black_1`
  and `bugsinpy_black_3` were screened through it, but both are
  `pending_blocked` because the current environment lacks the required
  `typed_ast` dependency. An isolated `typed-ast==1.4.0` install attempt on
  Python 3.11 failed because the package needs local MSVC build tools.
- `bugsinpy_black_2` was also screened as a possible sixth task and shares the
  same `typed_ast` import blocker, so it is recorded as `pending_blocked`.
- The next phase will not prioritize repairing the legacy `nose` or Black
  `typed_ast` / MSVC blockers. Those tasks remain blocked feasibility cases;
  expansion now moves to a broader BugsInPy candidate pool under the same
  project-level P2P-broad admission criteria.
- The next replacement sweep tried `bugsinpy_cookiecutter_1`. An audited
  coverage-only addopts override plus an isolated Cookiecutter dependency venv
  produced a completed project-level P2P-broad scope: 296 common nodeids and
  290 included P2P-broad tests. A migrated UTF-8 context oracle and four
  candidate patches now validate under F2P plus P2P-broad, so
  `bugsinpy_cookiecutter_1` enters `p2p_broad_main` as the second completed
  project-level main task.
- `bugsinpy_cookiecutter_2` now also enters `p2p_broad_main`: its multiple-hook
  oracle validates 11 candidates under F2P plus a separate project-level
  P2P-broad scope with 278 stable tests.
- `bugsinpy_cookiecutter_3` now enters `p2p_broad_main`: its prompt choice
  oracle validates four candidates under F2P plus a separate project-level
  P2P-broad scope with 255 stable tests.
- `bugsinpy_cookiecutter_4` is not admitted. A bounded project-level P2P-broad
  construction attempt is recorded as blocked by the current environment and
  command boundary: missing `yaml`/`ruamel`/`past`, unavailable `cookiecutter`
  console command invocation, and external template tests that failed or timed
  out. The tracked record is
  `data/p2p_scopes/bugsinpy_cookiecutter_4_p2p_blocked_environment_policy.json`;
  no candidates were constructed.
- `bugsinpy_tqdm_9` now enters `p2p_broad_main`: its SI-format and
  `len(tqdm(total=...))` oracle validates seven curated candidates under F2P
  plus a project-level P2P-broad scope with 12 stable tests. The first generic
  partial-candidate pass overproduced six label-invalid negatives because the
  reference diff contains style-only changes; these were filtered before final
  validation.
- `bugsinpy_PySnooper_1` now enters `p2p_broad_main`: its UTF-8 snoop-log
  oracle validates six curated candidates under F2P plus a project-level
  P2P-broad scope with 24 stable tests. The PySnooper dependency environment is
  isolated under ignored `outputs/envs/`, and the dependency audit is tracked in
  `data/p2p_scopes/bugsinpy_PySnooper_1_dependency_environment_audit.json`.
- `bugsinpy_PySnooper_2` is blocked as an unclear experimental-boundary case:
  it would require compatibility/test-fixture shims, which are not allowed for
  main-cohort admission at this stage.
- `bugsinpy_PySnooper_3` now enters `p2p_broad_main`: its file-output oracle
  validates four candidate patches under F2P plus a project-level P2P-broad
  scope with four stable tests. It uses only declared dependencies in an ignored
  isolated venv and does not introduce a task-specific fixture shim.
- `bugsinpy_fastapi_1` has a clear F2P oracle, but it is now recorded as
  `pending_blocked_official_test_root_timeout`: full-repo discovery timed out
  twice, and the user-approved official-test-root `tests/` scope also exceeded
  the bounded construction budget without producing a manifest.
- `bugsinpy_fastapi_2` has a clear F2P oracle but is excluded as a shared
  FastAPI official-root timeout-risk case. `bugsinpy_sanic_1` also has a clear
  F2P oracle, but its project-level P2P-broad construction reached the bounded
  runtime without producing a manifest.
- `bugsinpy_scrapy_1` is excluded as `blocked_dependency_native_build`: the
  retained F2P unittest targets require declared `Twisted==20.3.0`, whose local
  install attempts to build a native extension and fails without MSVC build
  tools. No dependency substitution, fixture edit, or task-file P2P downgrade
  was used.
- `bugsinpy_youtube-dl_1` has a clear F2P oracle, but project-level unittest
  P2P-broad construction reached the bounded runtime without producing a
  manifest, so it is recorded as
  `pending_blocked_project_level_unittest_discovery_timeout`.
- `bugsinpy_tornado_1` has a clear websocket F2P oracle after the documented
  Windows selector event loop policy, but project-level unittest P2P-broad
  construction timed out before producing a manifest.
- `bugsinpy_tornado_9` has a clear pure-function F2P oracle, but the Tornado
  project-level unittest P2P-broad path again failed to produce a manifest. It
  is recorded as shared Tornado project-level scope risk.
- `bugsinpy_tornado_2` has a clear redirect PUT F2P oracle after local checkout
  reconstruction and the documented Windows selector event loop policy, but
  only a P2P dry-run was performed because Tornado project-level unittest P2P
  already has repeated timeout evidence. It is not admitted.
- `bugsinpy_ansible_2` was blocked before F2P because the large repository
  checkout exceeded the bounded feasibility window and did not write BugsInPy
  marker files.
- `bugsinpy_matplotlib_1` was blocked before F2P/P2P because the checkout probe
  required Matplotlib compiled extensions such as `ft2font`; editable/native
  builds were not run silently.
- The 2026-06-12 decision froze the then-current 7-task main cohort as
  `EVP-7 Protocol Pilot` to validate the evidence-visibility protocol before
  blind expansion. Controlled `youtube-dl` admissions through
  `bugsinpy_youtube-dl_37` and the bounded `bugsinpy_thefuck_1`
  rules-root pip-family admission have raised the tracked structural cohort to
  21 tasks across 6 projects. The tracked candidate manifest contains 98
  promoted candidates, including 21 correct reference patches, 76
  issue-not-fixed negatives, and 1 regression negative. The tracked evidence
  packet manifest contains 392 E0/E2/E4/E6 packet records, with all four
  levels complete for 98/98 candidates and zero leakage findings.
  Three visible-test outcomes are `error` because partial candidates break
  import; they remain valid visible outcomes, not missing evidence. The
  realistic tool-only baselines are generated for apply-only, visible-tests,
  and visible-tool-summary conditions. The merge-gate schema dry-run now
  generates 392 parse-valid accept/reject/escalate records with zero leakage
  findings. The latest real DeepSeek official G5 full run still covers the
  20-task/94-candidate/376-packet cohort with explicit bounded parallelism
  (`--concurrency 4`). It produced 376/376 parse-valid records, token-usage cost
  estimates for 376/376 records, and estimated total cost USD `0.327352058`.
  The raw-output-free tracked summary reports
  `real_llm_verifier_signal_observed_on_evp7`: E4/E6 keep observed false accept
  rate 0.0 and accepted precision 1.0, with E4 recall 0.05 and E6 recall 0.35.
  The tracked quality audit passes with limitations: it supports pilot-level
  observations about evidence-level variation, but not scale-generalized
  claims, not a claim that the LLM outperforms the deterministic visible-test
  tool-only baseline, and not a claim that runner-estimated cost is an external
  billing statement. The new 21-task/98-candidate/392-packet cohort has passed
  no-API structural gates and prompt-boundary checks, but it has not been rerun
  with a real LLM verifier.
  A controlled-expansion readiness report summarizes the broader BugsInPy rescreen
  and the project-diverse bounded probe lanes used to reach the current
  21-task / 98-candidate cohort. The
  first post-G5 lane, `bugsinpy_fastapi_4`, completed checkout but is
  F2P-blocked by the current Pydantic v2 environment and is not admitted.
  `bugsinpy_sanic_2` now has F2P under an ignored isolated Sanic dependency
  env, but its bounded official tests-root P2P construction timed out without
  a manifest and is not admitted. A parallel F2P-only triage
  found clean youtube-dl F2P signals, and controlled youtube-dl admissions
  through `bugsinpy_youtube-dl_37` have now crossed the project-level P2P-broad
  plus candidate revalidation boundary. The
  remaining readiness lanes are blocked by environment or historical probe
  constraints: Scrapy lacks Twisted, Ansible reaches Windows `fcntl`, Luigi
  lacks Tornado after existing Python 3.11 compatibility, and Matplotlib remains
  an incomplete/native-extension blocker. The refreshed metadata screen now
  identifies no fresh-project promising candidates outside already-main or
  already-risky projects. After GitHub checkout became reachable,
  `bugsinpy_thefuck_1` established F2P in an ignored isolated Python 3.11 test
  venv. Full-project P2P exceeded budget, but the explicit
  `thefuck_rules_root_pip_p2p_v1` policy collected `tests/rules`, retained 4
  pip-family P2P-broad tests, and validated four candidates before admission.
  This admission is rules-root pip-family evidence, not full project coverage.
  A follow-up `bugsinpy_thefuck_5` probe established F2P under a task-specific
  legacy pytest env, but the rules-root `git push` policy retained only 2 P2P
  tests and the broader `git` policy timed out without a manifest, so it is not
  admitted.
  Start from
  `docs/protocol/evidence_visibility_protocol.md`,
  `docs/experiments/evp7_protocol_pilot.md`, and
  `data/evidence/evp7_evidence_packets.jsonl`.
- The current IEEE draft is `docs/paper/ieee_submission_draft.tex`; it now
  includes the prompt-only negative result, the conditional tool-augmented
  result, the bounded EVP-7 G5 376-record evidence-visibility result, and the
  reader-flow bridge, workload ledger, related-work positioning, deterministic
  tool-only attribution, qualitative decision-case boundaries, and a final
  consistency pass aligning `Evidence Gain`, unsupported claims, and the
  bounded conclusion.
- Advisor-facing workload and claim-boundary talking points are tracked at
  `docs/paper/advisor_workload_response_zh.md`. This is a no-API explanation
  packet for why the current paper is a full candidate-patch verification
  pipeline rather than only a prompt comparison.
- The current submission freeze candidate is tracked at
  `docs/artifact/submission_freeze_candidate_20260618.md`. It records the
  current paper/artifact package as a candidate state only; target venue,
  final formatting, and freezing the current 7-page IEEE PDF still require
  explicit user confirmation.
- A Nature-style pre-submission reviewer assessment is tracked at
  `docs/paper/nature_reviewer_presubmission_report.md`. It identifies the next
  paper-writing risks as tool-only attribution, EVP-7 qualitative cases,
  related-work positioning, and simplifying the reader path around the frozen
  EVP-7 result.
- Related-work citation mapping is tracked at
  `docs/experiments/evp7_related_work_positioning.md`; the reference-manager
  export is `docs/references/evp7_related_work_references.ris`.
- `docs/paper/ieee_preapi_draft.tex` is historical pre-API context only.
- `scripts/audit_paper_readiness.py` now separates three paper-result
  boundaries: the old prompt-only gate remains a negative/redesign result, the
  old 30-candidate tool-augmented run remains a conditional tool-assisted
  result, and the latest real 376-record EVP-7 G5 run is reported as a bounded
  pilot evidence-visibility result with explicit limitations. It also reports
  `submission_package_ready`, which joins the current result claim readiness
  with the no-API submission handoff boundary and requires the advisor-facing
  workload response packet and submission freeze-candidate packet to exist.
- The 15-20 bug expansion target has been exceeded at 21 tasks. Further
  expansion is no longer the default next step; it requires a new 30-50 bug
  decision boundary rather than blind metadata admission.

## Core Commands

For current readiness, run:

```powershell
python scripts\audit_execution_readiness.py `
  --out-json outputs\readiness_audit\latest.json `
  --out-md outputs\readiness_audit\latest.md
```

For API pilot preflight without making API calls, run:

```powershell
python scripts\preflight_api_pilot.py `
  --config configs\api_pilot.local.json `
  --out-json outputs\api_pilot_preflight\latest.json `
  --out-md outputs\api_pilot_preflight\latest.md
```

For EVP-7 controlled-expansion readiness, run:

```powershell
python scripts\summarize_evp7_expansion_readiness.py
```

For no-run static unittest P2P preflight, run:

```powershell
python scripts\static_unittest_p2p_preflight.py `
  --task-id bugsinpy_youtube-dl_7 `
  --project youtube-dl `
  --static-exclude-token "YoutubeDL(" `
  --static-exclude-token "download(" `
  --static-exclude-token "urlopen" `
  --static-exclude-token "http://" `
  --static-exclude-token "https://"
```

For the no-run youtube-dl P2P decision audit, run:

```powershell
python scripts\audit_youtubedl_p2p_decision.py `
  --out-json outputs\youtubedl_p2p_decision_audit\latest.json `
  --out-md outputs\youtubedl_p2p_decision_audit\latest.md
```

This audit writes an approval-required command packet for the proposed
`youtube-dl_7` P2P run. It does not execute P2P or create a tracked manifest.
It also invokes the P2P scope builder with `--dry-run` to verify that the
generated command is accepted without executing tests.

The approved `youtube-dl_7` P2P attempt is recorded in
`docs/experiments/evp7_youtubedl_p2p_execution_attempt_20260613.md`. The first
attempt timed out when dynamically generated `test.test_download.TestDownload.*`
tests entered the batch. The completed rerun uses
`--exclude-nodeid-prefix "test.test_download.TestDownload"` and the scope policy
`youtube_dl_dynamic_download_nodeid_exclusion_v1`; it produced
`data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json` with 108 P2P-broad tests.
The current human-input packet treats that approval-gated P2P path as resolved
and does not print the stale pre-policy rerun command once the tracked manifest
exists.

The latest admitted task is recorded in
`docs/experiments/thefuck1_candidate_validation.md`. It produced
`data/p2p_scopes/bugsinpy_thefuck_1_p2p_broad_rules_pip_policy.json` with 4
P2P-broad tests under the explicit `thefuck_rules_root_pip_p2p_v1` policy and
rebuilt the no-API EVP-7 artifacts to 21 tasks, 98 candidates, and 392 evidence
packets. The latest tracked DeepSeek G5 run still covers the earlier
20-task/94-candidate/376-packet cohort.

The preceding admitted task is recorded in
`docs/experiments/youtubedl37_candidate_validation.md`. It produced
`data/p2p_scopes/bugsinpy_youtube-dl_37_p2p_broad.json` with 30 P2P-broad
tests under the same explicit dynamic-download nodeid exclusion policy and
rebuilt the no-API EVP-7 artifacts to 20 tasks, 94 candidates, and 376 evidence
packets.

The preceding admitted task is recorded in
`docs/experiments/youtubedl23_candidate_validation.md`. It produced
`data/p2p_scopes/bugsinpy_youtube-dl_23_p2p_broad.json` with 137 P2P-broad
tests under the same explicit dynamic-download nodeid exclusion policy and
rebuilt the then-current no-API EVP-7 artifacts to 19 tasks, 90 candidates, and
360 evidence packets.

The earlier admitted task is recorded in
`docs/experiments/youtubedl21_candidate_validation.md`. It produced
`data/p2p_scopes/bugsinpy_youtube-dl_21_p2p_broad.json` with 143 P2P-broad
tests under the same explicit dynamic-download nodeid exclusion policy and
rebuilt the then-current no-API EVP-7 artifacts to 18 tasks, 86 candidates, and
344 evidence packets.

The earlier admitted task is recorded in
`docs/experiments/youtubedl20_candidate_validation.md`. It produced
`data/p2p_scopes/bugsinpy_youtube-dl_20_p2p_broad.json` with 142 P2P-broad
tests under the same explicit dynamic-download nodeid exclusion policy and
rebuilt the then-current no-API EVP-7 artifacts to 17 tasks, 82 candidates, and
328 evidence packets.

The previous admitted task before that is recorded in
`docs/experiments/youtubedl43_candidate_validation.md`. It produced
`data/p2p_scopes/bugsinpy_youtube-dl_43_p2p_broad.json` with 18 P2P-broad
tests under the same explicit dynamic-download nodeid exclusion policy and
rebuilt the then-current no-API EVP-7 artifacts to 16 tasks, 78 candidates, and
312 evidence packets.

The preceding admitted task is recorded in
`docs/experiments/youtubedl17_candidate_validation.md`. It produced
`data/p2p_scopes/bugsinpy_youtube-dl_17_p2p_broad.json` with 146 P2P-broad
tests and rebuilt the then-current no-API artifacts to 15 tasks, 74 candidates,
and 296 evidence packets.

The earlier admitted task is recorded in
`docs/experiments/youtubedl16_candidate_validation.md`. It produced
`data/p2p_scopes/bugsinpy_youtube-dl_16_p2p_broad.json` with 147 P2P-broad
tests and rebuilt the then-current no-API artifacts to 14 tasks, 70 candidates,
and 280 evidence packets.

The earlier admitted task is recorded in
`docs/experiments/youtubedl11_candidate_validation.md`. It produced
`data/p2p_scopes/bugsinpy_youtube-dl_11_p2p_broad.json` with 160 P2P-broad
tests and rebuilt the then-current no-API artifacts to 13 tasks, 66 candidates,
and 264 evidence packets.

Recent earlier youtube-dl admissions include
`docs/experiments/youtubedl6_candidate_validation.md`. It produced
`data/p2p_scopes/bugsinpy_youtube-dl_6_p2p_broad.json` with 110 P2P-broad tests
under the same explicit dynamic-download nodeid exclusion policy as part of the
controlled admission sequence that later reached 11 tasks, 58 candidates, and
232 evidence packets after `bugsinpy_youtube-dl_2`.

For future approval-gated P2P commands, validate the command without executing
tests by appending `--dry-run` before any real run.

For stage-by-stage plan progress, run:

```powershell
python scripts\audit_ai_plan_progress.py `
  --out-json outputs\plan_progress\latest.json `
  --out-md outputs\plan_progress\latest.md
```

For the frozen EVP-7 manifests, run:

```powershell
python scripts\build_evp7_protocol_manifests.py --check
python scripts\build_evp7_candidate_manifest.py --check
python scripts\run_evp7_visible_tests.py --run --check --timeout 90
python scripts\build_evp7_visible_tool_summaries.py --check
python scripts\build_evp7_evidence_packets.py --check
python scripts\run_evp7_tool_only_baselines.py --check
python scripts\run_evp7_merge_gate_schema_dry_run.py --check
python scripts\analyze_evp7_schema_dry_run_metrics.py --check
python scripts\build_evp7_g5_llm_prompt_manifest.py --check
python scripts\preflight_evp7_g5_llm_run.py `
  --config configs\evp7_g5_llm.example.json `
  --out data\reviews\evp7_g5_llm_preflight_example.json
python scripts\run_evp7_g5_llm_workflow.py `
  --check-only `
  --summary-out data\reviews\evp7_g5_workflow_check_only_example.json
python scripts\create_evp7_g5_llm_local_config.py `
  --dry-run `
  --dry-run-out data\reviews\evp7_g5_local_config_dry_run.json `
  --packet-md docs\experiments\evp7_g5_execution_confirmation_packet.md
```

After a real G5 full run, regenerate the tracked raw-output-free summary with:

```powershell
python scripts\summarize_evp7_g5_llm_full_run.py
```

The guarded workflow can run a full current 392-packet execution with explicit
bounded parallelism, for example `--concurrency 4` or `--concurrency 6`. The
default remains sequential. The latest tracked DeepSeek full-run summary is
`docs/experiments/evp7_g5_llm_376_full_result.md`; it covers the frozen
20-task/94-candidate/376-packet cohort, has no schema-invalid records, and keeps
raw model responses under ignored `outputs/`.

The current 21-task structural cohort is ready for the next G5 step only after
user confirmation. The historical freeze and no-API smoke readiness record is
`docs/experiments/evp7_20_task_freeze_and_g5_smoke_readiness.md`; it applies to
the earlier 20-task cohort. Current structural readiness is tracked in
`data/reviews/evp7_g5_llm_run_readiness.json` and records that real smoke
execution still requires explicit user confirmation for provider, model, cost
ceiling, smoke packet count, and full-run permission.

After confirmation, a 4-packet real G5 smoke was run in
`outputs/evp7_g5_llm_376_smoke_001`. The raw-output-free report is
`docs/experiments/evp7_g5_llm_376_smoke_result.md`: 4/4 outputs parsed, all
non-mock, but the provider response did not expose reliable cost telemetry.
That historical smoke cannot be backfilled because it did not persist provider
`usage`, but `scripts/run_evp7_g5_llm_workflow.py` now records usage summaries
and estimates `deepseek_official` / `deepseek-v4-pro` cost from official token
pricing when provider-reported cost is absent. Future executed runs fail if
cost remains unknown.

The post-repair 4-packet smoke is
`docs/experiments/evp7_g5_llm_376_smoke_002_result.md`. It produced 4/4 valid
non-mock outputs, 4/4 token-usage summaries, `unknown_cost_record_count=0`, and
estimated total cost USD `0.003392942`. This validates the cost gate but remains
smoke evidence only.

The 376-packet full run is recorded in
`docs/experiments/evp7_g5_llm_376_full_result.md`, with the quality audit in
`docs/experiments/evp7_g5_376_full_quality_audit.md`. The audit status is
`passed_with_limitations`; it supports bounded EVP-7 pilot signal claims and
continues to reject scale-generalized and deterministic-baseline superiority
claims.

For full-goal completion evidence, run:

```powershell
python scripts\audit_goal_completion.py `
  --out-json outputs\goal_completion\latest.json `
  --out-md outputs\goal_completion\latest.md
```

For the human-input packet required before real API execution or the
`youtube-dl_7` P2P approve/reject decision, run. The status section separates
the unsupported prompt-only positive claim from the conditional tool-augmented
claim:

```powershell
python scripts\write_human_input_packet.py `
  --out-json outputs\handoff\human_input_packet.json `
  --out-md outputs\handoff\human_input_packet.md
```

For OpenRouter candidate slug availability, run:

```powershell
python scripts\audit_openrouter_model_catalog.py `
  --model anthropic/claude-sonnet-4.6 `
  --model openai/gpt-5.1-codex `
  --model openai/gpt-5.2 `
  --model deepseek/deepseek-v3.2 `
  --model qwen/qwen3-coder-next `
  --model z-ai/glm-5 `
  --out-json outputs\model_selection\openrouter_catalog_audit.json `
  --out-md outputs\model_selection\openrouter_catalog_audit.md
```

For the Git sync decision packet, run:

```powershell
python scripts\write_git_sync_packet.py `
  --out-json outputs\handoff\git_sync_packet.json `
  --out-md outputs\handoff\git_sync_packet.md
```

The packet uses `git status --short --branch` and treats local `ahead` or
`behind` state as not synced. A workspace with a configured remote is not
GitHub-synced until the branch is clean and reports `ahead=0` and `behind=0`.

For Git sync packet safety checks only, run:

```powershell
python scripts\audit_git_sync_packet.py `
  --out-json outputs\git_sync_packet_audit\latest.json `
  --out-md outputs\git_sync_packet_audit\latest.md
```

For a one-command local pre-API handoff, run:

The handoff summary separates the unsupported prompt-only positive claim from
the supported conditional tool-augmented claim.

```powershell
python scripts\write_pre_api_handoff.py `
  --out-json outputs\handoff\pre_api_handoff.json `
  --out-md outputs\handoff\pre_api_handoff.md
```

For local quality checks after edits, run:

```powershell
python scripts\run_local_quality_gate.py `
  --out-json outputs\local_quality_gate\latest.json `
  --out-md outputs\local_quality_gate\latest.md
```

For the SQJ source-package route, also run:

```powershell
python scripts\generate_sqj_figures.py
python scripts\write_sqj_latex_draft.py --check
python scripts\audit_sqj_submission_checklist.py `
  --out-json outputs\sqj_submission_checklist_audit\latest.json `
  --out-md outputs\sqj_submission_checklist_audit\latest.md
python scripts\audit_sqj_final_freeze_readiness.py `
  --out-json outputs\sqj_final_freeze_readiness\latest.json `
  --out-md outputs\sqj_final_freeze_readiness\latest.md
```

For submission handoff and freeze-candidate boundary checks only, run:

```powershell
python scripts\audit_submission_handoff.py `
  --out-json outputs\submission_handoff_audit\latest.json `
  --out-md outputs\submission_handoff_audit\latest.md
python scripts\audit_submission_freeze_candidate.py `
  --out-json outputs\submission_freeze_candidate_audit\latest.json `
  --out-md outputs\submission_freeze_candidate_audit\latest.md
```

For credential-boundary checks only, run:

```powershell
python scripts\audit_credential_boundary.py `
  --out-json outputs\credential_boundary\latest.json `
  --out-md outputs\credential_boundary\latest.md
```

For bootstrap safety checks only, run:

```powershell
python scripts\audit_bootstrap_safety.py `
  --out-json outputs\bootstrap_safety\latest.json `
  --out-md outputs\bootstrap_safety\latest.md
```

For guarded workflow safety checks only, run:

```powershell
python scripts\audit_workflow_guard.py `
  --out-json outputs\workflow_guard\latest.json `
  --out-md outputs\workflow_guard\latest.md
```

For API failure-handling checks only, run:

```powershell
python scripts\audit_api_failure_handling.py `
  --out-json outputs\api_failure_handling\latest.json `
  --out-md outputs\api_failure_handling\latest.md
```

For API command-template checks only, run:

```powershell
python scripts\audit_command_templates.py `
  --out-json outputs\command_templates\latest.json `
  --out-md outputs\command_templates\latest.md
```

For experiment run-record generation only, including the prompt-only full run
and the conditional tool-augmented full run, run:

```powershell
python scripts\write_experiment_run_records.py `
  --out-json outputs\experiment_run_records\latest.json `
  --out-md outputs\experiment_run_records\latest.md
```

For no-API reproducibility evidence, run:

```powershell
python scripts\write_reproducibility_manifest.py `
  --run-dir outputs\patch_verification_pilot_001 `
  --out outputs\reproducibility\pilot_001_manifest.json
python scripts\write_reproducibility_manifest.py `
  --run-dir outputs\patch_verification_pilot_repro_001 `
  --out outputs\reproducibility\pilot_repro_001_manifest.json `
  --compare-to outputs\reproducibility\pilot_001_manifest.json `
  --compare-out outputs\reproducibility\pilot_compare.json `
  --compare-md outputs\reproducibility\pilot_compare.md
```

For generated paper tables, run:

```powershell
python scripts\analyze_evp7_g5_statistics.py
python scripts\analyze_evp7_utility_sensitivity.py
python scripts\analyze_evp7_tool_attribution.py
python scripts\analyze_evp7_qualitative_cases.py
python scripts\audit_paper_claim_boundary.py
python scripts\write_paper_tables.py `
  --out-md docs\paper\generated_tables.md `
  --out-tex docs\paper\generated_tables.tex
```

The generated tables now include the current EVP-7 workload ledger, G5
376-record real LLM result, statistical intervals, utility sensitivity,
deterministic tool-only attribution, and claim boundary. The claim-boundary
audit maps supported and unsupported EVP-7 claims to tracked evidence and paper
coverage before the tables and draft are regenerated.

The qualitative case analysis is a separate paper-writing artifact at
`docs/experiments/evp7_g5_376_qualitative_cases.md`. It reports six
representative EVP-7 decision sequences while keeping model-visible decisions
separate from evaluator-only interpretations.

For reproducible paper figures, including the EVP-7 evidence visibility curve
and the decision-to-metric flowchart, run:

```powershell
python scripts\generate_paper_figures.py
```

For the historical IEEEtran source draft, run:

```powershell
python scripts\write_ieee_latex_draft.py `
  --tables-tex docs\paper\generated_tables.tex `
  --out docs\paper\ieee_submission_draft.tex
```

The IEEE draft generator is now retained as a content-source and regression
check for the earlier bounded EVP-7 draft. The SQJ route must create a new
Springer Nature `sn-jnl` LaTeX main draft rather than submitting this IEEEtran
file directly. The draft foregrounds the current EVP-7 bounded result and
treats the earlier 30-candidate API pilot as diagnostic design evidence. It
also references the workload ledger and qualitative case audit as
interpretation of pipeline scope and decision mechanics, not as additional
scale evidence.
It includes an early `How to Read the Experiment` bridge that maps candidate
patches to evidence packets, model decisions, hidden-label joins, and aggregate
metrics using `fig7_decision_metric_flow`.

Paper readiness also checks the current paper framing. The tracked outline,
research definition, Markdown draft, historical IEEE draft, and future SQJ
`sn-jnl` draft must preserve the evidence-visibility claim boundary; stale
AI-generated-patch title framing fails readiness.
It also checks that the IEEE draft contains a related-work section with the
core field-specific citations and the boundary that Evidence Gain is a
descriptive pilot metric, not a proposed universal benchmark score.
It also checks that the IEEE draft, generator, and Markdown draft keep the
reader-flow bridge and fig7 decision-to-metric reference.
It also checks that final-polish wording reports a bounded EVP-7 pilot, formats
unsupported claims as explicit interpretations, and keeps `Evidence Gain`
title-cased in paper-facing prose.
It also checks `docs/protocol/evidence_visibility_protocol.md` for the current
21-task / 98-candidate / 392-packet structural EVP-7 state, so a stale protocol
summary no longer passes merely because the file exists. The same check covers
`docs/experiments/evp7_protocol_pilot.md`, which must also treat the 376-record
G5 run as historical real-run evidence for the previous 20-task cohort and the
248-record run as an older historical checkpoint. It also checks the
canonical roadmap, `docs/plans/final_paper_roadmap_zh.md`, so stale Phase A
counts cannot pass while the protocol files are current.

For a dry-run bootstrap of the current DeepSeek official API prerequisite
configs, run:

```powershell
python scripts\bootstrap_api_prereqs.py `
  --model deepseek-v4-pro `
  --api-provider deepseek_official `
  --provider DeepSeek `
  --selection-source "DeepSeek official API docs and user-confirmed primary model" `
  --selection-source-url https://api-docs.deepseek.com `
  --capability-source "DeepSeek official V4 model family" `
  --capability-band "single documented primary pilot model" `
  --reason "Use DeepSeek V4 Pro through the official DeepSeek API for the first within-model llm_only versus evidence_first comparison." `
  --dry-run `
  --allow-missing-credentials
```

After `.env` exists and the dry-run output is correct, rerun the same command
without `--dry-run --allow-missing-credentials` to write the ignored local
configs and run strict preflight.

For a guarded API workflow check, run:

```powershell
python scripts\run_api_pilot_workflow.py `
  --config configs\api_pilot.local.json `
  --check-only `
  --summary-out outputs\api_workflow_check\latest.json
```

For an anonymous supplemental package, run:

```powershell
python scripts\prepare_anonymous_artifact.py `
  --out artifacts\research95_anonymous_artifact.zip `
  --manifest-out artifacts\research95_anonymous_artifact_manifest.json
python scripts\audit_anonymous_artifact.py `
  --artifact artifacts\research95_anonymous_artifact.zip `
  --out-json artifacts\research95_anonymous_artifact_audit.json `
  --out-md artifacts\research95_anonymous_artifact_audit.md
```

The final submission checklist is `docs/artifact/submission_checklist.md`. It
lists the current paper package, all seven required PDF figures, claim-boundary
evidence, rebuild commands, artifact commands, exclusion boundary, and
ready-to-submit criteria. The artifact audit requires this checklist and
`docs/figures/fig7_decision_metric_flow.pdf` to be present in the ZIP. It also
requires `docs/paper/advisor_workload_response_zh.md`, so the submitted package
keeps the advisor-facing workload and claim-boundary explanation.
