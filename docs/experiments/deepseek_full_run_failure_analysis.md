# DeepSeek Full Run Failure Analysis

Date: 2026-06-05

## Scope

This note analyzes the qualitative failures from
`outputs/patch_verification_api_pilot_002`. The run used DeepSeek official API
with `deepseek-v4-pro`, 30 candidates, and two conditions: `llm_only` and
`evidence_first`.

The run is usable as a mixed/negative pilot result because it has 60 non-mock
records, passed run completeness, and has no `run_error.json`. It is not usable
for a positive claim because the gate verdict is `stop_or_redesign`.

## Main Failure Buckets

From `failure_examples.json`:

| bucket | count | interpretation |
|---|---:|---|
| `llm_only_false_accepts` | 2 | LLM-only accepted partial fixes. |
| `false_accepts` | 2 | Same two partial fixes were wrongly accepted. |
| `correct_patch_not_accepted` | 2 | Evidence-first did not accept two reference fixes. |
| `false_rejects` | 1 | Evidence-first rejected one correct reference fix. |
| `evidence_first_reject_or_escalate` | 24 | Evidence-first was broadly conservative. |
| `invalid_outputs` | 4 | DeepSeek sometimes exhausted 4096 completion tokens in reasoning and returned no parseable final JSON. |

## Critical Examples

### LLM-only false accepts

Both false accepts come from `bugsinpy_httpie_1`:

- `candidate_0005`, `bugsinpy_httpie_1__missing_change_1`;
- `candidate_0006`, `bugsinpy_httpie_1__missing_change_2`.

Both are partial fixes. `llm_only` accepted them because the visible diff looked
plausibly aligned with filename collision handling. In raw response terms, the
model reasoned from intent and surface plausibility: trimming a filename before
adding a suffix appears to address collision-related failure.

The weakness is that `llm_only` did not have a grounded mechanism to notice
that a required companion change was missing. This supports the original
motivation that patch-shaped plausibility is not enough for merge decisions.

### Evidence-first correct patches not accepted

Evidence-first failed on two correct reference fixes:

- `candidate_0001`, `bugsinpy_httpie_1__reference_fix`: decision `escalate`;
- `candidate_0023`, `bugsinpy_luigi_3__reference_fix`: decision `reject`.

For `candidate_0001`, evidence-first saw a patch that added filename-length
handling. The visible task summary said only that filename collision handling
should create a unique filename. Because the evidence packet did not include the
actual test body, failing behavior, or oracle output, the model treated the
length-handling change as possibly out of scope and escalated.

For `candidate_0023`, evidence-first made a stronger semantic judgment and
rejected the patch. It inferred from the diff that the JSON success path still
converts scalar elements incorrectly. The executable oracle says the reference
fix is correct, so this is a real model-verifier error under the current prompt
boundary.

### Invalid outputs

The invalid outputs are not dataset labels. They are execution reliability
failures:

- `llm_only` invalid outputs: `candidate_0001`, `candidate_0017`,
  `candidate_0020`;
- `evidence_first` invalid output: `candidate_0020`.

The common pattern is token exhaustion: `finish_reason=length`, most or all
completion tokens spent in reasoning, and no parseable final JSON object. The
4096-token setting fixed the smoke run but did not eliminate this failure mode
in the full run.

## Root Cause Assessment

The current result is not best explained as "evidence-first is worse" in
general. It is more precise to say:

> This implementation of evidence-first is too evidence-poor. It asks the model
> to make evidence-constrained decisions, but the visible evidence packet gives
> mostly patch text, task summary, and test names rather than executable
> behavior, test bodies, oracle output, or claim-specific traces.

This creates a predictable tradeoff:

- `llm_only` is willing to infer from plausible code changes, which preserves
  recall but accepts some partial fixes.
- `evidence_first` refuses unsupported accept decisions, which removes observed
  false accepts but loses correct-patch recall when the visible packet cannot
  prove why a reference fix is necessary and sufficient.

The result therefore supports a safety/utility tradeoff finding, not the
stronger claim that evidence-first verification is ready as a merge gate.

## Decision For Next Stage

Do not run a larger API experiment with the same `patch_verify_evidence_first_v1`
condition. Scaling this prompt would mainly scale a known failure mode.

The next minimal experiment should be a redesign smoke on the failure cases
only:

1. Add a new condition, tentatively `evidence_with_oracle_summary_v1`.
2. Keep hidden labels out of the prompt, but include model-visible evidence
   that a real reviewer would reasonably use:
   - relevant test body or assertion summary;
   - pre-patch failure mode;
   - post-patch oracle/test status, if the condition is explicitly framed as a
     tool-augmented verifier;
   - claim-to-evidence checklist for touched behavior.
3. Run only the critical examples first: `candidate_0001`, `candidate_0005`,
   `candidate_0006`, `candidate_0023`, and `candidate_0020`.
4. Continue only if the redesigned condition preserves the false-accept
   reduction while accepting the two reference fixes or escalating rather than
   rejecting them.

If this redesign cannot fix the recall loss on the failure examples, the paper
should pivot to a negative/methods contribution about the limits of prompt-only
merge gates and the need for executable evidence.
