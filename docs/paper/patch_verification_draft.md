# Evidence Visibility Matters: A Systematic Study of LLM-Based Verification for Candidate Patches

Draft status: EVP-7 bounded four-anchor submission draft, 2026-06-18.

This draft reports the first full DeepSeek official API pilot, the follow-up
tool-augmented verifier, and the current EVP-7 evidence-visibility pilot. The
current evidence supports dataset construction, executable label validation,
no-API baselines, prompt-boundary checks, deterministic no-API reproducibility,
model-selection boundary documentation, a 60-record real API run, a
30-candidate tool-augmented run, and a 376-record EVP-7 G5 run. The first
prompt-only result is mixed and does not support a positive prompt-only
evidence-first claim under the configured gate. The tool-augmented run shows
that making tool-execution evidence visible restores the safety/recall tradeoff
on the first pilot. The EVP-7 run supports only bounded pilot observations about
evidence-level variation, not scale-generalized claims.

## Abstract

AI coding agents increasingly produce patches for real software tasks, but a
patch that looks plausible is not necessarily safe to merge. This paper studies
patch acceptance as an evidence-conditioned merge-gate decision: given a real
task and a candidate patch, decide whether the patch should be accepted,
rejected, or escalated under visible evidence. We construct a hidden-evaluator
patch-verification pipeline from retained real-bug tasks, materialize
source-level candidates, validate labels with executable F2P/P2P evidence, and
generate model-visible E0/E2/E4/E6 evidence packets. The paper-facing EVP-7
pilot reviews 94 candidates from 20 real-bug tasks, yielding 376 real DeepSeek
G5 verifier records. A broader structural/no-API cohort tracks 21 tasks, 98
candidates, 392 leakage-audited evidence packets, 294 deterministic tool-only
decisions, qualitative case analysis, claim traceability, and artifact
readiness checks. E4 and E6 preserve zero observed false accepts and accepted
precision 1.0; E6 reaches correct recall 0.35 and Evidence Gain 14.25. The
result supports bounded four-anchor evidence-visibility observations, not a
full E0-E6 ladder, scale-generalized claims, or LLM superiority over
deterministic tool-only baselines.

## 1. Introduction

AI coding agents are increasingly used to generate patches for real codebases.
The standard question, "does the patch pass tests?", is insufficient when tests
are incomplete or when generated changes are plausible but partial. Software
teams need a merge-gate decision: accept, reject, or escalate.

This work treats patch review as a verification problem rather than a generic
bug-finding problem. The reviewer is asked to judge a candidate patch against a
task summary and visible patch context. The evaluator uses executable or
tool-backed evidence to determine whether the decision is correct.

The motivating failure mode comes from earlier experiments in this project:
LLM-only review produced useful signals but also over-reported defects on
fixed/reference controls. That makes prompt-only review unsuitable as a merge
gate without stronger evidence discipline.

## 2. Related Work and Positioning

Real-bug benchmarks and issue-based tasks make controlled repair evaluation
possible. Defects4J and BugsInPy provide reproducible fault corpora for testing
and debugging studies, while SWE-bench moves the setting toward real GitHub
issues and repository-level task resolution. These benchmarks define tasks and
outcomes, but they do not by themselves specify what evidence was visible to a
verifier before a patch was accepted, rejected, or escalated.

Automated repair research has long separated plausible patches from correct
patches. Generate-and-validate systems can produce patches that pass available
tests yet remain semantically incorrect. More recent LLM-based repair and
agentic software-engineering systems expand how patches are generated or tasks
are attempted. EVP-7 asks a different question: given a candidate patch, what
decision should a verifier make under a stated evidence packet?

The distinction is therefore evidence visibility, not another pass-rate
benchmark. The verifier decision is made with hidden evaluator labels withheld;
labels are joined only after review to compute false accepts, correct recall,
escalation, and utility. Evidence Gain is a descriptive pilot metric for this
frozen protocol, not a proposed universal benchmark score.

Reference mapping and RIS export are tracked in
`docs/experiments/evp7_related_work_positioning.md` and
`docs/references/evp7_related_work_references.ris`.

## 3. How to Read the Experiment

