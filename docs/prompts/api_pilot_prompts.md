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

## Prompt: `patch_verify_tool_augmented_evidence_v1`

Purpose: test whether the specific failure cases from the first DeepSeek full
run are caused by evidence poverty rather than only model capability. This is a
tool-augmented condition, not a prompt-only condition.

Template:

```text
You are performing tool-augmented verification of a proposed software patch.

Decide whether the patch should be accepted, rejected, or escalated for human/tool verification.

You may use only the visible task context, candidate patch, patch-apply status, and tool/oracle execution summary below. Do not assume hidden labels or evaluator annotations.
Return exactly one JSON object with fields: decision, confidence, claims, rationale, uncertainty.

Decision policy:
- Accept if the patch applies, relevant tool/oracle evidence supports the behavior, and no visible contradiction remains.
- Reject if the patch does not apply, tool/oracle evidence contradicts the behavior, the patch is unrelated, or required behavior is visibly missing.
- Escalate if tool evidence is incomplete, ambiguous, or insufficient to decide.

Task:
{task_summary}

Visible context:
{visible_context}

Candidate patch:
{patch_text}

Tool evidence:
{tool_evidence_summary}

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

## Redesign Smoke Boundary

After the first DeepSeek full run, `patch_verify_evidence_first_v1` should not
be scaled as-is. The next smoke test uses
`patch_verify_tool_augmented_evidence_v1` only on known failure cases and must
be reported as a separate tool-augmented condition.

## EVP-7 G5 Prompt: `patch_verify_evidence_visibility_merge_gate_v1`

Purpose: test evidence-visibility effects over the frozen EVP-7 protocol
packets using the fixed merge-gate schema from
`docs/protocol/evidence_visibility_protocol.md`.

Relationship to earlier prompts:

- It does not replace `patch_verify_evidence_first_v1`.
- It does not reuse the retained-oracle summary boundary from
  `patch_verify_tool_augmented_evidence_v1`.
- It is the first EVP-7 prompt designed for E0/E2/E4/E6 evidence-level
  ablation.

Template:

```text
You are a software merge-gate verifier for candidate patches.

Use only the visible evidence packet below. Do not infer hidden labels, hidden tests, oracle outcomes, reference-patch provenance, or evaluator notes.
Decide whether the candidate patch should be accepted, rejected, or escalated for human or tool review.

Return exactly one JSON object with this schema:
{
  "decision": "accept | reject | escalate",
  "confidence": 0.0,
  "primary_reason": "one concise reason grounded in visible evidence",
  "evidence_used": ["names of visible evidence fields used"],
  "risk_flags": ["partial_fix | under_fix | regression_risk | test_overfitting | insufficient_evidence"],
  "suspected_failure_type": "none | partial_fix | under_fix | regression | irrelevant | non_applicable | unknown",
  "human_review_needed": true
}

Decision policy:
- Accept only when visible evidence directly supports the patch and no visible contradiction remains.
- Reject when visible evidence contradicts the required behavior, the patch does not apply, visible tests fail/error/timeout, or the patch visibly fails to address the issue.
- Escalate when visible evidence is incomplete, ambiguous, or insufficient for a safe merge decision.
- If the evidence level is sparse, prefer escalation over unsupported acceptance.

Visible evidence packet:
{visible_evidence_packet_json}
```

Label-leakage boundary:

- The prompt payload is built only from `data/evidence/evp7_evidence_packets.jsonl`.
- It must not include candidate-specific evaluator fields such as
  `label_with_p2p_broad`, `candidate_type`, `expected_outcome`,
  `failure_type_label`, retained-oracle outcome, hidden P2P outcome, or
  reference provenance.
- Generic schema enum values such as `partial_fix` are allowed because they
  describe possible verifier risk flags and do not reveal any candidate's
  hidden label.

Dry-run readiness status:

- command:
  `python scripts\build_evp7_g5_llm_prompt_manifest.py --check`;
- prompt manifest records: 168;
- E0/E2/E4/E6 records: 42 each;
- label leakage failed count: 0;
- prompt text stored in tracked manifest: false;
- API call attempted: false.
