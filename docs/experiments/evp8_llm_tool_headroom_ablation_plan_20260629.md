# EVP-8 LLM-vs-Tool Headroom and E6 Ablation Plan

Date: 2026-06-29

This is a no-API planning document. It does not authorize model calls, cohort
mutation, prompt changes, or raw-output generation. Its purpose is to redirect
the current EVP-8 work from "LLM verifier as a practical automatic merge gate"
to a narrower and more defensible question:

> Does an LLM verifier add judgment value beyond visible tool evidence, or does
> it mainly follow the deterministic tool summary it is shown?

## Plain-Language Explanation

The current E6 setting gives the model both the evidence and a rule-based
verdict such as `accept`, `reject`, or `escalate`. That makes the result hard
to interpret. If the LLM accepts correct patches at E6, we cannot tell whether
it understood the patch or simply followed the rule verdict.

The next plan therefore separates three things:

1. What the tools alone decide.
2. What the LLM decides when it sees the tool verdict.
3. What the LLM decides when it sees the same evidence but not the verdict.

In simple terms: instead of asking "Can the LLM verify patches?", ask:

> After tests and tools have produced evidence, is the LLM doing any useful
> extra risk filtering?

If the answer is yes, the LLM may be useful as an evidence-aware triage layer.
If the answer is no, that is still a useful negative result: deterministic
tool evidence dominates the decision, and the LLM should not be claimed as an
independent verifier.

## Why This Plan Is Needed

The current Qwen v0.3 label-conditioned result shows:

- E0-E2 correct recall is 0%;
- E3-E6 correct recall rises sharply;
- E6 accepts 20/21 correct patches;
- E6 also accepts 4/77 non-correct patches, including partial/regression
  cases.

This result is informative, but it does not yet answer the most important
scientific question. E6 includes `rule_based_visible_merge_gate_decision`, so
the observed performance may be dominated by the deterministic tool summary.

The practical question is not whether a model follows a strong summary. The
practical question is whether a model can reduce dangerous false accepts or
make better escalation decisions when tools are imperfect.

## Main Research Questions

### RQ1: Is there any headroom for the LLM to improve over tools?

Before calling any model, measure the deterministic tool baseline's mistakes:

- tool accepts non-correct patches;
- tool rejects correct patches;
- tool escalates cases that hidden labels later show were clear accept/reject
  cases.

If the tool baseline has almost no mistakes, the current cohort is too easy to
answer LLM-added-value questions.

### RQ2: Does the E6 verdict field dominate LLM behavior?

Compare:

- `E6-full`: current E6, including rule-based verdict and reasons;
- `E6-no-verdict`: same visible evidence, but without rule-based verdict,
  rule-based reasons, or source tool decision;
- `rule-only`: deterministic gate output, no LLM call.

This directly tests whether the LLM's apparent improvement comes from the
verdict field.

### RQ3: When tools are wrong, does the LLM correct them?

Focus on the opportunity set:

- tool false accepts;
- tool false rejects;
- tool unnecessary escalations.

Overall accuracy can hide the real issue. The LLM only has practical value if
it changes decisions on the cases where tools are wrong or uncertain.

### RQ4: Which false accepts remain dangerous?

Analyze partial, regression, overfitted, and plausible-wrong patches that are
accepted by the LLM or by the tool baseline. These cases are more important
than easy noop/irrelevant rejects because they correspond to real merge-gate
risk.

## Experimental Conditions

| Condition | LLM call | Visible verdict shown | Purpose |
| --- | --- | --- | --- |
| `rule-only` | No | n/a | Measures deterministic tool baseline. |
| `E6-full` | Existing Qwen v0.3 result | Yes | Current strongest evidence condition. |
| `E6-no-verdict` | Future Qwen run, after explicit authorization | No | Tests whether LLM can reason from evidence without being handed the verdict. |
| `E5` | Existing Qwen v0.3 result | No E6 verdict | Reference point before deterministic summary. |

`E6-no-verdict` should remove at least:

- `rule_based_visible_merge_gate_decision`;
- `rule_based_visible_merge_gate_reasons`;
- `source_decision`.

It should keep:

- patch apply status;
- visible test outcomes;
- visible test outcome counts;
- visible contradictions derived from visible evidence;
- sanitized tool diagnostics;
- environment and run summaries if already model-visible.

## Phase Plan

### Phase 0: No-API Headroom Audit

Goal: determine whether the current 98-candidate cohort has enough tool errors
for an LLM-added-value experiment.

Inputs:

- `data/baselines/evp7_tool_only_decisions.jsonl`;
- `data/patches/evp7_candidates.jsonl`;
- `data/protocols/evp8_candidate_set_v0_1.json`;
- current Qwen v0.3 label-conditioned summary.

Outputs:

- raw-output-free JSON/Markdown summary of:
  - rule-only decision counts;
  - rule-only label-conditioned metrics;
  - tool false accepts;
  - tool false rejects;
  - tool escalations on correct and non-correct candidates;
  - opportunity-set size.

Pass condition:

- all 98 EVP-8 candidates can be joined to tool decisions and evaluator-only
  labels;
- no raw model response or prompt text is written;
- opportunity-set size is explicitly reported.

Stop condition:

- if opportunity-set size is too small to interpret LLM added value, stop
  before API calls and mark the current cohort as too tool-solved for this
  research question.

### Phase 1: E6-no-verdict Packet/Prompt Dry Run

