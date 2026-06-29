# SQJ Final-Freeze Readiness Packet

Status: SQJ final-freeze readiness packet, not final freeze.
Date: 2026-06-30

This packet records what is ready for a future Software Quality Journal (SQJ)
submission freeze and what still blocks submission. This packet does not authorize submission.
No model API calls are authorized.

## Current Ready Source Package

The current SQJ route has these tracked, regenerable source-package components:

- Main source draft: `docs/paper/sqj_submission_draft.tex`
- Bibliography: `docs/paper/sqj_references.bib`
- SQJ framing and claim boundary: `docs/paper/sqj_submission_framing.md`
- Generated tables: `docs/paper/generated_tables.md` and
  `docs/paper/generated_tables.tex`
- SQJ figure directory: `docs/figures/sqj/`
- SQJ source-package checklist: `docs/artifact/sqj_submission_checklist.md`
- SQJ human-decision packet: `docs/artifact/sqj_human_decision_packet.md`
- SQJ checklist audit: `scripts/audit_sqj_submission_checklist.py`
- SQJ artifact candidate gate audit: `scripts/audit_sqj_artifact_gate.py`
- SQJ final-authorization gate audit: `scripts/audit_sqj_final_authorization_gate.py`
- SQJ school-recognition gate audit: `scripts/audit_sqj_school_recognition_gate.py`
- SQJ human-input gate audit: `scripts/audit_sqj_human_inputs_gate.py`
- SQJ human-decision packet audit: `scripts/audit_sqj_human_decision_packet.py`
- SQJ PDF compile gate audit: `scripts/audit_sqj_pdf_compile_gate.py`
- SQJ figure-layout gate audit: `scripts/audit_sqj_figure_layout_gate.py`

The manuscript-facing SQJ figure set is:

- `docs/figures/sqj/sqj_fig1_evp8_protocol.pdf`
- `docs/figures/sqj/sqj_fig2_decision_patterns.pdf`
- `docs/figures/sqj/sqj_fig3_cost_boundary.pdf`

## Supported Claim Boundary

- Evidence visibility is a first-order experimental variable for LLM-based
  patch verification.
- The frozen EVP-8 v0.1 packet set supports descriptive five-model per-level
  decision-pattern reporting.
- The observed response is model-dependent and non-monotonic.
- The Kimi blocked attempts are cost/execution-risk evidence only, not valid
  model-result records.
- The fresh realistic branch is a two-project source-acquisition negative result,
  not a verifier-ready main experiment.
- API execution remains frozen after the EVP-8 cost overrun.

## Still Blocking Final Freeze

Final freeze is blocked until all of the following are resolved:

- school/department recognition confirmation for SQJ under the publication-year
  rules and warning-list policy;
- current school-recognition gate status `blocked_missing_school_recognition`
  until school/department confirmation is provided;
- local or CI PDF compilation after `sn-jnl.cls` is available;
- current local PDF compile gate status `blocked_missing_sn_jnl_cls` until the
  official Springer Nature class is installed;
- final SQJ-specific figure placement and caption audit after PDF compilation;
- current figure-layout gate status `blocked_pending_pdf_compile` until PDF
  compilation enables post-compile layout review;
- author information, funding, acknowledgements, and competing-interest
  confirmation;
- current human-input gate status `blocked_missing_human_inputs` until author,
  affiliation, funding, competing-interest, acknowledgement, and contribution
  statements are provided or confirmed;
- SQJ human-decision packet records all external human decisions still required
  before final freeze;
- current human-decision packet gate status
  `blocked_missing_human_decisions` until those decisions are resolved;
- final artifact package rebuild and audit;
- current artifact candidate gate status `candidate_artifact_dry_run_ready`;
  this is not a final artifact ZIP rebuild;
- final user authorization to submit.
- current final-authorization gate status `blocked_missing_final_authorization`
  until the user explicitly authorizes SQJ final submission.

## Forbidden Until Those Gates Pass

Do not claim:

- that school recognition is guaranteed;
- that Open Access or APC payment is approved;
- that the PDF compile gate has passed;
- that this packet is a final submission freeze;
- that LLM superiority over deterministic baselines is supported;
- that a final evidence-level ranking has been established;
- that the fresh realistic branch is a three-project verifier-ready main
  experiment;
- that the full-file generation repair demonstrates practical autonomous patch
  verification;
- that new model API calls can run without a new explicit budget and command.

## Safe Rebuild Order

Run these commands in order. Do not parallelize the figure generation and figure
audits because audits can otherwise inspect files while matplotlib is still
writing them.

```powershell
python scripts\write_paper_tables.py
python scripts\generate_sqj_figures.py
python scripts\write_sqj_latex_draft.py --check
python scripts\audit_sqj_submission_checklist.py --out-json outputs\sqj_submission_checklist_audit\latest.json --out-md outputs\sqj_submission_checklist_audit\latest.md
python scripts\audit_sqj_artifact_gate.py --out-json outputs\sqj_artifact_gate\latest.json --out-md outputs\sqj_artifact_gate\latest.md
python scripts\audit_sqj_final_authorization_gate.py --out-json outputs\sqj_final_authorization_gate\latest.json --out-md outputs\sqj_final_authorization_gate\latest.md
python scripts\audit_sqj_school_recognition_gate.py --out-json outputs\sqj_school_recognition_gate\latest.json --out-md outputs\sqj_school_recognition_gate\latest.md
python scripts\audit_sqj_human_inputs_gate.py --out-json outputs\sqj_human_inputs_gate\latest.json --out-md outputs\sqj_human_inputs_gate\latest.md
python scripts\audit_sqj_human_decision_packet.py --out-json outputs\sqj_human_decision_packet\latest.json --out-md outputs\sqj_human_decision_packet\latest.md
python scripts\audit_sqj_pdf_compile_gate.py --out-json outputs\sqj_pdf_compile_gate\latest.json --out-md outputs\sqj_pdf_compile_gate\latest.md
python scripts\audit_sqj_figure_layout_gate.py --out-json outputs\sqj_figure_layout_gate\latest.json --out-md outputs\sqj_figure_layout_gate\latest.md
python scripts\audit_sqj_final_freeze_readiness.py --out-json outputs\sqj_final_freeze_readiness\latest.json --out-md outputs\sqj_final_freeze_readiness\latest.md
python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md
python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md
```

## Next Human Decisions

1. Confirm whether SQJ is recognized by the school/department as D class or
   above for the relevant publication year.
2. Confirm author names, affiliations, funding, acknowledgements, competing
   interests, and data/code availability wording.
3. Provide or install the official Springer Nature `sn-jnl` template/class so
   the PDF compile gate can be added.
4. Decide whether to freeze and rebuild the anonymous artifact package after
   the compiled PDF layout has passed.

## Boundary

This is a readiness and blocker packet only. It keeps the SQJ route executable
without treating the current source package as submitted, accepted, recognized,
or final-frozen.
