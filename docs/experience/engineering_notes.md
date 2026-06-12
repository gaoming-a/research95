# Engineering Notes

## 2026-06-05 AI execution handoff plan

- Added `docs/plans/ai_agent_experiment_execution_plan_zh.md` as the clean
  task book for another AI agent. It separates actionable experiment stages
  from historical notes and explicitly lists commands, gates, forbidden
  actions, paper-readiness rules, artifact rules, and human-required inputs.
- Expanded the handoff plan into an executable contract: every stage now has
  required evidence files, pass criteria, a run-record template, failure
  handling rules, and a minimum human-input checklist. This is meant to prevent
  a later AI agent from treating command logs, dry-runs, mock reviews, or
  incomplete API runs as experimental evidence.
- The handoff plan intentionally keeps real API execution blocked until `.env`,
  `configs/model_selection.local.json`, `configs/api_pilot.local.json`, strict
  preflight, and `--execute` are all present.
- The plan distinguishes no-API reproduction, prompt dry-run, mock smoke, and
  real API model results to prevent accidental overclaiming.

## 2026-06-05 no-API reproducibility manifest

- Added `scripts/write_reproducibility_manifest.py` to hash deterministic
  no-API outputs and compare reproduced runs with the original pilot.
- Current comparison:
  `outputs/reproducibility/pilot_compare.json` reports `matched = true` for
  seven deterministic files across `outputs/patch_verification_pilot_001` and
  `outputs/patch_verification_pilot_repro_001`.
- The script deliberately treats runtime workdirs, raw API responses, and
  environment-dependent files as out of scope for deterministic reproducibility
  evidence.

## 2026-06-05 AI plan progress audit

- Added `scripts/audit_ai_plan_progress.py` to turn the execution plan into a
  stage-by-stage status report.
- Latest report: `outputs/plan_progress/latest.md`.
- Current stage counts are 4 complete, 2 partial, and 8 blocked. The blocked
  stages are real-API dependent and require `.env`,
  `configs/model_selection.local.json`, and `configs/api_pilot.local.json`.

## 2026-06-05 human input packet

- Added `scripts/write_human_input_packet.py` to generate an ignored handoff
  packet before real API execution.
- Latest output: `outputs/handoff/human_input_packet.md`.
- The packet now prefers `scripts/bootstrap_api_prereqs.py --dry-run` followed
  by the write/preflight/check-only/execute sequence, and keeps the older
  separate model-selection/API-config commands only as a debugging fallback.
- The packet reports missing required inputs without printing secrets:
  OpenRouter API key presence, concrete model slug, model-selection rationale,
  and local API config.
- The script uses `<repo_root>` instead of local absolute paths so it can be
  safely included in the anonymous artifact.

## 2026-06-05 pre-API handoff

- Added `scripts/write_pre_api_handoff.py` as a one-command local handoff.
- It refreshes readiness, deterministic reproducibility, paper readiness, plan
  progress, goal completion, and human-input reports without calling model APIs.
- Latest report: `outputs/handoff/pre_api_handoff.md`.
- Command display is normalized to `python ...` so the ignored handoff report
  does not expose the local Python installation path.

## 2026-06-05 Git sync packet

- Added `scripts/write_git_sync_packet.py` to document Git sync state without
  initializing or pushing.
- Latest report: `outputs/handoff/git_sync_packet.md`.
- Current state: `research95` is not a Git repository; the old repo remote is
  `https://github.com/gaoming-a/review.git`; using that remote or a new remote
  requires explicit user confirmation before any Git mutation.
- The packet now includes a remote decision record template, staging allowlist,
  ignore checks, cached-diff checks, post-sync acceptance criteria, and an
  explicit ban on `git add .`. This keeps the Git handoff executable by a later
  AI agent while still requiring human confirmation before mutation.
- Added `scripts/audit_git_sync_packet.py` and wired it into
  `scripts/run_local_quality_gate.py`, so Git handoff safety is checked even
  while the workspace remains intentionally uninitialized.
- `scripts/write_pre_api_handoff.py` now refreshes the Git sync packet audit
  and includes it in the authoritative pre-API report list.

## 2026-06-05 model selection shortlist

- Added `docs/experiments/model_selection_shortlist.md` as a decision aid for
  Stage 3.
- The shortlist uses LMArena as the capability-band source and the OpenRouter
  public model catalog API as the availability source.
- It recommends `anthropic/claude-sonnet-4.6` as a conservative first
  single-model pilot candidate, but does not create local config or replace
  user confirmation.

## 2026-06-05 OpenRouter model catalog audit

- Added `scripts/audit_openrouter_model_catalog.py`.
- It checks public OpenRouter catalog visibility for candidate slugs without an
  API key and without creating local config.
- Latest report: `outputs/model_selection/openrouter_catalog_audit.md`.
- Current result: all six shortlist slugs are visible in the public catalog.
- Added `--require-openrouter-catalog` to
  `scripts/create_model_selection_local.py` and
  `scripts/create_api_pilot_local_config.py`. The option is explicit so offline
  dry-runs remain possible, but real local config creation should use it when
  network access is available.

## 2026-06-05 OpenRouter runtime failure handling

- `src/cross_review/openrouter.py` now supports configurable request timeout,
  retry count, and retry backoff through `OPENROUTER_TIMEOUT_SECONDS`,
  `OPENROUTER_MAX_RETRIES`, and `OPENROUTER_RETRY_BACKOFF_SECONDS`.
- OpenRouter HTTP/network errors are sanitized before surfacing so provider
  keys are not copied into tracked outputs or terminal summaries.
- `scripts/run_patch_verification_api_pilot.py` now writes a sanitized
  `run_error.json` when a real API call fails mid-run. That file records the
  candidate, condition, model, completed review count, and error type without
  storing prompts or secrets.
- `scripts/audit_api_run_completeness.py` now fails any run directory that
  contains `run_error.json`; such runs must be rerun and cannot be used as
  experiment results.
- Added `scripts/audit_api_failure_handling.py` and wired it into
  `scripts/run_local_quality_gate.py`. The audit uses a local refused
  connection rather than OpenRouter, checks the sanitized `run_error.json`
  shape, verifies stdout/stderr/error-file secret redaction, and confirms
  completeness rejects the failed run. `SystemExit` writes its message to
  stderr, so the audit intentionally accepts the failure notice from either
  stdout or stderr.
- Added `scripts/write_experiment_run_records.py` and wired it into the local
  quality gate. The script turns existing JSON evidence into the run-record
  format required by the execution plan, while explicitly marking no-API,
  smoke, missing full runs, and quality gates as not eligible for positive
  paper claims.
- `scripts/write_pre_api_handoff.py` now refreshes the run ledger and lists it
  as an authoritative report. `scripts/audit_goal_completion.py` now requires
  the ledger to contain no-API, smoke API, full API, and quality-gate records,
  so a final completion claim cannot omit the experiment record book.

## 2026-06-05 paper draft readiness expansion

- Updated `docs/paper/patch_verification_draft.md` with pre-API
  reproducibility controls and model-selection boundaries.
- Updated `scripts/audit_paper_readiness.py` so methods/negative draft
  readiness requires the paper outline, model-selection docs, reproducibility
  comparison, model catalog audit, and pre-API handoff in addition to the pilot
  report and paper draft.
- Positive paper claims still require real API reviews, metrics, failure
  examples, and a stop/continue gate.

## 2026-06-05 anonymous artifact audit

- Refreshed `artifacts/research95_anonymous_artifact.zip`; current package has
  95 project files plus embedded artifact metadata.
- Added `scripts/audit_anonymous_artifact.py` to inspect the ZIP directly and
  verify required files, manifest consistency, and exclusion rules.
- Updated `scripts/run_local_quality_gate.py` to run the artifact ZIP audit
  when the ZIP exists, while keeping artifact dry-run as the baseline check.

## 2026-06-05 generated paper tables

- Added `scripts/write_paper_tables.py` to generate pre-API Markdown and LaTeX
  tables from current JSON outputs.
- Generated `docs/paper/generated_tables.md` and
  `docs/paper/generated_tables.tex`.
- These tables include dataset composition, executable validation, no-API
  baselines, and deterministic reproducibility. They intentionally exclude real
  model-review results because those do not exist yet.

## 2026-06-05 IEEE pre-API LaTeX draft

- Added `scripts/write_ieee_latex_draft.py`.
- Generated `docs/paper/ieee_preapi_draft.tex` using IEEEtran structure and
  generated pre-API tables.
- The draft explicitly marks real API results as pending and states that
  current no-API baselines are not model-review results.

This file starts fresh for the patch-verification project.

## Rules

- Record only issues that affect the new AI-generated patch-verification
  workflow.
- Do not copy long historical bug logs from the old cross-review project.
- If old behavior matters, summarize it in one paragraph and link to
  `docs/background/previous_findings_summary.md`.

## Initial Notes

- The clean workspace intentionally excludes raw `data/`, `outputs/`, `tmp/`,
  local API keys, local model configs, and old artifact ZIPs.
- Compile checks may create `__pycache__` files with local absolute paths; delete
  them before packaging or scanning.
- Evaluator-facing `patch_id` may encode construction type, so it must not
  appear in model-visible evidence packets. Use anonymous `candidate_id` for
  prompts.
- Do not put words such as `reference_fix`, `buggy_noop`, `irrelevant_patch`,
  `No-op`, or expected outcome labels in any model-visible context.
- The first no-API pilot initially used neutral patch placeholders. The builder
  now materializes unified diffs from retained buggy/fixed checkouts and
  generates 30 validated candidates.
- Cross-task real diffs did not reliably apply across retained BugsInPy
  checkouts. For now, unrelated controls use applicable comment-only source
  diffs; these are low-difficulty controls and must not be presented as the main
  negative class.
