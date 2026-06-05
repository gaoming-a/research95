# Tool-Augmented Full Run Result

Date: 2026-06-05

## Run

- Provider: DeepSeek official API
- Model: `deepseek-v4-pro`
- Condition: `tool_augmented_evidence`
- Prompt version: `patch_verify_tool_augmented_evidence_v1`
- Candidates: 30
- Review records: 30
- Output directory: `outputs/patch_verification_tool_augmented_full_001`
- Completeness: passed
- Mock records: 0
- Invalid outputs: 0

## Boundary

This is a tool-assisted verification result. The verifier saw patch-apply
status and executable behavior summaries derived from retained validation
runs. It must not be reported as prompt-only model ability and does not reverse
the original `evidence_first` full-run verdict of `stop_or_redesign`.

The defensible claim is conditional:

> When executable evidence summaries are visible, the tool-augmented verifier
> can use them to make correct accept/reject decisions on this 30-candidate
> pilot.

## Metrics

| condition | false accept rate | accepted precision | correct recall | false reject rate | escalation rate | invalid output rate | records |
|---|---:|---:|---:|---:|---:|---:|---:|
| `llm_only` | 0.0909 | 0.7143 | 1.0000 | 0.0000 | 0.0667 | 0.1000 | 30 |
| `prompt_only_evidence_first` | 0.0000 | 1.0000 | 0.7143 | 0.1429 | 0.1333 | 0.0333 | 30 |
| `tool_augmented_evidence` | 0.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 30 |

The first two rows come from `outputs/patch_verification_api_pilot_002`; the
tool-augmented row comes from
`outputs/patch_verification_tool_augmented_full_001`.

## Gate Result

`tool_augmented_full_gate.json` passed:

- review count: 30;
- mock review count: 0;
- condition counts: `{"tool_augmented_evidence": 30}`;
- false accept rate: 0.0;
- correct-patch recall: 1.0;
- invalid-output rate: 0.0.

## Interpretation

The result supports the redesigned paper direction:

1. LLM-only review is unsafe as a merge gate because it accepted partial fixes.
2. Prompt-only evidence-first review reduced false accepts but lost too much
   recall.
3. Tool-augmented evidence restored recall while preserving zero observed false
   accepts on this pilot.

This is a stronger and more realistic direction than claiming prompt-only
review is sufficient. The result is still limited by dataset size, one model,
and the fact that retained oracle summaries are strong evidence.

## Next Step

The paper should now present a three-condition story:

- `llm_only`: plausibility-driven baseline;
- prompt-only `evidence_first`: conservative but evidence-poor;
- `tool_augmented_evidence`: conditional verifier with executable evidence.

Before making stronger claims, add clearer wording on whether oracle summaries
represent realistic engineering evidence, upper-bound evidence, or a tool
workflow.
