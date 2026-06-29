# EVP-8 Realistic Hard-Negative Full-File Outcome Review v0.1

Date: 2026-06-30

This is a no-API outcome review. It reads tracked audits only and does not read
raw model outputs, prompt text, or patch text.

## Full-File Result

- candidates: `4`
- patch applied: `4`
- hidden oracle passed: `4`
- visible test passed: `4`
- visible-pass/hidden-fail: `0`
- visible-pass/hidden-pass: `4`

The full-file interface solved the earlier exact edit-plan materialization
failure, but it did not produce third-project hard negatives.

## Combined Gate

- total candidates: `94`
- visible-pass/hidden-fail: `26`
- projects with visible-pass/hidden-fail: `PySnooper`, `cookiecutter`
- required: at least `30` candidates across at least `3` projects
- gate passed: `false`
- ready for verifier API: `false`

## Interpretation

The current evidence supports a two-project fresh hard-negative cohort plus
documented source-acquisition failures. It does not support a verifier-ready
three-project realistic cohort.

## Recommendation

Do not run verifier API. Decide whether to downgrade the paper claim to a
two-project fresh hard-negative study or start a new source-acquisition
protocol with different target tasks.
