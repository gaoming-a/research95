# Evidence Visibility Protocol

This protocol defines the immediate Phase A route after the 2026-06-12
decision to freeze the current BugsInPy low-friction cohort.

## Decision

The current protocol pilot is named `EVP-7 Protocol Pilot`.

Approved now:

- freeze the current 7 BugsInPy main tasks;
- stop blind BugsInPy expansion under project-level P2P-broad;
- build the evidence-visibility protocol on the frozen cohort.

Not approved as the current main route:

- broad native/editable build work for old Python projects;
- task-file P2P downgrade to increase bug count;
- immediate external benchmark migration before schema and gates are stable.

## Frozen Cohort

The task manifest is:

```text
data/tasks/evp7_tasks.jsonl
```

It contains exactly the tasks that satisfy both registry conditions:

```text
project_level_p2p_status == completed
p2p_broad_main_included == true
```

The blocker registry is:

```text
data/exclusions/blocked_bugsinpy_projects.jsonl
```

Blocked, pending, insufficient, and appendix-only tasks remain part of the
audit trail. They must not be deleted to make the cohort look cleaner.

## Phase A Scope

The next protocol step is not a new bug search. It is to show that the frozen
cohort can support the final-paper evidence-visibility design.

Phase A must establish:

- a tracked candidate schema for EVP-7 patches;
- E0/E2/E4/E6 evidence packet builders;
- a leakage audit over generated evidence packets;
- realistic tool-only baselines;
- a fixed merge-gate output schema for LLM verifier runs;
- metrics for false accept, accepted precision, correct recall, escalation,
  FACR, Evidence Gain, and utility.

## Evidence Levels For The Pilot

Run the pilot with four levels first:

| Level | Visible evidence | Purpose |
| --- | --- | --- |
| E0 | issue or bug summary + candidate patch diff | LLM diff-only merge-gate behavior |
| E2 | E0 + apply/static/syntax/import style evidence | low-cost tool filtering |
| E4 | E2 + visible F2P/P2P execution evidence | executable visible evidence effect |
| E6 | E4 + realistic visible tool evidence summary | strongest realistic non-oracle setting |

E1/E3/E5 are deferred until the core curve is stable. E7 is an oracle upper
bound only and must not support realistic merge-gate claims.

## Visible And Hidden Boundary

Verifier-visible evidence may include:

- anonymous candidate id;
- issue or bug summary;
- candidate diff;
- changed files/functions;
- patch apply or static check status;
- visible test names and visible outcomes;
- realistic visible tool summary.

Verifier-hidden evidence includes:

- final labels;
- retained oracle labels;
- hidden F2P/P2P outcomes;
- reference patch provenance;
- manual failure taxonomy;
- hidden evaluator paths;
- any sentence equivalent to "this patch is correct" or "this patch is wrong".

## Merge-Gate Output Schema

LLM verifier runs should emit a strict JSON object:

```json
{
  "decision": "accept | reject | escalate",
  "confidence": 0.0,
  "primary_reason": "...",
  "evidence_used": ["diff", "static", "visible_tests", "tool_summary"],
  "risk_flags": [
    "partial_fix",
    "under_fix",
    "regression_risk",
    "test_overfitting",
    "insufficient_evidence"
  ],
  "suspected_failure_type": "none | partial_fix | under_fix | regression | irrelevant | non_applicable | unknown",
  "human_review_needed": true
}
```

Free-form reviewer prose can be stored as raw response evidence, but metrics
must use the parsed schema.

## Phase A Gates

Before further expansion, five gates must pass:

| Gate | Requirement |
| --- | --- |
| G1 packet completeness | every admitted candidate has E0/E2/E4/E6 packets |
| G2 leakage audit | no packet exposes hidden labels, oracle results, or provenance |
| G3 baseline readiness | tool-only baselines produce complete metrics |
| G4 schema stability | verifier outputs parse into accept/reject/escalate |
| G5 signal existence | E0 to E6 changes FAR, recall, escalation, or utility in an explainable way |

If G5 fails, the protocol should be redesigned before adding bugs.

## Post-A Expansion

Expansion to 15-20 bugs is deferred until Phase A passes. The preferred order is:

1. C-lite external/source expansion after protocol interfaces freeze;
2. B-selective native/build probes only when one project can unlock multiple
   tasks and the build is containerizable;
3. no return to blind BugsInPy sweeping as the default strategy.
