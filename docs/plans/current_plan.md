# Current Plan: AI-Generated Patch Verification

Last updated: 2026-06-05

## 1. Research Pivot

The previous direction tried to evaluate whether LLM cross-review or
agent-style context made code review more reliable. The result did not support
that strong hypothesis. The reusable finding is sharper:

> LLM-only review produces useful signals but is not a reliable merge gate
> because false positives persist on fixed/reference controls.

The new direction studies a more consequential problem:

> Can we reliably verify whether AI-generated patches should be accepted?

## 2. New Core Claim

Do not claim that cross-review is generally better. The target claim is:

> Evidence-first patch verification can reduce unsafe acceptance of incorrect
> AI-generated patches compared with LLM-only review, majority review, or
> agent-context review.

This claim must be proven with patch-level outcomes, not only reviewer opinions.

## 3. Experimental Unit

Each task should contain:

- a real issue or real bug;
- a candidate patch;
- source context around the patch;
- available tests or executable oracle;
- optional issue/test description;
- ground-truth patch outcome.

Patch outcome labels:

- `correct`;
- `incorrect`;
- `partial`;
- `overfitted`;
- `test_passing_wrong`;
- `irrelevant_or_noop`;
- `environment_invalid`.

Verifier decision labels:

- `accept`;
- `reject`;
- `escalate`;
- `invalid_output`.

## 4. Primary Metrics

- False accept rate: wrong patches accepted.
- False reject rate: correct patches rejected.
- Accepted precision: accepted patches that are actually correct.
- Correct-patch recall: correct patches accepted.
- Escalation rate: patches sent to human/tool review.
- Cost and invalid-output rate.

Candidate-level bug detection metrics from the old project are secondary.

## 5. Reusable Assets

Keep and adapt:

- real BugsInPy oracles in `scripts/oracles/`;
- paired buggy/fixed metadata design;
- claim-level evidence packet workflow;
- OpenRouter API wrapper and JSON parsing utilities;
- false-positive taxonomy and tool-gated upper-bound analysis as motivation.

Do not carry forward:

- generated-code benchmark framing as the main contribution;
- old IEEE real-bug draft as the active paper;
- prompt-only adjudication as ground truth;
- majority review as a claimed solution.

## 6. Immediate Work Order

Completed:

1. `scripts/build_patch_verification_dataset.py` generates
   `patch_verification_pilot_001`.
2. `scripts/analyze_patch_verification.py` computes the required no-API
   metrics.
3. The current no-API pilot contains 7 retained real-bug tasks, 30 candidates,
   and 90 deterministic verifier outputs.
4. Model-visible evidence packets use anonymous candidate ids and passed the
   label-leakage check.
5. Candidate patch text is now materialized from retained buggy/fixed checkout
   diffs when `--source-workspace-root` points to the external checkout root.
6. `scripts/validate_patch_candidates.py` applies each candidate patch and
   validates labels with retained oracles; the current pilot validates 30/30.
7. `docs/paper/patch_verification_draft.md` contains a pre-API methods draft
   with no-API validation results and explicit pending API sections.
8. `scripts/run_no_api_patch_pipeline.py` now reproduces the complete local
   no-API chain in one command. A fresh run to
   `outputs/patch_verification_pilot_repro_001` produced 30 candidates, 90
   baseline outputs, 30/30 executable validations, 60 prompt dry-run records,
   and a pilot report.
9. `scripts/write_reproducibility_manifest.py` now hashes deterministic
   no-API outputs and compares reproduced runs against the original pilot.
   `outputs/reproducibility/pilot_compare.json` currently reports
   `matched = true`.

Next:

1. At the start of a continuation turn, run
   `python scripts/audit_execution_readiness.py --out-json outputs/readiness_audit/latest.json --out-md outputs/readiness_audit/latest.md`
   to confirm no-API, API, and Git readiness.
2. Run
   `python scripts/audit_ai_plan_progress.py --out-json outputs/plan_progress/latest.json --out-md outputs/plan_progress/latest.md`
   to map execution stages to complete, partial, blocked, or pending.
3. Run
   `python scripts/write_human_input_packet.py --out-json outputs/handoff/human_input_packet.json --out-md outputs/handoff/human_input_packet.md`
   to produce the safe human-input checklist and command order before real API
   execution.
