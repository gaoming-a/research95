# DeepSeek Full API Run Result

Date: 2026-06-05

## Run

- Provider: DeepSeek official API
- Model: `deepseek-v4-pro`
- Conditions: `llm_only`, `evidence_first`
- Candidates: 30
- Review records: 60
- Output directory: `outputs/patch_verification_api_pilot_002`
- Completeness: passed
- Mock records: 0
- Run error: absent
- Raw responses: 60, all present, all valid JSON, all hashes matched

## Gate Verdict

The stop/continue gate returned `stop_or_redesign`.

Reason: `evidence_first` did not pass all configured gates. It reduced false
accepts and improved accepted precision, but correct-patch recall dropped more
than the configured tolerance.

## Main Metrics

| condition | false accept rate | accepted precision | correct recall | acceptance rate | escalation rate | invalid output rate |
|---|---:|---:|---:|---:|---:|---:|
| `llm_only` | 0.0909 | 0.7143 | 1.0000 | 0.2333 | 0.0667 | 0.1000 |
| `evidence_first` | 0.0000 | 1.0000 | 0.7143 | 0.1667 | 0.1333 | 0.0333 |

Delta, evidence-first minus llm-only:

- False accept rate: -0.0909
- Accepted precision: +0.2857
- Correct-patch recall: -0.2857

## Interpretation

This result is not a positive result for the current paper claim. It supports a
more cautious statement:

> In this single-model pilot, evidence-first prompting removed observed false
> accepts and improved accepted precision, but it also rejected or escalated
> more correct patches than allowed by the pre-registered gate.

The current evidence is therefore best treated as a mixed/negative result and a
prompt/protocol redesign signal, not as evidence that evidence-first review is
ready as a merge gate.

## Failure Pattern

Failure buckets from `failure_examples.json`:

- `llm_only_false_accepts`: 2
- `false_accepts`: 2
- `correct_patch_not_accepted`: 2
- `false_rejects`: 1
- `evidence_first_reject_or_escalate`: 24
- `invalid_outputs`: 4

The important qualitative pattern is that `llm_only` accepted two partial fixes
that `evidence_first` did not accept, but `evidence_first` also failed to accept
two correct reference patches. This is the exact safety/utility tradeoff that
the full paper must report.

## Consequence For The Plan

- Do not write a positive claim.
- Keep the paper at a methods plus mixed/negative-result boundary.
- Next experimental step should inspect failure examples and redesign the
  evidence-first condition before any larger run.
- If continuing this direction, add stronger visible evidence or tool outputs
  so evidence-first does not have to infer correctness from patch text alone.
