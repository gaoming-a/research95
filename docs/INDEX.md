# Research95 Index

## Project Execution Rules

- `../AGENTS.md`: project-level requirements for the plan-execute-audit-revise
  loop, including verification, diagnosis, documentation sync, and GitHub sync
  rules for future agent runs.

## Active Plan

- `plans/final_paper_roadmap_zh.md`: canonical final-paper route and subsequent
  research target. It upgrades the current pilot into an evidence-visibility
  empirical study with expanded data, tool-only baselines, hidden-evaluator
  separation, multi-level evidence ablation, artifact goals, and the rule that
  generator-unsolved but validation-stable tasks such as `httpie_5` should be
  treated as hard-generation/stress cases rather than deleted.
- `plans/current_plan_zh.md`: active per-turn execution log. Future agents must
  update this file before concrete experiments, API calls, data changes, paper
  edits, or Git sync work.
- `plans/current_plan.md`: English companion plan. It is useful for bilingual
  handoff context, but `plans/current_plan_zh.md` is the stricter execution log.

## Historical Plan References

- `plans/ai_agent_experiment_execution_plan_zh.md`: historical standalone task
  book for the earlier API-pilot route. Retain for traceability and command
  contracts, but do not let it override `plans/final_paper_roadmap_zh.md`.
- `plans/agent_execution_plan_zh.md`: older detailed step-by-step execution
  plan. Retain as reference only.

## New Paper Direction

- `paper/research_definition.md`: precise problem definition, hypotheses, and
  non-goals.
- `paper/patch_verification_outline.md`: target paper outline and contribution
  framing.
- `paper/patch_verification_draft.md`: mixed-result draft with no-API
  validation results and the first DeepSeek official API full-run outcome.
- `paper/generated_tables.md`: generated Markdown paper tables from current
  no-API outputs.
- `paper/generated_tables.tex`: generated LaTeX table snippets used by the
  current IEEE draft.
- `paper/ieee_submission_draft.tex`: current anonymous IEEEtran submission
  draft. It includes the prompt-only mixed/negative result, the separate
  tool-augmented full-run result, figures, threats, and conclusion.
- `paper/ieee_preapi_draft.tex`: historical IEEEtran pre-API LaTeX draft.
- `experiments/patch_verification_plan.md`: experiment design for the first
  patch-verification pilot.
- `experiments/patch_verification_pilot_report.md`: tracked summary of the
  current no-API pilot, executable validation, metrics, and prompt dry-run.
- `experiments/deepseek_full_run_result.md`: tracked summary of the first
  DeepSeek official API full run. The run completed with 60 non-mock reviews
  and passed completeness, but the gate verdict is `stop_or_redesign`.
- `experiments/deepseek_full_run_failure_analysis.md`: qualitative failure
  analysis for the DeepSeek full run, including `llm_only` false accepts,
  evidence-first recall loss, invalid-output causes, and the next redesign
  gate.
- `experiments/tool_augmented_redesign_smoke_result.md`: tracked result for the
  5-candidate `tool_augmented_evidence` redesign smoke. The smoke passed, but
  it is a separate tool-augmented diagnostic result rather than a rescue of the
  original prompt-only evidence-first claim.
- `experiments/tool_augmented_full_run_result.md`: tracked result for the
  30-candidate `tool_augmented_evidence` full run. The run passed its dedicated
  tool-assisted gate, with false accept rate 0 and correct-patch recall 1 on
  the current pilot.
- `experiments/tool_only_baseline_result.md`: deterministic tool-only baseline
  result on the current 30-candidate pilot. It separates patch-apply-only from
  validation-summary tool evidence and keeps the oracle-style boundary explicit.
- `experiments/qualitative_case_report.md`: four diagnostic cases comparing
  LLM-only, evidence-first, tool-only, and tool-augmented decisions.
- `experiments/bugsinpy_expansion_screening.md`: 15-task BugsInPy expansion
  screening registry. The five `httpie` tasks have completed the first Stage
  A/B closed loop; the remaining selected tasks still need task-specific
  oracles and candidate validations.
- `experiments/httpie_stage_ab_result.md`: tracked result for
  `httpie_stage_ab_001`, the first Stage A/B validated dataset slice with five
  `httpie` tasks, 22 candidates, executable validation, no-API baselines,
  tool-only baselines, and prompt-boundary dry-run checks.
- `experiments/httpie_ai_patch_generation_attempt.md`: tracked result for the
  first DeepSeek AI patch generation attempt on the five validated `httpie`
  tasks. It generated 10 patches, but 6 failed to apply, so it is diagnostic
  generator-pipeline evidence rather than a clean verifier dataset slice.