The experiment has one recurring unit. First, a real software task is paired
with a candidate patch. Second, the verifier receives a model-visible evidence
packet at a stated level, such as E0, E2, E4, or E6. Third, the verifier makes
one merge-gate decision: accept, reject, or escalate. Fourth, hidden evaluator
labels and oracle outcomes are joined only after the decision. Fifth, the joined
records are aggregated into false accepts, correct recall, escalation, utility,
and claim-boundary checks.

This reader path is the main line of the paper. The first-pilot sections later
in the draft are diagnostic design evidence for the workflow; the frozen EVP-7
run is the paper-facing evidence-visibility result. The corresponding visual
asset is `docs/figures/fig7_decision_metric_flow.pdf`.

## 4. Workload at a Glance

The main contribution is not only a set of prompts. The paper builds and audits
an end-to-end verification pipeline whose intermediate artifacts are tracked and
separated by visibility boundary.

| pipeline stage | tracked workload evidence |
|---|---|
| task admission | 21 structural tasks across 6 projects, admitted through project-level P2P or documented bounded policies |
| candidate construction | 98 structural candidates with 21 correct references, 76 issue-not-fixed negatives, and 1 regression negative |
| evidence packets | 392 E0/E2/E4/E6 packets, all complete, with G1 completeness and G2 leakage audit passed |
| visible evidence sources | 95 completed visible-test outcomes, 3 visible candidate-induced errors, and 98 complete visible tool summaries |
| tool-only baselines | 294 deterministic decisions across apply-only, visible-tests, and visible-tool-summary baselines |
| real LLM review | 376 DeepSeek G5 records over the paper-facing 20-task / 94-candidate cohort |
| interpretation and audit | 6 qualitative cases plus raw-output-free quality, utility, tool-attribution, and claim-boundary artifacts |

This ledger is why the current result is framed as a bounded empirical pilot
rather than as a small prompt comparison. The first-pilot 30-candidate runs are
diagnostic; the paper-facing result is the EVP-7 four-anchor evidence-visibility
study.

## 5. Research Questions

RQ1. How risky is evidence-poor LLM review as a merge gate for candidate
patches?

RQ2. Does prompt-only evidence discipline reduce observed false accepts, and
what correct-recall cost does it introduce?

RQ3. Across E0/E2/E4/E6, how does visible evidence change false accepts,
accepted precision, correct recall, escalation, and utility?

RQ4. What do deterministic and tool-assisted evidence baselines allow us to
claim about LLM contribution?

RQ5. Which paper claims remain supported or unsupported under the frozen
20-task EVP-7 pilot boundary?

## 6. Dataset Construction

The pilot dataset is built from retained BugsInPy-derived real-bug assets. Each
source task has a buggy checkout, a fixed checkout, a task summary, touched
files, visible test hints, and retained executable oracles.

Each candidate record contains evaluator-facing fields, including `patch_id`,
`candidate_type`, `expected_outcome`, and oracle metadata. Model-visible inputs
use an anonymous `candidate_id` and omit evaluator labels, oracle paths, oracle
results, and construction notes.

The first patch-verification pilot contains:

| item | value |
|---|---:|
| real-bug tasks | 7 |
| projects | 2 |
| patch candidates | 30 |
| correct reference patches | 7 |
| empty/no-op controls | 7 |
| unrelated controls | 7 |
| partial-fix candidates | 9 |

The current EVP-7 evidence-visibility pilot is a separate bounded cohort:

| item | value |
|---|---:|
| real-bug tasks | 20 |
| projects | 5 |
| patch candidates | 94 |
| evidence levels | 4 |
| evidence packets | 376 |
| correct reference patches | 20 |
| issue-not-fixed negatives | 74 |

Patch materialization uses retained source artifacts:

- `buggy_fixed_unified_diff`: reference diff between buggy and fixed checkouts.
- `empty_diff_against_buggy_checkout`: no-op control.
- `local_comment_only_unified_diff`: applicable unrelated source change.
- `first_hunk_of_reference_unified_diff`: partial candidate from a multi-hunk fix.
- `reference_diff_with_one_change_omitted`: partial candidate omitting one change block.
- `reference_replace_with_one_line_reverted`: partial candidate reverting one line inside a replace block.

