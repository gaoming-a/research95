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

The candidate manifest is:

```text
data/patches/evp7_candidates.jsonl
```

It contains 46 promoted candidates from the validated EVP-7 candidate outputs.
Its labels and failure taxonomy are evaluator-only inputs for metrics and must
not be copied into model-visible evidence packets.

The current evidence packet manifest is:

```text
data/evidence/evp7_evidence_packets.jsonl
```

It contains E0/E2/E4/E6 records for all 50 candidates. E0/E2 are complete.
E4 is complete for all 50 candidates after rerunning predeclared visible tests
in candidate workdirs with the same tracked project-level compat shims recorded
in the P2P manifests. E6 is complete for all 50 candidates after deterministic
visible tool summaries were generated from already model-visible static and
visible-test evidence. Three visible-test outcomes are `error` because partial
candidates break import; those are visible outcomes, not hidden evaluator
labels. Retained-oracle and hidden P2P validation results must not be used to
fill visible evidence fields.

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

Current gate status after the first packet builder:

- G1 passes: every admitted candidate has E0/E2/E4/E6 packet records;
- G2 passes for the generated packet records: automated leakage audit found no
  evaluator labels, oracle outcomes, hidden tests, reference provenance, or
  failure taxonomy in model-visible packets.
- G3 passes for deterministic tool-only baselines: apply-only, visible-tests,
  and visible-tool-summary conditions each produce 50 schema-valid decisions
  and aggregate metrics.
- G4 passes for the no-API merge-gate schema dry-run: all 200 E0/E2/E4/E6
  packet-level outputs parse into the fixed accept/reject/escalate JSON schema
  with zero leakage findings. These records are parser/schema evidence only,
  not LLM verifier results.
- G5 passes for pilot-level signal existence on the current 200-packet
  DeepSeek official run: `real_llm_verifier_signal_observed_on_evp7`.
  E4/E6 preserve false accept rate 0.0 and accepted precision 1.0 while
  increasing correct recall over E0 to 0.111111 at E4 and 0.222222 at E6, with
  positive Evidence Gain over E0. This supports EVP-7 pilot signal claims, not
  scale-generalized paper claims.
- The tracked full-run quality audit is `passed_with_limitations`: it supports
  the pilot evidence-visibility signal claim, but explicitly rejects claims that
  the LLM outperforms the deterministic visible-test tool-only baseline, that
  DeepSeek cost is known from runner output,
  or that the result generalizes beyond EVP-7.
- The G5 LLM prompt is `patch_verify_evidence_visibility_merge_gate_v1`. Its
  no-API prompt manifest covers all 200 E0/E2/E4/E6 packet prompts with zero
  leakage failures and no tracked full prompt text. The real DeepSeek official
  run wrote raw model responses only under ignored `outputs/evp7_g5_llm_003/`;
  tracked summaries remain raw-output-free.
- The tracked `configs/evp7_g5_llm.example.json` and
  `scripts/preflight_evp7_g5_llm_run.py` now prove structural readiness without
  API calls. Strict API readiness intentionally remains false until those user
  confirmations are supplied in an ignored local config.
- The guarded workflow `scripts/run_evp7_g5_llm_workflow.py` now supports
  check-only, mock validation, and bounded real execution. Mock records validate
  parser and metrics plumbing only; the tracked G5 result uses genuine LLM
  outputs.
- The local-config helper `scripts/create_evp7_g5_llm_local_config.py` now
  provides a dry-run confirmation packet. It must not write the ignored local
  config until provider, model, cost ceiling, smoke scope, and full-run
  permission are explicitly supplied.

## Post-A Expansion

Expansion to 15-20 bugs is deferred until Phase A passes. The preferred order is:

1. C-lite external/source expansion after protocol interfaces freeze;
2. B-selective native/build probes only when one project can unlock multiple
   tasks and the build is containerizable;
3. no return to blind BugsInPy sweeping as the default strategy.
