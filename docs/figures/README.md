# Paper Figures

This directory contains reproducible publication figures for the
patch-verification paper.

Generate all figures with:

```powershell
python scripts\generate_paper_figures.py
```

Each figure is emitted as PDF, SVG, and PNG:

- `fig1_framework`: patch-verification workflow.
- `fig2_evidence_visibility`: evidence boundary across review conditions.
- `fig3_dataset_composition`: pilot dataset and executable validation.
- `fig4_result_tradeoff`: main safety/recall tradeoff result.
- `fig5_claim_boundary`: supported claim boundary.

The IEEE submission draft references the PDF versions.

## Raster Visual Candidates

The `imagegen/` subdirectory contains four generated PNG candidates and their
exact prompts. These assets are for graphical abstracts, presentations, and
visual drafts only. Use the reproducible PDF/SVG/PNG figures above for exact
experimental claims and numeric paper evidence.
