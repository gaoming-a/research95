# DSA P3 Preregistration v0.1

Status: candidate freeze pending author sign-off
Target: DSA 2026 Regular
Prepared: 2026-07-11
Model API calls: 0

## Argument and boundary

On a task-disjoint controlled patch cohort, this study will estimate how
cumulative, genuinely executed visible evidence changes LLM automatic-merge
recommendations for paired hidden-failing and oracle-positive candidates. The
result is a finite-cohort decision-policy effect conditional on 30 frozen
tasks, three fixed model routes, three stateless repeats, and the frozen run
window. It is not evidence of autonomous correctness, software safety,
deployment prevalence, or an effect for all projects and LLMs.

## Terminology ledger

| Canonical term | Meaning | Locked usage |
|---|---|---|
| task | One frozen real-bug source with a paired candidate set | only scientific analysis unit; `n=30` |
| oracle-positive | Official reference fix passing every frozen visible and hidden check twice | candidate role, hidden until P8 |
| hard negative | First applicable frozen partial-fix transform passing visible checks but failing an independent hidden oracle twice | candidate role, hidden until P8 |
| condition | One cumulative model-visible packet from C0 through C3 | never exposed by name to the model |
| repeat | One stateless response draw for a fixed task/candidate/model block | nested, not an independent task sample |
| conditional interval | Repeat-block percentile interval conditional on frozen tasks/models | not a population confidence interval |
| accept | Recommend automatic merge | output decision |
| reject | Recommend do not merge | output decision |
| escalate | Supplied information does not support an automatic decision | output decision |

## Research questions and estimands

RQ1 asks how C3 rather than C0 changes accept probability for hard negatives;
RQ2 asks the same for oracle-positive candidates. Their paired primary
estimands are respectively `Delta_minus` and `Delta_plus`. RQ3 describes the
accept/reject/escalate pathways and cross-model heterogeneity; it is secondary.

For every task, candidate role, model, and repeat index, analysis pairs the C3
and C0 accept indicators. Contrasts are averaged across repeats, equally across
the three models within task, and equally across the 30 tasks. Both primary
effects must be reported together; neither direction is declared beneficial in
isolation.

## Evidence contract

- C0 contains the neutral change request, normalized candidate diff, and
  necessary code context.
- C1 adds actual patch-apply and syntax/import/static commands and results.
- C2 adds preregistered visible fail-to-pass names, commands, and results.
- C3 adds preregistered visible pass-to-pass/regression names, commands, and
  results.

Every added group is non-empty, command/result paired, and tied to a complete
environment hash. Earlier groups remain byte-identical under canonical JSON.
No packet exposes condition, protocol, label, verdict, oracle, candidate role,
source/project/task/commit/issue identity, or reference provenance. The hidden
tree is joined only after outputs and execution hashes are frozen.

## Statistics and reporting

The two primary intervals use 20,000 paired repeat-block bootstrap draws with
NumPy PCG64 seed `2026071103`. Within every fixed task-candidate-model block,
three repeat indices are sampled with replacement while preserving each C3/C0
pair. Percentile endpoints 0.0125 and 0.9875 give Bonferroni familywise 95%
coverage for the two primary estimands under this conditional procedure.

Model-specific effects, reject/escalate/non-escalation changes, transition
matrices, repeat disagreement, between-model disagreement, project-balanced
reweighting, and leave-one-project-out ranges are secondary or stability
analyses. Adjacent condition contrasts and cohort-conditional precision are
descriptive only. No pooled p-value or candidate/request-level sample-size
inflation is permitted.

## Exclusion, stopping, and no rerun

P1/P2 development tasks and projects remain excluded. P4 applies only the
first applicable frozen transform and uses only frozen reserve order before any
model call. Inapplicable transforms, visible failures, hidden-pass negatives,
or environment disagreement are discarded without reclassification. Reserve
exhaustion before 30 complete pairs stops the study.

Execution permits one retry only for transport failure, HTTP 429, or empty
response, subject to stage caps. A schema/semantic invalid, model identity or
price drift, fallback, hash drift, early label join, cost/token/window breach,
or valid-response overwrite stops the stage. Valid outputs are never replaced.
Unfavorable decisions, null/negative effects, wide intervals, disagreement,
reviewer preference, or a desire to alter the paper cannot trigger reruns.

## Frozen model routes

The proposed author freeze is, in route order:

1. Alibaba Cloud Model Studio `qwen3.7-plus-2026-05-26`, non-thinking JSON
   mode, temperature 0.2;
2. DeepSeek API `deepseek-v4-flash`, non-thinking JSON mode, temperature 0.2;
3. Google Gemini Developer API `gemini-3.5-flash`, structured output with
   minimal thinking and provider-recommended temperature omission.

Each request is stateless and capped at 32,768 input and 1,024 output tokens.
The exact endpoints, parameters, ordering algorithm, attempts, date window,
price snapshot, and route cost ceilings are in
`data/protocols/dsa_p3_model_freeze_v0_1.json`. Any documented ID or price drift
stops execution rather than substituting a route.

## Claim-evidence map

| Claim | Evidence | Status |
|---|---|---|
| The design uses a task-disjoint Regular source | P1/P2 registries and source selection | supported before P3 |
| The model-visible ladder has no label/verdict leakage | P3 recursive and rendered-prompt audit | requires mechanical Gate |
| C3 changes hard-negative accept policy | `Delta_minus` on new frozen outputs | needs P7/P8 evidence |
| C3 changes oracle-positive accept policy | `Delta_plus` on new frozen outputs | needs P7/P8 evidence |
| Effects vary by model or decision pathway | secondary analyses on new outputs | needs P7/P8 evidence |

## Assumptions or missing inputs

The author has not yet signed the 11 frozen items or accepted scientific
responsibility. Therefore this document is not yet immutable, P3 is not passed,
and P4, P5, and model API execution remain unauthorized.

The machine-readable preregistration is authoritative for exact formulas and
rules: `data/protocols/dsa_p3_preregistration_v0_1.json`.
