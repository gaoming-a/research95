# Research95 Index

## Project Execution Rules

- `../AGENTS.md`: project-level requirements for the plan-execute-audit-revise
  loop, including verification, diagnosis, documentation sync, and GitHub sync
  rules for future agent runs.

## Active Plan

- `plans/current_project_state_zh.md`: short current-state entry and file map.
  Start here before reading the long execution log. It records Git sync state,
  current paper/result boundaries, experiment-decision gates, active plan roles,
  key project files, script entry points, and forbidden misuses.
- `plans/final_paper_roadmap_zh.md`: canonical final-paper route and subsequent
  research target. It upgrades the current pilot into an evidence-visibility
  empirical study with expanded data, tool-only baselines, hidden-evaluator
  separation, multi-level evidence ablation, artifact goals, and the rule that
  generator-unsolved but validation-stable tasks such as `httpie_5` should be
  treated as hard-generation/stress cases rather than deleted. The 2026-06-12
  update extracts only non-duplicative external advice: the Evidence Visibility
  Curve framing, FACR/Evidence Gain as calibrated secondary metrics, the
  current E0/E2/E4/E6 four-anchor pilot boundary, realistic tool-only
  boundaries, and the need to keep roadmap Phase A counts aligned with the
  tracked structural cohort while keeping the historical real G5 run boundary
  explicit. As of 2026-06-17, E1/E3/E5 are not follow-up insertions for the
  current EVP-7 artifacts; a full adjacent-difference E0-E6 ladder requires a
  new EVP-8 or EVP-7-v2 protocol and rerun. As of 2026-06-18, non-conflicting
  reinforcement means either workload presentation over the existing pipeline
  or a user-confirmed second-model replication on E0/E4/E6 only. As of
  2026-06-20, the user-selected journal-upgrade route is a new EVP-8
  full-ladder protocol: freeze no-API packets/prompts/schema first, run
  DeepSeek V4 Pro and Qwen3.7 Max as the first batch, then add Kimi K2.6,
  Devstral 2, and Gemini 2.5 Flash on the same frozen inputs.
- `experiments/evp8_journal_scale_execution_plan_20260620.md`: no-API
  execution plan for the journal-scale EVP-8 route. It defines the planned
  E0-E6 full-ladder boundary, target five-model set, phased DeepSeek/Qwen first
  batch, later OpenRouter-compatible model completion, cost-planning boundary,
  required outputs, stop gates, and forbidden shortcuts.
- `../data/protocols/evp8_protocol_v0_1.json`: tracked EVP-8 protocol spec for
  the v0.1 full-ladder. It records the model-visible `E0-E6` field groups,
  evaluator-only `E7`, output schema, model plan, routing policy, cost
  observability, and stop gates.
- `../data/protocols/evp8_protocol_v0_1_audit_summary.json`: no-API audit
  summary for the EVP-8 v0.1 protocol spec. It should show
  `protocol_spec_audit_status=passed` and
  `phase0_api_readiness=ready_for_api_preflight` after the Phase 0 dry-run
  summaries are generated. This status still does not authorize API execution.
- `../data/protocols/evp8_candidate_set_v0_1.json`: model-visible-safe
  candidate-set manifest for EVP-8 Phase 0 smoke/protocol validation. It maps
  the tracked 21-task / 98-candidate structural cohort to anonymous EVP-8
  smoke candidate IDs without copying per-candidate evaluator labels.
- `../data/protocols/evp8_candidate_set_v0_1_summary.json`: aggregate
  candidate-set audit summary. It records 21 tasks, 6 projects, 98 candidates,
  aggregate evaluator-side label counts for balance audit, and
  `api_call_attempted=false`.
- `../prompts/evp8_visible_evidence_merge_gate_v0_1.md`: frozen EVP-8
  visible-evidence merge-gate prompt template. It stores the template text, not
  rendered per-packet prompts.
- `../data/protocols/evp8_prompt_manifest_v0_1.json`: no-API prompt-template
  manifest. It records prompt id, template hash/length, output-schema keys,
  and `api_call_attempted=false`.
- `../data/protocols/evp8_prompt_boundary_audit_v0_1.json`: no-API prompt
  boundary audit over the template and a minimal visible sample render. It
  stores hashes and counts, not rendered prompt text.
- `../data/protocols/evp8_evidence_packet_dry_run_summary_v0_1.json`:
  no-API summary over 686 planned EVP-8 packet skeletons. It validates
  cumulative field groups and leakage boundaries without writing full evidence
  packets.
- `../data/protocols/evp8_schema_dry_run_summary_v0_1.json`: no-API schema
  dry-run summary over 686 deterministic escalate outputs. It validates the
  EVP-8 output schema and stores no review records.
- `../data/protocols/evp8_cost_observability_dry_run_v0_1.json`: no-API
  summary over the planned EVP-8 model-call matrix. It validates 686 planned
  calls per model and required usage/cost fields without reading local config
  or calling APIs.
- `../data/protocols/evp8_deterministic_tool_baseline_dry_run_v0_1.json`:
  no-API deterministic baseline schema dry-run over 686 planned records. It
  uses only model-visible evidence slots and stores no baseline decision JSONL.
- `../configs/evp8_deepseek_qwen.example.json`: tracked no-secret example
  config for the EVP-8 Phase 1 DeepSeek/Qwen local preflight. The ignored local
  copy is `configs/evp8_deepseek_qwen.local.json` and must not be committed.
- `../data/protocols/evp8_deepseek_qwen_local_config_plan_v0_1.json`:
  no-secret summary of the ignored local config creation boundary. It records
  paths, model ids, planned call counts, and API-key env var names only.
- `../data/protocols/evp8_deepseek_qwen_preflight_summary_v0_1.json`: tracked
  no-secret EVP-8 DeepSeek/Qwen local preflight summary. It records structural
  checks and credential presence states without key values, raw outputs, or API
  calls.
- `../data/protocols/evp8_deepseek_qwen_smoke_check_only_v0_1.json`: tracked
  no-API smoke runner check-only summary. It records the deterministic
  project-frequency-stratified 5-candidate x 7-level smoke packet gate, prompt
  hashes, schema checks, and no-raw-output/no-API status.
- `../data/protocols/evp8_deepseek_qwen_smoke_execution_packet_v0_1.json`:
  no-API DeepSeek/Qwen smoke execution handoff packet. It records guard
  commands, future execute commands, expected output paths, stop gates, and the
  boundary that this packet does not authorize API calls.
- `experiments/evp8_deepseek_qwen_smoke_execution_packet_v0_1.md`: Markdown
  companion for the no-API smoke execution packet.
- `../data/protocols/evp8_deepseek_qwen_smoke_result_audit_v0_1.json`:
  no-API post-smoke audit scaffold. Before real execution it reports
  `waiting_for_execution`; after execution it validates tracked summaries
  without reading raw responses.
- `experiments/evp8_deepseek_qwen_smoke_result_audit_v0_1.md`: Markdown
  companion for the post-smoke audit scaffold.
