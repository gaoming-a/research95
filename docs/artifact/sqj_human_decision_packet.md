# SQJ Human Decision Packet

Status: SQJ human-decision packet, not final freeze.
Date: 2026-06-30

This packet lists the human decisions and external inputs still required before
the Software Quality Journal (SQJ) package can be treated as a final submission
freeze. It does not authorize submission, model API calls, PDF compilation, or
artifact release.

## Required Human Decisions

| id | current status | required human input | cannot be inferred by automation |
|---|---|---|---|
| `school_recognition` | `blocked_missing_school_recognition` | Confirm whether SQJ is recognized by the school/department for the relevant publication year and warning-list policy. | yes |
| `author_identity` | `blocked_missing_human_inputs` | Provide final author names, affiliations, corresponding author, and contact email. | yes |
| `funding_acknowledgements` | `blocked_missing_human_inputs` | Provide funding statement and acknowledgements, or explicitly confirm that none apply. | yes |
| `competing_interests` | `blocked_missing_human_inputs` | Confirm the competing-interest statement that should appear in the submission. | yes |
| `author_contributions` | `blocked_missing_human_inputs` | Provide author contribution statements matching the final author list. | yes |
| `springer_template` | `blocked_missing_sn_jnl_cls` | Provide or install the official Springer Nature `sn-jnl.cls` template/class so PDF compilation can run. | yes |
| `post_compile_layout_review` | `blocked_pending_pdf_compile` | Review figure placement, captions, references, and PDF layout after successful compilation. | yes |
| `final_artifact_rebuild` | `candidate_artifact_dry_run_ready` | Decide whether to rebuild and audit the final anonymous artifact ZIP after PDF layout passes. | yes |
| `final_submission_authorization` | `blocked_missing_final_authorization` | Explicitly authorize final SQJ submission after all other blockers are resolved. | yes |

## Current Non-Authorization Boundary

- Submission authorized: `false`.
- Human decisions complete: `false`.
- Final freeze complete: `false`.
- PDF compile passed: `false`.
- Model API calls authorized by this packet: `false`.
- Artifact release authorized by this packet: `false`.

## Safe Order

1. Confirm SQJ school/department recognition.
2. Provide final author, affiliation, funding, acknowledgement, competing
   interest, contribution, data-availability, and code-availability wording.
3. Provide or install the official Springer Nature `sn-jnl` template/class.
4. Compile the SQJ PDF and review figure placement/captions after compilation.
5. Rebuild and audit the final anonymous artifact package only after the PDF
   layout is accepted.
6. Explicitly authorize final SQJ submission.

## Forbidden Until Complete

- Do not claim that SQJ recognition is confirmed.
- Do not claim that the PDF compile gate has passed.
- Do not claim that human inputs are complete.
- Do not claim that the final artifact ZIP has been rebuilt.
- Do not claim that final submission has been authorized.
- Do not claim that the package is ready-to-submit or final freeze complete.
- Do not use broad API authorization as submission authorization.

## Audit Command

```powershell
python scripts\audit_sqj_human_decision_packet.py --out-json outputs\sqj_human_decision_packet\latest.json --out-md outputs\sqj_human_decision_packet\latest.md
```
