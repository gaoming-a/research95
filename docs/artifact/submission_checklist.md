# Final Submission Checklist

Date: 2026-06-15

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
