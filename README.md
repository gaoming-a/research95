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

The final-paper route is:

- `docs/plans/final_paper_roadmap_zh.md`

Treat that file as the single source for the next research target. It upgrades
the current pilot into an evidence-visibility empirical study with expanded
real-bug tasks, hidden-evaluator separation, tool-only baselines, evidence
ablation, an Evidence Visibility Curve, calibrated secondary metrics such as
FACR/Evidence Gain, and an anonymous artifact.

Every concrete continuation round must first update:

- `docs/plans/current_plan_zh.md`

Historical execution plans are retained for traceability only:

- `docs/plans/ai_agent_experiment_execution_plan_zh.md`
- `docs/plans/agent_execution_plan_zh.md`

They should not override `final_paper_roadmap_zh.md`.

## Current Status

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
- `bugsinpy_ansible_2` was blocked before F2P because the large repository
  checkout exceeded the bounded feasibility window and did not write BugsInPy
  marker files.
- `bugsinpy_matplotlib_1` was blocked before F2P/P2P because the checkout probe
  required Matplotlib compiled extensions such as `ft2font`; editable/native
  builds were not run silently.
- The 2026-06-12 decision freezes the current 7-task main cohort as
  `EVP-7 Protocol Pilot`. The tracked candidate manifest now contains 42
  promoted candidates across those 7 tasks. The tracked evidence packet
  manifest now contains 168 E0/E2/E4/E6 packet records. E0/E2 are complete;
  E4 and E6 are complete for 42/42 candidates after an independent visible-test
  runner, tracked P2P compat-shim reuse, and deterministic visible tool
  summaries. Three visible-test outcomes are `error` because partial candidates
  break import; they remain valid visible outcomes, not missing evidence. The
  realistic tool-only baselines are now generated for apply-only, visible-tests,
  and visible-tool-summary conditions. The merge-gate schema dry-run now
  generates 168 parse-valid accept/reject/escalate records with zero leakage
  findings. The G5 metric scaffold now computes FAR, recall, escalation, FACR,
  and Evidence Gain over schema-stable dry-run records. The G5 LLM prompt
  manifest now covers all 168 E0/E2/E4/E6 packets with zero leakage findings
  and no stored prompt text. A tracked G5 example config and preflight prove
  structural readiness while keeping the tracked example blocked from real
  execution. The real DeepSeek official G5 full run has now completed on all
  168 packets with explicit bounded parallelism (`--concurrency 4`). It
  produced 167 parse-valid outputs and one schema-invalid output, with
  pilot-level evidence-visibility metric variation observed on EVP-7. This
  supports EVP-7 pilot signal claims after quality audit, not scale-generalized
  paper claims. A controlled-expansion readiness report now summarizes the
  broader BugsInPy rescreen and defines project-diverse bounded probe lanes for
  the next 15-20 bug expansion step.
  Start from
  `docs/protocol/evidence_visibility_protocol.md`,
  `docs/experiments/evp7_protocol_pilot.md`, and
  `data/evidence/evp7_evidence_packets.jsonl`.
- The current IEEE draft is `docs/paper/ieee_submission_draft.tex`.
- `docs/paper/ieee_preapi_draft.tex` is historical pre-API context only.
- Further expansion to 15-20 bugs is deferred until EVP-7 protocol gates pass.

## Core Commands

For current readiness, run:

```powershell
python scripts\audit_execution_readiness.py `
  --out-json outputs\readiness_audit\latest.json `
  --out-md outputs\readiness_audit\latest.md
```

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

The guarded workflow can run the full 168-packet execution with explicit
bounded parallelism, for example `--concurrency 4` or `--concurrency 6`. The
default remains sequential.

For full-goal completion evidence, run:

```powershell
python scripts\audit_goal_completion.py `
  --out-json outputs\goal_completion\latest.json `
  --out-md outputs\goal_completion\latest.md
```

For the human-input packet required before real API execution, run:

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

For Git sync packet safety checks only, run:

```powershell
python scripts\audit_git_sync_packet.py `
  --out-json outputs\git_sync_packet_audit\latest.json `
  --out-md outputs\git_sync_packet_audit\latest.md
```

For a one-command local pre-API handoff, run:

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

For experiment run-record generation only, run:

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
python scripts\write_paper_tables.py `
  --out-md docs\paper\generated_tables.md `
  --out-tex docs\paper\generated_tables.tex
```

For the current IEEEtran LaTeX submission draft, run:

```powershell
python scripts\write_ieee_latex_draft.py `
  --tables-tex docs\paper\generated_tables.tex `
  --out docs\paper\ieee_submission_draft.tex
```

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