- `plans/current_plan_zh.md`: active per-turn execution log. Future agents must
  update this file before concrete experiments, API calls, data changes, paper
  edits, or Git sync work.
- `plans/current_plan.md`: English companion plan. It is useful for bilingual
  handoff context, but `plans/current_plan_zh.md` is the stricter execution log.
- `../data/cohorts/task_cohort_registry.json`: tracked cohort registry for the
  final project-level P2P main metrics. Only tasks with completed
  `project_level_p2p_broad` and `p2p_broad_main_included = true` enter the
  default `p2p_broad_main` metrics.
- `protocol/evidence_visibility_protocol.md`: Phase A protocol after the
  2026-06-12 Option A decision, controlled youtube-dl formal admissions through
  `youtube-dl_37`, and the bounded `thefuck_1` rules-root pip-family
  admission. The current tracked structural cohort is 21 tasks across 6
  projects, 98 candidates, and 392 E0/E2/E4/E6 evidence packets. It keeps E7 as
  oracle-only, records that E1/E3/E5 are outside the current EVP-7
  paper-facing protocol, records G1-G5 no-API gate status, and preserves the
  376-record real DeepSeek G5 result as a historical
  20-task/94-candidate bounded pilot.
- `../data/tasks/evp7_tasks.jsonl`: tracked task manifest for the frozen
  EVP-7 protocol pilot, generated from the cohort registry and P2P manifests.
- `../data/tasks/evp7_manifest_summary.json`: task-level summary of the current
  protocol pilot: 21 main tasks, 6 projects, and 98 registry-known candidates.
  The earlier `httpie_5` missing-count drift has been repaired in the tracked
  cohort registry.
- `../data/tasks/evp7_expansion_readiness.json`: post-G5 controlled-expansion
  readiness summary. It combines the current EVP-7 registry with the broader
  BugsInPy candidate-pool rescreen, reports the 21-task / 98-candidate current
  cohort, and lists project-diverse probe lanes that are metadata-only,
  admitted, or blocked.
- `../data/tasks/evp7_controlled_probe_results.json`: tracked status records
  for controlled expansion probes, including admitted and blocked outcomes.
- `../data/patches/evp7_candidates.jsonl`: tracked candidate manifest promoted
  from validated EVP-7 candidate outputs. It contains 98 candidates with global
  anonymous `evp7_candidate_id` values and evaluator-only labels kept explicit.
- `../data/patches/evp7_candidate_summary.json`: summary of the promoted EVP-7
  candidate records: 98 candidates, 21 correct reference patches, 76
  issue-not-fixed candidates, and 1 regression candidate.
- `../data/evidence/evp7_evidence_packets.jsonl`: tracked EVP-7 model-visible
  evidence packet records. It contains 392 E0/E2/E4/E6 records; all four
  levels are complete for all 98 candidates.
- `../data/evidence/evp7_evidence_packet_summary.json`: summary and leakage
  audit result for the EVP-7 evidence packets. G1 and G2 currently pass.
- `../data/evidence/evp7_visible_test_outcomes.jsonl`: independent model-visible
  visible-test outcome source generated by rerunning predeclared `visible_tests`
  in candidate workdirs.
- `../data/evidence/evp7_visible_test_outcome_summary.json`: summary of visible
  test outcome execution: 95 completed runner records and 3 visible error
  records, all counted as complete model-visible outcomes.
- `../data/evidence/evp7_visible_tool_summaries.jsonl`: deterministic visible
  tool summaries built only from model-visible static and visible-test evidence.
- `../data/evidence/evp7_visible_tool_summary_summary.json`: summary of visible
  tool summaries: 98 complete records.
- `../data/baselines/evp7_tool_only_decisions.jsonl`: deterministic tool-only
  accept/reject/escalate decisions for apply-only, visible-tests, and
  visible-tool-summary conditions. Decision records are generated from
  model-visible packets only.
- `../data/baselines/evp7_tool_only_metrics.json`: aggregate EVP-7 tool-only
  baseline metrics. G3 currently passes.
- `../data/reviews/evp7_merge_gate_schema_dry_run.jsonl`: deterministic
  no-API merge-gate schema dry-run records for all 392 EVP-7 E0/E2/E4/E6
  evidence packets. These records validate parser/schema stability only; they
  are not LLM verifier results.
- `../data/reviews/evp7_merge_gate_schema_dry_run_summary.json`: summary for
  the merge-gate schema dry-run. G4 currently passes with 392 valid parses and
  zero leakage findings.
- `../data/reviews/evp7_schema_dry_run_metrics.json`: no-API G5 metric
  scaffold over schema dry-run records. It computes FAR, accepted precision,
  recall, escalation, FACR, and Evidence Gain, but marks G5 signal claims as
  requiring genuine LLM verifier outputs.
- `../data/reviews/evp7_g5_llm_full_run_summary.json`: tracked raw-output-free
  summary of the earlier 12-task/62-candidate/248-packet DeepSeek official G5
  full run. Retained for historical comparison.
- `../data/reviews/evp7_g5_full_run_quality_audit.json`: tracked quality audit
  for the earlier 248-record DeepSeek full run. Retained for historical
  comparison.
- `../data/reviews/evp7_g5_llm_376_full_summary.json`: tracked raw-output-free
  summary of the latest real DeepSeek official G5 full run on the frozen
  20-task/94-candidate/376-packet cohort. It records 376/376 parse-valid
  outputs, token-usage cost estimates for 376/376 records, estimated total cost
  USD 0.327352058, and
  `real_llm_verifier_signal_observed_on_evp7`.
- `../data/reviews/evp7_g5_376_full_quality_audit.json`: tracked quality audit
  for the 376-record DeepSeek full run. It reads only the raw-output-free
  summary and marks the run `passed_with_limitations`.
- `../data/reviews/evp7_g5_376_statistical_analysis.json`: tracked
  raw-output-free statistical analysis for the frozen 20-task/94-candidate
  EVP-7 G5 run. It records Wilson intervals, candidate-level bootstrap
  intervals, paired deltas against E0, per-project breakdowns, and
  per-patch-source breakdowns without raw model responses.
- `../data/reviews/evp7_g5_376_utility_sensitivity.json`: tracked
  raw-output-free utility sensitivity analysis over false-accept, escalation,
  and false-reject penalty grids for the frozen EVP-7 G5 run.
- `../data/reviews/evp7_g5_376_tool_attribution.json`: tracked
  raw-output-free attribution analysis comparing deterministic tool-only
  decisions with matched E4/E6 LLM decisions. It shows the safety/recall
  boundary without claiming LLM superiority over tool evidence.
- `../data/reviews/evp7_g5_376_qualitative_cases.json`: tracked
  raw-output-free qualitative case analysis for six representative EVP-7
  decision sequences. It separates model-visible decisions from evaluator-only
  interpretations.