4. Run
   `python scripts/write_git_sync_packet.py --out-json outputs/handoff/git_sync_packet.json --out-md outputs/handoff/git_sync_packet.md`
   to record Git state and the required user decision before initialization or
   push. The report also includes a remote decision template, staging
   allowlist, ignore checks, cached-diff checks, and post-sync acceptance
   criteria; it does not execute `git init`, `git add`, `git commit`, or
   `git push`.
   Then run
   `python scripts/audit_git_sync_packet.py --out-json outputs/git_sync_packet_audit/latest.json --out-md outputs/git_sync_packet_audit/latest.md`
   to check that the Git handoff keeps the human decision gate, bans
   `git add .`, checks ignored local files before staging, and checks cached
   diffs after staging.
5. Run
   `python scripts/write_pre_api_handoff.py --out-json outputs/handoff/pre_api_handoff.json --out-md outputs/handoff/pre_api_handoff.md`
   to refresh all local pre-API handoff reports, including full-goal completion
   status, experiment run records, and Git handoff safety, without calling
   model APIs.
6. For any fresh local environment, first run
   `python scripts/run_no_api_patch_pipeline.py --out-dir outputs/patch_verification_pilot_repro_001`
   to verify the no-API pipeline without calling model APIs.
7. Run `scripts/write_reproducibility_manifest.py` to compare deterministic
   outputs in `outputs/patch_verification_pilot_001` and
   `outputs/patch_verification_pilot_repro_001`. The current comparison is
   matched.
8. Write and log the API pilot prompts for `llm_only` and `evidence_first`.
9. The current primary model path is DeepSeek official API with
   `--api-provider deepseek_official --model deepseek-v4-pro`. The OpenRouter
   shortlist/catalog files are retained only as alternative-path or historical
   model-selection documentation.
10. Use `scripts/audit_openrouter_model_catalog.py` only if the project later
    switches back to OpenRouter. In that case, verify candidate slug visibility
    before generating local config and pass `--require-openrouter-catalog` when
    network access is available.
11. Implement or adapt the API runner so every response records provider model id,
    prompt version, date, cost, raw response path, and invalid-output status.
   Status: implemented in `scripts/run_patch_verification_api_pilot.py` for
   DeepSeek official API and OpenRouter-compatible providers. DeepSeek official
   smoke has now been executed. The runner supports `--config`, `--dry-run`, and
   writes `metrics.json` after real API runs. Real API calls must go
   through `scripts/run_api_pilot_workflow.py`; the low-level runner is for
   dry-runs, mock checks, or workflow-internal execution. Direct real execution
   is rejected unless the guarded workflow supplies its internal flag.
   If a real API call fails mid-run, the low-level runner writes a sanitized
   `run_error.json`; completeness audit treats any run containing that file as
   incomplete and unusable as experiment evidence.
12. Run a smoke API pilot with `--limit 2` before running all validated 30
   candidates. Dry-run status: 60 rendered prompts passed label-leakage checks.
   Mock smoke status: `--mock-policy patch_surface` validates
   `reviews.jsonl -> metrics.json -> run_summary.md`, but is not an experiment.
13. Before any real API call, copy `configs/api_pilot.example.json` to an
   untracked local config or generate it with
   `scripts/create_api_pilot_local_config.py`. Before preflight, document the
   model in `configs/model_selection.local.json`, validate it with
   `scripts/validate_model_selection.py`, preferably generate it with
   `scripts/create_model_selection_local.py`, set the provider model id, add
   `.env`, and run `scripts/preflight_api_pilot.py`. The current config should
   use `DEEPSEEK_API_KEY`, `deepseek-v4-pro`, and `deepseek_official`.
   If the model id, source, capability band, and rationale are already
   explicitly chosen, `scripts/bootstrap_api_prereqs.py` can generate both
   ignored local configs, validate their model match, and run preflight in one
   command. Use `--dry-run --allow-missing-credentials` first when handing the
   task to another AI agent. The write mode requires `.env` to contain the
   current provider key; the DeepSeek official path requires `DEEPSEEK_API_KEY`
   before any local config files are written.
14. Regenerate `outputs/patch_verification_pilot_001/pilot_report.md` with
   `scripts/summarize_patch_verification_pilot.py` after each validation or
   dry-run update.
   Also regenerate the tracked summary
   `docs/experiments/patch_verification_pilot_report.md`.