- `experiments/qwen_httpie5_strict_agent_attempt.md`: tracked result for the
  Qwen strict-mode retry on `bugsinpy_httpie_5`. Qwen returned JSON edit plans,
  but exact `find` matching failed, so no candidate was admitted.
- `experiments/httpie5_task_stability_accounting.md`: retained-oracle stability
  audit and task-level generation accounting for `bugsinpy_httpie_5`. It
  classifies the task as `hard_generation_case` and points to the later P2P
  follow-up for regression-scope completion.
- `experiments/httpie5_pass_to_pass_scope.md`: P2P-core/P2P-broad scope report
  for `bugsinpy_httpie_5`; it collected 17 tests, excluded the retained
  fail-to-pass oracle and external-network tests, and retained 3 stable local
  P2P-broad tests.
- `experiments/project_level_p2p_scope_update.md`: transition report for the
  final `project_level_p2p_broad` standard. It records the completed
  `httpie_5` project-level manifest, the updated label name
  `correct_under_f2p_and_p2p_broad`, and the current Luigi project-level P2P
  blocker.
- `experiments/luigi_replacement_tasks_result.md`: validation, P2P scope, and
  task-accounting result for `bugsinpy_luigi_3` and `bugsinpy_luigi_4`. Both
  are classified as `main_balanced_task`; current P2P-broad scope is based on
  each task's relevant test file.
- `experiments/patch_evidence_bench_schema.md`: long-term expanded benchmark
  schema for
  TaskRecord, PatchRecord, EvidencePacket, ValidationOutcome, and
  VerifierDecision.
- `experiments/leakage_policy.md`: visible-evidence and hidden-evaluator
  separation policy for future expanded runs.
- `experiments/patch_candidate_schema.md`: current pilot JSONL schema for
  candidate patches, verifier outputs, and task-level generator accounting
  fields such as `generation_status` and `task_role`.
- `experiments/evidence_first_protocol.md`: comparison conditions and
  evidence-first verification workflow.
- `experiments/patch_verification_metrics.md`: metric definitions and stop-gate
  metrics.
- `experiments/pilot_dataset_construction.md`: first no-API pilot construction
  rules.
- `experiments/reusable_real_bug_assets.md`: how old real-bug assets map into
  the new patch-verification study.

## Reused Background Evidence

- `background/previous_findings_summary.md`: compact summary of why the old
  cross-review direction failed and what should carry forward.
- `background/reusable_bug_assets_summary.md`: concise map from old real-bug
  assets to patch-verification assets.

## Literature

- `literature/agent_topconf_2025_2026.md`: English literature notes for recent
  agent and software-engineering papers.
- `literature/agent_topconf_2025_2026_zh.md`: Chinese version of the recent
  literature notes.

## Code Assets

- `src/cross_review/`: reusable package for OpenAI-compatible provider API
  calls, JSON parsing, metrics, and local execution. The current primary path
  is DeepSeek official API; the OpenRouter-compatible client remains available
  as an alternative provider. Provider errors are sanitized before surfacing.
- `configs/api_pilot.example.json`: template config for the first API pilot.
- `configs/model_selection.example.json`: template for documenting model
  selection source, capability band, provider model id, API provider, and
  limitations.
- `experiments/model_selection_protocol.md`: protocol for model selection and
  paper-claim boundaries.
- `experiments/model_selection_shortlist.md`: historical/alternative
  OpenRouter decision aid, with observed candidate slugs and paper wording
  boundaries. The current primary model path is DeepSeek official API with
  `deepseek-v4-pro`.
- `scripts/audit_execution_readiness.py`: overall continuation audit for
  no-API outputs, API credentials/config readiness, and Git repository status.
- `scripts/audit_credential_boundary.py`: structural credential-boundary audit
  for `.gitignore`, `.env.example`, and tracked secret-file state. Latest
  report: `outputs/credential_boundary/latest.md`.
- `scripts/audit_bootstrap_safety.py`: no-API safety audit for
  `scripts/bootstrap_api_prereqs.py`, checking that dry-run writes no files and
  strict missing-credential execution fails without creating local configs.
  Latest report: `outputs/bootstrap_safety/latest.md`.
- `scripts/audit_workflow_guard.py`: no-API safety audit for
  `scripts/run_api_pilot_workflow.py`, checking that check-only never attempts
  model calls and that strict missing-prerequisite runs stop before review
  outputs are created. Latest report: `outputs/workflow_guard/latest.md`.