- `../data/reviews/evp7_g5_376_claim_traceability.json`: tracked
  raw-output-free claim-boundary traceability audit for the same EVP-7 G5 run.
  It maps supported and unsupported claims to summary, quality, statistics, and
  paper-draft coverage.
- `../data/reviews/evp7_g5_llm_prompt_manifest.jsonl`: no-API prompt manifest
  for the next G5 evidence-visibility LLM run. It stores prompt hashes,
  lengths, prompt id, evidence level, and leakage-check status, not full prompt
  text.
- `../data/reviews/evp7_g5_llm_run_readiness.json`: G5 LLM run readiness
  summary. It records 392 prompt records, zero leakage failures, estimated
  prompt scale, stop conditions, and required user confirmations for the current
  structural cohort.
- `../data/reviews/evp7_g5_llm_preflight_example.json`: no-API preflight
  result for the tracked G5 example config. Structural readiness passes while
  strict API readiness remains false because user confirmations are pending.
- `../data/reviews/evp7_g5_llm_preflight_strict_example.json`: strict-mode
  preflight result proving the example config is blocked from real API
  execution until provider, model, cost, smoke scope, and full-run permission
  are confirmed.
- `../data/reviews/evp7_g5_workflow_check_only_example.json`: guarded G5
  workflow check-only summary. It proves the workflow reaches structural
  readiness without attempting model/API calls.
- `../data/reviews/evp7_g5_workflow_mock_reviews.jsonl`: mock G5 workflow
  review records for the pre-admission 168 packets. These are pipeline-validation records,
  not model results.
- `../data/reviews/evp7_g5_workflow_mock_metrics.json`: metrics over the mock
  workflow records. It keeps `g5_signal_claim_status` as requiring real LLM
  verifier outputs.
- `../data/reviews/evp7_g5_workflow_mock_summary.json`: summary of the mock
  G5 workflow run.
- `../data/reviews/evp7_g5_local_config_dry_run.json`: dry-run packet for the
  future ignored G5 local config. It records that local config writing and API
  calls were not attempted, and lists the still-missing user confirmations.
- `experiments/evp7_20_task_freeze_and_g5_smoke_readiness.md`: historical
  freeze and smoke-readiness record for the 20-task / 94-candidate /
  376-packet structural cohort before `thefuck_1` admission. Current G5
  no-API readiness is tracked in `../data/reviews/evp7_g5_llm_run_readiness.json`
  for the 21-task / 98-candidate / 392-packet cohort.
- `../data/reviews/evp7_g5_llm_376_smoke_summary.json`: raw-output-free summary
  of the confirmed 4-packet real G5 smoke on the frozen 376-packet cohort. It
  records 4 valid non-mock API outputs and the cost-observability blocker.
- `experiments/evp7_g5_llm_376_smoke_result.md`: human-readable report for the
  confirmed 4-packet G5 smoke. It is parser/API path evidence only, not a full
  G5 result.
- `experiments/evp7_g5_cost_observability_fix.md`: no-API repair record for
  G5 cost observability. It documents token-usage-based DeepSeek cost
  estimation, unknown-cost failure behavior, and the historical smoke boundary.
- `../data/reviews/evp7_g5_llm_376_smoke_002_summary.json`: raw-output-free
  summary of the post-repair 4-packet real G5 smoke. It records provider token
  usage summaries, estimated token-price costs, and `unknown_cost_record_count=0`.
- `experiments/evp7_g5_llm_376_smoke_002_result.md`: human-readable
  post-repair smoke report. It validates the API/parser/cost-observability path
  only, not a full 376-packet G5 result.
- `experiments/evp7_g5_llm_376_full_result.md`: human-readable tracked summary
  of the latest real 376-packet DeepSeek G5 full run. Raw model responses stay
  ignored under `outputs/`.
- `experiments/evp7_g5_376_full_quality_audit.md`: human-readable quality audit
  for the 376-packet DeepSeek G5 full run. It supports bounded EVP-7 pilot
  signal claims and lists unsupported scale/baseline/cost-billing claims.
- `experiments/evp7_g5_376_statistical_analysis.md`: human-readable statistical
  analysis for the same 376-record run, including Wilson CIs, candidate-level
  bootstrap CIs, paired deltas versus E0, per-project breakdowns, and
  per-patch-source breakdowns.
- `experiments/evp7_g5_376_utility_sensitivity.md`: human-readable utility
  sensitivity analysis showing how evidence-level utility rankings behave under
  a bounded penalty grid.
- `experiments/evp7_g5_376_tool_attribution.md`: human-readable attribution
  analysis comparing matched deterministic tool-only and LLM decisions at E4
  and E6. It reports decision overlap, recovered tool-only false accepts, and
  correct tool accepts downgraded by the LLM.
- `experiments/evp7_g5_376_qualitative_cases.md`: human-readable qualitative
  case report for six representative EVP-7 decision paths, including
  evidence-enabled accepts, recovered tool-only false accepts, downgraded
  correct patches, and rejected non-fixing patches.
- `experiments/evp7_g5_376_claim_traceability.md`: human-readable
  claim-boundary traceability audit that verifies supported/unsupported EVP-7
  claims are covered by the paper tables, Markdown draft, and IEEE draft while
  preserving the bounded-pilot claim boundary.
- `../data/exclusions/blocked_bugsinpy_projects.jsonl`: tracked blocker
  registry for tasks excluded from the EVP-7 core cohort.

## Historical Plan References

- `plans/ai_agent_experiment_execution_plan_zh.md`: historical standalone task
  book for the earlier API-pilot route. Retain for traceability and command
  contracts, but do not let it override `plans/final_paper_roadmap_zh.md`.
- `plans/agent_execution_plan_zh.md`: older detailed step-by-step execution
  plan. Retain as reference only.

## New Paper Direction

- `paper/research_definition.md`: current evidence-visibility problem
  definition, hypotheses, non-goals, and bounded-claim boundary.
- `paper/patch_verification_outline.md`: current paper outline for
  `Evidence Visibility Matters: A Systematic Study of LLM-Based Verification
  for Candidate Patches`.
- `paper/patch_verification_draft.md`: staged result draft with no-API
  validation, the first DeepSeek official API full-run outcome, the
  tool-augmented full run, reader-flow bridge, workload-at-a-glance ledger,
  related-work positioning, and the bounded EVP-7 G5 376-record result.
- `paper/generated_tables.md`: generated Markdown paper tables from current
  tracked outputs, including the EVP-7 workload ledger, G5 376-record real-LLM
  result, Wilson/bootstrap intervals, utility sensitivity, deterministic
  tool-only attribution, and claim boundary.
- `paper/generated_tables.tex`: generated LaTeX table snippets used by the
  current IEEE draft, including the EVP-7 workload ledger, G5 376-record
  result, deterministic tool-only attribution, and claim-boundary snippets.
