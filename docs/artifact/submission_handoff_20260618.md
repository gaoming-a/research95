# Submission Handoff: Four-Anchor EVP-7 Paper Package

Date: 2026-06-18

This handoff records the current no-API submission state. It does not authorize
new model calls, cohort expansion, or evidence-level changes.

## Current Paper State

- Paper route: current four-anchor EVP-7 paper package.
- Supported claim: bounded evidence-visibility pilot observations.
- Structural/no-API cohort: 21 tasks, 6 projects, 98 candidates, 392
  E0/E2/E4/E6 evidence packets.
- Paper-facing real DeepSeek G5 run: 20 tasks, 94 candidates, 376 records.
- Evidence levels: E0/E2/E4/E6 only. E1/E3/E5 are future EVP-8 /
  EVP-7-v2 work and must not be inserted into current artifacts.
- Known non-blocker: the old prompt-only evidence-first gate remains
  `stop_or_redesign`; this blocks prompt-only positive claims, not the current
  bounded EVP-7 claim.

## Latest No-API Maintenance Run

The following commands were rerun on 2026-06-18:

```powershell
python scripts\write_paper_tables.py
python scripts\write_ieee_latex_draft.py --tables-tex docs\paper\generated_tables.tex --out docs\paper\ieee_submission_draft.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\paper_compile docs\paper\ieee_submission_draft.tex
pdftotext outputs\paper_compile\ieee_submission_draft.pdf - | rg -n "Workload at a Glance|20 tasks|94 candidates|376 records|21 tasks|98 candidates|bounded EVP-7"
python scripts\audit_paper_claim_boundary.py
python scripts\audit_paper_readiness.py --out-json outputs\paper_readiness\latest.json --out-md outputs\paper_readiness\latest.md
python scripts\run_local_quality_gate.py --out-json outputs\local_quality_gate\latest.json --out-md outputs\local_quality_gate\latest.md
python scripts\prepare_anonymous_artifact.py --out artifacts\research95_anonymous_artifact.zip --manifest-out artifacts\research95_anonymous_artifact_manifest.json
python scripts\audit_anonymous_artifact.py --artifact artifacts\research95_anonymous_artifact.zip --out-json artifacts\research95_anonymous_artifact_audit.json --out-md artifacts\research95_anonymous_artifact_audit.md
```

Observed results:

- paper tables and IEEE draft regenerated without tracked drift;
- IEEE PDF compiled twice to 7 pages;
- PDF text contains the workload ledger and bounded EVP-7 conclusion;
- claim-boundary audit passed and remained raw-output-free;
- paper readiness passed for the current bounded EVP-7 claim, with the old
  prompt-only `stop_or_redesign` blocker retained as a non-blocker for this
  paper route;
- local quality gate passed;
- anonymous artifact package rebuilt with 303 files and `safe: true`;
- artifact audit requires the advisor workload response packet;
- the submission freeze-candidate packet records the current package as a
  candidate state only and does not finalize the 7-page IEEE PDF;
- `scripts/audit_submission_freeze_candidate.py` checks that candidate boundary
  before paper readiness and local quality report submission-package readiness.

## Next Decision Boundary

Use `docs/experiments/evp7_next_decision_packet_20260618.md` before any
experimental continuation.

Default if no explicit decision is given:

- continue only no-API paper-submission maintenance;
- regenerate tables/draft/PDF/artifact;
- rerun readiness and artifact audits;
- update handoff notes.

Forbidden without explicit user confirmation:

- no second-model API calls;
- no cohort expansion;
- no E1/E3/E5 insertion;
- no new verifier design run;
- no claim that the LLM beats deterministic tool-only baselines.

## Current Submission Files

- `docs/paper/ieee_submission_draft.tex`
- `outputs/paper_compile/ieee_submission_draft.pdf` ignored local build
- `docs/paper/patch_verification_draft.md`
- `docs/paper/advisor_workload_response_zh.md`
- `docs/paper/generated_tables.md`
- `docs/paper/generated_tables.tex`
- `docs/artifact/submission_checklist.md`
- `docs/artifact/anonymous_artifact.md`
- `docs/artifact/submission_freeze_candidate_20260618.md`
- `artifacts/research95_anonymous_artifact.zip` ignored local build
