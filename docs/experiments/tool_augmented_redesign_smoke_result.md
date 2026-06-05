# Tool-Augmented Redesign Smoke Result

Date: 2026-06-05

## Run

- Provider: DeepSeek official API
- Model: `deepseek-v4-pro`
- Condition: `tool_augmented_evidence`
- Prompt version: `patch_verify_tool_augmented_evidence_v1`
- Candidates: 5 failure-case candidates from the first DeepSeek full run
- Review records: 5
- Output directory: `outputs/patch_verification_redesign_smoke_001`
- Completeness: passed
- Mock records: 0
- Invalid outputs: 0

## Boundary

This is not a replacement for the original `llm_only` versus
`evidence_first` full run. It is a failure-case-only redesign smoke.

The condition is tool-augmented: the verifier sees patch-apply status and
retained oracle execution summaries. Therefore, this result must be reported
separately from prompt-only review and cannot be used to claim that
`patch_verify_evidence_first_v1` succeeded.

## Decisions

| candidate | expected smoke behavior | decision |
|---|---|---|
| `candidate_0001` | accept reference fix | `accept` |
| `candidate_0005` | do not accept partial fix | `reject` |
| `candidate_0006` | do not accept partial fix | `reject` |
| `candidate_0020` | do not accept partial fix | `reject` |
| `candidate_0023` | accept reference fix | `accept` |

Smoke gate result: passed.

## Metrics

| metric | value |
|---|---:|
| accepted precision | 1.0000 |
| correct-patch recall | 1.0000 |
| false accept rate | 0.0000 |
| false reject rate | 0.0000 |
| escalation rate | 0.0000 |
| invalid output rate | 0.0000 |

## Interpretation

The result supports a narrow diagnostic claim:

> The first evidence-first failure was plausibly caused by evidence poverty.
> When the verifier sees explicit tool execution summaries on the known failure
> cases, the same model makes the expected accept/reject decisions.

This justified the larger tool-augmented experiment. It does not rescue the
original prompt-only positive claim.

## Next Step

The next experiment has now been run as
`outputs/patch_verification_tool_augmented_full_001`. The analysis should
compare:

- original `llm_only`;
- original prompt-only `evidence_first`;
- new tool-augmented verifier.

The paper claim must remain conditional: tool-visible execution evidence may
improve the safety/recall tradeoff relative to prompt-only review.