- `paper/ieee_submission_draft.tex`: current anonymous IEEEtran submission
  draft. It includes the prompt-only mixed/negative result, the separate
  tool-augmented full-run result, the bounded EVP-7 G5 376-record
  evidence-visibility result, the early decision-to-metric reader-flow bridge,
  workload-at-a-glance ledger, related-work positioning, deterministic
  tool-only attribution, qualitative case interpretation, figures, threats,
  conclusion, and final consistency polish for `Evidence Gain`,
  unsupported-claim formatting, and bounded
  conclusion wording.
- `paper/advisor_workload_response_zh.md`: no-API advisor-facing explanation
  packet for the current paper package. It summarizes the 21/98/392 structural
  pipeline, the 20/94/376 real G5 run, validation/audit/artifact work, allowed
  bounded claims, and disallowed overclaims.
- `artifact/submission_freeze_candidate_20260618.md`: no-API freeze-candidate
  packet for the current paper/artifact package. It records the current
  candidate state and the user confirmations still required before final
  freeze; it does not authorize API calls, expansion, or E1/E3/E5 insertion.
- `experiments/evp7_related_work_positioning.md`: related-work citation and
  positioning artifact. It maps field-specific primary references to the
  paper's evidence-visibility distinction and records why a strict Nature/CNS
  citation scope is not appropriate for this software-engineering claim.
- `references/evp7_related_work_references.ris`: reference-manager-ready RIS
  export for the related-work section.
- `paper/nature_reviewer_presubmission_report.md`: Nature-style
  pre-submission reviewer assessment of the current IEEE draft. It provides
  three reviewer reports plus a cross-review synthesis and keeps the assessment
  bounded to the tracked manuscript, tables, figures, and readiness evidence.
- `paper/ieee_preapi_draft.tex`: historical IEEEtran pre-API LaTeX draft.
- `experiments/patch_verification_plan.md`: experiment design for the first
  patch-verification pilot.
- `experiments/patch_verification_pilot_report.md`: tracked summary of the
  current no-API pilot, executable validation, metrics, and prompt dry-run.
- `experiments/evp7_protocol_pilot.md`: current EVP-7 protocol-pilot report.
  It now records the frozen 20-task / 94-candidate / 376-packet state, the
  current 376-record DeepSeek G5 result, and the older 248-record run only as a
  historical checkpoint.
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
- `experiments/bugsinpy_candidate_pool_screening.md`: broader BugsInPy
  metadata-level candidate-pool screening after the decision to stop
  prioritizing legacy `nose` and Black `typed_ast` repair. It identifies
  promising probe lanes before any checkout or P2P construction. The latest
  refresh treats self editable Git requirements as install-boundary notes
  rather than external network-service blockers, surfacing `thefuck` as the
  next fresh-project controlled probe lane.
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
- `experiments/p2p_feasibility_sweep_update.md`: bounded replacement-task
  feasibility sweep after freezing Luigi. It records that `httpie_1` to
  `httpie_4`, `tqdm_1` to `tqdm_8`, `black_1` to `black_3`, and earlier
  unvalidated Cookiecutter tasks were screened under the current project-level
  P2P budget and why blocked or insufficient tasks are retained in accounting.
  It also records the audited
  coverage-only pytest addopts override and isolated dependency environment
  used for the Cookiecutter P2P retries, plus the later notes admitting
  `cookiecutter_1`, `cookiecutter_2`, `cookiecutter_3`, and `tqdm_9` after
  oracle and candidate validation.
- `experiments/cookiecutter1_candidate_validation.md`: tracked validation
  report for `bugsinpy_cookiecutter_1`. It records the migrated UTF-8 context
  oracle, four candidate patches, F2P validation, P2P-broad validation over 290
  stable tests, and the cohort admission boundary.
- `experiments/cookiecutter2_candidate_validation.md`: tracked validation
  report for `bugsinpy_cookiecutter_2`. It records the multiple-hook oracle,
  11 candidate patches, F2P validation, P2P-broad validation over 278 stable
  tests, and admission as the third project-level main task.
- `experiments/cookiecutter3_candidate_validation.md`: tracked validation
  report for `bugsinpy_cookiecutter_3`. It records the prompt-choice
  `show_choices=False` oracle, four candidate patches, F2P validation,
  P2P-broad validation over 255 stable tests, and admission as the fourth
  project-level main task.
- `experiments/tqdm9_candidate_validation.md`: tracked validation report for
  `bugsinpy_tqdm_9`. It records the SI-format and `len(tqdm(total=...))`
  oracle, seven curated candidate patches, F2P validation, P2P-broad validation
  over 12 stable tests, and admission as the fifth project-level main task.
- `experiments/pysnooper1_candidate_validation.md`: tracked validation report
  for `bugsinpy_PySnooper_1`. It records the UTF-8 snoop-log oracle, isolated
  declared test dependency environment, six curated candidate patches, F2P
  validation, P2P-broad validation over 24 stable tests, and admission as the
  sixth project-level main task.
- `experiments/pysnooper3_candidate_validation.md`: tracked validation report
  for `bugsinpy_PySnooper_3`. It records the file-output oracle, isolated
  declared dependency environment, four candidate patches, F2P validation,
  P2P-broad validation over four stable tests, and admission as the seventh
  project-level main task. `bugsinpy_PySnooper_2` remains a blocked
  experimental-boundary case.
- `experiments/p2p_scope_policy.md`: official-test-root P2P policy. It allows
  project-level P2P-broad construction from a project's official test roots
  when full-repository discovery repeatedly times out, while still forbidding
  task-file-level scope and preserving the `p2p_broad_size >= 3` gate.
- `experiments/fastapi1_scope_probe.md`: FastAPI 1 probe result. It records the
  clear F2P oracle, two full-repo discovery timeouts, the approved `tests/`
  official-root attempt, and the final
  `pending_blocked_official_test_root_timeout` status.
- `experiments/fastapi2_sanic1_feasibility.md`: follow-up broader-pool probe.
  It records `bugsinpy_fastapi_2` as a clear-F2P shared FastAPI scope-risk case
  and `bugsinpy_sanic_1` as a clear-F2P task whose project-level P2P-broad
  construction timed out without a manifest.
- `experiments/scrapy1_feasibility.md`: Scrapy 1 dependency-boundary probe. It
  records `bugsinpy_scrapy_1` as blocked because declared `Twisted==20.3.0`
  requires unavailable local native build tools before the retained F2P oracle
  can run.
- `experiments/youtubedl1_feasibility.md`: youtube-dl 1 feasibility probe. It
  records a clear retained F2P oracle but blocks main-cohort admission because
  project-level unittest P2P-broad construction timed out before producing a
  manifest.
- `experiments/tornado1_feasibility.md`: Tornado 1 feasibility probe. It
  records the Windows selector event loop compatibility boundary, a clear
  retained websocket F2P oracle, and a project-level unittest P2P construction
  timeout.
- `experiments/tornado9_feasibility.md`: Tornado 9 feasibility probe. It
  records the same-task checkout parallelism boundary, a clear `url_concat`
  F2P oracle, and a shared Tornado project-level unittest P2P timeout.
