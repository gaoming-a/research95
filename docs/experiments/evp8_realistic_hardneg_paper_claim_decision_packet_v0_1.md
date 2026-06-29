# EVP-8 Realistic Hard-Negative Paper Claim Decision Packet v0.1

Date: 2026-06-30

This is a no-API paper-claim decision packet. It reads tracked summaries only
and does not read raw model outputs, prompt text, or patch text.

## Current Evidence

- fresh generated candidates after full-file attempt: `94`
- visible-pass/hidden-fail cases: `26`
- projects with visible-pass/hidden-fail cases: `PySnooper`, `cookiecutter`
- predeclared gate: at least `30` cases across at least `3` projects
- gate passed: `false`
- ready for verifier API: `false`

Third-project attempts did not solve the gate:

| project / route | result |
| --- | --- |
| `httpie` | 0 hard negatives; hidden-failing patches failed visible tests |
| `thefuck` | 0 hard negatives; generated patches were correct-like |
| `luigi` | exact edit-plan materialization failed before candidates |
| `youtube-dl` exact edit-plan | exact edit-plan materialization failed before candidates |
| `youtube-dl` full-file | 0 hard negatives; generated patches were correct-like |

## Decision

Do not run more verifier API for this branch.

The current fresh realistic branch should be downgraded to a two-project
fresh hard-negative supplement or reported as a source-acquisition negative
result. It is not a verifier-ready three-project realistic main experiment.

## Supported Claims

1. The source-acquisition protocol produced a real visible-pass/hidden-fail
   opportunity set, but only across `PySnooper` and `cookiecutter`.
2. Third-project acquisition failed for distinct reasons: visible-failing wrong
   patches, correct-like generated patches, and edit materialization failure.
3. The full-file interface fixed youtube-dl materialization but not the
   opportunity-set problem.
4. Gate readiness must be reported separately from verifier metrics.

## Unsupported Claims

Do not claim:

- the fresh realistic branch is ready for Qwen/DeepSeek verifier evaluation;
- the current data supports a three-project realistic hard-negative verifier
  experiment;
- more API calls under the same targets are likely to produce a clean
  opportunity set;
- generation-interface repair validates the verifier system.

## Paper Integration

Keep the existing evidence-visibility SQJ route as the main paper path unless a
larger fresh realistic cohort is built.

Use this branch as:

- threats-to-validity evidence about source acquisition;
- a supplementary negative result on hard-negative gate construction;
- motivation for reporting generator success/failure and gate readiness
  separately from verifier metrics.

Suggested wording:

> Our fresh realistic agent-patch source acquisition produced 26 validated
> visible-pass/hidden-fail cases across two projects, but repeated third-project
> attempts either produced correct-like patches, visible-failing wrong patches,
> or failed candidate materialization. We therefore treat this branch as a
> source-acquisition and gate-readiness result rather than a verifier-ready main
> experiment.

## Next Action

Shortest clean path: freeze this branch as a two-project supplement/negative
result and update the paper plan accordingly.

Longer path: start a separate, pre-registered source-acquisition protocol with
different target tasks before any further API calls.

Forbidden next action: do not run verifier APIs while `ready_for_verifier_api`
is false.