Goal: create a no-API packet variant that removes the rule verdict while
preserving visible evidence.

Required checks:

- 98 candidates x 1 level, or 98 candidates x selected ablation levels;
- no hidden labels;
- no reference provenance;
- no `expected_outcome`, `candidate_type`, `label_with_p2p_broad`, or other
  evaluator-only fields;
- no rendered prompt text stored in tracked outputs;
- deterministic schema dry-run passes.

Stop condition:

- if removing verdict fields also removes the evidence needed to reason, repair
  the packet design before any model call.

### Phase 2: Qwen-only Smoke for E6-no-verdict

Goal: cheaply confirm parse/schema/provider behavior for the new condition.

Scope:

- 5 candidates x 1 level first;
- use the same prompt schema unless a prompt change is explicitly reviewed and
  logged;
- no DeepSeek/Kimi/Devstral/Gemini calls.

Pass condition:

- 5/5 parse-valid;
- no forbidden risk flags;
- no model/provider drift;
- tracked summary remains raw-output-free.

Stop condition:

- parse/schema failure;
- prompt-boundary failure;
- cost or provider metadata missing;
- any need to change prompt policy without a prompt-change audit.

### Phase 3: Qwen-only Full E6-no-verdict Run

Goal: obtain a comparable 98-record Qwen decision set for the ablation.

Scope:

- Qwen only;
- 98 candidates x E6-no-verdict;
- no other evidence levels unless separately justified;
- ignored raw outputs under `outputs/`;
- tracked summary only contains aggregates and parsed decision fields.

Pass condition:

- 98/98 parse-valid;
- raw-output-free summary;
- label-conditioned metrics computed after execution.

### Phase 4: Three-Way Comparison

Compare:

- `rule-only`;
- `E6-full`;
- `E6-no-verdict`.

Metrics:

- correct recall;
- accepted precision;
- false accept rate;
- false reject rate;
- escalation rate;
- false accepts by `expected_outcome` and `candidate_type`;
- opportunity-set correction rate:
  - tool false accepts corrected by LLM;
  - tool false rejects corrected by LLM;
  - tool escalations resolved by LLM.

Interpretation:

- If `E6-full` is strong but `E6-no-verdict` collapses, the prior result was
  verdict-dominated.
- If `E6-no-verdict` matches `rule-only`, the LLM adds little decision value
  beyond visible tools in this cohort.
- If `E6-no-verdict` reduces false accepts without large recall loss, the LLM
  has evidence-aware risk-filtering value.
- If all three are similar and tool mistakes are rare, the cohort is too easy
  or too tool-solved.

### Phase 5: Hard-Case Diagnosis

If LLM and tool baseline are still identical, diagnose which explanation is
supported:

1. Tool baseline has almost no mistakes.
   - Conclusion: current cohort has insufficient headroom.
   - Repair: add harder candidates.
2. Tool baseline has mistakes and LLM repeats them.
   - Conclusion: negative result; LLM does not correct visible-tool failure
     modes.
   - Repair: do not force a positive claim; write failure-mode analysis.
3. LLM changes mostly easy cases.
   - Conclusion: aggregate metrics are misleading.
   - Repair: report opportunity-set metrics, not only full-cohort averages.
4. LLM changes false accepts but loses many correct accepts.
   - Conclusion: LLM is a risk-control/escalation layer, not an accept gate.

## Hard-Case Expansion Criteria

Only expand the cohort if Phase 0 shows insufficient headroom or Phase 4 cannot
distinguish LLM behavior from the tool baseline.

Preferred hard cases:

- visible tests pass but hidden oracle fails;
- partial fixes that solve the main path but miss edge cases;
- regression patches;
- overfitted patches;
- plausible but semantically wrong AI-agent patches.

Avoid over-expanding easy negatives:

- obvious noop;
- irrelevant patch;
- patch does not apply.

These are useful for sanity checks but weak for testing LLM added value.

## Claims Allowed After This Plan

Allowed after no-API Phase 0 only:

- report whether the current cohort has enough tool-baseline error headroom for
  an LLM-added-value experiment.

Allowed after E6-no-verdict execution:

- report Qwen-only ablation results on the frozen EVP-8 98-candidate cohort;
- report whether Qwen differs from rule-only on opportunity-set cases;
- report false-accept and recall tradeoffs.

Forbidden:

- claiming a reliable automatic patch verifier;
- claiming LLM superiority over tools without rule-only and no-verdict
  comparison;
- claiming practical merge automation;
- claiming generalization to real AI-agent patch streams without a separate
  agent-patch cohort.

## Expected Paper Reframing

The paper should not be framed as:

> We built a practical automated LLM patch verifier.

It should be reframed as:

> We evaluate whether LLM patch verifiers add value beyond visible tool
> evidence, and show when evidence-rich verification still produces dangerous
> false accepts.

The useful outcome can be positive or negative:

- Positive: LLM reduces tool false accepts without large recall loss.
- Negative: LLM mostly follows tools and should not be treated as an
  independent verifier.

Both outcomes are publishable if the experiment clearly separates tool
evidence, tool verdicts, and LLM decisions.

## Immediate Next Step

Do not run model APIs next. First implement Phase 0 as a no-API headroom audit.
Only after Phase 0 reports sufficient opportunity-set size should the project
move to E6-no-verdict packet dry-run and future Qwen-only smoke/full execution.
