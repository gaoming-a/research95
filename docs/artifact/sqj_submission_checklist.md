# SQJ Submission Checklist

Status: SQJ source package checklist, not final freeze.
Date: 2026-06-22

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

## Manuscript Source Package

- Main manuscript source:
  `docs/paper/sqj_submission_draft.tex`
- Bibliography:
  `docs/paper/sqj_references.bib`
- Manuscript generator:
  `scripts/write_sqj_latex_draft.py`
- Framing and claim boundary:
  `docs/paper/sqj_submission_framing.md`
- Generated table sources:
  `docs/paper/generated_tables.md`
  `docs/paper/generated_tables.tex`
- Current LaTeX class target:
  Springer Nature `sn-jnl`
- PDF compile gate:
  PDF compile gate is pending local `sn-jnl.cls` availability. The current
  gate validates source structure only.

## Paper Figures

The current reproducible figure set is available in PDF, SVG, and PNG:

- `docs/figures/fig1_framework.pdf`
- `docs/figures/fig2_evidence_visibility.pdf`
- `docs/figures/fig3_dataset_composition.pdf`
- `docs/figures/fig4_result_tradeoff.pdf`
- `docs/figures/fig5_claim_boundary.pdf`
- `docs/figures/fig6_evp7_visibility_curve.pdf`
- `docs/figures/fig7_decision_metric_flow.pdf`

These figures were originally built for the earlier paper package. They are
available as reproducible assets, but final SQJ figure placement and caption
wording still require a later layout pass.

## Supported Claims

- Evidence visibility is a first-order experimental variable for LLM-based
  patch verification.
- On the frozen EVP-8 v0.1 packet set, five selected models show descriptive
  per-level decision patterns.
- The observed patterns are model-dependent and non-monotonic.
- Blocked Kimi attempts are cost/execution-risk evidence only and are not valid
  model-result records.
- API execution remains frozen after the EVP-8 cost overrun.

## Forbidden Claims

The SQJ package must not claim:

- that LLM superiority over deterministic baselines is supported;
- that a final evidence-level ranking has been established;
- that E6 strictly improves over E4 as a general result;
- that the result scale-generalizes beyond the frozen EVP-8 v0.1 packet set;
- that SQJ recognition is guaranteed before school/department confirmation;
- that Open Access or APC payment is approved.

## Rebuild Commands

```powershell
python scripts\write_paper_tables.py
python scripts\write_sqj_latex_draft.py --check
python scripts\audit_sqj_submission_checklist.py --out-json outputs\sqj_submission_checklist_audit\latest.json --out-md outputs\sqj_submission_checklist_audit\latest.md
python scripts\summarize_evp8_five_model_synthesis.py --check
python scripts\summarize_evp8_cost_accounting.py --check
python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md
python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md
```

## Ready For Next Gate Criteria

- SQJ source draft regenerates from tracked inputs.
- SQJ checklist audit passes.
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
