# Paper Figures

This directory contains reproducible publication figures for the
patch-verification paper.

Generate all figures with:

```powershell
python scripts\generate_paper_figures.py
```

Each figure is emitted as PDF, SVG, and PNG:

- `fig1_framework`: patch-verification workflow.
- `fig2_evidence_visibility`: compact EVP-7 evidence boundary across
  E0/E2/E4/E6 visibility levels, with evaluator truth labels shown as hidden
  across all levels.
- `fig3_dataset_composition`: pilot dataset and executable validation.
- `fig4_result_tradeoff`: first-pilot safety/recall tradeoff result.
- `fig5_claim_boundary`: supported claim boundary.
- `fig6_evp7_visibility_curve`: EVP-7 evidence visibility curve over E0/E2/E4/E6.
- `fig7_decision_metric_flow`: flow from evidence-level LLM decisions to
  hidden-label metric computation.

The IEEE submission draft references the PDF versions. Under the SQJ route,
these remain historical/reproducible EVP-7 assets rather than the main
manuscript-facing figure set.

## SQJ Figures

Generate the SQJ-specific EVP-8 figure set with:

```powershell
python scripts\generate_sqj_figures.py
```

The SQJ figures are emitted under `docs/figures/sqj/` in PDF, SVG, and PNG:

- `sqj_fig1_evp8_protocol`: EVP-8 hidden-evaluator protocol and scale overview.
- `sqj_fig2_decision_patterns`: five-model per-level rejection/escalation
  patterns.
- `sqj_fig3_cost_boundary`: valid-result cost versus blocked-attempt cost
  boundary.

The SQJ source draft references these PDF versions.

## Raster Visual Candidates

The `imagegen/` subdirectory contains four generated PNG candidates and their
exact prompts. These assets are for graphical abstracts, presentations, and
visual drafts only. Use the reproducible PDF/SVG/PNG figures above for exact
experimental claims and numeric paper evidence.