- `scripts/audit_api_failure_handling.py`: no-API safety audit for mid-run API
  failures. It uses a local refused connection, verifies that the runner writes
  sanitized `run_error.json`, checks that no dummy secret leaks to stdout,
  stderr, or the error file, and confirms the completeness audit rejects the
  failed run. Latest report: `outputs/api_failure_handling/latest.md`.
- `scripts/audit_command_templates.py`: consistency audit for API command
  templates in the human-input packet and key docs, including bootstrap dry-run,
  strict write, preflight, check-only, and execute ordering. Latest report:
  `outputs/command_templates/latest.md`.
- `scripts/audit_ai_plan_progress.py`: stage-by-stage audit against
  `docs/plans/ai_agent_experiment_execution_plan_zh.md`, reporting which
  stages are complete, partial, blocked, or pending. Stage 8 requires
  `run_completeness.json` to prove a 60-record non-mock full run before
  postprocess is considered complete. Stage 9 now treats the prompt-only
  `stop_or_redesign` verdict as an interpreted negative/redesign signal when
  the separate tool-augmented full-run gate has passed. Latest report:
  `outputs/plan_progress/latest.md`.
- `scripts/audit_goal_completion.py`: full-objective completion audit that
  prevents mistaking local readiness, no-API reproduction, or paper skeletons
  for completion of the whole plan. It also requires the experiment run-record
  ledger to cover no-API, smoke API, full API, and quality-gate records. It
  preserves the prompt-only result as negative and checks the tool-augmented
  conditional claim separately. Latest report:
  `outputs/goal_completion/latest.md`.
- `scripts/write_human_input_packet.py`: writes an ignored handoff packet that
  lists missing human inputs, safe command order, and forbidden actions before
  real API execution. It includes smoke/full postprocess commands with expected
  candidate counts. Latest report: `outputs/handoff/human_input_packet.md`.
- `scripts/write_git_sync_packet.py`: writes an ignored Git sync decision
  packet with current Git state, old remote context, required remote decision,
  staging allowlist, safe command template, post-sync acceptance criteria, and
  forbidden actions. Latest report: `outputs/handoff/git_sync_packet.md`.
- `scripts/audit_git_sync_packet.py`: audits the Git sync packet safety rules,
  including the human decision gate, staging allowlist, ignored local-file
  checks before staging, cached-diff checks after staging, and the ban on
  `git add .`. Latest report: `outputs/git_sync_packet_audit/latest.md`.
- `scripts/write_pre_api_handoff.py`: one-command local handoff that refreshes
  readiness, reproducibility, paper readiness, plan progress, goal completion,
  experiment run records, human-input, Git-decision, and Git handoff audit
  reports without calling model APIs. Latest report:
  `outputs/handoff/pre_api_handoff.md`.
- `scripts/write_experiment_run_records.py`: writes the experiment run ledger
  required by the AI execution plan. It summarizes no-API reproduction, smoke
  API, full API, and local quality-gate records using existing JSON evidence
  and marks whether any run is allowed to support a paper claim. Latest report:
  `outputs/experiment_run_records/latest.md`.
- `scripts/audit_paper_readiness.py`: Stage-E audit that prevents moving from
  the pre-API methods draft to positive claims until real API outputs, failure
  examples, and the relevant gate are present. It reports prompt-only positive
  readiness and tool-augmented conditional readiness separately, so the
  `tool_augmented_evidence` result cannot be mistaken for prompt-only model
  ability. It also reports whether pre-API methods evidence is complete:
  pilot report, paper draft/outline, model-selection docs, reproducibility
  comparison, model catalog audit, and pre-API handoff.
- `scripts/write_paper_tables.py`: generates Markdown and LaTeX pre-API paper
  tables from dataset summary, validation summary, metrics, and deterministic
  reproducibility comparison.
- `scripts/write_ieee_latex_draft.py`: generates the current IEEEtran
  submission draft at `docs/paper/ieee_submission_draft.tex` from generated
  dataset/no-API tables plus audited prompt-only and tool-augmented metrics.
  The old `docs/paper/ieee_preapi_draft.tex` is retained only as historical
  pre-API context.
- `scripts/generate_paper_figures.py`: generates the publication figure set
  under `docs/figures/` in PDF, SVG, and PNG formats. Figures cover the
  workflow, evidence boundary, dataset composition, result tradeoff, and claim
  boundary.
