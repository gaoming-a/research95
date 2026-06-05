# Evidence-First Patch Verification Protocol

## Purpose

The evidence-first protocol began as the main proposed workflow. The first full
DeepSeek run showed that the prompt-only version is too evidence-poor: it
removed observed false accepts but failed to preserve correct-patch recall.

The revised workflow separates two conditions:

- prompt-only evidence-first verification;
- tool-augmented evidence verification.

The verifier must connect each decision to concrete evidence:

- executable oracle result;
- existing test result;
- targeted generated test result;
- static or type-check evidence;
- differential behavior;
- patch-diff evidence;
- human label, when explicitly collected.

## Workflow

1. Read the task summary and candidate patch.
2. Extract patch claims:
   - what behavior changed;
   - which files/functions changed;
   - what condition must hold for correctness.
3. Build an evidence checklist:
   - executable oracle available?
   - existing tests relevant?
   - targeted smoke check possible?
   - static check relevant?
   - claim supported by patch diff?
4. Run available no-API evidence tools.
5. Ask the verifier to decide using the evidence packet.
6. Accept only if the correctness claim is supported by sufficient evidence.
7. Reject if the evidence contradicts the claim or the patch is irrelevant.
8. Escalate if evidence is insufficient.

The model-visible evidence packet uses an anonymous `candidate_id`. Evaluator
fields such as `patch_id`, `candidate_type`, `expected_outcome`,
`hidden_oracles`, and construction notes are kept outside the prompt boundary.

## Conditions To Compare

### LLM-Only Review

The model sees task context and patch context, then outputs accept/reject.
No evidence packet is provided.

Purpose: baseline for unsupported decisions.

### Majority Review

Multiple LLM-only reviewers vote. The policy accepts by majority.

Purpose: test whether aggregation solves unsupported decisions.

### Agent-Context Review

The model sees additional workflow context, such as prior attempts or structured
debugging notes.

Purpose: test whether richer context changes reliability.

### Prompt-Only Evidence-First Verification

The model sees task context, patch context, and an evidence packet. It must
cite evidence for each accepted or rejected claim.

Purpose: test whether stricter evidence discipline helps without tool outputs.
The first full run returned `stop_or_redesign`, so this condition is no longer
the positive target method.

### Tool-Augmented Evidence Verification

The model sees task context, patch context, patch-apply status, and executable
behavior summaries. It must still avoid evaluator labels, but it may use the
visible tool outcomes as evidence.

Purpose: revised target workflow. It tests whether making executable evidence
visible repairs the safety/recall tradeoff observed in the prompt-only run.

### Oracle Upper Bound

The evaluator uses hidden oracle labels directly.

Purpose: upper bound only. It must not be presented as model capability.

## Evidence Sufficiency

Accepted patches require at least one of:

- hidden or held-out oracle passes and no contradictory evidence exists;
- targeted behavior check passes and source diff supports the intended fix;
- human-backed evidence confirms correctness.

Rejected patches require at least one of:

- oracle failure;
- targeted behavior check failure;
- patch does not touch relevant behavior;
- claim contradicts source diff or execution evidence.

Escalation is required when:

- evidence is absent;
- evidence is mixed;
- only visible tests pass and no stronger behavior check exists;
- the model cannot localize the correctness claim.

## Reporting Rule

Report both raw model decisions and evidence-gated decisions. Never pool them
without labeling the condition.

Tool-augmented results must be reported separately from prompt-only results.
They are evidence-assisted verifier behavior, not pure model-review ability.