15. Prefer `scripts/run_api_pilot_workflow.py` for real API smoke/full runs. It
   performs strict preflight and requires explicit `--execute` before any model
   call. The smoke run uses local config `smoke_limit=2`; after smoke passes,
   run the full pilot with
   `--run-dir outputs/patch_verification_api_pilot_002 --limit 0 --execute` to
   avoid overwriting smoke outputs and force all 30 candidates.
   Current DeepSeek smoke finding: `max_tokens=1200` caused empty final content
   on one candidate because the output ended at the reasoning stage. The valid
   smoke is `outputs/patch_verification_api_pilot_001_tokens4096`, using
   `max_tokens=4096`, with 4 non-mock review records, completeness passed, and
   invalid output rate 0. The smoke gate remains `indeterminate` and is not
   paper evidence.
16. After any smoke or full API run, run `scripts/postprocess_api_pilot_run.py`
   on the run directory to generate all API post-run reports. The wrapper was
   validated on the mock smoke run and correctly returned `not_evidence`.
   Use `--expected-candidates 2` for smoke and `--expected-candidates 30` for
   the full run so `run_completeness.json` records the expected count boundary.
17. If debugging step-by-step, generate a run-specific Markdown report
   with `scripts/summarize_api_pilot_results.py`. If the run uses
   `--mock-policy`, keep the report under ignored `outputs/` only and do not
   cite it as model evidence.
18. After a real full API run, run `scripts/extract_api_failure_examples.py` to
   prepare qualitative examples for failure analysis. Mock extraction only
   validates the local extraction pipeline.
19. Run `scripts/evaluate_api_pilot_gate.py` after the full API run to produce a
   stop/continue report. Do not write a positive paper claim if the verdict is
   `stop_or_redesign`, `indeterminate`, or `not_evidence`.
20. Run `scripts/audit_paper_readiness.py` before moving the paper beyond the
   pre-API methods draft.
21. Run `scripts/audit_goal_completion.py` before claiming the whole plan is
   complete. This audit requires real API results, postprocess reports, paper
   gate readiness, artifact safety, local quality, and Git repository evidence.
   Local quality now includes the no-API API-failure-handling audit and
   experiment run-record ledger generation.
22. Use `scripts/prepare_anonymous_artifact.py` to build the anonymous
   supplemental package. The current package contains source, docs, examples,
   and config templates only; it excludes outputs, data, credentials, and local
   checkouts.
23. Use `docs/figures/imagegen/` only as optional raster visual candidates for
   graphical abstracts, slides, and visual drafts. The exact prompts are stored
   in `docs/figures/imagegen/prompts.md`. These PNGs are not reproducible
   experimental evidence and must not replace the PDF/SVG figures generated by
   `scripts/generate_paper_figures.py`.
24. Treat `docs/plans/final_paper_roadmap_zh.md` as the canonical subsequent
   research target and long-term final-paper route. It records the
   evidence-visibility empirical-study plan, including data expansion,
   tool-only baselines, hidden-evaluator separation, evidence ablation,
   generated tests, multi-model verification, and artifact goals. It is the
   next-goal source, while this file and `current_plan_zh.md` remain the
   per-turn execution logs.
25. Treat the six-step prerequisite outputs as bounded preparation for the
   middle-report expansion route: `scripts/run_tool_only_baseline.py`,
   `docs/experiments/tool_only_baseline_result.md`,
   `docs/experiments/qualitative_case_report.md`,
   `docs/experiments/leakage_policy.md`, and
   `docs/experiments/bugsinpy_expansion_screening.md`. The BugsInPy screening
   registry is not an expanded validated dataset until task-specific oracles
   and candidate validations are completed.
26. Analyze whether evidence-first reduces false accepts without collapsing
   correct-patch recall or accepting only by rejecting/escalating everything.
27. Update README, index, plan, and experiment records after every change.

## 7. Stop/Continue Gate

Continue only if the pilot can show at least one of:

- evidence-first verification reduces false accepts versus LLM-only review;
- test-passing wrong or partial patches appear in the dataset and are
  meaningfully difficult;
- claim-level evidence explains why LLM-only decisions fail.

Stop if the new dataset cannot produce realistic incorrect/partial patches or
if the verifier reduces false accepts only by rejecting almost everything.
