# Reusable Real-Bug Assets

This document records which old assets were intentionally carried into the clean
`research95` workspace.

## High-Value Assets

- Validated BugsInPy samples from `tqdm`, `black`, `httpie`, and `luigi`.
- Minimal executable oracles under `scripts/oracles/`.
- Patch-hunk source-context construction logic.
- Fixed/reference controls for measuring specificity.
- Claim-level evidence packet and worksheet workflow.
- False-positive and tool-gated analysis notes.

## How They Map to Patch Verification

| Old Asset | New Use |
| --- | --- |
| Buggy checkout | Incorrect or no-op patch baseline |
| Fixed checkout | Correct patch baseline |
| Bug patch | Candidate patch text and source context |
| Regression oracle | Ground truth evidence source |
| Fixed-control false positives | Motivation for not trusting LLM-only review |
| Claim-level labels | Evidence-support labels for patch-review claims |

## Assets Not Migrated

- Raw `outputs/` and local benchmark checkouts.
- Old IEEE draft files.
- Generated-code benchmark results that do not support patch verification.
- Local API/model config files.

These can be recovered from the original workspace if needed, but they should
not be treated as active evidence in this clean direction.
