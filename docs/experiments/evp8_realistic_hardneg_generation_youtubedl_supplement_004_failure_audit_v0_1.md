# EVP-8 Realistic Hard-Negative youtube-dl Supplement 004 Failure Audit v0.1

Date: 2026-06-30

This is a raw-output-free failure audit for the Qwen youtube-dl supplement.
It does not store prompt text, patch text, raw response content, or verifier
outputs.

## Summary

- run id: `evp8_realistic_hardneg_generation_qwen_supplement_004`
- model: `qwen3.7-max`
- provider: `qwen_official`
- task: `bugsinpy_youtube-dl_7`
- failed variant: `43`
- failure point: `apply_edit_plan_before_candidate_construction`
- error class: `edit_plan_apply_failure`
- error: `find snippet not found in youtube_dl/utils.py`

## Boundary

- generation API was attempted for this supplement only.
- verifier API was not attempted.
- raw model output content was not read into this tracked audit.
- no generated candidate, relabeled candidate, or visible-test outcome was
  produced for this supplement.

## Decision

Do not continue blind API retries for youtube-dl under the current exact
search/replace edit-plan interface. The next step is a source-design or
generation-interface review before any further third-project supplement attempt.
