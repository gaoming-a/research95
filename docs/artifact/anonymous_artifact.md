# Anonymous Artifact Plan

This artifact package is intended for supplemental review material after the
paper direction stabilizes.

## Package Command

```powershell
python scripts\prepare_anonymous_artifact.py `
  --out artifacts\research95_anonymous_artifact.zip `
  --manifest-out artifacts\research95_anonymous_artifact_manifest.json
python scripts\audit_anonymous_artifact.py `
  --artifact artifacts\research95_anonymous_artifact.zip `
  --out-json artifacts\research95_anonymous_artifact_audit.json `
  --out-md artifacts\research95_anonymous_artifact_audit.md
```

## Included

- `README.md`, `pyproject.toml`, `.env.example`, and `.gitignore`.
- `src/` reusable utilities.
- `scripts/` dataset, validation, API, reporting, gate, readiness, and artifact
  scripts, including the API run completeness audit required before paper
  claims.
- `configs/` example configuration files only.
- `docs/` plans, schemas, metrics, prompt records, the current
  Evidence Visibility / Candidate Patches paper framing, reports,
  raw-output-free statistical, utility-sensitivity, and claim-boundary
  summaries, the active EVP-7 protocol, the final submission checklist, and
  reproducible paper figures.
- `examples/` small static examples.

## Excluded

- `.env`, API keys, local configs, key files, and PEM files.
- `outputs/`, `data/`, `tmp/`, `runs/`, `artifacts/`, and benchmark checkouts.
- Raw API responses and model-provider metadata that may contain private run
  details.
- Python caches, virtual environments, and local editor files.

## Current Boundary

The current artifact supports no-API reproduction, API-run preparation, and
tracked raw-output-free summaries of completed real API runs. It does not
contain raw model responses, ignored run directories, local configs, or
provider-private metadata.

## Current Audit

The latest ZIP audit passed on 2026-06-18 after the paper workload-ledger
refresh. It confirms:

- required source, config template, documentation, and handoff scripts are
  present;
- the final submission checklist is present at
  `docs/artifact/submission_checklist.md`;
- the no-API submission handoff is present at
  `docs/artifact/submission_handoff_20260618.md`;
- required protocol and paper-framing files are present:
  `docs/plans/final_paper_roadmap_zh.md`,
  `docs/protocol/evidence_visibility_protocol.md`,
  `docs/experiments/evp7_protocol_pilot.md`,
  `docs/paper/research_definition.md`, and
  `docs/paper/patch_verification_outline.md`;
- all seven paper-facing PDF figures are present, including
  `docs/figures/fig7_decision_metric_flow.pdf`;
- the current paper materials include the workload-at-a-glance ledger that
  separates the 21-task / 98-candidate / 392-packet structural pipeline from
  the 20-task / 94-candidate / 376-record real DeepSeek G5 run;
- embedded `ARTIFACT_README.md` includes no-API reproduction, local quality,
  credential-boundary, bootstrap-safety, command-template, pre-API handoff, and
  guarded real-API command templates, including full-run completeness
  postprocessing and the current no-API submission handoff entry;
- `outputs/`, `data/`, `tmp/`, `artifacts/`, real `.env`, and
  `configs/*.local.json` are absent;
- the embedded `ARTIFACT_MANIFEST.json` matches the packaged file list.