- Candidate labels should be treated as usable only after
  `scripts/validate_patch_candidates.py` reports `all_validated = true`.
- API dry-runs only validate prompt rendering and prompt-boundary checks. They
  are not reviewer results and must not be reported as experimental evidence.
- API mock runs only validate the local output and metrics pipeline. They are
  not model results and must not be mixed with real API conditions.
- `scripts/summarize_api_pilot_results.py` can summarize mock runs, but those
  reports must stay under ignored `outputs/` and be treated as reporting-chain
  smoke tests only.
- `scripts/extract_api_failure_examples.py` can also run on mock outputs, but
  mock examples only validate bucket extraction. Qualitative paper examples
  require real API reviews and manual raw-response inspection.
- Run `scripts/preflight_api_pilot.py` before any real OpenRouter call; it
  catches missing `.env`, placeholder model slugs, missing validation summaries,
  and candidate/evidence count mismatches.
- `scripts/run_no_api_patch_pipeline.py` is the preferred fresh-environment
  check. It intentionally creates an ignored dry-run config under the output
  directory and never calls OpenRouter.
- `scripts/create_api_pilot_local_config.py` should be used after model
  selection to avoid hand-editing `configs/api_pilot.local.json`; it does not
  validate credentials, so `scripts/preflight_api_pilot.py` remains mandatory.
- `scripts/validate_model_selection.py` and
  `configs/model_selection.local.json` are now part of the real API gate.
  `preflight_api_pilot.py` fails if the model selection record is missing or
  does not match the API config model.
- `scripts/create_model_selection_local.py` can create the ignored model
  selection record from command-line arguments, preventing malformed manual JSON.
- `scripts/bootstrap_api_prereqs.py` now chains explicit model-selection inputs
  into both ignored local config files, validates the model match, and runs
  preflight. Use `--dry-run` first when handing the task to another agent; the
  script intentionally does not create `.env` or choose a model.
- The bootstrap script now checks `OPENROUTER_API_KEY` before writing local
  config files unless `--allow-missing-credentials` is explicitly set. This
  prevents a failed strict preflight from leaving half-created local config
  files when `.env` is missing.
- `.env.example` now contains only placeholder values and safety comments. It
  is safe for the anonymous artifact; concrete provider keys must stay in the
  ignored `.env` file and must not be copied into tracked docs or outputs.
- `scripts/audit_credential_boundary.py` now checks `.gitignore`,
  `.env.example`, and tracked secret-file state as structured evidence. The
  local quality gate runs this audit in addition to broad sensitive-string
  scanning, so a future real `.env` can exist locally while still remaining
  outside tracked files and anonymous artifacts.
- `scripts/audit_bootstrap_safety.py` now verifies the bootstrap guardrail:
  dry-run must not create local config files, and strict execution without
  `OPENROUTER_API_KEY` must fail before creating temporary local configs. This
  keeps credential-preflight changes testable without real API calls.
- `scripts/audit_workflow_guard.py` now verifies the guarded API workflow
  itself: `--check-only` must report `model_call_attempted = false`, and a
  strict missing-prerequisite run must stop before `reviews.jsonl` or raw
  response files are created.
- `scripts/audit_command_templates.py` now checks the human-input packet and
  key docs for command-template drift. It enforces the intended order:
  bootstrap dry-run with `--allow-missing-credentials`, strict bootstrap write,
  preflight, check-only, then `--execute`.
- Readiness and plan-progress next-action text now also points to the bootstrap
  path instead of the older two-helper workflow. The command-template audit
  checks these script-level prompts so future status reports do not drift away
  from the safer handoff procedure.
- `scripts/run_local_quality_gate.py` now refreshes plan-progress state as
  part of the local report. Blocked or partial stages are reported as project
  state rather than local quality failures, because real API and Git stages
  still require human inputs.
- `scripts/prepare_anonymous_artifact.py` now writes a richer embedded
  `ARTIFACT_README.md` with no-API reproduction, quality gates, credential
  checks, bootstrap checks, command-template checks, handoff, and guarded API
  command templates. `scripts/audit_anonymous_artifact.py` validates that these
  README snippets are present inside the ZIP.
- `scripts/evaluate_api_pilot_gate.py` is the required post-run guardrail
  before writing positive claims. A mock run must produce `not_evidence`, and a
  real run with weak or collapsed metrics must be treated as stop/redesign.
- `scripts/audit_execution_readiness.py` is the current-turn status entry
  point. It reports no-API readiness, missing `.env` or local config, and the
  fact that `research95` is not currently a Git repository.
- `scripts/audit_paper_readiness.py` should be run before expanding the paper
  beyond the pre-API methods draft. Current state should report missing real API
  reviews, API report, failure examples, and gate report.
- `scripts/prepare_anonymous_artifact.py` generated the current anonymous
  package successfully after tightening validation to allow `.env.example`
  placeholders while still rejecting concrete keys, local paths, local configs,
  raw outputs, and benchmark checkouts.
- `scripts/postprocess_api_pilot_run.py` is the preferred post-run entry point.
  On the mock smoke output it regenerated all reports and returned
  `gate_verdict = not_evidence` with `positive_claim_ready = false`, as
  expected.
- `scripts/run_api_pilot_workflow.py` is the guarded real API entry point. It
  supports `--check-only` without API calls and requires explicit `--execute`
  after strict preflight before any model call. It now records
  `model_selection_validation.json`; missing model-selection files are reported
  as structured failures rather than Python tracebacks.
- `scripts/create_api_pilot_local_config.py` and
  `scripts/bootstrap_api_prereqs.py` now emit guarded workflow next commands.
  Direct `run_patch_verification_api_pilot.py` use should stay limited to
  prompt dry-runs, mock checks, or workflow-internal execution.
- The low-level runner now rejects direct real API execution unless
  `run_api_pilot_workflow.py` supplies its internal `--allow-direct-api-run`
  flag. `scripts/audit_workflow_guard.py` verifies this path without making API
  calls.
- The workflow now forwards `--run-dir` and `--limit` to the API runner.
  Explicit `--limit 0` means a full 30-candidate run and is no longer replaced
  by config `smoke_limit=2`. The workflow refuses to overwrite an existing
  `reviews.jsonl` unless `--allow-existing-output` is passed intentionally.
- Added `scripts/audit_api_run_completeness.py` and wired it into
  `scripts/postprocess_api_pilot_run.py` and the guarded workflow. Smoke runs
  should pass `--expected-candidates 2`; full runs should pass
  `--expected-candidates 30`. Paper readiness now requires
  `run_completeness.json` with 60 non-mock review records.
- API review records now include `raw_response_sha256`. The completeness audit
  verifies that each raw response path exists under the run directory, parses as
  JSON, and matches the recorded hash, and that required review fields are
  present.
- Do not run `prepare_anonymous_artifact.py` and `audit_anonymous_artifact.py`
  in parallel against the same ZIP path. The audit can observe a partially
  written archive and raise `BadZipFile`. Generate the ZIP first, then audit it
  as a separate step.
- `scripts/write_human_input_packet.py` now includes both smoke and full
  postprocess commands. `scripts/audit_command_templates.py` checks that smoke
  uses `--expected-candidates 2` and full run uses `--expected-candidates 30`.
- `scripts/audit_ai_plan_progress.py` now also requires this 60-record
  non-mock run-completeness evidence before marking Stage 8 postprocess
  complete.
- `scripts/run_local_quality_gate.py` is the preferred end-of-turn local gate.
  It passed after dynamic construction of sensitive-scan patterns so the scanner
  no longer flags its own rule strings. Passing this gate does not mean real API
  readiness; it reports API readiness separately.
- `scripts/audit_goal_completion.py` is the whole-objective guardrail. It keeps
  `complete = false` until no-API readiness, reproducibility, real full API
  reviews, postprocess outputs, non-mock failure examples, a positive paper
  gate, artifact safety, local quality, and Git repository/remote evidence are
  all present.

## 2026-06-05 DeepSeek official API switch

- The current primary execution path is DeepSeek official API with
  `api_provider = deepseek_official` and `model = deepseek-v4-pro`; OpenRouter
  support remains only as an alternative provider path.
- `scripts/bootstrap_api_prereqs.py`, `scripts/preflight_api_pilot.py`,
  `scripts/run_patch_verification_api_pilot.py`, model-selection validation,
  readiness audits, and command-template audits are now provider-aware.
- A real-looking DeepSeek key was found in `.env.example` and removed. The
  quality gate and artifact packager now scan for concrete `DEEPSEEK_API_KEY`
  assignments in tracked/packageable text, not only OpenRouter keys.
- The strict bootstrap safety audit uses an intentionally missing env file
  under `outputs/bootstrap_safety/`, so it does not accidentally pass because
  the developer's real `.env` exists.
- Verified locally without model calls: compileall passed, credential boundary
  passed, bootstrap safety passed, command templates passed, readiness reports
  `overall_ready_for_real_api = true`, and guarded workflow check-only reported
  `model_call_attempted = false`.

## 2026-06-05 DeepSeek smoke result

- First real DeepSeek smoke at `outputs/patch_verification_api_pilot_001`
  generated 4 non-mock review records and passed run completeness, but 2/4
  outputs were invalid. The invalid records had `finish_reason = length`,
  empty final `content`, and all completion tokens spent in `reasoning_content`.
- Root cause: `max_tokens = 1200` was too low for DeepSeek V4 reasoning on the
  larger reference-fix candidate, so the final JSON never appeared.
- Fixed `scripts/run_patch_verification_api_pilot.py` so config values for
  `temperature` and `max_tokens` actually override runner defaults. Updated API
  pilot config to `max_tokens = 4096`.
