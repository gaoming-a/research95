# EVP-8 Realistic Hard-Negative Third-Project Redesign Review v0.1

Date: 2026-06-30

This is a no-API source-design review. It does not read raw model outputs,
store prompt text, store patch text, or run verifier APIs.

## Current Gate

- candidates after thefuck supplement: `90`
- visible-pass/hidden-fail candidates: `26`
- visible-pass/hidden-fail projects: `PySnooper`, `cookiecutter`
- required gate: at least `30` visible-pass/hidden-fail candidates across at
  least `3` projects
- ready for verifier API: `false`

## Third-Project Attempts

| project | attempt | result |
| --- | --- | --- |
| `httpie` | Qwen and DeepSeek supplements | 0 hard negatives; hidden-failing candidates failed visible tests |
| `thefuck` | Qwen supplement 003 | 12 visible-pass/hidden-pass candidates; 0 hard negatives |
| `luigi` | Qwen supplement 002 | stopped before candidate construction on exact find-snippet failure |
| `youtube-dl` | Qwen supplement 004 | stopped before candidate construction on exact find-snippet failure |

## Diagnosis

The current fresh hard-negative gate is real but narrow. It provides 26 useful
visible-pass/hidden-fail cases across two projects, but it does not satisfy the
predeclared 30-candidate/3-project gate.

The third-project problem is not solved by simply adding more API calls under
the same setup. Simple third-project tasks can become correct-like because the
issue summary is clear enough for Qwen to fix the hidden oracle. More complex
tasks expose fragility in the exact search/replace edit-plan materialization
interface before candidates can be validated.

## Options

1. Downgrade the paper claim to a two-project fresh hard-negative cohort.
   This is the cleanest path without changing the protocol, but it weakens
   external validity.
2. Start a new generation-interface protocol.
   This may improve third-project yield, but it must be declared as a new
   protocol rather than silently merged into the same supplement series.
3. Use historical EVP-8-HARD cases only as calibration or appendix evidence.
   This is valid for failure-mode analysis but does not solve the fresh
   realistic third-project gate.

## Recommendation

Pause verifier API. Choose between a conservative two-project claim and a
separately frozen new generation-interface protocol before any further API
calls.
