# Final Submission Checklist

Date: 2026-06-18

This checklist records the current paper and anonymous supplemental artifact
state for the Evidence Visibility / Candidate Patches submission path.

## Paper Package

- Current LaTeX draft:
  `docs/paper/ieee_submission_draft.tex`
- Current compiled PDF target:
  `outputs/paper_compile/ieee_submission_draft.pdf`
- Current paper title:
  `Evidence Visibility Matters: A Systematic Study of LLM-Based Verification for Candidate Patches`
- Current claim scope:
  bounded EVP-7 evidence-visibility pilot, single DeepSeek G5 verifier run,
  20 real-bug tasks, 94 patch candidates, and 376 evidence packets.
- Current workload presentation:
  the paper also reports the broader structural/no-API pipeline as tracked
  workload evidence: 21 tasks, 98 candidates, 392 E0/E2/E4/E6 evidence
  packets, 294 deterministic tool-only decisions, qualitative cases, and
  raw-output-free claim/audit artifacts.
- Advisor-facing workload response:
  `docs/paper/advisor_workload_response_zh.md` summarizes why the current work
  is a candidate-patch verification pipeline rather than only a prompt
  comparison, while preserving the bounded EVP-7 claim boundary.
- Submission freeze candidate:
  `docs/artifact/submission_freeze_candidate_20260618.md` records the current
  paper/artifact package as a candidate state only. It does not freeze the
  current 7-page IEEE PDF or approve any new experiment.
- Latest compiled PDF check:
  `outputs/paper_compile/ieee_submission_draft.pdf` was regenerated from the
  current IEEE draft on 2026-06-18. The PDF is 7 pages and contains the
  workload ledger plus the bounded EVP-7 conclusion.
- Known non-blocker:
  the old prompt-only evidence-first full-run gate remains
  `stop_or_redesign`. This blocks prompt-only positive claims, not the current
  bounded EVP-7 evidence-visibility claim.

## Required Paper Figures

- `docs/figures/fig1_framework.pdf`
- `docs/figures/fig2_evidence_visibility.pdf`
- `docs/figures/fig3_dataset_composition.pdf`
- `docs/figures/fig4_result_tradeoff.pdf`
- `docs/figures/fig5_claim_boundary.pdf`
- `docs/figures/fig6_evp7_visibility_curve.pdf`
- `docs/figures/fig7_decision_metric_flow.pdf`

## Claim-Boundary Evidence

- `docs/experiments/evp7_g5_376_full_quality_audit.md`
- `docs/experiments/evp7_g5_376_statistical_analysis.md`
- `docs/experiments/evp7_g5_376_utility_sensitivity.md`
- `docs/experiments/evp7_g5_376_tool_attribution.md`
- `docs/experiments/evp7_g5_376_qualitative_cases.md`
- `docs/experiments/evp7_g5_376_claim_traceability.md`
- `docs/artifact/submission_handoff_20260618.md`
- `docs/artifact/submission_freeze_candidate_20260618.md`

## Rebuild Commands

```powershell
python scripts\write_paper_tables.py
python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex
```

## Audit Commands

```powershell
python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md
python scripts\audit_paper_claim_boundary.py
python scripts\audit_submission_handoff.py --out-json outputs\submission_handoff_audit\latest.json --out-md outputs\submission_handoff_audit\latest.md
python scripts\audit_submission_freeze_candidate.py --out-json outputs\submission_freeze_candidate_audit\latest.json --out-md outputs\submission_freeze_candidate_audit\latest.md
python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md
```

## Anonymous Artifact Commands

```powershell
python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json
python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md
```

The `artifacts/` directory is intentionally ignored and must not be committed.

## Exclusion Boundary

The anonymous package must not contain:

- `.env` or `.env.*` other than `.env.example`;
- `configs/*.local.json`;
- `outputs/`, `data/`, `tmp/`, `runs/`, or `artifacts/`;
- raw model responses or prompt text;
- benchmark checkouts;
- private keys, PEM files, caches, or virtual environments.

## Ready-To-Submit Criteria

- IEEE draft regenerates from tracked tables and scripts.
- LaTeX compiles twice without undefined references.
- Paper readiness passes for current paper framing, reader flow, related work,
  final-polish wording, protocol state, and EVP-7 bounded claim readiness.
- Claim-boundary audit passes and remains raw-output-free.
- Anonymous artifact audit passes and includes this checklist plus all seven
  required paper figures.
- Local quality gate passes.

## Latest Local Verification

Last checked on 2026-06-18 after the no-API paper package rebuild that followed
the reinforcement-route clarification:

- paper tables regenerated from tracked summaries;
- all seven paper figures regenerated in PDF/SVG/PNG form;
- IEEE draft regenerated from the current table snippets;
- LaTeX compiled twice without unresolved references, producing a 7-page PDF;
- PDF text contains the structural workload ledger and bounded EVP-7
  conclusion, including the 21/98/392 structural pipeline and the 20/94/376
  paper-facing DeepSeek G5 run;
- claim-boundary audit passed and remained raw-output-free;
- paper readiness and local quality gate passed, including the no-API
  submission handoff and freeze-candidate boundaries;
- anonymous artifact ZIP rebuilt with 303 files and audit result was
  `safe: true`;
- artifact audit now requires `docs/paper/advisor_workload_response_zh.md`;
- artifact and paper readiness gates now require
  `docs/artifact/submission_freeze_candidate_20260618.md`;
- paper readiness and local quality now run
  `scripts/audit_submission_freeze_candidate.py`;
- tracked handoff packet:
  `docs/artifact/submission_handoff_20260618.md`.