- `experiments/tornado2_feasibility.md`: Tornado 2 feasibility probe. It
  records a clear redirect PUT F2P oracle under the Windows selector event loop
  policy, plus a P2P dry-run only; no real P2P manifest exists, so the task is
  not admitted.
- `experiments/ansible2_feasibility.md`: Ansible 2 feasibility probe. It
  records a checkout timeout before F2P, with the incomplete retained workspace
  removed and no task-file downgrade.
- `experiments/matplotlib1_feasibility.md`: Matplotlib 1 feasibility probe. It
  records an unestablished F2P oracle due to checkout/test-layout issues and
  missing compiled `ft2font` extension.
- `experiments/evp7_protocol_pilot.md`: Option A execution record. It documents
  the EVP-7 freeze, generated manifests, blocker registry, and why candidate
  records/evidence packets are the next step instead of blind BugsInPy
  expansion. It now records controlled admissions through the frozen
  20-task/94-candidate/376-packet cohort; the earlier 12/62/248 and 13/66/264
  states are historical checkpoints.
- `experiments/evp7_g5_metric_scaffold.md`: no-API G5 metric scaffold report.
  It documents the FACR/Evidence Gain computation and the boundary that dry-run
  metric variation is not LLM signal evidence.
- `experiments/evp7_g5_llm_run_readiness.md`: no-API readiness report for the
  G5 LLM verifier run, including prompt id, prompt scope, stop conditions, and
  required user confirmations.
- `experiments/evp7_g5_execution_confirmation_packet.md`: human-facing
  confirmation packet for the G5 run. It records safe command
  order and forbidden actions before local config creation and API execution.
- `experiments/evp7_g5_llm_full_run_result.md`: historical tracked summary of
  the earlier 248-record DeepSeek official EVP-7 G5 full run. Raw model
  responses remain ignored under `outputs/`.
- `experiments/evp7_g5_full_run_quality_audit.md`: historical tracked
  claim-boundary audit for the earlier 248-record DeepSeek run. It lists
  supported pilot claims, unsupported claims, and limitations.
- `experiments/evp7_g5_llm_376_full_result.md`: tracked summary of the current
  376-record DeepSeek official EVP-7 G5 full run on the frozen
  20-task/94-candidate cohort. Raw model responses remain ignored under
  `outputs/`.
- `experiments/evp7_g5_376_full_quality_audit.md`: tracked claim-boundary audit
  for the current 376-record DeepSeek run. It records the bounded pilot signal,
  zero observed false accepts, complete cost observability, and unsupported
  scale/baseline/E6-strict/billing claims.
- `experiments/evp7_next_decision_packet_20260618.md`: no-API next-decision
  packet. It separates the current submit-ready four-anchor paper route from
  second-model key-anchor replication, new 30-50 bug expansion, and new
  verifier-design work; each experimental path requires explicit user
  confirmation before execution.
- `experiments/evp7_expansion_readiness.md`: controlled-expansion readiness
  report after EVP-7 G5. It records current main tasks, blocked-risk counts,
  broader BugsInPy metadata candidates, bounded project-lane probe rules, and
  the latest checkout/P2P blockers such as `bugsinpy_youtube-dl_10`,
  `bugsinpy_youtube-dl_13`, and the environment-blocked
  `bugsinpy_cookiecutter_4` P2P construction.
- `experiments/evp7_fastapi4_f2p_probe.md`: F2P-only controlled probe for
  `bugsinpy_fastapi_4`, currently blocked by current-environment Pydantic v2
  import incompatibility before target-test execution.
- `experiments/evp7_sanic2_f2p_probe.md`: F2P-only controlled probe for
  `bugsinpy_sanic_2`; the isolated dependency recheck now establishes F2P,
  but Sanic official tests-root P2P timed out without a manifest, so it is not
  admitted.
- `experiments/thefuck5_feasibility.md`: blocked follow-up probe for
  `bugsinpy_thefuck_5`. It establishes F2P under a task-specific legacy pytest
  env, but rules-root git P2P policies fail the >=3 gate or time out, so the
  task is not admitted.
- `experiments/evp7_parallel_f2p_triage_20260613.md`: parallel F2P-only triage
  for `scrapy_2`, `tornado_1`, and `youtube-dl_2`; only `youtube-dl_2` produced
  a new clean F2P signal in this batch.
- `experiments/evp7_remaining_f2p_triage_20260613.md`: remaining F2P-only
  triage for `ansible_1`, `luigi_1`, and `matplotlib_1`; all remain blocked
  under the no-install/no-edit boundary.
- `experiments/evp7_youtubedl_f2p_continuation_20260613.md`: youtube-dl
  F2P-only continuation for `youtube-dl_3`, `youtube-dl_4`, and
  `youtube-dl_5`; all three established clean F2P. `youtube-dl_4` and
  `youtube-dl_5` have since completed formal P2P/candidate admission, while
  `youtube-dl_3` remains a P2P candidate.
- `experiments/evp7_youtubedl_pure_utils_f2p_20260613.md`: pure-utils
  youtube-dl F2P-only continuation for `youtube-dl_6`, `youtube-dl_7`, and
  `youtube-dl_11`; all three established clean F2P. `youtube-dl_6` and
  `youtube-dl_7` have since completed formal P2P/candidate admission, while
  `youtube-dl_11` remains a P2P candidate.
- `experiments/evp7_youtubedl_p2p_decision_packet_20260613.md`: decision
  packet for whether to run one bounded project-level P2P-broad attempt for the
  current seven clean-F2P `youtube-dl` candidates. It now includes a no-run
  static preflight sweep that selects `youtube-dl_7` as the lowest-static-cost
  representative.
- `experiments/evp7_youtubedl_p2p_execution_attempt_20260613.md`: tracked
  record of the approved `bugsinpy_youtube-dl_7` P2P attempt. The command timed
  out before producing a manifest because dynamically generated
  `test.test_download.TestDownload.*` tests entered the batch. The follow-up
  approved execution-chain fix reran with the explicit
  `test.test_download.TestDownload` nodeid prefix exclusion and produced
  `data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json` with 108 P2P-broad
  tests.
- `experiments/youtubedl7_candidate_validation.md`: formal admission record for
  `bugsinpy_youtube-dl_7`. It documents the retained `js_to_json` oracle, four
  candidate records, oracle validation, P2P-broad validation, registry
  admission, and the 8-task/46-candidate/184-packet artifact refresh.
- `experiments/youtubedl6_candidate_validation.md`: formal admission record for
  `bugsinpy_youtube-dl_6`. It documents the retained DFXP time oracle, four
  candidate records, project-level P2P-broad validation with 110 retained
  unittest tests, registry admission, and the 9-task/50-candidate/
  200-packet no-API artifact refresh.
- `experiments/youtubedl5_candidate_validation.md`: formal admission record for
  `bugsinpy_youtube-dl_5`. It documents the retained unified-timestamp oracle,
  four candidate records, project-level P2P-broad validation with 128 retained
  unittest tests, registry admission, and the then-current 10-task/54-candidate/
  216-packet no-API artifact refresh.
