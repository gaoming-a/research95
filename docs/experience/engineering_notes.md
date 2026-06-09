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