## 7. Executable Label Validation

Candidate labels are validated by applying each candidate patch to a copied
buggy checkout and running retained executable oracles. This guards against
purely prompt-based or manually asserted labels.

Current validation status:

| validation item | value |
|---|---:|
| candidates validated | 30 |
| patches applied | 30 |
| oracle runs | 30 |
| validation failures | 0 |

Correct patches are expected to pass all retained oracles. Negative candidates
(`incorrect`, `irrelevant_or_noop`, and `partial`) are expected to fail at least
one retained oracle.

## 8. Review Conditions

### LLM-Only Review

The reviewer sees the task summary, visible context, and candidate patch. It
must output one JSON object with decision, confidence, claims, rationale, and
uncertainty. It does not see hidden oracle paths or oracle results.

### Evidence-First Verification

The reviewer sees the same task and patch context plus model-visible evidence
source metadata and visible test hints. It must tie every accept/reject decision
to concrete visible evidence. If the visible evidence is insufficient, it should
escalate.

### Tool-Augmented Evidence Verification

The reviewer sees the same task and patch context plus patch-apply status and
executable behavior summaries derived from retained validation runs. It still
does not see evaluator labels such as `expected_outcome`, `candidate_type`,
construction notes, or oracle paths. This condition must be reported separately
because it is tool-assisted verification, not prompt-only model ability.

### Oracle Upper Bound

The evaluator can use hidden labels and oracle outcomes to produce an upper
bound. This is not model capability and must be reported separately.

## 9. Metrics

Primary metrics are patch-level:

- false accept rate: incorrect, partial, or unrelated patches accepted;
- false reject rate: correct patches rejected;
- accepted precision: accepted patches that are actually correct;
- correct-patch recall: correct patches accepted;
- escalation rate: patches sent to human/tool verification;
- invalid-output rate and cost.

Escalation is neither accept nor reject. It should be reported separately
because reducing false accepts by escalating everything is not a useful merge
gate.

## 10. Current No-API Results

The current no-API baselines validate the metric implementation and expected
tradeoffs.

| baseline | accepted precision | false accept rate | correct recall | false reject rate |
|---|---:|---:|---:|---:|
| accept-all | 0.2333 | 1.0000 | 1.0000 | 0.0000 |
| reject-all | NA | 0.0000 | 0.0000 | 1.0000 |
| oracle upper bound | 1.0000 | 0.0000 | 1.0000 | 0.0000 |

Interpretation: the dataset and metrics expose the intended merge-gate tension.
The no-API results do not test the research hypothesis because no real model
reviewer decisions have been collected.

## 11. API Pilot Result

The first API pilot ran two conditions on the validated 30 candidates:

1. `llm_only`
2. `evidence_first`

Both conditions used `deepseek-v4-pro` through the DeepSeek official API. The
run produced 60 non-mock review records and passed the completeness audit:
30 candidates, 2 conditions, raw response hashes present, no missing raw
responses, no `run_error.json`, and required review fields present.

| condition | false accept rate | accepted precision | correct recall | escalation rate | invalid output rate |
|---|---:|---:|---:|---:|---:|
| `llm_only` | 0.0909 | 0.7143 | 1.0000 | 0.0667 | 0.1000 |
| `evidence_first` | 0.0000 | 1.0000 | 0.7143 | 0.1333 | 0.0333 |

The result is not a positive result. Evidence-first removed the observed false
accepts and improved accepted precision, but correct-patch recall dropped by
0.2857, exceeding the configured tolerance of 0.25. The stop/continue gate
therefore returned `stop_or_redesign`.

The most important failure pattern is that `llm_only` accepted two partial
fixes, while `evidence_first` did not accept them. However, `evidence_first`
also rejected or escalated two correct reference patches. The current result
therefore supports a safety/utility tradeoff claim, not a superiority claim.

## 12. Tool-Augmented Redesign Smoke

After the prompt-only full run returned `stop_or_redesign`, a targeted
5-candidate redesign smoke tested a separate `tool_augmented_evidence`
condition on the known failure cases. The condition exposed patch-apply status
and executable behavior summaries to the verifier.