- `figures/`: reproducible paper figure assets. The IEEE submission draft uses
  the PDF versions, while PNG versions are for quick local inspection.
- `figures/imagegen/`: generated raster visual candidates plus exact prompts
  for graphical abstracts, presentations, and visual drafts. These PNGs are
  conceptual assets and must not replace the reproducible numeric/vector
  figures when supporting experimental claims.
- `artifact/anonymous_artifact.md`: inclusion and exclusion policy for the
  anonymous supplemental package.
- `scripts/prepare_anonymous_artifact.py`: package builder for anonymous
  supplemental materials. It excludes credentials, local configs, raw outputs,
  benchmark checkouts, and generated artifacts.
- `scripts/audit_anonymous_artifact.py`: validates the generated anonymous ZIP
  contents, required files, manifest consistency, and exclusion rules.
- `scripts/create_api_pilot_local_config.py`: helper that creates an ignored
  `configs/api_pilot.local.json` after a concrete provider model id is chosen.
- `scripts/create_model_selection_local.py`: helper that creates an ignored
  `configs/model_selection.local.json` with source, capability, limitation,
  API provider, and model id metadata.
- `scripts/bootstrap_api_prereqs.py`: one-command bootstrap for explicitly
  provided model-selection inputs. It writes the ignored model-selection and
  API local configs, validates their model match, and runs preflight; dry-run
  mode prints planned configs without writing files.
- `scripts/validate_model_selection.py`: validator for documented model
  selection and optional cross-check against `configs/api_pilot.local.json`.
- `scripts/audit_openrouter_model_catalog.py`: public OpenRouter catalog
  availability audit for candidate model slugs. Latest report:
  `outputs/model_selection/openrouter_catalog_audit.md`.
- `scripts/build_patch_verification_dataset.py`: current no-API pilot dataset
  builder. It emits evaluator-facing candidates and model-visible anonymous
  evidence packets. It materializes patch text from an external retained
  buggy/fixed checkout root via `--source-workspace-root`.
- `scripts/run_no_api_patch_pipeline.py`: one-command no-API reproduction
  wrapper for dataset construction, baseline metrics, executable validation,
  API prompt dry-run, and pilot report generation.
- `scripts/write_reproducibility_manifest.py`: hashes deterministic no-API
  output files and compares reproduced runs with the original pilot. The latest
  local comparison matched all checked deterministic files in
  `outputs/reproducibility/pilot_compare.json`.
- `scripts/run_local_quality_gate.py`: one-command local quality gate for
  compile checks, cache cleanup, sensitive scan, credential-boundary checks,
  bootstrap safety, workflow guard, API failure handling, command templates,
  experiment run-record generation, Git handoff safety, readiness audits, paper
  readiness, and anonymous artifact dry-run.
- `scripts/analyze_patch_verification.py`: patch-verification metrics analyzer
  for verifier outputs.
- `scripts/validate_patch_candidates.py`: no-API executable validator that
  copies retained buggy checkouts, applies candidate patches, and runs retained
  oracles.
- `scripts/build_task_generation_accounting.py`: builds task-level generation
  accounting records from validation reports, relabeled generated candidates,
  and generation prompt manifests.
- `scripts/build_pass_to_pass_scope.py`: collects project tests and builds
  P2P-core/P2P-broad stable runnable subsets for a task.
- `scripts/validate_candidates_with_p2p.py`: validates candidate patches with
  retained oracle plus a P2P-broad scope and emits merged labels such as
  `correct_under_f2p_and_p2p_broad` and `incorrect_regression`.
- `scripts/run_patch_verification_api_pilot.py`: provider-aware runner for the
  small `llm_only` versus `evidence_first` API pilot. The current primary
  provider is DeepSeek official API. It supports config-driven dry-runs and
  writes metrics after real API runs. Direct real API execution is guarded;
  real calls should be made through `scripts/run_api_pilot_workflow.py`.
  Mid-run API failures write a sanitized `run_error.json`, which marks the run
  incomplete for downstream audits.
- `configs/api_redesign_smoke.example.json`: template for the failure-case-only
  `tool_augmented_evidence` redesign smoke. It must be copied or materialized
  under ignored output/local config paths before use.
- `configs/api_tool_augmented_full.example.json`: template for the
  30-candidate tool-augmented full run.
- `scripts/build_redesign_smoke_inputs.py`: builds the 5-candidate
  tool-augmented redesign-smoke input set, or the 30-candidate full-run input
  set with `--all-candidates`, from existing candidates, evidence packets, and
  validation records.
