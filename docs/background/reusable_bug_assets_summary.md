# Reusable Bug Assets Summary

The clean workspace keeps executable oracles and supporting scripts, but not the
old raw output directories or long run logs.

## Retained Asset Types

- Minimal BugsInPy executable oracles under `scripts/oracles/`.
- Real-bug validation logic in `scripts/validate_real_bug_dataset.py`.
- Source-context construction logic in `scripts/build_real_bug_review_dataset.py`.
- Claim evidence tooling in `scripts/build_claim_evidence_packets.py`,
  `scripts/build_claim_labeling_batch.py`, and
  `scripts/claim_label_worksheet.py`.

## Intended New Use

| Old Concept | Patch-Verification Use |
| --- | --- |
| Buggy version | Incorrect or no-op candidate patch |
| Fixed version | Correct reference patch |
| Bug patch | Candidate patch text and localization |
| Regression oracle | Behavioral evidence for patch outcome |
| Fixed-control false positives | Motivation for evidence-backed acceptance |

## Excluded Material

- Old reviewer API outputs.
- Old generated-code benchmark results.
- Old paper drafts.
- Old active plans.
- Local benchmark checkouts and virtual environments.

Recover excluded material from the original workspace only if a specific
patch-verification experiment needs it.
