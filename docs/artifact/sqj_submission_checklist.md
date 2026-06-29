# SQJ Submission Checklist

Status: SQJ source package checklist, not final freeze.
Date: 2026-06-30

This checklist records the current Software Quality Journal (SQJ) submission
route. It does not authorize new experiments, model API calls, cohort
expansion, evidence-level changes, or raw model-response tracking.

## Venue And Cost Route

- Target route: Software Quality Journal (SQJ).
- Cost route: non-OA / subscription route unless the user explicitly approves
  APC payment.
- School requirement route: school/department recognition confirmation is
  required before submission.
- Recognition boundary: this checklist does not guarantee SQJ recognition.
  Confirmation must check the publication-year CCF list, school category
  policy, and high-risk or warning-list status.
- Current recognition gate status: `blocked_missing_school_recognition` until
  the school/department recognition decision is provided or confirmed.

## Manuscript Source Package

- Main manuscript source:
  `docs/paper/sqj_submission_draft.tex`
- Bibliography:
  `docs/paper/sqj_references.bib`
- Manuscript generator:
  `scripts/write_sqj_latex_draft.py`
- Framing and claim boundary:
  `docs/paper/sqj_submission_framing.md`
- Final-freeze readiness packet:
  `docs/artifact/sqj_final_freeze_readiness.md`
- Generated table sources:
  `docs/paper/generated_tables.md`
  `docs/paper/generated_tables.tex`
- Current LaTeX class target:
  Springer Nature `sn-jnl`
- PDF compile gate:
  PDF compile gate is pending local `sn-jnl.cls` availability. The current
  gate validates source structure and compile preflight only. The expected
  local status is `blocked_missing_sn_jnl_cls` until the official Springer
  Nature class is installed.

## SQJ Paper Figures

The current SQJ-specific figure set is available in PDF, SVG, and PNG:

- `docs/figures/sqj/sqj_fig1_evp8_protocol.pdf`
- `docs/figures/sqj/sqj_fig2_decision_patterns.pdf`
- `docs/figures/sqj/sqj_fig3_cost_boundary.pdf`

The legacy `docs/figures/fig1` through `fig7` assets remain reproducible
historical figures for the earlier IEEE/EVP-7 package. The SQJ route uses the
`docs/figures/sqj/` figure set as the current manuscript-facing figure set.

## Supported Claims

- Evidence visibility is a first-order experimental variable for LLM-based
  patch verification.
- On the frozen EVP-8 v0.1 packet set, five selected models show descriptive
  per-level decision patterns.
- The observed patterns are model-dependent and non-monotonic.
- Blocked Kimi attempts are cost/execution-risk evidence only and are not valid
  model-result records.
- The fresh realistic branch is a two-project source-acquisition negative result,
  not a verifier-ready main experiment.
- API execution remains frozen after the EVP-8 cost overrun.

## Forbidden Claims

The SQJ package must not claim:

- that LLM superiority over deterministic baselines is supported;
- that a final evidence-level ranking has been established;
- that E6 strictly improves over E4 as a general result;
- that the result scale-generalizes beyond the frozen EVP-8 v0.1 packet set;
- that the fresh realistic branch is a three-project verifier-ready main experiment;
- that the full-file generation repair demonstrates practical autonomous patch
  verification;
- that SQJ recognition is guaranteed before school/department confirmation;
- that Open Access or APC payment is approved.

## Rebuild Commands

```powershell
python scripts\write_paper_tables.py
python scripts\generate_sqj_figures.py
python scripts\write_sqj_latex_draft.py --check
python scripts\audit_sqj_submission_checklist.py --out-json outputs\sqj_submission_checklist_audit\latest.json --out-md outputs\sqj_submission_checklist_audit\latest.md
python scripts\audit_sqj_artifact_gate.py --out-json outputs\sqj_artifact_gate\latest.json --out-md outputs\sqj_artifact_gate\latest.md
python scripts\audit_sqj_school_recognition_gate.py --out-json outputs\sqj_school_recognition_gate\latest.json --out-md outputs\sqj_school_recognition_gate\latest.md
python scripts\audit_sqj_human_inputs_gate.py --out-json outputs\sqj_human_inputs_gate\latest.json --out-md outputs\sqj_human_inputs_gate\latest.md
python scripts\audit_sqj_pdf_compile_gate.py --out-json outputs\sqj_pdf_compile_gate\latest.json --out-md outputs\sqj_pdf_compile_gate\latest.md
python scripts\audit_sqj_final_freeze_readiness.py --out-json outputs\sqj_final_freeze_readiness\latest.json --out-md outputs\sqj_final_freeze_readiness\latest.md
python scripts\summarize_evp8_five_model_synthesis.py --check
python scripts\summarize_evp8_cost_accounting.py --check
python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md
python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md
```

## Ready For Next Gate Criteria

- SQJ source draft regenerates from tracked inputs.
- SQJ figures regenerate from tracked synthesis and cost summaries.
- SQJ checklist audit passes.
- SQJ artifact candidate gate passes as `candidate_artifact_dry_run_ready`;
  this is not a final artifact ZIP rebuild.
- SQJ school-recognition gate audit passes while keeping recognition blocked as
  `blocked_missing_school_recognition` until school/department confirmation is
  provided.
- SQJ human-input gate audit passes while keeping the human-input status blocked
  as `blocked_missing_human_inputs` until author and submission metadata are
  provided or confirmed.
- SQJ PDF compile gate audit passes while keeping the compile status blocked
  unless `sn-jnl.cls` is actually available.
- SQJ final-freeze readiness audit passes.
- EVP-8 five-model synthesis and cost accounting checks pass.
- Paper readiness and local quality gate pass.
- No model API calls are made.
- No raw model responses, `.env`, local configs, `outputs/`, `artifacts/`, or
  benchmark checkouts are committed.

## Not Final Freeze

This is not a final submission freeze. The SQJ package still needs:

- official school/department recognition confirmation;
- local or CI LaTeX compile after `sn-jnl.cls` is available;
- SQJ-specific figure placement and caption audit;
- author information, funding, acknowledgements, and competing-interest
  confirmation;
- final artifact package rebuild and audit.
