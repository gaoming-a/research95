# API Pilot Prompt Specifications

Last updated: 2026-06-05

These prompts are for the first small API pilot after the no-API dataset gate.
They must be used only with model-visible evidence packets. Evaluator-facing
fields such as `patch_id`, `candidate_type`, `expected_outcome`,
`patch_materialization`, `hidden_oracles`, oracle paths, oracle results, and
construction notes must not be included.

## Output Schema

All reviewer prompts must request one JSON object:

```json
{
  "decision": "accept",
  "confidence": 0.0,
  "claims": [
    {
      "claim": "The patch changes behavior X.",
      "evidence": ["specific patch line or visible context item"],
      "evidence_status": "supported"
    }
  ],
  "rationale": "short explanation",
  "uncertainty": "short explanation or none"
}
```

Allowed `decision` values:

- `accept`
- `reject`
- `escalate`

Allowed `evidence_status` values:

- `supported`
- `contradicted`
- `insufficient`

## Prompt: `patch_verify_llm_only_v1`

Purpose: measure unsupported patch acceptance/rejection from task context and
patch text only.

Template:

```text
You are reviewing a proposed software patch.

Decide whether the patch should be accepted, rejected, or escalated for human/tool verification.

Use only the task context and patch text below. Do not assume hidden tests or oracle results.
Return exactly one JSON object matching the required schema.

Decision policy:
- Accept only if the patch clearly addresses the task behavior and no visible contradiction exists.
- Reject if the patch is empty, unrelated, internally inconsistent, or visibly fails to address the behavior.
- Escalate if the patch may be plausible but the visible evidence is insufficient.

Task:
{task_summary}

Visible context:
{visible_context}

Candidate patch:
{patch_text}
```

## Prompt: `patch_verify_evidence_first_v1`

Purpose: test whether an evidence-constrained reviewer reduces unsupported
acceptance by requiring explicit evidence before accepting.

Template:

```text
You are performing evidence-first verification of a proposed software patch.

Decide whether the patch should be accepted, rejected, or escalated for human/tool verification.

You must tie every accept/reject decision to concrete visible evidence. Do not assume hidden labels, hidden tests, or oracle results. Return exactly one JSON object matching the required schema.

Decision policy:
- Accept only if the patch's correctness claim is directly supported by the visible patch diff and task context.
- Reject if the patch is empty, unrelated, internally inconsistent, or contradicts the required behavior.
- Escalate if visible evidence is insufficient to verify the correctness claim.

Task:
{task_summary}

Visible context:
{visible_context}

Candidate patch:
{patch_text}

Available evidence sources:
{available_evidence_sources}

Visible tests or behavioral hints:
{visible_tests}
```

## Label-Leakage Check

Before any run, confirm the rendered prompt does not contain:

- evaluator `patch_id`;
- `candidate_type`;
- `expected_outcome`;
- `patch_materialization`;
- hidden oracle path;
- oracle pass/fail result;
- construction notes.

## Expected Impact

The first API pilot should not claim evidence-first is proven better. It should
test whether the prompt boundary and output schema can produce measurable
differences in false accept rate, accepted precision, correct-patch recall,
escalation rate, and invalid-output rate on the validated 30-candidate pilot.

## Dry-Run Status

Completed on 2026-06-05 without API calls:

- candidates: 30;
- conditions: `llm_only` and `evidence_first`;
- rendered prompt records: 60;
- label-leakage check: 60/60 passed;
- prompt length range: 1074 to 2794 characters.
- config-driven dry-run works via `scripts/run_patch_verification_api_pilot.py
  --config configs/api_pilot.example.json --dry-run`.

The dry-run validates prompt rendering and prompt-boundary checks only. It does
not produce reviewer decisions.