- Second smoke at `outputs/patch_verification_api_pilot_001_tokens4096`
  generated 4 non-mock review records, passed completeness, and had invalid
  output rate 0. This validates the execution chain and schema stability.
- The smoke gate is still `indeterminate`; it is too small for research claims.
  It only justifies moving to the 30-candidate full run, not writing positive
  paper results.

## 2026-06-05 Git initialization boundary

- After initializing `research95` as a Git repository, the credential-boundary
  audit initially misclassified tracked `.env.example` as a secret file because
  it matched the `.env.*` tracked-file pattern.
- `.env.example` is the intentionally tracked template and must remain allowed;
  concrete `.env`, `.env.*` variants other than `.env.example`, key files, and
  `configs/*.local.json` must remain untracked.
- `scripts/audit_credential_boundary.py` now filters `.env.example` out of the
  tracked-secret-file list while still validating that the template contains
  only placeholders.

## 2026-06-05 DeepSeek full run result

- Full run directory: `outputs/patch_verification_api_pilot_002`.
- The run completed with 60 non-mock review records, 30 candidates, 2
  conditions, no `run_error.json`, raw response hashes present, and
  `run_completeness.json` passed.
- Gate verdict: `stop_or_redesign`.
- Evidence-first improved safety metrics: false accept rate 0.0000 versus
  0.0909 for llm-only, and accepted precision 1.0000 versus 0.7143.
- Evidence-first also reduced correct-patch recall: 0.7143 versus 1.0000 for
  llm-only. The drop is 0.2857, exceeding the configured `max_recall_drop=0.25`.
- This is a mixed/negative result. Do not write a positive claim that
  evidence-first is better. The honest claim is that it removed observed false
  accepts in this pilot but at too high a recall cost under the configured gate.
- Next research step should inspect `failure_examples.md` and decide whether to
  redesign the evidence packet/prompt or pivot the paper toward merge-gate
  safety/utility tradeoffs.

## 2026-06-05 DeepSeek failure-analysis lesson

- The full-run failure analysis is now tracked in
  `docs/experiments/deepseek_full_run_failure_analysis.md`.
- The important failure is not simply model capability. `llm_only` accepted two
  partial `httpie_1` patches because they looked behaviorally plausible, while
  `evidence_first` refused or rejected two correct reference fixes because the
  evidence packet did not include the test body, failing behavior, oracle
  output, or claim-level trace needed to justify acceptance.
- Do not scale `patch_verify_evidence_first_v1` as-is. It would mostly scale a
  known evidence-poverty failure mode.
- The next experiment should be a failure-case-only redesign smoke with a
  clearly named tool/evidence-augmented condition. If that smoke cannot recover
  recall on the known reference-fix failures, the honest paper direction is a
  negative/methods claim about prompt-only merge-gate limits.

## 2026-06-05 redesign smoke config override bug

- While preparing `tool_augmented_evidence`, dry-run unexpectedly rendered 10
  prompts for `llm_only` and `evidence_first` instead of 5 prompts for the new
  condition.
- Root cause: `scripts/run_patch_verification_api_pilot.py` gave argparse a
  non-`None` default for `--conditions`, so `apply_config()` treated conditions
  as already set and did not load the config value.
- Fix: `--conditions` now defaults to `None`, and `apply_defaults()` fills the
  old two-condition default only after config values have been applied.
- Rule: if a new condition is driven by config, dry-run must prove the rendered
  manifest contains only that condition before any real API call.

## 2026-06-05 tool-augmented redesign smoke

- After fixing the config override bug, dry-run rendered exactly five
  `tool_augmented_evidence` prompts for the five known failure cases.
- The actual rendered prompt boundary scan found no evaluator labels, old
  evaluator patch ids, or local paths.
- Real DeepSeek smoke at `outputs/patch_verification_redesign_smoke_001`
  completed with 5 non-mock records, completeness passed, and invalid output
  count 0.
- Decisions matched the smoke gate: reference fixes `candidate_0001` and
  `candidate_0023` were accepted; partial fixes `candidate_0005`,
  `candidate_0006`, and `candidate_0020` were rejected.
- Treat this as evidence that tool-visible execution summaries can repair the
  known failure cases. It is not evidence that the original prompt-only
  `evidence_first` condition succeeded.

## 2026-06-05 tool-augmented full run

- After the user confirmed the route, the paper framing was revised before the
  full run: tool-augmented verification is a separate condition, not a rescue
  of prompt-only evidence-first.
- Built 30-candidate full-run inputs under
  `outputs/patch_verification_tool_augmented_full_001/inputs` with
  `--all-candidates`.
- Dry-run produced exactly 30 `tool_augmented_evidence` prompts, and direct
  rendered-prompt scanning found no evaluator labels, old evaluator patch ids,
  or local paths.
- Real DeepSeek full run completed with 30 non-mock records, completeness
  passed, and `tool_augmented_full_gate.json` passed.
- Metrics: false accept rate 0.0, accepted precision 1.0, correct-patch recall
  1.0, false reject rate 0.0, escalation rate 0.0, invalid-output rate 0.0.
- Interpret this as conditional tool-assisted verifier evidence. The result
  depends on visible executable behavior summaries and must not be described as
  prompt-only model-review ability.

## 2026-06-05 dual-claim audit repair

- After the tool-augmented full run passed, the old readiness scripts still
  treated the original prompt-only `stop_or_redesign` gate as the only path to
  a positive claim.
- Root risk: future execution would either keep reporting the new direction as
  blocked, or incorrectly rewrite the prompt-only negative result into a
  success.
- Fix: `scripts/audit_paper_readiness.py`, `scripts/audit_ai_plan_progress.py`,
  and `scripts/audit_goal_completion.py` now report prompt-only readiness and
  tool-augmented conditional readiness as separate checks.
- Rule: never change the old `positive_claim_ready=false` into true unless the
  prompt-only gate itself changes. The supported positive result is
  `tool_augmented_claim_ready=true`, bounded to tool-assisted verification.

## 2026-06-05 IEEE submission draft generation

- The Markdown paper draft already contained the real API and tool-augmented
  full-run results, but `docs/paper/ieee_preapi_draft.tex` still described a
  pending API pilot.
- Fix: `scripts/write_ieee_latex_draft.py` now generates
  `docs/paper/ieee_submission_draft.tex` as the current IEEEtran submission
  draft and leaves the old pre-API file as historical context.
- Initial generation bug: the prompt-only evidence-first result row was empty
  because `metrics.json` stores condition groups with provider-qualified keys
  such as `evidence_first::evidence_first__deepseek-v4-pro`.
- Repair: the script now resolves condition groups by prefix and reads the
  tool-augmented row from `tool_augmented_full_gate.json`.
- Verification: direct `pdflatex` compilation succeeded and produced a 4-page
  PDF under ignored `outputs/latex_build`. `latexmk` is unavailable because the
  local MiKTeX installation lacks Perl.

## 2026-06-06 publication figure generation

- Generated a reproducible figure set with `scripts/generate_paper_figures.py`
  instead of using non-reproducible bitmap generation.
- Outputs are written under `docs/figures/` in PDF, SVG, and PNG formats.
- Initial visual QA found overlap in `fig1_framework`: the execution-evidence
  note collided with the decision boxes. The script was repaired by reducing
  title size and moving the note below the verifier path.
- The IEEE draft now imports `graphicx` and references five PDF figures:
  framework, evidence visibility, dataset composition, result tradeoff, and
  claim boundary.
- Direct `pdflatex` compilation succeeded after figure insertion and produced a
  5-page PDF under ignored `outputs/latex_build`.

## 2026-06-06 imagegen visual candidates

- Generated four raster PNG candidates with the built-in `$imagegen` workflow:
  framework, evidence-boundary, tradeoff, and claim-boundary panels.
- Stored project copies under `docs/figures/imagegen/` and recorded exact
  prompts in `docs/figures/imagegen/prompts.md`.
- Rule: these imagegen outputs are conceptual visual assets for graphical
  abstracts, presentations, or visual drafts. They must not replace exact
  Matplotlib-generated vector figures when the figure is used as experimental
  evidence.

## 2026-06-08 final paper roadmap

- Saved the evaluated 90+ final-paper route as
  `docs/plans/final_paper_roadmap_zh.md`.
- The roadmap deliberately remains separate from `current_plan_zh.md`: it is a
  long-term route for an evidence-visibility empirical study, not the next
  mandatory execution baseline.
- Rule: do not jump directly to 80 bugs / 240 patches. First strengthen the
  current pilot with tool-only baselines and qualitative cases, then expand to
  15-20 bugs, and only enter larger data expansion after the pipeline remains
  stable.

## 2026-06-08 six-step prerequisite execution

- Added the long-term PatchEvidenceBench schema and leakage policy before
  expanding data. This prevents hidden evaluator results from being mixed into
  model-visible evidence.
- Implemented `scripts/run_tool_only_baseline.py` with two conditions:
  `tool_only_apply_only` and `tool_only_validation_summary`.
- Current metrics show why the boundary matters: apply-only is safe but
  unusable because it escalates all 30 candidates; validation-summary is perfect
  on the pilot but uses retained executable validation and must be treated as a
  tool-summary/oracle-style comparison.
- Generated a qualitative case report covering LLM-only false accepts,
  evidence-first recall loss, tool-only contrast, and tool-augmented repair.
- Screened the retained BugsInPy workspace: 22 tasks were eligible at checkout
  level and 15 were selected for the next registry. This is not yet an expanded
  validated dataset; each new task still needs an oracle wrapper and candidate
  validation.

## 2026-06-08 subsequent target designation

- `docs/plans/final_paper_roadmap_zh.md` is now the canonical subsequent
  research target for this project.
