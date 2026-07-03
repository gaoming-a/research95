# CCF-C Figure QA

Backend: Python / matplotlib only.

Generated figures:

- `ccfc_fig1_protocol`: schematic-led composite for the hidden-evaluator protocol.
- `ccfc_fig2_decision_patterns`: quantitative grid for repaired Qwen label-conditioned metrics and E6 ablations.
- `ccfc_fig3_claim_boundary`: asymmetric mixed-modality map for claim and validity boundaries.

Export contract:

- Formats: PDF, SVG, PNG.
- SVG text is configured with `svg.fonttype = none`.
- PDF text is configured with `pdf.fonttype = 42`.
- Source data: `figure_source_data.json`, derived from tracked aggregate claim-map JSON.
- Statistics: descriptive counts only; no new inferential test is introduced.

Review boundary:

- These figures support bounded evidence-conditioned risk-behavior claims after excluding the legacy v0.1 diagnostic setting from the main evidence chain.
- They do not support autonomous patch correctness verification, monotonic correctness improvement, or escalation-as-strict-correction claims.