- `experiments/youtubedl4_candidate_validation.md`: formal admission record for
  `bugsinpy_youtube-dl_4`. It documents the retained JSInterpreter call oracle,
  four candidate records, project-level P2P-broad validation with 137 retained
  unittest tests, registry admission, and the then-current 12-task/62-candidate/
  248-packet no-API artifact refresh. The latest 376-packet real G5 run
  supersedes that historical cohort as the current paper-facing result.
- `experiments/youtubedl11_candidate_validation.md`: formal admission record
  for `bugsinpy_youtube-dl_11`. It documents the retained `str_to_int` oracle,
  four candidate records, project-level P2P-broad validation with 160 retained
  unittest tests, registry admission, and the then-current 13-task/66-candidate/
  264-packet no-API artifact refresh.
- `experiments/youtubedl16_candidate_validation.md`: formal admission record
  for `bugsinpy_youtube-dl_16`. It documents the retained DFXP bytes oracle,
  four candidate records, project-level P2P-broad validation with 147 retained
  unittest tests, registry admission, and the then-current 14-task/70-candidate/
  280-packet no-API artifact refresh.
- `experiments/youtubedl17_candidate_validation.md`: formal admission record
  for `bugsinpy_youtube-dl_17`. It documents the retained `cli_bool_option`
  oracle, four candidate records, project-level P2P-broad validation with 146
  retained unittest tests, registry admission, and the then-current
  15-task/74-candidate/296-packet no-API artifact refresh.
- `experiments/youtubedl43_candidate_validation.md`: formal admission record
  for `bugsinpy_youtube-dl_43`. It documents the retained `url_basename`
  oracle, four candidate records, project-level P2P-broad validation with 18
  retained unittest tests, registry admission, and the then-current
  16-task/78-candidate/312-packet no-API artifact refresh.
- `experiments/youtubedl20_candidate_validation.md`: formal admission record
  for `bugsinpy_youtube-dl_20`. It documents the retained
  `get_element_by_attribute` oracle, four candidate records, project-level
  P2P-broad validation with 142 retained unittest tests, registry admission,
  and the then-current 17-task/82-candidate/328-packet no-API artifact refresh.
- `experiments/youtubedl21_candidate_validation.md`: formal admission record
  for `bugsinpy_youtube-dl_21`. It documents the retained `urljoin` bytes
  oracle, four candidate records, project-level P2P-broad validation with 143
  retained unittest tests, registry admission, and the then-current
  18-task/86-candidate/344-packet no-API artifact refresh.
- `experiments/youtubedl23_candidate_validation.md`: formal admission record
  for `bugsinpy_youtube-dl_23`. It documents the retained `js_to_json`
  single-line comment oracle, four candidate records, project-level P2P-broad
  validation with 137 retained unittest tests, registry admission, and the
  then-current 19-task/90-candidate/360-packet no-API artifact refresh.
- `experiments/youtubedl37_candidate_validation.md`: formal admission record
  for `bugsinpy_youtube-dl_37`. It documents the retained `uppercase_escape`
  oracle, four candidate records, project-level P2P-broad validation with 30
  retained unittest tests, registry admission, and the current
  20-task/94-candidate/376-packet no-API artifact refresh.
- `experiments/youtubedl2_candidate_validation.md`: formal admission record for
  `bugsinpy_youtube-dl_2`. It documents the retained MPD parser oracle, four
  candidate records, project-level P2P-broad validation with 147 retained
  unittest tests, registry admission, and the previous 11-task/58-candidate/
  232-packet artifact refresh that was covered by the repaired DeepSeek G5
  full run before the later 248-packet cohort became current.
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
  no-API outputs, API credentials/config readiness, and Git repository status,
  including working-tree cleanliness, upstream ahead/behind visibility, and
  latest API preflight report state.
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
  conditional claim separately. It now also verifies the resolved
  `youtube-dl_7` P2P admission manifest, including the recorded scope policy and
  P2P-broad size. Latest report:
  `outputs/goal_completion/latest.md`.
- `scripts/write_human_input_packet.py`: writes an ignored handoff packet that
  lists missing human inputs, safe command order, and forbidden actions before
  real API execution. It includes smoke/full postprocess commands with expected
  candidate counts, separate prompt-only/tool-augmented claim readiness, and the
  current required human-input list. When the tracked youtube-dl P2P manifest
  exists, it suppresses the stale approval-gated rerun command. Latest report:
  `outputs/handoff/human_input_packet.md`.
- `scripts/write_git_sync_packet.py`: writes an ignored Git sync decision
  packet with current Git state, upstream ahead/behind visibility, old remote
  context, required push/defer decision, staging allowlist, safe command
  template, post-sync acceptance criteria, and forbidden actions. Latest report:
  `outputs/handoff/git_sync_packet.md`.
- `scripts/audit_git_sync_packet.py`: audits the Git sync packet safety rules,
  including the human decision gate, ahead/behind fields, staging allowlist,
  ignored local-file checks before push, ahead-log inspection before push, and
  the ban on `git add .`. Latest report:
  `outputs/git_sync_packet_audit/latest.md`.
- `scripts/write_pre_api_handoff.py`: one-command local handoff that refreshes
  readiness, reproducibility, paper readiness, plan progress, goal completion,
  experiment run records, human-input, Git-decision, and Git handoff audit
  reports without calling model APIs. Its summary separates prompt-only positive
  claim readiness from the tool-augmented conditional claim. Latest report:
  `outputs/handoff/pre_api_handoff.md`.
- `scripts/write_experiment_run_records.py`: writes the experiment run ledger
  required by the AI execution plan. It summarizes no-API reproduction, smoke
  API, prompt-only full API, tool-augmented full API, and local quality-gate
  records using existing JSON evidence and marks whether any run is allowed to
  support a paper claim. Latest report: `outputs/experiment_run_records/latest.md`.
- `scripts/audit_paper_readiness.py`: Stage-E audit that prevents moving from
  the pre-API methods draft to positive claims until real API outputs, failure
  examples, and the relevant gate are present. It reports prompt-only positive
  readiness and tool-augmented conditional readiness separately, so the
  `tool_augmented_evidence` result cannot be mistaken for prompt-only model
  ability. It now also reports the current EVP-7 G5 bounded-pilot claim
  readiness from the raw-output-free 376-record DeepSeek summary and quality
  audit. It also checks paper framing, active protocol, protocol pilot report,
  final roadmap current-state consistency, reader-flow continuity, and
  final-polish claim wording before marking the current result claim ready.
  Its `submission_package_ready` field additionally requires the no-API
  submission handoff boundary to pass, and its required docs include the
  advisor-facing workload response packet.
- `scripts/write_paper_tables.py`: generates Markdown and LaTeX paper tables
  from dataset summary, validation summary, metrics, deterministic
  reproducibility comparison, the current EVP-7 workload ledger, and the
  current EVP-7 G5 376-record summary plus claim-boundary audit.