- Future work should use that roadmap as the source of next tasks, while still
  updating `docs/plans/current_plan_zh.md` before each concrete execution
  round.
- Boundary: this designation does not start the full 90+ route automatically;
  execution should proceed through Stage A/B and the existing 15-task expansion
  registry first.

## 2026-06-08 documentation cleanup

- Problem: README, current plans, and early experiment-plan files still mixed
  old API/pre-API "next step" wording with the newer final-paper roadmap. This
  could cause a future agent to restart completed prompt-only or
  tool-augmented runs instead of following the final roadmap.
- Fix: make `docs/plans/final_paper_roadmap_zh.md` the only final-paper route,
  keep `docs/plans/current_plan_zh.md` as the per-turn execution log, and mark
  older execution plans as historical/reference material.
- Rule: when a document describes a completed experiment, keep the result and
  command context, but rewrite any active "next step" language into completed
  status plus a pointer to the current roadmap.

## 2026-06-08 httpie Stage A/B slice

- The five selected `httpie` expansion tasks already had task-specific oracle
  files under `scripts/oracles/`. The missing piece was not oracle authoring but
  producing a separately bounded Stage A/B run instead of reusing the old
  seven-task pilot as if it were a new expansion result.
- Added filtered build support to `scripts/build_patch_verification_dataset.py`
  with `--task-id` and `--run-id`. Default behavior remains the original full
  built-in pilot, so existing quality gates and reports are not disturbed.
- `httpie_stage_ab_001` produced 22 candidates from five tasks, validated
  22/22 with apply + oracle checks, rendered 44 dry-run prompts, and generated
  tool-only baseline metrics.
- Rule: when a screened task group is promoted from registry to dataset slice,
  create a new run id and tracked result document; do not silently reinterpret
  an older pilot as expansion evidence.

## 2026-06-08 AI patch generation attempt

- Added `scripts/generate_ai_patch_candidates.py` for DeepSeek official API
  patch generation and `scripts/relabel_ai_patch_candidates.py` for
  post-validation outcome relabeling.
- Initial generator behavior was too brittle: it wrote candidate files only
  after the whole 10-patch run completed. When one response exhausted all
  output tokens in reasoning and returned empty final content, previously
  saved raw responses were not converted into candidates.
- Repair: generator now writes prompt manifest and pending candidates
  incrementally, reuses parseable raw responses, and stores retry attempts as
  separate raw files.
- Result: 10 AI patches were generated, but only 4 applied cleanly and 6 failed
  `git apply`. This is diagnostic generator-pipeline evidence, not a usable
  verifier experiment slice.
- Rule: for AI-generated patch datasets, generation success must be measured by
  apply + oracle validation, not by receiving a model response. If apply
  failure is high, stop and redesign the generation protocol before verifier
  API calls.

## 2026-06-08 strict agent generation with Qwen

- Added Qwen official API support through the OpenAI-compatible client using
  `QWEN_API_KEY` and optional `QWEN_BASE_URL`.
- Qwen solved the DeepSeek empty-final-content failure mode for
  `bugsinpy_httpie_5`: it returned structured JSON and a plausible edit plan.
- Under strict mode, the edit plan still failed because its `find` snippet did
  not match the buggy source exactly. The user explicitly rejected fuzzy apply,
  so the attempt was recorded as a strict generation failure.
- Rule: exact edit-plan mode is clean but brittle. If it blocks too many
  candidates, the project must either accept lower yield, allow controlled
  fuzzy apply with explicit paper wording, or switch to a true tool-using agent
  that can inspect and revise its edits before emitting the final diff.

## 2026-06-09 Qwen 3.7 Plus strict agent retry

- `qwen3.7-plus` generated one strict exact-match edit plan for
  `bugsinpy_httpie_5`; the script applied it in a copied checkout and exported a
  real `git diff`.
- The candidate applied cleanly and the retained oracle ran, but the oracle did
  not pass. This makes it a validated generated negative candidate, not a
  repair.
- The second candidate timed out after 3 provider attempts. Treat this as
  provider/run instability and do not infer semantic failure from the missing
  candidate.
- Fixed generator metadata so the candidate `source` field records the selected
  API provider instead of always using `deepseek_official_agent_edit`.
- Rule: successful materialization and semantic correctness must remain separate
  gates. A generated patch can be valuable for the verifier dataset even when it
  is incorrect, as long as apply + oracle validation is reproducible.

## 2026-06-09 DeepSeek agent-style patch validation

- Validated the 8 existing DeepSeek agent-style candidates from
  `httpie_agent_patch_stage_ab_001`; no new API calls were made.
- All 8 patches applied cleanly and all 8 retained oracles ran. This confirms
  that agent-style edit plans plus local `git diff` are much more reproducible
  than direct model-written unified diffs for this slice.
- All 8 retained oracles failed, so every candidate relabeled as `incorrect`.
  The protocol produced good generated negative samples, not correct repairs.
- Decision rule: do not expand AI-generated patches as the main balanced dataset
  source until the generator can produce both oracle-passing and oracle-failing
  patches. Use them as an extension for generated-negative or partial-fix
  verifier stress tests.

## 2026-06-09 final roadmap task-set reconstruction

- Do not change the research line from patch verification to patch generation.
  The central question remains whether verifiers accept, reject, or escalate
  candidate patches under different evidence visibility conditions.
- A task can be valuable even if no generator solves it. If validation is stable,
  keep it as a hard-generation or stress case and report generator success rate.
- Exclude a task only when reproducible validation fails: unstable environment,
  flaky tests, invalid reference patch, unreliable labels, or uncontrolled
  runtime.
- `httpie_5` should not be a main success case or a prompt-tuning target. If its
  oracle and reference validation remain stable, keep it with capped weight:
  one reference correct patch, a few generated incorrect patches, and at most
  one constructed partial/control patch.
- Rule: dataset balance is required at the dataset level, not per bug. Each bug
  does not need an AI-generated correct repair.

## 2026-06-09 httpie5 task accounting audit

- Rebuilt a single-task `httpie_5` slice and validated it twice. Both runs
  produced 6/6 validated labels: one reference patch passed the retained oracle,
  and five negative/control candidates failed as expected.
- Added `scripts/build_task_generation_accounting.py` to merge validation
  records, relabeled generated candidates, and prompt manifests into task-level
  accounting metadata.
- Current `httpie_5` accounting: 7 generation attempts, 3 admitted generated
  patches, 1 applicable incorrect patch, 2 environment-invalid patches, and 0
  correct generated patches.
- Decision: keep `httpie_5` as `hard_generation_case` with capped candidate
  weight. Do not use it as a main generation success case.
- Boundary: broad pass-to-pass regression stability is not separately measured
  by the current retained-oracle audit. Do not describe `httpie_5` as fully
  regression-stability audited until a pass-to-pass suite is defined.

## 2026-06-09 httpie5 P2P-broad scope

- Implemented `scripts/build_pass_to_pass_scope.py` to define P2P scope before
  using it for candidate labels. The script creates a compatibility shim for
  legacy `requests.compat.is_py26` imports and records that shim in the output.
- Direct per-test execution was initially too slow because each pytest process
  has high startup overhead and the suite contains external-network tests.
  Static exclusion of test methods containing `httpbin`, `http://`, or
  `https://` made the scope construction tractable and auditable.
- For `httpie_5`, 17 tests were collected, 1 retained fail-to-pass oracle was
  excluded, 13 external-network tests were excluded, and 3 stable local
  P2P-broad tests remained.
- `scripts/validate_candidates_with_p2p.py` labeled the 6 current candidates:
  one `correct_under_f2p_and_p2p_broad` reference patch and five
  `incorrect_issue_not_fixed` candidates.
- Rule: P2P-broad is an environment-specific stable runnable subset. Always
  report collection counts and exclusion reasons; do not describe it as the
  original project's full test suite.

## 2026-06-09 Luigi replacement tasks

- Built retained-oracle candidate slices for `bugsinpy_luigi_3` and
  `bugsinpy_luigi_4`; both repeated validations were stable.
- Extended P2P compatibility handling for old Luigi tests: Python 3.11
  `collections`/`inspect` compatibility, `mock` mapped to `unittest.mock`, and
  a lightweight `psutil` shim for import-time compatibility.
- Per-test P2P execution was too slow for Luigi 3. Added batch-first P2P scope
  construction and chunked candidate P2P validation.
- Luigi 3 result: 137 tests collected from `test/parameter_test.py`, 1 retained
  fail-to-pass oracle excluded, 1 static external dependency excluded, 135
  P2P-broad tests retained.
- Luigi 4 result: 14 tests collected from `test/contrib/redshift_test.py`, 1
  retained fail-to-pass oracle excluded, 13 P2P-broad tests retained.
- Boundary: current Luigi P2P-broad scopes are task-file stable subsets, not a
  project-wide Luigi regression suite. This needs a final design decision
  before claiming project-wide P2P coverage.

## 2026-06-10 project-level P2P-broad rebuild

- Final main labels should use `project_level_p2p_broad`, not task-file P2P
  scopes. Task-file scopes remain useful for smoke checks and appendix
  discussion only.
- `scripts/build_pass_to_pass_scope.py` now supports project-level test-file
  discovery, checkout-independent nodeid normalization, manifest output,
  Windows-safe batch chunking, and file-grouped batch validation.
- Legacy projects may not collect tests with `pytest .`. For `httpie_5`, the
  script must explicitly discover `tests.py`; otherwise project-level collection
  returns zero tests even though `tests/tests.py` is valid.
- `httpie_5` project-level P2P-broad completed with 17 collected tests, 1
  fail-to-pass oracle exclusion, 13 external-dependency exclusions, and 3
  included P2P-broad tests over 3 stability runs per version.