| candidate | expected smoke behavior | decision |
|---|---|---|
| `candidate_0001` | accept reference fix | `accept` |
| `candidate_0005` | do not accept partial fix | `reject` |
| `candidate_0006` | do not accept partial fix | `reject` |
| `candidate_0020` | do not accept partial fix | `reject` |
| `candidate_0023` | accept reference fix | `accept` |

The smoke passed with 5 non-mock reviews and 0 invalid outputs. This supports a
narrow diagnostic claim: the prompt-only failure was plausibly caused by
evidence poverty. It does not rescue the original prompt-only claim. It only
justifies a separate 30-candidate tool-augmented full run.

## 13. Tool-Augmented Full Run

The tool-augmented full run evaluated the same 30 candidates under a separate
`tool_augmented_evidence` condition. The verifier saw patch-apply status and
executable behavior summaries. It did not see evaluator labels such as
`expected_outcome`, `candidate_type`, construction notes, or oracle paths.

| condition | false accept rate | accepted precision | correct recall | false reject rate | escalation rate | invalid output rate |
|---|---:|---:|---:|---:|---:|---:|
| `llm_only` | 0.0909 | 0.7143 | 1.0000 | 0.0000 | 0.0667 | 0.1000 |
| `prompt_only_evidence_first` | 0.0000 | 1.0000 | 0.7143 | 0.1429 | 0.1333 | 0.0333 |
| `tool_augmented_evidence` | 0.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |

The tool-augmented full-run gate passed with 30 non-mock reviews, 0 invalid
outputs, false accept rate 0.0, and correct-patch recall 1.0.

This result supports a conditional tool-assisted verification claim. It does
not show that prompt-only evidence-first review is sufficient; instead, it
shows that executable evidence summaries can be decisive for the known
safety/recall tradeoff.

## 14. EVP-7 Evidence Visibility Pilot

After the 30-candidate pilots, EVP-7 freezes a larger evidence-visibility
cohort at 20 real-bug tasks, 94 patch candidates, and four model-visible
evidence levels per candidate: E0, E2, E4, and E6. The G5 merge-gate verifier
uses `deepseek-v4-pro` through the DeepSeek official API and returns
accept/reject/escalate decisions in a fixed schema.

The current 376-record full run produced 376 valid non-mock model outputs, no
schema-invalid records, and complete token-usage cost observability. The
runner-estimated cost is 0.327352058 USD; this is an estimate from provider
token usage and configured pricing, not an external billing statement.

| evidence | records | accept | escalate | reject | false accept | accepted precision | correct recall | Evidence Gain vs E0 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| E0 | 94 | 1 | 49 | 44 | 0.0000 | 1.0000 | 0.0500 | 0.0000 |
| E2 | 94 | 0 | 57 | 37 | 0.0000 | NA | 0.0000 | -3.0000 |
| E4 | 94 | 1 | 21 | 72 | 0.0000 | 1.0000 | 0.0500 | 7.0000 |
| E6 | 94 | 7 | 16 | 71 | 0.0000 | 1.0000 | 0.3500 | 14.2500 |

Utility sensitivity varies false-accept, escalation, and false-reject penalties
over 27 scenarios. Within this bounded grid, E6 is the best evidence level in
all scenarios and the ranking remains E6 > E4 > E0 > E2. Because every evidence
level has zero observed false accepts in this run, changing the false-accept
penalty does not affect the utility ranking.

The quality audit passes with limitations. The run produced raw-output-free
tracked metrics from real DeepSeek verifier outputs, and supports bounded EVP-7
pilot claims that those outputs vary by evidence level and that E4/E6 preserved
zero observed false accepts with accepted precision 1.0. It does not support
scale-generalized claims, a claim that the LLM outperforms the deterministic
visible-test/tool-only baseline, a claim that E6 strictly improves over E4, or a
claim that runner-estimated cost is an external bill.

The deterministic tool-only attribution analysis makes that boundary more
specific. At E6, the LLM and the matched visible-tool-summary baseline agree on
76 of 94 candidates, and the LLM accepts no candidate outside the tool-only
accept set. The LLM recovers the four observed tool-only false accepts, but it
also downgrades 12 tool-only true accepts to reject or escalation. This supports
a bounded safety/recall tradeoff interpretation, not a claim that the LLM
outperforms deterministic visible evidence.