- `scripts/write_ieee_latex_draft.py`: generates the current IEEEtran
  submission draft at `docs/paper/ieee_submission_draft.tex` from generated
  dataset/no-API tables, audited prompt-only and tool-augmented metrics, and
  the current EVP-7 G5 376-record summary plus claim-boundary audit.
  It also owns the paper-facing figure captions, including the compact EVP-7
  E0/E2/E4/E6 fig2 evidence-level caption checked by paper readiness.
  The generated narrative foregrounds the frozen EVP-7 bounded result while
  keeping the earlier 30-candidate API pilot as diagnostic design evidence and
  reporting unsupported EVP-7 interpretations explicitly; it also adds the
  workload-at-a-glance bridge that separates structural 21/98/392 work from
  paper-facing 20/94/376 real LLM review.
  The old `docs/paper/ieee_preapi_draft.tex` is retained only as historical
  pre-API context.
- `scripts/generate_paper_figures.py`: generates the publication figure set
  under `docs/figures/` in PDF, SVG, and PNG formats. Figures cover the
  workflow, compact E0/E2/E4/E6 evidence boundary, dataset composition,
  first-pilot result tradeoff, claim boundary, EVP-7 evidence visibility
  curve, and the model decision-to-metric computation flow.
- `scripts/analyze_evp7_g5_statistics.py`: generates the raw-output-free
  statistical analysis for the frozen EVP-7 G5 376-record run. It reads ignored
  review records structurally, joins tracked candidate labels only for aggregate
  metrics, and writes Wilson/bootstrap/paired-breakdown artifacts.
- `scripts/analyze_evp7_utility_sensitivity.py`: generates the raw-output-free
  utility sensitivity analysis for EVP-7, varying false-accept, escalation, and
  false-reject penalties without changing the frozen cohort or prompt.
- `scripts/analyze_evp7_tool_attribution.py`: generates the raw-output-free
  deterministic tool-only attribution analysis for EVP-7 by comparing matched
  E4/E6 tool-only and LLM decisions without writing raw model responses.
- `scripts/analyze_evp7_qualitative_cases.py`: generates the raw-output-free
  qualitative case report for selected EVP-7 decision paths while keeping
  reviewer-facing decision sequences separate from evaluator-only labels.
- `scripts/write_ieee_latex_draft.py`: generates the current IEEE draft,
  including the related-work positioning section and bibliography as well as
  the EVP-7 bounded-result narrative.
- `scripts/audit_paper_claim_boundary.py`: generates the EVP-7 claim-boundary
  traceability audit and fails when supported/unsupported claims are not covered
  by the current paper artifacts or required IEEE boundary cues are missing.
- `figures/`: reproducible paper figure assets. The IEEE submission draft uses
  the PDF versions, while PNG versions are for quick local inspection.
- `figures/imagegen/`: generated raster visual candidates plus exact prompts
  for graphical abstracts, presentations, and visual drafts. These PNGs are
  conceptual assets and must not replace the reproducible numeric/vector
  figures when supporting experimental claims.
- `artifact/anonymous_artifact.md`: inclusion and exclusion policy for the
  anonymous supplemental package.
- `artifact/submission_checklist.md`: final submission checklist for the current
  IEEE draft and anonymous artifact. It records required paper figures,
  claim-boundary evidence, rebuild/audit commands, exclusion boundaries, and
  ready-to-submit criteria, plus the latest local PDF/artifact verification
  status after the no-API paper package rebuild.
- `artifact/submission_handoff_20260618.md`: no-API handoff for the current
  four-anchor EVP-7 submission package. It records the latest PDF/artifact
  rebuild commands, audit results, default next action, and forbidden
  experiment actions without explicit user confirmation.
- `artifact/submission_freeze_candidate_20260618.md`: no-API freeze-candidate
  packet for the current paper/artifact package. It records the candidate
  state, open user confirmations, and no-API/no-expansion boundary before any
  final freeze decision.
- `scripts/prepare_anonymous_artifact.py`: package builder for anonymous
  supplemental materials. It includes tracked source, scripts, configs, docs,
  examples, and the final submission checklist while excluding credentials,
  local configs, raw outputs, benchmark checkouts, and generated artifacts.
- `scripts/audit_anonymous_artifact.py`: validates the generated anonymous ZIP
  contents, required files, manifest consistency, and exclusion rules. It now
  requires the submission checklist, the no-API submission handoff, the
  submission freeze-candidate packet, and all paper-facing PDF figures,
  including `fig7_decision_metric_flow.pdf`, plus the advisor-facing workload
  response packet.
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
  buggy/fixed checkout root via `--source-workspace-root`. It also supports
  task-level partial-candidate allowlists for cases where generic partial diffs
  are label-invalid after oracle validation.
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
  readiness, submission-handoff and freeze-candidate boundary checks, and
  anonymous artifact dry-run.
- `scripts/audit_submission_handoff.py`: no-API audit for
  `docs/artifact/submission_handoff_20260618.md`. It fails if the handoff loses
  the current four-anchor counts, the next-decision packet pointer, the default
  no-API continuation, or the forbidden-action boundary.
- `scripts/audit_submission_freeze_candidate.py`: no-API audit for
  `docs/artifact/submission_freeze_candidate_20260618.md`. It fails if the
  packet stops being a candidate, claims final freeze, authorizes API calls or
  expansion, loses the no-E1/E3/E5 boundary, or reports a stale artifact file
  count.
- `scripts/analyze_patch_verification.py`: patch-verification metrics analyzer
  for verifier outputs. By default, it reads
  `data/cohorts/task_cohort_registry.json` and filters metrics to the
  `p2p_broad_main` task cohort; use `--no-cohort-filter` only for diagnostic or
  appendix analyses.
- `scripts/validate_patch_candidates.py`: no-API executable validator that
  copies retained buggy checkouts, applies candidate patches, and runs retained
  oracles.
- `scripts/build_task_generation_accounting.py`: builds task-level generation
  accounting records from validation reports, relabeled generated candidates,
  generation prompt manifests, and the tracked task cohort registry.
- `scripts/build_pass_to_pass_scope.py`: collects project tests and builds
  P2P-core/P2P-broad stable runnable subsets for a task. It supports pytest and
  bounded unittest discovery/runner adapters, explicit nodeid-prefix exclusions
  for generated tests, plus `--dry-run` input validation that prints a no-run
  plan without creating output directories or manifests.
- `scripts/static_unittest_p2p_preflight.py`: no-run AST preflight for unittest
  P2P candidates. It estimates static test-method counts, token exclusions, and
  buggy/fixed remaining-set differences before expensive dynamic P2P runs.