- `validate_candidates_with_p2p.py` now emits
  `correct_under_f2p_and_p2p_broad` for the positive final label.
- Luigi project-level P2P is not just a matter of using the task-file command on
  a larger path. Luigi 3 discovers 113 test files and 904 nodeids, with 44
  collection errors in external-service/contrib areas. Two construction attempts
  exceeded local execution limits even after file-grouped batching.
- Do not silently downgrade Luigi to task-file P2P for final labels. Either
  build collection-error manifests plus stability caches for strict
  project-level P2P, or mark Luigi as `project_level_p2p_pending` and use
  smaller replacement tasks for final project-level main labels.

## 2026-06-10 Luigi freeze and cohort gating

- Final decision: do not continue brute-force Luigi project-level P2P in the
  current phase. Mark Luigi as `pending_blocked`, retain task-file P2P only as
  appendix/smoke evidence, and prioritize smaller replacement tasks with
  completed project-level P2P-broad manifests.
- Added `data/cohorts/task_cohort_registry.json` as the tracked source of truth
  for main-cohort inclusion. Current state: `bugsinpy_httpie_5` is
  `p2p_broad_main`; `bugsinpy_luigi_3` and `bugsinpy_luigi_4` are
  `blocked_or_pending` plus `p2p_local_smoke`.
- Main metrics should include only tasks where
  `project_level_p2p_status == completed` and `p2p_broad_main_included is
  true`.
- `scripts/analyze_patch_verification.py` now applies this filter by default
  when the cohort registry exists. Use `--no-cohort-filter` only for appendix or
  diagnostic runs.
- `scripts/build_task_generation_accounting.py` now reads the same cohort
  registry and overrides `main_experiment_included` for blocked tasks, so Luigi
  task-file labels do not leak into final main accounting.

## 2026-06-10 bounded replacement sweep

- Tried `bugsinpy_httpie_1` through `bugsinpy_httpie_4` as quick replacement
  candidates because they already existed in the Stage A/B validated `httpie`
  slice.
- Updated test discovery to ignore bundled virtual environments (`env`, `venv`,
  `.venv`) after `httpie_1` initially exposed hundreds of dependency package
  tests from `env/Lib/site-packages`.
- Updated project-level collection to run per test file. A single collection
  error should not erase all otherwise collectable nodeids for a project.
- `httpie_1` remains blocked because its tests require the real
  `pytest_httpbin` plugin from `tests/conftest.py`. Do not fake this fixture for
  main labels; it changes the test environment semantics.
- `httpie_4` needed additional old `requests.compat` fields such as
  `is_windows`, `is_py3`, and `bytes`. This compatibility shim is acceptable
  because it restores removed compatibility constants, but the project-level
  scope still exceeded the bounded sweep runtime.
- `httpie_2` and `httpie_3` also exceeded the bounded project-level P2P runtime.
  They are recorded as `pending_blocked`, not silently removed.
- Current lesson: replacement-task screening should happen before candidate
  expansion. Prefer projects with no required service fixtures, no bundled
  virtualenv inside the checkout, and project-level collection that finishes
  within the predefined budget.

## 2026-06-10 tqdm feasibility sweep

- `bugsinpy_tqdm_1` and `bugsinpy_tqdm_2` have much smaller test-file counts
  than Luigi, but most test files require the legacy `nose` dependency.
- Both tasks completed bounded project-level scope construction, but each
  retained only one stable P2P-broad test:
  `tqdm/tests/tests_version.py::test_version`.
- Because the main threshold is `p2p_broad_size >= 3`, both tasks are recorded
  as `completed_insufficient_p2p_broad` and excluded from `p2p_broad_main`.
- Do not silently install or emulate `nose` for main labels. Treat dependency
  installation as a separate environment decision because it changes the
  reproducibility contract.

## 2026-06-10 unittest adapter and black sweep

- Added a bounded `unittest` adapter to `scripts/build_pass_to_pass_scope.py`.
  The adapter uses standard-library discovery and runner execution and emits
  the same P2P manifest shape as pytest scopes.
- `_FailedTest` entries from unittest discovery must be recorded as collection
  errors, not as runnable tests. Otherwise a failed module import can be
  mistaken for one collected test.
- When `--manifest-out` is used and collection errors exist, the script now
  writes a tracked sibling collection-error manifest under `data/p2p_scopes/`.
- `bugsinpy_black_1` and `bugsinpy_black_3` both failed project-level unittest
  collection because importing `black` requires `typed_ast`. The dependency is
  listed in the BugsInPy requirements, but it was not installed silently during
  this sweep.
- Result: both black tasks are `pending_blocked`, not unsupported-framework
  failures. The framework adapter works enough to expose the real environment
  dependency blocker.
- A confirmed attempt to install `typed-ast==1.4.0` in an isolated Python 3.11
  venv failed because pip had to build the extension from source and the machine
  lacks Microsoft Visual C++ 14.0+ Build Tools. The failed venv was removed.
  Do not retry the same Python 3.11 installation path without changing one of:
  system build tools, Python version, or the allowed dependency version.

## 2026-06-10 cookiecutter feasibility sweep

- `bugsinpy_cookiecutter_1` reached project-level pytest discovery but collected
  zero nodeids because collection failed before executable test selection.
- First blocker: the retained checkout's `setup.cfg` supplied pytest-cov
  arguments. The repair was not to install pytest-cov, but to implement an
  audited sanitizer that removes only coverage options and preserves the rest
  of `addopts`.
- The sanitizer correctly transformed
  `-vvv --cov-report term-missing --cov=cookiecutter` into `-vvv`, but the
  retry then exposed real missing dependencies: `poyo`, `binaryornot`, and
  `freezegun`.
- After explicit approval, an isolated Python 3.11 venv under ignored
  `outputs/envs/` installed the Cookiecutter runtime/test dependencies needed
  for P2P while still excluding pytest-cov. Passing the venv Python explicitly
  as both the script runner and `--python` test interpreter mattered; a prior
  relative-path run left mixed system/venv Python processes and had to be
  terminated manually.
- Pytest 9 plus retained `-vvv` addopts emits tree-form `--collect-only` output
  instead of nodeid lines. The scope builder now parses tree output and maps
  parametrized nodeids back to their source segments for static exclusions.
- Result at this stage: `cookiecutter_1` had 296 common nodeids and 290
  P2P-broad tests over 3 stability runs per version. It still needed
  fail-to-pass oracle and candidate validation before main inclusion; that
  follow-up is recorded in the next note.

## 2026-06-10 cookiecutter candidate validation

- The `cookiecutter_1` retained buggy checkout lacks the original
  `non_ascii.json` test fixture while the fixed checkout contains it. The
  migrated oracle should create its own temporary UTF-8 JSON file and assert
  behavior directly; otherwise the label can conflate source behavior with test
  fixture presence.
- On this Windows environment, the Cookiecutter checkout contains `docs/*.md`
  reparse point/junction entries. `shutil.copytree` fails on them when building
  candidate workdirs. Candidate validation now skips symlink/reparse-point
  entries during checkout copying; these documentation links are not inputs to
  the retained oracle, patch diff, or P2P scope.
- Candidate-level P2P validation must reuse the P2P scope manifest's audited
  pytest addopts override. Without `-o addopts=-vvv`, pytest reads the original
  coverage options from `setup.cfg`, fails because `pytest-cov` is intentionally
  absent, and can falsely mark the reference patch as a regression.
- `cookiecutter_1` now has one reference candidate labeled
  `correct_under_f2p_and_p2p_broad` and three negative/control candidates
  labeled `incorrect_issue_not_fixed` over 290 P2P-broad tests. It is admitted
  to `p2p_broad_main`, but this does not make the final dataset large enough.

## 2026-06-10 cookiecutter_2 candidate validation

- The retained workspace for `cookiecutter_2` lacks BugsInPy metadata files
  such as `bugsinpy_bug.info` and `bugsinpy_run_test.sh`; derive the behavior
  from buggy/fixed source diff and tests, and document that inference rather
  than pretending original metadata exists.
- `tests/test_hooks.py::TestFindHooks::test_find_hook` is not a stable retained
  oracle in the retained checkout because `tests/test-hooks` already exists and
  setup fails with `FileExistsError`. Use direct behavior validation instead.
- The stable F2P node is
  `tests/test_hooks.py::TestExternalHooks::test_run_hook`: buggy fails because
  only one matching hook runs; fixed passes because all matching hooks run.
- A standalone oracle should create its own temporary template repository with
  two matching `pre_gen_project` hooks and assert that both marker files are
  produced. This avoids relying on mutable in-repo test fixture directories.
- `cookiecutter_2` now contributes 11 validated candidates: one reference
  correct patch, one no-op, one irrelevant patch, and eight partial fixes. Its
  project-level P2P-broad scope retains 278 tests, so it is admitted to
  `p2p_broad_main`.

## 2026-06-11 cookiecutter_3 candidate validation

- `cookiecutter_3` has complete BugsInPy metadata, and its original F2P command
  targets `tests/test_read_user_choice.py::test_click_invocation`.
- The first direct F2P run exposed a missing declared dependency:
  `future>=0.15.2`, required for `past.builtins`. Installing pinned
  `future==0.18.3` in the ignored Cookiecutter venv restored this import.
- The first project-level P2P scope still had 18 collection-error files due to
  missing `whichcraft`, also declared in `setup.py`. Installing pinned
  `whichcraft==0.6.1` in the same ignored venv reduced collection errors to
  zero.
- Parameterized F2P tests should be passed as explicit parameterized nodeids to
  the P2P scope builder. Passing only the parent nodeid excluded them as buggy
  baseline failures, which was semantically safe but produced unclear
  accounting.