- `scripts/run_tool_only_baseline.py`: builds deterministic tool-only
  `apply_only` and `validation_summary` verifier records from current
  candidates and validation outputs.
- `scripts/build_qualitative_case_report.py`: generates the tracked
  qualitative case report from existing prompt-only, tool-only, and
  tool-augmented outputs.
- `scripts/screen_bugsinpy_expansion.py`: screens retained BugsInPy checkouts
  and writes the next 15-task expansion registry.
- `experiments/deepseek_agent_patch_validation_result.md`: records validation
  of the 8 existing DeepSeek agent-style `httpie_1`-`httpie_4` generated
  patches; all applied and ran oracles, but all relabeled as `incorrect`.
- `experiments/qwen37_httpie5_strict_agent_attempt.md`: records the
  `qwen3.7-plus` strict agent retry on `bugsinpy_httpie_5`; it produced one
  applicable but oracle-failing generated negative candidate and timed out on
  the second candidate.
- `scripts/run_redesign_smoke_workflow.py`: guarded workflow for the
  tool-augmented redesign smoke and full run. It performs preflight/check-only
  gating, executes only the `tool_augmented_evidence` condition, and writes a
  dedicated smoke or full-run gate report instead of reusing the original
  prompt-only full-run gate.
- `scripts/run_api_pilot_workflow.py`: guarded API pilot workflow wrapper. It
  runs preflight, requires explicit `--execute` before any model call, runs the
  API pilot, records model-selection validation, and then runs postprocess.
  It forwards `--run-dir` and `--limit` to the runner; after smoke passes,
  full runs should use
  `--run-dir outputs/patch_verification_api_pilot_002 --limit 0 --execute`.
  Current valid DeepSeek smoke: `outputs/patch_verification_api_pilot_001_tokens4096`
  with `max_tokens=4096`, 4 non-mock reviews, run completeness passed, and
  invalid output rate 0.
  Current full run: `outputs/patch_verification_api_pilot_002`, 60 non-mock
  reviews, run completeness passed, gate verdict `stop_or_redesign`.
- `scripts/audit_api_run_completeness.py`: validates that an API smoke/full run
  has the expected review count, condition counts, metrics count, non-mock
  boundary, raw response paths, raw response hashes, review schema fields, and
  run summary, and fails any run directory that contains `run_error.json`. Full
  paper claims require a 60-record non-mock full-run completeness report.
- `scripts/preflight_api_pilot.py`: readiness checker for data files,
  validation summary, provider model id, API provider, and provider key
  presence.
- `scripts/summarize_patch_verification_pilot.py`: Markdown report generator
  for the current no-API pilot and API prompt dry-run outputs.
- `scripts/summarize_api_pilot_results.py`: Markdown report generator for
  real API or mock smoke `reviews.jsonl` and `metrics.json` outputs. Mock
  reports are explicitly marked as non-results.
- `scripts/extract_api_failure_examples.py`: post-run qualitative-analysis
  extractor for false accepts, correct patches not accepted, and evidence-first
  reject/escalate examples.
- `scripts/evaluate_api_pilot_gate.py`: post-run stop/continue gate evaluator
  that compares `llm_only` and `evidence_first` metrics and flags mock outputs
  as non-evidence.
- `scripts/postprocess_api_pilot_run.py`: one-command wrapper for API result
  report generation, failure example extraction, stop/continue gate evaluation,
  run completeness audit, paper readiness audit, and postprocess summary.
- `scripts/oracles/`: executable real-bug oracles.
- `scripts/validate_real_bug_dataset.py`: real-bug metadata and oracle
  validation.
- `scripts/build_real_bug_review_dataset.py`: source-context builder to adapt.
- `scripts/build_claim_evidence_packets.py`: evidence packet builder to adapt.
- `scripts/analyze_tool_gated_reviews.py`: oracle-gated analysis reference.
- `experience/engineering_notes.md`: fresh operational notes for this new
  workspace.
- `prompts/prompt_change_log.md`: fresh prompt log for patch-verification
  prompts only.
- `prompts/api_pilot_prompts.md`: prompt templates and label-leakage boundary
  for the first API pilot.

## Safety Rules

- Do not commit `.env`, local model configs, raw outputs, or benchmark checkouts.
- Do not use prompt-only adjudication as ground truth.
- Any positive result must distinguish LLM-only decisions from evidence-backed
  decisions.
- Do not run API calls until the no-API patch candidate dataset validates,
  realistic patch diffs are available, the difficult-negative ratio gate
  passes, and the API prompts/run metadata are documented.