- `scripts/audit_youtubedl_p2p_decision.py`: no-run consistency audit for the
  youtube-dl P2P decision packet. It verifies the recommended representative,
  command task, fail-to-pass nodeid, checkout existence, approval-required
  command packet, full command flags, builder dry-run result, and lowest
  static-cost candidate match.
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
- `scripts/screen_bugsinpy_candidate_pool.py`: metadata-level BugsInPy
  candidate-pool screener. It reads the BugsInPy source archive, current cohort
  registry, `bug.info`, `run_test.sh`, and requirements files, then emits a
  broader project/task screening report before checkout.
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
  presence. It can write JSON/Markdown reports under ignored `outputs/`.
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
- `scripts/oracles/`: executable real-bug oracles, including the retained
  `tqdm_9` SI-format, total-length oracle, and
  `youtubedl_7_js_to_json.py` and `youtubedl_6_dfxp_time.py` admission oracles.
- `scripts/validate_real_bug_dataset.py`: real-bug metadata and oracle
  validation.
- `scripts/build_real_bug_review_dataset.py`: source-context builder to adapt.
- `scripts/build_claim_evidence_packets.py`: evidence packet builder to adapt.
- `../scripts/build_evp7_protocol_manifests.py`: reproducible EVP-7 task and
  blocker manifest builder.
- `../scripts/build_youtubedl7_candidates.py`: builds the four-candidate
  `bugsinpy_youtube-dl_7` admission slice used before registry promotion.
- `../scripts/build_youtubedl6_candidates.py`: builds the four-candidate
  `bugsinpy_youtube-dl_6` admission slice used before registry promotion.
- `../scripts/build_evp7_candidate_manifest.py`: promotes validated EVP-7
  candidate outputs into tracked candidate records.
- `../scripts/build_evp7_evidence_packets.py`: builds model-visible E0/E2/E4/E6
  evidence packet records and runs the leakage audit.
- `../scripts/run_evp7_visible_tests.py`: reruns predeclared visible tests in
  candidate workdirs to generate independent E4 visible outcome evidence.
- `../scripts/build_evp7_visible_tool_summaries.py`: builds deterministic E6
  visible tool summaries from already model-visible evidence.
- `../scripts/run_evp7_tool_only_baselines.py`: builds deterministic EVP-7
  tool-only baseline decisions and aggregate metrics.
- `../scripts/run_evp7_merge_gate_schema_dry_run.py`: generates no-API
  accept/reject/escalate schema dry-run records from model-visible EVP-7
  packets and validates parser stability before any real LLM API call.
- `../scripts/analyze_evp7_schema_dry_run_metrics.py`: computes G5 aggregate
  metrics over schema dry-run, mock workflow, or real LLM review records,
  joining evaluator labels only for aggregate metrics and labeling the review
  source before stating signal status.
- `../scripts/build_evp7_g5_llm_prompt_manifest.py`: renders the G5
  evidence-visibility LLM prompt in memory, writes prompt hashes/lengths and
  readiness metadata, and verifies prompt-boundary leakage without API calls.
- `../scripts/build_evp8_prompt_manifest.py`: audits the frozen EVP-8 prompt
  template, writes prompt-template manifest and boundary-audit JSON, and does
  not generate evidence packets or call model APIs.
- `../scripts/build_evp8_packet_schema_dry_run.py`: validates planned EVP-8
  packet skeleton structure and output schema in memory, then writes summary
  artifacts without generating full packet JSONL records.
- `../scripts/build_evp8_cost_baseline_dry_run.py`: validates EVP-8 planned
  cost-observability fields and deterministic baseline output schema without
  local API config reads, raw outputs, or model calls.
- `../scripts/create_evp8_deepseek_qwen_local_config.py`: creates or dry-runs
  the ignored EVP-8 DeepSeek/Qwen local config from the tracked no-secret
  example config.
- `../scripts/preflight_evp8_deepseek_qwen.py`: validates the ignored EVP-8
  DeepSeek/Qwen local config and `.env` key presence without printing secrets
  or calling APIs.
- `../scripts/run_evp8_deepseek_qwen_smoke.py`: guarded EVP-8 DeepSeek/Qwen
  smoke runner. It supports check-only without API calls and refuses real smoke
  execution unless an ignored local config, strict preflight, explicit
  `--execute`, and a configured `--model-id` are supplied.
- `../scripts/write_evp8_smoke_execution_packet.py`: writes the no-API EVP-8
  DeepSeek/Qwen smoke execution packet and Markdown companion from tracked
  protocol/preflight/check-only summaries.
- `../scripts/audit_evp8_smoke_results.py`: audits future EVP-8 DeepSeek/Qwen
  smoke summaries without reading raw outputs; currently reports
  `waiting_for_execution` until real smoke summaries exist.
- `../configs/evp7_g5_llm.example.json`: tracked template for the G5 LLM
  run. It intentionally contains placeholders and is not API-ready.
- `../scripts/preflight_evp7_g5_llm_run.py`: no-API structural and strict
  readiness checker for the G5 LLM run config.
- `../scripts/run_evp7_g5_llm_workflow.py`: guarded G5 workflow. It
  supports check-only and mock validation without API calls, and refuses real
  execution unless strict preflight passes with an ignored local config and
  explicit `--execute`. Real execution also supports explicit bounded
  `--concurrency` while preserving ordered JSONL output, records raw-output-free
  usage summaries, estimates DeepSeek V4 Pro token cost when provider cost is
  absent, and fails executed runs whose cost remains unknown.
- `../scripts/create_evp7_g5_llm_local_config.py`: dry-run/write helper for
  ignored `configs/evp7_g5_llm.local.json`. Write mode requires explicit
  provider, model, cost ceiling, smoke scope, and full-run permission.
- `../scripts/summarize_evp7_g5_llm_full_run.py`: converts ignored real G5
  outputs into tracked JSON/Markdown summaries without copying raw model
  responses. It records workflow cost summaries when present.
- `../scripts/audit_evp7_g5_full_run_quality.py`: audits the tracked G5
  full-run summary without reading raw outputs and writes the claim-boundary
  JSON/Markdown audit, including cost-observability completeness.
- `../scripts/summarize_evp7_expansion_readiness.py`: summarizes current
  registry state, broader BugsInPy rescreen outputs, and tracked controlled
  probe statuses into expansion readiness artifacts.
- `scripts/analyze_tool_gated_reviews.py`: oracle-gated analysis reference.
- `experience/engineering_notes.md`: fresh operational notes for this new
  workspace.
- `../prompts/prompt_change_log.md`: prompt log for patch-verification prompts
  only. It records the EVP-8 prompt addition and the no-conflict check against
  the historical EVP-7 prompt.
- `../prompts/evp8_visible_evidence_merge_gate_v0_1.md`: frozen EVP-8 prompt
  template for the full-ladder no-API protocol.

## Safety Rules

- Do not commit `.env`, local model configs, raw outputs, or benchmark checkouts.
- Do not use prompt-only adjudication as ground truth.
- Any positive result must distinguish LLM-only decisions from evidence-backed
  decisions.
- Do not run API calls until the no-API patch candidate dataset validates,
  realistic patch diffs are available, the difficult-negative ratio gate
  passes, and the API prompts/run metadata are documented.