- A task-specific negative for this single-line prompt bug can set
  `show_choices=True`: it edits the relevant argument but preserves the
  duplicated-choice behavior.
- `cookiecutter_3` now contributes four validated candidates over 255 stable
  P2P-broad tests and is admitted to `p2p_broad_main`.

## 2026-06-11 tqdm_9 candidate validation

- `bugsinpy_tqdm_9` avoided the `tqdm_1/2` `nose` blocker because its retained
  checkout has a compact `tqdm/tests/tests_tqdm.py` suite that collected 14
  pytest nodeids without collection errors.
- Its retained oracle must cover both visible failures:
  `test_si_format` and `test_update`. A single SI-format check would miss the
  `__len__` behavior fixed in the same reference patch.
- Generic partial-diff generation is unsafe when the reference patch mixes bug
  fixes and style-only edits. The first `tqdm_9` candidate pass produced six
  `partial_fix` records that still passed the retained oracle. These records
  were filtered out with a task-level partial allowlist before final validation.
- Rule: every generated partial negative must be validated under the retained
  oracle before it can enter the dataset. Do not assume that omitting any
  reference diff hunk creates a behaviorally incorrect patch.
- `bugsinpy_tqdm_9` now contributes seven validated candidates over 12 stable
  P2P-broad tests and is admitted to `p2p_broad_main`.

## 2026-06-11 sixth-task screening boundary

- After `tqdm_9`, the remaining retained selected candidates were
  `black_2` and `tqdm_3` through `tqdm_8`.
- `black_2` has a clear `fmtonoff4` behavior test in `tests/test_black.py`, but
  importing `black` fails before test execution because `typed_ast` is absent.
  This is the same dependency class as `black_1/3`; do not silently install or
  emulate it.
- `tqdm_3` through `tqdm_8` collect only
  `tqdm/tests/tests_version.py::test_version` without new dependencies. The
  behavior-relevant test files still fail through the legacy `nose` path.
- Rule: do not downgrade these tasks to main cohort entries with a one-test
  P2P-broad scope. The next expansion needs an explicit environment decision
  for legacy dependencies or a broader BugsInPy project import.

## 2026-06-11 broader BugsInPy candidate pool

- The user confirmed the broader-project route: do not spend the next phase on
  legacy `nose` or Black `typed_ast` / MSVC repair.
- The local BugsInPy source archive is available at
  `D:/mgao/code/research/tmp/bugsinpy_archive/BugsInPy-master`; no network
  download is needed for metadata screening.
- `scripts/screen_bugsinpy_candidate_pool.py` performs metadata-only screening
  before checkout. The first run found 501 BugsInPy tasks, 479 new tasks not in
  the current registry, and 195 promising metadata-level candidates.
- Top low-friction candidates are `PySnooper_1-3`, followed by several
  `fastapi` and `sanic` pytest tasks. Heavy/native projects such as
  `keras`, `pandas`, and `spacy` are deprioritized by metadata blockers.

## 2026-06-11 PySnooper_1 candidate validation

- PySnooper's retained checkout needs the existing Python 3.11
  `collections.abc` compatibility shim before either buggy or fixed F2P can run.
  This is a runtime-compatibility shim, not a behavior patch.
- After the shim, the test suite requires `python-toolbox`, which is declared in
  `setup.py` under `extras_require['tests']`. Install such dependencies only in
  ignored isolated venvs and track a dependency audit; do not install them
  globally.
- The stable F2P behavior is `tests/test_chinese.py::test_chinese`: buggy fails
  with a UTF-8 log read error, fixed passes. A standalone oracle should create
  its own temporary snoop log and assert non-ASCII text preservation directly.
- Project-level P2P-broad for PySnooper retains 24 stable tests out of 29
  collected/common nodeids. Four tests fail on both buggy and reference
  checkouts under the retained Python 3.11 environment and must be excluded as
  buggy-baseline failures.
- The reference patch touches both `pysnooper/tracer.py` and
  `pysnooper/pycompat.py`. Candidate construction must support multi-file
  reference diffs; otherwise the reference patch can be incomplete.
- Label-leakage guards should match full tokens, not arbitrary substrings:
  `noop` is a substring of `PySnooper` and `pysnooper`, so substring matching
  falsely blocks legitimate candidates.
- `missing_change_1` is not a valid negative under the current Python 3.11
  oracle because it keeps the UTF-8 decode and UTF-8 log write behavior while
  omitting only Python 2 compatibility. Partial negative allowlists must be
  validated against the retained oracle before final dataset admission.
- `bugsinpy_PySnooper_1` now contributes six validated candidates over 24 stable
  P2P-broad tests and is admitted to `p2p_broad_main` as the sixth completed
  project-level main task.

## 2026-06-12 PySnooper_2 boundary decision

- `bugsinpy_PySnooper_2` checks out, but its original F2P path does not reach
  the target `custom_repr` assertion under the retained pipeline.
- The buggy checkout's copied `tests/test_pysnooper.py` imports
  `.mini_toolbox`, but `tests/mini_toolbox.py` is absent from the retained
  checkout.
- The reference checkout imports `pycompat.PY2` from `pysnooper/tracer.py`, but
  `pysnooper/pycompat.py` does not define `PY2` in the retained checkout.
- This is an unclear experimental-boundary problem, not a simple declared
  dependency or coverage-instrumentation blocker. A fixture shim could change
  test preconditions or output-capture behavior.
- User-confirmed rule: do not introduce task-specific
  compatibility/test-fixture shims for main-cohort admission at this stage.
- `bugsinpy_PySnooper_2` is therefore recorded as a blocked feasibility case
  with `p2p_broad_main_included = false`; next try `bugsinpy_PySnooper_3`, and
  if it needs the same class of shim, block it and move to `bugsinpy_fastapi_1`.

## 2026-06-12 PySnooper_3 candidate validation

- `bugsinpy_PySnooper_3` targets the older `pysnooper/pysnooper.py` file-output
  bug: the buggy code opens `output_path`, which is undefined, instead of the
  user-provided `output` path.
- Initial collection failed on missing `future`, then `python_toolbox`. Both are
  declared in the retained checkout through `requirements.txt` and
  `test_requirements.txt`, so installing them into a separate ignored venv is
  acceptable and should be audited.
- Do not reuse and mutate the `PySnooper_1` venv for this older checkout. Use a
  separate ignored environment, `outputs/envs/pysnooper3_p2p_py311`, so each
  task's dependency audit remains accurate.
- Unlike `PySnooper_2`, this task does not require a fixture shim or source-tree
  compatibility injection. Declared dependency installation is not the same as
  changing test fixtures.
- The reference patch is a single-line fix, so generic partial construction
  produces too few difficult negatives. A task-specific negative that changes
  the file mode but keeps the undefined `output_path` gives a relevant
  issue-not-fixed candidate.
- `bugsinpy_PySnooper_3` contributes four validated candidates over four stable
  P2P-broad tests and is admitted to `p2p_broad_main` as the seventh completed
  project-level main task.

## 2026-06-12 FastAPI_1 scope timeout boundary

- `bugsinpy_fastapi_1` has a clear F2P oracle:
  `tests/test_jsonable_encoder.py::test_encode_model_with_default` fails on the
  buggy checkout with an unexpected `exclude_defaults` keyword argument and
  passes on the fixed checkout.
- Its isolated environment uses only declared project/runtime test dependencies
  installed under ignored `outputs/envs/fastapi1_p2p_py311`.
- Full-repo project-level P2P-broad construction timed out twice and produced no
  `data/p2p_scopes/bugsinpy_fastapi_1_p2p_broad.json` manifest, even after an
  expanded execution window.
- This is a scope-policy boundary, not a candidate-label result. Do not mark the
  task as `p2p_broad_main` without an explicit decision on whether FastAPI's
  project-level P2P scope may be defined as the main `tests/` directory.
- User confirmed a general official-test-root policy: project-level P2P-broad
  may use a project's official test roots after repeated full-repo discovery
  timeouts, but not task-local test files.
- The scope builder needed a small execution-chain repair for directory roots:
  `static_source_segments` must read source files from collected nodeids when
  `--test-path` is a directory. Reading the directory path itself raises
  `PermissionError`.
- After that repair, the FastAPI `tests/` official-root attempt still exceeded
  the 60 minute construction budget and produced no P2P manifest. Record
  `bugsinpy_fastapi_1` as `pending_blocked_official_test_root_timeout`; do not
  keep retrying or downgrade to a task-file scope.

## 2026-06-12 FastAPI_2 and Sanic_1 feasibility

- `bugsinpy_fastapi_2` has a clear F2P oracle under the existing FastAPI venv:
  buggy receives `Socket Dependency`, fixed receives `Override`. It should not
  trigger another long FastAPI official-root P2P attempt because `fastapi_1`
  already exhausted that project-level scope path.
- `bugsinpy_sanic_1` requires a separate ignored dependency environment. Do not
  install the full requirements file: it contains broad unrelated dependencies
  and platform-hostile packages. Install only the declared runtime/test subset
  needed for the F2P and P2P probe.
- `multidict==4.7.6` can be installed with `MULTIDICT_NO_EXTENSIONS=1` to avoid
  the local MSVC build-tool blocker while preserving the package API needed by
  this probe.
- Old Sanic/aiofiles under Python 3.11 needs external runtime compatibility for
  `asyncio.coroutine` and legacy `loop=` keyword arguments on asyncio
  primitives. Keep this in the shared compat shim and record it as a runtime
  compatibility boundary, not a source or test-fixture edit.
- `bugsinpy_sanic_1` has a clear F2P oracle after that compatibility layer:
  buggy middleware order is `[1, 2, 3, 6, 5, 4]`, fixed passes with
  `[1, 2, 3, 4, 5, 6]`.