The qualitative case audit explains the decision mechanics behind the aggregate
tradeoff. It selects six representative EVP-7 cases and separates the
model-visible decision sequence from the evaluator-only interpretation. The
cases include evidence-enabled accepts, recovered tool-only false accepts,
correct patches downgraded by the LLM, and non-fixing patches rejected after
evidence became visible. These examples are interpretive evidence for the
bounded pilot, not additional scale evidence.

## 15. Reproducibility and Handoff Controls

The pre-API artifact includes deterministic reproduction checks for the local
dataset construction pipeline. The original no-API pilot and a reproduced run
are compared by hashing deterministic output files:

- `candidates.jsonl`
- `evidence_packets.jsonl`
- `verifier_outputs.jsonl`
- `dataset_summary.json`
- `metrics.json`
- `validation_summary.json`
- `pilot_report.md`

The current comparison checks 7 deterministic files and reports no missing or
mismatched files. Runtime work directories, raw API responses, external
checkouts, and environment-dependent files are not treated as deterministic
reproducibility evidence.

Generated paper tables for the current tracked state are available in
`docs/paper/generated_tables.md` and `docs/paper/generated_tables.tex`. These
tables are generated from JSON outputs rather than manually copied values.

The execution plan also separates local pre-API checks from model experiments.
The current handoff packet refreshes readiness, paper readiness, plan progress,
human-required inputs, Git-sync state, model-selection visibility, and
deterministic reproducibility. This is an engineering control: it prevents
dry-run, mock, or local validation outputs from being mistaken for model
results.

## 16. Model Selection Boundary

The first real API pilot is a within-model comparison. The same model must be
used for `llm_only` and `evidence_first`, so the first claim controls for base
model capability but does not establish cross-model generality.

Before any local model config is created, the executor must document:

- concrete provider model id;
- API provider;
- provider;
- selection source and date;
- capability source or capability band;
- reason for selection;
- known limitations.

The current DeepSeek runs use `deepseek-v4-pro` through DeepSeek official API.
This controls for base-model capability within each comparison, but it does not
establish cross-model generality.

## 17. Threats to Validity

Dataset size is small. The first 30-candidate pilot and the later 376-packet
EVP-7 pilot are designed to validate the method and failure surfaces, not to
make broad claims about all AI-generated patches.

The partial-fix candidates are source-backed and oracle-checkable, but they are
constructed from retained reference diffs rather than generated by live coding
agents. A later stage should add model-generated patches or SWE-bench-style
tasks.

Visible test hints may not represent the evidence actually available in all
engineering workflows. The protocol should distinguish visible context,
evidence packets, and hidden evaluator oracles.

Model behavior can drift over time and across providers. Every API run must
record provider model id, API provider, date, prompt version, decoding settings,
cost, raw response path, and invalid-output status.

The first pilot uses a single model by design. This is appropriate for testing
whether verification condition changes acceptance behavior within one model,
but it cannot support claims about all frontier models or all coding agents.

Tool-augmented evidence includes executable behavior summaries. This is closer
to engineering verification than prompt-only review, but it should not be
presented as pure LLM reasoning ability. If the summaries include direct
pass/fail outcomes, the condition is an evidence-assisted verifier and should
be interpreted as a tool workflow.

## 18. Current Conclusion

The current artifact reports a validated patch-verification pilot and a
completed single-model API pilot. The result does not show that prompt-only
evidence-first verification improves over LLM-only review under the configured
gate. Evidence-first reduced false accepts and improved accepted precision, but
it also reduced correct-patch recall beyond the configured tolerance.

The revised tool-augmented verifier passed the 30-candidate full-run gate by
accepting all correct reference patches and rejecting all negative candidates.
The EVP-7 G5 run then shows bounded evidence-level variation on a larger frozen
cohort. The paper should therefore report a staged finding: prompt-only review
is not enough, evidence-poor verification is too conservative, tool-visible
execution evidence can support a separate verifier under the first pilot, and
the EVP-7 evidence-visibility run provides bounded pilot evidence that
additional visible evidence changes merge-gate behavior.