- Sanic project-level P2P-broad construction reached the 60 minute budget while
  running timeout-related tests and produced no manifest. Record it as
  `pending_blocked_project_level_scope_timeout`; do not downgrade to task-file
  P2P for main evidence.

## 2026-06-12 Scrapy_1 dependency blocker

- `bugsinpy_scrapy_1` checkouts succeed, but the target unittest F2P commands
  require Twisted before any oracle behavior can be observed.
- Installing the declared Scrapy dependency `Twisted==20.3.0` in the isolated
  probe venv fails on Windows/Python 3.11 because the package builds a native
  extension and local Microsoft Visual C++ 14.0+ build tools are unavailable.
- Do not silently replace Twisted with a newer wheel-bearing version, stub the
  dependency, or edit Scrapy fixtures for main-cohort admission. Record the task
  as `blocked_dependency_native_build` and skip Scrapy-family candidates unless
  the dependency/toolchain boundary is explicitly revisited.

## 2026-06-12 youtube-dl_1 project-level discovery timeout

- `bugsinpy_youtube-dl_1` has a clean retained F2P oracle: the buggy checkout
  treats `is_live=False` as a match, while the fixed checkout passes.
- Full project-level unittest scope construction can still be infeasible even
  for a low-dependency utility bug. The `test/` discovery/P2P run reached 30
  minutes and produced only the compat shim directory, with no manifest.
- Do not convert this clear F2P result into main evidence by downgrading to
  `test_utils.py` task-file P2P. Record the project-level discovery timeout and
  move to the next candidate.

## 2026-06-12 Tornado local-server tests on Windows

- Tornado websocket/http tests that use local sockets fail under Python 3.11 on
  Windows with the default Proactor event loop because `add_reader` is not
  implemented.
- Setting `asyncio.WindowsSelectorEventLoopPolicy()` before importing/running
  Tornado tests restores the local test-server execution path and exposes the
  actual `bugsinpy_tornado_1` oracle: buggy `set_nodelay` asserts on
  `self.stream`, fixed passes.
- Keep this as a shared runtime compatibility shim for Windows local-server
  tests. It is not a Tornado source edit, test fixture edit, or external network
  dependency.
- `bugsinpy_tornado_1` still did not complete project-level unittest
  P2P-broad construction after the selector policy fix. The run reached 40
  minutes with only the compat shim written, and cleanup observed an SSL
  iostream test active. Record the task as a project-level scope timeout rather
  than downgrading websocket_test.py to main evidence.

## 2026-06-12 BugsInPy checkout parallelism boundary

- Do not run buggy and fixed checkout for the same BugsInPy task in parallel.
  The `bugsinpy-checkout` script uses the shared
  `projects/<project>/bugs/<id>/` directory as temporary storage for copied
  test and changed files, then removes those temporary directories.
- Parallel same-task checkout can race and leave one checkout with incomplete
  injected tests, as observed for `bugsinpy_tornado_9` fixed checkout missing
  `test_url_concat_none_params`.
- Safe parallelism is across different task ids, or after checkout has already
  completed. Same-task buggy/fixed checkout should stay serial.
- `bugsinpy_tornado_9` confirms that a pure-function F2P target does not by
  itself make Tornado project-level P2P feasible. The F2P oracle is clear after
  serial checkout repair, but project-level `tornado/test` scope construction
  still failed to produce a manifest. Treat this as shared Tornado
  project-level scope risk and avoid repeated long Tornado sweeps.

## 2026-06-12 Ansible checkout cost

- `bugsinpy_ansible_2` looked attractive at metadata level because its target is
  pure version-comparison logic, but the large Ansible checkout did not complete
  inside the bounded feasibility window.
- If a BugsInPy checkout does not write the metadata marker files such as
  `bugsinpy_run_test.sh`, do not run F2P against that partial checkout. Stop the
  checkout process, remove the incomplete retained workspace, and record a
  checkout feasibility blocker.

## 2026-06-12 Matplotlib native extension boundary

- Matplotlib checkout is expensive, and target tests can require compiled
  extensions such as `ft2font` even for apparently narrow rendering/tight-bbox
  behavior.
- Running from `PYTHONPATH=checkout/lib` is not enough for these tasks. Do not
  treat an unrelated installed Matplotlib package as checkout evidence, and do
  not silently run editable/native builds for main-cohort admission.
- `bugsinpy_matplotlib_1` should be recorded as a native/import blocker unless
  the build boundary is explicitly revisited.

## 2026-06-12 final-roadmap advice extraction

- The external advice was broadly aligned with the existing final roadmap, so
  the safe update was to add only deltas: Evidence Visibility Curve framing,
  FACR/Evidence Gain as secondary calibrated metrics, staged E0/E2/E4/E6-first
  ablation, realistic tool-only boundaries, and stale paper/cohort wording
  cleanup.
- Do not duplicate the already established E0-E7 ladder, visible/hidden
  separation, tool-only baseline list, Candidate Patches title, or scale
  tiers. Repetition makes later agents think these are competing plans.
- Treat “30-50 bugs / 100-180 patches” as the robust-thesis target, not an
  unconditional next-step gate. The latest BugsInPy sweep found real candidate
  pool and build-boundary blockers, so changing the scaling route requires a
  user decision.
- Any current result based on retained validation summaries or oracle-style
  summaries must stay labeled diagnostic, upper-bound-style, or non-realistic
  for hidden-evaluator-free merge-gate claims.

## 2026-06-12 EVP-7 protocol freeze

- User decision: choose Option A now. Freeze the current 7 completed
  project-level P2P tasks as `EVP-7 Protocol Pilot`; do not keep chasing an
  eighth BugsInPy task under the same low-friction screening boundary.
- The first protocol artifact should be task-level only:
  `data/tasks/evp7_tasks.jsonl` and
  `data/exclusions/blocked_bugsinpy_projects.jsonl`. Candidate-level EVP-7
  records must be generated in a separate step because current candidate JSONL
  files are referenced under ignored `outputs/` paths.
- When building protocol manifests, read only tracked registry and P2P scope
  files. Do not copy local retained checkout paths or infer commits from
  untracked workdirs; record missing commit/issue/touched-file fields as
  `metadata_backfill_required`.
- Blocked tasks are evidence of the sampling boundary, not noise. Preserve them
  in the blocker registry to avoid hidden cherry-picking.

## 2026-06-12 EVP-7 candidate manifest count boundary

- The task-level registry reported 36 known candidates because
  `bugsinpy_httpie_5` lacked `collection_summary.candidate_count` and label
  counts. Treat this number as a registry-known lower bound, not the final
  EVP-7 candidate count.
- The validated candidate JSONL plus P2P validation files promote to 42 tracked
  candidates: 7 correct reference patches and 35 issue-not-fixed negatives.
- Candidate manifests may carry evaluator-only fields for metrics, but evidence
  packet builders must strip labels, retained-oracle status, provenance, and
  failure taxonomy from model-visible prompts.
- When summary counts disagree, first diagnose source-of-truth granularity
  before changing inclusion policy. Here the task registry was incomplete for
  one admitted task; the candidate output files were the correct source for
  candidate-level cardinality.

## 2026-06-12 EVP-7 evidence packet leakage boundary

- Evidence packet records can be generated before every evidence level is
  complete, but they must explicitly mark missing visible evidence. Do not fill
  E4/E6 by copying retained-oracle or hidden P2P validation outcomes from the
  evaluator-side candidate manifest.
- E0/E2 are currently complete for all 42 EVP-7 candidates. E2 only exposes
  patch-apply evidence from validation; syntax/import/static analysis remains
  `not_run` until a visible static runner is added.
- E4/E6 records are useful for schema and leakage auditing, but G1 is still not
  passed because independent visible test outcomes and realistic visible tool
  summaries do not exist yet.
- The leakage audit should scan both keys and values for evaluator-only terms.
  It is a gate for accidental label/provenance leakage, not proof that G1/G5
  signal exists.

## 2026-06-12 EVP-7 visible-test runner boundary

- Visible E4 outcomes must be regenerated as a separate model-visible evidence
  source. Do not reuse retained-oracle or hidden P2P validation outcomes from
  evaluator validation JSONL.
- Empty-string `pytest_addopts_override` is meaningful: it clears project
  default addopts. Treating it as false caused cookiecutter_3 visible tests to
  fail with pytest exit code 4 until the runner switched to
  `addopts_override is not None`.
- PySnooper_1 and httpie_5 visible-test attempts currently hit environment or
  dependency import errors under Python 3.11. These are runner/environment
  boundaries, not candidate-patch failures. Do not classify pytest exit codes
  other than 0 and 1 as visible test failed; record them as `error`.
- Reusing tracked P2P manifest compat shims in the visible runner is an
  environment-consistency repair, not a new task-specific shim. The runner must
  not create or modify shims; it may only use `compat_shim.enabled=true` paths
  already recorded in tracked P2P manifests.
- After adding tracked compat-shim reuse, current visible outcome source
  completes 42/42 candidates. Three outcomes remain `error`, but they are
  candidate-induced import failures after the runner environment is aligned,
  so they count as complete visible runtime evidence. Deterministic E6 visible
  tool summaries also complete 42/42 by summarizing already model-visible
  patch-apply/static/test evidence.

## 2026-06-13 EVP-7 tool-only baseline boundary

- Tool-only decision records must be generated from model-visible evidence
  packets only. Evaluator labels may be joined only after decisions exist, and
  only for aggregate metrics.
- Apply-only is a safe but unusable baseline for EVP-7: it escalates all 42
  candidates, yielding false accept rate 0.0 and correct recall 0.0.
- Visible-tests and visible-tool-summary baselines currently have false accept
  rate 0.0, accepted precision 1.0, and correct recall 0.857143. They reject
  one correct patch, so they are strong safety baselines but not an oracle.

## 2026-06-13 EVP-7 merge-gate schema dry-run boundary

- G4 schema stability should be checked before any real verifier API call. The
  dry-run runner renders deterministic accept/reject/escalate JSON objects from
  model-visible EVP-7 packets and then parses them through the fixed schema.
- The dry-run records are not model outputs. They can prove parser/schema
  stability, evidence-level coverage, and leakage-boundary hygiene, but they
  cannot support claims about LLM merge-gate behavior.
- Keep `raw_response_text` and `parsed_output` in the dry-run records aligned:
  future API runners should be able to replace the deterministic raw response
  with a provider response while preserving the same parsed schema fields.
- Leakage scans for schema dry-run outputs should include evaluator markers
  such as final labels, construction taxonomy, hidden oracle terms, and
  candidate provenance. A parse-valid record is still invalid if it carries one
  of those markers.

## 2026-06-13 EVP-7 G5 metric scaffold boundary

- G5 needs two separate claims: metric-path readiness and real signal
  existence. Deterministic dry-run records can establish the former, but not
  the latter.
- FACR and Evidence Gain should be computed from the same aggregate confusion
  counts as FAR, accepted precision, recall, rejection, and escalation. This
  keeps the added paper-friendly metrics auditable rather than ornamental.
- Utility weights are currently a scaffold:
  `accept_correct - 5*accept_wrong - 0.25*escalate - reject_correct`.
  Before paper claims, run sensitivity analysis or document why these weights
  match the merge-gate risk model.
- The dry-run metric scaffold intentionally sets
  `g5_signal_claim_status = requires_real_llm_verifier_outputs`. Do not change
  that to passed unless genuine LLM verifier outputs have been produced under
  an approved API/model/cost boundary and analyzed through the same path.

## 2026-06-13 EVP-7 G5 prompt manifest boundary

- The G5 prompt manifest should store hashes and lengths, not full prompt text,
  so tracked artifacts can prove prompt coverage and leakage checks without
  duplicating all prompt payloads.
- `patch_verify_evidence_visibility_merge_gate_v1` is a new EVP-7 protocol
  prompt. It is not a scale-up of the stopped
  `patch_verify_evidence_first_v1` condition and does not reuse the
  retained-oracle/tool-summary boundary of
  `patch_verify_tool_augmented_evidence_v1`.
- Generic schema enum values such as `partial_fix` can appear in the prompt as
  possible verifier output categories. They are not leakage unless attached to
  a specific candidate as evaluator-side truth.
- A future real G5 run should stop on prompt-boundary failure, high smoke
  invalid-output rate, API/preflight failure, cost growth beyond the
  user-confirmed budget, or `run_error.json`.

## 2026-06-13 EVP-7 G5 preflight boundary

- Keep `configs/evp7_g5_llm.example.json` as a template only. Placeholder
  provider/model/cost/smoke/full-run fields must keep `api_ready = false`.
- `scripts/preflight_evp7_g5_llm_run.py` intentionally separates
  `structural_ready` from `api_ready`. Structural readiness can pass with the
  example config; strict API readiness must fail until the user supplies an
  ignored local config with concrete confirmations.
- The G5 preflight does not read `.env`, does not create local configs, and
  does not call any API. Credential checks belong to the final guarded runner
  after user confirmation.
- If a future agent changes the example config to concrete values, treat that
  as a scope violation unless the user explicitly asked to record those values
  in tracked files. Real provider/model/cost decisions should be local or
  documented as non-secret policy, not mixed with credentials.

## 2026-06-13 EVP-7 G5 guarded workflow boundary

- A guarded workflow should offer check-only and mock modes before real API
  execution. The check-only mode must report `model_call_attempted = false` and
  `api_call_attempted = false`.
- Mock G5 workflow records are useful only for validating parser, schema, and
  metrics plumbing. Keep `g5_signal_claim_status =
  requires_real_llm_verifier_outputs`; do not relabel mock variation as
  evidence-visibility signal.
- The initial workflow implementation exposed a relative-path bug: passing a
  relative `reviews_out` into `analyze_evp7_schema_dry_run_metrics.py` caused
  `Path.relative_to(REPO_ROOT)` to fail. Fix both caller and analyzer by
  resolving paths against `REPO_ROOT` before reading or reporting paths.
- The real execute path must reject the tracked example config and stop before
  API calls unless strict preflight passes on an ignored local config and the
  user has explicitly confirmed provider, model, cost ceiling, smoke scope, and
  full-run permission.

## 2026-06-13 EVP-7 G5 local config helper boundary

- The helper for `configs/evp7_g5_llm.local.json` must default to dry-run and
  must not choose provider, model, budget, smoke scope, or full-run permission.
- Dry-run artifacts are allowed in tracked docs/data because they contain only
  placeholders and the required confirmation checklist. They must record
  `local_config_write_attempted = false` and `api_call_attempted = false`.
- Non-dry-run config creation must fail if any confirmation is missing. A
  failed write must leave `configs/evp7_g5_llm.local.json` absent.
- The safe order after user confirmation is: create ignored local config, run
  strict preflight, run check-only workflow, execute smoke, inspect smoke
  invalid-output/cost, then decide whether full run is allowed.

## 2026-06-13 GitHub sync retry after transient network failure

- A failed `git push` with `Failed to connect to github.com port 443` or
  `Recv failure: Connection was reset` should be treated as a transport issue,
  not as a repository-state issue, after `git status --short --branch` shows a
  clean tree ahead of origin.
- Re-run a connection check or retry `git push origin main` before changing
  repository state. In this case the retry succeeded and synchronized
  `37e1b7f` to `origin/main`.
- Do not create extra commits only to compensate for a failed push; first
  verify whether the local commit is already clean and simply awaiting network
  recovery.

## 2026-06-13 EVP-7 G5 DeepSeek max-token smoke repair

- DeepSeek V4 can return an empty final `content` when the completion budget is
  too low, even when the prompt is valid. In EVP-7 G5, `max_tokens = 1024`
  produced valid E0/E2 outputs but empty E4/E6 outputs in the first 4-packet
  smoke.
- Treat this as an execution-chain output-format failure, not as model signal.
  Do not continue to full run until a repaired smoke has invalid-output rate 0.
- Raising G5 `max_tokens` to 4096 matched the earlier DeepSeek smoke lesson and
  repaired the same 4-packet smoke to 4/4 parse-valid outputs.

## 2026-06-13 EVP-7 G5 parallel full-run efficiency boundary

- If a long sequential G5 run is interrupted but the Python process continues in
  the background, inspect `Win32_Process.CommandLine` before starting another
  run. Stop only the obsolete non-concurrent process to avoid duplicate API
  spend.
- Use bounded concurrency for real G5 full runs after smoke passes. The first
  successful full run used `--concurrency 4`, completed 168 records, preserved
  original packet order, and wrote outputs once after all workers completed.
- Do not silently repair schema-invalid LLM outputs after a full run. The
  single invalid E0 record is a real output-quality boundary and should be
  reported in summaries instead of overwritten by a targeted retry.

## 2026-06-13 EVP-7 G5 bounded concurrency boundary

- Keep G5 execution sequential by default. `--concurrency` should be an explicit
  full-run speed knob, not an implicit behavior change.
- Validate all prompt boundaries before submitting parallel model calls. This
  keeps leakage or prompt-shape failures from becoming partially executed API
  runs.
- Parallel workers should return in any order, but the runner must write review
  JSONL in the original packet order. Do not let multiple workers append to the
  same JSONL file.
- Start bounded full runs at concurrency 4 or 6. If rate limits, timeouts, or
  invalid outputs rise, stop and diagnose instead of raising concurrency.

## 2026-06-13 EVP-7 controlled expansion probe status boundary

- Expansion readiness should distinguish metadata candidates from attempted
  probes. Keep attempted probe outcomes in
  `data/tasks/evp7_controlled_probe_results.json` and let the readiness
  summarizer overlay those statuses, rather than editing generated Markdown by
  hand.
- `bugsinpy_fastapi_4` checkouts completed, but both buggy and fixed versions
  failed during pytest collection under the current Pydantic v2 environment.
  Treat this as a dependency-environment blocker, not as F2P evidence.
- `bugsinpy_sanic_2` checkouts completed quickly, but both versions failed
  before the target test because `aiofiles` is absent. Treat missing declared
  runtime dependencies the same way: record the blocker and do not install
  silently inside a F2P-only probe.
- Do not silently install or substitute dependencies after a collection-level
  environment blocker. Move to another independent lane unless a later plan
  explicitly authorizes dependency isolation.
- In parallel F2P-only triage, keep each task's buggy/fixed checkout serial,
  but run independent project lanes concurrently. This saved time while still
  keeping each F2P result interpretable.
- `bugsinpy_youtube-dl_2` established clean F2P under the no-install boundary.
  It is not admission evidence until project-level P2P-broad and candidate
  revalidation are explicitly run.
- In F2P-only screening, distinguish path setup from dependency installation:
  `ansible_1` needed `PYTHONPATH=lib` to reach the package, but then hit the
  Windows `fcntl` blocker. That final blocker should be recorded rather than
  hidden behind the first path error.
- Existing runtime compatibility shims can be reused when already documented
  for the project family, as with Luigi `inspect.ArgSpec/getargspec`; once the
  next missing dependency appears, stop rather than silently installing it.
- When one project family establishes clean F2P under the no-install boundary,
  additional same-family F2P-only probes can be efficient as long as they do
  not bypass the project-level P2P-broad admission gate. The youtube-dl 3-5
  continuation added three F2P candidates without changing main-cohort status.
